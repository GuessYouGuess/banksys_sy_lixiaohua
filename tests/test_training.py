"""training 模块与训练 CLI 测试。"""

import json

import joblib
import pandas as pd
import pytest

from app.config import CATEGORICAL_COLUMNS, ID_COLUMN, NUMERIC_COLUMNS, TARGET_COLUMN
from app.training import (
    RANDOM_STATE,
    build_pipeline,
    evaluate,
    prepare_data,
    save_artifact,
    split_data,
    train_and_evaluate,
)
from scripts import train_model


def test_split_data_stratified(make_df):
    # Arrange
    df = make_df(n=100, seed=5)

    # Act
    train, test = split_data(df)

    # Assert
    assert len(train) + len(test) == len(df)
    assert len(test) == 20  # 20% 划分
    # 分层:两集正样本率接近(约为 15%)
    pos_rate = lambda d: (d[TARGET_COLUMN] == "yes").mean()  # noqa: E731
    assert abs(pos_rate(train) - pos_rate(df)) < 0.05
    assert abs(pos_rate(test) - pos_rate(df)) < 0.05


def test_build_pipeline_steps():
    # Act
    pipeline = build_pipeline()

    # Assert
    assert [s[0] for s in pipeline.steps] == ["preprocess", "model"]
    assert pipeline["model"].class_weight == "balanced"
    assert pipeline["model"].random_state == RANDOM_STATE


def test_prepare_data_drops_id_and_maps_target(make_df):
    # Arrange
    df = make_df()

    # Act
    features, target = prepare_data(df)

    # Assert
    assert ID_COLUMN not in features.columns
    assert TARGET_COLUMN not in features.columns
    assert set(target.unique()) <= {0, 1}
    assert target.dtype.kind == "i"


def test_evaluate_values():
    # Arrange
    y_true = pd.Series([1, 0, 1, 1, 0])
    y_pred = pd.Series([1, 0, 1, 0, 0])
    y_prob = pd.Series([0.9, 0.1, 0.8, 0.4, 0.2])

    # Act
    metrics = evaluate(y_true, y_pred, y_prob)

    # Assert
    assert metrics["accuracy"] == pytest.approx(0.8)
    assert metrics["precision"] == pytest.approx(1.0)
    assert metrics["recall"] == pytest.approx(0.6667)  # 指标保留 4 位小数
    assert metrics["auc"] == pytest.approx(1.0)
    assert set(metrics) == {"accuracy", "precision", "recall", "f1", "auc"}


def test_train_and_evaluate_returns_pipeline_and_metrics(make_df):
    # Arrange
    train_df = make_df(n=60, seed=1)
    test_df = make_df(n=30, seed=2)

    # Act
    pipeline, metrics, y_true, y_pred = train_and_evaluate(train_df, test_df)

    # Assert
    assert len(y_true) == len(y_pred) == len(test_df)
    assert 0.0 <= metrics["auc"] <= 1.0
    # 预测概率在两分类上存在
    proba = pipeline.predict_proba(test_df.drop(columns=[ID_COLUMN, TARGET_COLUMN]))
    assert proba.shape == (len(test_df), 2)


def test_save_artifact_writes_three_files(tmp_path, make_df):
    # Arrange
    train_df = make_df(n=40, seed=3)
    test_df = make_df(n=20, seed=4)
    pipeline, metrics, _, _ = train_and_evaluate(train_df, test_df)

    # Act
    save_artifact(pipeline, metrics, duration_median=123.0, output_dir=tmp_path)

    # Assert
    assert (tmp_path / "model.joblib").is_file()
    saved_metrics = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert saved_metrics == metrics
    metadata = json.loads((tmp_path / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["duration_median"] == 123.0
    assert metadata["random_state"] == RANDOM_STATE
    # 产物可重新加载并给出两分类标签(列名索引要求 DataFrame)
    reloaded = joblib.load(tmp_path / "model.joblib")
    sample = pd.DataFrame(
        [{**{c: 0.0 for c in NUMERIC_COLUMNS}, **{c: "a" for c in CATEGORICAL_COLUMNS}}]
    )
    predicted = reloaded.predict(sample)
    assert predicted.shape == (1,)
    assert predicted[0] in {0, 1}


def test_cli_gate_fails_below_threshold(monkeypatch, make_df):
    # Arrange: 小数据 AUC 大概率低于门槛;直接替换训练结果强制失败
    fake_pipeline = build_pipeline()
    low_metrics = {"accuracy": 0.5, "precision": 0.1, "recall": 0.1, "f1": 0.1, "auc": 0.5}

    def _fake_train(train_df, test_df, class_weight="balanced"):
        return fake_pipeline, low_metrics, None, None

    monkeypatch.setattr(train_model, "load_dataset", lambda _: make_df(n=10))
    monkeypatch.setattr(train_model, "train_and_evaluate", _fake_train)
    monkeypatch.setattr(train_model, "save_artifact", lambda *a: None)

    # Act
    code = train_model.main([])

    # Assert
    assert code == 1  # AUC 0.5 < 0.75 → 门禁失败


def test_cli_success_writes_artifact(monkeypatch, make_df):
    # Arrange
    fake_pipeline = build_pipeline()
    good_metrics = {"accuracy": 0.9, "precision": 0.8, "recall": 0.7, "f1": 0.75, "auc": 0.9}
    written = {}

    def _fake_train(train_df, test_df, class_weight="balanced"):
        return fake_pipeline, good_metrics, None, None

    def _fake_save(pipeline, metrics, duration_median, output_dir):
        written["metrics"] = metrics
        written["median"] = duration_median

    monkeypatch.setattr(train_model, "load_dataset", lambda _: make_df(n=10))
    monkeypatch.setattr(train_model, "train_and_evaluate", _fake_train)
    monkeypatch.setattr(train_model, "save_artifact", _fake_save)

    # Act
    code = train_model.main([])

    # Assert
    assert code == 0
    assert written["metrics"] == good_metrics
    assert isinstance(written["median"], float)  # duration 中位数取自训练数据

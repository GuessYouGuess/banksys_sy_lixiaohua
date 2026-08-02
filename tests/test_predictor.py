"""predictor 模块测试:加载、构造输入、预测。"""

import json

import joblib
import pandas as pd
import pytest

from app.config import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS
from app.predictor import (
    LABEL_NO,
    LABEL_YES,
    build_input_row,
    feature_options,
    load_metadata,
    load_model,
    predict,
)
from app.training import train_and_evaluate


def test_feature_options(make_df):
    # Arrange
    df = make_df()

    # Act
    options = feature_options(df, "job")

    # Assert
    assert options == ["a", "b", "unknown"]  # 去重排序,含 unknown 类别


def test_build_input_row_fills_duration_median():
    # Arrange
    categorical = {c: "a" for c in CATEGORICAL_COLUMNS}
    numeric = {c: 1.0 for c in NUMERIC_COLUMNS}

    # Act
    row = build_input_row(categorical, numeric, duration_median=180.0)

    # Assert
    assert list(row.columns) == NUMERIC_COLUMNS + CATEGORICAL_COLUMNS
    assert row.shape == (1, len(NUMERIC_COLUMNS) + len(CATEGORICAL_COLUMNS))
    assert row.loc[0, "duration"] == 180.0  # 表单不收集,用中位数填充


def test_build_input_row_invalid_value_raises(make_df):
    # Arrange: 缺一个分类特征取值
    categorical = {c: "a" for c in CATEGORICAL_COLUMNS[:-1]}
    numeric = {c: 1.0 for c in NUMERIC_COLUMNS}

    # Act / Assert
    with pytest.raises(KeyError):
        build_input_row(categorical, numeric, duration_median=0.0)


def test_predict_returns_label_and_probability(make_df):
    # Arrange: 用合成数据训练一个真实流水线
    train_df = make_df(n=80, seed=7)
    test_df = make_df(n=20, seed=8)
    pipeline, _, _, _ = train_and_evaluate(train_df, test_df)

    categorical = {c: "a" for c in CATEGORICAL_COLUMNS}
    numeric = {c: 0.0 for c in NUMERIC_COLUMNS}
    input_row = build_input_row(categorical, numeric, duration_median=100.0)

    # Act
    result = predict(pipeline, input_row)

    # Assert
    assert result["label"] in {LABEL_YES, LABEL_NO}
    assert 0.0 <= result["prob_yes"] <= 1.0
    # 概率与阈值一致:≥0.5 → yes
    assert (result["prob_yes"] >= 0.5) == (result["label"] == LABEL_YES)


def test_load_model_missing_raises(tmp_path):
    # Act / Assert
    with pytest.raises(FileNotFoundError, match="模型产物不存在"):
        load_model(tmp_path / "nope.joblib")


def test_load_model_and_metadata_roundtrip(tmp_path, make_df):
    # Arrange: 保存产物后加载
    train_df = make_df(n=40, seed=9)
    test_df = make_df(n=10, seed=10)
    pipeline, _, _, _ = train_and_evaluate(train_df, test_df)
    joblib.dump(pipeline, tmp_path / "model.joblib")
    (tmp_path / "metadata.json").write_text(
        json.dumps({"duration_median": 180.0, "random_state": 42}), encoding="utf-8"
    )

    # Act
    loaded_model = load_model(tmp_path / "model.joblib")
    metadata = load_metadata(tmp_path / "metadata.json")

    # Assert
    assert metadata["duration_median"] == 180.0
    sample = pd.DataFrame(
        [{**{c: 0.0 for c in NUMERIC_COLUMNS}, **{c: "a" for c in CATEGORICAL_COLUMNS}}]
    )
    assert loaded_model.predict(sample).shape == (1,)

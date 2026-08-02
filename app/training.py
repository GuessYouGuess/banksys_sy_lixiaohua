"""离线训练核心逻辑(纯函数,便于测试)。

约定:分类列含 unknown 值,按独立类别处理(不填充);duration 特征保留
(预测表单不收集,由 metadata 中的中位数填充,见 US-3 技术备注)。
"""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.config import CATEGORICAL_COLUMNS, ID_COLUMN, NUMERIC_COLUMNS, TARGET_COLUMN

RANDOM_STATE = 42
DEFAULT_AUC_THRESHOLD = 0.75
HOLDOUT_SIZE = 0.2
METADATA_FILE = "metadata.json"


def split_data(
    df: pd.DataFrame, test_size: float = HOLDOUT_SIZE, seed: int = RANDOM_STATE
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """按目标分层划分训练/评估集(固定种子,可复现)。

    data/test.csv 无标签(仅特征列),不能做评估集,故从 train.csv 内部划分。
    """
    train, test = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=df[TARGET_COLUMN]
    )
    return train, test


def build_pipeline(class_weight: str = "balanced") -> Pipeline:
    """预处理(标准化 + 独热编码)+ 逻辑回归二分类流水线。"""
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_COLUMNS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
        ]
    )
    return Pipeline(
        [
            ("preprocess", preprocessor),
            (
                "model",
                LogisticRegression(
                    class_weight=class_weight, random_state=RANDOM_STATE, max_iter=1000
                ),
            ),
        ]
    )


def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """拆出特征矩阵与目标序列(丢弃 id,subscribe 映射 yes=1/no=0)。"""
    features = df.drop(columns=[ID_COLUMN, TARGET_COLUMN])
    target = df[TARGET_COLUMN].map({"yes": 1, "no": 0}).astype(int)
    return features, target


def evaluate(y_true: pd.Series, y_pred: pd.Series, y_prob: pd.Series) -> dict:
    """计算评估指标:准确率/精确率/召回率/F1/ROC AUC。"""
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred)), 4),
        "recall": round(float(recall_score(y_true, y_pred)), 4),
        "f1": round(float(f1_score(y_true, y_pred)), 4),
        "auc": round(float(roc_auc_score(y_true, y_prob)), 4),
    }


def train_and_evaluate(
    train_df: pd.DataFrame, test_df: pd.DataFrame, class_weight: str = "balanced"
) -> tuple[Pipeline, dict, pd.Series, pd.Series]:
    """训练并评估,返回 (流水线, 指标, y_true, y_pred);AUC 门禁由调用方执行。"""
    x_train, y_train = prepare_data(train_df)
    x_test, y_test = prepare_data(test_df)
    pipeline = build_pipeline(class_weight=class_weight)
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)
    y_prob = pipeline.predict_proba(x_test)[:, 1]
    metrics = evaluate(y_test, y_pred, y_prob)
    return pipeline, metrics, y_test, y_pred


def save_artifact(
    pipeline: Pipeline, metrics: dict, duration_median: float, output_dir: str | Path
) -> None:
    """保存模型产物(model.joblib)、指标(metrics.json)与预测元数据(metadata.json)。

    metadata.duration_median 供预测页填充表单不收集的 duration 特征(US-4)。
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_dir / "model.joblib")
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    metadata = {
        "duration_median": float(duration_median),
        "random_state": RANDOM_STATE,
        "auc_threshold": DEFAULT_AUC_THRESHOLD,
    }
    (output_dir / METADATA_FILE).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

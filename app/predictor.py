"""预测核心逻辑:加载模型产物、构造输入、输出预测(纯逻辑,可测试)。

duration 特征在真实营销场景预测时未知:表单不收集,用训练集中位数填充
(中位数由训练脚本写入 models/metadata.json,见 US-3 技术备注)。
"""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from app.config import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS

MODEL_PATH = "models/model.joblib"
METADATA_PATH = "models/metadata.json"

LABEL_YES = "yes"
LABEL_NO = "no"
PROB_THRESHOLD = 0.5  # 默认决策阈值(后续可据业务调优)


def load_model(path: str | Path = MODEL_PATH) -> Pipeline:
    """加载训练产物;缺失时抛 FileNotFoundError(由页面捕获提示)。"""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"模型产物不存在: {path},请先运行 python -m scripts.train_model")
    return joblib.load(path)


def load_metadata(path: str | Path = METADATA_PATH) -> dict:
    """加载预测元数据(duration 中位数等)。"""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"元数据不存在: {path},请先运行 python -m scripts.train_model")
    return json.loads(path.read_text(encoding="utf-8"))


def feature_options(train_df: pd.DataFrame, column: str) -> list[str]:
    """分类特征的可选取值(来自训练数据,保证与训练一致)。"""
    return sorted(train_df[column].dropna().unique().tolist())


def build_input_row(
    categorical: dict[str, str], numeric: dict[str, float], duration_median: float
) -> pd.DataFrame:
    """按 schema 构造单行特征 DataFrame。

    numeric 不含 duration(表单不收集,见模块 docstring),统一用训练中位数填充。
    """
    row = {c: float(numeric[c]) for c in NUMERIC_COLUMNS if c != "duration"}
    row["duration"] = float(duration_median)
    row.update({c: str(categorical[c]) for c in CATEGORICAL_COLUMNS})
    return pd.DataFrame([row])[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS]


def predict(pipeline: Pipeline, input_df: pd.DataFrame) -> dict:
    """输出预测结论与认购概率。"""
    prob_yes = float(pipeline.predict_proba(input_df)[0, 1])
    label = LABEL_YES if prob_yes >= PROB_THRESHOLD else LABEL_NO
    return {"label": label, "prob_yes": prob_yes}

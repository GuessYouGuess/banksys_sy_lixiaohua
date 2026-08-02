"""认购预测页(US-4):点选/填写客户信息 → 实时预测认购概率与结论。

分类特征用下拉框(选项取自训练数据),数值特征用数字输入(范围取自训练数据);
duration 特征真实预测时未知,不收集,用训练中位数填充(见 US-3 技术备注)。
"""

import pandas as pd
import streamlit as st

from app.config import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS
from app.data_io import load_dataset
from app.predictor import (
    METADATA_PATH,
    MODEL_PATH,
    build_input_row,
    feature_options,
    load_metadata,
    load_model,
    predict,
)

DATASET_PATH = "data/train.csv"


@st.cache_data
def _train_df() -> pd.DataFrame:
    return load_dataset(DATASET_PATH)


@st.cache_resource
def _model():
    return load_model(MODEL_PATH)


@st.cache_data
def _metadata() -> dict:
    return load_metadata(METADATA_PATH)


def _numeric_bounds(df: pd.DataFrame, column: str) -> tuple[int, int, int]:
    """数值特征输入范围与默认值(取自训练数据,取整;默认取中位数)。"""
    lo = int(float(df[column].min()))
    hi = int(float(df[column].max()))
    default = int(float(df[column].median()))
    return lo, hi, default


def _categorical_inputs(df: pd.DataFrame) -> dict[str, str]:
    inputs = {}
    for column in CATEGORICAL_COLUMNS:
        options = feature_options(df, column)
        inputs[column] = st.selectbox(f"{column}", options, key=f"cat_{column}")
    return inputs


def _numeric_inputs(df: pd.DataFrame) -> dict[str, float]:
    inputs = {}
    for column in NUMERIC_COLUMNS:
        if column == "duration":
            continue  # 真实预测时未知,不收集(见模块 docstring)
        lo, hi, default = _numeric_bounds(df, column)
        inputs[column] = st.number_input(
            f"{column}({lo} ~ {hi})",
            min_value=float(lo),
            max_value=float(hi),
            value=float(default),
            step=1.0,
            key=f"num_{column}",
        )
    return inputs


def _show_result(result: dict, inputs: dict) -> None:
    prob = result["prob_yes"]
    label = result["label"]
    c1, c2 = st.columns(2)
    c1.metric("认购概率", f"{prob:.1%}")
    if label == "yes":
        c2.metric("预测结论", "✅ 会认购", delta=None)
    else:
        c2.metric("预测结论", "❌ 不会认购", delta=None)
    with st.expander("查看本次预测所用输入"):
        st.json(inputs)
    st.caption(f"模型决策阈值:{prob:.1%} ≥ 50% → 认购;duration 按训练中位数填充。")


def render() -> None:
    st.header("🎯 认购预测")
    try:
        train_df = _train_df()
        model = _model()
        metadata = _metadata()
    except FileNotFoundError as exc:
        st.error(f"模型产物缺失:{exc}")
        st.info("请先在仓库根目录运行 python -m scripts.train_model 训练模型。")
        return

    st.caption("填写客户信息(所有输入均来自训练数据范围,点选即可)")
    with st.form("predict_form"):
        categorical = _categorical_inputs(train_df)
        numeric = _numeric_inputs(train_df)
        submitted = st.form_submit_button("预测", type="primary")

    if submitted:
        input_row = build_input_row(categorical, numeric, metadata["duration_median"])
        result = predict(model, input_row)
        inputs = {**categorical, **numeric, "duration": metadata["duration_median"]}
        _show_result(result, inputs)

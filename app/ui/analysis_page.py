"""数据分析页(US-2):概览、分布、分组对比、相关性,支持交互筛选。

图表配色遵循 dataviz 规范:蓝=认购、橙=未认购(实体色不随排序变化);
计数/分布用单色蓝;相关矩阵用蓝红发散色(中性灰为 0)。
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.analysis import (
    categorical_value_counts,
    correlation_matrix,
    group_subscribe_rate,
    numeric_stats,
    target_counts,
)
from app.config import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, TARGET_COLUMN
from app.data_io import load_dataset

DATASET_PATH = "data/train.csv"

# dataviz reference palette(验证过的调色板)
COLOR_YES = "#2a78d6"  # 蓝:认购
COLOR_NO = "#eb6834"  # 橙:未认购
COLOR_BAR = "#2a78d6"  # 单色计数条
COLOR_RED = "#e34948"  # 相关矩阵负端
COLOR_MID = "#f0efec"  # 相关矩阵中性点(0)
GRID = "#e1e0d9"
INK = "#0b0b0b"


@st.cache_data
def _load() -> pd.DataFrame:
    return load_dataset(DATASET_PATH)


def _style(fig: go.Figure, height: int = 360) -> go.Figure:
    """统一图表样式:细网格、无背景、图例水平置顶。"""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=44, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", color=INK),
        xaxis=dict(gridcolor=GRID, zeroline=False),
        yaxis=dict(gridcolor=GRID, zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def _filter_controls(df: pd.DataFrame) -> pd.DataFrame:
    """分类特征筛选控件,返回过滤后的 DataFrame。"""
    column = st.selectbox("按分类特征筛选", ["无"] + CATEGORICAL_COLUMNS, key="filter_col")
    if column == "无":
        return df
    values = st.multiselect(
        f"选择「{column}」的取值", sorted(df[column].unique()), key="filter_vals"
    )
    return df[df[column].isin(values)] if values else df


def _overview(df: pd.DataFrame) -> None:
    st.subheader("数据集概览")
    total = len(df)
    pos = int(target_counts(df).get("yes", 0))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("总行数", f"{total:,}")
    c2.metric("认购数", f"{pos:,}")
    c3.metric("认购率", f"{pos / total:.1%}")
    c4.metric("特征数", len(df.columns) - 2)
    with st.expander("数据预览(前 5 行)"):
        st.dataframe(df.head(5))


def _target_distribution(df: pd.DataFrame) -> None:
    st.subheader("目标分布(认购 vs 未认购)")
    counts = target_counts(df).reindex(["yes", "no"], fill_value=0)
    fig = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker_color=[COLOR_YES, COLOR_NO],
            text=counts.values,
            textposition="outside",
        )
    )
    fig.update_layout(xaxis_title=TARGET_COLUMN, yaxis_title="客户数", showlegend=False)
    st.plotly_chart(_style(fig, 320), key="plot_target", width="stretch")


def _categorical_distribution(df: pd.DataFrame) -> None:
    st.subheader("分类特征分布")
    column = st.selectbox("分类特征", CATEGORICAL_COLUMNS, key="cat_col")
    counts = categorical_value_counts(df, column)
    fig = px.bar(x=counts.index, y=counts.values)
    fig.update_traces(marker_color=COLOR_BAR, text=counts.values, textposition="outside")
    fig.update_layout(xaxis_title=column, yaxis_title="客户数", showlegend=False)
    st.plotly_chart(_style(fig), key="plot_cat", width="stretch")


def _numeric_distribution(df: pd.DataFrame) -> None:
    st.subheader("数值特征分布")
    column = st.selectbox("数值特征", NUMERIC_COLUMNS, key="num_col")
    fig = px.histogram(df, x=column, nbins=40)
    fig.update_traces(marker_color=COLOR_BAR)
    fig.update_layout(xaxis_title=column, yaxis_title="客户数", showlegend=False)
    st.plotly_chart(_style(fig), key="plot_num", width="stretch")
    st.dataframe(numeric_stats(df))


def _group_compare(df: pd.DataFrame) -> None:
    st.subheader("分组对比(客户数与认购率)")
    column = st.selectbox("分组特征", CATEGORICAL_COLUMNS, key="group_col")
    grouped = group_subscribe_rate(df, column)

    counts_fig = px.bar(x=grouped.index, y=grouped["客户数"])
    counts_fig.update_traces(marker_color=COLOR_BAR, text=grouped["客户数"], textposition="outside")
    counts_fig.update_layout(xaxis_title=column, yaxis_title="客户数", showlegend=False)
    st.plotly_chart(_style(counts_fig), key="plot_group_counts", width="stretch")

    rate_fig = px.bar(x=grouped.index, y=grouped["认购率"])
    rate_fig.update_traces(
        marker_color=COLOR_YES, text=[f"{v:.1%}" for v in grouped["认购率"]], textposition="outside"
    )
    rate_fig.update_layout(
        xaxis_title=column, yaxis_title="认购率", yaxis_tickformat=".0%", showlegend=False
    )
    st.plotly_chart(_style(rate_fig), key="plot_group_rate", width="stretch")


def _correlation(df: pd.DataFrame) -> None:
    st.subheader("数值特征相关性")
    corr = correlation_matrix(df)
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            zmin=-1,
            zmax=1,
            colorscale=[[0, COLOR_RED], [0.5, COLOR_MID], [1, COLOR_YES]],
            colorbar=dict(title="r"),
            hovertemplate="%{y} × %{x}: %{z:.2f}<extra></extra>",
        )
    )
    st.plotly_chart(_style(fig, 520), key="plot_corr", width="stretch")


def render() -> None:
    st.header("📊 数据分析")
    df = _load()
    filtered = _filter_controls(df)
    st.caption(f"筛选后 {len(filtered):,} 行 / 共 {len(df):,} 行")
    if filtered.empty:
        st.warning("当前筛选结果为空,请调整筛选条件。")
        return
    _overview(filtered)
    _target_distribution(filtered)
    _categorical_distribution(filtered)
    _numeric_distribution(filtered)
    _group_compare(filtered)
    _correlation(filtered)

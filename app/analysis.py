"""分析逻辑纯函数:为分析页提供统计计算(不依赖 Streamlit,便于测试)。

约定:pdays=999 表示该客户此前从未被联系过(UCI 数据集语义)。
"""

import pandas as pd

from app.config import NUMERIC_COLUMNS, TARGET_COLUMN

# pdays=999 为"从未联系过"的哨兵值
PDAYS_NEVER = 999


def target_counts(df: pd.DataFrame) -> pd.Series:
    """目标变量各取值计数(认购/未认购)。"""
    return df[TARGET_COLUMN].value_counts().sort_index()


def categorical_value_counts(df: pd.DataFrame, column: str, top_n: int = 15) -> pd.Series:
    """分类特征取值计数;类别过多时合并尾部为"其他(含 N 类)"。"""
    counts = df[column].value_counts()
    if len(counts) <= top_n:
        return counts
    top = counts.head(top_n - 1)
    others = counts.iloc[top_n - 1 :].sum()
    top[f"其他({len(counts) - top_n + 1}类)"] = others
    return top.sort_values(ascending=False)


def group_subscribe_rate(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """按分类特征分组:客户数 + 认购率(正样本占比),按客户数降序。"""
    grouped = df.groupby(column, observed=True)[TARGET_COLUMN]
    result = pd.DataFrame(
        {"客户数": grouped.size(), "认购率": grouped.apply(lambda s: (s == "yes").mean())}
    )
    return result.sort_values("客户数", ascending=False)


def numeric_stats(df: pd.DataFrame) -> pd.DataFrame:
    """数值特征描述统计(count/mean/std/min/四分位/max)。"""
    cols = [c for c in NUMERIC_COLUMNS if c in df.columns]
    return df[cols].describe().T


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """数值特征两两相关矩阵(用于热力图)。"""
    cols = [c for c in NUMERIC_COLUMNS if c in df.columns]
    return df[cols].corr()

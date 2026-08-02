"""analysis 模块测试:统计纯函数。"""

import pandas as pd
import pytest

from app.analysis import (
    PDAYS_NEVER,
    categorical_value_counts,
    correlation_matrix,
    group_subscribe_rate,
    numeric_stats,
    target_counts,
)
from app.config import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, TARGET_COLUMN


def _small_df() -> pd.DataFrame:
    """3 行数据:1 个 yes、2 个 no;job 有重复类别。"""
    row = {c: 1.0 for c in NUMERIC_COLUMNS}
    row.update({c: "x" for c in CATEGORICAL_COLUMNS})
    return pd.DataFrame(
        [
            {**row, "id": 1, "job": "admin.", TARGET_COLUMN: "yes"},
            {**row, "id": 2, "job": "admin.", TARGET_COLUMN: "no"},
            {**row, "id": 3, "job": "student", TARGET_COLUMN: "no"},
        ]
    )


def test_target_counts():
    # Act
    counts = target_counts(_small_df())

    # Assert
    assert counts.to_dict() == {"no": 2, "yes": 1}


def test_categorical_value_counts_within_top_n():
    # Act
    counts = categorical_value_counts(_small_df(), "job", top_n=15)

    # Assert
    assert counts.to_dict() == {"admin.": 2, "student": 1}


def test_categorical_value_counts_truncates_tail():
    # Arrange: 20 个类别,top_n=6 → 前 5 + 1 个"其他"
    df = pd.DataFrame(
        {"c": [f"v{i}" for i in range(20)], "id": range(20), TARGET_COLUMN: ["no"] * 20}
    )
    # 补齐其余必需列(仅用 c 列做计数,其余填默认)
    for col in NUMERIC_COLUMNS:
        df[col] = 0
    for col in CATEGORICAL_COLUMNS:
        df[col] = "x"

    # Act
    counts = categorical_value_counts(df, "c", top_n=6)

    # Assert
    assert len(counts) == 6
    assert counts.iloc[0] == 15  # 尾部 15 类合并后数值最大,排最前
    assert "其他" in counts.index[0]


def test_group_subscribe_rate():
    # Act
    result = group_subscribe_rate(_small_df(), "job")

    # Assert
    assert result.loc["admin.", "客户数"] == 2
    assert result.loc["admin.", "认购率"] == 0.5
    assert result.loc["student", "认购率"] == 0.0
    # 按客户数降序
    assert list(result.index) == ["admin.", "student"]


def test_numeric_stats_shape():
    # Act
    stats = numeric_stats(_small_df())

    # Assert
    assert list(stats.index) == NUMERIC_COLUMNS
    assert {"count", "mean", "min", "max"} <= set(stats.columns)


def test_correlation_matrix_value():
    # Arrange: 两个完全线性相关的数值列
    df = _small_df()
    df["age"] = [1.0, 2.0, 3.0]
    df["duration"] = [2.0, 4.0, 6.0]

    # Act
    corr = correlation_matrix(df)

    # Assert
    assert corr.loc["age", "duration"] == pytest.approx(1.0)
    assert corr.loc["age", "age"] == pytest.approx(1.0)


def test_pdays_never_sentinel():
    # 语义约束:pdays 的"从未联系"哨兵值必须是 999
    assert PDAYS_NEVER == 999

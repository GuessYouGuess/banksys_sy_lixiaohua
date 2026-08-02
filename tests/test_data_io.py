"""data_io 模块测试:加载与 schema 校验。"""

import pandas as pd
import pytest

from app.config import CATEGORICAL_COLUMNS, ID_COLUMN, NUMERIC_COLUMNS, TARGET_COLUMN
from app.data_io import load_csv, load_dataset, validate_schema


def _valid_df() -> pd.DataFrame:
    """构造一个满足 schema 的最小 DataFrame。"""
    data = {c: [0] for c in NUMERIC_COLUMNS}
    data.update({c: ["a"] for c in CATEGORICAL_COLUMNS})
    data[ID_COLUMN] = [1]
    data[TARGET_COLUMN] = ["no"]
    return pd.DataFrame(data)


def _write_csv(tmp_path, df: pd.DataFrame) -> str:
    path = tmp_path / "data.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    return str(path)


def test_load_csv_reads_valid_file(tmp_path):
    # Arrange
    df = _valid_df()
    path = _write_csv(tmp_path, df)

    # Act
    loaded = load_csv(path)

    # Assert
    assert loaded.shape == df.shape
    assert list(loaded.columns) == list(df.columns)


def test_load_csv_missing_file_raises(tmp_path):
    # Act / Assert
    with pytest.raises(FileNotFoundError, match="不存在"):
        load_csv(tmp_path / "nope.csv")


def test_load_csv_empty_file_raises(tmp_path):
    # Arrange
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    # Act / Assert
    with pytest.raises(ValueError, match="为空"):
        load_csv(path)


def test_validate_schema_ok():
    # Arrange
    df = _valid_df()

    # Act
    result = validate_schema(df)

    # Assert
    assert result is df


def test_validate_schema_missing_column_raises():
    # Arrange: 删掉一列
    df = _valid_df().drop(columns=["job"])

    # Act / Assert
    with pytest.raises(ValueError, match="job"):
        validate_schema(df)


def test_validate_schema_bad_target_value_raises():
    # Arrange
    df = _valid_df()
    df.loc[0, TARGET_COLUMN] = "maybe"

    # Act / Assert
    with pytest.raises(ValueError, match="maybe"):
        validate_schema(df)


def test_validate_schema_nan_target_raises():
    # Arrange
    df = _valid_df()
    df.loc[0, TARGET_COLUMN] = None

    # Act / Assert
    with pytest.raises(ValueError, match="空值"):
        validate_schema(df)


def test_load_dataset_end_to_end(tmp_path):
    # Arrange
    path = _write_csv(tmp_path, _valid_df())

    # Act
    loaded = load_dataset(path)

    # Assert
    assert loaded[TARGET_COLUMN].iloc[0] == "no"


def test_real_train_csv_schema():
    """真实训练集可被加载并通过 schema 校验(数据门禁,见 03 规范)。"""
    # Arrange / Act
    df = load_dataset("data/train.csv")

    # Assert
    assert len(df) == 22500
    assert set(df[TARGET_COLUMN].unique()) == {"yes", "no"}

"""数据加载与 schema 校验(纯函数,便于单元测试)。"""

from pathlib import Path

import pandas as pd

from app.config import REQUIRED_COLUMNS, TARGET_COLUMN, TARGET_VALUES


def load_csv(path: str | Path) -> pd.DataFrame:
    """读取 UTF-8 CSV;文件不存在或为空时抛出可定位的错误。"""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"数据文件不存在: {path}")
    try:
        return pd.read_csv(path, encoding="utf-8")
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"数据文件为空: {path}") from exc


def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    """校验列完整性与目标取值,不合法抛 ValueError;合法则原样返回。"""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"缺少必需列: {missing}")
    if df[TARGET_COLUMN].isna().any():
        raise ValueError(f"目标列 {TARGET_COLUMN} 存在空值")
    bad = sorted(set(df[TARGET_COLUMN].unique()) - set(TARGET_VALUES))
    if bad:
        raise ValueError(f"目标列 {TARGET_COLUMN} 含非法取值: {bad}")
    return df


def load_dataset(path: str | Path) -> pd.DataFrame:
    """加载并校验数据集的便捷入口。"""
    return validate_schema(load_csv(path))

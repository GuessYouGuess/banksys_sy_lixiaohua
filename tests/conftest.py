"""测试共用 fixture:合成数据构造器(含 unknown 类别与不平衡目标)。"""

import numpy as np
import pandas as pd
import pytest

from app.config import CATEGORICAL_COLUMNS, ID_COLUMN, NUMERIC_COLUMNS, TARGET_COLUMN


@pytest.fixture
def make_df():
    def _make(n: int = 40, seed: int = 0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        data = {c: rng.normal(size=n) for c in NUMERIC_COLUMNS}
        data.update({c: rng.choice(["a", "b", "unknown"], size=n) for c in CATEGORICAL_COLUMNS})
        data[ID_COLUMN] = range(n)
        data[TARGET_COLUMN] = rng.choice(["no", "yes"], size=n, p=[0.85, 0.15])
        return pd.DataFrame(data)

    return _make

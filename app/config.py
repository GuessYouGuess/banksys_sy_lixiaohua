"""数据 schema 常量:数据分析、训练、预测共用(见 standards/00 目录地图)。

数据集 21 个特征 + 目标列 subscribe(与 data/train.csv 表头一致)。
"""

ID_COLUMN = "id"
TARGET_COLUMN = "subscribe"
TARGET_VALUES = ("yes", "no")

NUMERIC_COLUMNS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]

CATEGORICAL_COLUMNS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

REQUIRED_COLUMNS = [ID_COLUMN, *NUMERIC_COLUMNS, *CATEGORICAL_COLUMNS, TARGET_COLUMN]

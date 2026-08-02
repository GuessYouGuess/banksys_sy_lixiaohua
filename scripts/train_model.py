"""离线训练入口:训练 → 评估 → AUC 门禁 → 保存产物。

data/test.csv 无标签(仅特征列),评估使用 train.csv 内部 20% 分层划分。
用法:
    python -m scripts.train_model [--output models/]
退出码:0 成功;1 数据错误或 AUC 门禁失败(CI 门禁用)。
"""

import argparse
import json
import sys
from pathlib import Path

from app.data_io import load_dataset
from app.training import (
    DEFAULT_AUC_THRESHOLD,
    RANDOM_STATE,
    save_artifact,
    split_data,
    train_and_evaluate,
)

TRAIN_PATH = "data/train.csv"
DEFAULT_OUTPUT_DIR = "models"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="模型产物输出目录")
    args = parser.parse_args(argv)

    train_df = load_dataset(TRAIN_PATH)
    train_df, eval_df = split_data(train_df)

    pipeline, metrics, _, _ = train_and_evaluate(train_df, eval_df)
    duration_median = float(train_df["duration"].median())

    output_dir = Path(args.output)
    save_artifact(pipeline, metrics, duration_median, output_dir)

    print(f"训练完成(seed={RANDOM_STATE}): {json.dumps(metrics, ensure_ascii=False)}")
    if metrics["auc"] < DEFAULT_AUC_THRESHOLD:
        print(f"AUC 门禁失败:{metrics['auc']} < {DEFAULT_AUC_THRESHOLD}", file=sys.stderr)
        return 1
    print(f"AUC 门禁通过:{metrics['auc']} >= {DEFAULT_AUC_THRESHOLD}")
    print(f"产物已保存:{output_dir}/ (model.joblib / metrics.json / metadata.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

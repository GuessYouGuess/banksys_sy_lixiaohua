"""应用启动包装器:把仓库根目录加入 sys.path 后启动 Streamlit 应用。

streamlit run 只把脚本所在目录加入 sys.path;直接运行 app/main.py 时
import app 包会失败(容器内实测 ModuleNotFoundError,见 PROGRESS GOTCHAS)。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import main  # noqa: E402

main()

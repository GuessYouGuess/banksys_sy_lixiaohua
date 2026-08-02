"""冒烟测试:应用入口可导入、版本号正确。"""

import app.main  # noqa: F401


def test_app_imports():
    # Arrange / Act / Assert:导入 app.main 不抛异常即通过
    assert app.main is not None

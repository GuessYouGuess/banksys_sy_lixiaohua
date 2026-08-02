"""应用冒烟测试:侧边栏导航两页可渲染(streamlit AppTest 真实执行脚本)。"""

from streamlit.testing.v1 import AppTest

APP_PATH = "app/main.py"


def test_analysis_page_renders():
    # Arrange / Act: 默认选中第一个页面(数据分析),真实执行
    at = AppTest.from_file(APP_PATH, default_timeout=120).run()

    # Assert
    assert not at.exception
    assert at.title[0].value == "🏦 银行营销认购预测系统"  # 侧边栏标题
    assert at.header[0].value == "📊 数据分析"


def test_switch_to_predict_page():
    # Arrange
    at = AppTest.from_file(APP_PATH, default_timeout=120).run()

    # Act: 切换到认购预测页
    at.sidebar.radio[0].set_value("认购预测").run()

    # Assert
    assert not at.exception
    assert at.header[0].value == "🎯 认购预测"


def test_predict_page_submit_with_defaults():
    # Arrange: 进入认购预测页
    at = AppTest.from_file(APP_PATH, default_timeout=120).run()
    at.sidebar.radio[0].set_value("认购预测").run()

    # Act: 修改一个下拉框取值后提交表单
    at.selectbox(key="cat_job").set_value("student").run()
    at.button[0].click().run()

    # Assert: 无异常,展示认购概率指标
    assert not at.exception
    assert at.metric[0].label == "认购概率"
    assert at.metric[0].value.endswith("%")

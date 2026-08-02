"""Streamlit 应用入口:侧边栏导航(数据分析页 / 认购预测页)。"""

import streamlit as st

from app.ui.analysis_page import render as render_analysis
from app.ui.predict_page import render as render_predict

st.set_page_config(page_title="银行营销认购预测系统", page_icon="🏦", layout="wide")

PAGES = {"数据分析": render_analysis, "认购预测": render_predict}


def main() -> None:
    st.sidebar.title("🏦 银行营销认购预测系统")
    page = st.sidebar.radio("页面", list(PAGES), label_visibility="collapsed")
    PAGES[page]()


main()

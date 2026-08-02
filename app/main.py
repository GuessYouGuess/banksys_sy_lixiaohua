"""Streamlit 应用入口(占位)。

数据分析页与认购预测页将在后续模块中接入,当前仅保证可启动、
可被健康检查探测,以验证工程与部署链路。
"""

import streamlit as st

st.set_page_config(page_title="银行营销认购预测系统", page_icon="🏦", layout="wide")

st.title("银行营销认购预测系统")
st.write("数据分析与在线预测功能开发中,进度见 standards/PROGRESS.md。")

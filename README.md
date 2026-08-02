# banksys_sy_lixiaohua · 银行营销认购预测系统

> 项目文档与工程规范见 `standards/`,开发前请先阅读。

## 项目简介

基于银行电话营销公开数据集(UCI Bank Marketing),提供:

1. **数据分析交互页面** — 数据集概览、特征分布、分组对比、相关性分析,支持交互式筛选;
2. **在线认购预测系统** — 离线训练二分类模型,Web 端点选客户特征,实时预测是否认购定期存款及概率。

技术栈:Python 3.11 · Streamlit · scikit-learn · pytest · ruff · Docker
端口:8888(容器内固定,主机 8888~8898 自动回退)

## 开发状态

- [x] 需求与项目上下文(standards/00、01、PROGRESS)
- [ ] 仓库初始化与 CI/CD(进行中)

详细进度见 `standards/PROGRESS.md`。

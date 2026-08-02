# banksys_sy_lixiaohua · 银行营销认购预测系统

> 项目文档与工程规范见 `standards/`,开发前请先阅读。

## 项目简介

基于银行电话营销公开数据集(UCI Bank Marketing),提供两个功能:

1. **数据分析交互页面** — 数据集概览、特征分布、分组对比、相关性分析,支持交互式筛选;
2. **在线认购预测系统** — 离线训练二分类模型,Web 端点选客户特征,实时预测是否认购定期存款及概率。

## 技术栈

Python 3.11 · Streamlit · scikit-learn · pandas · Plotly · pytest · ruff · Docker · GitHub Actions

- 端口:容器内固定 **8888**;主机端口 8888~8898 自动回退
- 健康检查:`/_stcore/health`(Streamlit 内置端点)

## 快速开始(本地开发)

```bash
# 1) 建环境(推荐 conda,或 venv + python 3.11)
conda create -y -n banksys python=3.11
conda activate banksys

# 2) 装依赖(国内可用清华源)
pip install -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3) 启动应用(http://localhost:8888)
streamlit run run.py --server.port 8888
```

## 检查命令(提交前必跑)

```bash
ruff format --check .   # 格式
ruff check .            # 静态检查
pytest --cov=app --cov-fail-under=80   # 单测 + 覆盖率(≥80%)
```

## Docker 构建与运行

```bash
docker build -t banksys_sy_lixiaohua:latest .
docker run -d --name banksys_sy_lixiaohua --restart unless-stopped -p 8888:8888 banksys_sy_lixiaohua:latest
curl -fsS http://localhost:8888/_stcore/health   # 期望输出: ok
```

国内服务器构建慢时:

```bash
docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t banksys_sy_lixiaohua:latest .
```

## CI / CD

| 流程 | 触发 | 内容 |
|---|---|---|
| CI | PR / push main | ruff format+check、pytest+覆盖率 ≥80%、docker build |
| CD | 合并 main | SSH 同步代码 → `scripts/deploy.sh`(构建、端口回退、运行、健康检查) |

CD 需要 GitHub Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`(规范 `standards/05-cicd-standards.md`)。

## 目录结构

```text
banksys_sy_lixiaohua/
├── standards/            # 项目记忆与工程规范(先读 README.md)
├── data/                 # 公开教学数据(train.csv / test.csv,进 Git)
├── app/                  # Streamlit 应用与业务逻辑
├── scripts/              # 训练脚本 train_model.py、部署脚本 deploy.sh
├── models/               # 训练产物(joblib,进 Git)
├── tests/                # 单元测试
├── Dockerfile            # 生产镜像(仅运行依赖)
└── .github/workflows/    # ci.yml / cd.yml
```

## 开发状态

- [x] 需求与项目上下文(`standards/00`、`01`、`PROGRESS`)
- [x] 工程骨架 + 占位应用(M1)
- [ ] Docker + CI/CD(进行中)
- [ ] 数据分析页 / 离线训练 / 在线预测(后续 PR)

详细进度与决策见 `standards/PROGRESS.md`。

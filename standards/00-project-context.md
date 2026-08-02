# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。
> **填写方式**:把 `<...>` 替换成真实内容;用不到的行删掉。

---

## 1. 项目是什么

- **项目名称**:`banksys_sy_lixiaohua`(银行营销认购预测系统)
- **一句话目标**:基于银行电话营销数据集,提供交互式数据分析页面 + 离线训练/在线预测的认购(是否购买定期存款)预测系统
- **使用者/受益者**:银行营销分析人员(看数据)、客户经理(用预测筛选高潜客户)、课程评审(验证 CI/CD 闭环)
- **核心功能**:
  - 功能 1:数据分析交互页面(数据集概览、特征分布、分组对比、相关性,支持交互筛选)
  - 功能 2:在线认购预测(点选/输入客户特征 → 输出是否认购 + 概率)
- **输入/数据**:UCI Bank Marketing(银行电话营销)公开数据集
  - `data/train.csv` 22,500 行、`data/test.csv` 7,501 行,共 30,002 行
  - 21 个特征(`id`、`age`、`job`、`marital`、`education`、`default`、`housing`、`loan`、`contact`、`month`、`day_of_week`、`duration`、`campaign`、`pdays`、`previous`、`poutcome`、`emp_var_rate`、`cons_price_index`、`cons_conf_index`、`lending_rate3m`、`nr_employed`)+ 目标列 `subscribe`(yes/no)
  - 目标正样本占比约 13.1%(类别不平衡);分类列含 `unknown` 值(如 `default` 占 21.6%)
  - **公开教学数据,进 Git**(按 `05` 标准:公开教学数据可入库)

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 数据/ML 生态成熟,课程指定 |
| Web 框架 | Streamlit | 交互式数据分析 + 表单预测一栈搞定,零前端代码 |
| 机器学习 | scikit-learn(+joblib 产物) | 分类/预处理生态成熟,训练快、可复现 |
| 测试 | pytest | 标准、可接覆盖率 |
| 格式/静态检查 | ruff(format + check) | 快,课程指定 |
| 打包/运行 | Docker | 镜像化部署,CI 构建 + CD 部署一致 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
banksys_sy_lixiaohua/
├── standards/                 # AI 项目记忆与通用规范
├── data/                      # 公开教学数据,进 Git(train.csv / test.csv)
├── app/                       # Streamlit 应用与业务逻辑
│   ├── main.py                # 入口:侧边栏导航(数据分析页 / 认购预测页)
│   ├── data_io.py             # 数据加载与 schema 校验
│   ├── analysis.py            # 分析逻辑(纯函数,可测试)
│   ├── predictor.py           # 加载模型、构造特征、输出预测
│   └── ui/                    # 两个页面的 UI 组装
│       ├── analysis_page.py
│       └── predict_page.py
├── scripts/
│   └── train_model.py         # 离线训练入口(输出指标报告 + 模型产物)
├── models/                    # 训练产物(是否进 Git:待决策,见 PROGRESS ADR)
├── tests/                     # 单元测试(pytest)
├── requirements.txt           # 生产运行依赖
├── requirements-dev.txt       # 本地/CI 检查依赖
├── Dockerfile                 # 容器化(容器内端口 8888)
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
├── .gitignore
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | `pytest --cov --cov-fail-under=80` |
| 构建 | CI 内 `docker build` 成功(本地不强制装 Docker) |
| 业务/模型指标 | 测试集二分类 **AUC ≥ 0.75**(训练脚本非零退出即失败,作为 CI 门禁);预测接口响应 < 2s |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 大文件、数据集、模型产物是否进 Git:数据集为公开教学数据,**进 Git**;模型产物(joblib)体积小、**进 Git**(2026-08-02 确认),保证部署镜像确定性。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 模型产物与训练脚本必须**可复现**(固定随机种子)。

## 6. 部署/CI 占位符取值

> `guides/` 和 workflow 里的通用占位符,在本项目里的真实值只写这里。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys_sy_lixiaohua` | 仓库名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/banksys_sy_lixiaohua` | 服务器部署目录 |
| `<PORT>` | `8888` | 容器内端口固定 8888;主机端口 8888~8898 区间自动回退(见 `05` 第 4 节) |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/_stcore/health` | Streamlit 内置健康端点,返回 "ok" |
| `<SSH_USER>` | 待配置(GitHub Secrets) | `SSH_USER` |
| `<SSH_HOST>` | 待配置(GitHub Secrets) | 服务器公网 IP 或域名 |

# PROGRESS · banksys_sy_lixiaohua 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by Claude)

- **阶段**:`PR #1 CI 全绿,等待人类 Review+合并`(对应 `06` 六步流程:第 ⑤ 步「触发 PR」→ 第 ⑥ 步「人工审核→合并→CD」)
- **上一步完成**:
  - ⑤ PR #1 已创建:`https://github.com/GuessYouGuess/banksys_sy_lixiaohua/pull/1`(closes #1)
  - CI 复检全绿(run 30729332926):build ✓ / lint ✓ / test ✓(覆盖率 100%)
  - 修复提交 `f360c57`:pytest pythonpath 配置 + actions 升 v7
- **下一步 (TODO 第一条)**:✋ 等人类 Review + 合并 PR #1;合并后 CD 自动部署,AI 盯流水线并汇报端口/健康检查
- **阻塞项**:无(AI 不自行合并,合并是人类的动作)

> **⚠️ 分支策略修订(待人类确认)**:原计划 M1~M9 全在本分支。按 `04`/`06`「一需求一分支一 PR、PR < 400 行」,改为:
> - 本分支(`feature/1-init-engineering`,US-1)只做:骨架 + Dockerfile + CI/CD workflows + README → PR #1 完整演示 六步链(CI 全绿→人工合并→CD 部署→健康检查)
> - US-2 分析页 → `feature/2-analysis`;US-3 训练 → `feature/3-training`;US-4 预测 → `feature/4-prediction`(各自 PR,每轮复用已跑通的链路)

---

## 待办清单 (TODO,按优先级)

**文档(本会话)**
- [x] 读取 standards/README.md、00/01/PROGRESS、02~06
- [x] 填写 `00-project-context.md`(项目身份、目录地图、端口 8888、质量门槛)
- [x] 填写 `01-requirements.md`(US-1 ~ US-7,带验收标准)
- [x] 初始化本 PROGRESS.md,列出第一批 TODO
- [ ] **✋ 等待人类确认**:需求文档 + 两个待决策项(见 ADR)

**① 建仓 + 配 Secrets**
- [x] `gh repo create banksys_sy_lixiaohua --public`(开源仓库)✅ https://github.com/GuessYouGuess/banksys_sy_lixiaohua
- [x] main 只放最小引导提交(.gitignore / 占位 README,commit f087deb)
- [ ] **✋ 提示人类配置 GitHub Secrets**:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`(可用 `gh secret list` 核对)

**② 开 feature 分支**
- [ ] 从最新 main 切 `feature/1-init-engineering`(US-1 工程初始化,不直接改 main)

**③ 本地模块化开发(逐模块汇报,每个模块过确认门)**
- [x] **M1 工程骨架**(本分支):pyproject/ruff、requirements 拆分、app 包 + 占位入口、冒烟测试 ✅ 本地自检全绿,健康端点实测 `ok`
- [x] **M9 前移(本分支,PR #1 收尾)**:Dockerfile(端口 8888、`PIP_INDEX_URL`、HEALTHCHECK)、`ci.yml` + `cd.yml`、`scripts/deploy.sh`、`.gitattributes`、README、LICENSE ✅ 提交 `e5aed15`,YAML/bash 语法校验通过
- [ ] **US-2 → `feature/2-analysis`**:M2 数据层(`app/data_io.py` + 测试)→ M3 分析逻辑(纯函数 + 测试)→ M4 分析页;data/ 随本分支入库
- [ ] **US-3 → `feature/3-training`**:M5 离线训练(`scripts/train_model.py`、AUC ≥ 0.75 门禁、产物入 `models/`)
- [ ] **US-4 → `feature/4-prediction`**:M6 预测逻辑(`app/predictor.py` + 测试)→ M7 预测页 → M8 入口导航整合

**④ 本地 CI 自检(AI 执行,全绿才继续)**
- [ ] `ruff format --check .` + `ruff check .`
- [ ] `pytest --cov --cov-fail-under=80`
- [ ] 模型门禁:跑训练脚本确认 AUC ≥ 0.75(本地不强制 docker build)

**⑤ 触发 PR**
- [ ] push feature 分支 + `gh pr create`(PR 描述带 `closes #1`)
- [ ] 汇报 PR 链接与 CI 状态(`gh run watch`),CI 全绿后停下

**⑥ 人工审核 → 合并(人类)→ CD**
- [ ] 人类 Review + 合并(⭐ AI 绝不自行合并;分支默认保留)
- [ ] CD 自动部署,AI 盯流水线并汇报:落地端口、`/_stcore/health` 结果、访问地址

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-08-02 | 端口:容器内固定 8888;主机 8888~8898 自动回退 | 按 `05` 第 4 节标准,防 `port is already allocated` |
| 2026-08-02 | 健康检查用 `/_stcore/health` | Streamlit 内置健康端点,返回 "ok",无需额外接口 |
| 2026-08-02 | 数据集进 Git | 公开 UCI 教学数据(3.6MB),按 `05` 标准可入库,保证 CI/部署一致 |
| 2026-08-02 | 单入口 + 侧边栏导航两页 | 两个功能一个应用,符合"单一入口"需求(US-5) |
| 2026-08-02 | `duration` 特征:训练保留、预测表单不收集(中位数填充) | 经典陷阱:通话时长在真实预测时未知;策略固定并写注释 |
| 2026-08-02 | 模型产物**进 Git**(2026-08-02 人类确认) | joblib 小体积;部署镜像直接 COPY 产物,免构建期训练,镜像确定性好 |
| 2026-08-02 | ⏳ **待决策:二分类算法选择** | 推荐:逻辑回归 + 类别权重起步,GBM 作为对比;评估后固定一种,门禁 AUC ≥ 0.75 不变 |

---

## 已知坑 (GOTCHAS)

- **CI `ModuleNotFoundError: No module named 'app'`**:本地 `python -m pytest` 会隐式把 cwd 加入 sys.path,CI 直接调 `pytest` 控制台脚本不会。解决:pyproject `[tool.pytest.ini_options] pythonpath = ["."]`;验证:本地直接调 `pytest.exe` 复现修复后通过。
- **actions Node.js 20 弃用警告**:checkout@v4/setup-python@v5 被迫跑在 Node 24。解决:升 `actions/checkout@v7`、`actions/setup-python@v7`(2026-08-02 查最新 tag)。
- **push 网络超时**:`Failed to connect to github.com:443`(HTTPS 抖动)。解决:重试;注意 push 输出 `e5aed15..f360c57` 可能已成功而后续命令报错,用 `git ls-remote`/`gh run list` 核实。
- **conda 4.9.2 `run` 不支持多行 `-c`**:Windows 下 `conda run -n env python -c "<多行>"` 报 `AssertionError: Support for scripts where arguments contain newlines`。解决:写单行脚本或直调 `envs/<env>/python.exe`。
- **pandas 3.0 已安装**:本地/CI 均解析到 pandas 3.0.5(主要版本升级,行为有变),后续模块注意 API 兼容;已锁下限 `pandas>=2.0`。
- 数据风险(见 `01` 技术备注):分类列含 `unknown` 值(`default` 21.6%);正样本仅 13.1%(类别不平衡)。

---

## 里程碑 (DONE)

- [x] 需求与上下文文档初始化完成(2026-08-02)
- [ ] 仓库创建 + Secrets 配置(第 ① 步)— 仓库已建,待 Secrets
- [ ] 第一条 feature 分支(第 ② 步)
- [ ] 模块化开发完成 + 本地自检全绿(第 ③④ 步)
- [ ] 第一个 PR 合并(第 ⑤⑥ 步)
- [ ] CD 自动部署 + 健康检查通过

> 反臃肿:里程碑超过 15 条时,把更早内容合并成一行摘要,保持本文件可快速阅读。

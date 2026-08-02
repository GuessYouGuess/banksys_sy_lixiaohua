# PROGRESS · banksys_sy_lixiaohua 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by Claude)

- **阶段**:`feature 分支已开,待确认进入开发`(对应 `06` 六步流程:第 ② 步「开 feature 分支」)
- **上一步完成**:Secrets 已配置并核对(`SSH_HOST`/`SSH_PRIVATE_KEY`/`SSH_USER` 均在 2026-08-02 配置)
- **下一步 (TODO 第一条)**:✋ 等人类确认分支名 → 进入第 ③ 步 M1 开发
- **阻塞项**:无

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
- [ ] M1 工程骨架:pyproject/ruff 配置、`requirements.txt` + `requirements-dev.txt`、`.gitignore`
- [ ] M2 数据层:`app/data_io.py` 加载 + schema 校验(纯函数)+ 测试
- [ ] M3 分析逻辑:`app/analysis.py` 统计纯函数 + 测试
- [ ] M4 数据分析页:`app/ui/analysis_page.py`(概览、分布、分组对比、相关性、筛选)
- [ ] M5 离线训练:`scripts/train_model.py`(固定种子、评估报告、AUC ≥ 0.75 门禁、产物入 `models/`)
- [ ] M6 预测逻辑:`app/predictor.py`(预处理一致性 + 输入校验)+ 测试
- [ ] M7 认购预测页:`app/ui/predict_page.py`(点选表单 + 结果展示)
- [ ] M8 入口:`app/main.py` 侧边栏导航两页 + 缓存
- [ ] M9 Docker + 文档:Dockerfile(端口 8888、`PIP_INDEX_URL` 参数)、README、LICENSE

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

- 暂无真实故障(尚未进入开发)。已知数据风险(已写进 `01` 技术备注):分类列含 `unknown` 值(`default` 21.6%)需明确处理策略;正样本仅 13.1%(类别不平衡,不能只看准确率)。
- 后续 CI/CD 真实故障必须按 `06` 第 5 节「故障反哺铁律」写回本文件。

---

## 里程碑 (DONE)

- [x] 需求与上下文文档初始化完成(2026-08-02)
- [ ] 仓库创建 + Secrets 配置(第 ① 步)— 仓库已建,待 Secrets
- [ ] 第一条 feature 分支(第 ② 步)
- [ ] 模块化开发完成 + 本地自检全绿(第 ③④ 步)
- [ ] 第一个 PR 合并(第 ⑤⑥ 步)
- [ ] CD 自动部署 + 健康检查通过

> 反臃肿:里程碑超过 15 条时,把更早内容合并成一行摘要,保持本文件可快速阅读。

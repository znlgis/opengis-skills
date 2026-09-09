---
name: my-opencode-deepseek-config
description: "Use when deploying, tuning, or extending the OpenCode × DeepSeek V4 optimal configuration (orchestrator routing, 12 agents, thinking tiers, prompt-cache prefix discipline, DCP compaction, permissions baseline, 25 skills, slash commands) — installing to another machine, adding an agent or skill, adjusting model routing/cost, or troubleshooting why an agent routes/compacts/thinks a certain way."

tags:
  - opencode
  - deepseek
  - agent-config
  - prompt-cache
  - model-routing
  - ai
---

> **项目地址：** <https://github.com/znlgis/my-opencode-deepseek-config>
>
> **许可证：** MIT License（最新 tag：v4.0.0）
>
> **文档：** <https://github.com/znlgis/my-opencode-deepseek-config/blob/main/README.md>（中英双语）
>
> **前置条件：** OpenCode ≥ v1.18.x（DeepSeek provider 内置）、DeepSeek API Key（<https://platform.deepseek.com/api_keys>）

## 概述

OpenCode 多 Agent 框架下 DeepSeek V4 模型族（Pro + Flash + Flash-Vision）的**最优纯配置方案**——零额外依赖，全部能力由 `opencode.jsonc` + `agents/*.md` + `skills/*/SKILL.md` + `AGENTS.md` 实现。核心理念：**Token 效率优先，用最小的上下文成本达到最好的开发效果**。

当前配置概览：

- 默认主 Agent `orchestrator`（意图门控 + 模型感知路由 + 后备链）；第二 primary `solo`（单模型内联执行、零委派）
- 3 模型矩阵：`deepseek/deepseek-v4-pro`（深度推理/审查/重型实现）、`deepseek/deepseek-v4-flash`（路由/规划/常规执行，**provider 层关 thinking + temperature 0**）、`deepseek/deepseek-v4-flash-vision-exp`（多模态）
- 12 个 Agent、25 个技能（按需加载）、17 个 slash 命令、`subagent_depth: 3`、`share: "disabled"`
- 上下文双引擎：内置 compaction（opencode.jsonc，自动触发 + prune 旧工具输出）+ DCP 插件（dcp.jsonc，主动去重 + 按模型成本分级压缩阈值）

**环境要求：** OpenCode ≥ v1.18.x；后台子智能体委派需环境变量 `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`（未设置时后台委派报错，应退回前台串行）。

---

## 安装部署

```bash
git clone https://github.com/znlgis/my-opencode-deepseek-config.git
```

**方式一（推荐）：环境变量指向 `opencode/` 子目录**

```powershell
# Windows 永久生效
[Environment]::SetEnvironmentVariable("OPENCODE_CONFIG_DIR", "D:\path\to\my-opencode-deepseek-config\opencode", "User")
```

```bash
# Linux / macOS
export OPENCODE_CONFIG_DIR="$HOME/path/to/my-opencode-deepseek-config/opencode"
```

**方式二：符号链接到 `~/.config/opencode`**（Windows 需管理员 `New-Item -ItemType SymbolicLink`；类 Unix `ln -s .../opencode ~/.config/opencode`）

**API Key：** TUI 内 `/connect` → DeepSeek → 粘贴 Key（自动存 `~/.local/share/opencode/auth.json`），或环境变量 `DEEPSEEK_API_KEY`。

**验证：** `/models` 显示 `deepseek/deepseek-v4-pro`；Agent 列表含 `orchestrator`/`planner`/`deep-worker` 等 12 个。

---

## Agent 结构（12 个）

| Agent | 模型档 | 权限 | 作用 |
|-------|--------|------|------|
| `orchestrator` | flash · thinking 关 | 读写 | 默认入口：意图门控 + 路由 + 后备链 |
| `solo` | pro · 默认 high | 读写 | 单模型内联执行器，`permission.task: "*": "deny"` 零委派 |
| `planner` | flash + `reasoningEffort: low` | 读写 | 规划、架构、拆解任务 |
| `deep-worker` | pro | 读写 | 重型实现、多文件改动（禁研究/禁委托，带拒绝契约） |
| `light-orchestrator` | flash + low | 读写 | 轻量任务、单文件编辑 |
| `oracle` | pro | **只读** | 根因分析、深度理解代码 |
| `reviewer` | pro | **只读** | 单遍代码审查（证据门控） |
| `explore` / `librarian` | flash · thinking 关 | **只读** | 代码库搜索 / 文档检索（librarian 无任何 bash 权限） |
| `consultant` / `ui-builder` | flash · thinking 关 | 读写 | 方案建议 / 前端 UI |
| `vision` | flash-vision-exp | 读写 | 图像/截图/图表/UI 稿理解 |

只读 Agent 真只读化：`edit: deny` + bash 白名单（默认 deny，仅放行 `git status/diff/log/show/blame`、`rg` 等只读子命令）。各 agent 带 `skills` 白名单（默认 deny + 按职责放行，防误加载重型 skill）。

**思考分档关键点：** `reasoning_effort` 是**请求级**思考强度（`low`/`high`/`max`），不是模型 ID——经 agent frontmatter `options`（camelCase `reasoningEffort`，深度合并到 `model.options`）设置，3 模型矩阵不变。

---

## 路由策略与成本

- **Trivial → flash off**（搜索/查询/咨询/UI/探索）；**Routine → flash low**（规划/常规多文件实现）；**Deep/uncertain → pro high**（根因分析/审查/重型实现）
- flash 无法胜任时自动升级 pro（带完整上下文）
- 价格（USD / 1M tokens，off-peak，peak 翻倍）：flash 输入 0.22 / 输出 0.66；pro 输入 0.66 / 输出 1.98（**pro = 3× flash**）；`cache_read` 0.007 / 0.022（比输入价便宜约 **30×**）
- 成本估算脚本：`scripts/estimate-cost.js`

### 提示缓存纪律（最大杠杆）

- **字节稳定前缀**：agent 提示词、AGENTS.md、规则顺序保持不变；时间戳/随机 ID/动态文件列表等易变内容置于 payload **尾部**
- **冻结工具集**：不在会话中途重排 tool schema 或注入规则
- 插件固定版本（superpowers `#v6.3.0`、DCP `@3.1.15`）防自动更新导致前缀漂移
- DCP `modelMaxLimits`/`modelMinLimits`：pro 更早压缩、flash 更晚压缩

---

## Slash 命令（17 个）

| 命令 | 目标 | 用途 |
|------|------|------|
| `/deep` `/quick` `/ui` `/vision` `/plan` `/oracle` | 对应 agent | 直达路由：重型实现 / 轻量编辑 / 前端 / 图像 / 规划 / 溯源 |
| `/review [PR号]` | reviewer | PR 模式回帖 GitHub（gh-cli），无参审查本地 diff；>500 有效行先报 scoped 计划 |
| `/commit` | light-orchestrator | Conventional Commits 提交信息 |
| `/release` | deep-worker（git-release） | Tag 发布准备 |
| `/reflect` | oracle（reflect） | 发现摩擦 → 配置优化建议 |
| `/handoff` | light-orchestrator | 会话压缩为交接文档 |
| `/codemap` `/learn` `/simplify` `/rmslop` | explore / deep-worker / oracle+light-orchestrator / deep-worker | 结构图 / 经验沉淀 AGENTS.md / 行为保持简化 / 死代码清理 |
| `/spec-propose` `/spec-apply` | planner / deep-worker（spec-workflow） | 规约驱动变更：提案 → 按 tasks 实现归档 |

典型工作流：新功能 `/spec-propose → /spec-apply → /review`；排障 `/oracle → /deep → /rmslop → /commit`。

---

## 技能清单（25 个，`opencode/skills/`）

按需加载（原生 `skill` 工具），代表性分组：

- **过程纪律**：`grilling`、`wait-what`、`diagnosing-bugs`、`verification` 类（superpowers 插件另提供 brainstorming/TDD/systematic-debugging）
- **代码质量**：`code-review`、`security-review`、`simplify`、`remove-deadcode`、`codebase-design`、`domain-modeling`、`grill-with-docs`
- **Git/GitHub**：`git-master`、`git-release`、`resolving-merge-conflicts`、`gh-cli`、`to-tickets`、`triage`
- **文档/知识**：`verify-with-docs`、`writing-for-agents`、`codemap`、`handoff`、`reflect`、`office-docs`、`vision-prep`、`opencode-config`、`spec-workflow`

---

## 常见问题

| 问题 | 处理 |
|------|------|
| 改动 `~/.config/opencode` 后不生效 | 它是独立副本（非符号链接）时须运行 `scripts\sync-config.ps1` 从仓库源同步（支持 `-Src` 指定源目录） |
| 后台委派报 `background: true` 错误 | 未设 `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`；设置之或退回前台串行委派 |
| 成本突然翻倍 | 检查是否 peak 时段计价；确认 trivial 任务没有落到 pro（pro = 3×）；确认前缀未被动态内容打散（`cache_read` 便宜 30×） |
| flash agent 输出质量差 | 需要思考的中档任务给 `planner`/`light-orchestrator`（flash + thinking 开 + `reasoningEffort: low`），而不是 flash 关思考档 |
| 新模型/新 provider 想加 | 本仓库约束：仅 DeepSeek V4 三模型，不引入其他模型 |

---

## 参考资源

- 仓库：<https://github.com/znlgis/my-opencode-deepseek-config>
- 配置目录：`opencode/`（`opencode.jsonc`、`dcp.jsonc`、`AGENTS.md`、`agents/`、`skills/`）
- 借鉴来源：[oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)、[oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim)、[anomalyco/opencode](https://github.com/anomalyco/opencode)、[mattpocock/skills](https://github.com/mattpocock/skills)、[OpenSpec](https://github.com/Fission-AI/OpenSpec)
- 相关 SKILL：本仓库 [deepseek-harness](../../ai/deepseek-harness/SKILL.md)（DeepSeek 官方模型配置指南）、[oh-my-openagent](../../ai/oh-my-openagent/SKILL.md)（多 agent 编排插件）

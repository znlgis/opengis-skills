---
name: my-opencode-deepseek-config
description: "Use when deploying or tuning the znlgis OpenCode v2 × DeepSeek Flash config — orchestrator routing, 12 agents, thinking tiers via model variants (#low/#high), prompt-cache prefix discipline, limit.input compaction, permission baseline, 23 skills; also when a change has no effect because OpenCode fell back to v1 key names (providers/permissions/media.image), background delegation errors without OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS, or ~/.config/opencode needs sync-config.ps1."
tags:
  - opencode
  - deepseek
  - agent-config
  - prompt-cache
  - model-routing
  - permissions
  - agent
  - ai
---

> **项目地址：** <https://github.com/znlgis/my-opencode-deepseek-config>
>
> **许可证：** MIT（最新 tag：v5.0.0）
>
> **文档：** <https://github.com/znlgis/my-opencode-deepseek-config/blob/main/README.md>（中英双语）
>
> **前置条件：** OpenCode **v2**（桌面版自带 CLI 实测 2.2.0，截至 2026-10；1.18.x 及更早不再支持）、DeepSeek API Key（<https://platform.deepseek.com/api_keys>）

## 概述

在 OpenCode v2 多 Agent 框架下，只用 `deepseek/deepseek-flash` **一个模型**、用 thinking 档位区分 Agent 分工的纯配置方案——零额外依赖，能力全部由 `opencode.jsonc` + `agents/*.md` + `skills/*/SKILL.md` + `AGENTS.md` 实现。核心理念：**Token 效率优先，用最小的上下文成本达到最好的开发效果**。

- 默认主 Agent `orchestrator`（意图门控 + 路由 + 后备链）；第二 primary `solo`（单模型内联执行、零委派）
- 单模型三档：`deepseek/deepseek-flash`（thinking 关 + `temperature: 0`）、`#low`、`#high`，三档同价，差别只在 reasoning token 数量
- 12 个 Agent、23 个技能、18 个 slash 命令；`experimental.subagent_depth: 2`；`share: "disabled"`
- 权限基线：`read` 放行、`shell` 默认 `ask`、`.env` 类 `deny`、外部目录 `ask`
- 上下文压缩只用内置 compaction：`limit.input` 显式声明工作窗口，触发点 = `limit.input − compaction.buffer`
- 唯一插件 superpowers（git URL 固定 tag `#v7.0.1`），纯 skill 注入，不提供模型映射

---

## 安装部署

```powershell
# 1. 克隆
git clone https://github.com/znlgis/my-opencode-deepseek-config.git

# 2. 指向仓库内的 opencode/ 配置目录（当前会话生效）
$env:OPENCODE_CONFIG_DIR = "D:\path\to\my-opencode-deepseek-config\opencode"

# 3. API Key（也可启动后在 TUI 里 /connect）
$env:DEEPSEEK_API_KEY = "sk-your-key-here"

# 4. 启动
opencode
```

永久生效（Windows）：

```powershell
[Environment]::SetEnvironmentVariable("OPENCODE_CONFIG_DIR", "D:\path\to\my-opencode-deepseek-config\opencode", "User")
```

Linux / macOS：把 `export OPENCODE_CONFIG_DIR="$HOME/path/to/my-opencode-deepseek-config/opencode"` 追加到 `~/.bashrc` 或 `~/.zshrc`。

替代方案是把 `opencode/` 软链到全局配置路径（Windows 需管理员；Linux/macOS 用 `ln -s`）。

```bash
# 后台子智能体委派必须开启，否则 background: true 直接报错
export OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true
```

验证三步：

1. `/models` 显示 `deepseek/deepseek-flash`
2. Agent 列表有 12 个自定义 Agent
3. 任意提需求时 `orchestrator` 自动分析并路由（想跳过路由就直接用 `/quick`、`/deep`、`/review`）

> **必须由 OpenCode v2.x 运行。** PATH 上的 `opencode` 可能是旧版（1.18.4）；用旧版启动会走 V1→V2 迁移路径，本文描述的路由、权限、压缩、名册行为都不成立。

改完仓库文件后必须同步（`~/.config/opencode` 是独立副本，不是符号链接）：

```powershell
.\scripts\sync-config.ps1              # 可用 -Src 指定源目录
```

同步排除 `node_modules`/`.git`/包清单与锁文件；`skills/`、`agents/` 的删除清理走 git 索引，`git rm` 后即使未提交也会在同步时删掉目标目录里的同名副本。

---

## 单模型与三档 thinking

本仓库只使用 **一个模型** `deepseek/deepseek-flash`（V4.1 Flash，原生多模态），不引入任何其他模型。Agent 之间的差异只有一个维度——**思考档位**，用模型 variant 表达：

| 档位 | 模型引用 | 机制 | 典型 Agent |
|------|----------|------|------------|
| 省（trivial） | `deepseek/deepseek-flash` | body `{"thinking":{"type":"disabled"}}` + `temperature: 0` | `orchestrator`/`explore`/`librarian`/`consultant`/`ui-builder`/`vision` |
| 中（routine） | `deepseek/deepseek-flash#low` | thinking 开 + `settings.reasoningEffort: low` | `planner`/`light-orchestrator` |
| 高（deep） | `deepseek/deepseek-flash#high` | thinking 开 + `settings.reasoningEffort: high` | `deep-worker`/`oracle`/`reviewer`/`solo` |

思考强度由两个**请求参数**控制，且都声明在 `opencode.jsonc` 的**模型层**：

- **thinking 开关**：`{"thinking":{"type":"enabled"|"disabled"}}`，是**请求体（body）字段**
- **thinking 强度**：`settings.reasoningEffort`（配置里 camelCase，线上是 `reasoning_effort`）——这是 aisdk 层唯一会转成 `reasoning_effort` 的路径

```jsonc
"providers": {
  "deepseek": {
    "models": {
      "deepseek-flash": {
        "body": {
          "thinking": { "type": "disabled" },
          "temperature": 0
        },
        "capabilities": {
          "tools": true,
          "input": ["text", "image"],
          "output": ["text"]
        },
        "variants": [
          { "id": "low",  "settings": { "reasoningEffort": "low" },  "body": { "thinking": { "type": "enabled" } } },
          { "id": "high", "settings": { "reasoningEffort": "high" }, "body": { "thinking": { "type": "enabled" } } }
        ]
      }
    }
  }
}
```

> **写法陷阱：** `thinking`/`temperature` 写进 `settings` 不生效（openai-chat 协议不实现该 option）；`reasoningEffort` 写进 Agent 的 `options` 也不生效（`options` 只落到 `request.body`）。两者都必须写在模型层：toggle 进 `body`、effort 进 `settings`。Agent frontmatter 里不再出现任何思考参数。

模型 ID 命名规则是 `provider_id/model_id`，variant 用 `#` 后缀——本仓库只有 `deepseek/deepseek-flash`、`#low`、`#high` 三个引用。

**官方语义要点**（以 OpenCode v2 thinking_mode 文档为准）：思考模式默认打开、effort 默认 `high`，所以只有默认档（显式 `disabled`）真能省 reasoning token；`#high` 只是把默认值写明，`#low` 是唯一存在的中间档。思考模式**不支持** `temperature`/`presence_penalty`/`frequency_penalty`（传入不报错也不生效）；`top_p` 只在思考模式下生效（有效范围 0.95–1.0），所以本配置不设 `top_p`。

---

## v2 原生键名（本仓库唯一写法）

本仓库是 **OpenCode v2 专属配置**，只写 v2 原生键：

| 用途 | v2 键 | 不要写（v1 拼写） |
|------|-------|-------------------|
| 插件 | `plugins` | `plugin` |
| 模型 | `providers` / `models` | `provider` |
| Agent / 命令 | `agents` / `commands` | `agent` / `command` |
| 权限 | `permissions`（有序 `{action, resource, effect}`，action 为 `shell`/`subagent`） | `permission`（`bash`/`task`） |
| 附件 | `media.image` | `attachment` |
| 嵌套深度 | `experimental.subagent_depth` | 顶层 `subagent_depth` |
| 压缩 | `compaction` = `{auto, keep, buffer}` | `prune`/`tail_turns`/`reserved` |

只要文件里出现任一 v1 触发键（`provider`/`agent`/`command`/`plugin`/`permission`/`tools`/`attachment`/`small_model` 等），v2 就改走 V1→V2 迁移路径，本文描述的行为不再成立。`$schema` 保持 `https://opencode.ai/config.json`。

---

## Agent 结构（12 个）

### Primary

| Agent | 模型 | 作用 |
|-------|------|------|
| `orchestrator` | flash（thinking 关） | 默认入口：意图门控（Intent Gate）+ 路由 + 后备链 |
| `solo` | `#high` | 单模型内联执行器：`{action: subagent, resource: "*", effect: deny}` 零委派，全程在当前会话完成 |

### Subagents

| Agent | 模型 | 权限 | 作用 |
|-------|------|------|------|
| `planner` | `#low` | 读写 | 规划、架构、拆解任务 |
| `deep-worker` | `#high` | 读写 | 重型实现、多文件改动、复杂调试 |
| `oracle` | `#high` | **只读** | 根因分析、深度理解代码 |
| `reviewer` | `#high` | **只读** | 代码审查升级层 |
| `light-orchestrator` | `#low` | 读写 | 轻量任务、单文件编辑 |
| `explore` | flash | **只读**（仅可写 `.opencode/codemap.md`） | 代码库搜索、并行探索 |
| `librarian` | flash | **只读**（无任何 shell 白名单） | 文档检索、Web 搜索 |
| `ui-builder` / `consultant` | flash | 读写 | 前端 UI / 方案建议 |
| `vision` | flash | 读写（shell 仅限 `ask` 门控脚本） | 图像/截图/图表理解 |

只读 Agent 真只读化：`edit: deny` + shell 白名单（默认 deny 全部，仅放行 `git status/diff/log/show/blame/grep`、`rg` 等只读子命令；`oracle`/`reviewer` 另允许 `gh pr view/diff`、`gh api` 以支持回帖）。

各 Agent 带 `skills` 白名单（默认 deny + 按职责放行）。**白名单不只是权限**：被 deny 的 skill 不会出现在该 Agent 的 skill 名册里，所以这份名单同时就是常驻上下文预算。

---

## 路由策略与成本

- **Trivial → thinking off**：搜索、查询、咨询、UI、探索、文档检索
- **Routine → `#low`**：规划、常规多文件实现
- **Deep/uncertain → `#high`**：深度推理、根因分析、重型多文件实现
- **代码审查两级**：`/review` 默认 thinking off 初检（≤8 个逻辑文件且 ≤300 有效行、无高风险触发），命中升级条件才委派 `reviewer`（`#high`）；`/deep-review` 强制全量
- **自动升级**：便宜档无法胜任时升级到 `#high`（带完整上下文，并说明升级理由）

价格（USD / 1M tokens，off-peak；peak = ×2，北京时间周一至周五 09:00–12:00 与 14:00–18:00）：

| 模型 | 输入 | 输出 | 缓存命中 cache_read |
|------|------|------|---------------------|
| `deepseek-flash` | 0.15 | 0.60 | 0.003 |

两个成本杠杆：

1. **思考档位**：三档同一单价，差别只在 reasoning token 数量（按输出价计费）——升档是多花输出 token，不是换更贵的单价
2. **提示词缓存**：`cache_read` 比输入价便宜 **50×**（0.003 vs 0.15），保住字节稳定前缀就是省钱

```bash
node scripts/estimate-cost.js     # 按实际 token 数估算
```

### 提示缓存纪律（最大杠杆）

- **字节稳定前缀**：agent 提示词、`AGENTS.md`、规则顺序保持字节稳定；时间戳/随机 ID/动态文件列表放 payload **尾部**
- **冻结工具集**：不在会话中途重排 tool schema 或注入规则
- **插件固定版本**（superpowers `#v7.0.1`）防自动更新导致前缀漂移
- **压缩窗口按模型声明**：`limit.input` 显式写出（`131072−16000=115,072`），保留尾部 `keep.tokens: 12000`

---

## Slash 命令（18 个）

| 命令 | Agent | 用途 |
|------|-------|------|
| `/deep` `/quick` `/ui` `/vision` `/plan` `/oracle` | 对应 Agent | 直达路由：重型实现 / 轻量编辑 / 前端 / 图像 / 规划 / 溯源 |
| `/review [PR]` | `light-orchestrator`（code-review）→ 按需升级 `reviewer` | flash 初检；带 PR ref/URL 时回帖 GitHub |
| `/deep-review [PR]` | `reviewer` | 强制 `#high` 全量审查，跳过低档初检 |
| `/commit` | `light-orchestrator` | Conventional Commits 提交信息 |
| `/release` | `deep-worker`（git-release） | Tag 发布准备 |
| `/reflect` | `oracle`（reflect） | 发现摩擦 → 配置优化建议 |
| `/handoff` | `light-orchestrator`（handoff） | 会话压缩为交接文档 |
| `/codemap` `/learn` `/simplify` `/rmslop` | explore / deep-worker / light-orchestrator+oracle / deep-worker | 结构图 / 经验沉淀 / 行为保持简化 / 死代码清理 |
| `/spec-propose` `/spec-apply` | planner / deep-worker（spec-workflow） | 规约驱动变更：提案 → 按 tasks 实现归档 |

---

## 典型工作流

### 工作流一：新功能（规约驱动）

1. `/spec-propose` 交给 `planner`：澄清意图、拆解任务、产出提案
2. `/spec-apply` 交给 `deep-worker`：按 tasks 逐项实现（重型多文件改动走 `#high`）
3. `/review` 交给只读 `reviewer`：本地 diff 单遍审查（带 PR 号则回帖 GitHub）
4. `/commit` 由 `light-orchestrator` 生成 Conventional Commits 提交信息

### 工作流二：排障与清理

1. `/oracle` 只读根因分析（`#high`）
2. `/deep` 让 `deep-worker` 落地修复
3. `/rmslop` 清死代码，`/simplify` 做行为保持的简化
4. `/commit` 收尾；摩擦较大时 `/reflect` 让 oracle 给出配置优化建议

### 工作流三：换一台机器复现环境（端到端）

输入：一台装了 OpenCode v2 的机器 + DeepSeek Key；输出：可用的 orchestrator 路由。

1. `git clone` 仓库，把 `OPENCODE_CONFIG_DIR` 指向仓库内 `opencode/` 子目录
2. `/connect` 填 DeepSeek Key（或设 `DEEPSEEK_API_KEY`）
3. 后台委派前设 `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`
4. `/models` 确认 `deepseek/deepseek-flash`，Agent 列表确认 12 个齐全
5. `node scripts/validate-jsonc.js` 校验配置；用 `opencode-cli.exe debug config` 看已解析结果

### 工作流四：改配置并同步回全局

1. 按「配置变更点速查」定位到 `opencode.jsonc` / `agents/<name>.md` / `AGENTS.md` / `skills/<name>/SKILL.md`
2. 改完 `.\scripts\sync-config.ps1` 同步到 `~/.config/opencode`
3. 重载：桌面 v2 用 `opencode-cli.exe reload`，或重启 opencode
4. 校验：`node scripts/validate-jsonc.js`，必要时 `opencode-cli.exe debug config` 对比解析结果

---

## 配置变更点速查

| 想改的东西 | 文件 | 位置 |
|-----------|------|------|
| 模型清单 / 价格 / thinking / temperature | `opencode/opencode.jsonc` | `providers.deepseek.models` |
| 默认 Agent、嵌套深度、工具输出上限、压缩参数、附件缩放 | `opencode/opencode.jsonc` | 顶层同名键 |
| 权限（读 / shell / skill / 外部目录） | `opencode/opencode.jsonc` | `permissions` |
| 内置 agent 的模型与一次性 agent 的 skill 屏蔽 | `opencode/opencode.jsonc` | `agents`（inline 权限追加在最后，last-match-wins） |
| 快捷命令的 Agent 与模板 | `opencode/opencode.jsonc` | `commands` |
| 单个 Agent 的模型、工具、skill 白名单、拒绝契约 | `opencode/agents/<name>.md` | frontmatter + 正文 |
| 全局行为规则 | `opencode/AGENTS.md` | 对应小节 |
| 插件版本（pin） | `opencode/opencode.jsonc` | `plugins` |
| 压缩触发窗口 / buffer / 保留尾部 | `opencode/opencode.jsonc` | `limit.input` + `compaction` |

---

## 最佳实践

1. **保住提示缓存前缀**：agent 提示词、`AGENTS.md`、规则顺序字节稳定；易变内容放尾部；插件锁版本
2. **按成本分档**：三档同价，cost 只随 reasoning token 增长——默认档关 thinking 才是真省
3. **压缩窗口算出来**：`limit.input` 显式声明，触发点 = `limit.input − compaction.buffer`，不要继承默认
4. **只读 Agent 真只读**：`edit: deny` + shell 白名单；skills 白名单默认 deny 按职责放行
5. **名册即预算**：skill 的 name+description 每轮常驻；不用就删，别留"备用"
6. **配置改动后同步**：`~/.config/opencode` 是独立副本，改完跑 `scripts\sync-config.ps1`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 改动 `~/.config/opencode` 后不生效 | 它是独立副本（非符号链接）时须运行 `scripts\sync-config.ps1` 从仓库源同步 |
| 配置看似生效但路由/压缩行为不对 | 可能混入了 v1 键名，OpenCode 改走 V1→V2 迁移路径；按「v2 原生键名」表逐项核对 |
| 后台委派报 `background: true` 错误 | 未设 `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`；设置后重启，或退回前台串行 |
| 成本突然翻倍 | 检查是否 peak 时段（×2）；确认 trivial 任务没落到 `#high`；确认前缀没被动态内容打散（`cache_read` 便宜 50×） |
| thinking 关了但账单仍高 | `thinking` 写在了 `settings` 或 agent `options` 里（不生效）；必须写在模型层 `body` |
| flash 设置 `temperature` 没效果 | 思考模式下不支持 `temperature`；只有默认档（thinking 关）真正生效 |
| 用 PATH 上的 opencode 启动后一切都不对 | 那是旧版（1.18.4），走的是迁移路径；用桌面版 v2 自带 CLI 或升级到 v2 |
| 新模型/新 provider 想加 | 本仓库约束：只用 `deepseek/deepseek-flash`，不引入其他模型 |
| `estimate-cost.js` 数字与账单不符 | 脚本按你给的 token 数估算；peak/off-peak、缓存命中率、reasoning token 都要按真实值填 |

---

## AI 使用建议

- **推荐工作流模式**：先确认运行时是 OpenCode v2，再谈行为。路由按三档：trivial → thinking off、routine → `#low`、deep/uncertain → `#high`；改配置走「变更点速查」定位文件，改完 `sync-config.ps1` 同步并用 `validate-jsonc.js` 校验。
- **关键注意事项**：① 只写 v2 原生键，混入 v1 键会触发迁移路径；② 思考参数只在模型层（toggle 进 `body`、effort 进 `settings`）；③ 三档同价，省的是 reasoning token；④ skill 白名单决定名册大小，也就是每轮常驻成本；⑤ 后台委派要环境变量。
- **常用代码模式**：模型定义 = `providers.deepseek.models["deepseek-flash"]` 的 `body` + `variants`；权限 = `permissions` 有序规则 `{action, resource, effect}`；压缩 = `limit.input` + `compaction: {auto, keep: {tokens}, buffer}`。
- **不要臆造**：本仓库已从三模型矩阵（pro/flash/vision）收敛为单模型 + 思考档，不要再写 `deepseek-v4-pro` 或"pro = 3× flash"；没有 `dcp.jsonc` 这类第三方压缩插件配置；`subagent_depth` 已迁到 `experimental` 下。字段语义以仓库 `README.md`、`docs/UPGRADE.md` 与 OpenCode v2 文档为准。

---

## 相关技能

- **opencode** — 本配置方案的宿主客户端，配置字段以它为准：[../opencode/SKILL.md](../opencode/SKILL.md)
- **oh-my-openagent** — 另一套主打多模型协同的 Agent 方案：[../oh-my-openagent/SKILL.md](../oh-my-openagent/SKILL.md)
- **superpowers-zh** — 中文方法论 Skill 集，与本仓库的 superpowers 插件同源：[../superpowers-zh/SKILL.md](../superpowers-zh/SKILL.md)
- **deepseek-harness** — DeepSeek 官方 Agent 框架（另一套模型/工具编排形态）：[../deepseek-harness/SKILL.md](../deepseek-harness/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/znlgis/my-opencode-deepseek-config>
- 升级流程：仓库内 `docs/UPGRADE.md`（不变量、基线表、上游核对点、验收命令）
- 配置目录：`opencode/`（`opencode.jsonc`、`AGENTS.md`、`agents/`、`skills/`）
- 借鉴来源：[oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)、[oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim)、[anomalyco/opencode](https://github.com/anomalyco/opencode)、[OpenSpec](https://github.com/Fission-AI/OpenSpec)

---
name: opencode
description: "Use when configuring a model-agnostic terminal AI coding agent through opencode.jsonc — $schema validation, permissions array for shell/edit/webfetch, small_model cost routing, MCP local|remote servers, custom agents (.opencode/agents/*.md) and commands, cli.json themes, opencode run for CI and opencode serve for SDK; also for /undo failing outside a Git repo, no model after /connect, and config keys silently merged instead of replaced. OpenCode v2 (npm @opencode/cli)."
license: MIT
metadata:
  category: ai
  tags: "ai, agent, coding-agent, llm, terminal, tui, mcp, opencode"
---

> **项目地址：** <https://github.com/anomalyco/opencode>
>
> **官网 / 文档：** <https://opencode.ai> ｜ **配置 Schema：** <https://opencode.ai/config.json>（V2 终端客户端配置统一在全局 `cli.json`）
>
> **许可证：** MIT
>
> **最新版本：** v2.2.7（截至 2026-11，npm `@opencode/cli` latest 与仓库 tag `v2.2.7` 一致，2026-11-10 发布；GitHub `releases/latest` 指向的仍是 V1 线 `v1.19.5`，不要据此判断 V2 版本）；迭代快，以本机 `opencode --version` 为准

> **注意：** OpenCode 迭代非常快，命令、配置字段与模型名称请以你当前版本的 `opencode --help`、TUI 内 `/help` 及在线 JSON Schema 为准。

> **v2.2.7 变化（可选读）**：新增 GitHub Copilot Auto 模型路由、侧边栏标签快捷键与会话已读/未读标记；`read` 支持负 offset（如 `-50` 读末 50 行）并在找不到文件时提示相近路径；shell 结果以 `Exit code: N` 结尾；MCP 远程登录刷新更稳。**破坏性变更**：`@opencode/ai` 移除 `ImageResponse.image`（改用 `response.images[0]`）；SDK 在插件仍加载时 `agent.list` 只返回已加载 Agent，`integration.list`/`usage.limits`/`vcs.init`/`rpc.call`/`artifact.*` 不再等待最多 5 秒，需监听对应 `*.updated` 事件刷新。

## 概述

OpenCode 是一个**以终端为核心**的开源 AI 编码智能体（区别于 IDE 内联补全），可读代码、改代码、跑命令、调用工具，自主完成多步开发任务。核心理念是「**模型无关 + 配置即代码**」：

- **模型无关**：基于 [AI SDK](https://ai-sdk.dev/) 与 [Models.dev](https://models.dev) 支持 75+ 提供商，云端（Claude/GPT/Gemini/Qwen）与本地（Ollama/LM Studio/llama.cpp）自由切换。
- **权限系统**：V2 用 `permissions` 有序规则数组（`action` + `resource` + `effect: allow|ask|deny`），按 shell/edit/webfetch 等动作与命令、路径做细粒度控制；V2 另提供 `policies` 做管理员强制约束。
- **上下文与成本可控**：自动压缩（compaction）、工具输出裁剪（prune）、小模型分流（`small_model`）。
- **配置即代码**：`opencode.jsonc`、`AGENTS.md`、自定义命令/Agent/Skill 都是纯文本，可提交进 Git、团队共享。
- **多种形态**：TUI（`opencode`）、精简交互（`opencode mini`）、CLI（`opencode run` 脚本化/CI）、Server/SDK（`opencode serve` / `--server` 暴露 HTTP API）、桌面与 Web（Beta）。
- **Git 快照**：`/undo`、`/redo` 依赖项目为 Git 仓库，可随时撤销 AI 改动。

---

## 安装

V2 与 V1 使用同一个 `opencode` 命令，默认不再并存；装 V2 前先移除包管理器装的 V1。

```bash
# 一键安装脚本（V2，最简单）
curl -fsSL https://opencode.ai/v2/install | bash

# 包管理器（V2 包名是 @opencode/cli，不是 V1 的 opencode-ai）
npm install -g @opencode/cli
brew install anomalyco/tap/opencode-v2   # macOS/Linux 官方 tap（跟随 V2）
mise use -g opencode
nix run github:anomalyco/opencode

opencode --version                       # 验证：应为 2.x
```

> Windows 推荐在 **WSL** 中使用；TUI 在 WezTerm/Alacritty/Ghostty/Kitty 等现代终端渲染更佳。桌面版是 Beta，从 <https://opencode.ai/download> 下载。

---

## 快速上手

```bash
cd your-project        # 建议是 Git 仓库（/undo /redo /快照依赖 Git）
opencode               # 启动 TUI
```

TUI 内常用斜杠命令：

```text
/connect    # 接入模型提供商（粘贴 API Key；或选 OpenCode Zen 网关）
/models     # 选择当前模型
/init       # 生成项目级 AGENTS.md（让 OpenCode 了解你的项目）
/undo /redo # 基于 Git 快照撤销/重做 AI 改动
/share      # 生成会话分享链接
/help       # 查看全部命令
```

也可用环境变量提供密钥（如 `ANTHROPIC_API_KEY`、`OPENAI_API_KEY`），启动时自动识别。

### CLI / 无头模式（脚本与 CI）

```bash
opencode run "为 utils.ts 补充单元测试并运行"      # 单次执行
opencode run -m anthropic/claude-sonnet-5-5 "重构登录模块"
opencode serve --port 4096                         # 启动 HTTP Server（配合 SDK）
```

---

## 配置体系（核心）

OpenCode 支持 **JSON / JSONC**（带注释）。务必加 `$schema` 获得校验与补全。项目根配置文件 `opencode.json`：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-5-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "autoupdate": true,
  // V2：permissions 是「有序规则数组」，后匹配的规则生效（不是 V1 的 key 对象）
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git status *", "effect": "allow" },
    { "action": "shell", "resource": "git diff *", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "deny" },
    { "action": "edit", "resource": "*", "effect": "allow" },
    { "action": "webfetch", "resource": "*", "effect": "ask" }
  ]
}
```

> **V2 破坏性变更（官方三项）**：① 插件改用新 Plugin API；② Server API 与客户端的契约变更；③ 终端配置从分层 `tui.json(c)` 改为**单一的全局 `cli.json`**（首次启动自动迁移）。其余受支持的 V1 配置字段 V2 仍读取并在内存中归一化，无需立刻改写；但 V1 的 `permission` 对象、`tool` 权限写法在原生 V2 里应改用 `permissions` 数组。

### 配置位置与优先级

| 角色 | 路径 |
|------|------|
| 全局配置 | `~/.config/opencode/opencode.json` |
| 项目配置（可提交 Git） | 项目根 `opencode.json` |
| 终端客户端设置（主题/键位） | V2 统一为全局 `~/.config/opencode/cli.json`（V1 的 `tui.json(c)` 首次启动自动迁移） |
| 自定义路径 / 目录 | `OPENCODE_CONFIG` / `OPENCODE_CONFIG_DIR` 环境变量 |

`.opencode/` 与 `~/.config/opencode/` 下使用复数子目录：`agents/`、`commands/`、`plugins/`、`skills/`、`tools/`、`themes/`（V2 的 Agent 用 Markdown 文件，frontmatter 里写 `description` / `mode` / `model` / `permissions`）。

配置优先级（后者覆盖前者）：组织远程 < 全局 < 自定义 < 项目 < .opencode/ < 内联 < 托管。覆盖，不替换。

### 终端客户端配置（V2：全局 `cli.json`）

V2 把终端客户端的主题、键位等设置集中到全局 `~/.config/opencode/cli.json`（`opencode.json` 不再承载这些键）：

```jsonc
{
  "theme": "tokyonight"
}
```

> 从 V1 升级时，旧的 `tui.json`/`tui.jsonc` 会自动迁移到 `cli.json`；不要把 V1 的 `tui.json` 继续指向已转换的 V2 配置。

---

## 自定义 Agent / 命令 / 工具

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "build",
  "agent": {
    "reviewer": {
      "description": "只读代码评审，不允许修改",
      "model": "anthropic/claude-sonnet-5-5",
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" },
        { "action": "shell", "resource": "*", "effect": "deny" }
      ]
    }
  },
  "mcp": {
    "playwright": { "type": "local", "command": ["npx", "@playwright/mcp@latest"], "enabled": true },
    "jira": { "type": "remote", "url": "https://jira.example.com/mcp", "enabled": false }
  }
}
```

- **Agent**：可定义只读评审、文档撰写等子代理，并限定模型与权限。
- **自定义命令**：放 `commands/*.md`，复用提示词模板。
- **MCP 扩展**：`type: local`（启动本地进程）或 `type: remote`（HTTP），为 Agent 增加外部工具能力。
- **规则上下文**：`AGENTS.md`（项目根）描述项目约定、构建/测试命令，OpenCode 每次会话注入。

---

## Token 优化与省钱配置

| 手段 | 配置/做法 |
|------|----------|
| 小模型分流 | `small_model` 处理标题生成、压缩等轻量任务，主任务用强模型 |
| 上下文自动压缩 | 长会话触发 compaction，把历史摘要化，避免无限膨胀 |
| 工具输出裁剪 | 大输出（如长日志）自动 prune，仅保留关键片段 |
| 按需切模型 | `/models` 或 `opencode run -m ...`，简单任务用便宜模型 |
| 提示缓存 | 在 `provider` 选项中开启缓存，复用系统提示降低费用 |
| 收紧权限 | `bash`/`webfetch` 设 `ask`/`deny`，减少无谓工具调用 |

---

## 典型工作流

```bash
# 1. 进入项目并初始化上下文
cd my-app && opencode
> /init                       # 生成 AGENTS.md

# 2. 接入并选择模型
> /connect                    # 接入 Anthropic / OpenCode Zen
> /models                     # 选 claude-sonnet-5-5

# 3. 交给它做多步任务（它会读文件、改代码、跑命令）
> 实现用户注册接口，加上输入校验与单元测试，并运行测试

# 4. 审阅与撤销
> /undo                       # 不满意则基于 Git 快照回滚

# 5. CI 中无头运行
opencode run "升级依赖并修复由此产生的编译错误"
```

---

## 常见问题（FAQ）

| 问题 | 解决 |
|------|------|
| `/undo` 不可用 | 当前目录不是 Git 仓库；`git init` 后再用 |
| 没有可用模型 | 先 `/connect` 接入提供商或设置 `ANTHROPIC_API_KEY` 等环境变量，再 `/models` |
| 配置不生效 | 注意「合并而非替换」与优先级：项目配置覆盖全局；用 `$schema` 校验拼写 |
| 主题/键位改了没反应 | V2 的终端设置统一在全局 `~/.config/opencode/cli.json`，不写在 `opencode.json`；先确认没有旧的 `tui.json` 覆盖 |
| Token 消耗过快 | 设 `small_model`、收紧 `permission`、用便宜模型处理简单任务、开启提示缓存 |
| 想接公司内部工具 | 通过 `mcp`（local/remote）接入，或用 `opencode mcp add <name> --url ...` 写入配置；再在 Agent 权限内开放 |
| 从 V1 升级后权限/主题失效 | V2 三项破坏性变更：插件 API、Server API、终端配置改 `cli.json`；`permission` 对象改写 `permissions` 数组，其余受支持的 V1 字段会被归一化读取 |
| 升级后命令变了 | 以 `opencode --help` / `/help` 与官网 Schema 为准（迭代快） |
| 直接 import `@opencode/ai` 的代码升级后拿不到图片 | 2.2.7 移除了 `ImageResponse.image`，改用 `response.images[0]` |
| SDK 的 `agent.list` / `vcs.init` 返回不完整 | 2.2.7 起在插件加载期间这些端点不再阻塞等待：先监听 `*.updated` 事件，拿到变更后再取 |
| 想快速读文件尾部 | 2.2.7 起 `read` 支持负 offset，如 `-50` 读最后 50 行；offset 超界返回末尾内容与总行数而不是报错 |

---

## AI 使用建议

- 用户提到「终端 AI 编码代理」「opencode.json 配置」「模型无关」「省 Token / 控制成本」「自定义 Agent / MCP」时加载本技能。
- 区分形态：交互用 **TUI**（`opencode`/`opencode mini`），脚本/CI 用 **`opencode run`**，集成用 **`opencode serve`/`--server` + SDK**。
- 配置问题先排查「合并 vs 替换」与优先级；主题/键位归全局 `cli.json`，行为/模型/权限归 `opencode.json`。V2 权限用 `permissions` 有序数组，最后匹配者生效。
- 生成配置时始终带 `"$schema"`，并优先用细粒度 `permission` 收敛 `bash`/`webfetch` 风险。
- 由于版本迭代快，生成命令/字段后提醒用户以本机 `--help` 与在线 Schema 校验。

---

## 相关技能

- **oh-my-openagent** — 多模型协同的终端 Agent；5.x 起是独立应用（OmO Native），不再作为 OpenCode 插件运行：[../oh-my-openagent/SKILL.md](../oh-my-openagent/SKILL.md)
- **my-opencode-deepseek-config** — OpenCode + DeepSeek 的纯配置实践（Agent/技能/命令清单）：[../my-opencode-deepseek-config/SKILL.md](../my-opencode-deepseek-config/SKILL.md)
- **superpowers-zh** — 中文方法论 Skill 层，可在 OpenCode 中加载：[../superpowers-zh/SKILL.md](../superpowers-zh/SKILL.md)
- **deepseek-harness** — DeepSeek 官方智能体框架（对比另一类 Agent 设计）：[../deepseek-harness/SKILL.md](../deepseek-harness/SKILL.md)

---

## 参考资源

- 官方文档：<https://opencode.ai/docs>
- 配置 JSON Schema：<https://opencode.ai/config.json>
- Models.dev（模型/提供商目录）：<https://models.dev>
- 变更日志：<https://github.com/anomalyco/opencode/releases>（V2 版本看 npm/tag，V1 仍在 GitHub latest）
- 上游中文教程：<https://znlgis.github.io/>（ai/opencode 系列）

---
name: opencode
description: "Use when working with a model-agnostic terminal AI coding agent that uses opencode.json for declarative configuration — MCP servers, custom commands, agent routing, skills. OpenCode: configuration-as-code terminal AI coding agent with multi-model support."
tags:
  - ai
  - agent
  - coding-agent
  - llm
  - terminal
  - tui
  - mcp
  - opencode
---

> **项目地址：** <https://github.com/anomalyco/opencode>
>
> **官网 / 文档：** <https://opencode.ai> ｜ **配置 Schema：** <https://opencode.ai/config.json> ｜ **TUI Schema：** <https://opencode.ai/tui.json>
>
> **许可证：** MIT
> **版本：** 迭代快，以本机 `opencode --version` 为准

> ⚠️ OpenCode 迭代非常快，命令、配置字段与模型名称请以你当前版本的 `opencode --help`、TUI 内 `/help` 及在线 JSON Schema 为准。

## 概述

OpenCode 是一个**以终端为核心**的开源 AI 编码智能体（区别于 IDE 内联补全），可读代码、改代码、跑命令、调用工具，自主完成多步开发任务。核心理念是「**模型无关 + 配置即代码**」：

- **模型无关**：基于 [AI SDK](https://ai-sdk.dev/) 与 [Models.dev](https://models.dev) 支持 75+ 提供商，云端（Claude/GPT/Gemini/Qwen）与本地（Ollama/LM Studio/llama.cpp）自由切换。
- **权限系统**：每类工具（edit/bash/read/webfetch 等）可设 `allow`/`ask`/`deny`，支持按命令、路径的细粒度规则。
- **上下文与成本可控**：自动压缩（compaction）、工具输出裁剪（prune）、小模型分流（`small_model`）。
- **配置即代码**：`opencode.json`、`AGENTS.md`、自定义命令/Agent/Skill 都是纯文本，可提交进 Git、团队共享。
- **三种形态**：TUI（终端交互）、CLI（`opencode run` 脚本化/CI）、Server/SDK（`opencode serve` 暴露 HTTP API）。
- **Git 快照**：`/undo`、`/redo` 依赖项目为 Git 仓库，可随时撤销 AI 改动。

---

## 安装

```bash
# 一键安装脚本（最简单）
curl -fsSL https://opencode.ai/install | bash

# 包管理器
npm install -g opencode-ai          # Node 生态（npm/bun/pnpm/yarn）
brew install anomalyco/tap/opencode # macOS/Linux 官方 tap（更新最及时）
scoop install opencode              # Windows
sudo pacman -S opencode             # Arch
mise use -g opencode
nix run nixpkgs#opencode

opencode --version                  # 验证
```

> Windows 推荐在 **WSL** 中使用；TUI 在 WezTerm/Alacritty/Ghostty/Kitty 等现代终端渲染更佳。

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
opencode run -m anthropic/claude-sonnet-4-5 "重构登录模块"
opencode serve --port 4096                         # 启动 HTTP Server（配合 SDK）
```

---

## 配置体系（核心）

OpenCode 支持 **JSON / JSONC**（带注释）。务必加 `$schema` 获得校验与补全：

```jsonc title="opencode.json"
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "autoupdate": true,
  "permission": {
    "edit": "allow",
    "bash": { "git push": "ask", "rm *": "deny", "*": "allow" },
    "webfetch": "ask"
  }
}
```

### 配置位置与优先级

| 角色 | 路径 |
|------|------|
| 全局配置 | `~/.config/opencode/opencode.json` |
| 项目配置（可提交 Git） | 项目根 `opencode.json` |
| TUI 设置（主题/键位） | `~/.config/opencode/tui.json` 或项目根 `tui.json` |
| 自定义路径 / 目录 | `OPENCODE_CONFIG` / `OPENCODE_CONFIG_DIR` 环境变量 |

`.opencode/` 与 `~/.config/opencode/` 下使用复数子目录：`agents/`、`commands/`、`plugins/`、`skills/`、`tools/`、`themes/`。

配置优先级（后者覆盖前者）：组织远程 < 全局 < 自定义 < 项目 < .opencode/ < 内联 < 托管。覆盖，不替换。

### TUI 专属配置（`tui.json`）

```jsonc title="tui.json"
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight",
  "diff_style": "auto",
  "attention": { "enabled": true, "notifications": true, "sound": true }
}
```

> `opencode.json` 旧的顶层 `theme`/`keybinds`/`tui` 键已废弃，会自动迁移到 `tui.json`。

---

## 自定义 Agent / 命令 / 工具

```jsonc title="opencode.json"
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "build",
  "agent": {
    "reviewer": {
      "description": "只读代码评审，不允许修改",
      "model": "anthropic/claude-sonnet-4-5",
      "permission": { "edit": "deny", "bash": "deny" }
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
> /models                     # 选 claude-sonnet-4-5

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
| 主题/键位改了没反应 | 这些属于 TUI 设置，应写在 `tui.json` 而非 `opencode.json` |
| Token 消耗过快 | 设 `small_model`、收紧 `permission`、用便宜模型处理简单任务、开启提示缓存 |
| 想接公司内部工具 | 通过 `mcp`（local/remote）接入 MCP server，并在 Agent 权限内开放 |
| 升级后命令变了 | 以 `opencode --help` / `/help` 与官网 Schema 为准（迭代快） |

---

## AI 使用建议

- 用户提到「终端 AI 编码代理」「opencode.json 配置」「模型无关」「省 Token / 控制成本」「自定义 Agent / MCP」时加载本技能。
- 区分三种形态：交互用 **TUI**，脚本/CI 用 **`opencode run`**，集成用 **`opencode serve` + SDK**。
- 配置问题先排查「合并 vs 替换」与优先级；主题/键位归 `tui.json`，行为/模型/权限归 `opencode.json`。
- 生成配置时始终带 `"$schema"`，并优先用细粒度 `permission` 收敛 `bash`/`webfetch` 风险。
- 由于版本迭代快，生成命令/字段后提醒用户以本机 `--help` 与在线 Schema 校验。

---

## 参考资源

- 官方文档：<https://opencode.ai/docs>
- 配置 JSON Schema：<https://opencode.ai/config.json>
- Models.dev（模型/提供商目录）：<https://models.dev>
- 上游中文教程：<https://znlgis.github.io/>（ai/opencode 系列）

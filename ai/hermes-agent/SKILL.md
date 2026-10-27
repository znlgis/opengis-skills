---
name: hermes-agent
description: "Use when you want a terminal agent that learns from experience — hermes setup/model/tools/doctor, skills + persistent memory + session search, hermes gateway for Telegram/Discord/Slack/WhatsApp/Signal, hermes cron create for scheduled jobs, MCP and subagents; also for `hermes: command not found` after install.sh, Python 3.15 unsupported-engine errors, and Windows users wrongly told to use WSL2. Hermes Agent (Nous Research), Python 3.11-3.14."
tags:
  - ai
  - agent
  - self-improving
  - memory
  - terminal
  - mcp
  - python
  - nous-research
---

> **项目地址：** <https://github.com/NousResearch/hermes-agent>
>
> **官网 / 文档：** <https://nousresearch.com/> ｜ <https://hermes-agent.nousresearch.com/docs>
>
> **许可证：** MIT ｜ **语言：** Python（3.11 – 3.14，`requires-python = ">=3.11,<3.15"`）
>
> **最新版本：** v0.22.5（2026-10-23 发布，实测 `releases/latest` 重定向；见 [GitHub Releases](https://github.com/NousResearch/hermes-agent/releases)）

## 概述

Hermes 是「The agent that grows with you」——**唯一内置完整学习闭环的开源 Agent**。它不是 IDE 插件或单一模型封装，而是一套完整的 Agent Harness：

- **自学习闭环**：使用中自主**创建技能（skills）**、在使用时**改进技能**、把关键事实写入**持久化记忆**、检索自己的**历史会话**，并对用户建立越来越精确的画像。
- **终端优先**：CLI/TUI（`hermes`）交互，命令如 `hermes setup`、`hermes model`、`hermes tools`、`hermes config`、`hermes doctor`。
- **模型无关**：支持多 Provider 与模型配置体系。
- **工具系统 + 终端后端**：执行命令、读写文件等。
- **MCP 集成**与上下文文件。
- **消息网关**：多平台接入（Telegram 等），可一边在聊天里对话一边让它在云端 VM 干活。
- **定时任务 / 自动化**、**语音/视觉/浏览器**、**子代理协作**、**插件开发**。
- **部署灵活**：5 美元 VPS、GPU 集群，或 Daytona / Modal 等空闲近零成本的 Serverless。

---

## 安装

支持 Linux、macOS、WSL2、Termux（Android）、Nix。一键脚本：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
# 脚本会准备 Python 环境，并在 ~/.hermes/hermes-agent/ 下执行 uv pip install -e ".[all]"

source ~/.bashrc      # 或 source ~/.zshrc
hermes                # 进入 TUI
```

> Windows 自 v0.22 起**原生支持**（CLI、gateway、TUI、工具均可直接跑，无需 WSL2）；仍可用 WSL2 走 Linux 一键脚本。Termux 默认安装 `.[termux]` 子集（跳过尚未测试的浏览器与 WhatsApp 部分）。

手动 / 开发安装（uv）：

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv venv --python 3.11
uv pip install -e ".[all,dev]"
./hermes               # 直接运行（无需手动 source venv）
```

---

## 初始化与核心命令

```bash
hermes setup     # 首次初始化（账户、目录、基础配置）
hermes model     # 选择 Provider 与模型
hermes tools     # 配置每个平台启用哪些 toolset
hermes config    # 编辑配置
hermes doctor    # 体检 / 排错
```

---

## 自学习闭环（核心特性）

Hermes 区别于普通 Agent 的关键在于「学习」：

- **技能(Skills)**：把成功的做法沉淀为可复用技能；后续遇到类似任务自动调用并持续改进。
- **记忆(Memory)**：把重要事实持久化，跨会话保留；它会「提醒自己」去固化知识。
- **历史检索**：能搜索自己过去的对话，复用上下文与结论。
- **用户画像**：跨会话累积，对「你是谁、偏好什么」建立越来越准的模型。
- **可选 Honcho 记忆 Provider**：接入 [plastic-labs/honcho](https://github.com/plastic-labs/honcho) 做辩证用户建模（dialectic user modeling），把零散事实提炼为动态用户画像；仓库内置 `plugins/memory/honcho/` 实现，执行 `uv pip install -e ".[honcho]"` 后以 `hermes plugins enable memory:honcho` 启用。

> 这意味着 Hermes 越用越「懂你」，适合作为长期个人/团队助手，而非一次性任务工具。

---

## 典型工作流

### 工作流一：快速上手

```bash
hermes setup      # 初始化配置（向导）
hermes model      # 选择/配置 Provider 与模型
hermes            # 不带子命令直接启动终端 TUI
```

创建第一个技能：让 Hermes 监听你的工作 → 自动总结模式 → 写入技能文件。之后可用 `hermes skills list` 查看、`hermes memory` 管理记忆。

### 工作流二：长期运行部署

```bash
# 启动消息网关（Telegram / Discord / Slack / WhatsApp / Signal 共用同一 gateway 进程）
hermes gateway

# 定时任务：schedule 支持 "30m" / "every 2h" / cron 表达式
hermes cron create "0 9 * * *" "汇总昨天的提交并生成晨报" --name daily-brief --deliver telegram
hermes cron list --all
```

> `hermes serve` 是无界面的 Web/API 服务（`--host` / `--port` / `--stop` / `--status`），**不是**消息网关；旧文档里的 `hermes serve --gateway telegram` 已不存在。定期审查 `~/.hermes/memories/` 和 `~/.hermes/skills/` 确保记忆质量。

### 工作流三：团队协作

1. 配置 MCP 集成 → 连接外部工具与数据源
2. 设置子代理 → 分配专门任务给子代理
3. 审查子代理产出 → 合并到主上下文

---

## 进阶能力

| 能力 | 说明 |
|------|------|
| 模型供应商与配置 | 多 Provider，统一配置体系（`hermes model` / `hermes config`） |
| 工具系统与终端后端 | 命令执行、文件读写等；按平台启用 toolset |
| MCP 集成 | 接入 MCP server 扩展外部工具；配合上下文文件注入项目知识 |
| 消息网关 | 多平台接入，远程对话与云端执行解耦 |
| 定时任务 | cron 式自动化 |
| 语音 / 视觉 / 浏览器 | 多模态与网页操作 |
| 子代理协作 | 拆解复杂任务并行处理 |
| 插件开发 | 扩展自定义能力与研究功能 |

---

## 常见问题（FAQ）

| 问题 | 解决 |
|------|------|
| 安装失败 | 确认 Python ≥ 3.11；脚本依赖 `uv`，可先手动装 uv 再 `uv pip install -e ".[all]"` |
| Windows 能跑吗 | 能，v0.22+ 原生支持（CLI/gateway/TUI/tools）；老教程要求 WSL2 已过时，WSL2 仍可选 |
| `pip install` 报 `Requires-Python >=3.11,<3.15` | 用 Python 3.11–3.14 建 venv；3.15 尚未支持 |
| `hermes serve --gateway` 报无法识别参数 | `serve` 只起 Web/API 服务；消息网关用 `hermes gateway` |
| `hermes` 安装后不在 PATH | `install.sh` 会把 `~/.local/bin` 写入 shell rc；重开终端或 `source ~/.bashrc`，Termux 用 `~/bin` |
| Android 部分功能缺失 | Termux 默认装 `.[termux]` 子集（跳过浏览器/WhatsApp），按官方 Termux Guide 手动补齐 |
| 选不到模型 | 先 `hermes model` 配置 Provider 与 API Key；`hermes doctor` 排错 |
| 它“记住”的东西在哪 | 持久化记忆/技能存于 Hermes 主目录（`~/.hermes/` 或 `$HERMES_HOME`） |
| 想接私有工具 | 通过 MCP 集成接入，并在 `hermes tools` 中启用 |

---

## AI 使用建议

- 用户提到「自学习 / 会成长的 AI Agent」「Nous Research Hermes」「带记忆和技能闭环的终端 Agent」时加载本技能。
- 强调其差异点：**学习闭环（技能+记忆+历史+用户画像）**，而非普通工具调用框架。
- 安装走官方 `install.sh`（Linux/macOS/WSL2/Termux/Nix），用 `hermes setup/model/tools/doctor` 完成初始化与排错。
- 复杂任务建议用子代理协作 + MCP 扩展；长期使用价值来自记忆与技能的持续积累。

---

## 相关技能

- **pi** — 终端编码 Agent（另一套工具链与权限模型）：[../pi/SKILL.md](../pi/SKILL.md)
- **opencode** — 终端 AI 编码 Agent（OpenCode 生态）：[../opencode/SKILL.md](../opencode/SKILL.md)
- **superpowers-zh** — 中文方法论文档层，可叠加在 Hermes 的工作流之上：[../superpowers-zh/SKILL.md](../superpowers-zh/SKILL.md)

---

## 参考资源

- 文档：<https://hermes-agent.nousresearch.com/docs>
- Nous Research：<https://nousresearch.com/>
- 上游中文教程：<https://znlgis.github.io/>（ai/hermes-agent 系列）

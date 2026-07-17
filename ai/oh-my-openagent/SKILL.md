---
name: oh-my-openagent
description: "Use when configuring OpenCode for multi-model orchestration, Agent Harness patterns, CI/automation integration, or token cost optimization. Oh-My-OpenAgent: curated OpenCode agent configurations and prompt engineering patterns."
tags: [ai, agent, opencode, orchestration, multi-model, lsp, ast, harness]
---

> **项目地址�?* <https://github.com/code-yeongyu/oh-my-openagent>
>
> **安装文档�?* <https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/installation.md>
>
> **许可证：** SUL-1.0（Sustainable Use License，商用前请阅读条款）�?**npm 包：** `oh-my-opencode` �?**作者：** YeonGyu-Kim

> 说明：项目以 npm �?**`oh-my-opencode`** 发布，CLI 别名包含 `oh-my-opencode` / `oh-my-openagent` / `omo` / `lazycodex`。它�?**OpenCode 的插�?*，使用前需先安�?[OpenCode](../opencode/SKILL.md)�?

## 概述

OmO 不是新模型，也不�?Cursor/Claude Code 的克隆，而是把开�?AI 编程客户�?**OpenCode** 升级成一�?*多模型协同的开发团�?*�?

- **多模型编�?*：不同模型各司其职并行运转——Claude Opus 做总指挥（编排）、GPT 深度推理、Kimi 加速、Gemini 处理前端/视觉、Grok Code Fast 做代码检索�?
- **并行后台智能�?*：把任务分派给多个后�?agent 并行处理�?
- **精心打造的 LSP / AST 工具**：基�?`ast-grep` �?LSP 的结构化代码检索与编辑（比纯文�?grep 更准），内置 MCP（ast-grep-mcp、git-bash-mcp、lsp-tools-mcp）�?
- **电池全包**：开箱即用的 agents、commands、skills、rules-engine、comment-checker 等�?
- **跨平�?*：随包提�?darwin/linux/windows 各架构二进制�?

---

## 安装

前置：先安装 OpenCode，并确认可用�?

```bash
opencode --version    # 确认 OpenCode 已安�?
```

�?bun 一键安装（推荐，带交互 TUI）：

```bash
bunx oh-my-opencode install
```

非交互安装（CI / 脚本，可显式带标志）�?

```bash
bunx oh-my-opencode install --no-tui \
  # 例如 --openai / --subscription / --max20 等模型与订阅相关标志
```

> ⚠️ 官方安装手册特别提示：让 Agent 获取安装文档时务必用 `curl` 而非 WebFetch——WebFetch 会做摘要，丢�?`--openai`、subscription、`max20` 等关键标志：
>
> ```bash
> curl -fsSL https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/refs/heads/dev/docs/guide/installation.md
> ```

---

## 核心理念与组�?

| 组成 | 作用 |
|------|------|
| 多模型编�?| 按「编�?推理/加�?视觉/检索」角色分配不同模型并行协�?|
| 并行后台智能�?| 同时跑多�?agent，缩短端到端时延 |
| LSP / AST 工具 | `ast-grep` + LSP 做结构化检索与重构，配�?MCP server |
| Skills / Commands / Agents | OpenCode 插件形态下的可复用技能、命令与子代�?|
| rules-engine / comment-checker | 规则约束与注释质量检查，提升产出工程质量 |

---

## 典型工作�?

```text
1. 安装 OpenCode 并接入多个模�?Provider（Claude / GPT / Gemini / Kimi / Grok 等）
2. bunx oh-my-opencode install        # 安装 OmO 插件�?OpenCode
3. �?OpenCode 中发起任务，OmO 自动按角色编排多模型 + 并行后台 agent
4. 借助 LSP/AST 工具做精准的跨文件检索与重构
5. �?rules-engine / comment-checker 等把关产出质�?
```

---

## 常见问题（FAQ�?

| 问题 | 解决 |
|------|------|
| 它是独立工具�?| 不是，OmO �?**OpenCode 的插�?*，必须先�?OpenCode |
| npm 包叫什�?| `oh-my-opencode`（CLI 别名�?`omo` / `oh-my-openagent` / `lazycodex`�?|
| 安装命令丢了标志 | 不要�?WebFetch 取安装文档，�?`curl` 原文，保�?`--openai`/subscription/`max20` �?|
| 需要哪些模�?| 多模型协作场景建议至少接入编�?Claude Opus)+推理(GPT)+视觉(Gemini)+检�?Grok) |
| 许可证能商用�?| SUL-1.0（Sustainable Use License），商用前阅读条�?|
| �?OpenCode 关系 | OmO 复用 OpenCode 的配�?权限/Provider 体系，在其上叠加编排与工�?|

---

## AI 使用建议

- 用户提到「OpenCode 多模型编排」「oh-my-opencode / OmO / lazycodex」「并行后台智能体 + AST/LSP 工具」时加载本技能�?
- 始终先确�?**OpenCode 已安�?*，再 `bunx oh-my-opencode install`；可同时加载 [opencode](../opencode/SKILL.md) 技能�?
- 获取/复述安装命令时保留全部标志，不要摘要化（按官方提示用 `curl`）�?
- 强调它是「插�?+ 编排层」，价值在多模型分工与结构化代码工具，而非又一个模型�?

---

## 参考资�?

- 安装文档�?https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/installation.md>
- OpenCode�?https://opencode.ai> �?本仓 [ai/opencode](../opencode/SKILL.md)
- 上游中文教程�?https://znlgis.github.io/>（ai/oh-my-openagent 系列�?

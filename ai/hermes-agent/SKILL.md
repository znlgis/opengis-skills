---
name: hermes-agent
description: "Use when building self-learning AI agents that improve through experience �?terminal-first interface, tool calling, memory persistence, autonomous task execution. Hermes Agent: self-improving general-purpose AI agent with local-first architecture."
tags: [ai, agent, self-improving, memory, terminal, mcp, python, nous-research]
---

> **项目地址�?* <https://github.com/NousResearch/hermes-agent>
>
> **官网 / 文档�?* <https://nousresearch.com/> �?<https://hermes-agent.nousresearch.com/docs>
>
> **许可证：** MIT �?**语言�?* Python（≥ 3.11�?

## 概述

Hermes 是「The agent that grows with you」—�?*唯一内置完整学习闭环的开�?Agent**。它不是 IDE 插件或单一模型封装，而是一套完整的 Agent Harness�?

- **自学习闭�?*：使用中自主**创建技能（skills�?*、在使用�?*改进技�?*、把关键事实写入**持久化记�?*、检索自己的**历史会话**，并对用户建立越来越精确的画像�?
- **终端优先**：CLI/TUI（`hermes`）交互，命令�?`hermes setup`、`hermes model`、`hermes tools`、`hermes config`、`hermes doctor`�?
- **模型无关**：支持多 Provider 与模型配置体系�?
- **工具系统 + 终端后端**：执行命令、读写文件等�?
- **MCP 集成**与上下文文件�?
- **消息网关**：多平台接入（Telegram 等），可一边在聊天里对话一边让它在云端 VM 干活�?
- **定时任务 / 自动�?*�?*语音/视觉/浏览�?*�?*子代理协�?*�?*插件开�?*�?
- **部署灵活**�? 美元 VPS、GPU 集群，或 Daytona / Modal 等空闲近零成本的 Serverless�?

---

## 安装

支持 Linux、macOS、WSL2、Termux（Android）、Nix。一键脚本：

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
# 脚本会准�?Python 环境，并�?~/.hermes/hermes-agent/ 下执�?uv pip install -e ".[all]"

source ~/.bashrc      # �?source ~/.zshrc
hermes                # 进入 TUI
```

> Windows 不直接支持，请安�?**WSL2** 后在 WSL 内执�?Linux 流程。Termux 默认安装 `.[termux]` 子集（跳过尚未测试的浏览器与 WhatsApp 部分）�?

手动 / 开发安装（uv）：

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv venv --python 3.11
uv pip install -e ".[all,dev]"
./hermes               # 直接运行（无需手动 source venv�?
```

---

## 初始化与核心命令

```bash
hermes setup     # 首次初始化（账户、目录、基础配置�?
hermes model     # 选择 Provider 与模�?
hermes tools     # 配置每个平台启用哪些 toolset
hermes config    # 编辑配置
hermes doctor    # 体检 / 排错
```

---

## 自学习闭环（核心特性）

Hermes 区别于普�?Agent 的关键在于「学习」：

- **技�?Skills)**：把成功的做法沉淀为可复用技能；后续遇到类似任务自动调用并持续改进�?
- **记忆(Memory)**：把重要事实持久化，跨会话保留；它会「提醒自己」去固化知识�?
- **历史检�?*：能搜索自己过去的对话，复用上下文与结论�?
- **用户画像**：跨会话累积，对「你是谁、偏好什么」建立越来越准的模型�?

> 这意味着 Hermes 越用越「懂你」，适合作为长期个人/团队助手，而非一次性任务工具�?

---

## 进阶能力

| 能力 | 说明 |
|------|------|
| 模型供应商与配置 | �?Provider，统一配置体系（`hermes model` / `hermes config`�?|
| 工具系统与终端后�?| 命令执行、文件读写等；按平台启用 toolset |
| MCP 集成 | 接入 MCP server 扩展外部工具；配合上下文文件注入项目知识 |
| 消息网关 | 多平台接入，远程对话与云端执行解�?|
| 定时任务 | cron 式自动化 |
| 语音 / 视觉 / 浏览�?| 多模态与网页操作 |
| 子代理协�?| 拆解复杂任务并行处理 |
| 插件开�?| 扩展自定义能力与研究功能 |

---

## 常见问题（FAQ�?

| 问题 | 解决 |
|------|------|
| 安装失败 | 确认 Python �?3.11；脚本依�?`uv`，可先手动装 uv �?`uv pip install -e ".[all]"` |
| Windows 能跑�?| 不直接支持，�?WSL2 后在 WSL 内安�?|
| Android 部分功能缺失 | Termux 默认�?`.[termux]` 子集（跳过浏览器/WhatsApp），按官�?Termux Guide 手动补齐 |
| 选不到模�?| �?`hermes model` 配置 Provider �?API Key；`hermes doctor` 排错 |
| 它“记住”的东西在哪 | 持久化记�?技能存�?Hermes 主目录（`~/.hermes/` �?`$HERMES_HOME`�?|
| 想接私有工具 | 通过 MCP 集成接入，并�?`hermes tools` 中启�?|

---

## AI 使用建议

- 用户提到「自学习 / 会成长的 AI Agent」「Nous Research Hermes」「带记忆和技能闭环的终端 Agent」时加载本技能�?
- 强调其差异点�?*学习闭环（技�?记忆+历史+用户画像�?*，而非普通工具调用框架�?
- 安装走官�?`install.sh`（Linux/macOS/WSL2/Termux/Nix），�?`hermes setup/model/tools/doctor` 完成初始化与排错�?
- 复杂任务建议用子代理协作 + MCP 扩展；长期使用价值来自记忆与技能的持续积累�?

---

## 参考资�?

- 文档�?https://hermes-agent.nousresearch.com/docs>
- Nous Research�?https://nousresearch.com/>
- 上游中文教程�?https://znlgis.github.io/>（ai/hermes-agent 系列�?

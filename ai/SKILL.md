---
name: ai-skills
description: "Use when building LLM applications, RAG knowledge bases, AI agents, multi-agent crews, high-throughput model serving, PDF/document parsing into Markdown, terminal coding agents, multi-model orchestration, plugin-based agent harnesses, or file translation. Index of 17 skills: Dify, LangChain, LlamaIndex, Ollama, Transformers, vLLM, CrewAI, MinerU, Hermes Agent, OpenClaw, OpenCode, Pi, DocuTranslate, DeepSeek Harness and more."
tags:
  - ai
  - llm
  - agent
  - rag
  - workflow
  - prompt
  - chatbot
  - opensource
---

> **父级入口：** [../SKILL.md](../SKILL.md) — 全仓 114 技能总索引

## 概述

本分类涵盖 **17 个 AI/LLM 开源项目**的技能文件：

- **LLM 应用平台**：Dify（RAG + 工作流 + Agent 一站式）
- **应用框架**：LangChain（LCEL + LangGraph 工具调用 Agent）、LlamaIndex（文档 RAG/索引/Workflow）
- **本地推理与模型库**：Ollama（本地 LLM 运行与 OpenAI 兼容 API）、Hugging Face Transformers（模型定义、推理与微调）、vLLM（高吞吐 OpenAI 兼容推理服务）
- **多 Agent 编排**：CrewAI（角色化 Agent / Task / Crew / Flows）
- **文档解析**：MinerU（PDF/Office → Markdown/JSON，可接 RAG 与翻译流水线）
- **智能体 / 助手**：Hermes Agent（自学习通用智能体）、OpenClaw（多通道个人 AI 助手 Gateway）
- **终端编码代理**：Pi（极简 Agent Harness）、OpenCode（模型无关、配置即代码的 AI coding agent）
- **插件式智能体框架**：DeepSeek Harness（dsh，Cordis 引擎驱动的插件化 Agent Harness）
- **文件翻译**：DocuTranslate（基于 LLM 的本地多格式文件翻译工具）
- **编排与方法论**：Oh-My-OpenAgent（v5 起的独立 `omo` CLI，senpi 引擎，已脱离 OpenCode 插件形态）、Superpowers-zh（中文 AI 编程方法论 Skills）
- **Agent 配置方案**：My OpenCode DeepSeek Config（OpenCode × DeepSeek V4 最优纯配置）

### 何时加载此索引？

- 用户想「搭建 LLM 应用」「做 RAG 知识库」「开发 AI Agent」
- 不确定 Dify 和 Hermes Agent 的区别
- 需要中文优化的提示词模板

---

## 技能列表

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [dify](./dify/SKILL.md) | 开源 LLM 应用开发平台（RAG + 工作流 + Agent） | `llm` `rag` `workflow` `agent` |
| [langchain](./langchain/SKILL.md) | LLM 应用框架（LCEL + LangGraph Agent） | `llm` `agent` `rag` `python` |
| [llamaindex](./llamaindex/SKILL.md) | 私有数据 RAG/索引框架（Workflow/Agent） | `llm` `rag` `indexing` `python` |
| [ollama](./ollama/SKILL.md) | 本地大模型运行与推理（OpenAI 兼容 API） | `llm` `local-inference` `rest-api` `gguf` |
| [huggingface-transformers](./huggingface-transformers/SKILL.md) | HF 模型推理与微调框架（pipeline/Trainer） | `transformers` `pytorch` `nlp` `fine-tuning` |
| [hermes-agent](./hermes-agent/SKILL.md) | 自学习通用型 AI 智能体（终端优先） | `agent` `self-improving` `terminal` |
| [openclaw](./openclaw/SKILL.md) | 多通道个人 AI 助手 Gateway | `agent` `gateway` `assistant` |
| [pi](./pi/SKILL.md) | 极简可扩展终端 AI 编码代理（Agent Harness） | `agent` `coding-agent` `terminal` `typescript` |
| [opencode](./opencode/SKILL.md) | 模型无关的终端 AI 编码代理（配置即代码） | `agent` `coding-agent` `terminal` `mcp` |
| [docutranslate](./docutranslate/SKILL.md) | 基于 LLM 的本地多格式文件翻译工具 | `llm` `translation` `pdf` `mcp` |
| [oh-my-openagent](./oh-my-openagent/SKILL.md) | OmO 5.x 独立 CLI（senpi 引擎，多模型并行 + AST/LSP 工具） | `agent` `omo` `orchestration` `cli` |
| [superpowers-zh](./superpowers-zh/SKILL.md) | 中文 AI 编程方法论 Skills 集合 | `methodology` `chinese` `skill` |
| [deepseek-harness](./deepseek-harness/SKILL.md) | DeepSeek Harness（dsh）：插件化智能体框架 | `agent` `deepseek` `plugin` `cordis` `typescript` |
| [my-opencode-deepseek-config](./my-opencode-deepseek-config/SKILL.md) | OpenCode × DeepSeek 最优配置（单模型 + 思考档，12 Agent/23 Skill） | `opencode` `deepseek` `agent-config` |
| [vllm](./vllm/SKILL.md) | 高吞吐 LLM 推理服务（PagedAttention + OpenAI 兼容 API） | `llm` `inference` `serving` `python` |
| [crewai](./crewai/SKILL.md) | 角色化多 Agent 协作框架（Agent/Task/Crew/Flows） | `agent` `multi-agent` `orchestration` `python` |
| [mineru](./mineru/SKILL.md) | 文档解析引擎：PDF/Office → Markdown/JSON（公式表格） | `pdf` `parsing` `markdown` `rag` |

---

## 快速导航

| 用户需求 | 推荐加载 |
|---------|---------|
| "搭建 LLM 聊天应用" | `dify/SKILL.md` |
| "做 RAG 知识库问答" | `dify/SKILL.md` |
| "开发能自学习/调用工具的 AI Agent" | `hermes-agent/SKILL.md` |
| "搭建多通道个人 AI 助手 / Gateway" | `openclaw/SKILL.md` |
| "在终端用极简 Agent Harness 编码" | `pi/SKILL.md` |
| "在终端用 AI 自主改代码 / 跑命令" | `opencode/SKILL.md` |
| "配置 opencode.json / 省 Token" | `opencode/SKILL.md` |
| "部署/调优 OpenCode×DeepSeek 配置" | `my-opencode-deepseek-config/SKILL.md` |
| "翻译 PDF/Word/Excel/字幕等文件" | `docutranslate/SKILL.md` |
| "用中文 TDD/审查方法论约束 AI" | `superpowers-zh/SKILL.md` |
| "多模型并行编排 / OmO CLI（omo 命令）" | `oh-my-openagent/SKILL.md` |
| "用插件式架构开发 AI Agent" | `deepseek-harness/SKILL.md` |
| "DeepSeek 官方智能体框架 dsh" | `deepseek-harness/SKILL.md` |
| "把 PDF 批量转成 Markdown 喂给 RAG" | `mineru/SKILL.md` |
| "自建高吞吐 OpenAI 兼容推理服务" | `vllm/SKILL.md` |
| "让多个角色 Agent 协作完成复杂任务" | `crewai/SKILL.md` |

---

## 相关分类

- **[gis/](../gis/SKILL.md)** — GIS 领域的 AI 流水线（GeoPipeAgent）
- **[csharp/](../csharp/SKILL.md)** — .NET 后端与前端框架
- **[iot/](../iot/SKILL.md)** — 物联网与嵌入式 AI

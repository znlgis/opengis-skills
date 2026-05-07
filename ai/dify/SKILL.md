---
name: dify
description: Dify 是开源 LLM 应用开发平台，集成 RAG 引擎、工作流编排、Agent、可视化提示词、模型管理（OpenAI/Claude/Gemini/Ollama/通义千问/智谱/百川 等）与 API 网关，让团队能在数小时内构建并上线生成式 AI 应用，支持私有化部署。
tags: llm, workflow, rag, agent, platform
---

> **项目地址：** <https://github.com/langgenius/dify>
>
> **官网：** <https://dify.ai/>
>
> **官方文档：** <https://docs.dify.ai/>
>
> **许可证：** Dify Open Source License（基于 Apache-2.0 + 附加条款）

## 概述

Dify 提供：

- **应用类型**：Chatbot / Agent / Text Generator / Workflow / Chatflow
- **可视化编排**：节点化拖拽（LLM / Knowledge / Tool / IF-Else / 迭代 / 代码）
- **RAG 引擎**：知识库 + 多种检索（向量 / 全文 / 混合 / 重排）
- **多模型**：OpenAI / Anthropic / Gemini / Bedrock / Azure / Ollama / Hugging Face / 通义 / 智谱 GLM / 百川 / Moonshot / DeepSeek / 豆包 / xAI 等
- **工具系统**：内置 + 自定义（OpenAPI Schema）
- **多模态**：图像理解 / TTS / STT
- **API 与 Webhook**：每个应用自动生成 RESTful API
- **多租户 / SSO / RBAC / 监控 / 日志**
- **私有化部署**：Docker Compose / Helm / K8s

---

## 部署（Docker Compose）

```bash
git clone https://github.com/langgenius/dify
cd dify/docker
cp .env.example .env
# 编辑 .env：SECRET_KEY、INIT_PASSWORD 等
docker compose up -d
# Web UI: http://localhost
```

数据持久化在 `./volumes/`。生产环境建议使用外部 PostgreSQL + Redis + 对象存储 + 向量库（Weaviate/Qdrant/PGVector/Milvus）。

### Helm（K8s）

```bash
helm repo add dify https://langgenius.github.io/dify-helm
helm install dify dify/dify -n dify --create-namespace
```

---

## 配置模型供应商

进入 「设置 → 模型供应商」：

- 添加 OpenAI / Azure：填 API Key、Base URL
- Ollama 本地：`http://host.docker.internal:11434`
- 通义千问：DashScope API Key
- 智谱 GLM：API Key
- 设置「系统模型」（默认推理 / 嵌入 / 重排 / TTS / STT）

---

## 创建应用

| 类型 | 用途 |
|------|------|
| Chatbot | 多轮对话，自动会话上下文 |
| Agent | 工具调用 + 推理（ReAct/FunctionCall） |
| Text Generator | 单次生成（写作/翻译/总结） |
| Workflow | 复杂业务流程（节点编排） |
| Chatflow | Chatbot + Workflow（可拖拽对话流程） |

---

## RAG 知识库

1. 「知识库」→ 创建 → 上传 PDF/Word/Markdown/网页/Notion
2. 选择切分模式：自动 / 自定义（分隔符、最大长度、重叠）
3. 选择嵌入模型 + 索引方式（高质量向量 / 经济）
4. 启用混合检索（语义 + 关键词）+ Rerank
5. 在应用中绑定知识库 → 自动生成上下文

---

## 工作流（Workflow）核心节点

| 节点 | 功能 |
|------|------|
| Start | 输入参数 |
| LLM | 模型推理 |
| Knowledge Retrieval | 知识库检索 |
| Question Classifier | 问题分类 |
| HTTP Request | 调用外部 API |
| Code | 运行 Python/JavaScript |
| Tool | 内置/自定义工具 |
| If/Else | 条件分支 |
| Iteration | 迭代列表 |
| Variable Aggregator | 合并变量 |
| Template Transform | Jinja2 字符串模板 |
| Parameter Extractor | 从文本抽参数 |
| End | 输出 |

支持引用上游变量：`{{#node1.text#}}`。

---

## 自定义工具（OpenAPI）

```yaml
openapi: 3.0.0
info: { title: Weather, version: '1.0' }
paths:
  /weather:
    get:
      operationId: getWeather
      parameters:
        - name: city
          in: query
          required: true
          schema: { type: string }
      responses:
        '200': { description: ok }
```

「工具 → 自定义工具」上传后，Agent / Workflow 可直接调用。

---

## API 调用

每个应用自带 API 端点：

```bash
curl -X POST 'https://your-dify/v1/chat-messages' \
  -H 'Authorization: Bearer app-xxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "inputs": {},
    "query": "北京今天天气",
    "user": "user-001",
    "conversation_id": "",
    "response_mode": "streaming"
  }'
```

`response_mode`：`blocking`（同步）/ `streaming`（SSE）。

工作流调用：`POST /v1/workflows/run`。

---

## Webhook / 触发

- 通过 API 嵌入网站、微信公众号、飞书、钉钉
- Dify 提供官方 Web 客户端（`/embed`）与 SDK（Python / Node.js）

---

## 监控与日志

- 「日志与标注」：每条对话/请求详情、token 用量、节点耗时
- 标注后回流为评估集，进行「评估 → 测试集回归」

---

## 性能与生产建议

1. **PostgreSQL 与 Redis 单独部署**，向量库选 Qdrant/Weaviate
2. **WebApp / API / Worker / Sandbox 多副本**
3. 启用 **rerank** 提升检索质量
4. 使用 **Streaming** 减少首字节时间
5. **缓存**：相同 prompt + 输入命中缓存；启用「LLM 节点缓存」
6. **限流**：网关层（Nginx / APISIX）+ 应用 API Key 限速

---

## 典型工作流

### 场景一：搭建企业知识库问答机器人

```yaml
# 整体步骤
1. 准备知识库文档（PDF/Markdown/网页）
2. 知识库 → 上传文档 → 选择嵌入模型（bge-m3）→ 启用混合检索 + Rerank
3. 创建 Chatbot 应用 → 绑定知识库
4. 配置系统提示词："你是企业内部助手，仅基于知识库回答..."
5. 配置模型（GPT-4o-mini 或 DeepSeek-V3）
6. 测试 → 发布 → 获取 API Key
7. 通过 iframe 嵌入官网或对接飞书/钉钉/企微
```

```bash
# API 调用示例
curl -X POST 'https://dify.example.com/v1/chat-messages' \
  -H 'Authorization: Bearer app-xxxxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "inputs": {},
    "query": "公司年假政策是什么？",
    "user": "employee-001",
    "response_mode": "streaming"
  }'
```

### 场景二：构建多步骤审批工作流

```yaml
# Workflow 节点编排
Start → 用户提交申请
  → Question Classifier（判断申请类型：请假/报销/采购）
  → IF/ELSE 分支
    → 请假分支：
      → Code 节点（Python 计算剩余年假）
      → HTTP Request（调 HR 系统校验）
      → LLM 节点（生成审批意见）
    → 报销分支：
      → Parameter Extractor（抽取金额/事由）
      → Knowledge Retrieval（查报销政策）
      → LLM 节点（合规判断）
  → Variable Aggregator（汇总分支结果）
  → Template Transform（生成审批通知）
  → End（返回审批结果 + 通知）
```

---

## AI 使用建议

### 推荐工作流

1. **先选应用类型**：简单问答 → Chatbot，需要工具调用 → Agent，复杂流程 → Workflow/Chatflow
2. **调试提示词**：在「提示词编排」中先用 GPT-4o-mini 快速迭代，确认效果后换大模型
3. **知识库先行**：先上传小批量文档验证切分/检索效果，确认检索质量后再全量导入
4. **节点逐步调试**：Workflow 每加一个节点就运行测试，避免排错困难
5. **监控上线**：启用「日志与标注」，收集真实用户反馈后持续优化

### 关键模式与常见陷阱

- **RAG 检索质量**：中文场景务必选中文嵌入模型（bge-m3 / text2vec），并启用 Rerank
- **模型选择**：Agent 场景必须用支持 Function Calling 的模型（GPT-4o/Claude/DeepSeek-V3），国产小模型可能不支持
- **变量引用**：Workflow 中 `{{#节点名.字段#}}` 语法容易写错，复制节点 ID 粘贴
- **Code 节点限制**：Python/JS 沙箱无网络访问，如需调外部 API 请用 HTTP Request 节点
- **流式响应**：前端对接务必用 SSE（`response_mode: streaming`），否则长回复体验差
- **Token 消耗**：别把所有文档塞进上下文，善用 Knowledge Retrieval 节点的 top_k 限制

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 简单 FAQ 问答 | Chatbot + 知识库 |
| 需要查数据库/调 API | Agent + 自定义工具 |
| 多步骤审批/数据流转 | Workflow |
| 对话式多步骤 | Chatflow |
| 纯文本生成（无对话） | Text Generator |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 上传文档失败 | 检查 `STORAGE_*` 配置（本地 / S3）与权限 |
| 嵌入失败 | 嵌入模型未配置 / 余额不足；切换其它供应商 |
| 私有 Ollama 不通 | Docker 网络：`host.docker.internal` 或自定义网络 |
| 响应慢 | 启用 streaming；缩短 prompt；减少检索 topK |
| 中文检索差 | 使用 `bge-m3` / `text2vec` 等中文嵌入 + jieba 关键词 |

---

## 相关技能

- **hermes-agent** — 轻量级 LLM Agent 框架，适合需要自建后端 Agent 的场景：[../hermes-agent/SKILL.md](../hermes-agent/SKILL.md)
- **oh-my-openagent** — AI Agent 工程化模板集合，覆盖 ReAct/Plan-Execute/Multi-Agent 模式：[../oh-my-openagent/SKILL.md](../oh-my-openagent/SKILL.md)
- **superpowers-zh** — 中文提示词/Skill 工程库，可与 Dify 的提示词编排结合使用：[../superpowers-zh/SKILL.md](../superpowers-zh/SKILL.md)

---

## 参考资源

- 文档：<https://docs.dify.ai/>
- 模板市场：<https://dify.ai/templates>
- 中文教程（znlgis）：<https://znlgis.github.io/ai/tutorial/dify/>
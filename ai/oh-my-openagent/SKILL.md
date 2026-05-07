---
name: oh-my-openagent
description: oh-my-openagent 是开源的 AI Agent 工程化模板/框架集合，封装常用 Agent 模式（ReAct、Plan-Execute、Multi-Agent、Tool Use、RAG）的最佳实践，提供配置化提示词、工具、向量检索与 LLM 适配，便于快速搭建可控、可观测、可上线的智能体应用。
tags: llm, agent, rag, tool-calling, pattern
---

> **项目地址：** <https://github.com/znlgis/oh-my-openagent>（如位置变动请以 znlgis.github.io 为准）
>
> **许可证：** MIT / Apache-2.0（视仓库声明）

## 概述

oh-my-openagent 通常包含：

- **Agent 框架**：ReAct、Plan-Execute、Reflective、CodeAct
- **工具适配**：函数式工具 + OpenAPI 工具 + MCP 工具
- **多 LLM**：OpenAI / Claude / Gemini / 通义 / 智谱 / DeepSeek / Ollama
- **RAG**：可插拔向量库（FAISS/Chroma/Qdrant/Milvus/PGVector）
- **记忆 Memory**：会话短记忆 + 长期向量记忆
- **可观测**：日志 / Tracing（OpenTelemetry / LangSmith）
- **示例 Agent**：客服、数据分析、代码助手、网页自动化

> 不同发行版结构有所差异，本 SKILL 给出通用 Agent 工程模式。

---

## 安装与运行

```bash
git clone https://github.com/znlgis/oh-my-openagent
cd oh-my-openagent
cp .env.example .env       # 配置 LLM API Key、向量库、日志
pip install -r requirements.txt   # 或 pnpm install
python main.py             # 或 pnpm dev
```

`.env` 关键项：

```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE=qdrant
QDRANT_URL=http://localhost:6333
LOG_LEVEL=INFO
```

---

## 项目结构（典型）

```
oh-my-openagent/
├── agents/             # 预置 Agent
├── tools/              # 工具实现
├── prompts/            # 模板提示词（YAML/Jinja2）
├── retrievers/         # RAG 检索器
├── memory/             # 长短期记忆
├── llm/                # LLM 适配器
├── observability/      # 日志、tracing、指标
├── apps/               # 上层应用（CLI / Web / API）
└── examples/           # 示例
```

---

## 核心 Agent 模式

### ReAct

```python
from oh_my_openagent import ReActAgent

agent = ReActAgent(
    llm="gpt-4o-mini",
    tools=[search, calculator, sql_runner],
    max_iter=8,
    system_prompt=open("prompts/react.zh.md").read(),
)
print(agent.run("北京今天 PM2.5？给出 RTI 等级"))
```

### Plan-Execute

```python
from oh_my_openagent import PlanExecuteAgent

agent = PlanExecuteAgent(
    planner_llm="gpt-4o", executor_llm="gpt-4o-mini",
    tools=[...], replan_on_failure=True
)
agent.run("帮我把 ./data/*.csv 合并并按月汇总写到 report.xlsx")
```

### Multi-Agent（角色协作）

```yaml
# agents.yaml
- name: planner
  role: 任务规划
  llm: gpt-4o
- name: coder
  role: 代码执行
  llm: gpt-4o-mini
  tools: [run_python, fs]
- name: critic
  role: 评审
  llm: gpt-4o
```

```python
from oh_my_openagent import MultiAgentTeam
team = MultiAgentTeam.from_yaml("agents.yaml")
team.run("生成一个 NPS 调查报告")
```

---

## 工具开发

```python
from oh_my_openagent.tools import tool

@tool(name="get_weather", description="查询城市天气，参数 city")
def get_weather(city: str) -> dict:
    import requests
    return requests.get("https://wttr.in/" + city + "?format=j1").json()
```

OpenAPI 工具：

```python
from oh_my_openagent.tools.openapi import OpenAPIToolset
ts = OpenAPIToolset.from_url("https://api.example.com/openapi.json",
                             auth=("user", "pwd"))
agent = ReActAgent(llm="gpt-4o-mini", tools=ts.tools())
```

MCP 工具（与 Claude / IDE Agents 互通）：

```python
from oh_my_openagent.tools.mcp import MCPClient
client = await MCPClient.connect("stdio:///path/to/mcp-server")
agent.tools += client.list_tools()
```

---

## RAG 集成

```python
from oh_my_openagent.retrievers import VectorRetriever

retriever = VectorRetriever(
    store="qdrant",
    collection="kb",
    embedder="bge-m3",
    top_k=5,
    rerank="bge-reranker-base"
)
retriever.ingest_dir("./docs")

agent = ReActAgent(
    llm="gpt-4o-mini",
    tools=[retriever.as_tool()],
    system_prompt="先用 retrieve 工具检索相关资料再回答。"
)
```

---

## 记忆 Memory

```python
from oh_my_openagent.memory import VectorMemory, SessionMemory

session = SessionMemory(max_turns=20)
long_term = VectorMemory(store="qdrant", collection="memory")

agent = ReActAgent(llm="gpt-4o-mini",
                   memory=[session, long_term])
```

---

## 评估与回归

```python
from oh_my_openagent.eval import AgentEvalSuite, ToolUseScorer, GroundednessScorer

suite = AgentEvalSuite.from_jsonl("eval/qa.jsonl")
report = suite.run(agent, scorers=[ToolUseScorer(), GroundednessScorer()])
report.save_html("eval/report.html")
```

---

## 部署

- **CLI**：`python -m oh_my_openagent.cli run agents/customer.yaml`
- **API**：FastAPI + SSE 输出 `/agents/{name}/run`
- **容器**：Dockerfile 自带；可与 Dify / Langfuse / Helicone 对接观测

---

## 性能与最佳实践

1. **限制 max_iter**，防止死循环
2. **工具结果摘要**：长 JSON 在工具层先摘要再喂给 LLM
3. **缓存 LLM 调用**（输入哈希）
4. **流式输出**：UI 端 SSE
5. **监控**：每次工具调用、token 用量、延迟、错误率
6. **失败重试 + 退避**

---

## AI 使用建议

### 推荐工作流

1. **选 Agent 模式**：简单任务 → ReAct，多步骤 → Plan-Execute，多角色 → Multi-Agent，代码生成 → CodeAct
2. **配工具**：函数式工具用 `@tool` 装饰器，外部 API 用 OpenAPIToolset，MCP 服务器用 MCPClient
3. **搭 RAG**：先选嵌入模型（bge-m3）→ 选向量库（Qdrant/Chroma/FAISS）→ 文档切分 → 灌入 → 绑定检索器为工具
4. **配记忆**：短期用 SessionMemory（max_turns），长期用 VectorMemory
5. **评估上线**：用 AgentEvalSuite 回归测试 → 部署为 FastAPI SSE 端点

### 关键模式与常见陷阱

- **模型 function-calling 不稳定**：国产模型切换到 ReAct 文本协议（`tool_protocol: react`）
- **工具结果截断**：长 JSON 在工具层先摘要再喂给 LLM，避免 token 超限
- **max_iter 死循环**：ReAct 建议 5-8 轮，Plan-Execute 建议 3-5 轮总计划
- **RAG 检索不准**：中文场景用 bge-m3 嵌入 + bge-reranker 重排，调整切分 chunk_size
- **多 Agent 死锁**：设定全局最大轮次 + 超时，引入 critic 早停
- **Token 省成本**：缓存 LLM 调用（输入哈希相同则命中），流式输出减少首字节时间

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 快速可视化搭建 | Dify Workflow / Agent |
| 轻量级单 Agent 后端 | hermes-agent |
| 需要完整 Agent 工程模板 | oh-my-openagent |
| 桌面/GUI 自动化 | openclaw |
| 提示词/Skill 管理 | superpowers-zh |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 工具调用 JSON 解析失败 | 启用 function-calling / structured-output；或加严格 system prompt |
| 国产模型 tool-call 不稳定 | 改用 ReAct 文本协议；或选支持 function-call 的模型 |
| RAG 检索不准 | 选更好的中文嵌入；启用 rerank；调整切分 |
| token 超长 | 摘要历史；裁剪上下文；用 sliding window |
| 多 Agent 死锁 | 限制最大轮次；引入 critic 早停 |

---

## 相关技能

- **hermes-agent** — 轻量级 Agent 后端框架，适合快速部署单个 Agent：[../hermes-agent/SKILL.md](../hermes-agent/SKILL.md)
- **dify** — 可视化 LLM 应用平台，适合非开发人员构建 AI 应用：[../dify/SKILL.md](../dify/SKILL.md)
- **openclaw** — 桌面/GUI 自动化 Agent，适合 RPA 场景：[../openclaw/SKILL.md](../openclaw/SKILL.md)
- **superpowers-zh** — 中文提示词工程库，其 Skill 可作为 Agent 的 system prompt：[../superpowers-zh/SKILL.md](../superpowers-zh/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/znlgis/oh-my-openagent>
- 中文教程（znlgis）：<https://znlgis.github.io/ai/tutorial/oh-my-openagent/>
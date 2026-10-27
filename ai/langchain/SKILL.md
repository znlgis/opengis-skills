---
name: langchain
description: "Use when building LLM apps in Python with LangChain 1.4.7 — LCEL chains (prompt | model | parser), create_agent with @tool and checkpointer+thread_id memory, RAG (loaders, splitters, PGVector, retriever), init_chat_model across providers; also for `ModuleNotFoundError: langchain.memory`, agent forgetting earlier turns, tools never called, and langchain-core version mismatch."
tags:
  - llm
  - agent
  - rag
  - lcel
  - tool-calling
  - langgraph
  - python
  - framework
---

> **项目地址：** <https://github.com/langchain-ai/langchain>
>
> **官方文档：** <https://python.langchain.com/>（现重定向至 <https://docs.langchain.com/oss/python/langchain/overview>）
>
> **许可证：** MIT
>
> **最新版本：** langchain 1.4.7、langchain-core 1.7.0（PyPI 实测，截至 2026-10；GitHub 最新 Release 标签即 `langchain-core==1.7.0`，LangChain 已按包独立发版）

## 概述

LangChain 是用于构建 LLM 应用的 Python 框架，1.x 起以 LangGraph 为运行时，官方推荐入口为 `create_agent` 与 LCEL 管道语法。

- **模型层**：`init_chat_model` 统一初始化 OpenAI / Anthropic / Google / DeepSeek / Ollama 等模型
- **LCEL**：`prompt | model | parser` 声明式组合 Runnable，天然支持 `invoke / batch / stream`
- **Agents**：`create_agent` 构建工具调用循环（Tool Calling Loop），基于 LangGraph 图执行
- **Tools**：`@tool` 装饰器把 Python 函数暴露给模型
- **RAG**：文档加载（langchain-community）→ 切分（langchain-text-splitters）→ 向量库 → 检索器
- **记忆**：短期会话用 checkpointer + `thread_id`；长期记忆用 store（均来自 LangGraph）
- **包拆分**：主包 langchain、接口层 langchain-core、社区集成 langchain-community、各 provider 独立包

包家族与版本（2026-10）：

| 包 | 内容 | 当前版本 |
|------|------|---------|
| langchain | 主包：agents、chat_models、tools | 1.4.7 |
| langchain-core | Runnable/LCEL、消息、提示词、解析器、向量库接口 | 1.7.0 |
| langgraph | 运行时：checkpointer、store | 1.2.18 |
| langchain-community | 社区集成：文档加载器、向量库 | 0.4.2 |
| langchain-openai | OpenAI / Azure 集成 | 1.7.3 |
| langchain-text-splitters | 文本切分器 | 1.1.3 |
| langchain-classic | 旧版链与 memory（兼容维护） | 1.0.8 |

---

## 环境准备

### 安装

```bash
# pip（要求 Python >= 3.10，官方 quickstart 建议 3.11）
pip install -U langchain

# provider 集成是 extras，按需安装
pip install -U "langchain[openai]"
pip install -U "langchain[deepseek]"
pip install -U "langchain[community]"        # 文档加载器等社区集成

# RAG 常用配套
pip install -U langchain-text-splitters langchain-postgres pypdf
```

```bash
# uv（官方推荐流程）
uv python pin 3.11
uv init
uv add langchain
uv sync
```

### API Key 配置

```bash
export OPENAI_API_KEY="sk-..."
export DEEPSEEK_API_KEY="sk-..."          # 使用 DeepSeek 时
export ANTHROPIC_API_KEY="sk-ant-..."     # 使用 Claude 时
```

在代码中加载 `.env`（需 `pip install python-dotenv`）：

```python
from dotenv import load_dotenv

load_dotenv()
```

### 验证安装

```bash
python -c "import langchain, langchain_core; print(langchain.__version__)"
```

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-5.5", temperature=0)
print(model.invoke("用一句话说明 LangChain 是什么").text)
```

---

## 核心 API/命令

### ChatModel 初始化与调用

`init_chat_model` 接受 `"{model_provider}:{model}"` 字符串，也可传 `model` + `model_provider` 两个参数：

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-5.5", temperature=0.5, timeout=600, max_retries=6)
# 等价写法
model = init_chat_model("deepseek-chat", model_provider="deepseek")

# 单次调用 / 流式 / 批量
response = model.invoke("Why do parrots have colorful feathers?")
for chunk in model.stream("介绍一下 GDAL"):
    print(chunk.text, end="", flush=True)
results = model.batch(["问题一", "问题二"], config={"max_concurrency": 5})
```

### 消息与提示词

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一名 GIS 工程师助手。"),
    ("human", "用 {level} 的口径解释 {topic}。"),
])
```

消息对象来自 `langchain.messages`（`SystemMessage` / `HumanMessage` / `AIMessage` / `ToolMessage`）；`model.invoke` 既接受纯字符串，也接受 `{"role": ..., "content": ...}` 字典列表。

### LCEL 链（prompt | model | parser）

所有组件（Prompt、Model、Parser、Retriever）都是 Runnable，用 `|` 组合成 RunnableSequence：

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
chain = prompt | model | parser
print(chain.invoke({"level": "初学者", "topic": "坐标参考系"}))
```

```python
# 并行分支与透传
from langchain_core.runnables import RunnablePassthrough

chain = {
    "context": retriever,
    "question": RunnablePassthrough(),
} | prompt | model | StrOutputParser()
```

### 工具定义（@tool）

```python
from langchain.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database for records matching the query.

    Args:
        query: Search terms to look for
        limit: Maximum number of results to return
    """
    return f"Found {limit} results for '{query}'"
```

- docstring 成为工具描述（进入模型 prompt），类型注解定义输入 schema，二者必须写清楚
- 自定义名称与描述：`@tool("web_search", description="...")`
- 复杂入参用 Pydantic：`@tool(args_schema=WeatherInput)`
- 保留参数名 `config`、`runtime` 不可占用（运行时注入用 `ToolRuntime`）

### Agents（create_agent）

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5.5",
    tools=[search_database],
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)
result = agent.invoke({"messages": [{"role": "user", "content": "查一下成都的订单"}]})
print(result["messages"][-1].text)
```

`create_agent` 常用参数：`model`、`tools`、`system_prompt`、`checkpointer`、`response_format`、`state_schema`、`store`、`middleware`。

### 结构化输出

```python
from pydantic import BaseModel

class Answer(BaseModel):
    summary: str
    confidence: float

# 模型级
structured_model = model.with_structured_output(Answer)
# Agent 级：结果放在 result["structured_response"]
agent = create_agent(model="openai:gpt-5.5", tools=[], response_format=Answer)
```

### 记忆（会话历史）

1.x 不再使用 `langchain.memory`（已移入 langchain-classic 兼容包），会话历史由 LangGraph checkpointer 管理：

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(model="openai:gpt-5.5", tools=[], checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "session-001"}}
agent.invoke({"messages": [{"role": "user", "content": "记住：我在成都"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "我在哪座城市？"}]}, config=config)  # 同一 thread_id 保留历史
```

生产环境换持久化 checkpointer：`SqliteSaver`（langgraph-checkpoint-sqlite）、`PostgresSaver`（langgraph-checkpoint-postgres）；长期记忆用 `store`（如 `InMemoryStore`、`PostgresStore`）配合 `create_agent(..., store=store)`。

### RAG 组件

```python
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_postgres import PGVector

# 加载与切分
docs = PyPDFLoader("gis_manual.pdf").load()
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
splits = splitter.split_documents(docs)

# 向量库：本地内存 / 生产 PostgreSQL（psycopg3 连接串）
vector_store = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-large"))
vector_store = PGVector(
    embeddings=OpenAIEmbeddings(model="text-embedding-3-large"),
    collection_name="gis_docs",
    connection="postgresql+psycopg://user:pass@localhost:5432/gis",
    use_jsonb=True,
)
vector_store.add_documents(splits)
retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 4})
```

---

## 典型工作流

### 工作流一：RAG 问答链（LCEL）

```python
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

docs = PyPDFLoader("gis_manual.pdf").load()
splits = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150).split_documents(docs)

vector_store = InMemoryVectorStore(OpenAIEmbeddings(model="text-embedding-3-large"))
vector_store.add_documents(splits)
retriever = vector_store.as_retriever(search_kwargs={"k": 4})

prompt = ChatPromptTemplate.from_messages([
    ("system", "仅依据以下上下文回答，无法回答时明确说明。\n\n{context}"),
    ("human", "{question}"),
])
model = init_chat_model("openai:gpt-5.5", temperature=0)

chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | model | StrOutputParser()
print(chain.invoke("如何用 GDAL 做栅格重投影？"))
```

### 工作流二：带记忆的工具调用 Agent

```python
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: City name
    """
    return f"Current weather in {location}: 22 C, sunny"

agent = create_agent(
    model="openai:gpt-5.5",
    tools=[get_weather],
    system_prompt="你是天气助手，回答简洁。",
    checkpointer=InMemorySaver(),
)
config = {"configurable": {"thread_id": "weather-demo"}}
agent.invoke({"messages": [{"role": "user", "content": "北京天气如何？"}]}, config=config)
result = agent.invoke({"messages": [{"role": "user", "content": "那明天呢？"}]}, config=config)
print(result["messages"][-1].text)
```

### 工作流三：GIS 实战——自然语言查询 PostGIS + 生成/执行 GDAL 命令

把数据库与命令行封装为工具，交给 `create_agent` 编排（需 `pip install psycopg`，并确保 GDAL 已加入 PATH）：

```python
import shlex
import subprocess

import psycopg
from langchain.agents import create_agent
from langchain.tools import tool

ALLOWED_GDAL = {"gdalinfo", "gdal_translate", "gdalwarp", "ogr2ogr"}

@tool
def query_postgis(sql: str) -> str:
    """执行只读 SQL 查询 PostGIS 并返回结果（建议用 ST_AsGeoJSON 输出几何）。

    Args:
        sql: 以 SELECT 开头的只读 SQL 语句，可使用 PostGIS 的 ST_* 函数
    """
    if not sql.strip().lower().startswith("select"):
        return "拒绝执行：仅允许 SELECT 查询"
    with psycopg.connect("postgresql://gis_ro:pass@localhost:5432/gis") as conn:
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = '10s'")
            cur.execute(sql)
            rows = cur.fetchall()
    return str(rows[:50])

@tool
def run_gdal(command: str) -> str:
    """执行 GDAL 命令行工具（白名单内），返回标准输出。

    Args:
        command: 完整命令，如 "gdalinfo input.tif" 或 "gdalwarp -t_srs EPSG:4326 in.tif out.tif"
    """
    args = shlex.split(command)
    if not args or args[0] not in ALLOWED_GDAL:
        return f"仅允许执行：{sorted(ALLOWED_GDAL)}"
    proc = subprocess.run(args, capture_output=True, text=True, timeout=120)
    return proc.stdout or proc.stderr

agent = create_agent(
    model="openai:gpt-5.5",
    tools=[query_postgis, run_gdal],
    system_prompt=(
        "你是 GIS 助手：查询数据用 query_postgis（先看表结构再写 SQL）；"
        "处理栅格/矢量文件用 run_gdal，执行前先向用户复述即将运行的命令。"
    ),
)

result = agent.invoke({"messages": [{
    "role": "user",
    "content": "统计成都市内 2023 年后建成的学校数量，并列出名称",
}]})
print(result["messages"][-1].text)
```

---

## 最佳实践

1. **优先 1.x 写法**：Agent 用 `create_agent`、链路用 LCEL；`LLMChain`、`ConversationBufferMemory` 等旧预制链已移出主包，新项目不要再用
2. **模型配置集中化**：统一用 `init_chat_model("provider:model")`，切换供应商只改字符串；provider 包按需安装
3. **工具描述即提示词**：docstring 写清"何时用、参数含义"，类型注解不可省；避免同名/空格命名，用 snake_case
4. **结构化输出不要手写 JSON 解析**：模型级用 `with_structured_output`，Agent 级用 `response_format`
5. **会话隔离**：所有多轮调用固定 `thread_id`；生产环境用 Sqlite/Postgres checkpointer 替代 `InMemorySaver`
6. **RAG 质量三要素**：切分粒度（中文可减小 chunk_size 并按标点切）、元数据保留 `source` 便于溯源、检索 `k` 与 MMR 参数按数据调优
7. **工具安全**：SQL 工具只开只读连接并设 statement_timeout；命令工具用白名单 + 超时；不要用 `shell=True`
8. **可观测性**：设置 `LANGSMITH_TRACING=true` 与 `LANGSMITH_API_KEY` 接入 LangSmith，逐层查看 prompt/工具调用
9. **成本控制**：长会话加摘要/裁剪中间件，限制检索 `k`，批量调用设 `max_concurrency`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `pip install langchain` 后 `import langchain_openai` 报 ModuleNotFoundError | provider 集成是 extras：装 `pip install "langchain[openai]"` 或单独 `pip install langchain-openai` |
| 调用模型报 `AuthenticationError` / 找不到 API Key | 检查环境变量名（`OPENAI_API_KEY` 等）是否正确、是否 `load_dotenv()`；确认 Key 与 provider 匹配 |
| `from langchain.memory import ConversationBufferMemory` 报错 | 1.x 已移除 memory 模块；改用 checkpointer + `thread_id`，或安装 `langchain-classic` 兼容旧代码 |
| 多轮对话不记得上文 | `create_agent` 未传 `checkpointer`，或每次调用 `thread_id` 不同；两者都需正确设置 |
| 工具从未被模型调用 | 检查工具 docstring 与类型注解；确认所选模型支持 tool calling；可用 `model.bind_tools([...])` 单独验证 `response.tool_calls` |
| 如何拿到 Agent 最终答案 | 取 `result["messages"][-1].text`（或 `.content`）；消息列表同时包含工具调用等中间消息 |
| RAG 检索结果不相关 | 调整 chunk_size / chunk_overlap；中文场景按句号等标点切分；换更强的嵌入模型；检索加 `search_type="mmr"` |
| 长会话超出上下文窗口 | 减少检索 `k` 与历史消息数；接入摘要中间件；把长文档留在向量库而不是 prompt 里 |

---

## AI 使用建议

### 推荐工作流

1. **先定形态**：单轮生成用 LCEL 链；需要多步推理/调工具用 `create_agent`；RAG 问答两者皆可（LCEL 更可控，Agent 更灵活）
2. **最小验证**：先跑通 `init_chat_model` 的 `invoke`，再加工具，最后加 checkpointer，逐层排查
3. **工具先行**：先把每个工具用普通 Python 调通（含参数校验与异常处理），再包 `@tool` 注册给 Agent
4. **GIS 场景拆解**：数据查询→`query_postgis`，文件处理→`run_gdal`，空间分析逻辑写在 SQL 或 Python 工具内部，不要指望模型心算坐标

### 关键模式与常见陷阱

- **LCEL 输入契约**：`prompt | model | parser` 中 prompt 的变量名必须与链输入字典的 key 完全一致，否则 KeyError
- **消息取用**：`agent.invoke` 返回值是状态字典，最终答复在 `messages[-1]`，不要直接 `print(result)`
- **线程隔离**：`thread_id` 是会话主键；测试与生产、不同用户务必分开，否则历史串话
- **工具错误处理**：工具内抛异常会中断调用；用 `wrap_tool_call` 中间件把异常转为 `ToolMessage` 让模型自行纠错
- **包版本**：`langchain` 与 `langchain-core` 大版本需配套（1.x 搭配 1.x）；混装 0.x 与 1.x 会出现导入错误
- **不要编造**：`init_chat_model` 的 provider 名、`@tool` 参数、checkpointer 路径均以官方文档为准，升级后优先查 reference.langchain.com

## 相关技能

- **dify** — 可视化 LLM 应用平台，适合不想写代码的 RAG/工作流场景：[../dify/SKILL.md](../dify/SKILL.md)
- **deepseek-harness** — 插件化 Agent Harness（TypeScript），可与 LangChain 服务互补：[../deepseek-harness/SKILL.md](../deepseek-harness/SKILL.md)
- **docutranslate** — 基于 LLM 的多格式文件翻译，可作为 RAG 文档预处理环节：[../docutranslate/SKILL.md](../docutranslate/SKILL.md)
- **openclaw** — 多通道个人 AI 助手 Gateway，可承载 LangChain 构建的对话服务：[../openclaw/SKILL.md](../openclaw/SKILL.md)

---

## 参考资源

- 官方文档（现址）：<https://docs.langchain.com/oss/python/langchain/overview>
- Quickstart：<https://docs.langchain.com/oss/python/langchain/quickstart>
- Agents 指南：<https://docs.langchain.com/oss/python/langchain/agents>
- Tools 指南：<https://docs.langchain.com/oss/python/langchain/tools>
- 检索与 RAG：<https://docs.langchain.com/oss/python/langchain/retrieval>
- 集成目录（加载器/向量库）：<https://docs.langchain.com/oss/python/integrations/vectorstores/pgvector>
- API Reference：<https://reference.langchain.com/python/>
- GitHub Releases：<https://github.com/langchain-ai/langchain/releases>

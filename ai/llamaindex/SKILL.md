---
name: llamaindex
description: "Use when building RAG and agent applications over documents with LlamaIndex — SimpleDirectoryReader loading, node parsers, VectorStoreIndex with local or external vector stores (Chroma, PGVector, Qdrant), query engines and response modes, chat engines, RouterQueryEngine routing, event-driven Workflows, and FunctionAgent tool calling. Includes GIS use cases such as turning standards and GIS documents into a knowledge base. Covers llama-index 0.14.x (MIT, Python 3.10+)."
tags:
  - llm
  - rag
  - indexing
  - query-engine
  - chat-engine
  - workflows
  - agent
  - vector-store
  - retrieval
  - python
---

> **项目地址：** <https://github.com/run-llama/llama_index>
>
> **官方文档：** <https://docs.llamaindex.ai/>（2026 年起 301 重定向至 <https://developers.llamaindex.ai/python/framework/>）
>
> **许可证：** MIT
> **最新版本：** llama-index 0.14.25、llama-index-core 0.14.25（PyPI，2026-10；GitHub 最新 Release 标签为 `v0.14.25`，包按组件独立发版）

## 概述

LlamaIndex 是连接大语言模型与私有数据的 Python 框架，核心流程是把文档切分为节点（Node）、建立索引并对外暴露查询与对话接口。

- **数据加载**：`SimpleDirectoryReader` 等 Reader 把 PDF / Markdown / Word / 网页等解析为 `Document`
- **切分**：`SentenceSplitter`、`TokenTextSplitter` 等 Node Parser 把 `Document` 切成带元数据的 `Node`
- **索引**：`VectorStoreIndex` 建立向量索引，另有 `SummaryIndex`、`KeywordTableIndex` 等
- **存储**：`StorageContext` 统一挂载向量库、文档库、索引库，可持久化到磁盘或外部数据库
- **检索与合成**：Retriever 召回节点，Response Synthesizer 按响应模式（response_mode）合成答案
- **上层接口**：Query Engine（单轮）、Chat Engine（多轮）、Router（多路选择）、Workflows（事件驱动）、Agent（工具调用）

包拆分（2026-10，`pip install llama-index` 元包仅拉取以下四项）：

| 包 | 内容 | 当前版本 |
|------|------|---------|
| llama-index | 元包：core + OpenAI LLM/嵌入集成 + nltk | 0.14.25 |
| llama-index-core | 索引、检索、Workflows、Agent 等核心 | 0.14.25 |
| llama-index-llms-openai | OpenAI / Azure LLM 集成 | 0.7.x |
| llama-index-embeddings-openai | OpenAI 嵌入集成 | 0.6.x |

其余向量库、嵌入、LLM 集成均为独立包，按需安装。

---

## 环境准备

### 安装

```bash
# 元包：含 core 与 OpenAI 集成，开箱即用（要求 Python >= 3.10）
pip install llama-index

pip install llama-index-core

# 常用集成（按需）
pip install llama-index-embeddings-huggingface      # 本地嵌入模型
pip install llama-index-llms-ollama                 # 本地 LLM
pip install llama-index-vector-stores-chroma        # Chroma
pip install llama-index-vector-stores-postgres      # PostgreSQL / pgvector
pip install llama-index-vector-stores-qdrant        # Qdrant
```

### API Key 配置

```bash
export OPENAI_API_KEY="sk-..."        # Linux / macOS
set OPENAI_API_KEY=sk-...             # Windows cmd
```

在代码中加载 `.env`（需 `pip install python-dotenv`）：

```python
from dotenv import load_dotenv

load_dotenv()
```

### 验证安装

```bash
python -c "import llama_index.core; print(llama_index.core.__version__)"
```

```python
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4o-mini")
print(llm.complete("用一句话说明 LlamaIndex 是什么"))
```

---

## 核心 API/命令

### 全局设置（Settings）

`Settings` 是全局单例，统一配置 LLM、嵌入模型与切分器，未显式传入的组件会回退到这里的默认值：

```python
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter

Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
```

本地模型替换（离线场景）：

```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")
Settings.llm = Ollama(model="qwen3:8b", request_timeout=120.0)
```

### 文档加载与切分

```python
from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core.node_parser import SentenceSplitter

# 加载整个目录（可用 input_files 指定文件）
documents = SimpleDirectoryReader("data").load_data()
documents = SimpleDirectoryReader(input_files=["gis_manual.pdf"]).load_data()

# 也可直接构造 Document
documents = [Document(text="...", metadata={"source": "spec.md"})]

# 切分为节点
parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
nodes = parser.get_nodes_from_documents(documents)
```

要点：`chunk_overlap` 必须小于 `chunk_size`；中文文档建议减小 `chunk_size` 并按标点切分；保留 `metadata` 便于溯源。

### 索引构建与持久化

```python
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage

index = VectorStoreIndex.from_documents(documents)
index.storage_context.persist("storage")          # 持久化到磁盘

# 下次直接加载，无需重新向量化
storage_context = StorageContext.from_defaults(persist_dir="storage")
index = load_index_from_storage(storage_context)
```

也可在构建时指定切分器：`VectorStoreIndex.from_documents(documents, transformations=[SentenceSplitter(...)])`。

### 向量库对接

内存向量库适合快速试验；生产环境把外部向量库挂到 `StorageContext` 即可，索引代码基本不变：

```python
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("gis_docs")
vector_store = ChromaVectorStore(chroma_collection=collection)

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
```

```python
from sqlalchemy import make_url
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.postgres import PGVectorStore

url = make_url("postgresql://user:pass@localhost:5432")
vector_store = PGVectorStore.from_params(
    database="vector_db",
    host=url.host,
    port=url.port,
    user=url.username,
    password=url.password,
    table_name="gis_docs",
    embed_dim=1536,                                # 需与嵌入模型维度一致
    hybrid_search=True,                            # 向量 + 全文混合检索
    text_search_config="simple",
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
```

从已有向量库恢复索引：`VectorStoreIndex.from_vector_store(vector_store=vector_store)`。

`embed_dim` 必须与所选嵌入模型的输出维度一致（如 `text-embedding-3-small` 为 1536），否则写入报错。

### 查询引擎与响应模式

```python
query_engine = index.as_query_engine()             # 默认 response_mode="compact"
response = query_engine.query("如何做栅格重投影？")
print(response)                                    # 答案文本
for node in response.source_nodes:
    print(node.metadata.get("source"), node.score)  # 溯源
```

常用响应模式：

| response_mode | 说明 |
|------|------|
| `compact` | 默认。拼接尽可能多的节点后合成，LLM 调用较少 |
| `refine` | 逐节点迭代改进答案，更细致但调用多 |
| `tree_summarize` | 递归归并各节点答案，适合摘要类问题 |
| `simple_summarize` | 截断所有节点塞进单次 prompt，快但可能丢细节 |
| `no_text` | 只检索不生成，用于查看 `source_nodes` |

```python
# 流式输出
index.as_query_engine(streaming=True).query("总结这份规范").print_response_stream()
# 摘要场景
index.as_query_engine(response_mode="tree_summarize")
```

### 聊天引擎（多轮）

```python
from llama_index.core.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",             # 见下表
    memory=memory,
    verbose=True,
)
print(chat_engine.chat("这份数据用什么坐标系？"))
print(chat_engine.chat("那它的精度是多少？"))       # 保留上文
chat_engine.reset()                                # 清空历史
```

`chat_mode` 取值：`best`（自动选择）、`condense_question`、`context`、`condense_plus_context`（推荐默认）、`simple`（纯 LLM 对话）、`react`（ReAct Agent）、`openai`（OpenAI Agent）。

### 路由（RouterQueryEngine）

当存在多个数据源或多种检索方式时，用 LLM 选择器按工具描述路由：

```python
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, PydanticSingleSelector
from llama_index.core.tools import QueryEngineTool

spec_tool = QueryEngineTool.from_defaults(
    query_engine=spec_engine,
    description="查询测绘规范条款与术语定义，适合规范类问题",
)
catalog_tool = QueryEngineTool.from_defaults(
    query_engine=catalog_engine,
    description="查询空间数据目录与图层元数据，适合数据检索类问题",
)

router = RouterQueryEngine(
    selector=PydanticSingleSelector.from_defaults(),
    query_engine_tools=[spec_tool, catalog_tool],
)
print(router.query("2000 国家大地坐标系的定义是什么？"))
```

`LLMSingleSelector` 把选项以文本注入提示词；`PydanticSingleSelector` 走函数调用返回结构化结果。多选场景用 `LLMMultiSelector` / `PydanticMultiSelector`。

### 工作流（Workflows）

Workflows 是事件驱动、按步骤执行的编排模型：每个 `@step` 接收一个事件、返回一个事件，返回事件的类型决定下一个执行的步骤。

```python
from llama_index.core.workflow import Workflow, step, Event, StartEvent, StopEvent

class ParsedEvent(Event):
    nodes_count: int

class IngestFlow(Workflow):
    @step
    async def parse(self, ev: StartEvent) -> ParsedEvent:
        docs = SimpleDirectoryReader(ev.data_dir).load_data()
        index = VectorStoreIndex.from_documents(docs)
        return ParsedEvent(nodes_count=len(docs))

    @step
    async def report(self, ev: ParsedEvent) -> StopEvent:
        return StopEvent(result=f"已索引 {ev.nodes_count} 个文档")

w = IngestFlow(timeout=120, verbose=True)
result = await w.run(data_dir="data")               # 关键字参数进入 StartEvent
print(result)
```

要点：`StartEvent` / `StopEvent` 由框架提供；自定义事件是 Pydantic 对象；`Context`（`ctx.store`、`ctx.send_event`）用于跨步骤共享状态与动态分发。

### Agent 与工具

```python
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import FunctionTool

def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the product."""
    return a * b

agent = FunctionAgent(
    tools=[multiply, FunctionTool.from_defaults(fn=multiply)],
    llm=Settings.llm,
    system_prompt="你是助手，需要计算时调用工具。",
)
response = await agent.run(user_msg="20 + 2 * 4 等于多少？")
```

`FunctionAgent` 依据工具名、参数、docstring 与类型注解选择工具；普通函数可直接传入，`FunctionTool.from_defaults` 可显式指定名称与描述。其余 Agent 实现包括 `ReActAgent`、`CodeActAgent`。

---

## 典型工作流

### 工作流一：最小 RAG 问答

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
print(query_engine.query("文档中提到的数据精度是多少？"))
```

### 工作流二：GIS 规范知识库 + 地理编码工具 Agent

把规范知识库封装成查询引擎工具，把地理编码封装成函数工具，交给 `FunctionAgent` 编排：

```python
import requests
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import QueryEngineTool

spec_index = VectorStoreIndex.from_documents(SimpleDirectoryReader("specs").load_data())
spec_tool = QueryEngineTool.from_defaults(
    query_engine=spec_index.as_query_engine(),
    name="spec_search",
    description="查询测绘/GIS 规范条款与术语定义，回答规范类问题",
)

def geocode(address: str) -> str:
    """把中文地址解析为经纬度，返回 'lon,lat'。

    Args:
        address: 待解析的地址文本，如 "成都市天府广场"
    """
    resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": address, "format": "json", "limit": 1},
        headers={"User-Agent": "gis-rag-demo"},
        timeout=15,
    )
    hits = resp.json()
    if not hits:
        return f"未找到：{address}"
    return f"{hits[0]['lon']},{hits[0]['lat']}"

agent = FunctionAgent(
    tools=[spec_tool, geocode],
    llm=Settings.llm,
    system_prompt=(
        "你是 GIS 助手：规范与术语问题调用 spec_search；"
        "地址转坐标调用 geocode。不要臆测坐标数值。"
    ),
)
response = await agent.run(user_msg="成都市天府广场的坐标是多少？坐标系的定义依据哪份规范？")
print(response)
```

要点：Agent 只负责编排，坐标换算与空间分析逻辑应写在工具函数内部，不要让模型心算坐标。

---

## 最佳实践

1. **统一走 Settings**：LLM、嵌入模型、切分器集中在 `Settings` 配置，切换供应商只改一处；单索引需要差异化时再按调用参数覆盖
2. **先切分再建索引**：显式设置 `chunk_size` / `chunk_overlap`（overlap < size），中文按标点切分并适当减小 chunk；保留 `metadata`（`source`、页码）便于溯源
3. **嵌入维度对齐**：外部向量库的 `embed_dim` 必须与嵌入模型输出维度一致，换模型时需重建索引
4. **持久化避免重复计算**：实验阶段用 `index.storage_context.persist()` 落盘；生产环境改用 Chroma / PGVector / Qdrant，通过 `from_vector_store` 恢复
5. **响应模式按场景选**：事实问答用 `compact`，长文摘要用 `tree_summarize`，需要溯源用 `no_text` 先看 `source_nodes`
6. **多轮对话用 Chat Engine**：单轮问答用 Query Engine；多轮用 `as_chat_engine(chat_mode="condense_plus_context", memory=ChatMemoryBuffer.from_defaults(token_limit=...))`，避免历史无限增长
7. **多数据源用 Router**：工具 `description` 即路由依据，必须写清"何时选我"，否则选择器误判
8. **复杂流程用 Workflows**：把解析、索引、校验拆成 `@step`，用类型化事件串联，天然支持超时与可观测
9. **工具即接口**：Agent 工具用清晰的 docstring 与类型注解，外部调用加超时；工具内异常应自行捕获返回文本，而不是抛出中断整个 Agent
10. **安全边界**：数据库工具只开只读连接并设 statement_timeout；命令类工具用白名单；不要用 `shell=True`

---

## 常见问题

| 问题 | 排查与解决 |
|------|-----------|
| `pip install llama-index` 后 `import llama_index.llms.ollama` 报 ModuleNotFoundError | 集成是独立包：装 `pip install llama-index-llms-ollama`；元包只含 core 与 OpenAI 集成 |
| 调用模型报 `AuthenticationError` / 找不到 API Key | 检查环境变量名（`OPENAI_API_KEY` 等）并确认已 `load_dotenv()`；Key 需与所用 provider 匹配 |
| 检索结果不相关 | 调整 `chunk_size` / `chunk_overlap`（中文按标点切、适当减小）；换更强的嵌入模型；`as_query_engine(similarity_top_k=...)` 调大召回并考虑混合检索 |
| 答案没有依据 / 想核对出处 | 取 `response.source_nodes`，读取每个节点的 `metadata["source"]` 与 `score`；或先用 `response_mode="no_text"` 只做检索 |
| 多轮对话不记得上文 | 用 Chat Engine 并传入 `memory=ChatMemoryBuffer.from_defaults(token_limit=...)`；Query Engine 无状态，不适合多轮 |
| 写入 PGVector 报维度不匹配 | `embed_dim` 必须等于嵌入模型输出维度（如 `text-embedding-3-small` 为 1536）；换模型后需重建表/索引 |
| Workflows 不执行 / 卡住 | 确认 `@step` 的入参和返回类型注解正确（返回事件类型决定下一跳）；`await w.run(...)` 的参数名需与 `StartEvent` 字段对应；必要时调大 `timeout` |

---

## 参考资源

- 官方文档（现址）：<https://developers.llamaindex.ai/python/framework/>
- 查询引擎与响应模式：<https://developers.llamaindex.ai/python/framework/module_guides/deploying/query_engine/>
- Workflows：<https://developers.llamaindex.ai/python/framework/understanding/workflows/>
- Agent：<https://developers.llamaindex.ai/python/framework/understanding/agent/>
- GitHub Releases：<https://github.com/run-llama/llama_index/releases>
- PyPI：<https://pypi.org/project/llama-index/>

---

## 相关技能

- [langchain](../langchain/SKILL.md) — LLM 应用框架，LCEL 链与 LangGraph Agent，与 LlamaIndex 索引能力可互补
- [dify](../dify/SKILL.md) — 可视化 LLM 应用平台，无需编码即可搭建 RAG 知识库与工作流
- [docutranslate](../docutranslate/SKILL.md) — 基于 LLM 的多格式文件翻译，可作为 RAG 文档预处理环节
- [ollama](../ollama/SKILL.md) — 本地模型运行时，可为 LlamaIndex 提供离线 LLM 与嵌入后端

---

## AI 使用建议

### 推荐工作流

1. **先跑通最小链路**：`SimpleDirectoryReader` → `VectorStoreIndex.from_documents` → `as_query_engine().query()`，确认数据与 Key 正常后再叠加向量库、路由与 Agent
2. **逐层加能力**：单轮问答 → 持久化/外部向量库 → Chat Engine 多轮 → Router 多源 → Workflows/Agent，每层单独验证
3. **工具先行**：Agent 工具先用普通 Python 调通（含参数校验、超时与异常处理），再包成 `FunctionTool` 或直接传入 `FunctionAgent`
4. **GIS 场景拆解**：规范/文档做成向量知识库（spec_search），空间数据目录做成独立索引，地理编码等外部能力封装为函数工具，空间计算写在工具内部
5. **版本敏感**：LlamaIndex 迭代快（当前 0.14.25），文档已从 `docs.llamaindex.ai` 迁至 `developers.llamaindex.ai`；API 以官方文档与 `llama_index.core` 源码为准

### 关键模式与常见陷阱

- **导入路径分两段**：核心一律从 `llama_index.core.*` 导入，各集成从 `llama_index.<类型>.<供应商>` 导入（如 `llama_index.vector_stores.chroma`），两者不可混用
- **Settings 是全局单例**：在进程早期设置一次即可；忘记设置 `embed_model` 时默认回退 OpenAI 嵌入，离线环境会因缺少 Key 报错
- **维度必须对齐**：`PGVectorStore.from_params(embed_dim=...)` 与嵌入模型维度不一致会写入失败，换嵌入模型需重建索引
- **不要编造**：向量库类名、`from_params` 参数、selector 与 Agent 类名均以官方文档为准，升级后优先查 `developers.llamaindex.ai`

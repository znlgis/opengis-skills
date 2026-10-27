---
name: crewai
description: "Use when orchestrating multi-agent work with crewAI 1.15 — Agent/Task/Crew, Process.sequential vs hierarchical, @tool / BaseTool custom tools, or event-driven Flows with @start/@listen/@router and or_/and_ for branching and state; also when tasks ignore their expected_output, tools never fire because the agent lacks them, or a JSON-first project (agents/*.jsonc + crew.jsonc) needs the YAML scaffold via --classic. Includes wiring GIS analysis as tools."
tags:
  - ai
  - agent
  - multi-agent
  - orchestration
  - python
  - llm
  - workflow
  - gis
---

> **项目地址：** <https://github.com/crewAIInc/crewAI>
>
> **官方文档：** <https://docs.crewai.com/>
>
> **PyPI：** `crewai`（1.15.30，截至 2026-10）｜ 工具包：`crewai-tools`（同版号）
>
> **许可证：** MIT

## 概述

crewAI 用两层抽象组织多智能体系统，边界很清楚：

- **Crews（自治）**：`Agent`（角色、目标、背景、工具）+ `Task`（描述、期望产出、依赖）组成团队，`Crew` 按 `Process` 调度执行
- **Flows（可控）**：事件驱动的编排层，`@start` / `@listen` / `@router` 加 `or_` / `and_` 组合条件，带类型化 state，适合生产级分支与重试
- **两者可混用**：Flow 里调 Crew，或 Crew 的某个 Task 触发 Flow，是官方推荐的生产形态
- **Python 原生**：prompt、工具、执行路径、state 都能直接用 Python 改，不跟框架打架
- **生产特性**：结构化输出（`output_pydantic`/`output_json`）、memory、knowledge、checkpointing、异步执行、MCP/A2A 支持
- **脚手架**：1.x 默认 **JSON-first** 项目（`agents/*.jsonc` + `crew.jsonc`），需要传统 YAML/Python 结构用 `--classic`

---

## 环境准备

### 前置条件

| 项 | 要求 |
|----|------|
| Python | `>=3.10,<3.14` |
| 包管理 | 官方推荐 [uv](https://docs.astral.sh/uv/)（CLI 也用它装） |
| 模型 | 任一经 LiteLLM 支持的 provider（OpenAI、Anthropic、DeepSeek、本地 vLLM/Ollama 均可） |

### 方式一：uv tool（官方推荐，装 CLI）

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 安装 crewai CLI
uv tool install crewai
uv tool update-shell      # 若提示 PATH 警告
uv tool list              # 应能看到 crewai
```

后续升级 CLI：`uv tool install crewai --upgrade`（只升全局 CLI，不升项目环境里的 crewai）。

### 方式二：pip（已有虚拟环境时）

```bash
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\Activate.ps1
python -m pip install -U crewai
python -m pip install -U crewai-tools            # 需要现成工具集时
```

### 验证

```bash
crewai version
python -c "import crewai, crewai_tools; print(crewai.__version__)"
```

> Windows 上装 `chroma-hnswlib` 可能报 `fatal error C1083: Cannot open include file: 'float.h'`——装 Visual Studio Build Tools 的「Desktop development with C++」工作负载即可。

---

## 核心模型：Agent / Task / Crew

### 代码式最小 Crew

```python
from crewai import Agent, Crew, Process, Task

researcher = Agent(
    role="Senior Data Researcher",
    goal="Uncover cutting-edge developments in {topic}",
    backstory="You are a seasoned researcher who presents findings clearly.",
    verbose=True,
)

analyst = Agent(
    role="Reporting Analyst",
    goal="Turn research into a clear report",
    backstory="You are a meticulous analyst who writes concisely.",
    verbose=True,
)

research_task = Task(
    description="Research {topic} and list 10 key points.",
    expected_output="A bullet list of 10 relevant points.",
    agent=researcher,
)

report_task = Task(
    description="Expand the research into a full markdown report.",
    expected_output="A markdown report with a section per topic.",
    agent=analyst,
    context=[research_task],
    output_file="output/report.md",
)

crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, report_task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff(inputs={"topic": "AI Agents"})
print(result.raw)
```

### Process 两种

| Process | 行为 | 何时用 |
|---------|------|--------|
| `Process.sequential` | 按任务顺序依次执行 | 步骤线性、依赖清晰 |
| `Process.hierarchical` | 自动指派一个 manager agent 做规划、委派与结果校验 | 任务边界模糊、需要动态拆解 |

层级模式下用 `manager_llm` 或 `manager_agent` 指定管理者。

### 结构化输出

```python
from pydantic import BaseModel

class Verdict(BaseModel):
    passed: bool
    issues: list[str]

review_task = Task(
    description="Review the generated report for factual errors.",
    expected_output="A verdict object.",
    agent=analyst,
    output_pydantic=Verdict,
)
```

要纯 JSON 就用 `output_json=SomeModel`；需要写文件加 `output_file`。

---

## 工具

### 用装饰器定义

```python
import subprocess
from crewai.tools import tool

@tool("Buffer a GeoPackage layer")
def buffer_layer(input_path: str, layer_name: str, distance: float) -> str:
    """Buffer one layer by distance (map units) into out/buffer.gpkg."""
    subprocess.run(
        ["ogr2ogr", "out/buffer.gpkg", input_path, "-nln", "buffered",
         "-dialect", "sqlite",
         "-sql", "SELECT ST_Buffer(geometry, " + str(distance) + ") AS geometry FROM " + layer_name],
        check=True,
    )
    return "wrote out/buffer.gpkg (layer: buffered)"

analyst = Agent(
    role="GIS Analyst",
    goal="Run geoprocessing requests accurately",
    backstory="You are precise and always verify output files exist.",
    tools=[buffer_layer],
)
```

### 继承 BaseTool（需要构造参数时）

```python
import subprocess
from crewai.tools import BaseTool

class QgisProcessTool(BaseTool):
    name: str = "Run qgis_process algorithm"
    description: str = "Run a qgis_process algorithm by id, e.g. native:buffer"

    def _run(self, algorithm: str, params_json: str) -> str:
        out = subprocess.check_output(
            ["qgis_process", "run", algorithm, "--json", params_json], text=True
        )
        return out[:2000]

analyst = Agent(role="GIS Analyst", goal="...", backstory="...", tools=[QgisProcessTool()])
```

### 现成工具

`crewai-tools` 提供搜索引擎、抓取、文件、数据库等一批工具；官方脚手架里在 `tools/` 写自定义工具，然后在 `crew.jsonc` 里用 `"custom:<name>"` 引用。

> 工具必须出现在 agent 的 `tools` 列表里才会被调用；仅定义不挂载等于没写。

---

## Flows：可控编排

```python
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, router, start, or_

class OpsState(BaseModel):
    ready: bool = False
    approved: bool = False
    notes: list[str] = []

class DataFlow(Flow[OpsState]):
    @start()
    def ingest(self):
        self.state.ready = True
        return "ingested"

    @listen(ingest)
    def validate(self):
        self.state.notes.append("validated")

    @router(validate)
    def gate(self):
        return "publish" if self.state.ready and self.state.approved else "hold"

    @listen("publish")
    def publish(self):
        return "published"

    @listen(or_("hold", "publish"))
    def report(self):
        return "done: " + str(self.state.notes)

flow = DataFlow()
flow.kickoff()
```

- `@start`：入口；可以有多个
- `@listen(x)`：x 完成后触发；支持 `or_(...)` / `and_(...)` 组合
- `@router`：返回字符串决定下游走哪条分支
- state 用 Pydantic 模型类型化，分支与重试都基于它

---

## 脚手架与项目结构

```bash
# 默认：JSON-first
crewai create crew my_project
cd my_project

# 传统 Python/YAML 结构（crew.py + config/agents.yaml + config/tasks.yaml）
crewai create crew my_project --classic
```

JSON-first 结构：

```text
my_project/
├── agents/
│   └── researcher.jsonc      # role / goal / backstory / llm / tools / settings
├── crew.jsonc                # agents 列表、tasks、process、inputs
├── knowledge/                # 可选知识文件
├── skills/                   # 可选技能文件
├── tools/                    # 自定义工具
├── .env
└── pyproject.toml
```

`crew.jsonc` 关键字段：

```jsonc
{
  "name": "Latest AI Development",
  "agents": ["researcher", "reporting_analyst"],
  "tasks": [
    { "name": "research_task", "description": "Research {topic}", "expected_output": "10 bullets", "agent": "researcher" },
    { "name": "reporting_task", "description": "Write the report", "expected_output": "markdown",
      "agent": "reporting_analyst", "context": ["research_task"], "output_file": "output/report.md", "markdown": true }
  ],
  "process": "sequential",
  "inputs": { "topic": "AI Agents" }
}
```

运行：

```bash
crewai install
crewai run        # 缺 inputs 时会提示补值
```

`{placeholder}` 写在 agent/task 文本里，默认值放 `crew.jsonc` 的 `inputs`。

---

## 典型工作流

### 工作流一：新建 Crew 并跑通（端到端）

输入：一个业务问题；输出：`output/report.md`。

1. `uv tool install crewai` → `crewai version` 确认
2. `crewai create crew latest-ai-development` → `cd` 进去
3. 改 `agents/researcher.jsonc`：写 role/goal/backstory、`llm`、`tools`
4. 改 `crew.jsonc`：两个 task、`process: "sequential"`、`inputs`
5. `.env` 里填 provider key（用搜索工具再填 `SERPER_API_KEY`）
6. `crewai install` → `crewai run`，检查控制台输出与 `output/report.md`
7. 想要"管理者自动分派"，把 `process` 改成 `hierarchical` 并指定 `manager_llm`

### 工作流二：GIS 分析 Agent（Crew + 自定义工具）

输入：`data/roads.gpkg`；输出：缓冲区图层 + 分析报告。

1. 为每个 GIS 动作写一个薄工具：`ogr2ogr` 转换、`qgis_process run native:buffer`、`gdal warp` 重投影、统计脚本
2. 工具里只做一件事，并返回结构化文本（路径 + 行数 + 关键指标），方便模型判断下一步
3. 配置两个 Agent：`GIS Analyst`（拿工具，负责执行）与 `Report Writer`（不拿工具，负责写结论）
4. Task 串起来：先"读取 `data/roads.gpkg` 并统计要素数"，再"缓冲 100 米到 `out/buffer.gpkg`"，最后"写 300 字摘要到 `out/report.md`"
5. `expected_output` 写清可验收的产物（文件路径 + 字段），否则模型会给你一段散文
6. 跑完检查产物是否真落地；失败就把命令与 stderr 作为 context 回灌下一个 task 重试

### 工作流三：用 Flow 包住 Crew 做生产编排

1. 定义 `State`（Pydantic）承载输入路径、校验结果、重试计数
2. `@start` 做输入校验（文件存在、CRS 合法），不合法直接 `@router` 到失败分支
3. 合法则 `@listen` 里调 `crew.kickoff(inputs=...)`，把结果写进 state
4. `@router` 按结果决定"出图 / 人工复核 / 重跑"
5. 最后 `@listen(or_(...))` 汇总写报告——所有分支都收口到一处

---

## 最佳实践

1. **一个 Task 一个可验收产物**：`expected_output` 写文件路径、字段名、行数这类硬指标
2. **工具薄、职责单一**：工具只调一条命令并返回结构化结果，别把整条流水线塞进一个工具
3. **执行与写作分 Agent**：拿工具的 Agent 只管跑，写结论的 Agent 不拿工具，避免"边跑边编"
4. **Flow 管控制、Crew 管探索**：需要分支/重试/状态就上 Flow，需要多角色头脑风暴再用 Crew
5. **inputs 显式化**：`{placeholder}` 全部落在 `crew.jsonc` 的 `inputs`，别靠模型猜
6. **结构化输出优先**：下游要程序消费就用 `output_pydantic`，别解析自然语言
7. **成本可控**：verbose 只在调试开；hierarchical 会多一轮 manager 调用，别默认开

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `crewai create crew` 建出来的目录与旧教程不一致 | 1.x 默认 JSON-first（`agents/*.jsonc` + `crew.jsonc`）；要 `crew.py` + `config/*.yaml` 加 `--classic` |
| 工具明明定义了却从不被调用 | 没挂到 agent 的 `tools` 列表；或工具 description 没写清"什么时候用" |
| Task 输出跑偏、缺文件 | `expected_output` 太含糊；改成可验收的产物描述，必要时加 `output_file` |
| `crewai run` 提示缺参数 | `crew.jsonc` 的 `inputs` 没给默认值而模板里有 `{placeholder}`；CI 里要预填 |
| Windows 安装报 `chroma-hnswlib` / `float.h` 编译错误 | 装 Visual Studio Build Tools 的「Desktop development with C++」工作负载 |
| provider key 配了仍报鉴权 | `.env` 放在项目根、变量名与 provider 约定一致；确认 `llm` 字段写的是 `provider/model` 形式 |
| hierarchical 模式跑得很慢/很贵 | 每步多了 manager 决策；任务线性时改回 `sequential` |
| Flow 的分支不触发 | `@router` 返回的字符串要与下游 `@listen` 的参数完全一致；组合条件用 `or_`/`and_` 而不是布尔表达式 |
| 结构化输出解析失败 | Pydantic 模型字段别用复杂嵌套；失败时减少字段或用 `output_json` |

---

## AI 使用建议

- **推荐工作流模式**：先判断"要自治还是要控制"——多角色协作/头脑风暴用 Crew（`Process.sequential` 起步，需要动态分派再上 hierarchical）；有分支、重试、人工卡点就包一层 Flow。GIS 场景把每个外部命令封成薄工具，Agent 只负责选工具与串步骤。
- **关键注意事项**：① 1.x 默认 JSON-first，老教程的 YAML 结构要加 `--classic`；② 工具必须挂到 agent 才算数；③ `expected_output` 是可验收性的关键；④ Python 3.10–3.13；⑤ Flow 的 router 返回值必须与 listen 的字符串一致。
- **常用代码模式**：Crew = `Agent(...)` + `Task(..., agent=..., context=[...], output_pydantic=Model)` + `Crew(agents=[...], tasks=[...], process=Process.sequential).kickoff(inputs={...})`；工具 = `@tool("name")` 或 `class X(BaseTool)`；Flow = `class F(Flow[State])` + `@start/@listen/@router`。
- **不要臆造**：没有 `crewai.CrewAI()` 这种入口；`crewai_tools` 与 `crewai` 是两个包（工具要单独装）；YAML 的 `config/agents.yaml` 只在 `--classic` 结构里存在。

---

## 相关技能

- **langchain** — 通用 LLM 编排框架，可把 Crew 的某一步换成 LCEL 链：[../langchain/SKILL.md](../langchain/SKILL.md)
- **llamaindex** — RAG 侧框架，给 Crew 提供检索工具：[../llamaindex/SKILL.md](../llamaindex/SKILL.md)
- **vllm** — 自建 OpenAI 兼容端点，作为 Crew 的本地模型后端：[../vllm/SKILL.md](../vllm/SKILL.md)
- **dify** — 低代码 LLM 应用平台（另一种可视化编排形态，可对照选型）：[../dify/SKILL.md](../dify/SKILL.md)
- **mineru** — 解析后的文档作为 Crew 的知识/检索来源：[../mineru/SKILL.md](../mineru/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/crewAIInc/crewAI>
- 文档：<https://docs.crewai.com/>
- 快速开始：<https://docs.crewai.com/en/quickstart>
- Flows：<https://docs.crewai.com/concepts/flows>
- LLM 配置：<https://docs.crewai.com/en/concepts/llms>
- 示例仓库：<https://github.com/crewAIInc/crewAI-examples>
- 官方 Skills（给编码 Agent 用的脚手架指引）：<https://github.com/crewAIInc/skills>

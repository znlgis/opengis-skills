---
name: mineru
description: "Use when turning PDFs, scans, or Office documents into structured Markdown/JSON for RAG or translation pipelines with MinerU 4.1 — mineru parse / mineru-kit parse, quality tiers flash/basic/standard/advanced, DoclibClient Python SDK, V1 HTTP API, or Docker on NVIDIA GPUs; also when magic-pdf commands fail because 4.0 renamed the entrypoints, when a parse returns quality_tier_unavailable, or when a CI image has no GPU and you need the ONNX/llama.cpp CPU path."
license: MIT
metadata:
  category: ai
  tags: "pdf, ocr, document-parsing, rag, markdown, python, vlm, cli, gpu"
---

> **项目地址：** <https://github.com/opendatalab/MinerU>
>
> **官方文档：** <https://opendatalab.github.io/MinerU/>
>
> **最新版本：** 4.1.7（截至 2026-11，[PyPI](https://pypi.org/project/mineru/) 实测；4.1 相对 4.0 有破坏性接口变更，见下文）
>
> **许可证：** AGPL-3.0

## 概述

MinerU 把 PDF、扫描件、图片与多种办公文档解析成**结构化 Markdown / JSON**，输出保留版面顺序、公式、表格与图片资源，可直接喂给 RAG 检索、翻译流水线或人工复核。

- **多档质量**：`flash`/`basic`/`standard`/`advanced` 四档，按"速度 ↔ 精度 ↔ 硬件"取舍，而不是按旧版 backend 名字猜
- **两个入口**：`mineru`（库式、带缓存与续读协议）与 `mineru-kit`（无状态、一次到底）
- **本地文档库**：解析结果落库，用 `doc:.../page:N` 定位符续读，不必反复整篇重解析
- **可编程**：Python `DoclibClient` 与 V1 HTTP API；另有 WebUI 与服务模式
- **后端自动选择**：小模型走 ONNX/Torch，VLM 走 llama.cpp / vLLM / LMDeploy，按本机依赖与设备自动挑
- **容器化**：官方 Dockerfile 面向 Linux + NVIDIA（Windows 走 WSL2）

---

## 环境准备

### 前置条件

| 项 | 要求 |
|----|------|
| Python | `>=3.11,<3.15`（4.1 起不再支持 3.10；推荐 3.12） |
| 操作系统 | Linux / macOS / Windows；Docker 路径只覆盖 Linux + NVIDIA GPU |
| 硬件 | CPU 可跑（ONNX 小模型 + llama.cpp Vulkan）；NVIDIA GPU 装 `mineru[full]` 吞吐最好 |
| 磁盘 | 模型权重与文档库需要额外空间，默认在 `~/.mineru/models` |

### 方式一：uv 虚拟环境（官方推荐）

```bash
pip install uv
uv venv .mineru --python 3.12

# Linux/macOS
source .mineru/bin/activate
# Windows (PowerShell)
.\ .mineru\Scripts\Activate.ps1

uv pip install -U "mineru>=4.1,<5"
```

### 方式二：普通 pip（已有环境时）

```bash
python -m pip install -U "mineru>=4.1,<5"
```

需要最好吞吐时装 extras：

```bash
# NVIDIA GPU 推荐：自带匹配的 torch 与推理引擎
uv pip install -U "mineru[full]>=4.1,<5"

# 只补 torch 侧
uv pip install -U "mineru[torch]>=4.1,<5"
```

> Windows 上 GPU 版 torch 需要单独装；macOS 默认安装即为最佳吞吐，不需要 `[full]`。

### 方式三：Docker（Linux + NVIDIA）

```bash
# 在仓库根目录（含 4.x Dockerfile）执行；国内源用 docker/china/Dockerfile
docker build -t mineru:4 -f docker/global/Dockerfile .
```

基础镜像保留 vLLM 0.21.0、默认 CUDA 13.0（可改用文件中注释的 cu129 基础镜像）；镜像按包索引区间 `mineru[torch]>=4.0,<5` 安装，tag 不锁定版本，需可复现时在 Dockerfile 里改成精确版本。构建期显式下载 Torch 小模型与 vLLM 权重（可在无 GPU 构建机上准备），运行期固定 `MINERU_MODEL_SMALL_BACKEND=torch`、`MINERU_MODEL_VLM_ENGINE=vllm`。国内版 Dockerfile 走 ModelScope，global 版走 Hugging Face。

### 验证

```bash
mineru version --json          # 4.x 的版本查询；老 CLI 用 mineru --version
mineru-kit models show         # 打印实际生效的小模型后端与 VLM 引擎
mineru --help                  # 查看当前安装支持的子命令
mineru-kit parse --help        # 无状态入口
```

---

## 命令行入口

### `mineru`：带文档库的库式入口

默认只解析 PDF 的**前 10 页**，并返回定位符供续读——适合对话式/增量式阅读。

```bash
# 解析并输出 JSON（默认前 10 页）
mineru parse "document.pdf" --json

# 指定页范围与返回体量
mineru parse "book.pdf" --pages 1-10 --limit 12000 --json

# 按定位符继续读（不会重新解析）
mineru read "doc:ab12cd3/tier:standard/page:11" --limit 12000 --json
mineru read "doc:ab12cd3/tier:standard/page:42" --context 1 --json

# 把某一页的某个块导出成图片
mineru read "doc:ab12cd3/tier:standard/page:12/block:5" --format image --output ./page12-block5.png

# 在已索引的文档里检索
mineru search "liquidated damages" --min-tier basic --json

# 强制重解析
mineru parse --force "document.pdf" --json
```

管理类子命令：

```bash
mineru show          # 解析/文档状态
mineru list          # 已索引文档
mineru find <name>   # 按文件名找文档
mineru watch <dir>   # 加入/刷新受监视目录
mineru scan          # 扫描受监视目录
mineru forget <path> # 从库中移除（不删原文件）
mineru invalidate    # 让缓存结果失效
mineru usage --json  # 用量
```

### `mineru-kit`：无状态一次性转换

适合批处理与 CI：默认处理**全部页面**，直接落文件。

```bash
# 单文件 → Markdown
mineru-kit parse document.pdf -o document.md --tier standard

# 目录批量 → zip
mineru-kit parse ./documents -o ./output --format zip

# 网页存档（MHTML 等按整篇处理，需显式 flash 档）
mineru-kit parse saved-page.mhtml -o saved-page.md --tier flash

# 预下载模型（按档位）
mineru-kit models download --tier standard

# WebUI
mineru-kit webui
```

页范围写法：`1-5,8,r3-r1`——`r1` 是末页，`all` 是整篇。

---

## 质量档位与后端

| 档位 | 适用 | 本机执行方式 |
|------|------|--------------|
| `flash` | 快速预览、建索引、原生文本文档 | 原生 PDF 文本层 / 扫描件走 Flash OCR |
| `basic` | OCR、公式与表格 | ONNX 或 Torch 小模型，不需要本地 VLM |
| `standard` | 复杂版面、高质量解析（**默认**） | 小模型 + VLM |
| `advanced` | 更高的质量要求 | Standard 模型栈，加更多推理计算 |

- PDF 与图片四档都支持；Office / ODF / RTF / EPUB / OFD / HTML / MHTML / CSV 走本地 Flash 整篇解析（Python SDK 里要显式传 `tier="flash"`）
- 纯文本不解析，但可以被文档库索引与读取
- 本地 `parse()` 与 `mineru-kit parse` 对 PDF 默认 Standard；Advanced 需显式指定，没有单独的 Advanced 模型下载

自动后端选择：

| 环境 | 小模型 | VLM |
|------|--------|-----|
| Apple Silicon / MPS | Torch / MPS | llama.cpp |
| Linux / Windows，基础包 | 无 Torch 加速时 ONNX / CPU | llama.cpp |
| Linux，有加速器 + full Torch | vLLM，否则 LMDeploy | — |
| Windows，有加速器 + full Torch | LMDeploy | — |
| 纯 CPU | ONNX / CPU | llama.cpp |

显式指定但依赖缺失会**直接报错**，不会静默换后端。

---

## 配置

配置文件在 `$MINERU_HOME/config.yaml`，可用 `MINERU_CONFIG` 指向别处。3.x 的 `mineru.json` 不再被读取，`model.stack`/`MINERU_MODEL_STACK`/`--stack` 已移除，两个组件分开配置：

```yaml
model:
  source: auto
  base_dir: ~/.mineru/models
  small_backend: auto
  vlm:
    engine: auto
```

远程 VLM 走 `model.vlm.server_url` + `model.vlm.api_key`/`model.vlm.model`；环境变量对应 `MINERU_MODEL_VLM_API_KEY`/`MINERU_MODEL_VLM_MODEL`。旧变量 `MINERU_VL_API_KEY`/`MINERU_VL_MODEL_NAME` 仍被识别，但若与新配置冲突会报错要求你清理。

改配置后要重启相关服务，并按后端选择重新下载/校验模型——旧的模型目录存在不等于就绪。

---

## Python SDK 与 HTTP API

### DoclibClient（先起服务）

```bash
mineru server start
mineru server status --json
mineru server stop
```

> 4.1 起 Doclib 首次启动自动生成本机 token（写入实际 `config.yaml` 的 `doclib.auth.token`），CLI 自动读取；**直接集成**必须带凭据：`DoclibClient(base_url=..., token=...)` 或 HTTP 头 `Authorization: Bearer <token>`，否则 UDS/TCP 接口一律拒绝。`MINERU_DOCLIB_AUTH_TOKEN` 可覆盖文件值。

```python
import time

from mineru import DoclibClient
from mineru.doclib import ParseRequest

client = DoclibClient()
submit = client.ensure_parse(ParseRequest(path="paper.pdf", tier="standard"))

# ensure_parse 立即返回，轮询它创建出来的解析任务
for parse_id in submit.wait_parse_ids:
    parse = client.get_parse(parse_id)
    while parse.status in ("pending", "parsing"):
        time.sleep(1)
        parse = client.get_parse(parse_id)
    if parse.status != "done":
        raise RuntimeError(f"{parse_id} -> {parse.status}: {parse.error_code} {parse.error_msg}")

content = client.read_content(f"doc:{submit.short_id}/tier:standard/page:1")
print(content.content)
```

`DoclibClient` 还覆盖检索、受监视目录、页/块定位符续读与结果失效；`help(DoclibClient)` 可看全貌。

### V1 HTTP API（4.1：Tasks 是唯一异步入口）

```bash
# 起自部署 API 服务（/v1 前缀，浏览器 /docs 看 OpenAPI）
mineru-kit api-server --host 127.0.0.1 --port 8000 --tier standard

curl -s http://127.0.0.1:8000/v1/health
curl -s http://127.0.0.1:8000/v1/tiers      # 只描述 PDF/图片可用档位
# 提交 JSON 清单（files[].file_name / bytes 或 url / 可选 sha256sum/page_range）
curl -s -X POST http://127.0.0.1:8000/v1/tasks \
  -H 'Content-Type: application/json' \
  -d '{"tier":"standard","files":[{"file_name":"document.pdf","bytes":123456}]}'
# 用创建回执里的 upload（PUT 地址+请求头）上传缺失文件，然后轮询
curl -s http://127.0.0.1:8000/v1/tasks/<task_id>
curl -s -X POST http://127.0.0.1:8000/v1/tasks/<task_id>/cancel
```

要点：

- **4.1 是破坏性协议升级**：独立的 `/v1/uploads` 与 `/v1/parse/jobs` 全部路由已移除（返回 404，无别名）；旧客户端必须改走 Tasks。
- 状态：父任务 `waiting-file/pending/running/completed/partial/failed/canceled`；每个成功文件在 `files[].result_url` 单独下载，父任务没有总 ZIP。
- `output_formats` 取 `default`（Markdown + JSON + images 的 ZIP）、`docx`、`html`、`latex`；`include_model_output` 已删除（提交即 400）。
- 单文件同步调用另起包装服务 `mineru-kit file-parse-server`（默认 8003）；主 API Server / Router 不提供 `/v1/file_parse`。
- 解析 API 与 OpenAI 兼容的 VLM server（`mineru-kit vlm-server`）是两个不同接口，地址不可互换。

---

## 典型工作流

### 工作流一：把一批 PDF 变成 RAG 语料（端到端）

输入：`docs/*.pdf`；输出：`out/*.md` + 结构化 JSON + 图片资源。

1. 建环境并验证：`uv venv .mineru --python 3.12` → 激活 → `uv pip install -U "mineru>=4.1,<5"` → `mineru version --json`
2. 先拿一份样本试档位：`mineru-kit parse docs/sample.pdf -o out/sample.md --tier standard`，看公式/表格是否还原
3. 抽样不合格时换档：表格密集的用 `--tier advanced`；只需文本检索的用 `--tier basic` 省算力
4. 批量跑：`mineru-kit parse ./docs -o ./out --format zip`（无状态、默认全页）
5. 检查产物：Markdown 结构、图片是否落在资源目录、页序是否连续
6. 灌进向量库：按页/标题切块后入库（切块策略见 RAG 技能），保留 `source.pdf#page=N` 以便溯源

### 工作流二：对话式读一篇长报告（带定位续读）

输入：一份 200 页 PDF；输出：逐段结论，不重复花算力。

1. `mineru server start` 起本地文档库
2. `mineru parse "report.pdf" --json` ——默认只回前 10 页与定位符
3. 需要第 11 页时 `mineru read "doc:<id>/tier:standard/page:11" --json`
4. 需要上下文时加 `--context 1`；需要看某个图的原始分辨率时 `--format image --output ...`
5. 关键结论回查：`mineru search "..." --min-tier basic --json`

### 工作流三：GPU 容器里跑服务

1. 在有 NVIDIA 驱动的 Linux（或 WSL2）上：`docker build -t mineru:4 -f docker/global/Dockerfile .`
2. 运行时挂载模型缓存目录，避免每次重建下载权重
3. 确认容器内 `MINERU_MODEL_SMALL_BACKEND=torch`、`MINERU_MODEL_VLM_ENGINE=vllm` 生效
4. `curl /v1/health` 与 `/v1/tiers` 确认服务可用与支持的档位
5. 提交解析任务并取结果；非 NVIDIA 设备请按官方说明留在 `mineru<4` 的 legacy 镜像

---

## 最佳实践

1. **按文档类型选档**：原生文本 PDF 用 `flash` 就够；扫描件至少 `basic`；复杂版面/公式表格才上 `standard`/`advanced`
2. **批量用 `mineru-kit`，交互用 `mineru`**：前者无状态全页，后者带缓存与定位续读，混用会浪费算力
3. **先小样再全量**：档位不对时全量重跑很贵
4. **模型目录单独挂卷**：容器里尤其重要，否则每次构建/重建都重新下权重
5. **别把纯文本塞进解析器**：纯文本不解析，直接索引即可
6. **API 与 VLM server 分清**：解析 API 端口不是 OpenAI 兼容端口
7. **保留原始页码**：下游切块时把页码写进元数据，回答才能溯源

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `magic-pdf` 命令找不到或行为不符 | 4.0 换了入口：库式用 `mineru`，无状态用 `mineru-kit`；`magic-pdf` 是 3.x 的 CLI（PyPI 上停在 1.3.12） |
| 报 `quality_tier_unavailable` | 本地文档库发现服务没有 Standard/Basic 能力时的显式拒绝（不会偷偷降到 Flash 或上传官方服务）；装对应模型或显式改用 `flash` |
| 只能解析前 10 页 | `mineru parse` 的设计如此；要整篇用 `--pages all` 或改用 `mineru-kit parse` |
| 显式指定后端就报错 | 显式选择但依赖缺失时框架直接失败，不会静默换后端；按「质量档位与后端」表实现装依赖 |
| 配置改了不生效 | 4.0 读 `$MINERU_HOME/config.yaml`（`MINERU_CONFIG` 可覆盖），不读旧的 `mineru.json`；`--stack`/`MINERU_MODEL_STACK` 已移除 |
| 旧版结果 JSON 读不进来 | 4.0 只严格读当前 schema 的结果；Doclib 缓存里的旧历史由专用 reader 转换，库外旧 JSON 不保证可用——重新解析源文档 |
| 升级 4.1 后 Python 装不上 | 4.1 要求 `>=3.11,<3.15`，不再支持 3.10：用 Python 3.12 新建环境重装，并同步改服务启动配置的解释器路径 |
| 旧客户端调 `/v1/uploads` 或 `/v1/parse/jobs` 返回 404 | 4.1 已删除这两组路由且不保留别名：改走 `POST /v1/tasks` 清单 + `PUT` 上传 + `GET /v1/tasks/{task_id}` 轮询，客户端与服务端一起升级 |
| 调 Doclib 接口报 401/403 | 4.1 起需 Bearer token：CLI 会自动读取，直接集成用 `DoclibClient(base_url=..., token=...)` 或 `Authorization: Bearer <token>`；地址以 `doclib.endpoint.json` 为准 |
| Windows 上 GPU 很慢 | 默认安装走 CPU/llama.cpp；Windows 需要单独装 GPU 版 torch，或直接用 Linux 容器 |
| Docker 构建完推理报没有 GPU | 构建机可以无 GPU，但推理必须有匹配的 NVIDIA 硬件与驱动；非 NVIDIA 设备请用 legacy 镜像 |
| Office/MHTML 解析报档位错误 | 这类格式只走本地 Flash 整篇解析，显式传 `tier="flash"` |

---

## AI 使用建议

- **推荐工作流模式**：先判入口——要交互式/增量阅读走 `mineru`（默认 10 页 + 定位续读）；要批量出文件走 `mineru-kit`；要程序化集成走 `DoclibClient` 或 V1 HTTP API。档位按文档类型定：原生文本 `flash`、扫描件 `basic`、复杂版面 `standard`、极限质量 `advanced`。
- **关键注意事项**：① 4.x 入口与 3.x 完全不同，别混用 `magic-pdf`；② Python `>=3.11,<3.15`（4.1 起移除 3.10）；③ 模型与配置在 `$MINERU_HOME`，旧 `mineru.json` 不读；④ 显式后端缺依赖会直接报错；⑤ 非 NVIDIA Docker 场景留在 3.x。
- **常用代码模式**：批量 = `mineru-kit parse ./docs -o ./out --format zip --tier standard`；增量 = `mineru parse x.pdf --json` → `mineru read "doc:<id>/tier:standard/page:N"`；SDK = `DoclibClient().ensure_parse(ParseRequest(path=..., tier="standard"))` → 轮询 `get_parse` → `read_content(locator)`。
- **不要臆造**：没有 `--backend`/`--stack` 这类 4.0 已移除的参数；没有 `mineru -p input.pdf -o output` 这种 3.x 写法；解析 API 不是 OpenAI 兼容接口。

---

## 相关技能

- **docutranslate** — 文档翻译流水线，可与解析产物对接（先解析再翻译）：[../docutranslate/SKILL.md](../docutranslate/SKILL.md)
- **langchain** — RAG 编排框架，把 MinerU 输出接进切块/向量库链：[../langchain/SKILL.md](../langchain/SKILL.md)
- **llamaindex** — 另一套 RAG 框架，`SimpleDirectoryReader` 风格的数据接入：[../llamaindex/SKILL.md](../llamaindex/SKILL.md)
- **dify** — 低代码 LLM 应用平台，文档知识库上游同样需要可靠解析：[../dify/SKILL.md](../dify/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/opendatalab/MinerU>
- 文档：<https://opendatalab.github.io/MinerU/>
- 质量档位与运行时：<https://opendatalab.github.io/MinerU/usage/tiers/>
- Python SDK / HTTP API：<https://opendatalab.github.io/MinerU/usage/sdk_api/>
- Docker 部署：<https://opendatalab.github.io/MinerU/quick_start/docker_deployment/>
- 3.x → 4.0 迁移：<https://opendatalab.github.io/MinerU/reference/migration_4/>
- 变更历史：<https://opendatalab.github.io/MinerU/reference/changelog/>

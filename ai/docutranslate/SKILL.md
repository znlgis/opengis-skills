---
name: docutranslate
description: Use when translating documents locally via LLM — PDF, Word, Excel, Markdown, SRT subtitles with format preservation. DocuTranslate: LLM-powered multi-format local file translation tool with MCP server support.
tags: [ai, llm, translation, document, pdf, mineru, mcp, python, cli]
---

> **项目地址：** <https://github.com/xunbu/docutranslate>
>
> **PyPI：** <https://pypi.org/project/docutranslate/>
>
> **官方文档：** README（中/英/日/越）｜启动服务后 `http://127.0.0.1:8010/docs`（Swagger UI）
>
> **最新发布：** 参见 [GitHub Releases](https://github.com/xunbu/docutranslate/releases) |
>
> **许可证：** Mozilla Public License 2.0 (MPL-2.0)

## 概述

DocuTranslate 是一款**基于大语言模型（LLM）的本地文件翻译工具**，主打「多格式 + 保留排版 + 可编程集成」。

- **多格式支持**：`pdf`、`docx`、`xlsx`、`md`、`txt`、`json`、`epub`、`srt`、`ass` 等。
- **PDF 智能解析**：接入 [MinerU](https://github.com/opendatalab/MinerU)（在线或本地部署），识别学术论文中的表格、公式、代码。
- **术语表自动生成**：确保专业术语在全文中翻译一致。
- **格式保留**：`docx`/`xlsx` 翻译后保留原始格式（暂不支持旧版 `doc`/`xls`）。
- **多 AI 平台**：兼容 OpenAI 兼容协议的主流平台，支持高并发翻译与自定义提示词。
- **多种使用形态**：开箱即用的 Web UI、RESTful API、Client SDK、MCP Server，以及 Windows/Mac 便携整合包（<40MB）。

> ⚠️ 翻译 `pdf` 时会先转换为 markdown，**会丢失原始版式**。对版式有严格要求者请注意。

> DocuTranslate 迭代很快，命令、字段与参数请以当前版本的 `docutranslate --help`、Web 界面、`http://127.0.0.1:8010/docs` 及仓库最新代码为准。

---

## 环境与安装

### 前置要求

- Python `3.11+`（源码/包安装方式）
- AI 平台的 API Key（OpenAI 兼容协议）
- 翻译 PDF 需 MinerU：在线（[申请 Token](https://mineru.net/apiManage/token)）或本地部署

### 安装方式

```bash
# pip 安装
pip install docutranslate
# 安装 MCP 扩展
pip install "docutranslate[mcp]"

# uv 安装（推荐）
uv init
uv add docutranslate
uv add "docutranslate[mcp]"

# 源码
git clone https://github.com/xunbu/docutranslate.git
cd docutranslate
uv sync --no-dev            # uv sync --no-dev --extra mcp / --all-extras
```

**Docker：**

```bash
docker run -d -p 8010:8010 xunbu/docutranslate:latest
# 请从 GitHub Releases 获取最新标签：https://github.com/xunbu/docutranslate/releases
docker run -it -p 8010:8010 xunbu/docutranslate:latest
```

**便携整合包：** 从 [GitHub Releases](https://github.com/xunbu/docutranslate/releases) 下载 Windows/Mac 整合包，解压后填入 API-Key 即可使用。

---

## Web UI 与 API 服务

```bash
docutranslate -i                       # 启动 GUI（默认仅本机访问）
docutranslate -i --host 0.0.0.0        # 允许局域网其它设备访问
docutranslate -i -p 8081               # 指定端口
docutranslate -i --cors                # 启用默认 CORS
docutranslate -i --with-mcp            # 启动 GUI 并附带 MCP SSE 端点（共享队列/端口）
```

- **交互界面**：`http://127.0.0.1:8010`（或指定端口）
- **API 文档（Swagger UI）**：`http://127.0.0.1:8010/docs`
- **MCP SSE 端点**：`http://127.0.0.1:8010/mcp/sse`（`--with-mcp` 启动时）

---

## Client SDK（推荐入门方式）

`Client` 类提供简单直观的编程接口，自动识别文件类型并选择工作流：

```python
from docutranslate.sdk import Client

client = Client(
    api_key="YOUR_API_KEY",
    base_url="https://api.openai.com/v1/",
    model_id="gpt-4o",
    to_lang="Chinese",
    concurrent=10,          # 并发请求数
)

# 1) 纯文本文件（无需 PDF 解析引擎）
result = client.translate("path/to/document.txt")
print("已保存:", result.save())

# 2) PDF（在线 MinerU，需 token）
result = client.translate(
    "path/to/document.pdf",
    convert_engine="mineru",
    mineru_token="YOUR_MINERU_TOKEN",
    formula_ocr=True,       # 公式识别
)
result.save(fmt="html")

# 3) PDF（本地部署 MinerU，适合内网/离线）
result = client.translate(
    "path/to/document.pdf",
    convert_engine="mineru_deploy",
    mineru_deploy_base_url="http://127.0.0.1:8000",
    mineru_deploy_backend="hybrid-auto-engine",
)
result.save(fmt="markdown")

# 4) Docx（保留格式）
result = client.translate("path/to/document.docx", insert_mode="replace")  # replace/append/prepend
result.save(fmt="docx")

# 5) 导出 base64（便于 API 传输）
b64 = result.export(fmt="html")
```

**异步：** 使用 `client.translate_async()` 支持并行多任务；`result.workflow` 可访问底层工作流做高级操作。

### 常用 `Client` 参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `api_key` / `base_url` / `model_id` | `str` | - | AI 平台凭证与模型 |
| `to_lang` | `str` | - | 目标语言（如 `"Chinese"`、`"English"`） |
| `concurrent` | `int` | `10` | 并发 LLM 请求数 |
| `convert_engine` | `str` | `"mineru"` | PDF 解析引擎：`mineru` / `mineru_deploy` |
| `md2docx_engine` | `str` | `"auto"` | md→docx：`python` / `pandoc` / `auto` / `null` |
| `mineru_token` | `str` | - | 在线 MinerU token |
| `mineru_deploy_base_url` | `str` | - | 本地 MinerU 地址 |
| `skip_translate` | `bool` | `False` | 仅解析、不翻译 |
| `chunk_size` | `int` | `3000` | 送入 LLM 的分块大小 |
| `temperature` | `float` | `0.3` | LLM 温度 |
| `timeout` / `retry` | `int` | `60` / `3` | 超时秒数 / 失败重试次数 |
| `rpm` / `tpm` | `int` | - | 每分钟请求/令牌限速 |

---

## 环境变量

以环境变量方式配置（便于 Docker/MCP/CI）：

| 环境变量 | 说明 | 必填 |
|----------|------|------|
| `DOCUTRANSLATE_API_KEY` | AI 平台 API Key | 是 |
| `DOCUTRANSLATE_BASE_URL` | AI 平台 Base URL | 是 |
| `DOCUTRANSLATE_MODEL_ID` | 模型 ID | 是 |
| `DOCUTRANSLATE_TO_LANG` | 目标语言（默认中文） | 否 |
| `DOCUTRANSLATE_CONCURRENT` | 并发请求数（默认 10） | 否 |
| `DOCUTRANSLATE_CONVERT_ENGINE` | PDF 转换引擎 | 否 |
| `DOCUTRANSLATE_MINERU_TOKEN` | MinerU API Token | 否 |

---

## MCP 集成

DocuTranslate 可作为 MCP（Model Context Protocol）服务器接入 AI 助手：

```bash
docutranslate --mcp                                  # stdio 模式
docutranslate --mcp --transport sse                  # SSE 模式（默认 8000 端口）
docutranslate --mcp --transport sse --mcp-host 127.0.0.1 --mcp-port 8000
docutranslate --mcp --transport streamable-http      # Streamable HTTP 模式
```

**uvx 免安装配置（客户端 `mcpServers`）：**

```json
{
  "mcpServers": {
    "docutranslate": {
      "command": "uvx",
      "args": ["--from", "docutranslate[mcp]", "docutranslate", "--mcp"],
      "env": {
        "DOCUTRANSLATE_API_KEY": "sk-xxxxxx",
        "DOCUTRANSLATE_BASE_URL": "https://api.openai.com/v1",
        "DOCUTRANSLATE_MODEL_ID": "gpt-4o",
        "DOCUTRANSLATE_TO_LANG": "Chinese"
      }
    }
  }
}
```

SSE 模式下客户端配置端点：`http://127.0.0.1:8000/mcp/sse`。

---

## 典型工作流

1. **准备**：安装 DocuTranslate，准备 AI 平台 API Key（PDF 另需 MinerU token 或本地部署）。
2. **选择形态**：普通用户 → Web UI；开发者 → Client SDK / REST API / MCP。
3. **配置模型与解析引擎**：填写 `base_url`/`model_id`；PDF 选择 `mineru`（在线）或 `mineru_deploy`（本地）。
4. **术语一致性**：启用术语表自动生成，或提供自定义术语表与提示词。
5. **翻译并导出**：`result.save(fmt=...)` 输出 `markdown`/`html`/`docx` 等格式。

---

## AI 使用建议

- 生成 SDK 调用代码时，务必带上 `base_url`/`model_id`/`to_lang`；PDF 场景默认 `convert_engine="mineru"` 需要 `mineru_token`。
- 内网/离线场景优先建议 `convert_engine="mineru_deploy"` + 本地 MinerU。
- 对版式敏感的 PDF 应提醒用户「PDF→markdown 会丢失原始版式」。
- 高并发场景配置 `concurrent`/`rpm`/`tpm` 做限速，避免触发平台限流。
- 参数字段以用户当前版本的 `docutranslate --help` 与 `/docs` 为准，避免臆造 API。

---

## 常见问题（FAQ）

| 问题 | 说明 |
|------|------|
| PDF 翻译后版式丢失？ | PDF 会先转 markdown，属预期行为；对版式敏感请用其它格式或本地 MinerU。 |
| 不想暴露到局域网？ | 默认仅本机访问；需要局域网访问才加 `--host 0.0.0.0`。 |
| 支持 `doc`/`xls` 吗？ | 暂不支持旧版二进制格式，仅 `docx`/`xlsx`。 |
| 如何只解析不翻译？ | SDK 传 `skip_translate=True`。 |
| 触发平台限流？ | 降低 `concurrent`，设置 `rpm`/`tpm` 限速。 |

---

## 参考资源

- 项目仓库：<https://github.com/xunbu/docutranslate>
- 中文 README：<https://github.com/xunbu/docutranslate/blob/main/README_ZH.md>
- MCP 文档：<https://github.com/xunbu/docutranslate/blob/main/docutranslate/mcp/README.md>
- MinerU：<https://github.com/opendatalab/MinerU>
- 上游中文教程：<https://znlgis.github.io/ai/docutranslate/>

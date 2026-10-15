---
name: ollama
description: "Use when running local LLMs — pull and manage models, write Modelfiles, call the REST API (generate/chat/embed) with streaming, use the OpenAI-compatible endpoint, or tune context length, GPU offload and keep-alive. Ollama: MIT-licensed local inference runtime for Llama, Qwen, DeepSeek, Gemma, gpt-oss and embedding models."
tags:
  - llm
  - local-inference
  - model-serving
  - rest-api
  - openai-compatible
  - modelfile
  - gguf
  - gpu
  - embeddings
---

> **项目地址：** <https://github.com/ollama/ollama>
>
> **官网：** <https://ollama.com/>
>
> **官方文档：** <https://docs.ollama.com/>（仓库文档目录：<https://github.com/ollama/ollama/tree/main/docs>）
>
> **许可证：** MIT
> **最新版本：** v0.40.4（截至 2026-10 的最新 Release，见 [GitHub Releases](https://github.com/ollama/ollama/releases)）

## 概述

Ollama 是本地运行与管理大语言模型的开源工具，用 Modelfile 把模型权重、提示词模板与运行参数打包成可复用的本地模型。服务默认监听 `127.0.0.1:11434`，自动检测 NVIDIA CUDA、AMD ROCm、Apple Metal、Vulkan 并调度 GPU 加速。除原生 REST API 外还提供 OpenAI 兼容层，现有 OpenAI SDK 代码可基本零改动切换到本地模型。支持文本生成、多模态输入、工具调用、结构化输出与嵌入向量。

- **模型管理**：pull / ls / ps / rm / cp / create，模型库覆盖 Llama、Qwen、DeepSeek、Gemma、gpt-oss 等
- **Modelfile**：FROM / PARAMETER / SYSTEM / TEMPLATE / MESSAGE，定义私有模型
- **REST API**：`/api/generate`、`/api/chat`、`/api/embed`、`/api/tags`、`/api/ps`、`/api/pull` 等，默认 NDJSON 流式
- **OpenAI 兼容**：`/v1/chat/completions`、`/v1/completions`、`/v1/embeddings`、`/v1/models`、`/v1/responses`
- **GPU 加速**：CUDA / ROCm / Metal / Vulkan 自动调度，多卡按显存分摊
- **性能调优**：num_ctx、num_gpu、keep_alive 与一组 `OLLAMA_*` 环境变量

---

## 环境准备

### 方式一：Linux / macOS 一键脚本

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 方式二：Windows（PowerShell）

```powershell
irm https://ollama.com/install.ps1 | iex
```

### 方式三：Docker

```bash
# CPU
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# NVIDIA GPU
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# AMD GPU（ROCm 镜像）
docker run -d --device /dev/kfd --device /dev/dri -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama:rocm

# 在容器内运行模型
docker exec -it ollama ollama run llama3.2
```

模型数据持久化在卷 `ollama`（容器内 `/root/.ollama`）。

### 验证安装

```bash
ollama --version                 # 查看版本
ollama run llama3.2              # 首次运行自动拉取模型并进入对话
curl http://localhost:11434/api/version   # 确认服务已启动
```

`ollama serve --help` 可查看当前版本支持的全部环境变量。

---

## 核心 API/命令

### CLI 常用命令

| 命令 | 说明 |
|------|------|
| `ollama run <model>` | 拉取（如缺失）并交互式运行；支持管道输入与 `"""` 多行输入 |
| `ollama pull <model>` | 下载模型 |
| `ollama ls` | 列出本地模型 |
| `ollama ps` | 列出运行中模型（含到期时间与显存占用） |
| `ollama stop <model>` | 停止运行中模型 |
| `ollama rm <model>` | 删除模型 |
| `ollama cp <src> <dst>` | 复制 / 重命名模型（如 `ollama cp llama3.2 gpt-3.5-turbo` 做别名） |
| `ollama create <name> -f ./Modelfile` | 依据 Modelfile 创建自定义模型 |
| `ollama serve` | 启动服务端 |
| `ollama signin` / `ollama signout` | 登录 / 登出（云模型需要） |

嵌入模型可直接经 CLI 调用：

```bash
ollama run nomic-embed-text "Hello world"   # 输出 JSON 数组
echo "Hello world" | ollama run nomic-embed-text
```

### Modelfile 语法

| 指令 | 说明 |
|------|------|
| `FROM` | 必需。基础模型（如 `FROM llama3.2`）、GGUF 文件或 Safetensors 目录路径 |
| `PARAMETER` | 运行参数：`num_ctx`、`temperature`、`num_predict`、`top_k`、`top_p`、`repeat_penalty`、`repeat_last_n`、`seed`、`stop`、`min_p` 等 |
| `SYSTEM` | 系统提示词，在模板中通过 `{{ .System }}` 注入 |
| `TEMPLATE` | Go 模板语法编写完整提示词模板，变量：`{{ .System }}`、`{{ .Prompt }}`、`{{ .Response }}` |
| `MESSAGE` | 预置对话历史，角色为 `system` / `user` / `assistant` |
| `LICENSE` | 模型许可证文本 |
| `CAPABILITY` | 声明模型能力（可重复出现） |

Modelfile 不区分大小写，指令顺序任意。示例：

```dockerfile
FROM llama3.2
PARAMETER temperature 1
PARAMETER num_ctx 4096
SYSTEM You are Mario from super mario bros, acting as an assistant.
```

自定义对话模板：

```dockerfile
FROM llama3.2
TEMPLATE """{{ if .System }}System: {{ .System }}
{{ end }}User: {{ .Prompt }}
Assistant: {{ .Response }}"""
```

创建与运行：

```bash
ollama create my-model -f ./Modelfile
ollama run my-model
```

### REST API 端点

服务基础地址：`http://localhost:11434`。

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/generate` | POST | 文本补全 |
| `/api/chat` | POST | 多轮对话（支持 `tools`、`think`） |
| `/api/embed` | POST | 生成嵌入向量 |
| `/api/tags` | GET | 列出本地模型 |
| `/api/ps` | GET | 列出运行中模型 |
| `/api/show` | POST | 查看模型信息 |
| `/api/pull` | POST | 拉取模型 |
| `/api/push` | POST | 推送模型 |
| `/api/create` | POST | 创建模型 |
| `/api/copy` | POST | 复制模型 |
| `/api/delete` | DELETE | 删除模型 |
| `/api/version` | GET | 查看版本 |

文本补全：

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

对话（`messages` 支持 `role` 为 `system` / `user` / `assistant` / `tool`，可选 `images` 字段传图片）：

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [
    { "role": "user", "content": "Why is the sky blue?" }
  ],
  "stream": false
}'
```

嵌入（`input` 可为字符串或字符串数组）：

```bash
curl http://localhost:11434/api/embed -d '{
  "model": "nomic-embed-text",
  "input": ["第一段文本", "第二段文本"]
}'
```

要点：

- 响应字段：`response` / `message.content`、`done`、`done_reason`，以及统计字段 `total_duration`、`load_duration`、`prompt_eval_count`、`eval_count`、`eval_duration`；生成速度 = `eval_count / eval_duration * 10^9`（tokens/s）
- `options` 可传运行时参数：`num_ctx`、`num_gpu`、`temperature`、`num_predict`、`top_k`、`top_p`、`stop` 等
- `keep_alive` 控制模型驻留时长，默认 `5m`；`format` 可设 `"json"` 或 JSON Schema 做结构化输出

### 流式响应（NDJSON）

除 `stream: false` 外，端点默认按行返回 JSON 对象（NDJSON）。逐行解析即可实现打字机效果（完整示例见「典型工作流」场景三）：

```python
import json
import requests

resp = requests.post(
    "http://localhost:11434/api/chat",
    json={"model": "llama3.2",
          "messages": [{"role": "user", "content": "你好"}],
          "stream": True},
    stream=True,
)
for line in resp.iter_lines():
    if line:
        print(json.loads(line)["message"]["content"], end="", flush=True)
```

### OpenAI 兼容层

基础地址 `http://localhost:11434/v1/`，`api_key` 任意非空即可（被忽略，惯例填 `ollama`）：

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")
completion = client.chat.completions.create(
    model="gpt-oss:20b",
    messages=[{"role": "user", "content": "Say this is a test"}],
)
print(completion.choices[0].message.content)
```

```bash
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-oss:20b",
       "messages": [{"role": "user", "content": "Say this is a test"}]}'
```

- 支持：`/v1/chat/completions`（流式、JSON 模式、视觉、tools、推理强度控制）、`/v1/completions`、`/v1/models`、`/v1/embeddings`、`/v1/responses`（v0.13.3 起）
- 不支持：`tool_choice`、`logit_bias`、`user`、`n`、图片 URL
- OpenAI 接口无法直接设置 `num_ctx`：需在 Modelfile 写 `PARAMETER num_ctx <大小>` 后用 `ollama create` 生成模型再调用
- 需要 OpenAI 风格模型名时可用别名：`ollama cp llama3.2 gpt-3.5-turbo`

### 性能调优与环境变量

| 环境变量 | 说明 |
|----------|------|
| `OLLAMA_HOST` | 监听地址，默认 `127.0.0.1:11434` |
| `OLLAMA_KEEP_ALIVE` | 模型驻留内存时长，默认 `5m`；负数常驻、`0` 立即卸载 |
| `OLLAMA_MODELS` | 模型存储目录 |
| `OLLAMA_CONTEXT_LENGTH` | 默认上下文长度，默认 4096 tokens |
| `OLLAMA_NUM_PARALLEL` | 每模型并发请求数，默认 1；显存需求按「并发数 × 上下文」增长 |
| `OLLAMA_MAX_LOADED_MODELS` | 同时加载的模型数，默认 3 × GPU 数量（纯 CPU 为 3） |
| `OLLAMA_FLASH_ATTENTION` | 设为 `1` 强制开启 FlashAttention，`0` 关闭 |
| `OLLAMA_KV_CACHE_TYPE` | KV 缓存量化类型，默认 `f16`，可选 `q8_0`、`q4_0` |
| `OLLAMA_ORIGINS` | 允许的浏览器跨域来源 |

设置方式（按平台）：

```bash
# Linux（systemd）
sudo systemctl edit ollama.service
# 在 [Service] 段加入：Environment="OLLAMA_KEEP_ALIVE=30m"
sudo systemctl daemon-reload && sudo systemctl restart ollama

# macOS（launchctl，设置后重启 Ollama 应用）
launchctl setenv OLLAMA_KEEP_ALIVE 30m
```

Windows：退出 Ollama，在系统设置的用户环境变量中新增后从开始菜单重新启动。

请求级参数优先级高于环境变量：

- `keep_alive`：单次请求覆盖驻留时长（原生 API 与 OpenAI 兼容层均支持）
- `options.num_ctx`：单次请求的上下文长度
- `options.num_gpu`：卸载到 GPU 的层数，`0` 为纯 CPU

### GPU 加速说明

- **NVIDIA CUDA**：需计算能力 5.0+ 与驱动 550+；计算能力 5.0–6.2 的显卡需驱动 570+
- **AMD ROCm**：Linux 需 ROCm v7 驱动，Windows 需 ROCm v7 / HIP7；支持 Radeon RX/PRO、Ryzen AI、Instinct
- **Apple Metal**：Apple 芯片默认启用
- **Vulkan**：Windows / Linux 可选启用，`OLLAMA_VULKAN=0` 可关闭
- **多卡调度**：单卡装得下就单卡运行，否则自动分摊到多卡
- **指定设备**：NVIDIA 用 `CUDA_VISIBLE_DEVICES`（建议用 UUID，`-1` 强制 CPU）、AMD 用 `ROCR_VISIBLE_DEVICES`、Vulkan 用 `GGML_VK_VISIBLE_DEVICES`

`ollama ps` 的 PROCESSOR 列可查看实际占用：`100% GPU`、`100% CPU` 或 `48%/52% CPU/GPU` 之类的分摊比例。

---

## 典型工作流

### 场景一：拉起模型并脚本化调用

```bash
ollama pull llama3.2                  # 拉取模型
ollama run llama3.2                   # 交互式对话（退出用 Ctrl+D）
ollama ps                             # 确认加载位置与显存占用
echo "用一句话解释什么是 GIS" | ollama run llama3.2   # 管道脚本化调用
```

### 场景二：定制私有模型

```dockerfile
# ./Modelfile
FROM llama3.2
PARAMETER temperature 0.3
PARAMETER num_ctx 8192
SYSTEM 你是地理信息领域的助手，回答使用简体中文，代码示例优先使用 Python。
```

```bash
ollama create geo-assistant -f ./Modelfile
ollama run geo-assistant
# 修改 Modelfile 后重新执行 create 即可覆盖更新
```

### 场景三：应用接入（REST 流式 + OpenAI SDK）

```python
# 方式一：原生 REST，NDJSON 流式
import json

import requests

resp = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3.2", "prompt": "解释 WGS84 坐标系", "stream": True},
    stream=True,
)
for line in resp.iter_lines():
    if line:
        data = json.loads(line)
        print(data["response"], end="", flush=True)
        if data["done"]:
            print(f"\n完成，共生成 {data['eval_count']} tokens")
```

```python
# 方式二：OpenAI SDK 指向本地服务
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")
stream = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "解释 WGS84 坐标系"}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

### 场景四：本地嵌入与向量化

```bash
ollama pull nomic-embed-text
curl http://localhost:11434/api/embed -d '{
  "model": "nomic-embed-text",
  "input": ["GIS 是地理信息系统", "CAD 是计算机辅助设计"]
}'
```

返回的 `embeddings` 数组可直接写入向量库，配合 Dify 知识库或自建 RAG 流水线使用。

---

## 最佳实践

1. **先确认 GPU 生效**：安装后执行 `ollama ps`，PROCESSOR 列应为 `100% GPU`；若为 `100% CPU`，先排查驱动版本与显存是否满足
2. **上下文按需设置**：默认 4096 tokens，长文档场景再调大 `num_ctx` / `OLLAMA_CONTEXT_LENGTH`，避免无谓显存占用
3. **显存换算**：并发需求约为 `OLLAMA_NUM_PARALLEL × num_ctx`；显存紧张时先降并发再降上下文
4. **KV 缓存量化**：显存不足时可设 `OLLAMA_KV_CACHE_TYPE=q8_0`（目前为全局选项）
5. **keep_alive 分级**：交互场景设 `30m` 以上避免反复加载；批处理收尾设 `0` 立即释放显存
6. **流式优先**：应用侧按 NDJSON 逐行解析，首 token 延迟显著优于等待完整响应
7. **结构化输出**：需要严格 JSON 时用 `format: "json"` 或传 JSON Schema，不要只靠提示词约束
8. **服务暴露需谨慎**：本地 API 无内置鉴权，跨机访问时经反向代理加认证，并用 `OLLAMA_ORIGINS` 收紧跨域
9. **模型目录外置**：服务器上用 `OLLAMA_MODELS` 指向大容量磁盘，避免系统盘写满

---

## 常见问题

| 问题 | 排查与解决 |
|------|-----------|
| `curl` 连接 11434 被拒绝 | 确认 `ollama serve` 在运行、端口未被占用；`ollama --version` 验证安装完整 |
| 推理速度明显偏慢 | `ollama ps` 查看 PROCESSOR 列；核对 NVIDIA 驱动 550+ / AMD ROCm v7；显存不足会退化为 CPU 推理 |
| 显存不足 / out of memory | 降低 `num_ctx`、`OLLAMA_NUM_PARALLEL` 或 `OLLAMA_MAX_LOADED_MODELS`；启用 `OLLAMA_KV_CACHE_TYPE=q8_0`；换更小的量化模型 |
| 回复被截断、上下文不够 | 默认上下文仅 4096 tokens；用 Modelfile `PARAMETER num_ctx`、请求 `options.num_ctx` 或 `OLLAMA_CONTEXT_LENGTH` 调大 |
| 模型每次调用都重新加载 | 驻留时间默认 `5m` 已过期；请求传 `keep_alive` 或设置 `OLLAMA_KEEP_ALIVE`（负数表示常驻） |
| OpenAI SDK 调用报错 | `base_url` 必须带 `/v1/` 后缀；`api_key` 填任意非空值（如 `ollama`）；模型需先 `ollama pull` |
| Docker 容器访问宿主机 Ollama | macOS / Windows 用 `http://host.docker.internal:11434`；Linux 可用 `--network=host` |
| 如何确认模型用了 GPU | `ollama ps` 的 PROCESSOR 列：`100% GPU` / `100% CPU` / 混合分摊比例 |

---

## 参考资源

- 官网与模型库：<https://ollama.com/>、<https://ollama.com/library>
- 文档站：<https://docs.ollama.com/>；API 参考：<https://docs.ollama.com/api>
- 仓库文档目录：<https://github.com/ollama/ollama/tree/main/docs>
- Modelfile 文档：<https://docs.ollama.com/modelfile>
- OpenAI 兼容文档：<https://docs.ollama.com/openai>
- GPU 支持说明：<https://docs.ollama.com/gpu>
- 版本发布：<https://github.com/ollama/ollama/releases>
- 问题排查：<https://docs.ollama.com/troubleshooting>

---

## 相关技能

- [dify](../dify/SKILL.md) — LLM 应用开发平台，可将 Ollama 配置为本地模型供应商
- [docutranslate](../docutranslate/SKILL.md) — 文档翻译工具，可与本地模型配合完成离线翻译
- [hermes-agent](../hermes-agent/SKILL.md) — 自学习通用型 AI 智能体，需要本地推理时可用 Ollama 提供后端
- [opencode](../opencode/SKILL.md) — 终端 AI 编码智能体，支持接入 Ollama 本地模型

---

## AI 使用建议

### 推荐工作流

1. **先验证环境**：`ollama --version` 与 `ollama ps` 确认服务与 GPU 状态后，再写调用代码
2. **模型先拉后用**：任何 API / SDK 调用前先 `ollama pull <model>`，避免运行时才暴露模型缺失
3. **调试用 CLI，集成交付用 API**：交互调试用 `ollama run`，代码集成用 `/api/chat` 或 OpenAI 兼容层
4. **参数改动小步走**：每次只调一个参数（num_ctx / num_gpu / keep_alive），用 `eval_count` 与 `eval_duration` 量化对比
5. **版本敏感**：Ollama 迭代快（当前 v0.40.4），API 字段与 CLI 命令以当前版本的 `--help` 与官方文档为准

### 关键模式与常见陷阱

- **流式解析**：REST 默认 `stream: true`，返回 NDJSON，必须逐行 `json.loads`，不要整体 `resp.json()`
- **`stream: false` 才是单对象**：脚本化非流式场景记得显式关闭，否则会拿到多行数据
- **上下文不在 OpenAI 接口里设**：`num_ctx` 只能经 Modelfile `PARAMETER` 固化到模型，或在原生 API 的 `options` 中传
- **显存与并发是乘法关系**：`OLLAMA_NUM_PARALLEL` 提高吞吐，但显存按「并发 × 上下文」增长，容易 OOM
- **`ollama ps` 是首选诊断工具**：加载位置（GPU/CPU）、显存占用、到期时间一目了然
- **环境变量改动需重启服务**：Linux `systemctl restart ollama`、macOS 重启应用、Windows 重新启动程序后生效

### 如何选择接入方式

| 场景 | 推荐方式 |
|------|---------|
| 快速体验 / 调试提示词 | `ollama run`（CLI） |
| 自有应用集成 | 原生 REST API（`/api/chat`、`/api/embed`） |
| 已有 OpenAI SDK 代码迁移 | OpenAI 兼容层（`/v1/chat/completions`） |
| 固定系统提示词 / 默认参数 | Modelfile + `ollama create` |
| RAG / 语义检索 | `/api/embed` + 向量库 |

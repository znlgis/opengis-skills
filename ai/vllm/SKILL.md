---
name: vllm
description: "Use when self-hosting an OpenAI-compatible LLM endpoint with vLLM 0.32 — vllm serve, offline LLM.generate / llm.chat, PagedAttention with continuous batching and prefix caching, --tensor-parallel-size / --pipeline-parallel-size, AWQ/GPTQ/FP8 quantization, or wiring LangChain/LlamaIndex clients at http://localhost:8000/v1; also when the server OOMs on long context, chat requests ignore your sampling params because generation_config.json overrides them, or engine startup dies compiling kernels."
tags:
  - llm
  - inference
  - serving
  - openai-api
  - gpu
  - quantization
  - python
  - cli
---

> **项目地址：** <https://github.com/vllm-project/vllm>
>
> **官方文档：** <https://docs.vllm.ai/>
>
> **PyPI：** `vllm`（0.32.0，截至 2026-10）
>
> **许可证：** Apache-2.0

## 概述

vLLM 是目前最主流的开源 LLM 推理与服务平台，把"高吞吐、低延迟、OpenAI 兼容"三件事一次做掉。

- **PagedAttention**：KV cache 按页管理，显存碎片少、并发高
- **Continuous batching / chunked prefill / prefix caching**：连续批处理、分块预填充、前缀复用
- **量化**：FP8、MXFP8/MXFP4、NVFP4、INT8、INT4、GPTQ/AWQ、GGUF、compressed-tensors、ModelOpt、TorchAO 等
- **并行**：tensor / pipeline / data / expert / context 并行，支持多机
- **OpenAI 兼容 API**：`/v1/models`、`/v1/completions`、`/v1/chat/completions`，另支持 Anthropic Messages API 与 gRPC
- **模型面广**：200+ Hugging Face 架构（Llama / Qwen / Gemma / Mixtral / DeepSeek-V3 / Qwen-MoE / GPT-OSS / Mamba / 多模态 / embedding / reward）
- **硬件**：NVIDIA、AMD、Intel GPU，x86/ARM/PowerPC CPU，以及 TPU / Gaudi / Ascend 等插件

---

## 环境准备

### 前置条件

| 项 | 要求 |
|----|------|
| 操作系统 | Linux（macOS 需走 vLLM-Metal；Windows 建议 WSL2 + Linux 容器） |
| Python | 3.11 – 3.14 |
| GPU | NVIDIA 需匹配的 CUDA 驱动；AMD 走 ROCm wheel；Intel 走 XPU |
| 磁盘 | 模型权重 + 编译产物，几十 GB 起步 |

### 方式一：uv（官方推荐）

```bash
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install vllm --torch-backend=auto
vllm download-kernels
```

`--torch-backend=auto` 会按驱动版本自动选 PyTorch 源；也可写死 `--torch-backend=cu126`。`vllm download-kernels` 预编译 kernel，避免首次启动在 Hopper 及以上卡上编译几分钟。

### 方式二：pip / conda

```bash
# pip
python -m pip install vllm

# conda
conda create -n vllm python=3.12 -y
conda activate vllm
pip install --upgrade uv
uv pip install vllm --torch-backend=auto
```

### 方式三：不改环境直接试

```bash
uv run --with vllm vllm --help
```

### 其他硬件

```bash
# AMD ROCm（支持 Python 3.12、ROCm 7.0、glibc >= 2.35）
uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/

# Google TPU
uv pip install vllm-tpu
```

Apple Silicon 用 [vLLM-Metal](https://github.com/vllm-project/vllm-metal)；Ascend NPU 用 [vllm-ascend](https://github.com/vllm-project/vllm-ascend)。

### 验证

```bash
vllm --version
vllm serve --help | head -30
```

---

## 离线批量推理

```python
from vllm import LLM, SamplingParams

prompts = [
    "Hello, my name is",
    "The president of the United States is",
    "The capital of France is",
    "The future of AI is",
]
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

llm = LLM(model="facebook/opt-125m")
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt!r}")
    print(f"Generated: {output.outputs[0].text!r}")
```

要点：

- `llm.generate` **不会**自动套 chat template；Instruct/Chat 模型要自己 `tokenizer.apply_chat_template(...)`，或直接用 `llm.chat(messages_list, sampling_params)`
- 默认从 Hugging Face 拉模型；用 ModelScope 时设 `export VLLM_USE_MODELSCOPE=True`
- 输出是 `RequestOutput` 列表，含 prompt、生成 token 与统计信息

---

## OpenAI 兼容服务

```bash
vllm serve Qwen/Qwen2.5-1.5B-Instruct
# 默认 http://localhost:8000，一个服务一个模型
```

```bash
# 列出模型
curl http://localhost:8000/v1/models

# completions
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen2.5-1.5B-Instruct","prompt":"San Francisco is a","max_tokens":7,"temperature":0}'

# chat completions
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen2.5-1.5B-Instruct","messages":[{"role":"user","content":"用一句话解释 PagedAttention"}]}'
```

常用开关：

| 开关 | 作用 |
|------|------|
| `--host` / `--port` | 监听地址与端口（默认 8000） |
| `--api-key`（或 `VLLM_API_KEY`） | 开启鉴权；可传多个 key 做轮换 |
| `--generation-config vllm` | **忽略**模型仓库里的 `generation_config.json`，用自己的采样默认值 |
| `--tensor-parallel-size N` | 张量并行，单机 N 卡 |
| `--pipeline-parallel-size N` | 流水线并行，配合 TP 做多机 |
| `--max-model-len` | 限制上下文长度（OOM 时最常调的就是它） |
| `--gpu-memory-utilization` | KV cache 可用显存比例 |
| `--quantization` | 指定量化后端（如 `auto_awq`） |
| `--max-num-seqs` | 并发序列上限 |
| `--enforce-eager` | 关 CUDA graph（排查崩溃/省显存时用） |

> 默认会应用模型自带的 `generation_config.json`，你的 temperature/max_tokens 可能被模型推荐值覆盖；需要可控就加 `--generation-config vllm`。

---

## 并行与量化

### 张量并行 / 流水线并行

```bash
# 单机 4 卡
vllm serve meta-llama/Llama-3.1-8B-Instruct --tensor-parallel-size 4

# 8 卡：4 路张量并行 × 2 路流水线并行
vllm serve <model> --tensor-parallel-size 4 --pipeline-parallel-size 2
```

### 量化

```bash
# AutoAWQ 量化权重
vllm serve TheBloke/Llama-2-7B-AWQ --quantization auto_awq
```

支持的量化路径包括 AutoAWQ、GPTQModel、FP8 W8A8（llm-compressor）、bitsandbytes 等；具体模型与硬件的组合以[量化文档](https://docs.vllm.ai/en/latest/features/quantization/index.html)为准。未指定时 vLLM 会从权重 metadata 自动识别。

---

## 与 LangChain / LlamaIndex 接入

vLLM 实现的是 OpenAI 协议，所以两边的接入方式统一是"把 base_url 指向 vLLM"。

```python
from openai import OpenAI

client = OpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1")
resp = client.chat.completions.create(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    messages=[{"role": "user", "content": "hello"}],
)
print(resp.choices[0].message.content)
```

```python
# LangChain：用 OpenAI 兼容客户端，不换 provider 类
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
)
print(llm.invoke("用一句话解释 continuous batching").content)
```

```python
# LlamaIndex：OpenAILike 走自定义 base_url
from llama_index.llms.openai_like import OpenAILike

llm = OpenAILike(
    model="Qwen/Qwen2.5-1.5B-Instruct",
    api_base="http://localhost:8000/v1",
    api_key="EMPTY",
    is_chat_model=True,
)
print(llm.complete("用一句话解释 PagedAttention"))
```

> 只要服务端是 OpenAI 兼容的，就不需要 vLLM 专属客户端；把 `base_url`/`api_base` 指过去即可。反过来，vLLM 的离线 `LLM` 类不能跨进程给别的框架用。

---

## 典型工作流

### 工作流一：把本地模型变成团队可用的 API（端到端）

输入：一张 NVIDIA 卡 + 一个 HF 模型；输出：`http://<host>:8000/v1` 可用的 OpenAI 端点。

1. 建环境：`uv venv --python 3.12 --seed` → 激活 → `uv pip install vllm --torch-backend=auto` → `vllm download-kernels`
2. 先跑最小模型确认链路：`vllm serve facebook/opt-125m`
3. `curl http://localhost:8000/v1/models` 确认服务活着
4. 换目标模型并调参：`vllm serve <model> --max-model-len 8192 --gpu-memory-utilization 0.90 --max-num-seqs 64`
5. 多卡：加 `--tensor-parallel-size <卡数>`；显存不够先降 `--max-model-len` 与 `--max-num-seqs`
6. 加鉴权：`--api-key $KEY`（或 `VLLM_API_KEY`），客户端改用该 key
7. 压测与观测：盯吞吐/延迟/GPU 利用率，按需开 prefix caching（默认已启用）

### 工作流二：批量离线打分/生成（不用起服务）

输入：一份 prompt 列表；输出：结构化结果文件。

```python
import json
from vllm import LLM, SamplingParams

prompts = [line.strip() for line in open("prompts.txt", encoding="utf-8") if line.strip()]
llm = LLM(model="Qwen/Qwen2.5-1.5B-Instruct", max_model_len=4096, tensor_parallel_size=1)
outs = llm.generate(prompts, SamplingParams(temperature=0, max_tokens=256))

with open("results.jsonl", "w", encoding="utf-8") as f:
    for p, o in zip(prompts, outs):
        f.write(json.dumps({"prompt": p, "text": o.outputs[0].text}, ensure_ascii=False) + "\n")
```

离线批处理省掉 HTTP 与网络开销，适合跑评测集、批量标注、离线合成数据。

### 工作流三：容器化部署

1. 用官方镜像 `vllm/vllm-openai:<tag>`（ROCm 版为 `vllm/vllm-openai-rocm`，XPU 版自 v0.26.0 起有官方镜像）
2. 挂载 HF 缓存目录避免每次重下权重
3. 对外只暴露网关端口，鉴权与限流放前面
4. 健康检查打 `/health`（或 `/v1/models`），确认模型已加载再放流量

---

## 性能与显存

1. **先压 `--max-model-len`**：长上下文是显存第一杀手；按真实需求设，不要照抄模型上限
2. **`--gpu-memory-utilization` 留余量**：0.85–0.92 之间找平衡，太高会在长请求时 OOM
3. **prefix caching**：多轮/多请求共享前缀（如固定 system prompt）时收益最大
4. **chunked prefill**：长 prompt 与解码请求混跑时平滑延迟
5. **量化**：显存换精度；AWQ/GPTQ 权重最省事，FP8 需要 Hopper 以上更合适
6. **`vllm download-kernels`**：省掉启动期编译，CI 里尤其值得
7. **别在容器里 pip 装一半**：镜像已带匹配的 torch/CUDA，自己再装容易版本打架

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 启动就 OOM（`CUDA out of memory`） | 降 `--max-model-len`、`--max-num-seqs`、`--gpu-memory-utilization`；或改量化权重/多卡 TP |
| 客户端传的 temperature/max_tokens 没生效 | 服务端默认套用了模型仓库的 `generation_config.json`；加 `--generation-config vllm` |
| 首次启动卡在编译 kernel 几分钟 | 预跑 `vllm download-kernels`；或先用小模型验证链路 |
| `pip install vllm` 后跑不起来 | 平台/驱动不匹配（Linux + 匹配 CUDA）；改 `--torch-backend=cuXXX` 或用官方镜像 |
| 显存够但吞吐上不去 | 看是否被 `--max-num-seqs` 限制；确认 continuous batching 生效（默认开）；检查是否开了 `--enforce-eager` |
| 多卡起不来 | TP 数必须整除注意力头数/模型分片；先试 `--tensor-parallel-size 1` 排除模型问题 |
| 服务被外部扫到 | 默认无鉴权；生产必须 `--api-key`（可多个轮换）+ 反代/网关 + 网络隔离 |
| Windows/macOS 装不上 | Windows 建议 WSL2 跑 Linux 容器；macOS 用 vLLM-Metal |
| 想跑 GGUF 权重 | 支持，但走 GGUF 路径的性能与特性（如 prefix caching）不同于原生权重，先小规模验证 |

---

## AI 使用建议

- **推荐工作流模式**：要 API 就 `vllm serve <model>`（必要时加 TP/量化/鉴权）；要批量跑数据就用离线 `LLM`；要接框架就统一走 OpenAI 兼容 base_url。调优顺序固定为：先 `--max-model-len` → 再 `--gpu-memory-utilization` → 再 `--max-num-seqs` → 最后才是量化。
- **关键注意事项**：① vLLM 只服务 Linux/匹配 GPU 栈，Windows 走容器；② `llm.generate` 不套 chat template，Chat 模型要么手动套要么用 `llm.chat`；③ 默认应用 `generation_config.json`；④ 默认无鉴权；⑤ 一个服务一个模型。
- **常用代码模式**：服务 = `vllm serve <model> --tensor-parallel-size 4 --max-model-len 8192`；离线 = `LLM(model=...)` + `SamplingParams(...)` + `llm.generate(prompts, sp)`；客户端 = `OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")`。
- **不要臆造**：没有 `vllm serve --model-id` 这种参数；不要在 Python 里 `from vllm.entrypoints import LLM`（顶层是 `from vllm import LLM`）；Anthropic Messages API 与 gRPC 是额外入口，但客户端主路径仍是 OpenAI 协议。

---

## 相关技能

- **ollama** — 本地单机跑模型的轻量方案，适合开发期替代（生产吞吐不够时换 vLLM）：[../ollama/SKILL.md](../ollama/SKILL.md)
- **huggingface-transformers** — 直接用 transformers 推理，对照理解 KV cache/批处理差异：[../huggingface-transformers/SKILL.md](../huggingface-transformers/SKILL.md)
- **langchain** — 把 vLLM 的 OpenAI 端点接进链与 Agent：[../langchain/SKILL.md](../langchain/SKILL.md)
- **llamaindex** — RAG 框架侧接入同一端点：[../llamaindex/SKILL.md](../llamaindex/SKILL.md)
- **mineru** — 解析产物进 RAG 的上游环节：[../mineru/SKILL.md](../mineru/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/vllm-project/vllm>
- 文档：<https://docs.vllm.ai/>
- 快速开始：<https://docs.vllm.ai/en/latest/getting_started/quickstart.html>
- 并行与扩缩：<https://docs.vllm.ai/en/latest/serving/parallelism_scaling.html>
- 量化：<https://docs.vllm.ai/en/latest/features/quantization/index.html>
- 支持的模型：<https://docs.vllm.ai/en/latest/models/supported_models.html>
- Docker Hub：<https://hub.docker.com/r/vllm/vllm-openai>

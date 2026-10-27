---
name: huggingface-transformers
description: "Use when running or fine-tuning Hugging Face Transformers models in Python — pipeline() inference, AutoModel/AutoTokenizer from_pretrained, device_map + dtype memory management, Trainer fine-tuning, BGE embeddings for Chinese RAG; also for CUDA out of memory on load, transformers 5.21 `Requires-Python >=3.11`, `pipeline("summarization")` removed in v5, and ImportError after upgrading. transformers 5.21.0 + PyTorch."
tags:
  - transformers
  - huggingface
  - pytorch
  - llm
  - nlp
  - fine-tuning
  - inference
  - embeddings
  - model-hub
---

> **项目地址：** <https://github.com/huggingface/transformers>
>
> **官方文档：** <https://huggingface.co/docs/transformers/>
>
> **许可证：** Apache-2.0
>
> **最新版本：** v5.21.0（PyPI 与 `releases/latest` 双核实，截至 2026-10；5.21.0 上传于 2026-10-26）

## 概述

Transformers 是 Hugging Face 开源的模型定义框架，为文本、视觉、音频与多模态模型提供统一的推理与训练接口。它把「配置、模型、预处理器」抽象为三类基类，并只用 `pipeline` 与 `Trainer` 两个 API 覆盖推理与微调两条主线。模型权重托管在 Hugging Face Hub，`from_pretrained()` 可按名称或路径自动下载并缓存。

- **AutoClass**：`AutoModel` / `AutoTokenizer` / `AutoModelForCausalLM` / `AutoModelForSequenceClassification` / `AutoModelForSeq2SeqLM` 等按任务自动推断架构
- **pipeline()**：任务级推理封装，一行完成预处理、前向与后处理
- **Trainer**：PyTorch 训练/评估循环，配合 `TrainingArguments` 配置超参
- **显存管理**：`device_map="auto"`、`dtype="auto"`、`BitsAndBytesConfig` 量化
- **生态**：`datasets`、`evaluate`、`accelerate`、`huggingface_hub`、`safetensors` 协同工作

Transformers 是库（进程内推理/训练），与 Ollama 这类独立推理服务定位不同，详见「最佳实践」。

---

## 环境准备

要求 Python **>= 3.11**（5.21.0 起，实测 `requires_python`；5.19–5.20 仍为 >= 3.10）。

```bash
# 核心：Transformers 与 PyTorch
pip install -U transformers torch

# 常用配套：数据集、评估指标、多设备调度
pip install -U datasets evaluate accelerate
```

可选 GPU 加速：

```bash
# NVIDIA CUDA（按显卡驱动选择 cu 版本，示例）
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

量化推理（8bit/4bit）需额外安装：

```bash
pip install -U bitsandbytes
```

验证安装：

```bash
python -X utf8 -c "import torch, transformers; print(transformers.__version__, torch.__version__, torch.cuda.is_available())"
```

登录 Hub（拉取受限模型或推送模型时需要，Token 从账号设置生成）：

```bash
hf auth login
```

---

## 核心 API/命令

### pipeline() 快速推理

`pipeline(task, model=..., device=..., dtype=...)` 返回任务流水线；不传 `model` 时使用该任务的默认模型。

```python
from transformers import pipeline

# 文本分类（情感分析别名 sentiment-analysis）
clf = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
clf("This restaurant is awesome")
# [{'label': 'POSITIVE', 'score': 0.9998...}]

# 文本生成
gen = pipeline("text-generation", model="openai-community/gpt2")
gen("the secret to baking a good cake is", max_new_tokens=40, return_full_text=False)

# 特征抽取（嵌入）
feat = pipeline("feature-extraction", model="BAAI/bge-large-zh-v1.5")
feat("地理信息系统")
```

`device` 与 `device_map` 互斥，不可同时传：

| 参数 | 说明 |
|------|------|
| `device` | `0`/`1` 指定 GPU 序号，`"cpu"`、`"mps"`（Apple）、`-1` 强制 CPU；不传时自动选首个可用加速器 |
| `device_map="auto"` | 交由 Accelerate 分配权重到最快设备，需安装 `accelerate` |
| `dtype` | 默认 `"auto"`（按权重保存精度加载），可显式传 `torch.float16` / `torch.bfloat16`（v5 参数名，旧版为 `torch_dtype`） |
| `batch_size` | 批推理大小，默认 1；延迟敏感或纯 CPU 场景不建议开启 |
| `torch_dtype` 兼容 | v5 统一为 `dtype`，旧脚本里的 `torch_dtype` 建议迁移 |

常见任务标识：`text-classification`（别名 `sentiment-analysis`）、`text-generation`、`feature-extraction`、`fill-mask`、`token-classification`（别名 `ner`）、`zero-shot-classification`、`automatic-speech-recognition`、`image-classification`、`image-text-to-text` 等。

### AutoModel / AutoTokenizer 加载

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf", dtype="auto", device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

inputs = tokenizer(["The secret to baking a good cake is "], return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=30)
print(tokenizer.batch_decode(outputs, skip_special_tokens=True)[0])
```

任务头模型：`AutoModelForSequenceClassification`（分类）、`AutoModelForCausalLM`（自回归生成）、`AutoModelForSeq2SeqLM`（序列到序列）、`AutoModel`（仅隐藏态，用于嵌入）。

### tokenizer 用法

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("google-t5/t5-small")

# 单条 / 批量：padding 补齐、truncation 截断、return_tensors 输出张量
enc = tokenizer("summarize: 这是一段需要摘要的长文本", return_tensors="pt")
batch = tokenizer(["句子一", "句子二"], padding=True, truncation=True, max_length=128)

# 标签编码（seq2seq 训练用 text_target）
labels = tokenizer(text_target="简短摘要", max_length=64, truncation=True)

print(enc["input_ids"].shape)
print(tokenizer.decode(enc["input_ids"][0], skip_special_tokens=True))
```

### Trainer 微调

```python
from datasets import load_dataset
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    DataCollatorWithPadding, Trainer, TrainingArguments,
)

model = AutoModelForSequenceClassification.from_pretrained("distilbert/distilbert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
dataset = load_dataset("cornell-movie-review-data/rotten_tomatoes")

dataset = dataset.map(lambda ex: tokenizer(ex["text"], truncation=True), batched=True)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

args = TrainingArguments(
    output_dir="distilbert-rotten-tomatoes",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    num_train_epochs=2,
    eval_strategy="epoch",
)
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    processing_class=tokenizer,
    data_collator=data_collator,
)
trainer.train()
trainer.push_to_hub()   # 需先 hf auth login
```

序列到序列任务（摘要/翻译）用 `Seq2SeqTrainer` + `Seq2SeqTrainingArguments`，并设 `predict_with_generate=True`。

### 显存与精度管理

```python
import torch
from transformers import BitsAndBytesConfig, pipeline

# 半精度 + 自动分配
pipe = pipeline("text-generation", model="google/gemma-2-2b", dtype=torch.bfloat16, device_map="auto")

# 8bit 量化
pipe = pipeline(
    "text-generation", model="google/gemma-7b", device_map="auto",
    model_kwargs={"quantization_config": BitsAndBytesConfig(load_in_8bit=True)},
)
```

### v5 任务变更（重要）

v5 移除了以下 `pipeline` 任务，调用会提示改用 `text-generation` 搭配对话模型：`summarization`、`translation`、`question-answering`、`text2text-generation`。摘要/翻译场景优先使用指令对话模型经 `text-generation` 完成，或对 T5/BART 等 seq2seq 模型直接用 `model.generate()`。

---

## 典型工作流

### 场景一：文本分类（批量 + GPU）

```python
from accelerate import Accelerator
from datasets import load_dataset
from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset

device = Accelerator().device
clf = pipeline("text-classification", device=device)

# 直接传列表
print(clf(["This movie is great", "This movie is awful"]))

# 流式处理大数据集，避免一次性载入内存
ds = load_dataset("stanfordnlp/imdb", name="plain_text", split="unsupervised")
for out in clf(KeyDataset(ds, "text"), batch_size=8, truncation="only_first"):
    print(out)
```

### 场景二：文本生成

```python
from transformers import pipeline

gen = pipeline("text-generation", model="google/gemma-2-2b", device_map="auto")
out = gen(
    "用一句话解释什么是地理信息系统：",
    max_new_tokens=128,
    do_sample=True,
    temperature=0.7,
    num_return_sequences=1,
)
print(out[0]["generated_text"])
```

### 场景三：摘要（v5 推荐路径）

```python
# 方式一：seq2seq 模型直接 generate
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

name = "google-t5/t5-small"
tok = AutoTokenizer.from_pretrained(name)
mdl = AutoModelForSeq2SeqLM.from_pretrained(name)
ids = tok("summarize: 长文本内容……", return_tensors="pt").input_ids
out = mdl.generate(ids, max_new_tokens=100, do_sample=False)
print(tok.decode(out[0], skip_special_tokens=True))

# 方式二：指令对话模型 + text-generation（v5 对 summarization 任务的替代方案）
from transformers import pipeline

gen = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct", device_map="auto")
print(gen("请用两句话总结下面内容：……", max_new_tokens=200)[0]["generated_text"])
```

### 场景四：中文嵌入 + RAG

```python
from transformers import AutoModel, AutoTokenizer
import torch

name = "BAAI/bge-large-zh-v1.5"
tok = AutoTokenizer.from_pretrained(name)
mdl = AutoModel.from_pretrained(name, device_map="auto")

def embed(texts):
    # BGE 检索场景：查询句加指令前缀，段落不加
    batch = tok(texts, padding=True, truncation=True, max_length=512, return_tensors="pt").to(mdl.device)
    with torch.no_grad():
        out = mdl(**batch)
    return torch.nn.functional.normalize(out.last_hidden_state[:, 0], dim=-1)  # CLS 向量

query = "为这个句子生成表示以用于检索相关文章：什么是坐标系"
doc_vectors = embed(["WGS84 是地理坐标系统", "CAD 是计算机辅助设计"])
q_vector = embed([query])
print((q_vector @ doc_vectors.T).softmax(dim=-1))
```

向量写入 FAISS/Milvus 等向量库后即可搭建检索增强问答，可与 Dify 知识库或 LangChain 检索器对接。

---

## 最佳实践

1. **优先 `dtype="auto"` + `device_map="auto"`**：避免 PyTorch 默认以 float32 二次加载权重造成显存翻倍
2. **大模型走量化**：显存不足时用 `BitsAndBytesConfig`（8bit/4bit），比换更小模型改动更小
3. **批推理看场景**：GPU 且序列长度规整时才开 `batch_size`；延迟敏感或纯 CPU 关闭
4. **流式处理大数据集**：用 `KeyDataset` 或生成器迭代，不要先 `list()` 载入全部数据
5. **显存不足的排查顺序**：降 `batch_size` → 降 `max_length`/`max_new_tokens` → 开半精度 → 量化
6. **微调先小步**：`learning_rate` 从 2e-5 起，先跑 1 epoch 验证流程再放大
7. **离线/内网环境**：设 `HF_HOME` 指定缓存目录，或 `HF_HUB_OFFLINE=1` 使用本地缓存
8. **固定版本**：生产环境锁定 `transformers` 与 `torch` 版本，v5 有破坏性变更（如任务移除、`dtype` 参数）
9. **与 Ollama 的定位差异**：Transformers 是 Python 库，进程内加载权重、可训练、可自定义前向；Ollama 是独立服务，专注 GGUF 量化模型的开箱即用推理与 API。需要微调、自定义算子或非 LLM 任务（分类/嵌入/ASR）选 Transformers；只需跑现成 LLM 且要 HTTP API 选 Ollama

---

## 常见问题

| 问题 | 排查与解决 |
|------|-----------|
| `ImportError: cannot import name ...` | 版本不匹配，先 `pip install -U transformers`；5.21+ 需 Python >= 3.11 |
| `pip install transformers` 报 `Requires-Python >=3.11` | 5.21.0 起最低 Python 3.11；要么升级解释器，要么钉 `transformers==5.20.x`（仍支持 3.10） |
| 从 4.x 升到 5.x 后 TF/JAX 代码报错 | v5 移除 TensorFlow 与 JAX 后端，只保留 PyTorch；相关代码需迁移到 torch 或留在 4.x |
| 模型下载慢或超时 | 设镜像端点 `export HF_ENDPOINT=https://hf-mirror.com`，或 `hf auth login` 后用官方源；检查 `HF_HOME` 磁盘空间 |
| CUDA out of memory | 用 `device_map="auto"` + `dtype="auto"`；降 `batch_size`；开 `BitsAndBytesConfig` 量化；`torch.cuda.empty_cache()` |
| 明明有 GPU 却跑在 CPU | 检查 `torch.cuda.is_available()`；CUDA 版 torch 未装或驱动不匹配，按官网 index-url 重装 |
| `pipeline("summarization")` 报任务已移除 | v5 已移除该任务，改用 `text-generation` 对话模型或对 seq2seq 模型直接 `model.generate()` |
| `device` 与 `device_map` 同时传报错 | 两者互斥，只保留其一；单卡用 `device=0`，多卡/大模型用 `device_map="auto"` |
| 生成结果被截断 | `max_new_tokens` 太小或超 `model_max_length`；调大生成长度并检查 tokenizer 的 `max_length` |
| `trust_remote_code` 相关报错 | 部分模型需 `trust_remote_code=True` 加载自定义代码，确认来源可信后再开启 |
| Tokenizer 报 `text_target` 未知 | 该参数用于 seq2seq 标签编码，普通编码直接传位置参数或用 `padding`/`truncation` |

---

## AI 使用建议

### 推荐工作流

1. **先验证环境**：`python -c "import torch, transformers; print(transformers.__version__)"` 确认版本与 CUDA 可用性再写代码
2. **推理优先用 pipeline**：单任务快速验证用 `pipeline()`，需要细粒度控制（自定义采样、嵌入归一化）时改用 `AutoModel` + tokenizer
3. **加载参数成对给**：大模型一律 `from_pretrained(..., dtype="auto", device_map="auto")`，避免显存翻倍与手动 `.to()`
4. **微调用 Trainer 骨架**：`model + tokenizer + dataset + data_collator + TrainingArguments`，先跑通再调超参
5. **版本敏感**：v5 有破坏性变更（任务移除、`dtype` 取代 `torch_dtype`），以当前版本官方文档为准

### 关键模式与常见陷阱

- **`device` 与 `device_map` 互斥**：不要同时传，否则报错
- **`return_full_text`**：文本生成默认回传含提示词的完整文本，只要生成部分时设为 `False`
- **嵌入取向量**：BGE 等模型取 `last_hidden_state[:, 0]`（CLS）并做 L2 归一化，检索时查询句需加指令前缀
- **任务名随版本变**：`summarization` 等在 v5 已移除，硬编码旧任务名会失败
- **精度与显存**：`dtype="auto"` 是显存优化的第一手段，量化是第二手段，换模型是最后手段
- **离线环境**：先在有网机器预下载到 `HF_HOME` 缓存，再设 `HF_HUB_OFFLINE=1` 复用

## 相关技能

- [ollama](../ollama/SKILL.md) — 本地推理服务，适合开箱即用跑 GGUF LLM；Transformers 侧重进程内推理与微调
- [langchain](../langchain/SKILL.md) — LLM 应用编排框架，可直接封装 Transformers 模型与 HuggingFaceEmbeddings
- [dify](../dify/SKILL.md) — LLM 应用平台，可接入 Transformers 嵌入模型构建 RAG 知识库
- [docutranslate](../docutranslate/SKILL.md) — 文档翻译工具，可配合本地 Transformers 模型做离线翻译

---

## 参考资源

- 官方文档：<https://huggingface.co/docs/transformers/>
- 快速上手：<https://huggingface.co/docs/transformers/quicktour>
- Pipeline 指南：<https://huggingface.co/docs/transformers/main_classes/pipelines>
- 训练与 Trainer：<https://huggingface.co/docs/transformers/main_classes/trainer>
- 模型与数据集 Hub：<https://huggingface.co/models>、<https://huggingface.co/datasets>
- 中文嵌入模型：<https://huggingface.co/BAAI/bge-large-zh-v1.5>
- 版本发布：<https://github.com/huggingface/transformers/releases>
- PyPI：<https://pypi.org/project/transformers/>

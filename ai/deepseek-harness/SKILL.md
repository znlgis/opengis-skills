---
name: deepseek-harness
description: "Use when building AI agent applications with a plugin-based architecture — Web UI, CLI, Python SDK, Cordis plugin system, multi-model orchestration. DeepSeek Harness (dsh): open-source agent harness by DeepSeek AI where everything is a plugin, powered by Cordis for spatiotemporal composability."
tags:
  - ai
  - agent
  - deepseek
  - plugin
  - cordis
  - typescript
  - python
  - llm
  - harness
  - web-ui
---

> **项目地址：** <https://github.com/deepseek-ai/deepseek-harness>
>
> **官方文档：** 见仓库 README 及 docs/ 目录
>
> **许可证：** MIT

## 概述

DeepSeek Harness（简称 `dsh`）是 DeepSeek AI 开源的 **智能体框架**，采用"一切皆插件"的架构理念，由 Cordis 引擎驱动。支持 Web UI、CLI、Python SDK 三种使用方式，以及 Cordis 插件范式的扩展开发。

### 核心特性

| 特性 | 说明 |
|------|------|
| 插件架构 | 基于 Cordis，一切功能以插件形式提供 |
| 多接入方式 | Web UI / CLI / Python SDK / ACP JSON-RPC |
| 多模型支持 | 灵活的模型供应商配置体系 |
| Profile/Bundle | CLI 下的配置 Profile 和 Bundle 管理 |
| Session 管理 | 完整的会话日志与 Agent 循环 |
| 开发者友好 | TypeScript + Python 双语言 SDK |

---

## 环境准备

### 安装（npm）

```bash
# 需要 Node.js
npx @deepseek-ai/dsh web
# 默认启动 Web UI: http://127.0.0.1:3080
```

### 从源码安装

```bash
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

### 前置条件

- Node.js 18+（npm 方式）
- pnpm（从源码构建）
- DeepSeek API Key 或其他兼容模型的 API Key

---

## 核心 API

### Web UI 启动

```bash
# 默认端口 3080
npx @deepseek-ai/dsh web

# 自定义端口
npx @deepseek-ai/dsh web --port 8080
```

### CLI 使用

```bash
# 基础对话
npx @deepseek-ai/dsh chat

# 使用指定 Profile
npx @deepseek-ai/dsh chat --profile my-profile

# 使用 Bundle（预设配置包）
npx @deepseek-ai/dsh chat --bundle my-bundle
```

### Python SDK

```python
from deepseek_harness import Harness

# 初始化
harness = Harness(model="deepseek-chat")

# 对话
response = harness.chat("Hello, how can you help me?")

# 带工具调用
response = harness.chat(
    "Analyze this data",
    tools=["code_interpreter", "web_search"]
)
```

### ACP JSON-RPC 自动化

```python
import jsonrpc

# 通过 JSON-RPC 协议接入
client = jsonrpc.Client("http://127.0.0.1:3080/rpc")
result = client.call("chat.completions", {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}]
})
```

---

## 典型工作流

### 1. 快速启动对话

```bash
# 安装并启动
npx @deepseek-ai/dsh web

# 在浏览器中打开 http://127.0.0.1:3080
# 配置 API Key → 开始对话
```

### 2. 配置多模型

```yaml
# config.yaml 示例
models:
  deepseek-chat:
    provider: deepseek
    api_key: ${DEEPSEEK_API_KEY}
    model: deepseek-chat
  
  deepseek-reasoner:
    provider: deepseek
    api_key: ${DEEPSEEK_API_KEY}
    model: deepseek-reasoner
```

### 3. 开发 Cordis 插件

```typescript
// my-plugin.ts
import { Plugin } from '@deepseek-ai/dsh';

export class MyToolPlugin extends Plugin {
  name = 'my-tool';
  
  tools = [
    {
      name: 'my_custom_tool',
      description: 'A custom tool for specific tasks',
      handler: async (params) => {
        // 实现工具逻辑
        return { result: 'done' };
      }
    }
  ];
}
```

---

## Cordis 插件体系

Cordis 是 DeepSeek Harness 的核心引擎，提供了 **时空可组合性**（Spatiotemporal Composability）的编程范式：

- **Service**：提供能力（如 LLM 调用、文件操作）
- **Component**：组合 Service 的功能单元
- **Plugin**：打包 Component 的可分发单元

### 插件发现与注册

```bash
# 在 GitHub 仓库上添加 dsh-plugin topic 可被发现
# 插件仓库示例
gh repo create my-dsh-plugin --public
gh repo edit my-dsh-plugin --add-topic dsh-plugin
```

---

## 最佳实践

1. **开发者预览阶段**：当前为 Developer Preview，API 可能有 Breaking Changes
2. **插件化设计**：优先通过插件扩展功能，而非修改核心代码
3. **Profile 管理**：为不同使用场景创建不同 Profile（开发/生产/测试）
4. **模型选择**：根据任务复杂度选择 `deepseek-chat`（快速）或 `deepseek-reasoner`（推理）

---

$h$faq`

| 问题 | 解决方案 |
|------|---------|
| `dsh web` 启动后页面空白？ | 确认 Node.js 版本 ≥ 18，清除缓存后重试 |
| 如何配置代理？ | 在环境变量中设置 `HTTP_PROXY` / `HTTPS_PROXY` |
| 插件如何调试？ | 使用 `pnpm dsh web --debug` 启用调试模式 |
| 与 OpenCode 有何区别？ | dsh 是 DeepSeek 官方框架，OpenCode 是模型无关的社区工具 |

---

## AI 使用建议

- 用户提到「DeepSeek Harness」「dsh」「Cordis 插件框架」时加载本技能
- 当前为 **Developer Preview**，API 可能有 Breaking Changes，以仓库最新代码为准
- 推荐使用 `npx @deepseek-ai/dsh web` 快速启动 Web UI 体验
- 插件开发遵循 Cordis 范式：Service → Component → Plugin 三层抽象
- 多模型选择：`deepseek-chat`（快速通用）vs `deepseek-reasoner`（深度推理）

---

## 相关技能

- **opencode** — 模型无关的终端 AI 编码代理：[../opencode/SKILL.md](../opencode/SKILL.md)
- **pi** — 极简终端 AI 编码代理：[../pi/SKILL.md](../pi/SKILL.md)
- **hermes-agent** — 自学习通用型 AI 智能体：[../hermes-agent/SKILL.md](../hermes-agent/SKILL.md)
- **dify** — 开源 LLM 应用开发平台：[../dify/SKILL.md](../dify/SKILL.md)

---

## 参考资源

- [DeepSeek Harness GitHub](https://github.com/deepseek-ai/deepseek-harness)
- [Cordis 编程范式论文](https://github.com/deepseek-ai/deepseek-harness/blob/main/docs/architecture.md)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs)
- [Discord 社区](https://discord.gg/deepseek)

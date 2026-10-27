---
name: deepseek-harness
description: "Use when running, scripting, or extending DeepSeek Harness (dsh) 0.2.1 — npx @deepseek-ai/dsh web / dsh --profile, headless one-shot runs, the deepseek-harness-sdk Python DeepSeekHarness client, or Cordis plugins that export apply(ctx) and register tools with defineTool; also when a profile patch fails to load, tools never appear in a session, or DeepSeekHarness raises on startup. dsh: plugin-everything agent harness by DeepSeek AI, powered by Cordis."
tags:
  - ai
  - agent
  - deepseek
  - cordis
  - plugin
  - typescript
  - python
  - harness
  - cli
---

> **项目地址：** <https://github.com/deepseek-ai/deepseek-harness>
>
> **官方文档：** <https://deepseek-harness.github.io/deepseek-harness/>
>
> **npm：** `@deepseek-ai/dsh`（0.2.1-rc.2，截至 2026-10）｜ **PyPI：** `deepseek-harness-sdk`
>
> **许可证：** MIT

## 概述

DeepSeek Harness（命令 `dsh`）是 DeepSeek AI 开源的智能体框架，"一切皆插件"架构，底层是 [Cordis](https://github.com/cordiverse/cordis)（设计见论文 *A Programming Paradigm for Spatiotemporal Composability*）。一个 `dsh` 进程 = 一棵由 plugin bundle 逐层 patch 出来的插件树；Web / headless / SDK / ACP 都是不同的 profile，不是不同的可执行文件。

- **profile 即入口**：`dsh web`、`dsh --profile headless "job"`、`dsh --profile sdk`、`dsh --profile acp` 共用同一个 npm 包
- **分层组合**：shipped bundle → profile 的 `cordis.patch.yml` → `$DSH_HOME/cordis.patch.yml` → `--patch` 覆盖层
- **插件形态**：TypeScript 模块导出 `name` / `inject` / `apply(ctx)`，工具用 `defineTool` 注册
- **双语言自动化**：`dsh --profile headless` 一条命令出结果；Python 侧有 `deepseek-harness-sdk`
- **developer preview**：官方明确会有 breaking changes，锁版本使用

---

## 环境准备

### 方式一：npm 直接跑（最快验证）

```bash
# 需要 Node.js；首次会下载依赖
npx @deepseek-ai/dsh web
```

默认在 `http://127.0.0.1:3080` 起 Web UI 并尝试打开浏览器；SSH 场景只打印地址。加 `--no-open` 不自动开浏览器：

```bash
npx @deepseek-ai/dsh web --no-open
```

### 方式二：仓库源码构建（开发插件时用）

```bash
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

### 方式三：Python SDK

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install deepseek-harness-sdk
```

SDK 自带匹配的原生运行时 wheel 和 `dsh` 命令，跑 SDK 不需要系统 Node.js；只有用 `dsh plugin` 管理插件时才需要 pnpm。

验证：

```bash
dsh --version                 # 打印运行时版本
npx @deepseek-ai/dsh --help   # 启动器自身的参数（不是 web app 的参数）
```

> profile 启动时会校验插件声明的 `engines.dsh` 版本区间，不兼容需要显式声明精确版本豁免。

---

## 核心用法

### 入口模式

| 命令 | 用途 |
|------|------|
| `dsh <name>` / `dsh --profile <name>` | 启动 `$DSH_HOME/profiles/<name>` 下的 profile |
| `dsh web` | Web UI（默认 127.0.0.1:3080） |
| `dsh --profile headless "job"` | 跑一个持久化会话，打印最终答案后退出 |
| `dsh --profile sdk` / `sdk-minimal` | 通过 JSON-RPC stdio 服务 SDK 客户端 |
| `dsh --profile acp` | 通过 ACP stdio 服务自动化客户端 |
| `dsh --profile <name> --from-default-profile <template>` | 用 shipped 模板重建一个自定义 profile |
| `dsh plugin --profile <name> <pnpm args>` | 转发给 pnpm 管理该 profile 的插件 |

启动器只解析自己的参数，第一个不认识的 token 起都交给 profile 里的 app：

```bash
dsh --profile web --port 8080     # --port 属于 web app，不是启动器的
dsh --profile web --help          # web app 自己的帮助
dsh --help                        # 启动器帮助
```

### 检查组合结果（不启动）

```bash
dsh --profile web --dump-default-config   # 打印默认组合树
dsh --profile web --dump-config           # 打印叠加了本机 patch 后的结果
dsh --profile web --dump-config-schema    # 打印插件声明的 JSON Schema
```

### Python SDK

```python
from pathlib import Path

from deepseek_harness import DeepSeekHarness

workspace = Path("./workspace").resolve()
dsh_home = Path("./example-dsh-home").resolve()

with DeepSeekHarness(
    provider="deepseek-official",
    model="deepseek-v4-flash",
    max_tokens=49_152,
    cwd=str(workspace),
    dsh_home=str(dsh_home),
    profile="sdk-minimal",
) as harness:
    result = harness.run(
        "Inspect the repository and fix the failing tests.",
        session_id="example-001",
    )

print(result.final_response)
```

要点：

- SDK 懒启动捆绑的 `dsh --profile sdk-minimal` 进程，上下文管理器退出时关闭
- 配置 = profile + 持久 patch + home patch + 构造时传入的 `patches` 元组，没有"整份配置对象"这种入口
- 凭据走环境变量 `DEEPSEEK_API_KEY`（代理端点用 `DEEPSEEK_BASE_URL`）
- SDK 不会静默读取 `~/.dsh`；`dsh_home` 必须显式给
- `sdk-minimal` 只有 `bash`/`pwsh`、`read_image`、`working_directory` 三个面向模型的工具；要写文件得自己 patch 进 `str_replace_editor`

解除 minimal 限制（把编辑器工具 patch 进来）：

```yaml
# editor.patch.yml
- insert:
    - id: tool-str-replace-editor
      name: '@deepseek-ai/dsh-tool-str-replace-editor'
```

```python
DeepSeekHarness(profile="sdk-minimal", patches=("./editor.patch.yml",), ...)
```

---

## 插件开发

插件是一个 TypeScript 模块，导出 `apply`，框架加载时把 `ctx` 交给它注册能力：

```typescript
import type { Context } from '@deepseek-ai/cordis'

export const name = 'hello-plugin'

export function apply(ctx: Context) {
  console.log('[hello-plugin] plugin loaded!')
}
```

注册一个模型可调用的工具：

```typescript
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'greet-tool'
export const inject = ['tools']

export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'greet',
    description: 'Greet someone by name.',
    parameters: {
      name: { type: 'string', required: true, description: 'The name to greet' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      return `Hello, ${args.name}!`
    },
  }))
}
```

三种形态：函数模块（最常用）、`export default { name, inject, apply }` 对象、以及 `extends Service` 的类（需要向别的插件提供服务时）。`ctx` 上注册的东西在插件卸载时自动清理；需要显式释放的资源用 `ctx.effect(() => { ...; return () => cleanup() })`。

### 把本地插件挂进 Web

```yaml
# scratch-plugin/cordis.yml —— 插件路径必须是绝对路径
- insert:
    - id: hello
      name: '/absolute/path/to/deepseek-harness/scratch-plugin/src/my-plugin.ts'
```

```bash
pnpm dsh web --patch ./scratch-plugin/cordis.yml
```

---

## 典型工作流

### 工作流一：从零跑起 Web UI 并接一个模型

输入：一台装了 Node.js 的机器 + 一个 DeepSeek API Key；输出：能在浏览器里对话的 dsh 会话。

1. `npx @deepseek-ai/dsh web`（远程服务器加 `--no-open`，自己转发 3080 端口）
2. 打开 `http://127.0.0.1:3080`，进 **Settings → Models**，填 [DeepSeek API Key](https://platform.deepseek.com/) 保存——模型路由立刻可用，不需要重启
3. 点 **Choose workspace** 选一个项目目录（未选工作区时会话输入框不可用）
4. 发一条任务（例如"总结这个仓库，列出主要包"），观察工具调用与审批提示
5. 需要换 provider / 自定义 OpenAI 兼容端点时按 [providers 指南](https://deepseek-harness.github.io/deepseek-harness/) 改配置

### 工作流二：CI 里用 headless 跑一次任务

输入：仓库 + 提示词；输出：stdout 上的最终答案与退出码。

```bash
export DEEPSEEK_API_KEY=sk-...
dsh --profile headless "run the test suite and summarize failures"
echo "exit=$?"
```

headless 每次跑一个新建的持久会话，"job" 是交给模型的自然语言任务；适合放进 CI 做一个受控的一次性步骤，而不是长驻对话。

### 工作流三：写一个自定义工具并验证模型能调用

输入：插件目录；输出：模型能调用的 `greet` 工具。

1. 在仓库里建 `scratch-plugin/src/my-plugin.ts`，按上面的 `defineTool` 写法导出 `apply` 与 `inject = ['tools']`
2. 写 `scratch-plugin/cordis.yml`，用绝对路径 `insert` 这个插件
3. `pnpm dsh web --patch ./scratch-plugin/cordis.yml` 启动，终端应打印插件加载日志
4. 在 Web UI 里说"用 greet 工具跟 Ada 打个招呼"，确认返回 `Hello, Ada!`
5. 改完代码重启开发命令（或让 dsh-hmr 重载）再看效果

### 工作流四：Python 侧批量跑任务

1. `pip install deepseek-harness-sdk`，准备一个一次性工作区目录和一个独立的 `dsh_home`
2. 用 `DeepSeekHarness(...)` 上下文管理器包住 `harness.run(prompt, session_id=...)`
3. `result.final_response` 取结果；sessions 以未压缩 JSONL 落在 `<dsh_home>/sessions`
4. 需要额外工具就先写 patch 文件、通过 `patches=` 传进去

---

## 最佳实践

1. **锁版本**：developer preview 会破坏兼容；升级前先跑一遍自己的插件/脚本
2. **一个用途一个 profile**：把"跑 Web""跑 CI""跑 SDK"分成不同 profile，改动隔离
3. **用 `--dump-config` 排查**：插件不生效时先看组合树里到底有没有那一行
4. **插件路径写绝对路径**：patch 文件只贡献配置，不改变模块解析目录
5. **别把 `~/.dsh` 当垃圾场**：SDK 场景用独立的 `dsh_home`，profile、凭据、会话都隔离
6. **安全边界**：`sdk-minimal` 固定 danger-full-access，shell 能改运行时可见的任何路径；用一次性 checkout 或容器

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 浏览器打开 3080 空白或连不上 | 确认进程真在监听（服务端日志有 URL）；远程机器用 `--no-open` 并自己转发端口；先 `dsh --version` 确认运行时可用 |
| `dsh web --port 8080` 报未知参数 | `--port` 属于 web app 而不是启动器；写成 `dsh --profile web --port 8080` 或 `dsh web --port 8080` 让 app 解析 |
| 插件改了不生效 | patch 里插件路径不是绝对路径、或没带 `--patch`；用 `--dump-config` 确认该行进了组合树 |
| 工具没出现在会话里 | 插件没写 `export const inject = ['tools']`（Cordis 会等依赖就绪）、或工具名与 instanceof 注册失败；看启动日志有无插件加载报错 |
| 打开会话说还没选工作区 | Web UI 需要先 Choose workspace；`dsh` 进程的当前目录只是默认根 |
| `DeepSeekHarness(...)` 启动即报错 | `dsh_home` 不存在、profile 缺 JSON-RPC server 行（`sdk`/`sdk-minimal` 才有）、或 patch 语法错——错误会明确指出是 profile 还是 patch |
| SDK 想写文件但只有 bash | `sdk-minimal` 故意精简；把 `str_replace_editor` 用 patch 插进来，或换 `sdk` profile |
| 升级后插件报版本不兼容 | 插件声明的 `engines.dsh` 与运行时不符；升级插件，或用官方支持的精确版本豁免 |
| 想接 ACP 客户端 | 用 `dsh --profile acp`，不要自己拼 JSON-RPC；ACP 与 SDK 是两个 profile |

---

## AI 使用建议

- **推荐工作流模式**：先确认目标形态——人在浏览器里用就走 `dsh web`；机器里跑一次性任务走 `dsh --profile headless`；Python 程序内嵌走 `deepseek-harness-sdk` 的 `DeepSeekHarness`；要扩能力就写 Cordis 插件（`apply(ctx)` + `defineTool`）。诊断配置问题一律先 `--dump-config`。
- **关键注意事项**：① 启动器参数与 app 参数分界在第一个不识别 token；② 插件路径必须绝对路径；③ `inject` 声明依赖，否则 `ctx.tools` 可能还没就绪；④ developer preview，锁版本；⑤ `sdk-minimal` 只有三个工具且固定 danger-full-access。
- **常用代码模式**：Web = `npx @deepseek-ai/dsh web`；headless = `dsh --profile headless "job"`；Python = `with DeepSeekHarness(provider=..., model=..., cwd=..., dsh_home=..., profile="sdk-minimal") as h: h.run(prompt, session_id=...)`；工具 = `ctx.tools.register(defineTool({name, description, parameters, output, execute}))`。
- **不要臆造**：没有 `dsh chat` 子命令、没有 `--bundle` 参数、没有 `from deepseek_harness import Harness` 这种简化类；`dsh` 不用 `config.yaml` 描述模型清单（模型在 Web UI 的 Settings → Models 或 provider 配置里）。API 细节以官方文档站与仓库 `docs/` 为准。

---

## 相关技能

- **opencode** — 模型无关的终端编码 Agent（对照另一种 Agent 宿主形态）：[../opencode/SKILL.md](../opencode/SKILL.md)
- **hermes-agent** — 自学习通用型 Agent（对照技能/记忆闭环设计）：[../hermes-agent/SKILL.md](../hermes-agent/SKILL.md)
- **dify** — 开源 LLM 应用开发平台（低代码编排对照）：[../dify/SKILL.md](../dify/SKILL.md)
- **my-opencode-deepseek-config** — OpenCode × DeepSeek 的纯配置方案（另一套路由/成本纪律）：[../my-opencode-deepseek-config/SKILL.md](../my-opencode-deepseek-config/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/deepseek-ai/deepseek-harness>
- 文档站：<https://deepseek-harness.github.io/deepseek-harness/>
- Cordis：<https://github.com/cordiverse/cordis>｜ 设计论文：<https://arxiv.org/abs/2608.25512>
- 安全须知：<https://github.com/deepseek-ai/deepseek-harness/blob/master/SAFETY.md>
- 插件目录话题：<https://github.com/topics/dsh-plugin>
- DeepSeek API：<https://platform.deepseek.com/api-docs>

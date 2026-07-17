---
name: pi
description: "Use when needing a minimal, extensible terminal AI coding agent harness in TypeScript with plugin architecture. Pi: minimalist terminal AI coding agent emphasizing simplicity and composability."
tags: [ai, agent, coding-agent, terminal, llm, typescript, extension, pi]
---

> **项目地址�?* <https://github.com/earendil-works/pi>
>
> **官网 / 文档�?* <https://pi.dev> �?<https://pi.dev/docs/latest>
>
> **最新发布：** 参见 [GitHub Releases](https://github.com/earendil-works/pi/releases)
>
> **许可证：** MIT

## 概述

Pi 是一个面向工程化场景�?**Agent Harness**，不仅是单一 CLI�?

- `@earendil-works/pi-coding-agent`：交互式终端编码 Agent
- `@earendil-works/pi-agent-core`：Agent 运行时（工具调用 + 状态管理）
- `@earendil-works/pi-ai`：统一多模�?Provider API
- `@earendil-works/pi-tui`：终�?UI 渲染�?

适用场景�?

- 终端内多步代码任务（读改代码、执行命令、追踪上下文�?
- 自建可扩�?Agent（Extensions / Skills / Prompt Templates�?
- 需要模型供应商可替换、可审计、可容器化的团队环境

---

## 环境与安�?

### 前置要求

- Node.js `>=22.19.0`
- npm（或等价 Node 包管理器�?

### 常用安装方式

```bash
# 全局安装 coding agent CLI
npm install -g @earendil-works/pi-coding-agent

# 验证版本
pi --version
```

如需源码开发：

```bash
git clone https://github.com/earendil-works/pi.git
cd pi
npm install --ignore-scripts
npm run build
```

> 上游仓库�?monorepo，官方开发流程以 `npm install --ignore-scripts`、`npm run build`、`npm run check` 为主�?

---

## 核心能力速览

| 能力 | 说明 |
|------|------|
| 多模型统一接入 | OpenAI / Anthropic / Google �?Provider 统一抽象 |
| Agent 运行�?| 工具调用、会话状态、任务分解与执行 |
| CLI + TUI | 终端交互式编码体验，适配日常研发流程 |
| 可扩展机�?| Extensions、Skills、Prompt 模板、主�?|
| 容器化方�?| Gondolin / Docker / OpenShell 等隔离模�?|
| 工程化发�?| Monorepo + release 流程 + 依赖锁定策略 |

---

## 常用命令

```bash
pi --help
pi --version
```

开发仓库常用校验命令（�?`pi` 源码目录）：

```bash
npm run build
npm run check
npm run test
```

---

## 典型工作�?

### 1) 本地终端编码助手

1. 在项目目录启�?`pi`
2. �?Agent 分析需求并分步执行
3. 审阅改动与命令输�?
4. 人工确认后提�?

### 2) 团队扩展能力

1. 基于 Extensions 定义团队工具接入方式
2. 把可复用提示流程沉淀�?Skills
3. 在仓库内版本化管理配置，确保团队一致�?

### 3) 强隔离执�?

1. 对高权限任务采用容器/沙箱模式
2. 将内置工具与 `!` 命令路由到隔离环�?
3. 保留宿主�?Provider 凭据与审计链�?

---

## 安全与最佳实�?

Pi 默认继承启动进程权限，不自带强制权限沙箱。生产建议：

- 对不受信任的任务启用容器化（Docker / Gondolin / OpenShell�?
- 将敏感凭据放在最小权限环境变量中
- 固定依赖版本并审�?lockfile 变更
- �?CI 中执�?`npm ci --ignore-scripts` + 安全审计

---

## 常见问题（FAQ�?

| 问题 | 解决建议 |
|------|---------|
| `pi` 命令不可�?| 检�?Node 版本与全局安装路径，重新安�?`@earendil-works/pi-coding-agent` |
| 依赖安装失败 | 使用官方推荐�?`npm install --ignore-scripts`，并检查网络代�?|
| 模型调用异常 | 核对 Provider API Key、Base URL 与模型名称配�?|
| 想限制工具权�?| 使用容器�?沙箱运行，不要直接在高权限宿主机执行不受信任的任�?|
| 团队想统一规范 | �?Skills/模板/配置文件纳入仓库版本控制并走 PR 审查 |

---

## AI 使用建议

- 用户提到「Pi」「Agent Harness」「终端编码代理」「多 Provider 统一接入」时优先加载本技能�?
- 回答部署问题时先确认�?**个人本地使用** 还是 **团队隔离部署**�?
- 涉及权限控制时明确说明：Pi 默认不提供强制沙箱，应结合容器方案�?
- 涉及版本差异时提醒以 `pi --version` �?Releases 页面为准�?

---

## 参考资�?

- 项目主页�?https://pi.dev>
- 文档�?https://pi.dev/docs/latest>
- Releases�?https://github.com/earendil-works/pi/releases>
- npm 包：<https://www.npmjs.com/package/@earendil-works/pi-coding-agent>
- 上游中文教程�?https://znlgis.github.io/ai/pi/>

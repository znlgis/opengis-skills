---
name: openclaw
description: "Use when setting up a multi-channel personal AI assistant gateway bridging chat platforms (Telegram, Discord, WhatsApp, WeChat) with LLM backends. OpenClaw: multi-channel AI assistant gateway for unified personal AI access."
tags:
  - ai
  - assistant
  - gateway
  - self-hosted
  - multi-channel
  - typescript
  - agent
---

> **项目地址：** <https://github.com/openclaw/openclaw>
>
> **官网 / 文档：** <https://openclaw.ai> ｜ <https://docs.openclaw.ai>
>
> **许可证：** MIT ｜ **语言：** TypeScript
> **发布频道：** latest / beta / dev（参见 [GitHub Releases](https://github.com/openclaw/openclaw/releases)）

> ⚠️ OpenClaw 的助手可以执行命令、读写文件、控制设备并接入你的私人聊天账号。**对外暴露前**务必阅读官方 [Security](https://docs.openclaw.ai/gateway/security) 与 [Exposure runbook](https://docs.openclaw.ai/gateway/security/exposure-runbook)，并配置沙箱与访问控制。

## 概述

OpenClaw 是「本地优先、单一信任边界、面向个人助手场景的多通道 AI Gateway」。聊天平台只是**入口**，真正的核心是常驻的 **Gateway（控制平面）**，负责会话、通道、模型、工具、节点、技能、插件、配置与安全策略。

- **本地优先 Gateway**：单一控制平面，统一管理 sessions / channels / tools / events。
- **多通道接入**：WhatsApp、Telegram、Slack、Discord、Google Chat、Signal、iMessage、IRC、Microsoft Teams、Matrix、飞书(Feishu)、LINE、Mattermost、Nextcloud Talk、Nostr、Synology Chat、Tlon、Twitch、Zalo、微信(WeChat)、QQ、WebChat 等。
- **多智能体路由**：把不同通道/账号/对端路由到隔离的 agent（独立 workspace 与会话）。
- **工具与沙箱**：每类工具可 allow/ask/deny；典型默认放行 `bash`/`process`/`read`/`write`/`edit`/`sessions_*`，默认拒绝 `browser`/`canvas`/`nodes`/`cron`/`discord`/`gateway`。
- **节点(Nodes)**：手机/桌面作为节点通过 Gateway WebSocket 配对，暴露设备能力（语音、屏幕、Canvas）。
- **Control UI / Canvas / 语音**：可在 macOS/iOS/Android 上听说，并渲染可交互的实时 Canvas。

---

## 安装与启动

推荐用引导式 `onboard`（支持 macOS / Linux / Windows）：

```bash
npm install -g openclaw@latest
# 或 pnpm add -g openclaw@latest

# 引导设置 Gateway、workspace、通道、技能，并安装常驻守护进程（launchd/systemd 用户服务）
openclaw onboard --install-daemon

# Gateway 管理
openclaw gateway status
openclaw gateway stop
openclaw gateway --port 18789 --verbose   # 默认端口 18789
```

最小配置 `~/.openclaw/openclaw.json`（仅设置模型与默认值，JSON5 语法）：

```json5
{
  agent: {
    model: "<provider>/<model-id>",
  },
}
```

完整配置项见官方 [Configuration](https://docs.openclaw.ai/gateway/configuration)。也支持 [Docker 安装](https://docs.openclaw.ai/install/docker) 与 [Nix](https://github.com/openclaw/nix-openclaw)。

发布通道：`latest`（稳定，tag `vYYYY.M.D`）、`beta`（预发布）、`dev`（main 头部）。

---

## 典型工作流

```text
1. openclaw onboard --install-daemon     # 初始化 Gateway + workspace + 通道
2. 在 onboard 中接入至少一个聊天通道（如 Telegram）与一个模型 Provider
3. 在手机用 Telegram/WhatsApp 直接与助手对话；桌面用 Control UI 观察与控制
4. 按需开启工具（bash/process/...）、节点（设备能力）、cron（定时任务）
5. 暴露到公网前：配置沙箱、访问控制，按 Exposure runbook 加固
```

多智能体：在 `openclaw.json` 中把不同通道/账号路由到不同 agent，实现「工作助手」「家庭助手」隔离运行（各自 workspace 与会话历史）。

---

## 安全与沙箱（重点）

- **默认最小权限**：保持危险工具（`browser`/`canvas`/`nodes`/`cron`/`gateway`）默认 deny，仅按需开启。
- **远程暴露分层加固**：优先用 [Tailscale](https://docs.openclaw.ai/gateway/tailscale) 等私有网络，而非裸公网；务必读 [Remote access](https://docs.openclaw.ai/gateway/remote) 与 Exposure runbook。
- **隔离运行**：用专用账户/容器/虚拟机运行 Gateway，限制其可访问的文件与命令。
- **审计**：通过 events 与日志观察助手实际执行的工具调用。

---

## 本地开发（源码）

仓库是 pnpm workspace：

```bash
pnpm install
pnpm openclaw setup          # 写入本地 config/workspace（首次或重置后）
pnpm ui:build                # 构建 Control UI
pnpm gateway:watch           # 开发期按需重建运行时
# UI 迭代：pnpm ui:dev；生产构建：pnpm build 产出 dist/
```

> `pnpm openclaw ...` 经 `tsx` 直接运行 TypeScript；`pnpm gateway:watch` 不会重建 `dist/control-ui`，改动 `ui/` 后需重跑 `pnpm ui:build`。

---

## 常见问题（FAQ）

| 问题 | 解决 |
|------|------|
| OpenClaw 是桌面 RPA / Computer Use 吗？ | 不是。它是**多通道个人助手 Gateway**，核心是控制平面，聊天平台是入口 |
| Gateway 没保持运行 | 用 `openclaw onboard --install-daemon` 安装守护进程；`openclaw gateway status` 检查 |
| 通道连不上 | 在 onboard 中重新配置该通道凭证；不同平台的默认行为见官方 Channels 文档 |
| 助手执行了危险命令 | 收紧沙箱，把 `bash`/`process` 等设为 `ask`/`deny`，限定可用工具 |
| 想远程访问 | 优先 Tailscale 等私网；公网暴露前按 Security + Exposure runbook 加固 |
| 端口冲突 | `openclaw gateway --port <port>`（默认 18789） |
| 多账号互相串话 | 用多智能体路由，把通道/账号映射到隔离 agent（独立 workspace） |

---

## AI 使用建议

- 用户提到「个人 AI 助手网关」「把 Telegram/WhatsApp/微信接到一个 AI」「self-hosted assistant gateway」「OpenClaw」时加载本技能。
- 先澄清：**接哪些通道**、**用什么模型**、**是否需要节点/语音/Canvas**、**是否对外暴露**。
- 生成命令以 `openclaw onboard` 为起点，配置写 `~/.openclaw/openclaw.json`；强调最小权限沙箱与暴露前加固。
- 不要把 OpenClaw 误描述为桌面操作/Computer Use 工具——它是多通道助手 Gateway。

---

## 参考资源

- 文档：<https://docs.openclaw.ai>（Gateway、Configuration、Security、Sandboxing、Remote、Web surfaces）
- 架构：<https://docs.openclaw.ai/concepts/architecture> ｜ Gateway 协议：<https://docs.openclaw.ai/reference/rpc>
- 上游中文教程：<https://znlgis.github.io/>（ai/openclaw 系列）

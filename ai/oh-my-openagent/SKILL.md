---
name: oh-my-openagent
description: "Use when installing or running OmO (oh-my-openagent) 5.1.48 — the standalone omo CLI built on senpi, migrating an older OpenCode-plugin install with omo setup, choosing thinking levels with /thinking, or switching native/legacy editions; also when omo --version still prints 4.19.x because a stale global omo shadows omo-ai, the curl installer falls back to GitHub Releases, or provider keys and MCP servers must come across from OpenCode. npm omo-ai, SUL-1.0."
tags:
  - ai
  - agent
  - omo
  - opencode
  - cli
  - orchestration
  - migration
---

> **项目地址：** <https://github.com/code-yeongyu/oh-my-openagent>
>
> **官网 / 文档：** <https://omo.dev> ｜ <https://omo.dev/docs>
>
> **npm 包：** `omo-ai`（5.1.48，截至 2026-10）｜ CLI 命令：`omo`
>
> **许可证：** SUL-1.0（Sustainable Use License，商用前阅读条款）

> **版本关键变化：** OmO 5.0 起是**独立应用**（"OmO Native"），跑在作者维护的 senpi（[pi](https://github.com/badlogic/pi-mono) 的 fork）上，**不再需要 OpenCode**。4.x 及更早才是 OpenCode 插件（`oh-my-opencode`），旧装可用 `omo setup` 迁移。

## 概述

OmO 不是模型、也不是 IDE 插件，而是"一条 `omo` 命令把 token 变成交付物"的终端 Agent：调研、出稿、写后端前端、写代码都在同一套内置能力里。

- **独立运行时**：自带 senpi 引擎，不依赖 OpenCode 的插件注册
- **多模型编排**：不同角色分配不同模型并行跑（订阅型 provider 也支持）
- **并行后台智能体**：任务分给多个后台 agent 并行推进
- **内置工具集**：结构化检索/编辑、浏览器使用等以 skills 形式按需加载
- **思考档位**：`/thinking <level>`、`/efforts <level>` 控制推理强度，`Shift+Tab` 循环切换
- **会话续接**：`/resume`（或 `/sessions`）翻历史；shell 里 `omo -c` 续上一个会话、`omo -r` 打开选择器
- **自诊断**：`omo doctor` 看各任务类别能跑哪些 provider、旧安装留下了什么

---

## 安装

### 方式一：官方安装脚本（推荐）

```bash
curl -fsSL https://get.omo.dev/install.sh | bash
omo
```

Windows PowerShell：

```powershell
irm https://get.omo.dev/install.ps1 | iex
```

脚本会把对应 OS/CPU 的原生 `omo` 二进制装到 `~/.local/bin`，用发布校验和校验；镜像不可达时回退到 GitHub Releases。要换频道或锁版本，在 `bash` 后面追加：

```bash
curl -fsSL https://get.omo.dev/install.sh | bash -s -- beta
curl -fsSL https://get.omo.dev/install.sh | bash -s -- 5.1.1
```

### 方式二：包管理器（bun / npm）

```bash
bun add -g omo-ai          # 或 npm i -g omo-ai
```

> npm 上名为 `omo` 的包是别人的，与本项目无关；认准 `omo-ai`。

### 方式三：从旧版（OpenCode 插件）迁移

```bash
bunx oh-my-openagent install --platform=native     # 没有 bun 用 npx
```

这条命令会：① 找到被 `oh-my-openagent`/`oh-my-opencode`/`lazycodex` 占用的全局 `omo` 并只删这一个文件；② 执行 `bun add -g omo-ai`（或 `npm i -g omo-ai`）；③ 校验 `omo --version` 现在确实答的是 omo-ai；④ 询问是否立刻跑 `omo setup`（`--no-tui` 时只打印命令）。

验证：

```bash
omo --version        # 期望：omo 5.x.x (engine: senpi ...)
omo doctor           # provider/模型可用性 + 旧安装残留
```

要求：bun（推荐）或 npm，**Node 24 或更新**。

---

## 核心命令

| 命令 | 作用 |
|------|------|
| `omo` | 启动交互式会话 |
| `omo -c` / `omo -r` | 续上一个会话 / 打开历史选择器 |
| `omo setup` | 从 OpenCode 版或 LazyCodex 迁移 provider keys、自定义 provider、MCP、skills 与模型选择 |
| `omo doctor` | 诊断：哪些任务类别能跑、旧安装残留 |
| `omo doctor --models` | 看每个类别与 agent 用哪个模型、按什么顺序回退 |
| `omo update` | 包管理器安装方式下的自更新 |
| `omo --version` | 版本 + 引擎标识 |

会话内命令：

| 命令 | 作用 |
|------|------|
| `/thinking <level>` | 设置思考强度（不带参数打开选择器） |
| `/efforts <level>` | 在有 effort 分级的模型上直接设 reasoning effort |
| `Shift+Tab` | 循环切换思考档位 |
| `/resume` / `/sessions` | 恢复历史会话 |
| `/help` | 列出全部命令 |
| `/bug` | 在应用内提交问题报告（发送前可预览确切内容） |

### 配置：模型排除与回退

`omo doctor --models` 展示类别→模型的解析顺序；某个模型不想参与回退时，用 `omo.json` 里的 `exclude_models` 把它从所有位置排除。配置结构见 [omo-json 参考](https://omo.dev/docs)。

---

## 典型工作流

### 工作流一：从零装好并跑第一个任务（端到端）

输入：一台装了 Node 24+（或 bun）的机器 + 至少一个模型 provider 的凭据；输出：完成一次真实任务。

1. `curl -fsSL https://get.omo.dev/install.sh | bash`（Windows 用 `irm ... | iex`）
2. 确认 `omo --version` 回答的是 `omo 5.x.x (engine: senpi ...)`——如果还是 `4.19.x`，说明旧的全局 `omo` 还挡在前面
3. `omo doctor` 检查 provider 与任务类别可用性
4. `omo` 进会话，`/thinking low` 起步（轻任务别一上来就拉满）
5. 提一个具体任务，观察工具调用与产物；需要更强推理时 `/thinking high` 或 `Shift+Tab`
6. 收尾后 `omo -c` 继续、`omo -r` 翻其它会话

### 工作流二：从 OpenCode 插件版迁移

输入：一个 4.x（`oh-my-openagent`/`oh-my-opencode`）安装；输出：原生版接管，配置不丢。

1. `omo --version`、`npm ls -g oh-my-openagent oh-my-opencode` 先看清旧安装占用了什么
2. `bunx oh-my-openagent install --platform=native`（幂等；会先清掉旧的 `omo` 命令文件）
3. `omo setup` 迁移 provider keys、自定义 provider、MCP server、skills、模型选择
4. `omo doctor` 核对残留；再看 `omo doctor --models` 确认类别→模型顺序符合预期
5. 旧 OpenCode 环境可以并存——setup 不会写 OpenCode 的配置文件

### 工作流三：换频道或回滚版本

1. 装 beta：`curl -fsSL https://get.omo.dev/install.sh | bash -s -- beta`
2. 装指定版本：`... | bash -s -- 5.1.1`
3. 包管理器安装的用 `omo update` 更新；卸载 `rm ~/.local/bin/omo`，或 `bun remove -g omo-ai` / `npm uninstall -g omo-ai`
4. 回滚后再次 `omo --version` 确认引擎标识与版本

---

## 最佳实践

1. **先 doctor 再提问**：装完/迁移完先 `omo doctor`，能省掉一大半"为什么这个类别没反应"
2. **思考档位按任务给**：轻任务 `/thinking` 低档起步，复杂任务再升；`Shift+Tab` 是临时切换
3. **迁移用 installer，不要手搓 `bun add -g`**：旧机器上手工安装会被陈旧 `omo` 遮蔽（npm 报 EEXIST、bun 并着装），installer 会先清理
4. **凭据留在本机**：setup 只搬移配置，不要把 key 写进仓库
5. **看版本不只是看 tag**：`omo --version` 的引擎标识才是"到底跑的是哪一代"的判据

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `omo --version` 仍是 `4.19.x` | 旧包（`oh-my-openagent`/`oh-my-opencode`/`lazycodex`）还占着全局 `omo`；重跑 `bunx oh-my-openagent install --platform=native`（幂等，会先删旧命令文件并打印修复动作） |
| 安装脚本卡住或失败 | 镜像不可达时脚本会回退 GitHub Releases；网络受限就改用 `bun add -g omo-ai` |
| `omo` 找到的版本不对（PATH 顺序） | installer 会打印需要的 `export PATH="...:$PATH"`；照抄后重开终端 |
| `omo setup` 后模型还是旧的 | 用 `omo doctor --models` 看类别→模型顺序；必要时在 `omo.json` 用 `exclude_models` 排除不想要的模型 |
| 还需要 OpenCode 吗 | 5.x 不再需要；旧版（4.x 及更早）才是 OpenCode 插件。两代可以并存 |
| 许可证能商用吗 | SUL-1.0（Sustainable Use License），商用前阅读条款 |
| 报告问题怎么带日志 | 会话里 `/bug` 生成可预览的报告（含近期日志、脱敏后的环境与配置、会话记录）；不能使用时走 GitHub issue |

---

## AI 使用建议

- **推荐工作流模式**：先确认代际——`omo --version` 出现 `engine: senpi` 才是原生 5.x；迁移一律走 `bunx oh-my-openagent install --platform=native` + `omo setup`；排障先 `omo doctor` 与 `omo doctor --models`。
- **关键注意事项**：① npm 包是 `omo-ai`，不是 `omo`；② 旧安装会通过全局命令名遮蔽新装，必须让 installer 清理；③ 需要 bun 或 npm + Node 24+；④ 思考档位是会话级命令（`/thinking`、`/efforts`），不是 CLI 参数。
- **常用代码模式**：安装 = `curl -fsSL https://get.omo.dev/install.sh | bash`；迁移 = `bunx oh-my-openagent install --platform=native` → `omo setup`；诊断 = `omo doctor` / `omo doctor --models`；续接 = `omo -c`。
- **不要臆造**：5.x 没有 `bunx oh-my-opencode install`（那是 4.x 的 OpenCode 插件安装路径）；没有 `lazycodex` 作为主命令（只是旧版遗留的 bin 名）；不要写"必须先装 OpenCode"——只有 4.x 需要。

---

## 相关技能

- **opencode** — 4.x 时代的宿主客户端；5.x 已解耦，但配置语义仍有参考价值：[../opencode/SKILL.md](../opencode/SKILL.md)
- **my-opencode-deepseek-config** — 另一套 OpenCode 多 Agent 纯配置方案（DeepSeek 单模型 + thinking 档位）：[../my-opencode-deepseek-config/SKILL.md](../my-opencode-deepseek-config/SKILL.md)
- **superpowers-zh** — 方法论约束层，与模型编排互补：[../superpowers-zh/SKILL.md](../superpowers-zh/SKILL.md)
- **deepseek-harness** — DeepSeek 官方 Agent 框架（另一种"一切皆插件"的宿主）：[../deepseek-harness/SKILL.md](../deepseek-harness/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/code-yeongyu/oh-my-openagent>
- 安装与排障：<https://omo.dev/docs/install>
- 从 OpenCode 迁移：<https://omo.dev/docs>（Migrating from OpenCode）
- npm：<https://www.npmjs.com/package/omo-ai>
- 许可证：<https://github.com/code-yeongyu/oh-my-openagent/blob/dev/LICENSE.md>

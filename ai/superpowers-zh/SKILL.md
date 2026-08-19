---
name: superpowers-zh
description: "Use when constraining AI coding with Chinese TDD methodology, systematic debugging, code review, and verification workflows. Superpowers-zh: Chinese adaptation of the Superpowers AI-assisted programming skills and methodologies."
tags:
  - ai
  - skill
  - methodology
  - chinese
  - tdd
  - code-review
  - prompt
  - claude-code
---

> **项目地址：** <https://github.com/jnMetaCode/superpowers-zh>
>
> **英文上游：** <https://github.com/obra/superpowers>
>
> **许可证：** MIT ｜ **npm 包：** 参见 [npm](https://www.npmjs.com/package/superpowers-zh)｜ **运行要求：** Node.js ≥ 20

## 概述

superpowers-zh 不是代码库或语言框架，而是一套面向 AI 编程工具的「**工作方式插件**」：把工程实践固化为可被 AI 助手加载的 **Skills**，让 AI 在执行任务时先遵循流程、再生成代码。核心目标三句话：

1. **让 AI 先想清楚再动手**：不从模糊需求直接跳到编码，先澄清目的、约束、成功标准与可选方案。
2. **让 AI 用工程纪律工作**：用 TDD、系统化调试、完成前验证、代码审查约束「看起来能跑」的草率实现。
3. **让中文团队直接落地**：在完整汉化基础上补充中文代码审查、中文 Git 工作流、中文技术文档与提交规范等本土化能力。

包内含 `skills/`、`agents/`、`commands/`、`hooks/` 与一键安装脚本 `bin/superpowers-zh.js`。它在 obra/superpowers（英文上游，250k+ ⭐）基础上完整汉化并新增 6 个中国原创 skills，支持 Claude Code / GitHub Copilot CLI / Hermes Agent / Cursor / Claw Code / Windsurf / Kiro / Gemini CLI / OpenCode / Qoder 等 20 款工具。

---

## 安装

```bash
# 一键安装（交互式选择目标 AI 工具并写入对应配置）
npx superpowers-zh
```

要求 Node.js ≥ 20。安装器会按所选工具把 skills/agents/commands/hooks 写入相应位置（如 Claude Code 的 plugin、Cursor 的 `.cursor-plugin`、OpenCode 的 `.opencode/plugins`、Codex 的 `.codex-plugin`、Gemini 的 `gemini-extension.json` 等）。

---

## Skill 机制与方法论闭环

每个 Skill 都有**名称 + 触发描述 + 详细流程**。当 AI 工具支持 Skill 发现或自定义指令时，会在对应场景加载这些流程，用流程约束行动。核心方法论按软件交付链路组织：

| 阶段 | Skill 作用 |
|------|-----------|
| 需求澄清 | 先问清目的、约束、成功标准，避免基于模糊需求乱改 |
| 方案设计 / 计划编写 | 列出可选方案与权衡，产出可执行计划再动手 |
| TDD | 先写测试再实现，约束「看起来能跑」的实现 |
| 系统化调试 | 复现 → 定位根因 → 修复 → 回归测试，而非凭直觉乱试补丁 |
| 完成前验证 | 收尾前必须运行测试 / 构建 / lint，不说「应该好了」 |
| 代码审查与反馈处理 | 验证审查建议是否适用本代码库，而非盲目附和 |
| 分支收尾 | 规范提交、合并与分支清理 |
| 并行子智能体 / Git Worktree | 用子代理与 worktree 并行推进多任务 |
| 中国特色 Skills | 中文审查表达、提交规范、文档排版、国内 Git 平台流程、MCP 构建器、工作流执行器 |

`using-superpowers` 是入口型 Skill：引导 AI 在合适时机发现并加载其余技能。

---

## 典型工作流

```text
1. npx superpowers-zh           # 为你的 AI 工具安装中文方法论 Skills
2. 在 AI 工具中提出任务 → AI 先加载「需求澄清」Skill，问清目标与约束
3. 进入「方案设计 / 计划」Skill，产出方案与计划
4. 用「TDD」Skill 先写测试，再实现
5. 出 Bug 时走「系统化调试」Skill：复现→根因→修复→回归
6. 收尾用「完成前验证」运行测试/构建/lint，再用「代码审查」「分支收尾」收口
```

---

## 常见问题（FAQ）

| 问题 | 解决 |
|------|------|
| 它是模型或插件吗 | 都不是，是一套被 AI 加载的「方法论 Skills」，约束 AI 的工作流程 |
| 支持哪些工具 | Claude Code、Copilot CLI、Cursor、OpenCode、Hermes Agent、Windsurf、Gemini CLI、Kiro、Qoder 等 20 款 |
| 和英文 superpowers 区别 | 完整汉化 + 6 个中国原创 skills（中文审查/提交规范/文档排版/国内 Git 流程/MCP 构建器/工作流执行器） |
| 安装要求 | Node.js ≥ 20，`npx superpowers-zh` 一键安装 |
| AI 不触发 Skill | 确认工具支持 Skill 发现/自定义指令，并已写入对应配置；从 `using-superpowers` 入口引导 |
| 能和编码 Agent 一起用吗 | 可以，常与 OpenCode / Hermes Agent / Claude Code 搭配，作为「工作方式约束层」 |

---

## AI 使用建议

- 用户提到「让 AI 先澄清需求再写代码」「中文 TDD / 代码审查方法论」「superpowers 中文版」「AI 编程工作流规范」时加载本技能。
- 它是**方法论约束层**，与具体编码工具（OpenCode、Claude Code、Hermes 等）正交，可叠加使用。
- 安装用 `npx superpowers-zh`（Node ≥ 20）；强调「澄清→设计→计划→TDD→调试→验证→审查→收尾」闭环。
- 鼓励 AI 在动手前主动加载「需求澄清/计划」Skill，在收尾前加载「完成前验证」Skill。

---

## 参考资源

- 仓库：<https://github.com/jnMetaCode/superpowers-zh>
- 英文上游 obra/superpowers：<https://github.com/obra/superpowers>
- 上游中文教程：<https://znlgis.github.io/>（ai/superpowers-zh 系列）

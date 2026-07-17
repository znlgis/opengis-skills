---
name: superpowers-zh
description: "Use when constraining AI coding with Chinese TDD methodology, systematic debugging, code review, and verification workflows. Superpowers-zh: Chinese adaptation of the Superpowers AI-assisted programming skills and methodologies."
tags: [ai, skill, methodology, chinese, tdd, code-review, prompt, claude-code]
---

> **项目地址 -- ?* <https://github.com/jnMetaCode/superpowers-zh>
>
> **英文上游 -- ?* <https://github.com/obra/superpowers>
>
> **许可证：** MIT  -- ?**npm 包：** 参见 [npm](https://www.npmjs.com/package/superpowers-zh) -- ?**运行要求 -- ?* Node.js  -- ?20

## 概述

superpowers-zh 不是代码库或语言框架，而是一套面 -- ?AI 编程工具的 -- ?*工作方式插件**」：把工程实践固化为可被 AI 助手加载 -- ?**Skills**，让 AI 在执行任务时先遵循流程、再生成代码。核心目标三句话 -- ?

1. ** -- ?AI 先想清楚再动 -- ?*：不从模糊需求直接跳到编码，先澄清目的、约束、成功标准与可选方案 -- ?
2. ** -- ?AI 用工程纪律工 -- ?*：用 TDD、系统化调试、完成前验证、代码审查约束「看起来能跑」的草率实现 -- ?
3. **让中文团队直接落 -- ?*：在完整汉化基础上补充中文代码审查、中 -- ?Git 工作流、中文技术文档与提交规范等本土化能力 -- ?

包内 -- ?`skills/`、`agents/`、`commands/`、`hooks/` 与一键安装脚 -- ?`bin/superpowers-zh.js`。它 -- ?obra/superpowers（英文上游， -- ?15  -- ?⭐）基础上完整汉化并新增 4 个中国原 -- ?skills，支 -- ?Claude Code / GitHub Copilot CLI / Hermes Agent / Cursor / Claw Code / Windsurf / Kiro / Gemini CLI / OpenCode / Qoder  -- ?18 款工具 -- ?

---

## 安装

```bash
# 一键安装（交互式选择目标 AI 工具并写入对应配置）
npx superpowers-zh
```

要求 Node.js  -- ?20。安装器会按所选工具把 skills/agents/commands/hooks 写入相应位置（如 Claude Code  -- ?plugin、Cursor  -- ?`.cursor-plugin`、OpenCode  -- ?`.opencode/plugins`、Codex  -- ?`.codex-plugin`、Gemini  -- ?`gemini-extension.json` 等） -- ?

---

## Skill 机制与方法论闭环

每个 Skill 都有**名称 + 触发描述 + 详细流程**。当 AI 工具支持 Skill 发现或自定义指令时，会在对应场景加载这些流程，用流程约束行动。核心方法论按软件交付链路组织：

| 阶段 | Skill 作用 |
|------|-----------|
| 需求澄 -- ?| 先问清目的、约束、成功标准，避免基于模糊需求乱 -- ?|
| 方案设计 / 计划编写 | 列出可选方案与权衡，产出可执行计划再动 -- ?|
| TDD | 先写测试再实现，约束「看起来能跑」的实现 |
| 系统化调 -- ?| 复现  -- ?定位根因  -- ?修复  -- ?回归测试，而非凭直觉乱试补 -- ?|
| 完成前验 -- ?| 收尾前必须运行测 -- ?/ 构建 / lint，不说「应该好了 -- ?|
| 代码审查与反馈处 -- ?| 验证审查建议是否适用本代码库，而非盲目附和 |
| 分支收尾 | 规范提交、合并与分支清理 |
| 并行子智能体 / Git Worktree | 用子代理 -- ?worktree 并行推进多任 -- ?|
| 中国特色 Skills | 中文审查表达、提交规范、文档排版、国 -- ?Git 平台流程 |

`using-superpowers` 是入口型 Skill：引 -- ?AI 在合适时机发现并加载其余技能 -- ?

---

## 典型工作 -- ?

```text
1. npx superpowers-zh           # 为你 -- ?AI 工具安装中文方法 -- ?Skills
2.  -- ?AI 工具中提出任 -- ? -- ?AI 先加载「需求澄清」Skill，问清目标与约束
3. 进入「方案设 -- ?/ 计划」Skill，产出方案与计划
4. 用「TDD」Skill 先写测试，再实现
5.  -- ?Bug 时走「系统化调试」Skill：复现→根因→修复→回归
6. 收尾用「完成前验证」运行测 -- ?构建/lint，再用「代码审查」「分支收尾」收 -- ?
```

---

## 常见问题（FAQ -- ?

| 问题 | 解决 |
|------|------|
| 它是模型或插件吗 | 都不是，是一套被 AI 加载的「方法论 Skills」，约束 AI 的工作流 -- ?|
| 支持哪些工具 | Claude Code、Copilot CLI、Cursor、OpenCode、Hermes Agent、Windsurf、Gemini CLI、Kiro、Qoder  -- ?18  -- ?|
| 和英 -- ?superpowers 区别 | 完整汉化 + 4 个中国原 -- ?skills（中文审 -- ?提交规范/国内 Git 流程等） |
| 安装要求 | Node.js  -- ?20，`npx superpowers-zh` 一键安 -- ?|
| AI 不触 -- ?Skill | 确认工具支持 Skill 发现/自定义指令，并已写入对应配置；从 `using-superpowers` 入口引导 |
| 能和编码 Agent 一起用 -- ?| 可以，常 -- ?OpenCode / Hermes Agent / Claude Code 搭配，作为「工作方式约束层 -- ?|

---

## AI 使用建议

- 用户提到「让 AI 先澄清需求再写代码」「中 -- ?TDD / 代码审查方法论」「superpowers 中文版」「AI 编程工作流规范」时加载本技能 -- ?
- 它是**方法论约束层**，与具体编码工具（OpenCode、Claude Code、Hermes 等）正交，可叠加使用 -- ?
- 安装 -- ?`npx superpowers-zh`（Node  -- ?20）；强调「澄清→设计→计划→TDD→调试→验证→审查→收尾」闭环 -- ?
- 鼓励 AI 在动手前主动加载「需求澄 -- ?计划」Skill，在收尾前加载「完成前验证」Skill -- ?

---

## 参考资 -- ?

- 仓库 -- ?https://github.com/jnMetaCode/superpowers-zh>
- 英文上游 obra/superpowers -- ?https://github.com/obra/superpowers>
- 上游中文教程 -- ?https://znlgis.github.io/>（ai/superpowers-zh 系列 -- ?

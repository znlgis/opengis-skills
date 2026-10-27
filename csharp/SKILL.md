---
name: csharp-skills
description: "Use when developing with .NET/C# for Web APIs, ORM data access, Excel/Word file I/O, spreadsheet controls, structured logging, resilience policies, background jobs, error tracking, or .NET code protection. Index of 12 skills: Furion, Admin.NET Backend, Admin.NET Frontend, SqlSugar, NPOI, SOD, ReoGrid, Serilog, Polly, Hangfire, DotNet Reactor, Sentry."
tags:
  - dotnet
  - csharp
  - webapi
  - orm
  - office
  - excel
  - framework
  - security
---

> **父级入口：** [../SKILL.md](../SKILL.md) — 全仓 114 技能总索引

## 概述

本分类涵盖 **12 个 .NET 生态开源项目**的技能文件，聚焦企业级 Web 开发核心需求：

- **Web 框架**：Furion、Admin.NET
- **数据访问**：SqlSugar、SOD（PDF.NET）
- **Office 操作**：NPOI、ReoGrid
- **日志与弹性**：Serilog、Polly、Hangfire
- **错误追踪与监控**：Sentry .NET SDK
- **代码保护**：DotNet Reactor

### 何时加载此索引？

- 用户使用 C#/.NET 开发
- 涉及「ORM」「Web API」「Excel 读写」「代码混淆」
- 不确定该用 SqlSugar 还是 SOD

---

## 技能列表

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [furion](./furion/SKILL.md) | .NET 极简企业级 Web 框架 | `dotnet` `webapi` `framework` |
| [admin-net-backend](./admin-net-backend/SKILL.md) | Admin.NET 后端（基于 Furion） | `dotnet` `webapi` `rbac` `multitenant` |
| [admin-net-frontend](./admin-net-frontend/SKILL.md) | Admin.NET 前端（Vue 3） | `vue` `frontend` `admin` |
| [sqlsugar](./sqlsugar/SKILL.md) | 国产高性能多数据库 ORM | `orm` `dotnet` `database` |
| [sod](./sod/SKILL.md) | PDF.NET SOD：ORM + SQL-MAP + OQL | `orm` `dotnet` `database` |
| [npoi](./npoi/SKILL.md) | .NET Excel/Word 读写 | `excel` `office` `dotnet` |
| [reogrid](./reogrid/SKILL.md) | .NET 电子表格控件 | `dotnet` `spreadsheet` `winforms` `wpf` |
| [dotnet-reactor](./dotnet-reactor/SKILL.md) | .NET 商业级混淆/加壳/授权 | `dotnet` `obfuscation` `security` |
| [sentry](./sentry/SKILL.md) | Sentry .NET SDK：错误追踪与性能监控 | `dotnet` `error-tracking` `monitoring` `performance` |
| [serilog](./serilog/SKILL.md) | Serilog：结构化日志（sink/enricher/JSON 输出） | `dotnet` `logging` `structured-logging` `serilog` |
| [polly](./polly/SKILL.md) | Polly：v8 ResiliencePipeline 重试/超时/断路器 | `dotnet` `resilience` `retry` `circuit-breaker` |
| [hangfire](./hangfire/SKILL.md) | Hangfire：持久化后台任务与 Cron 调度 | `dotnet` `background-jobs` `cron` `scheduling` |

---

## 快速导航

| 用户需求 | 推荐加载 |
|---------|---------|
| "写一个 Web API 接口" | `furion/SKILL.md` |
| "快速搭建后台管理系统" | `admin-net-backend/SKILL.md` + `admin-net-frontend/SKILL.md` |
| ".NET 读写 Excel" | `npoi/SKILL.md` |
| ".NET 表格控件" | `reogrid/SKILL.md` |
| "多数据库 ORM 操作" | `sqlsugar/SKILL.md` |
| "MyBatis 风格的 SQL 映射" | `sod/SKILL.md` |
| "保护 .NET 代码不被反编译" | `dotnet-reactor/SKILL.md` |
| ".NET 错误追踪与性能监控" | `sentry/SKILL.md` |
| "结构化日志 / 输出 JSON 日志" | `serilog/SKILL.md` |
| "HTTP 重试、超时、熔断" | `polly/SKILL.md` |
| "后台任务与定时作业" | `hangfire/SKILL.md` |

---

## 相关分类

- **[gis/](../gis/SKILL.md)** — .NET GIS 组件（Mapsui、NetTopologySuite 等）
- **[cad/](../cad/SKILL.md)** — .NET CAD 开发（iFoxCAD、xBIM 等）
- **[ai/](../ai/SKILL.md)** — LLM 应用与 Agent

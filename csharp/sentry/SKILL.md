---
name: sentry
description: "Use when adding error tracking, performance monitoring, and release health to .NET applications — ASP.NET Core, MAUI, WPF, Blazor, EF Core integration. Sentry .NET SDK: cross-platform error and performance monitoring with source map support, breadcrumbs, and alerting."
tags:
  - dotnet
  - csharp
  - error-tracking
  - monitoring
  - performance
  - aspnet-core
  - observability
---

> **项目地址：** <https://github.com/getsentry/sentry-dotnet>
>
> **官方文档：** <https://docs.sentry.io/platforms/dotnet/>
>
> **NuGet：** <https://www.nuget.org/packages/Sentry>
>
> **许可证：** MIT

## 概述

Sentry 是一个开源的 **错误追踪与性能监控平台**，.NET SDK 支持将异常、崩溃、性能指标统一上报到 Sentry 服务端（SaaS 或自托管）。

### 核心特性

| 特性 | 说明 |
|------|------|
| 自动异常捕获 | 集成 ASP.NET Core / MAUI / WPF / Blazor / Console |
| 性能监控 | Transaction + Span 模型，自动采集 HTTP/DB/EF Core 耗时 |
| 源码映射 | Release + Debug Files 支持，还原压缩/混淆后的堆栈 |
| Breadcrumb | 自动记录用户操作、HTTP 请求、日志等上下文 |
| Session Replay | 用户会话回放（Web 前端支持） |
| Alerting | 基于 Issue / Metric 的告警规则 |
| 自托管 | 完整的自托管部署方案（Docker/Kubernetes） |

### 支持的平台

| 包名 | 用途 |
|------|------|
| `Sentry` | 核心 SDK（控制台/Worker） |
| `Sentry.AspNetCore` | ASP.NET Core Web API / MVC |
| `Sentry.Maui` | .NET MAUI 移动应用 |
| `Sentry.AspNetCore.Blazor.WebAssembly` | Blazor WASM |
| `Sentry.EntityFramework` | Entity Framework Core 集成 |
| `Sentry.DiagnosticSource` | DiagnosticSource 事件采集 |
| `Sentry.OpenTelemetry` | OpenTelemetry 集成 |
| `Sentry.Profiling` | 代码级性能剖析 |

---

## 环境准备

### 安装

```bash
# ASP.NET Core 项目
dotnet add package Sentry.AspNetCore

# 控制台 / Worker 项目
dotnet add package Sentry

# 可选集成
dotnet add package Sentry.EntityFramework     # EF Core
dotnet add package Sentry.DiagnosticSource    # HTTP / EF Core 自动 Span
dotnet add package Sentry.OpenTelemetry       # OTel 桥接
dotnet add package Sentry.Profiling           # 性能剖析
```

### 初始化

```csharp
// ASP.NET Core (Program.cs)
builder.WebHost.UseSentry(o =>
{
    o.Dsn = "https://examplePublicKey@o0.ingest.sentry.io/0";
    o.TracesSampleRate = 1.0;  // 100% 性能追踪采样
    o.Environment = builder.Environment.EnvironmentName;
    o.Release = "my-app@1.0.0";
});

// 控制台应用
SentrySdk.Init(o =>
{
    o.Dsn = "https://examplePublicKey@o0.ingest.sentry.io/0";
    o.TracesSampleRate = 0.2;  // 20% 采样
});
```

---

## 核心 API

### 手动上报异常

```csharp
try
{
    DoSomething();
}
catch (Exception ex)
{
    // 添加额外上下文
    SentrySdk.ConfigureScope(scope =>
    {
        scope.SetTag("feature", "payment");
        scope.SetExtra("request_body", requestBody);
        scope.User = new SentryUser { Id = "12345", Email = "user@example.com" };
    });
    
    SentrySdk.CaptureException(ex);
}
```

### 性能追踪

```csharp
// 创建 Transaction
var transaction = SentrySdk.StartTransaction("process-order", "task");
SentrySdk.ConfigureScope(s => s.Transaction = transaction);

try
{
    // Span: 数据库查询
    var dbSpan = transaction.StartChildSpan("db.query", "SELECT * FROM orders");
    var orders = await db.QueryAsync("SELECT * FROM orders WHERE ...");
    dbSpan.Finish();

    // Span: 业务逻辑
    var bizSpan = transaction.StartChildSpan("business.process");
    ProcessOrders(orders);
    bizSpan.Finish();

    transaction.Finish(SpanStatus.Ok);
}
catch (Exception ex)
{
    transaction.Finish(ex);
}
```

### Breadcrumb 自动采集

```csharp
// ASP.NET Core 自动记录：
// - HTTP 请求/响应
// - EF Core 查询
// - 日志消息（需配置 SentryLogs）
// - 认证事件

// 手动添加 Breadcrumb
SentrySdk.AddBreadcrumb(
    "User clicked checkout button",
    category: "ui",
    level: BreadcrumbLevel.Info
);
```

---

## 典型工作流

### ASP.NET Core 完整集成

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.WebHost.UseSentry(o =>
{
    o.Dsn = Environment.GetEnvironmentVariable("SENTRY_DSN");
    o.TracesSampleRate = 0.3;
    o.ProfilesSampleRate = 0.1;  // 采样率
    o.Environment = builder.Environment.EnvironmentName;
    o.Release = $"my-api@{Assembly.GetExecutingAssembly().GetName().Version}";
    
    // 性能：只追踪特定路由
    o.TracePropagationTargets = new[] { "https://my-api.com" };
});

builder.Services.AddSentryEFCore();  // EF Core 集成

var app = builder.Build();
app.UseSentryTracing();  // 性能中间件
app.MapControllers();
app.Run();
```

### 自托管部署（Docker）

```bash
# Sentry 自托管（开发环境）
git clone https://github.com/getsentry/self-hosted.git
cd self-hosted
./install.sh
# 访问 http://localhost:9000
```

---

## 最佳实践

1. **DSN 安全**：DSN 可以公开（不像 API Key），但仍建议通过环境变量管理
2. **采样率**：生产环境建议 `TracesSampleRate = 0.1-0.3`，避免高流量下性能影响
3. **Release 标记**：设置 `Release` 标签，让 Sentry 关联代码变更与错误
4. **BeforeSend 钩子**：过滤敏感信息（密码、Token）再上报
5. **用户隐私**：遵守 GDPR，配置 `SendDefaultPii = false`（默认）

---

$h$faq`

| 问题 | 解决方案 |
|------|---------|
| DSN 在哪里获取？ | Sentry Dashboard → Settings → Projects → Client Keys |
| 如何过滤敏感数据？ | 使用 `BeforeSend` 回调或 ` beforeSendTransaction` |
| ASP.NET Core 中性能追踪不生效？ | 确保调用了 `app.UseSentryTracing()` |
| 如何与 OpenTelemetry 共存？ | 安装 `Sentry.OpenTelemetry`，通过 OTel 桥接 |
| EF Core 查询没有追踪？ | 安装 `Sentry.EntityFramework` 并注册服务 |

---

## AI 使用建议

### 推荐工作流

1. **安装 SDK**：`dotnet add package Sentry.AspNetCore`（ASP.NET Core）或 `Sentry`（基础）
2. **配置 DSN**：在 `appsettings.json` 中设置 `Sentry:Dsn` 或环境变量 `SENTRY_DSN`
3. **启用追踪**：添加 `SentrySdk.Init()` + `app.UseSentryTracing()`
4. **自动采集**：ASP.NET Core、EF Core、HttpClient 等自动采集性能数据
5. **自定义事件**：`SentrySdk.CaptureMessage()` 或 `SentrySdk.CaptureException()`

### 关键注意事项

- **DSN 必填**：无 DSN 时 SDK 静默不工作，不会抛异常
- **性能追踪**：必须调用 `app.UseSentryTracing()`，否则无 Span 数据
- **采样率**：生产环境建议 `TracesSampleRate = 0.1`（10%），避免过多数据
- **隐私过滤**：用 `BeforeSend` 回调过滤敏感数据（PII、密码等）
- **自托管**：Docker 部署需配置 `SENTRY_SECRET_KEY` 和邮件服务

---

## 相关技能

- **furion** — .NET Web 框架：[../furion/SKILL.md](../furion/SKILL.md)
- **sqlsugar** — .NET ORM：[../sqlsugar/SKILL.md](../sqlsugar/SKILL.md)
- **dotnet-reactor** — .NET 代码保护：[../dotnet-reactor/SKILL.md](../dotnet-reactor/SKILL.md)

---

## 参考资源

- [Sentry .NET 文档](https://docs.sentry.io/platforms/dotnet/)
- [Sentry ASP.NET Core 指南](https://docs.sentry.io/platforms/dotnet/guides/aspnetcore/)
- [sentry-dotnet GitHub](https://github.com/getsentry/sentry-dotnet)
- [Sentry 自托管文档](https://docs.sentry.io/self-hosted/)
- [性能监控文档](https://docs.sentry.io/product/performance/)

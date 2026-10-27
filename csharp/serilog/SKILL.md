---
name: serilog
description: "Use when adding structured logging to .NET apps — Serilog.AspNetCore UseSerilogRequestLogging, LoggerConfiguration WriteTo.Console/File, appsettings.json ReadFrom.Configuration, DI via builder.Services.AddSerilog(), or diagnosing missing log output, duplicate ASP.NET Core request logs, and JSON log formatting. Serilog: structured diagnostic logging for .NET with message templates and sinks."
tags:
  - dotnet
  - csharp
  - logging
  - serilog
  - structured-logging
  - aspnet-core
  - observability
---

> **项目地址：** <https://github.com/serilog/serilog>
>
> **官方文档：** <https://serilog.net/>
>
> **NuGet：** `Serilog`（核心，4.4.0）；`Serilog.AspNetCore`（10.0.0，版本跟随 Microsoft.Extensions.Hosting）
>
> **常用配套包：** `Serilog.Sinks.Console` 6.1.1 / `Serilog.Sinks.File` 7.0.0 / `Serilog.Settings.Configuration` 10.0.1 / `Serilog.Formatting.Compact` 3.0.0（截至 2026-10，NuGet）
>
> **目标框架：** net8.0 / net9.0 / net10.0 / netstandard2.0 / .NET Framework 4.6.2+
>
> **许可证：** Apache-2.0

## 概述

Serilog 是 .NET 的结构化日志库：日志事件不是先拼成字符串，而是保留具名属性与值，再交给 sink 渲染成文本或 JSON。核心包 `Serilog` 只负责管道与事件模型，输出能力全部由 sink 包提供。

- **结构化事件**：消息模板 `"Processed {@Position} in {Elapsed} ms"` 记录 `Position` / `Elapsed` 两个属性
- **sink 可组合**：控制台、文件、Seq、OpenTelemetry、Elasticsearch 等都通过 `WriteTo.*` 挂载
- **配置驱动**：`ReadFrom.Configuration(IConfiguration)` 支持在 `appsettings.json` 中声明 sink 与级别
- **ASP.NET Core 一等公民**：`Serilog.AspNetCore` 把框架自身的 `ILogger` 输出接入 Serilog 管道，并提供单事件请求日志中间件
- **低开销**：级别关闭时几乎不产生分配（`Log.Logger` 的 `IsEnabled` 短路）

日志管道的两个关键概念：

| 概念 | 作用 | 典型 API |
|------|------|---------|
| Logger | 事件入口，决定最小级别与 enricher | `new LoggerConfiguration().MinimumLevel.Debug()` |
| Sink | 事件出口，决定写入哪里、什么格式 | `.WriteTo.Console()` / `.WriteTo.File(...)` |

---

## 安装

### 方式一：dotnet CLI（推荐）

```bash
# ASP.NET Core 项目：一个包带齐核心 + Console/File/Debug sink + 配置绑定
dotnet add package Serilog.AspNetCore

# 控制台 / Worker / 类库
dotnet add package Serilog
dotnet add package Serilog.Sinks.Console
dotnet add package Serilog.Sinks.File
```

### 方式二：PackageReference 直接写 csproj

```xml
<ItemGroup>
  <PackageReference Include="Serilog.AspNetCore" Version="10.0.0" />
  <PackageReference Include="Serilog.Sinks.Async" Version="2.1.0" />
  <PackageReference Include="Serilog.Enrichers.Environment" Version="3.0.1" />
</ItemGroup>
```

### 方式三：Visual Studio 包管理器控制台

```powershell
Install-Package Serilog.AspNetCore -Version 10.0.0
```

### 验证安装

```bash
dotnet list package | grep -i serilog
```

控制台最小可运行验证（不依赖任何宿主）：

```csharp
using Serilog;

using var log = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateLogger();

log.Information("Hello, Serilog!");
```

输出形如 `[12:01:43 INF] Hello, Serilog!` 即安装成功。

> 版本选择：`Serilog.AspNetCore` 的版本号跟随 `Microsoft.Extensions.Hosting`。.NET 8 项目用 8.x，.NET 9 用 9.x，.NET 10 用 10.x；跨大版本混用会在启动时报 `MissingMethodException`。

---

## 核心 API 速查

| 对象 / 方法 | 说明 |
|------------|------|
| `new LoggerConfiguration()` | 构建 `Logger` 的入口 |
| `.MinimumLevel.Information()` / `.MinimumLevel.Override(src, level)` | 全局级别与按 `SourceContext` 覆写 |
| `.Enrich.FromLogContext()` | 启用 `LogContext.PushProperty` 动态属性 |
| `.Enrich.WithMachineName()` | 机器名 enricher（需 `Serilog.Enrichers.Environment`） |
| `.WriteTo.Console()` / `.WriteTo.File(path)` | 控制台 / 文件 sink |
| `.WriteTo.Async(a => a.File(...))` | 异步包装 sink（需 `Serilog.Sinks.Async`） |
| `.ReadFrom.Configuration(config)` | 从 `IConfiguration` 读取 sink 与级别 |
| `.Destructure.ByTransforming<T>(...)` | 控制对象如何序列化为属性 |
| `Log.CloseAndFlush()` | 进程退出前冲刷缓冲，文件 sink 不丢日志 |
| `Serilog.Debugging.SelfLog.Enable(...)` | sink 自身报错时的诊断输出 |

### 消息模板与属性

```csharp
var position = new { Latitude = 25, Longitude = 134 };
log.Information("Processed {@Position} in {Elapsed} ms", position, 34);

// {@X} 解构对象为结构化属性；{X} 走 ToString()
// 属性名即字段名，后续可被 sink 以 JSON 字段写出
```

### 在 ASP.NET Core 中接入

```csharp
using Serilog;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .CreateLogger();

try
{
    Log.Information("Starting web application");

    var builder = WebApplication.CreateBuilder(args);
    builder.Services.AddSerilog();   // 让 ASP.NET Core 的 ILogger 走 Serilog

    var app = builder.Build();
    app.UseSerilogRequestLogging();  // 每个请求合并为一条日志
    app.MapGet("/", () => "Hello World!");
    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
```

`UseSerilogRequestLogging()` 必须放在 MVC / 端点映射**之前**：中间件只统计它之后的管道耗时，放晚了会漏掉处理逻辑。

### 从 appsettings.json 读取配置

```json
{
  "Serilog": {
    "Using": [ "Serilog.Sinks.Console", "Serilog.Sinks.File" ],
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft.AspNetCore": "Warning",
        "Microsoft.EntityFrameworkCore": "Warning"
      }
    },
    "WriteTo": [
      { "Name": "Console" },
      {
        "Name": "File",
        "Args": {
          "path": "logs/app-.log",
          "rollingInterval": "Day",
          "retainedFileCountLimit": 30,
          "outputTemplate": "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {SourceContext} {Message:lj}{NewLine}{Exception}"
        }
      }
    ],
    "Enrich": [ "FromLogContext", "WithMachineName", "WithThreadId" ]
  }
}
```

```csharp
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .CreateLogger();

builder.Services.AddSerilog();
```

`ReadFrom.Configuration` 要求 `Serilog.Settings.Configuration` 包；sink 名（`"Console"`、`"File"`）来自 `Using` 列表里声明的程序集，缺一个就会在启动时报 `Unable to find a method called "Console"`。

### 结构化属性与作用域

```csharp
using Serilog.Context;

public class OrderService(ILogger<OrderService> logger)
{
    public async Task HandleAsync(string orderId)
    {
        // 用 ILogger 写日志，属性同样进入 Serilog 事件
        using (LogContext.PushProperty("OrderId", orderId))
        {
            logger.LogInformation("Processing order {OrderId}", orderId);
            await Task.Delay(1);
            logger.LogWarning("Slow downstream call for {OrderId}", orderId);
        }
    }
}
```

### 文件滚动与 JSON 格式

```csharp
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console(new Serilog.Formatting.Compact.CompactJsonFormatter())
    .WriteTo.File(
        new Serilog.Formatting.Compact.CompactJsonFormatter(),
        "logs/app-.json",
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 14,
        fileSizeLimitBytes: 100 * 1024 * 1024,
        rollOnFileSizeLimit: true)
    .CreateLogger();
```

Compact JSON 每行一个对象，便于日志采集器（Loki / Filebeat / Vector）按行解析；文本模板适合人工看，两者可以同时挂。

### 异步与刷新

```csharp
Log.Logger = new LoggerConfiguration()
    .WriteTo.Async(a => a.File("logs/app-.log", rollingInterval: RollingInterval.Day),
                   bufferSize: 10000)
    .CreateLogger();

// 进程退出、崩溃处理、Worker 停止时都要冲刷
Log.CloseAndFlush();
```

异步 sink 会缓冲事件，**不调用 `CloseAndFlush()` 就退出会丢日志**，这是生产环境最常见的"日志末尾缺几条"的原因。

---

## 典型工作流

一个从零到可交付的接入流程：控制台验证 → ASP.NET Core 接入 → 配置文件化 → 落地校验。

### 输入

- 一个 ASP.NET Core 8/9/10 Web API 项目（示例 `src/MyApi`）
- 要求：请求日志一请求一条、本地控制台 + 按天滚动文件、生产接采集器

### 步骤

**1. 加包并跑通最小管道**

```bash
cd src/MyApi
dotnet add package Serilog.AspNetCore
```

```csharp
// Program.cs
using Serilog;

Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .WriteTo.Console()
    .CreateLogger();
```

**2. 接管宿主日志并开启请求日志**

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSerilog();

var app = builder.Build();
app.UseSerilogRequestLogging();
app.MapControllers();
app.Run();
```

此时 `dotnet run` 后访问任一接口，应只看到一条 `HTTP GET /path responded 200 in 12.3 ms`。

**3. 把配置搬进 appsettings**

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSerilog((services, lc) => lc
    .ReadFrom.Configuration(builder.Configuration)
    .ReadFrom.Services(services));

var app = builder.Build();
app.UseSerilogRequestLogging();
app.MapControllers();
app.Run();
```

配置文件见上一节；`ReadFrom.Services` 让 `IConfiguration` / `IHostEnvironment` 可注入到自定义 sink 与 enricher。

**4. 补齐退出冲刷与启动异常**

```csharp
try
{
    Log.Information("Starting web application");
    var app = builder.Build();
    app.UseSerilogRequestLogging();
    app.MapControllers();
    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
```

**5. 验证输出**

```bash
dotnet run --urls http://localhost:5080
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5080/api/health
tail -n 3 logs/app-*.log
```

### 输出

- 控制台与 `logs/app-<date>.log` 各出现一条请求日志，含路径、状态码、耗时
- 业务代码里的 `ILogger<T>` 输出与 Serilog 输出写往同一批 sink，级别一致
- 进程退出时文件 sink 已冲刷，日志末尾完整

---

## 最佳实践

1. **一个进程一个 `Log.Logger`**：用 `builder.Services.AddSerilog()` 统一，不要在 service 里各自 `new LoggerConfiguration()`
2. **用消息模板不用字符串插值**：`log.Information($"id={id}")` 会丢属性，永远写 `log.Information("id={Id}", id)`
3. **生产降噪**：`MinimumLevel.Override("Microsoft.AspNetCore", "Warning")`，否则框架自身的 Information 会淹没有效日志
4. **敏感字段不进日志**：解构对象时用 `Destructure.ByTransforming` 脱敏，或对属性名加黑名单
5. **启动/关闭用 try/finally**：`Log.CloseAndFlush()` 是文件 sink 不丢日志的前提
6. **sink 失败要可观测**：`SelfLog.Enable(Console.Error)` 能让磁盘写满、权限不足这类问题现形

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 加包后没有日志输出 | `Log.Logger` 未赋值，或只装了 `Serilog` 却没装 sink 包；检查 `WriteTo.*` 是否被调用 |
| 控制台重复输出两份 | `AddSerilog()` 之后仍保留默认 `Logging` 配置；删除 `appsettings.json` 的 `Logging` 节，或只保留一套 provider |
| 请求日志一条都没有 | `UseSerilogRequestLogging()` 放到了 `MapControllers()` 之后，或中间件管道里被短路 |
| 请求日志太多（一个请求多条） | 未启用 `UseSerilogRequestLogging()`，框架默认每个阶段各发一条 |
| 启动报 `Unable to find a method called "Console"` | `appsettings.json` 的 `Using` 未声明对应 sink 程序集，或包未安装 |
| 文件日志最后几条丢失 | 未调用 `Log.CloseAndFlush()`，或用了 `WriteTo.Async` 后直接 `Environment.Exit` |
| `Serilog.AspNetCore` 版本与 .NET 版本不匹配 | 该包版本跟随 `Microsoft.Extensions.Hosting`：.NET 8 用 8.x、.NET 9 用 9.x、.NET 10 用 10.x |
| `ILogger` 里的属性没进 JSON | 用了字符串插值而非消息模板；改成 `logger.LogInformation("...{Id}", id)` |
| 自定义 enricher 不生效 | 忘记 `.Enrich.With<T>()`，或 enricher 未在 `Using` 中声明 |
| 日志写入磁盘失败但程序不报错 | sink 异常默认被吞，开启 `SelfLog.Enable(Console.Error)` 后再查权限与磁盘空间 |

---

## AI 使用建议

- **执行环境**：命令在终端 / shell 中执行（Windows 用 PowerShell）；`dotnet add package` 首次需访问 NuGet，离线时先用本地缓存。
- **先探测版本**：`dotnet list package` 核对 `Serilog` 4.4.0 与 `Serilog.AspNetCore` 10.0.0；后者版本跟随 Microsoft.Extensions.Hosting，与核心包**不同号属正常**，不要强行对齐。
- **验证产物**：`dotnet run` 后确认控制台出现一条结构化日志，并检查 `appsettings.json` 的 `Serilog:Using` 与实际加载的 sink 包一致；若只看到内置 `Microsoft.Extensions.Logging` 的格式，说明 `UseSerilog()` 没生效。
- **常见误操**：同时调用 `builder.Host.UseSerilog()` 与 `builder.Logging.AddSerilog()` 会导致日志重复；`ReadFrom.Configuration` 需要在 csproj 里带上 `Serilog.Settings.Configuration`，否则配置被静默忽略。
- **安全与权限**：日志里不要输出连接串、口令与个人信息；`WriteTo.File` 会写磁盘，部署前确认路径可写与滚动策略。

---

## 相关技能

- **furion** — .NET Web 框架，生产项目常与 Serilog 一起替换默认日志：[../furion/SKILL.md](../furion/SKILL.md)
- **admin-net-backend** — Admin.NET 后端使用 log4net/Elasticsearch，迁移日志方案时对照本项目结构：[../admin-net-backend/SKILL.md](../admin-net-backend/SKILL.md)
- **sentry** — 错误追踪与性能监控，与 Serilog 组合做日志 + 异常双通道：[../sentry/SKILL.md](../sentry/SKILL.md)
- **hangfire** — 后台任务，任务内日志同样走 Serilog 管道：[../hangfire/SKILL.md](../hangfire/SKILL.md)
- **polly** — 弹性策略，重试/熔断事件适合用 Serilog 记录：[../polly/SKILL.md](../polly/SKILL.md)

---

## 相关资源

- 官网与文档：<https://serilog.net/>
- GitHub 仓库：<https://github.com/serilog/serilog>
- 消息模板规范：<https://messagetemplates.org>
- sink 列表：<https://github.com/serilog/serilog/wiki/Provided-Sinks>
- 配置参考：<https://github.com/serilog/serilog-settings-configuration>
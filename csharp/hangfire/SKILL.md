---
name: hangfire
description: "Use when running background jobs in .NET — fire-and-forget BackgroundJob.Enqueue, delayed Schedule, recurring Cron jobs via RecurringJob.AddOrUpdate, Hangfire.SqlServer/Hangfire.InMemory storage, or the Hangfire dashboard at /hangfire. Also for jobs stuck in 'Awaiting' state, dashboard returning 401/404 behind a proxy, and duplicate job execution in multi-instance deployments. Hangfire: background job processing for .NET."
tags:
  - dotnet
  - csharp
  - background-jobs
  - hangfire
  - scheduling
  - recurring-jobs
  - dashboard
---

> **项目地址：** <https://github.com/HangfireIO/Hangfire>
>
> **官方文档：** <https://docs.hangfire.io/>
>
> **NuGet：** `Hangfire.Core` 1.8.25（核心）、`Hangfire.AspNetCore` 1.8.25（ASP.NET Core 宿主）
>
> **存储/配套：** `Hangfire.SqlServer` 1.8.25、`Hangfire.PostgreSql` 1.21.1、`Hangfire.InMemory` 1.0.0、`Hangfire.Dashboard.BasicAuthorization` 1.0.2（截至 2026-10，NuGet）
>
> **目标框架：** netstandard2.0 / netcoreapp3.0+ / .NET Framework 4.5.1+（`Hangfire.Core` 为 netstandard2.0）
>
> **许可证：** LGPL-3.0

## 概述

Hangfire 把后台任务持久化到数据库（或内存/Redis），由独立的 worker 池拉取执行。任务在进程重启、部署滚动、机器宕机后仍会重试，这是它与 `Task.Run` / `IHostedService` 的本质区别。

- **三种任务形态**：fire-and-forget（`Enqueue`）、延迟（`Schedule`）、周期（`RecurringJob.AddOrUpdate` + Cron）
- **持久化存储**：SQL Server、PostgreSQL、MySQL、Redis、内存等，通过 `UseXxxStorage` 挂载
- **自动重试**：默认失败后按指数退避重试 10 次，可用 `[AutomaticRetry]` 覆盖
- **仪表盘**：`/hangfire` 可视化队列、重试、成功/失败任务与服务器心跳
- **任务链**：`ContinueJobWith` 串联依赖任务
- **多实例安全**：基于存储的分布式锁，多台服务器/多个容器共享同一存储时任务不会被重复执行

| 概念 | 说明 |
|------|------|
| Job | 一个待执行的方法调用（序列化后进存储） |
| Queue | 任务队列，默认 `default`，可自定义并用 `[Queue("name")]` 指定 |
| Server | 执行任务的进程角色，`AddHangfireServer()` 或 `UseHangfireServer()` 启动 |
| Storage | 任务与状态持久化位置，必须显式配置 |

---

## 安装

### 方式一：dotnet CLI

```bash
# ASP.NET Core 宿主：核心 + 宿主集成
dotnet add package Hangfire.AspNetCore

# 存储实现（任选一个）
dotnet add package Hangfire.SqlServer
dotnet add package Hangfire.PostgreSql

# 本地开发 / 单元测试用内存存储
dotnet add package Hangfire.InMemory
```

### 方式二：PackageReference

```xml
<ItemGroup>
  <PackageReference Include="Hangfire.AspNetCore" Version="1.8.25" />
  <PackageReference Include="Hangfire.SqlServer" Version="1.8.25" />
  <PackageReference Include="Hangfire.Dashboard.BasicAuthorization" Version="1.0.2" />
</ItemGroup>
```

### 方式三：包管理器控制台

```powershell
Install-Package Hangfire.AspNetCore -Version 1.8.25
Install-Package Hangfire.SqlServer -Version 1.8.25
```

### 验证安装

```bash
dotnet list package | grep -i hangfire
```

最小可运行验证（控制台，内存存储，无需数据库）：

```csharp
using Hangfire;
using Hangfire.InMemory;

GlobalConfiguration.Configuration.UseInMemoryStorage();

using var server = new BackgroundJobServer();

BackgroundJob.Enqueue(() => Console.WriteLine("job ran: {0}", DateTime.Now));
Console.ReadLine();
```

输出 `job ran: <时间>` 即安装与存储配置正确。

---

## 核心 API 速查

| 能力 | API | 说明 |
|------|-----|------|
| 即时任务 | `BackgroundJob.Enqueue(() => Method())` | 返回 job id |
| 延迟任务 | `BackgroundJob.Schedule(() => Method(), TimeSpan.FromMinutes(5))` | 也接受 `DateTimeOffset` |
| 周期任务 | `RecurringJob.AddOrUpdate("id", () => Method(), Cron.Daily)` | id 相同则覆盖，可重复调用 |
| 删除周期任务 | `RecurringJob.RemoveIfExists("id")` | 部署下线任务时用 |
| 手动触发 | `RecurringJob.TriggerJob("id")` | 不等下一个 Cron 点 |
| 删除/重排队 | `BackgroundJob.Delete(id)` / `BackgroundJob.Requeue(id)` | 运维常用 |
| 任务链 | `BackgroundJob.ContinueJobWith(parentId, () => Next())` | 父任务成功后执行 |
| 队列指定 | `[Queue("critical")]` + `BackgroundJob.Enqueue(...)` | 配合多 worker 分流 |
| 重试策略 | `[AutomaticRetry(Attempts = 3, OnAttemptsExceeded = AttemptsExceededAction.Fail)]` | 加在任务方法上 |

### 三种任务形态

```csharp
using Hangfire;

// 1. fire-and-forget：立即入队，异步执行
var jobId = BackgroundJob.Enqueue(() => Console.WriteLine("Hello, world!"));

// 2. delayed：延迟执行
BackgroundJob.Schedule(() => Console.WriteLine("5 分钟后"), TimeSpan.FromMinutes(5));

// 3. recurring：Cron 周期任务
RecurringJob.AddOrUpdate("sync-orders", () => SyncOrders(), Cron.Hourly);
RecurringJob.AddOrUpdate("daily-report", () => SendReport(), "0 8 * * *");
```

Cron 表达式使用标准 5 段格式（分 时 日 月 周），时区默认 UTC；需要本地时间时显式传 `TimeZoneInfo`：

```csharp
RecurringJob.AddOrUpdate("daily-report", () => SendReport(), "0 8 * * *",
    new RecurringJobOptions { TimeZone = TimeZoneInfo.FindSystemTimeZoneById("Asia/Shanghai") });
```

### ASP.NET Core 接线

```csharp
using Hangfire;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddHangfire(config => config
    .SetDataCompatibilityLevel(CompatibilityLevel.Version_180)
    .UseSimpleAssemblyNameTypeSerializer()
    .UseRecommendedSerializerSettings()
    .UseSqlServerStorage(builder.Configuration.GetConnectionString("Hangfire")));

// 在 Web 进程内跑 worker（小规模够用；也支持独立 Worker 服务）
builder.Services.AddHangfireServer();

var app = builder.Build();

app.UseHangfireDashboard();          // 默认路径 /hangfire
app.MapControllers();
app.Run();
```

### 仪表盘与授权

```csharp
app.UseHangfireDashboard("/jobs", new DashboardOptions
{
    DashboardTitle = "My Jobs",
    AppPath = "/",
    Authorization = new[] { new BasicAuthAuthorizationFilter(
        new BasicAuthAuthorizationFilterOptions
        {
            RequireSsl = true,
            SslRedirect = false,
            LoginCaseSensitive = true,
            Users = new[]
            {
                new BasicAuthAuthorizationUser
                {
                    Login = "admin",
                    PasswordClear = "change-me"
                }
            }
        }) }
});
```

`UseHangfireDashboard(pathMatch, options)` 的 `pathMatch` 默认 `/hangfire`。生产环境仪表盘**默认不鉴权**，不配置 `Authorization` 等于把任务与连接串暴露在公网。

### 任务参数与序列化

```csharp
// 参数必须可被 Newtonsoft.Json 序列化（Hangfire.Core 依赖 Newtonsoft.Json）
public class ReportService
{
    public void Build(int tenantId, DateTime from, DateTime to) { /* ... */ }
}

BackgroundJob.Enqueue<ReportService>(s => s.Build(42, DateTime.UtcNow.AddDays(-1), DateTime.UtcNow));
```

参数在入队时序列化、执行时反序列化，因此：

- 不要传 `CancellationToken`、`HttpContext`、`DbContext` 实例
- 自定义类型要能被 JSON 往返（构造函数/属性可写）
- 类型重命名或挪命名空间会让存量任务反序列化失败

### 重试与失败处理

```csharp
[AutomaticRetry(Attempts = 5, DelaysInSeconds = new[] { 10, 60, 300 },
                OnAttemptsExceeded = AttemptsExceededAction.Fail)]
public void CallWebhook(string url) { /* ... */ }
```

默认重试 10 次且指数退避；对不可恢复错误（参数非法、404）应设 `Attempts = 0` 直接失败，避免无意义重试占满队列。

### 多实例与队列分流

```csharp
builder.Services.AddHangfireServer(options =>
{
    options.WorkerCount = Environment.ProcessorCount * 2;
    options.Queues = new[] { "critical", "default" };   // 顺序即优先级
});
```

多台实例共享同一存储时无需额外协调：Hangfire 用存储层锁保证一个任务只被一台服务器取出。

---

## 典型工作流

场景：给一个多租户后台加"每天 8 点导出前一天的订单报表并发邮件"的周期任务，要求可观测、失败可重试、部署不重复。

### 输入

- ASP.NET Core 项目，SQL Server 已存在
- 已有 `ReportService.Build(tenantId, from, to)` 与 `MailService.Send(...)`

### 步骤

**1. 加包并配置存储**

```bash
dotnet add package Hangfire.AspNetCore
dotnet add package Hangfire.SqlServer
```

```csharp
builder.Services.AddHangfire(config => config
    .SetDataCompatibilityLevel(CompatibilityLevel.Version_180)
    .UseSimpleAssemblyNameTypeSerializer()
    .UseRecommendedSerializerSettings()
    .UseSqlServerStorage(builder.Configuration.GetConnectionString("Hangfire"),
        new SqlServerStorageOptions
        {
            CommandBatchMaxTimeout = TimeSpan.FromMinutes(5),
            SlidingInvisibilityTimeout = TimeSpan.FromMinutes(5),
            QueuePollInterval = TimeSpan.Zero,
            UseRecommendedIsolationLevel = true,
            DisableGlobalLocks = true
        }));

builder.Services.AddHangfireServer(options => options.WorkerCount = 10);
```

表结构由 `Hangfire.SqlServer` 自带脚本创建：启用 `PrepareSchemaIfNecessary = true`（默认）即可在首次启动自动建表。

**2. 定义任务并注册周期计划**

```csharp
public class DailyReportJob(ReportService reports, MailService mail)
{
    [AutomaticRetry(Attempts = 3)]
    [Queue("reports")]
    public async Task RunAsync()
    {
        var yesterday = DateTime.UtcNow.Date.AddDays(-1);
        foreach (var tenant in await reports.GetTenantIdsAsync())
        {
            await reports.BuildAsync(tenant, yesterday, yesterday.AddDays(1));
            await mail.SendAsync(tenant, "order-report", yesterday);
        }
    }
}

// 应用启动后注册（重复调用是幂等的）
app.Services.GetRequiredService<IRecurringJobManager>()
   .AddOrUpdate<DailyReportJob>("daily-order-report",
       job => job.RunAsync(),
       "0 8 * * *",
       new RecurringJobOptions
       {
           TimeZone = TimeZoneInfo.FindSystemTimeZoneById("Asia/Shanghai")
       });
```

或者在 `Program.cs` 直接用静态 `RecurringJob.AddOrUpdate`（需先初始化 `JobStorage.Current`）。用 `IRecurringJobManager` 更利于测试。

**3. 挂仪表盘并加鉴权**

```csharp
app.UseHangfireDashboard("/jobs", new DashboardOptions
{
    Authorization = new[] { new HangfireAuthorizationFilter() },
    StatsPollingInterval = 5000
});
```

**4. 验证**

```csharp
// 手动触发，不等 8 点（也可在 /jobs 的 Recurring 页点 Trigger now）
RecurringJob.TriggerJob("daily-order-report");
```

```bash
dotnet run
# 浏览器打开 http://localhost:5080/jobs，Recurring 页点 Trigger now，
# 再看 Jobs 页的任务状态与重试历史
```

### 输出

- `/jobs/recurring` 中出现 `daily-order-report`，下次执行时间按 `Asia/Shanghai` 8:00 计算
- 手动触发后面板 `Succeeded` 计数 +1；失败时按 3 次退避重试，最终进 `Failed` 并保留异常堆栈
- 多实例部署时同一时刻只有一个实例执行该任务

---

## 最佳实践

1. **任务方法必须幂等**：至少一次投递语义下，重试与超时重投都可能执行两次
2. **参数保持小而可序列化**：传 ID 不传实体图；`DbContext`/`HttpContext`/`CancellationToken` 一律不进参数
3. **存储与 Web 进程分离**：生产建议把 `AddHangfireServer()` 拆到独立 Worker 服务，Web 只入队
4. **仪表盘必须鉴权**：`DashboardOptions.Authorization` 显式配置，并放在内网或反向代理鉴权之后
5. **队列按优先级分流**：`options.Queues = new[] { "critical", "default" }`，关键任务用 `[Queue("critical")]`
6. **重试要有上限与告警**：`[AutomaticRetry(Attempts = 3)]` + 失败告警，防止坏任务长期占用队列
7. **周期任务 id 保持稳定**：id 是覆盖键，改名会留下旧任务继续跑

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 任务一直停在 `Enqueued` 不执行 | 没有启动 server：Web 里需 `AddHangfireServer()`，或独立进程 `new BackgroundJobServer()` |
| `/hangfire` 打开 404 | `UseHangfireDashboard()` 没调用，或与路由前缀冲突；检查 `pathMatch` 与实际访问路径 |
| 仪表盘 401 / 一直跳登录 | 反向代理未透传 Authorization 头，或 `RequireSsl` 与代理终止 TLS 不匹配 |
| 多实例下同一任务执行两次 | 各实例存储配置不一致（连了不同库），或有人在代码里绕过服务器手动执行 |
| 任务反序列化失败 / 方法找不到 | 任务方法或参数类型被重命名、挪命名空间、改签名；存量任务需清理或兼容处理 |
| 任务参数为 null | 参数不可 JSON 往返（只读属性、无无参构造、接口类型），改用简单类型或 DTO |
| 周期任务不触发 | Cron 时区按 UTC 解释；需要本地时间显式传 `RecurringJobOptions.TimeZone` |
| 数据库表不存在 | `PrepareSchemaIfNecessary` 被关，或账号无建表权限；手工执行 `Hangfire.SqlServer` 附带脚本 |
| 部署后任务重复灌入 | `RecurringJob.AddOrUpdate` 幂等没问题，但若用 `AddOrUpdate` + 随机 id 会不断新增 |
| 想按队列隔离 worker | `AddHangfireServer(o => o.Queues = ...)` 配多组服务器，或拆分独立 Worker |

---

## 相关技能

- **serilog** — 任务内日志与失败告警统一走结构化日志：[../serilog/SKILL.md](../serilog/SKILL.md)
- **polly** — 任务内部的瞬时故障重试（与 Hangfire 的任务级重试分工不同）：[../polly/SKILL.md](../polly/SKILL.md)
- **sqlsugar** — 任务体内常用 ORM，注意作用域与连接管理：[../sqlsugar/SKILL.md](../sqlsugar/SKILL.md)
- **furion** — .NET Web 框架，`Furion.Schedule` 与 Hangfire 的功能重叠与选型：[../furion/SKILL.md](../furion/SKILL.md)
- **sentry** — 后台任务异常上报与性能追踪：[../sentry/SKILL.md](../sentry/SKILL.md)

---

## 相关资源

- 官方文档：<https://docs.hangfire.io/>
- GitHub 仓库：<https://github.com/HangfireIO/Hangfire>
- 官方站点：<https://www.hangfire.io>
- Cron 表达式速查：<https://crontab.guru/>

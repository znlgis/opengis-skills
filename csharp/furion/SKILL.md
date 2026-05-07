---
name: furion
description: Furion 是基于 .NET 的开源企业级 Web 框架，强调极简 API、约定优先与零配置启动，集成动态 API、规范化结果、依赖注入、SqlSugar/EFCore、JWT 鉴权、远程请求、定时任务、事件总线等模块，是国内 .NET 生态最流行的脚手架之一。
tags: dotnet, webapi, framework, dynamic-api, jwt
---

> **项目地址：** <https://gitee.com/dotnetchina/Furion>
>
> **GitHub 镜像：** <https://github.com/MonkSoul/Furion>
>
> **官方文档：** <https://furion.net/>
>
> **NuGet：** `Furion`、`Furion.Pure`
>
> **许可证：** MIT

## 概述

Furion 主要特性：

- **零配置启动**：`Inject()` + `AddInject()` 自动激活
- **动态 API**：实现 `IDynamicApiController` → 自动暴露 RESTful 接口
- **规范化结果**：统一 `RESTfulResult<T>` 响应
- **依赖注入**：`ITransient/IScoped/ISingleton` 标记接口自动注册
- **数据库**：内置 SqlSugar 与 EF Core 双方案
- **鉴权**：`[Authorize]` + JWT + 策略
- **远程请求**：`IHttpRemote` + `[HttpRequest]` 配置式
- **定时任务**：`Furion.Schedule`（基于 Quartz 类似的语法）
- **事件总线**：本地 + RabbitMQ
- **配置**：`App.GetConfig`、`Config<TOptions>`

> Furion 适合 Admin.NET、企业内部系统、微服务后端。

---

## 安装

```bash
dotnet add package Furion
# 或基础版（不含全部子包）
dotnet add package Furion.Pure
```

---

## 启动配置

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args).Inject();   // 关键

builder.Services.AddControllers().AddInject();               // 关键

var app = builder.Build();
app.UseInject();                                             // 关键
app.MapControllers();
app.Run();
```

`Inject()` 会扫描程序集自动加载 Furion 的「应用启动模块」（`AppStartup`）。

---

## 动态 API

```csharp
public class HelloService : IDynamicApiController
{
    public string Get() => "Hello Furion";
    public int Add(int a, int b) => a + b;
    public Task<List<User>> List() => /* ... */;
}
```

启动后自动暴露：

- `GET  /api/hello/get`
- `POST /api/hello/add`
- `GET  /api/hello/list`

可用 `[ApiDescriptionSettings]`、`[HttpGet]` 等控制路由。

---

## 规范化响应

默认所有接口返回：

```json
{
  "statusCode": 200,
  "succeeded": true,
  "data": { ... },
  "errors": null,
  "extras": null,
  "timestamp": 1700000000
}
```

异常自动包装为：

```json
{ "statusCode": 500, "succeeded": false, "errors": "ex.Message" }
```

可通过 `App.Configuration["SpecificationDocumentSettings:..."]` 关闭或自定义。

---

## 依赖注入

```csharp
public interface IUserService { User GetById(int id); }

public class UserService : IUserService, ITransient
{
    public User GetById(int id) => /* ... */;
}

// 直接构造函数注入即可，无需 services.AddTransient<...>()
public class HelloService(IUserService userSvc) : IDynamicApiController { ... }
```

`ITransient` / `IScoped` / `ISingleton` 三选一作为标记接口。

---

## 数据库（SqlSugar 集成）

```bash
dotnet add package Furion.Extras.DatabaseAccessor.SqlSugar
```

```json
{
  "DbConnectionString": "server=.;database=demo;uid=sa;pwd=...;TrustServerCertificate=true"
}
```

```csharp
builder.Services.AddSqlSugar(new ConnectionConfig {
    ConnectionString = App.Configuration["DbConnectionString"],
    DbType = DbType.SqlServer,
    IsAutoCloseConnection = true
});

public class UserService(ISqlSugarClient db) : IDynamicApiController
{
    public List<User> List() => db.Queryable<User>().ToList();
}
```

EF Core 走 `Furion.DatabaseAccessor`：

```csharp
public class MyDbContext : AppDbContext<MyDbContext> { ... }

builder.Services.AddDatabaseAccessor(opt => {
    opt.AddDbPool<MyDbContext>(DbProvider.SqlServer);
}, "Furion.Database.Migrations");
```

---

## JWT 鉴权

```json
"JWTSettings": {
  "ValidateIssuer": true,
  "ValidateAudience": true,
  "ValidateLifetime": true,
  "ValidIssuer": "Furion",
  "ValidAudience": "Furion",
  "IssuerSigningKey": "Wts3hE2mp..."
}
```

```csharp
builder.Services.AddJwt<JwtHandler>();   // 自定义 IAuthorizationHandler
```

```csharp
[Authorize]
public class OrderService : IDynamicApiController { ... }
```

登录返回：

```csharp
var token = JWTEncryption.Encrypt(new Dictionary<string, object> {
    { "UserId", 1 }, { "Account", "admin" }
});
```

---

## 远程请求（IHttpRemote）

```csharp
public interface IGithub : IHttpDispatchProxy
{
    [Get("https://api.github.com/users/{user}")]
    Task<GithubUser> GetUserAsync([Path] string user);
}

builder.Services.AddRemoteRequest(opt => opt.AddHttpProxy<IGithub>());

// 注入即用
public class HelloService(IGithub gh) : IDynamicApiController
{
    public Task<GithubUser> User(string user) => gh.GetUserAsync(user);
}
```

---

## 定时任务（Furion.Schedule）

```csharp
[JobDetail("job1", Description = "每分钟一次")]
[PeriodSeconds(60, TriggerId = "trigger1")]
public class HelloJob : IJob
{
    public Task ExecuteAsync(JobExecutingContext context, CancellationToken ct)
        => Console.Out.WriteLineAsync("hello " + DateTime.Now);
}

builder.Services.AddSchedule(opt => opt.AddJob<HelloJob>());
```

---

## 事件总线

```csharp
public class OrderCreatedEventSubscriber : IEventSubscriber
{
    [EventSubscribe("order:created")]
    public Task OnOrderCreated(EventHandlerExecutingContext ctx)
    {
        var order = ctx.Source.Payload as Order;
        return Task.CompletedTask;
    }
}

builder.Services.AddEventBus(opt =>
    opt.AddSubscriber<OrderCreatedEventSubscriber>());

// 触发
await eventPublisher.PublishAsync("order:created", new Order { Id = 1 });
```

---

## 配置访问

```csharp
var dbCs = App.Configuration["DbConnectionString"];

[Configuration]
public class JwtSettings { public string ValidIssuer { get; set; } = ""; }

var jwt = App.GetConfig<JwtSettings>("JWTSettings");
```

---

## AI 使用建议

### 推荐工作流

1. **快速起步**：`dotnet new webapi` → 添加 Furion 包 → `builder.Services.AddControllers().AddInject()` → `app.UseInject()`
2. **定义服务**：实现 `IDynamicApiController` + 标记接口（`ITransient`/`IScoped`/`ISingleton`）→ 接口自动暴露
3. **配置数据库**：二选一 — SqlSugar（`AddSqlSugar`）或 EF Core（`AddDatabaseAccessor`）
4. **鉴权**：配置 `JWTSettings` + `AddJwt<JwtHandler>()` + `[Authorize]`
5. **扩展**：远程请求用 `IHttpDispatchProxy`，定时任务用 `IJob`，事件总线用 `IEventSubscriber`

### 关键模式与常见陷阱

- **`Inject()` 三步走**：`builder.Inject()` → `builder.Services.AddControllers().AddInject()` → `app.UseInject()`，缺一不可
- **动态 API 命名**：方法名决定 HTTP 动词（`Get`/`Post`/`Add`/`Update`/`Delete`/`Page`），不匹配时用 `[HttpPost]` 覆盖
- **DI 标记接口**：`ITransient`/`IScoped`/`ISingleton` 三选一，Abstract 类不生效
- **规范化响应**：所有接口默认包装为 `{statusCode, succeeded, data, errors}`，可通过配置关闭
- **Swagger 不显示**：检查 `app.UseInject()` 是否正确调用，以及 `SpecificationDocumentSettings` 分组配置

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 快速构建单体 API | Furion 动态 API |
| 已有大型项目渐进迁移 | 仅用 Furion 的 DI/配置/事件总线 |
| 微服务架构 | Furion + 自建网关 |
| 前后端分离后台 | Furion（后端）+ Admin.NET 前端模板 |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 接口未暴露 | 服务实现 `IDynamicApiController` 并 `AddInject()` |
| Swagger 不显示 | 启用 `app.UseInject()`；检查 `SpecificationDocumentSettings.GroupOpenApiInfos` |
| DI 不生效 | 实现类需带 `ITransient/IScoped/ISingleton` 之一 |
| 单元测试 | 使用 `Furion.UnitTesting` 包，或调用 `App.Initialize()` |
| `App` 未初始化 | 异步入口需 `Inject()` 完成后 |

---

## 相关技能

- **sqlsugar** — Furion 默认推荐的 ORM，提供链式查询与多数据库支持：[../sqlsugar/SKILL.md](../sqlsugar/SKILL.md)
- **admin-net-backend** — 基于 Furion + SqlSugar 的完整后台框架，适合直接生成项目：[../admin-net-backend/SKILL.md](../admin-net-backend/SKILL.md)

---

## 参考资源

- 官网：<https://furion.net/>
- 仓库：<https://gitee.com/dotnetchina/Furion>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/tutorial/furion/>
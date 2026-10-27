---
name: polly
description: "Use when adding retry, timeout, circuit-breaker, rate-limit or fallback resilience to .NET HTTP/database calls — ResiliencePipelineBuilder AddRetry/AddTimeout/AddCircuitBreaker, Polly 8 ResiliencePipeline, Microsoft.Extensions.Http.Resilience AddStandardResilienceHandler, or fixing TimeoutRejectedException, retries multiplying load, and 'The circuit is now open'. Polly: .NET resilience and transient-fault-handling library."
tags:
  - dotnet
  - csharp
  - resilience
  - polly
  - retry
  - circuit-breaker
  - httpclient
  - reliability
---

> **项目地址：** <https://github.com/App-vNext/Polly>
>
> **官方文档：** <https://www.pollydocs.org/>
>
> **NuGet：** `Polly.Core` 8.8.1（v8 管道与策略）、`Polly.Extensions` 8.8.1（DI 注册 + 遥测）、`Polly.RateLimiting` 8.8.1（限流策略）、`Polly` 8.8.1（仅承载 v7 旧 API）
>
> **配套：** `Microsoft.Extensions.Http.Resilience` 10.11.0（`IHttpClientFactory` 标准弹性 handler，版本跟随 Microsoft.Extensions.*）
>
> **目标框架：** net8.0 / net6.0 / netstandard2.0 / .NET Framework 4.6.2+
>
> **许可证：** BSD-3-Clause

## 概述

Polly 是 .NET 的弹性与瞬时故障处理库。v8 起以 **ResiliencePipeline** 为核心：把若干策略（retry / timeout / circuit breaker / rate limiter / hedging / fallback）组合成一条管道，业务代码只负责把委托交给管道执行。

- **策略组合**：`AddRetry`、`AddTimeout`、`AddCircuitBreaker` 可链式叠加，顺序即执行顺序（外层先执行）
- **同步/异步统一**：`Execute` / `ExecuteAsync`，异步重载接收 `CancellationToken`
- **结果型重试**：`ShouldHandle = PredicateBuilder.HandleResult(...)` 能对 `HttpResponseMessage` 等返回值判定，而不只是异常
- **DI 原生支持**：`AddResiliencePipeline(name, builder => ...)` 注册命名管道，`ResiliencePipelineProvider<string>` 按名解析
- **可观测**：`Polly.Extensions` 提供 Telemetry（日志 + 指标），与 OpenTelemetry 打通

v7 的 `Policy.Handle<...>().Retry(...)` 写法**仍可用但不推荐**：它们只存在于 `Polly` 包中，v8 新能力（hedging、结果型管道、DI 管道、遥测）都不会覆盖旧 API。

| 包 | 内容 | 什么时候用 |
|----|------|-----------|
| `Polly.Core` | `ResiliencePipelineBuilder`、retry / timeout / circuit-breaker / fallback / hedging 策略 | 新代码默认选它 |
| `Polly.Extensions` | `AddResiliencePipeline(...)`、`ConfigureTelemetry(...)`、DI 与遥测 | 需要在 `IServiceCollection` 里配管道 |
| `Polly.RateLimiting` | `AddRateLimiter(...)` / `RateLimiterStrategyOptions` | 需要限流策略时单独安装（不在 `Polly.Core` 里） |
| `Polly` | v7 旧 API：`Policy` / `AsyncPolicy` / `BrokenCircuitException` | 只在维护既有 v7 代码时 |
| `Microsoft.Extensions.Http.Resilience` | `AddStandardResilienceHandler` 等 HTTP 专用 handler | 用 `IHttpClientFactory` 调外部 HTTP |

---

## 安装

### 方式一：dotnet CLI

```bash
# 只用管道本体
dotnet add package Polly.Core

# 需要 DI 注册 / 遥测
dotnet add package Polly.Extensions

# 需要限流策略（独立包）
dotnet add package Polly.RateLimiting

# 维护 v7 旧代码
dotnet add package Polly

# HttpClient 标准弹性（含重试/熔断/超时/限流）
dotnet add package Microsoft.Extensions.Http.Resilience
```

### 方式二：PackageReference

```xml
<ItemGroup>
  <PackageReference Include="Polly.Core" Version="8.8.1" />
  <PackageReference Include="Polly.Extensions" Version="8.8.1" />
  <PackageReference Include="Microsoft.Extensions.Http.Resilience" Version="10.11.0" />
</ItemGroup>
```

### 验证安装

```bash
dotnet list package | grep -i polly
```

最小可运行验证：

```csharp
using Polly;

var pipeline = new ResiliencePipelineBuilder()
    .AddRetry(new RetryStrategyOptions { MaxRetryAttempts = 2 })
    .AddTimeout(TimeSpan.FromSeconds(5))
    .Build();

int attempt = 0;
var result = await pipeline.ExecuteAsync(async token =>
{
    attempt++;
    if (attempt < 3) throw new HttpRequestException("transient");
    return "ok";
});
Console.WriteLine($"result={result} attempts={attempt}");   // result=ok attempts=3
```

---

## 核心 API 速查

| 策略 | 构建方法 | 关键选项 |
|------|---------|---------|
| 重试 | `AddRetry(new RetryStrategyOptions { ... })` | `MaxRetryAttempts`、`Delay`、`BackoffType`、`UseJitter`、`ShouldHandle` |
| 超时 | `AddTimeout(TimeSpan)` / `AddTimeout(new TimeoutStrategyOptions)` | `TimeoutGenerator`、`OnTimeout` |
| 熔断 | `AddCircuitBreaker(new CircuitBreakerStrategyOptions { ... })` | `FailureRatio`、`MinimumThroughput`、`SamplingDuration`、`BreakDuration` |
| 限流 | `AddRateLimiter(new RateLimiterStrategyOptions { ... })` | 需 `Polly.RateLimiting` 包；`DefaultRateLimiterOptions`、`OnRejected` |
| 对冲 | `AddHedging(new HedgingStrategyOptions<T> { ... })` | `MaxHedgedAttempts`、`Delay`、`ActionGenerator` |
| 降级 | `AddFallback(new FallbackStrategyOptions<T> { ... })` | `ShouldHandle`、`FallbackAction` |
| 管道执行 | `Execute` / `ExecuteAsync` | 委托接收 `CancellationToken` |

### 重试：指数退避 + 抖动

```csharp
using Polly;
using Polly.Retry;

var pipeline = new ResiliencePipelineBuilder()
    .AddRetry(new RetryStrategyOptions
    {
        ShouldHandle = new PredicateBuilder()
            .Handle<HttpRequestException>()
            .Handle<TimeoutRejectedException>(),
        MaxRetryAttempts = 4,
        BackoffType = DelayBackoffType.Exponential,
        UseJitter = true,                    // 避免重试风暴同步
        Delay = TimeSpan.FromSeconds(1),
        OnRetry = args =>
        {
            Console.WriteLine($"retry #{args.AttemptNumber} after {args.RetryDelay}");
            return default;
        }
    })
    .Build();

await pipeline.ExecuteAsync(async token => await httpClient.GetAsync("https://api.example.com/health", token), ct);
```

`MaxRetryAttempts = 4` 表示**额外重试 4 次**（总共最多 5 次调用），这是最常见的 off-by-one 误解。

### 超时：必须传 CancellationToken

```csharp
var pipeline = new ResiliencePipelineBuilder()
    .AddTimeout(new TimeoutStrategyOptions
    {
        Timeout = TimeSpan.FromSeconds(3),
        OnTimeout = args =>
        {
            Console.WriteLine($"{args.Context.OperationKey} timed out after {args.Timeout}");
            return default;
        }
    })
    .Build();

// 委托必须接收并使用 token，否则超时无法中断底层调用
await pipeline.ExecuteAsync(async token => await db.QueryAsync(sql, token), ct);
```

超时策略靠协作式取消生效：委托里不把 token 传给下游，`AddTimeout` 到点只会抛出 `TimeoutRejectedException`，而不会真正终止正在跑的 IO。

### 熔断：失败率触发

```csharp
using Polly.CircuitBreaker;

var pipeline = new ResiliencePipelineBuilder()
    .AddRetry(new RetryStrategyOptions { MaxRetryAttempts = 2 })
    .AddCircuitBreaker(new CircuitBreakerStrategyOptions
    {
        FailureRatio = 0.5,
        MinimumThroughput = 10,
        SamplingDuration = TimeSpan.FromSeconds(30),
        BreakDuration = TimeSpan.FromSeconds(15),
        ShouldHandle = new PredicateBuilder().Handle<HttpRequestException>(),
        OnOpened = args =>
        {
            Console.WriteLine($"circuit opened for {args.BreakDuration}");
            return default;
        }
    })
    .Build();
```

熔断器统计的是"最近 `SamplingDuration` 内至少 `MinimumThroughput` 次调用"的失败比例；熔断打开期间所有执行被快速拒绝，抛 `ExecutionRejectedException` 的派生异常，不再打下游。注意 `BrokenCircuitException` 只存在于 v7 的 `Polly` 包，`Polly.Core`（v8）里没有这个类型。

### 限流

```csharp
// 需额外安装 Polly.RateLimiting，它不在 Polly.Core 中
using Polly.RateLimiting;

var pipeline = new ResiliencePipelineBuilder()
    .AddRateLimiter(new RateLimiterStrategyOptions
    {
        DefaultRateLimiterOptions = new ConcurrencyLimiterOptions
        {
            PermitLimit = 20,
            QueueLimit = 100,
            QueueProcessingOrder = QueueProcessingOrder.OldestFirst
        }
    })
    .Build();
```

### 在 DI 中注册命名管道

```csharp
builder.Services.AddResiliencePipeline("orders-api", (pipelineBuilder, context) =>
{
    pipelineBuilder
        .AddRetry(new RetryStrategyOptions { MaxRetryAttempts = 3, Delay = TimeSpan.FromMilliseconds(300) })
        .AddTimeout(TimeSpan.FromSeconds(10));
});

public class OrderClient(ResiliencePipelineProvider<string> pipelines)
{
    public Task<string> GetAsync(CancellationToken ct)
    {
        var pipeline = pipelines.GetPipeline("orders-api");
        return pipeline.ExecuteAsync(async token => await Fetch(token), ct).AsTask();
    }
}
```

### HttpClient 标准弹性

```csharp
builder.Services.AddHttpClient("inventory")
    .AddStandardResilienceHandler();   // 重试 + 熔断 + 总超时 + 尝试超时，内置合理默认值

// 需要覆盖默认值时
builder.Services.AddHttpClient("inventory")
    .AddStandardResilienceHandler(options =>
    {
        options.Retry.MaxRetryAttempts = 3;
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(5);
        options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(20);
    });
```

`AddStandardResilienceHandler` 来自 `Microsoft.Extensions.Http.Resilience`，与 `Polly.Core` 的管道是同一套引擎，只是把 HTTP 场景的默认参数和指标埋点打好了。

---

## 典型工作流

场景：给一个调用第三方支付网关的 ASP.NET Core API 加上弹性保护，要求"抖动不重试、超时快速失败、持续故障时熔断不再打下游，并能在日志里看见"。

### 输入

- 现有 `HttpClient` 直连支付网关，偶发 `HttpRequestException` 与 504
- 目标：瞬时故障自动恢复；下游长时间不可用时保护自己

### 步骤

**1. 加包**

```bash
dotnet add package Polly.Core
dotnet add package Polly.Extensions
```

**2. 定义管道（重试在内层，熔断在外层）**

顺序很关键：`AddRetry(...).AddCircuitBreaker(...)` 表示熔断包住重试，即"重试耗尽仍失败 = 熔断器记一次失败"；反过来会让每次重试都独立参与熔断统计。

```csharp
builder.Services.AddResiliencePipeline("pay-gateway", pipelineBuilder =>
{
    pipelineBuilder
        .AddRetry(new RetryStrategyOptions
        {
            ShouldHandle = new PredicateBuilder()
                .Handle<HttpRequestException>()
                .HandleResult<HttpResponseMessage>(r => (int)r.StatusCode >= 500),
            MaxRetryAttempts = 3,
            BackoffType = DelayBackoffType.Exponential,
            UseJitter = true,
            Delay = TimeSpan.FromMilliseconds(200)
        })
        .AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            MinimumThroughput = 8,
            SamplingDuration = TimeSpan.FromSeconds(30),
            BreakDuration = TimeSpan.FromSeconds(20)
        })
        .AddTimeout(TimeSpan.FromSeconds(15));
});
```

**3. 业务侧经管道调用**

```csharp
public class PayGatewayClient(
    HttpClient http,
    ResiliencePipelineProvider<string> pipelines,
    ILogger<PayGatewayClient> logger)
{
    public async Task<string> ChargeAsync(string payload, CancellationToken ct)
    {
        var pipeline = pipelines.GetPipeline("pay-gateway");
        try
        {
            var response = await pipeline.ExecuteAsync(
                async token => await http.PostAsync("/charge", new StringContent(payload), token), ct);
            return await response.Content.ReadAsStringAsync(ct);
        }
        catch (ExecutionRejectedException ex)
        {
            // v8：熔断/限流/超时被拒绝时抛 ExecutionRejectedException 及其子类
            logger.LogWarning(ex, "pay gateway rejected by pipeline, falling back to queue");
            throw new InvalidOperationException("gateway unavailable, retry later", ex);
        }
    }
}
```

**4. 打开遥测确认策略命中**

```csharp
builder.Services.AddResiliencePipeline("pay-gateway", (pipelineBuilder, context) =>
{
    pipelineBuilder.AddRetry(new RetryStrategyOptions { MaxRetryAttempts = 3 });
    pipelineBuilder.ConfigureTelemetry(context.ServiceProvider.GetRequiredService<ILoggerFactory>());
});
```

Telemetry 会输出 `Resilience event occurred. EventName: 'OnRetry'` 这类结构化日志，可直接被 Serilog / OpenTelemetry 采集。

**5. 验证**

```bash
# 用一个会间歇 500 的假下游验证重试与熔断
dotnet run --project src/MyApi
for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code} " http://localhost:5080/api/pay/charge; done; echo
```

### 输出

- 偶发失败：日志出现 `OnRetry` 事件，请求最终成功
- 持续故障：`MinimumThroughput` 内的失败率达到阈值后熔断打开，后续请求快速失败（`ExecutionRejectedException`），20 秒后自动半开试探
- 全程每个请求有总耗时上限（15 秒），不会无限挂起

---

## 最佳实践

1. **只对瞬态故障重试**：4xx、参数错误、幂等性不确定的写操作不该重试；用 `ShouldHandle` 精确限定
2. **重试必须退避 + 抖动**：`BackoffType.Exponential` + `UseJitter = true`，否则多实例会同时重试放大下游压力
3. **重试次数 ≤ 3~4**：重试是延迟而非修复，次数越多对下游越不友好
4. **超时必须把 token 传到底**：委托签名带 `CancellationToken` 并一路透传给 `HttpClient` / EF Core / Dapper
5. **熔断放外层、重试放内层**：让熔断统计的是"一次完整业务调用"的成败
6. **熔断打开要有降级路径**：捕获 `ExecutionRejectedException` 走缓存、队列或明确错误，而不是 500 直接冒泡
7. **v7 迁移到 v8**：`Policy.Handle<>().WaitAndRetryAsync(...)` → `ResiliencePipelineBuilder().AddRetry(...)`；`ExecuteAsync` 的返回类型从 `Task<T>` 变成 `ValueTask<T>`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 重试次数比预期多一次 | `MaxRetryAttempts` 是"额外重试次数"，总调用数 = 1 + 该值 |
| 超时设置后请求仍不中断 | 委托没有接收/使用 `CancellationToken`，或底层 API 不支持取消；超时策略只能协作式取消 |
| 一直抛 `ExecutionRejectedException` | 熔断已打开，等 `BreakDuration` 后自动半开；或检查 `FailureRatio`/`MinimumThroughput` 是否过于敏感 |
| 编译报找不到 `BrokenCircuitException` | 该类型只在 v7 的 `Polly` 包；用 v8 管道时改为捕获 `ExecutionRejectedException` |
| 熔断一直不打开 | `MinimumThroughput` 没达到（采样窗口内调用量不足），或 `ShouldHandle` 没覆盖实际抛出的异常类型 |
| 升级到 v8 后编译报找不到 `Policy` | 只装了 `Polly.Core`；v7 旧 API 在 `Polly` 包里，要么换新 API，要么补装 `Polly` |
| `AddResiliencePipeline` 找不到 | 缺 `Polly.Extensions` 包，命名管道与 DI 集成不在 `Polly.Core` 中 |
| `ValueTask` 不能直接 await 两次 | v8 的 `ExecuteAsync` 返回 `ValueTask<T>`，需要 await 两次时先 `.AsTask()` |
| 重试对象是 `HttpResponseMessage` 但没触发 | 用了 `RetryStrategyOptions` 而非 `RetryStrategyOptions<HttpResponseMessage>`，结果判定必须带泛型 |
| `Microsoft.Extensions.Http.Resilience` 版本冲突 | 该包版本跟随 `Microsoft.Extensions.*`（.NET 10 用 10.x），与项目 TFM 对齐 |
| 管道里超时和重试谁耗时更长 | 顺序决定语义：`AddTimeout` 在外层就是"总时长上限"，在内层就是"单次尝试上限" |

---

## 相关技能

- **serilog** — 结构化日志，记录重试/熔断事件与降级路径：[../serilog/SKILL.md](../serilog/SKILL.md)
- **sentry** — 错误追踪，熔断与最终失败可作为异常上报观测：[../sentry/SKILL.md](../sentry/SKILL.md)
- **furion** — .NET Web 框架，结合 `IHttpRemote` 远程请求配置弹性：[../furion/SKILL.md](../furion/SKILL.md)
- **hangfire** — 后台任务重试与延迟调度（Hangfire 自带 `AutomaticRetry`，与 Polly 的分工要分清）：[../hangfire/SKILL.md](../hangfire/SKILL.md)
- **admin-net-backend** — 企业后台常见的外部依赖（支付/短信/OSS）是弹性策略的主要落点：[../admin-net-backend/SKILL.md](../admin-net-backend/SKILL.md)

---

## 相关资源

- 官方文档：<https://www.pollydocs.org/>
- GitHub 仓库：<https://github.com/App-vNext/Polly>
- v7 旧版文档（分支 7.2.4）：<https://github.com/App-vNext/Polly/tree/7.2.4>
- HTTP 弹性：<https://learn.microsoft.com/dotnet/core/resilience/http-resilience>

---
name: sqlsugar
description: SqlSugar 是国产开源高性能 .NET ORM，支持 SQL Server / MySQL / Oracle / PostgreSQL / SQLite / 达梦 / 人大金仓 / 神通 / OceanBase 等近 20 种数据库，提供链式 LINQ-like 查询、Code First、读写分离、分库分表、事务、主键雪花算法、AOT 等丰富特性，是 Furion / Admin.NET 等框架默认 ORM。
---

> **项目地址：** <https://github.com/DotNetNext/SqlSugar>
>
> **官方文档：** <https://www.donet5.com/Home/Doc>
>
> **NuGet：** `SqlSugar` / `SqlSugarCore`
>
> **许可证：** Apache-2.0

## 概述

SqlSugar 主要特性：

- **多数据库**：SQL Server / MySQL / Oracle / PostgreSQL / SQLite / 达梦 / 人大金仓 / 神舟通用 / GBase / Highgo / Oscar / Tdengine / ClickHouse / OceanBase / MariaDB / Access / 行云数据库
- **Code First / DB First** 双模式
- **链式查询**：`Queryable<T>().Where(...).Select(...).ToList()`
- **Lambda 表达式 → SQL**
- **批量操作**：`Insertable / Updateable / Deletable.ExecuteCommand()`
- **多种主键策略**：自增、Guid、雪花 ID
- **读写分离 / 分库分表**
- **AOT 友好**（高级版）
- **事务**：`UseTran` 自动管理

---

## 安装

```bash
dotnet add package SqlSugarCore     # .NET 6+
# 或
dotnet add package SqlSugar         # .NET Framework
```

---

## 创建客户端

```csharp
using SqlSugar;

var db = new SqlSugarClient(new ConnectionConfig {
    DbType = DbType.MySql,
    ConnectionString = "server=127.0.0.1;uid=root;pwd=...;database=demo",
    IsAutoCloseConnection = true,
    InitKeyType = InitKeyType.Attribute   // 通过特性识别主键
});

db.Aop.OnLogExecuting = (sql, p) => Console.WriteLine(sql);
```

> 多数据库：使用 `SqlSugarClient(List<ConnectionConfig>)` 或 `SqlSugarScope`（推荐 DI 注入）。

### 在 ASP.NET Core 中注册

```csharp
builder.Services.AddSingleton<ISqlSugarClient>(sp =>
    new SqlSugarScope(new ConnectionConfig {
        DbType = DbType.SqlServer,
        ConnectionString = builder.Configuration.GetConnectionString("Default"),
        IsAutoCloseConnection = true
    }));
```

---

## 实体定义

```csharp
[SugarTable("users")]
public class User
{
    [SugarColumn(IsPrimaryKey = true, IsIdentity = true)]
    public int Id { get; set; }

    [SugarColumn(Length = 50, IsNullable = false)]
    public string Name { get; set; } = "";

    public int  Age { get; set; }

    [SugarColumn(IsNullable = true, ColumnDataType = "datetime")]
    public DateTime? CreateTime { get; set; }

    [SugarColumn(IsIgnore = true)]
    public string Computed { get; set; } = "";
}
```

---

## CRUD

```csharp
// 插入（自增主键回填）
int id = db.Insertable(new User { Name = "Tom", Age = 18 })
           .ExecuteReturnIdentity();

// 批量
db.Insertable(list).ExecuteCommand();

// 更新
db.Updateable(new User { Id = 1, Name = "Tom2" }).ExecuteCommand();
db.Updateable<User>().SetColumns(u => new User { Age = u.Age + 1 })
                     .Where(u => u.Id == 1).ExecuteCommand();

// 删除
db.Deletable<User>().Where(u => u.Id == 1).ExecuteCommand();
db.Deletable<User>(new[] { 1, 2, 3 }).ExecuteCommand();
```

---

## 查询

```csharp
var u  = db.Queryable<User>().First(u => u.Id == 1);

var ls = db.Queryable<User>()
           .Where(u => u.Age > 18 && u.Name.Contains("T"))
           .OrderBy(u => u.Id, OrderByType.Desc)
           .Select(u => new { u.Id, u.Name })
           .ToList();

// 分页
int total = 0;
var page = db.Queryable<User>()
             .Where(u => u.Age > 18)
             .ToPageList(pageNumber: 1, pageSize: 20, totalNumber: ref total);

// JOIN
var join = db.Queryable<User, Order>((u, o) => new JoinQueryInfos(
                JoinType.Left, u.Id == o.UserId))
             .Where((u, o) => u.Age > 18)
             .Select((u, o) => new { u.Name, o.Amount })
             .ToList();
```

---

## 异步 API

```csharp
var ls = await db.Queryable<User>().ToListAsync();
await db.Insertable(u).ExecuteCommandAsync();
```

---

## 事务

```csharp
var result = await db.Ado.UseTranAsync(async () => {
    await db.Insertable(a).ExecuteCommandAsync();
    await db.Updateable(b).ExecuteCommandAsync();
});
if (!result.IsSuccess) Console.WriteLine(result.ErrorMessage);
```

---

## Code First（自动建库/建表）

```csharp
db.DbMaintenance.CreateDatabase();              // 创建库
db.CodeFirst.InitTables(typeof(User), typeof(Order));   // 创建/更新表
db.CodeFirst.InitTables<User>();
```

---

## 雪花 ID

```csharp
public class Order {
    [SugarColumn(IsPrimaryKey = true)]
    public long Id { get; set; }      // 不要 IsIdentity
}

SnowFlakeSingle.WorkId = 1;           // 设置工作机器号

var o = new Order { Id = SnowFlakeSingle.Instance.NextId() };
```

---

## 读写分离

```csharp
new ConnectionConfig {
    ConnectionString = "主库",
    SlaveConnectionConfigs = new() {
        new SlaveConnectionConfig { HitRate = 10, ConnectionString = "从库1" },
        new SlaveConnectionConfig { HitRate = 10, ConnectionString = "从库2" }
    }
};
```

写走主库，读自动负载到从库。

---

## 分表（按时间）

```csharp
[SplitTable(SplitType.Month)]   // 月分表
[SugarTable("Logs_{year}{month}")]
public class Log { ... }

db.Insertable(log).SplitTable().ExecuteCommand();
db.Queryable<Log>().SplitTable(t => t.InMonths(2024, 2024, 1)).ToList();
```

---

## AOP（日志 / 拦截）

```csharp
db.Aop.OnLogExecuting    = (sql, p) => log.Info(sql);
db.Aop.OnError           = ex      => log.Error(ex);
db.Aop.OnLogExecuted     = (sql,p) => /* 监控 */;
db.Aop.DataExecuting     = (val, e) => /* 自动填充 CreateTime */;
```

---

## 性能与最佳实践

1. **批量 Insert** 用 `Insertable(list).UseSqlBulkCopy()` 或 `PageSize`
2. **大查询**用 `ToPageList`，不要 ToList 全量
3. **复杂表达式** 抽成方法，避免反射开销
4. **Aop** 异步日志，避免影响主流程
5. **使用 SqlSugarScope** 在 DI 中替代直接 `SqlSugarClient`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 表名映射不对 | `[SugarTable("name")]` 或全局 `EntityService` |
| 外键关联未带条件 | `Mapper` 配合 `Includes` 显式指定 |
| 多线程异常 | 使用 `SqlSugarScope`（线程安全） |
| 中文乱码 | MySQL 用 `utf8mb4`，连接字符串加 `Charset=utf8mb4` |
| 时间精度丢失 | 列改 `datetime(3)` 或 `datetime2` |

---

## 参考资源

- 官方文档：<https://www.donet5.com/Home/Doc>
- 仓库：<https://github.com/DotNetNext/SqlSugar>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/tutorial/sqlsugar/>

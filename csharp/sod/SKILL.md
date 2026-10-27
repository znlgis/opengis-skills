---
name: sod
description: "Use when needing a multi-paradigm .NET ORM — EntityBase + EntityQuery CRUD, OQL chain queries with oql.Limit paging, MyBatis-style SQL-MAP XML via SqlMapper, AdoHelper raw SQL, MyDB.GetDBHelperByConnectionName. Also for identity keys not written back after Insert, dirty-field updates, and provider switching across SqlServer/MySql/DaMeng/Kingbase. PDF.NET SOD: ORM + SQL-MAP + OQL."
tags:
  - dotnet
  - orm
  - database
  - sql-mapping
  - oql
  - mybatis-style
  - multi-database
---

> **项目地址：** <https://github.com/znlgis/SOD>（镜像仓库，最后提交 2025-07-05；国内主仓库见 <https://gitee.com/znlgis/SOD>，截至 2026-10 仍可访问但更新缓慢）
>
> **官网：** <https://www.pwmis.com/sod/>
>
> **官方文档：** <http://www.pwmis.com/sod/>
>
> **NuGet：** `PDF.NET.SOD`
>
> **NuGet（.NET 6+）：** `PWMIS.SOD`
>
> **最新版本：** PDF.NET.SOD 7.0.1 / PWMIS.SOD 6.0.3（截至 2026-10，NuGet 实测）
>
> **许可证：** Apache-2.0

## 概述

SOD 由 PDF.NET 演化而来，主要特点：

- **混合 ORM 模式**：原生 SQL + ORM + SQL-MAP（XML 配置）+ OQL（对象查询语言）
- **多数据库**：SqlServer / Oracle / MySQL / PostgreSQL / SQLite / Access / 达梦 DM / 人大金仓 / 神舟通用
- **AdoHelper**：屏蔽底层 Provider 差异
- **实体类**：`EntityBase`，支持脏字段跟踪、字段映射、状态机
- **OQL**：链式 API 查询、连接、分组、聚合
- **SQL-MAP**：XML 写 SQL，Mybatis 风格
- **读写分离**：主从配置
- **缓存与监控**：内置 SQL 性能日志

---

## 安装

### 方式一：dotnet CLI

```bash
# .NET 6+ 用 PWMIS.SOD（新版核心库）
dotnet add package PWMIS.SOD

# .NET Framework / netstandard2.0 用 PDF.NET.SOD 系列
dotnet add package PDF.NET.SOD.Core

# 对应数据库 Provider
dotnet add package PDF.NET.SOD.MySQL.Provider
dotnet add package PDF.NET.SOD.PostgreSQL.Provider
```

### 方式二：PackageReference

```xml
<ItemGroup>
  <PackageReference Include="PWMIS.SOD" Version="6.0.3" />
</ItemGroup>
```

### 验证安装

```bash
dotnet list package | grep -i sod
```

> 两个包的实测结构：`PWMIS.SOD` 6.0.3 提供 `lib/net6.0/PWMIS.SOD.Core.dll`；`PDF.NET.SOD` 7.0.1 只含 `PWMIS.SOD.Core.Extensions.dll`，完整核心在 `PDF.NET.SOD.Core` 7.0.1 里。按目标框架选包，不要混装。

---

## 核心 API 速查

| 对象 | 入口 | 说明 |
|------|------|------|
| 数据访问入口 | `MyDB.GetDBHelperByConnectionName(name)` / `MyDB.GetDBHelperByProviderString(cs, provider)` | 返回 `AdoHelper`（`db`，继承自 `CommonDB`），屏蔽底层 Provider 差异 |
| 实体基类 | `EntityBase` | `TableName` / `IdentityName` / `PrimaryKeys`；属性用 `getProperty<T>()` / `setProperty()` |
| 实体 CRUD | `new EntityQuery<T>(db)` | `Insert` / `Update`（仅脏字段）/ `Delete` / `GetList` / `GetEntity` |
| OQL 链式查询 | `OQL.From(entity).Select(...).Where(...).OrderBy(...).END` | 支持多表连接、分组、聚合；`oql.Limit(pageSize, pageIndex)` 分页 |
| SQL-MAP | `new SqlMapper(db).ExecuteList<T>("Map.Statement", param)` | XML 写 SQL（MyBatis 风格），SqlMapTool 可生成强类型 DAL |
| 原生 SQL | `db.ExecuteDataSet(...)` / `db.ExecuteNonQuery(...)` / `db.GetParameter(...)` | 用 AdoHelper 直接执行 |
| 事务 | `db.BeginTransaction()` → `db.Commit()` / `db.Rollback()` | 均定义在 `CommonDB` 上，`AdoHelper` 继承而来；没有 `UseTransaction` 辅助方法 |

---

## 配置连接字符串（App.config / appsettings）

```xml
<connectionStrings>
  <add name="local" providerName="SqlServer"
       connectionString="server=.;database=demo;uid=sa;pwd=..." />
</connectionStrings>
```

或代码：

```csharp
using PWMIS.DataProvider.Data;
var db = MyDB.GetDBHelperByProviderString(
    "server=.;database=demo;uid=sa;pwd=...", "SqlServer");
```

---

## 实体类

```csharp
using PWMIS.DataMap.Entity;

[Serializable]
public class User : EntityBase
{
    public User() {
        TableName  = "Users";
        IdentityName = "Id";        // 自增列
        PrimaryKeys.Add("Id");
    }

    public int Id        { get => getProperty<int>("Id");
                           set => setProperty("Id", value); }
    public string Name   { get => getProperty<string>("Name");
                           set => setProperty("Name", value, 50); }
    public DateTime Time { get => getProperty<DateTime>("CreateTime");
                           set => setProperty("CreateTime", value); }
}
```

可通过 SOD CodeMaker 或 `EntityBuilder` 自动生成。

---

## CRUD（EntityQuery）

```csharp
using PWMIS.DataMap.Entity;

var db = MyDB.GetDBHelperByConnectionName("local");
var q  = new EntityQuery<User>(db);

var u = new User { Name = "Tom", Time = DateTime.Now };
q.Insert(u);                                     // INSERT

u.Name = "Tom2";
q.Update(u);                                     // UPDATE（仅脏字段）

var list = q.GetList(top: 10);                  // SELECT TOP 10
var u1   = q.GetEntity(new User { Id = 1 });    // by PK

q.Delete(u1);                                    // DELETE
```

---

## OQL（链式查询）

```csharp
var u = new User();
var oql = OQL.From(u)
            .Select(u.Id, u.Name)
            .Where(cmp => cmp.Comparer(u.Id, ">", 10) &
                          cmp.Comparer(u.Name, "like", "%T%"))
            .OrderBy(o => o.Asc(u.Id))
            .END;

oql.Limit(20, 1);    // 第 1 页，每页 20 条

var list = EntityQuery<User>.QueryList(oql, db);
```

聚合：

```csharp
var sum = OQL.From(u).Select(u.Id.Sum()).END;
int total = (int)EntityQuery.ExecuteOql(sum, db);
```

---

## 多表连接

```csharp
var u = new User();   var o = new Order();
var oql = OQL.From(u)
            .InnerJoin(o).On(u.Id, o.UserId)
            .Select(u.Name, o.Amount)
            .END;
```

---

## SQL-MAP（XML 模式）

`Maps/UserMap.xml`：

```xml
<sqlMap name="User">
  <statement name="ListByName" desc="按姓名查">
    <![CDATA[
    select * from Users where Name like @Name
    ]]>
  </statement>
</sqlMap>
```

```csharp
var dal = new SqlMapper(db);
var rows = dal.ExecuteList<User>("User.ListByName",
    new { Name = "%Tom%" });
```

通过 SOD 工具（SqlMapTool）从 XML 自动生成强类型 DAL 类。

---

## AdoHelper（原生 SQL）

```csharp
var ds = db.ExecuteDataSet("select * from Users where Id=@Id",
            CommandType.Text, db.GetParameter("@Id", 1));

int rows = db.ExecuteNonQuery("update Users set Name=@N where Id=@Id",
    CommandType.Text,
    db.GetParameter("@N",  "Tom"),
    db.GetParameter("@Id", 1));
```

---

## 事务

```csharp
db.BeginTransaction();
try {
    q.Insert(u1);
    q.Insert(u2);
    db.Commit();
} catch {
    db.Rollback();
    throw;
}
```

批量写入时可用 `q.Insert(new List<User> { u1, u2 })` 一次提交；SOD 没有 `UseTransaction(() => {...})` 这种委托式包装，事务边界要自己用 `BeginTransaction()` / `Commit()` 显式写，`CommonDB.OnErrorRollback` 只在内部错误处理里生效。

---

## 读写分离

通过 `MyDB.GetDBHelperByConnectionName(...)` 选择不同连接配置；SOD 支持主从切换：

```xml
<add name="local-master" providerName="SqlServer" connectionString="..."/>
<add name="local-slave"  providerName="SqlServer" connectionString="..."/>
```

写走 master，读走 slave；或借助 `IReadDb` / `IWriteDb` 接口。

---

## 多数据库适配

仅替换 `providerName`：

| 数据库 | providerName |
|--------|--------------|
| SQL Server | `SqlServer` |
| Oracle | `Oracle` |
| MySQL | `MySql` |
| PostgreSQL | `PostgreSQL` |
| SQLite | `Sqlite` |
| 达梦 | `DaMeng` |
| 人大金仓 | `Kingbase` |
| 神通 | `OSCAR` |

---

## 性能与监控

- 启用 `MyDB.SQL_LOG_INFO` 输出慢 SQL
- `db.CommandTimeOut`
- 连接池大小通过连接字符串
- OQL 大数据量分页用 `Limit()`，不要 ToList 全量

---

## 典型工作流

### 工作流一：建实体并完成一次 CRUD

1. 实体继承 `EntityBase`，标好 `TableName`、`IdentityName`、`PrimaryKeys`，属性一律用 `getProperty<T>()` / `setProperty()` 声明
2. 新增用 `EntityQuery<T>` 的 `Instance` + `Insert()`，插入后从实体上取回填的自增主键
3. 改单个字段用 `setProperty` 后 `Update()`，只提交变更字段
4. 删除/按条件批量操作走 OQL，或直接用 `AdoHelper` 执行原生 SQL

### 工作流二：复杂查询与分页

1. 条件复杂时用 OQL 链式 API 拼查询，固定 SQL 场景写 SQL-MAP XML 并用 SqlMapTool 生成强类型 DAL
2. 分页用 `oql.Limit(pageSize, pageIndex)`，不要 `ToList()` 后手工分页
3. 慢查询打开 `MyDB.SQL_LOG_INFO` 看输出，必要时调 `CommandTimeOut`

### 工作流三：换数据库 / 读写分离

1. 换库只需要改连接字符串的 `providerName`（SqlServer / MySql / PostgreSQL / DaMeng 等）
2. 读写分离：分别配主从连接串，写走 master、读走 slave
3. 事务要在同一个 `AdoHelper`（`CommonDB`）实例里 `BeginTransaction()` → 操作 → `Commit()`/`Rollback()`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 字段映射错误 | 使用 `MapField(...)` 指定列名 |
| 自增主键未填回 | `IdentityName` 设置正确 |
| 中文乱码 | 数据库用 utf8mb4 / NVARCHAR |
| 事务跨连接失败 | 使用同一 `AdoHelper` 实例（事务挂在 `CommonDB` 上，换实例即换事务） |
| 找不到 `UseTransaction` / `GetDBHelperByConnectionString` | 6.0/7.0 版没有这两个成员：事务用 `BeginTransaction()`/`Commit()`/`Rollback()`，按连接串取 helper 用 `MyDB.GetDBHelperByProviderString(cs, providerName)` |
| OQL 查全表把内存吃满 | 改用 `oql.Limit(pageSize, pageIndex)` 分页，避免 `ToList()` 全量取回 |

---

## AI 使用建议

### 推荐工作流

1. **建实体类**：继承 `EntityBase`，设置 `TableName`、`IdentityName`、`PrimaryKeys`，属性用 `getProperty<T>()` / `setProperty()` 
2. **选查询方式**：简单 CRUD → `EntityQuery<T>`；复杂条件 → OQL 链式 API；固定 SQL → SQL-MAP XML
3. **多数据库切换**：仅改连接字符串的 `providerName`（SqlServer / MySql / PostgreSQL / DaMeng 等）
4. **读写分离**：配置主从连接字符串，写走 master，读走 slave
5. **事务**：同一 `AdoHelper` 实例内 `BeginTransaction()` → 操作 → `Commit()` / `Rollback()`（无 `UseTransaction` 委托式 API）

### 关键模式与常见陷阱

- **实体属性声明**：必须用 `getProperty<T>(name)` / `setProperty(name, value, size)`，不能用自动属性
- **自增主键回填**：`IdentityName` 必须设置正确，否则 INSERT 后 `Id` 不更新
- **脏字段跟踪**：`Update()` 只提交变更字段（调用 `setProperty` 的字段），性能优于全量更新
- **OQL 分页**：用 `oql.Limit(pageSize, pageIndex)` 分页，不要 ToList 后手动分页
- **SQL-MAP 工具链**：用 SOD 的 SqlMapTool 从 XML 生成强类型 DAL，手写 XML 容易拼错

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 政企项目（达梦/金仓/神通） | SOD（多数据库支持最全） |
| 追求开发效率 | SqlSugar（链式查询更现代） |
| MyBatis 用户迁移 | SOD SQL-MAP 模式 |
| 新项目 | 评估 SqlSugar vs SOD 的数据库支持列表 |

---

## 相关技能

- **sqlsugar** — 同为 .NET ORM，链式查询更现代化，生态更活跃：[../sqlsugar/SKILL.md](../sqlsugar/SKILL.md)
- **furion** — .NET Web 框架，Furion 内置 SqlSugar 集成，SOD 亦可配合使用：[../furion/SKILL.md](../furion/SKILL.md)
- **npoi** — 查询结果导出 Excel 时与 SOD 组合使用：[../npoi/SKILL.md](../npoi/SKILL.md)
- **admin-net-backend** — 基于 Furion + SqlSugar 的后台框架，可对照其分层与 DAL 组织方式：[../admin-net-backend/SKILL.md](../admin-net-backend/SKILL.md)

---

## 参考资源

- 官网：<https://www.pwmis.com/sod/>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/sod/>

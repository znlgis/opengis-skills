---
name: sod
description: "Use when needing a multi-paradigm .NET ORM with SQL-MAP (MyBatis-style XML mapping), OQL (Object Query Language), and traditional ORM. PDF.NET SOD: combines ORM + SQL-MAP + OQL for flexible .NET data access."
tags:
  - dotnet
  - orm
  - database
  - sql-mapping
  - oql
---

> **项目地址：** <https://github.com/znlgis/SOD>（社区主仓库见 <https://gitee.com/znlgis/SOD>）
>
> **官网：** <https://www.pwmis.com/sod/>
>
> **官方文档：** <http://www.pwmis.com/sod/>
>
> **NuGet：** `PDF.NET.SOD`
>
> **NuGet（.NET 6+）：** `PWMIS.SOD`
>
> **最新版本：** PDF.NET.SOD 7.0.1 / PWMIS.SOD 6.0.3（截至2026-09，NuGet）
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

```bash
dotnet add package PDF.NET.SOD
# 或对应数据库 Provider：
dotnet add package PDF.NET.SOD.MySQL
dotnet add package PDF.NET.SOD.PostgreSQL
```

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
var db = MyDB.GetDBHelperByConnectionString(
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

或：

```csharp
db.UseTransaction(() => {
    q.Insert(u1); q.Insert(u2);
    return true;
});
```

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
3. 事务要在同一个 `AdoHelper` 实例里 `BeginTransaction()` → 操作 → `Commit()`/`Rollback()`

---

## AI 使用建议

### 推荐工作流

1. **建实体类**：继承 `EntityBase`，设置 `TableName`、`IdentityName`、`PrimaryKeys`，属性用 `getProperty<T>()` / `setProperty()` 
2. **选查询方式**：简单 CRUD → `EntityQuery<T>`；复杂条件 → OQL 链式 API；固定 SQL → SQL-MAP XML
3. **多数据库切换**：仅改连接字符串的 `providerName`（SqlServer / MySql / PostgreSQL / DaMeng 等）
4. **读写分离**：配置主从连接字符串，写走 master，读走 slave
5. **事务**：同一 `AdoHelper` 实例内 `BeginTransaction()` → 操作 → `Commit()` / `Rollback()`

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

## 常见问题

| 问题 | 解决 |
|------|------|
| 字段映射错误 | 使用 `MapField(...)` 指定列名 |
| 自增主键未填回 | `IdentityName` 设置正确 |
| 中文乱码 | 数据库用 utf8mb4 / NVARCHAR |
| 事务跨连接失败 | 使用同一 `AdoHelper` 实例 |
| OQL 查全表把内存吃满 | 改用 `oql.Limit(pageSize, pageIndex)` 分页，避免 `ToList()` 全量取回 |

---

## 相关技能

- **sqlsugar** — 同为 .NET ORM，链式查询更现代化，生态更活跃：[../sqlsugar/SKILL.md](../sqlsugar/SKILL.md)
- **furion** — .NET Web 框架，Furion 内置 SqlSugar 集成，SOD 亦可配合使用：[../furion/SKILL.md](../furion/SKILL.md)

---

## 参考资源

- 官网：<https://www.pwmis.com/sod/>
- 中文教程（znlgis）：<https://znlgis.github.io/csharp/sod/>

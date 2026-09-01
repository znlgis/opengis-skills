# Admin.NET Backend Service Patterns

Service development patterns and key conventions split from SKILL.md.

---

## 服务开发模式

### 继承 BaseService（泛型 CRUD）

```csharp
// BaseService<T> 自动提供 GetDetail / GetList / Add / Update / Delete 接口
[ApiDescriptionSettings(Order = 100)]
public class MyBusinessService : BaseService<MyEntity>
{
    public MyBusinessService(SqlSugarRepository<MyEntity> rep) : base(rep) { }
}
```

### 自定义服务（推荐方式）

```csharp
/// <summary>
/// 自定义业务服务 🏷️
/// </summary>
[ApiDescriptionSettings(Order = 200)]
public class MyCustomService : IDynamicApiController, ITransient
{
    private readonly SqlSugarRepository<MyEntity> _rep;

    public MyCustomService(SqlSugarRepository<MyEntity> rep)
    {
        _rep = rep;
    }

    /// <summary>
    /// 分页查询 🔖
    /// </summary>
    [DisplayName("分页查询")]
    public async Task<SqlSugarPagedList<MyEntityOutput>> Page(MyEntityInput input)
    {
        return await _rep.AsQueryable()
            .WhereIF(!string.IsNullOrWhiteSpace(input.Name), u => u.Name.Contains(input.Name))
            .OrderBy(u => u.CreateTime, OrderByType.Desc)
            .Select<MyEntityOutput>()
            .ToPagedListAsync(input.Page, input.PageSize);
    }

    /// <summary>
    /// 新增 🔖
    /// </summary>
    [ApiDescriptionSettings(Name = "Add"), HttpPost]
    [DisplayName("新增")]
    public async Task<long> Add(AddMyEntityInput input)
    {
        var entity = input.Adapt<MyEntity>();
        await _rep.InsertAsync(entity);
        return entity.Id;
    }

    /// <summary>
    /// 更新 🔖
    /// </summary>
    [ApiDescriptionSettings(Name = "Update"), HttpPost]
    [DisplayName("更新")]
    public async Task Update(UpdateMyEntityInput input)
    {
        var entity = input.Adapt<MyEntity>();
        await _rep.AsUpdateable(entity).IgnoreColumns(true).ExecuteCommandAsync();
    }

    /// <summary>
    /// 删除 🔖
    /// </summary>
    [ApiDescriptionSettings(Name = "Delete"), HttpPost]
    [DisplayName("删除")]
    public async Task Delete(DeleteMyEntityInput input)
    {
        await _rep.FakeDeleteAsync(input.Adapt<MyEntity>());  // 软删除
    }
}
```

### 输入 / 输出 DTO

```csharp
public class MyEntityInput : BasePageInput
{
    public string? Name { get; set; }
}

public class AddMyEntityInput
{
    [Required(ErrorMessage = "名称不能为空")]
    public string Name { get; set; }

    public string? Remark { get; set; }
}

public class UpdateMyEntityInput : AddMyEntityInput
{
    [Required(ErrorMessage = "Id不能为空")]
    public long Id { get; set; }
}

public class DeleteMyEntityInput
{
    [Required(ErrorMessage = "Id不能为空")]
    public long Id { get; set; }
}

public class MyEntityOutput
{
    public long Id { get; set; }
    public string Name { get; set; }
    public string? Remark { get; set; }
    public DateTime? CreateTime { get; set; }
}
```

---

## 关键模式与约定

### Furion 动态 API

实现 `IDynamicApiController` 接口即自动暴露为 API，方法名约定映射 HTTP 动词：

| 方法名前缀 | HTTP 动词 | 示例 |
|-----------|----------|------|
| `Get` / `Find` / `Fetch` / `Query` | GET | `GetDetail(long id)` |
| `Post` / `Add` / `Create` / `Insert` | POST | `Add(AddInput input)` |
| `Put` / `Update` | PUT | `Update(UpdateInput input)` |
| `Delete` / `Remove` / `Clear` | DELETE | `Delete(long id)` |
| `Page` | POST（分页） | `Page(PageInput input)` |

可通过 `[HttpPost]` / `[HttpGet]` 强制覆盖，通过 `[ApiDescriptionSettings(Name = "xxx")]` 自定义路由段。

### SqlSugar 仓储

```csharp
// 注入仓储
private readonly SqlSugarRepository<TEntity> _rep;

// 常用操作
await _rep.InsertAsync(entity);                           // 新增
await _rep.AsUpdateable(entity).IgnoreColumns(true)
    .ExecuteCommandAsync();                               // 更新（忽略空列）
await _rep.FakeDeleteAsync(entity);                       // 软删除
await _rep.DeleteByIdAsync(id);                           // 物理删除
await _rep.GetByIdAsync(id);                              // 按 ID 查
await _rep.GetListAsync();                                // 查全部
await _rep.AsQueryable()                                  // 条件查询
    .WhereIF(condition, u => u.Field == value)
    .OrderBy(u => u.CreateTime, OrderByType.Desc)
    .Select<OutputDto>()
    .ToPagedListAsync(page, pageSize);                    // 分页

// 切换数据库上下文（多租户）
_rep.Context.AsTenant().GetConnection(tenantDbConfigId);
```

### 依赖注入

```csharp
// 瞬态（每次请求新实例）
public class MyService : ITransient { }

// 作用域（每次请求共享）
public class MyService : IScoped { }

// 单例
public class MyService : ISingleton { }
```

### 事件总线

```csharp
// 发布事件
await _eventPublisher.PublishAsync(new ChannelEventSource("MyEvent:Handler", eventData));

// 订阅处理
[EventSubscribe("MyEvent:Handler")]
public async Task HandleMyEvent(EventHandlerExecutingContext context)
{
    var data = context.Source.Payload;
    // 处理逻辑
}
```

### 缓存使用

```csharp
// 注入缓存
private readonly SysCacheService _cache;

// 读写缓存
await _cache.SetAsync(key, value);
var result = await _cache.GetAsync<T>(key);
await _cache.RemoveAsync(key);
```

---


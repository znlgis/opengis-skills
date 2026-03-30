---
name: Admin.NET 后端
description: Admin.NET 是基于 .NET8/10 (Furion/SqlSugar) 实现的通用权限开发框架后端，提供多租户、RBAC 鉴权、动态 API、缓存、任务调度、代码生成、文件管理、微信对接等企业级功能，支持插件式扩展。
---

> **项目地址：** <https://github.com/znlgis/Admin.NET>
>
> **后端代码目录：** `Admin.NET/`（.NET 解决方案）
>
> **在线文档：** <https://adminnet.top/>
>
> **演示环境：** <https://demo.adminnet.top>（账号：superAdmin.NET / 密码：Admin.NET++010101）
>
> **许可证：** MIT + Apache 2.0

## 概述

Admin.NET 后端基于 **.NET 8 / .NET 10** 构建，核心依赖 **Furion** 框架（动态 API、依赖注入、事件总线、远程请求等）和 **SqlSugar** ORM（自动建库建表、多租户、多数据库支持）。框架采用分层架构 + 插件式开发，适用于中小企业快速搭建权限管理系统。

**核心技术栈：**
- **运行时：** .NET 8.0 / .NET 10.0
- **Web 框架：** ASP.NET Core + Furion
- **ORM：** SqlSugar（支持 MySQL、SQL Server、PostgreSQL、Oracle、SQLite、达梦等）
- **缓存：** NewLife.Redis / MemoryCache
- **认证：** JWT Bearer（Furion.Extras.Authentication.JwtBearer）
- **实时通讯：** SignalR（支持 Redis 背板）
- **任务调度：** Sundial
- **日志：** log4net / Elasticsearch
- **对象映射：** Mapster

---

## 项目结构

```
Admin.NET/                         # 后端解决方案根目录
├── Admin.NET.sln                  # Visual Studio 解决方案文件
├── Admin.NET.Core/                # 核心框架层
│   ├── Attribute/                 # 自定义特性
│   ├── Cache/                     # 缓存工具
│   ├── Const/                     # 常量定义
│   ├── Entity/                    # 核心实体（EntityBase 等基类）
│   ├── Enum/                      # 枚举定义
│   ├── EventBus/                  # 事件总线
│   ├── Extension/                 # 扩展方法
│   ├── Hub/                       # SignalR Hub
│   ├── Job/                       # 定时任务
│   ├── Logging/                   # 日志组件
│   ├── Option/                    # 配置选项类
│   ├── SeedData/                  # 种子数据
│   ├── Service/                   # 核心服务（见下方服务模块表）
│   ├── SignalR/                   # SignalR 配置
│   ├── SignatureAuth/             # 签名认证
│   ├── SqlSugar/                  # SqlSugar 配置与仓储
│   ├── ElasticSearch/             # ES 日志集成
│   ├── Update/                    # 数据库更新脚本
│   └── Utils/                     # 工具类
├── Admin.NET.Application/         # 应用层（业务示例）
│   ├── Configuration/             # 应用配置
│   ├── Const/                     # 应用常量
│   ├── Entity/                    # 业务实体
│   ├── EventBus/                  # 业务事件
│   ├── OpenApi/                   # 开放 API
│   ├── Startup.cs                 # 应用层启动配置
│   └── GlobalUsings.cs            # 全局 using
├── Admin.NET.Web.Core/            # Web 中间件与配置
├── Admin.NET.Web.Entry/           # 启动入口
│   ├── Controllers/               # 控制器
│   ├── appsettings.json           # 配置文件
│   └── wwwroot/                   # 静态资源
├── Admin.NET.Test/                # 单元测试
└── Plugins/                       # 插件目录
    ├── Admin.NET.Plugin.GoView/          # GoView 数据大屏
    ├── Admin.NET.Plugin.DingTalk/        # 钉钉集成
    ├── Admin.NET.Plugin.ApprovalFlow/    # 审批流程
    ├── Admin.NET.Plugin.K3Cloud/         # 金蝶 K3 Cloud
    ├── Admin.NET.Plugin.ReZero/          # ReZero 零代码
    └── Admin.NET.Plugin.WorkWeixin/      # 企业微信
```

---

## 环境准备与运行

### 前置要求

- .NET 8 SDK 或 .NET 10 SDK
- 数据库（SQLite 默认 / MySQL / SQL Server / PostgreSQL / Oracle / 达梦等）
- Redis（可选，用于缓存和 SignalR 背板）

### 运行后端

```bash
cd Admin.NET
dotnet restore Admin.NET.sln
dotnet run --project Admin.NET.Web.Entry
```

启动后默认访问 `https://localhost:5005`，Swagger 文档地址：`https://localhost:5005/api`

### 配置文件

主配置文件为 `Admin.NET.Web.Entry/appsettings.json`，关键配置节点：

```json
{
  "DbConnection": {
    "DbType": "Sqlite",
    "ConnectionString": "DataSource=./admin.net.db"
  },
  "Cache": {
    "CacheType": "Memory"
  },
  "JWTSettings": {
    "ValidateIssuerSigningKey": true,
    "IssuerSigningKey": "your-secret-key",
    "ValidIssuer": "Admin.NET",
    "ValidAudience": "Admin.NET",
    "ExpiredTime": 120
  }
}
```

---

## 核心服务模块

`Admin.NET.Core/Service/` 目录下按业务领域划分服务模块：

| 服务目录 | 说明 | 关键类 |
|---------|------|--------|
| `Auth/` | 登录认证、Token 管理 | `SysAuthService` |
| `User/` | 用户管理 | `SysUserService` |
| `Role/` | 角色管理、权限分配 | `SysRoleService` |
| `Org/` | 机构 / 组织架构管理 | `SysOrgService` |
| `Menu/` | 菜单与按钮权限管理 | `SysMenuService` |
| `Pos/` | 职位管理 | `SysPosService` |
| `Dict/` | 数据字典管理 | `SysDictTypeService` / `SysDictDataService` |
| `Config/` | 系统参数配置 | `SysConfigService` |
| `Tenant/` | 多租户管理 | `SysTenantService` |
| `Log/` | 访问日志 / 操作日志 | `SysLogVisService` / `SysLogOpService` |
| `File/` | 文件上传下载管理 | `SysFileService` |
| `Job/` | 任务调度管理 | `SysJobService` |
| `Notice/` | 通知公告（SignalR 推送） | `SysNoticeService` |
| `OnlineUser/` | 在线用户管理（SignalR） | `SysOnlineUserService` |
| `Message/` | 站内消息 | `SysMessageService` |
| `CodeGen/` | 代码生成器 | `SysCodeGenService` |
| `Cache/` | 缓存管理 | `SysCacheService` |
| `Server/` | 服务器监控 | `SysServerService` |
| `DataBase/` | 数据库管理 | `SysDatabaseService` |
| `Wechat/` | 微信小程序 / 支付 | `SysWechatService` |
| `Alipay/` | 支付宝支付 | `SysAlipayService` |
| `OAuth/` | 第三方 OAuth 登录 | `SysOAuthService` |
| `OpenAccess/` | 开放接口签名认证 | `SysOpenAccessService` |
| `Print/` | 打印模板管理 | `SysPrintService` |
| `Region/` | 行政区域 | `SysRegionService` |
| `APIJSON/` | APIJSON 协议支持 | `ApiJsonService` |
| `Lang/` | 多语言管理 | `SysLangService` |
| `Template/` | 模板管理 | `SysTemplateService` |
| `Plugin/` | 插件管理 | `SysPluginService` |
| `Enum/` | 枚举查询服务 | `SysEnumService` |
| `Const/` | 常量查询服务 | `SysConstService` |
| `Common/` | 通用服务 | `CommonService` |
| `Schedule/` | 计划任务管理 | - |

---

## 实体基类

所有业务实体继承自 `EntityBase` 或其变体：

```csharp
/// 实体基类 - 含主键 Id
[SugarTable(null)]
public abstract class EntityBase
{
    [SugarColumn(ColumnDescription = "主键Id", IsPrimaryKey = true, IsIdentity = false)]
    public virtual long Id { get; set; }
}

/// 带审计字段的实体基类
public abstract class EntityBaseData : EntityBase
{
    public virtual long? CreateUserId { get; set; }
    public virtual DateTime? CreateTime { get; set; }
    public virtual long? UpdateUserId { get; set; }
    public virtual DateTime? UpdateTime { get; set; }
    public virtual bool IsDelete { get; set; }  // 软删除
}

/// 带租户的实体基类
public abstract class EntityTenant : EntityBaseData
{
    public virtual long? TenantId { get; set; }
}
```

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

## 认证与鉴权

### JWT 登录流程

```
POST /api/sysAuth/login
Content-Type: application/json

{
  "account": "admin",
  "password": "加密后的密码"
}

返回：{ "accessToken": "...", "refreshToken": "..." }
```

### 使用 Token

```
Authorization: Bearer {accessToken}
```

### 权限控制

- **菜单权限**：通过角色绑定菜单控制页面可见性
- **按钮权限**：通过菜单上的按钮权限标识（如 `sysUser:add`）做细粒度控制
- **数据权限**：角色可绑定数据范围（全部 / 本部门 / 本部门及以下 / 仅本人 / 自定义）

---

## 文件管理

```csharp
// 上传文件
POST /api/sysFile/uploadFile
Content-Type: multipart/form-data

// 文件存储支持：
// - Local（本地存储）
// - Aliyun（阿里云 OSS）
// - Tencent（腾讯云 COS）
// - Minio
// - QiNiu（七牛云）
```

---

## 代码生成

代码生成器根据数据库表结构自动生成前后端代码：

1. 在 Swagger 或管理界面中选择数据库表
2. 配置字段对应的前端控件类型
3. 一键生成：后端 Service / Entity / DTO + 前端 Vue 页面

---

## 插件开发

新建类库项目引用 `Admin.NET.Core`，在 `Plugins/` 目录下组织：

```csharp
// 1. 新建项目 Admin.NET.Plugin.MyPlugin
// 2. 引用 Admin.NET.Core
// 3. 实现服务
[ApiDescriptionSettings("MyPlugin", Order = 100)]
public class MyPluginService : IDynamicApiController, ITransient
{
    // 业务代码
}

// 4. 在 Admin.NET.Web.Entry 中引用该插件项目即可自动注册
```

---

## 常用第三方集成

| 功能 | NuGet 包 | 用途 |
|------|---------|------|
| 微信小程序/支付 | `SKIT.FlurlHttpClient.Wechat.*` | 微信 API 对接 |
| 支付宝支付 | `AlipaySDKNet.Standard` | 支付宝 API 对接 |
| 导入导出 | `Magicodes.IE.Excel` / `MiniExcel` | Excel/Word/PDF 导入导出 |
| 二维码 | `QRCoder` | 二维码生成 |
| 国密算法 | `BouncyCastle.Cryptography` | SM2/SM3/SM4 加密 |
| LDAP | `Novell.Directory.Ldap.NETStandard` | LDAP/AD 域认证 |
| 短信 | `AlibabaCloud.SDK.Dysmsapi20170525` | 阿里云短信 |
| 邮件 | `MailKit` / `NETCore.MailKit` | 邮件发送 |
| IP 定位 | `IPTools.China` / `IPTools.International` | IP 地址解析 |
| 限流 | `AspNetCoreRateLimit` | API 访问限流 |
| ES 日志 | `Elastic.Clients.Elasticsearch` | Elasticsearch 日志 |
| OAuth | `AspNet.Security.OAuth.*` | 第三方登录（微信/Gitee） |

---

## 开发流程最佳实践

```
1. 建议每个业务系统单独创建一个工程（参考 Admin.NET.Application 层的结构）
2. 自建应用层引用 Admin.NET.Core 层（不修改核心工程名）
3. Admin.NET.Web.Entry 引用新建的应用层工程
4. 接口 / 服务 / 控制器采用合并模式，不影响自建应用层的使用
5. 可随主仓库升级而升级，避免冲突
```

---

## 注意事项

1. **数据库自动迁移**：首次启动会自动创建数据库和种子数据，无需手动执行 SQL
2. **雪花 ID**：主键使用 `Yitter.IdGenerator` 生成雪花 ID（long 类型）
3. **软删除**：继承 `EntityBaseData` 的实体默认使用软删除（`IsDelete` 字段）
4. **多租户**：实体继承 `EntityTenant` 自动按 `TenantId` 隔离数据
5. **API 分组**：通过 `[ApiDescriptionSettings("GroupName")]` 对 Swagger 接口分组
6. **权限控制**：方法上 `[DisplayName("操作名")]` 会注册为权限标识，搭配 `[Authorize]` 使用
7. **国密支持**：通过 `BouncyCastle.Cryptography` 和 `sm-crypto` 实现 SM2/SM3/SM4 算法
8. **Docker 部署**：后端目录包含 `.dockerignore`，可直接用 Dockerfile 容器化部署

---

## 参考链接

- **GitHub：** <https://github.com/znlgis/Admin.NET>
- **GitHub 镜像：** <https://github.com/zuohuaijun/Admin.NET>
- **Gitee 镜像：** <https://gitee.com/zuohuaijun/Admin.NET>
- **GitCode 镜像：** <https://gitcode.com/zuohuaijun/Admin.NET>
- **在线文档：** <https://adminnet.top/>
- **Furion 框架：** <https://gitee.com/dotnetchina/Furion>
- **SqlSugar 文档：** <https://www.donet5.com/Home/Doc>
- **vue-next-admin：** <https://lyt-top.gitee.io/vue-next-admin-doc-preview/>

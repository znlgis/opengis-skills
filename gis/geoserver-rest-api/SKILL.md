---
name: geoserver-rest-api
description: "Use when automating GeoServer management — programmatic workspace, datastore, and layer creation, style upload, service configuration via REST API. GeoServer REST API: manage GeoServer without GUI using curl, Python, or any HTTP client."
tags:
  - rest
  - api
  - http
  - server
  - wms
  - wfs
  - automation
  - curl
  - geoserver
  - json
---

> **项目地址：** <https://github.com/geoserver/geoserver>
>
> **REST API 文档：** <https://docs.geoserver.org/latest/en/user/rest/index.html>
>
> **API 参考：** <https://docs.geoserver.org/stable/en/user/rest/api/index.html>
>
> **最新版本：** GeoServer 3.0.1（截至 2026-10，[官方下载](https://geoserver.org/release/stable/)）
>
> **许可证：** GPL-2.0

## 概述

GeoServer 是一个基于 Java 的开源地理空间数据服务器，实现了 OGC WMS、WFS、WCS、WMTS 等标准协议。GeoServer REST API 提供了完整的 RESTful 配置管理接口，可通过标准 HTTP 方法（GET / POST / PUT / DELETE）对 GeoServer 的各类资源进行编程式管理。

REST API 的典型用途包括：

- **自动化部署**：批量创建工作空间、数据存储、发布图层
- **CI/CD 集成**：在持续集成流水线中自动配置 GeoServer
- **AI 智能体**：通过 HTTP 接口让 AI 自主管理地图服务
- **运维脚本**：批量修改样式、更新数据源连接参数

**基础 URL 格式：** `http://{host}:{port}/geoserver/rest`

**默认认证：** 用户名 `admin`，密码 `geoserver`（HTTP Basic Auth）

**数据格式：** 支持 JSON 和 XML，通过 `Accept` / `Content-Type` 请求头或 URL 后缀（`.json` / `.xml`）指定。

---

## 环境准备与认证方式

所有写操作（POST / PUT / DELETE）均需认证。GeoServer 默认使用 HTTP Basic Auth：

```bash
# curl 方式
curl -u admin:geoserver ...

# HTTP Header 方式
Authorization: Basic YWRtaW46Z2Vvc2VydmVy
```

---

## API 端点一览

REST API 按资源分组，完整端点清单见 [reference/endpoints.md](reference/endpoints.md)：

| 资源组 | 基础路径 | 资源组 | 基础路径 |
|---|---|---|---|
| 系统管理 | `/rest/about/*`、`/rest/reload`、`/rest/reset` | 图层 | `/rest/layers` |
| 工作空间 | `/rest/workspaces` | 图层组 | `/rest/layergroups` |
| 命名空间 | `/rest/namespaces` | 样式 | `/rest/styles` |
| 数据存储 | `/rest/workspaces/{ws}/datastores` | OGC 服务设置 | `/rest/services/{wms\|wfs\|wcs\|wmts}/settings` |
| 要素类型 | `.../datastores/{ds}/featuretypes` | 安全 | `/rest/security/*` |
| 覆盖存储 / 覆盖 | `/rest/workspaces/{ws}/coveragestores` | GeoWebCache | `/gwc/rest/*` |

---

## 常用操作示例

### 1. 获取 GeoServer 版本

```bash
curl -u admin:geoserver \
  "http://localhost:8080/geoserver/rest/about/version.json"
```

### 2. 创建工作空间

```bash
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{"workspace":{"name":"myws"}}' \
  "http://localhost:8080/geoserver/rest/workspaces"
```

### 3. 创建 PostGIS 数据存储

```bash
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{
    "dataStore": {
      "name": "pgstore",
      "connectionParameters": {
        "entry": [
          {"@key": "host", "$": "localhost"},
          {"@key": "port", "$": "5432"},
          {"@key": "database", "$": "geodata"},
          {"@key": "user", "$": "postgres"},
          {"@key": "passwd", "$": "postgres"},
          {"@key": "dbtype", "$": "postgis"},
          {"@key": "schema", "$": "public"}
        ]
      }
    }
  }' \
  "http://localhost:8080/geoserver/rest/workspaces/myws/datastores"
```

### 4. 上传 Shapefile 并自动发布图层

```bash
curl -u admin:geoserver -XPUT \
  -H "Content-Type: application/zip" \
  --data-binary @roads.zip \
  "http://localhost:8080/geoserver/rest/workspaces/myws/datastores/roads/file.shp"
```

> 上传后自动创建同名数据存储和图层。Shapefile 需打包为 ZIP（包含 .shp、.shx、.dbf、.prj 文件）。

### 5. 发布 PostGIS 表为要素类型

```bash
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{"featureType":{"name":"buildings","nativeName":"buildings"}}' \
  "http://localhost:8080/geoserver/rest/workspaces/myws/datastores/pgstore/featuretypes"
```

### 6. 上传 GeoTIFF 栅格数据

```bash
curl -u admin:geoserver -XPUT \
  -H "Content-Type: image/tiff" \
  --data-binary @dem.tif \
  "http://localhost:8080/geoserver/rest/workspaces/myws/coveragestores/dem/file.geotiff"
```

### 7. 创建并上传 SLD 样式

```bash
# 步骤 1：创建样式定义
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{"style":{"name":"mystyle","filename":"mystyle.sld"}}' \
  "http://localhost:8080/geoserver/rest/workspaces/myws/styles"

# 步骤 2：上传 SLD 文件内容
curl -u admin:geoserver -XPUT \
  -H "Content-Type: application/vnd.ogc.sld+xml" \
  --data-binary @mystyle.sld \
  "http://localhost:8080/geoserver/rest/workspaces/myws/styles/mystyle"
```

### 8. 为图层设置默认样式

```bash
curl -u admin:geoserver -XPUT \
  -H "Content-Type: application/json" \
  -d '{"layer":{"defaultStyle":{"name":"mystyle","workspace":"myws"}}}' \
  "http://localhost:8080/geoserver/rest/layers/myws:roads"
```

### 9. 创建图层组

```bash
curl -u admin:geoserver -XPOST \
  -H "Content-Type: application/json" \
  -d '{
    "layerGroup": {
      "name": "basemap",
      "layers": {
        "layer": [
          {"name": "myws:roads"},
          {"name": "myws:buildings"}
        ]
      },
      "styles": {
        "style": [
          {"name": "line"},
          {"name": "polygon"}
        ]
      }
    }
  }' \
  "http://localhost:8080/geoserver/rest/workspaces/myws/layergroups"
```

### 10. 删除工作空间（级联删除所有内容）

```bash
curl -u admin:geoserver -XDELETE \
  "http://localhost:8080/geoserver/rest/workspaces/myws?recurse=true"
```

---

## 典型工作流

### 发布矢量数据（Shapefile）完整流程

```text
1. POST /rest/workspaces               → 创建工作空间
2. PUT  .../datastores/{ds}/file.shp   → 上传 Shapefile（自动创建数据存储和图层）
3. POST /rest/workspaces/{ws}/styles   → 创建样式
4. PUT  .../styles/{style}             → 上传 SLD 文件
5. PUT  /rest/layers/{layer}           → 绑定样式到图层
```

### 发布矢量数据（PostGIS）完整流程

```text
1. POST /rest/workspaces                       → 创建工作空间
2. POST .../datastores                          → 创建 PostGIS 数据存储
3. POST .../datastores/{ds}/featuretypes        → 发布数据库表为图层
4. PUT  /rest/layers/{layer}                    → 配置图层样式
```

### 发布栅格数据（GeoTIFF）完整流程

```text
1. POST /rest/workspaces                            → 创建工作空间
2. PUT  .../coveragestores/{cs}/file.geotiff        → 上传 GeoTIFF（自动创建存储和覆盖）
3. PUT  /rest/layers/{layer}                        → 配置图层样式
```

---

## C# 客户端（GeoServerDesktop.GeoServerClient）

本技能的配套教程系列以 C# 客户端库 **GeoServerDesktop.GeoServerClient** 为主线：它把上述 REST 端点封装为强类型、全异步的 .NET API，适用于桌面管理工具、CI/CD 集成与 .NET 运维脚本。

- **定位**：面向 .NET 的 GeoServer REST API 完整封装，分层架构（Configuration / Http / Models / Services），客户端声明兼容 GeoServer 2.20+
- **仓库**：[github.com/znlgis/GeoServerDesktop](https://github.com/znlgis/GeoServerDesktop)（社区维护，2026-09 仍活跃）
- **NuGet**：`GeoServerDesktop.GeoServerClient`（最新 1.1.1）
- **环境要求**：.NET Standard 2.0（支持 .NET Framework 4.6.1+、.NET 6/8+），依赖 Newtonsoft.Json

核心入口类：

| 类 | 职责 |
|---|---|
| `GeoServerClientOptions` | 连接配置——`BaseUrl` / `Username` / `Password` / `TimeoutSeconds` |
| `GeoServerClientFactory` | 服务工厂——`CreateWorkspaceService()` 等创建各类服务实例，`IDisposable` |
| `WorkspaceService` / `DataStoreService` / `FeatureTypeService` / `LayerService` / `StyleService` 等 | 各资源组的异步 CRUD 服务 |
| `GeoServerRequestException` | 统一异常——携带 `StatusCode` 与 `ResponseContent` |

```csharp
using GeoServerDesktop.GeoServerClient.Configuration;
using GeoServerDesktop.GeoServerClient.Services;

var options = new GeoServerClientOptions
{
    BaseUrl = "http://localhost:8080/geoserver",
    Username = "admin",
    Password = "geoserver"
};

using var factory = new GeoServerClientFactory(options);
var workspaceService = factory.CreateWorkspaceService();

// 与 REST 端点一一对应：列出 / 创建工作空间
var workspaces = await workspaceService.GetWorkspacesAsync();
await workspaceService.CreateWorkspaceAsync("myws");
```

> **与通用 REST 的关系：** 该客户端是对前文 `/rest/*` 端点的直接封装——请求路径、JSON 包装结构（`{"workspace":{...}}`）、认证方式完全一致；不使用该库时，用 curl 或任意 HTTP 客户端按前文示例直接调用即可。完整教程见 [znlgis 博客：GeoServer REST API](https://znlgis.github.io/gis/tutorial/geoserver-rest-api/)。

---

## 请求与响应格式

### JSON 格式约定

请求和响应使用 JSON 时需注意 GeoServer 的 JSON 包装结构：

```json
// 工作空间列表响应
{
  "workspaces": {
    "workspace": [
      {"name": "cite", "href": "http://..."},
      {"name": "tiger", "href": "http://..."}
    ]
  }
}

// 单个工作空间响应
{
  "workspace": {
    "name": "myws",
    "isolated": false,
    "dataStores": "http://...",
    "coverageStores": "http://...",
    "wmsStores": "http://..."
  }
}
```

### 常用 Content-Type

| 格式 | Content-Type |
|------|-------------|
| JSON | `application/json` |
| XML | `application/xml` 或 `text/xml` |
| SLD | `application/vnd.ogc.sld+xml` |
| ZIP (Shapefile) | `application/zip` |
| GeoTIFF | `image/tiff` |
| GeoPackage | `application/geopackage+sqlite3` |

### HTTP 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 401 | 认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 405 | 方法不允许 |
| 500 | 服务器内部错误 |

---

## 重要注意事项

1. **认证必需**：所有修改操作（POST / PUT / DELETE）必须提供有效认证凭据。
2. **recurse 参数**：删除工作空间、数据存储时，添加 `?recurse=true` 可级联删除所有子资源，否则存在子资源时删除会失败。
3. **JSON 包装**：GeoServer REST API 的 JSON 请求 / 响应体均使用单层包装对象（如 `{"workspace":{...}}`），这与标准 REST 实践不同，使用时需注意。
4. **URL 后缀**：可使用 `.json` 或 `.xml` 后缀替代 `Accept` 请求头来指定响应格式。
5. **文件上传**：上传 Shapefile 时需打包为 ZIP 格式，且 ZIP 内必须包含 `.shp`、`.shx`、`.dbf`、`.prj` 文件。
6. **编码**：图层名、工作空间名建议使用英文字母、数字和下划线，避免中文和特殊字符。
7. **GeoWebCache**：通过 REST API 修改图层后，可能需要手动清空该图层的 GWC 缓存才能看到更新效果。

---

## 常见问题

| 问题 | 解决 |
|------|------|
| GET 正常但 POST/PUT 返回 401 | 补全 HTTP Basic Auth 凭据（默认 `admin:geoserver`），并确认 REST 访问规则未被安全设置禁用 |
| POST 返回 400 且资源未创建 | 检查 JSON 包装层（如 `{"workspace":{...}}`）与 `Content-Type: application/json` 是否正确 |
| 上传 Shapefile 失败 | 必须打包为 ZIP（含 `.shp`/`.shx`/`.dbf`/`.prj`），PUT 到 `.../datastores/{ds}/file.shp` |
| 上传样式后图层样式未变化 | 确认 SLD 上传使用 `application/vnd.ogc.sld+xml`，并检查图层是否绑定到该样式 |
| 删除 Workspace / Store 报错 | 添加 `?recurse=true` 级联删除子资源 |
| 修改配置后服务端未生效 | `POST /rest/reload` 重新加载配置；瓦片更新需清理 GWC 缓存 |
| 无法确认服务版本 | `GET /rest/about/version.json` 返回 GeoServer 与组件版本 |

---

## AI 使用建议

### 推荐工作流

1. **确认 GeoServer 运行**：先验证 `http://localhost:8080/geoserver/rest/about/version.json` 可访问
2. **创建工作空间**：POST `/rest/workspaces` → 创建命名空间
3. **添加数据存储**：根据数据类型 POST datastores（矢量）或 coveragestores（栅格）
4. **发布图层**：POST featuretypes（矢量）或 coverages（栅格）
5. **配置样式**：POST styles + PUT SLD 文件 → PUT layers 绑定样式
6. **验证发布**：GET `/rest/layers.json` 确认图层列表，访问 WMS GetMap 测试

### 关键注意事项

- **JSON 包装结构**：GeoServer REST API 的 JSON 请求/响应使用单层包装（如 `{"workspace":{...}}`）
- **recurse 参数**：删除 Workspace/Store 时务必添加 `?recurse=true` 级联删除
- **Shapefile 上传**：必须打包为 ZIP（含 .shp/.shx/.dbf/.prj），用 PUT 方式上传
- **URL 后缀**：可用 `.json` / `.xml` 后缀替代 `Accept` 头指定响应格式
- **Content-Type**：样式上传使用 `application/vnd.ogc.sld+xml`，栅格上传使用 `image/tiff`
- **认证**：所有 POST/PUT/DELETE 操作需要 HTTP Basic Auth（默认 admin:geoserver）

## 相关技能

- **geoserver** — GeoServer 服务器运维配置：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **geoserver-cloud** — 云原生微服务版本：[../geoserver-cloud/SKILL.md](../geoserver-cloud/SKILL.md)
- **gdal** — 命令行数据预处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **postgis** — 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)

## 参考资源

- GeoServer 源码仓库：<https://github.com/geoserver/geoserver>
- REST API 概述：<https://docs.geoserver.org/latest/en/user/rest/index.html>
- REST API 参考：<https://docs.geoserver.org/stable/en/user/rest/api/index.html>
- GeoServer 用户手册：<https://docs.geoserver.org/stable/en/user/>
- C# 客户端仓库：<https://github.com/znlgis/GeoServerDesktop>
- 端点清单补充文件：[reference/endpoints.md](reference/endpoints.md)
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/geoserver-rest-api/>

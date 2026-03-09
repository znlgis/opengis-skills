---
name: geoserver-rest-api
description: GeoServer REST API 是 GeoServer 提供的 RESTful 配置接口，允许通过 HTTP 请求以 JSON 或 XML 格式对工作空间、数据存储、图层、样式、图层组、服务设置及安全等资源进行增删改查管理，适用于自动化运维、CI/CD 和 AI 智能体集成场景。
---

> **项目地址：** <https://github.com/geoserver/geoserver>
>
> **REST API 文档：** <https://docs.geoserver.org/latest/en/user/rest/index.html>
>
> **API 参考：** <https://docs.geoserver.org/stable/en/user/rest/api/index.html>
>
> **许可证：** GNU General Public License v2.0+

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

## 认证方式

所有写操作（POST / PUT / DELETE）均需认证。GeoServer 默认使用 HTTP Basic Auth：

```bash
# curl 方式
curl -u admin:geoserver ...

# HTTP Header 方式
Authorization: Basic YWRtaW46Z2Vvc2VydmVy
```

---

## API 端点一览

### 系统管理

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 获取版本信息 | GET | `/rest/about/version.json` | 返回 GeoServer 版本与组件信息 |
| 获取系统状态 | GET | `/rest/about/system-status.json` | 返回系统运行状态 |
| 获取清单 | GET | `/rest/about/manifest.json` | 返回已加载模块清单 |
| 重新加载配置 | POST | `/rest/reload` | 从磁盘重新加载配置 |
| 重置缓存 | POST | `/rest/reset` | 重置内存中的资源缓存 |

### 工作空间 (Workspaces)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出所有工作空间 | GET | `/rest/workspaces.json` | 返回工作空间列表 |
| 创建工作空间 | POST | `/rest/workspaces` | 创建新工作空间 |
| 获取工作空间详情 | GET | `/rest/workspaces/{ws}.json` | 获取指定工作空间信息 |
| 修改工作空间 | PUT | `/rest/workspaces/{ws}` | 更新工作空间配置 |
| 删除工作空间 | DELETE | `/rest/workspaces/{ws}?recurse=true` | 删除工作空间（recurse=true 级联删除） |
| 获取默认工作空间 | GET | `/rest/workspaces/default.json` | 获取默认工作空间 |
| 设置默认工作空间 | PUT | `/rest/workspaces/default` | 设置默认工作空间 |

### 命名空间 (Namespaces)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出所有命名空间 | GET | `/rest/namespaces.json` | 返回命名空间列表 |
| 创建命名空间 | POST | `/rest/namespaces` | 创建新命名空间 |
| 获取命名空间详情 | GET | `/rest/namespaces/{ns}.json` | 获取指定命名空间 |
| 修改命名空间 | PUT | `/rest/namespaces/{ns}` | 更新命名空间 |
| 删除命名空间 | DELETE | `/rest/namespaces/{ns}` | 删除命名空间 |

### 数据存储 (Data Stores) — 矢量数据

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出数据存储 | GET | `/rest/workspaces/{ws}/datastores.json` | 列出工作空间下的矢量数据存储 |
| 创建数据存储 | POST | `/rest/workspaces/{ws}/datastores` | 创建新数据存储 |
| 获取数据存储详情 | GET | `/rest/workspaces/{ws}/datastores/{ds}.json` | 获取指定数据存储信息 |
| 修改数据存储 | PUT | `/rest/workspaces/{ws}/datastores/{ds}` | 更新数据存储连接参数 |
| 删除数据存储 | DELETE | `/rest/workspaces/{ws}/datastores/{ds}?recurse=true` | 删除数据存储 |
| 上传文件到数据存储 | PUT | `/rest/workspaces/{ws}/datastores/{ds}/file.{ext}` | 上传 Shapefile 等文件（ext: shp, gpkg 等） |
| 通过 URL 加载数据 | PUT | `/rest/workspaces/{ws}/datastores/{ds}/url.{ext}` | 从远程 URL 加载数据 |
| 外部引用数据 | PUT | `/rest/workspaces/{ws}/datastores/{ds}/external.{ext}` | 引用服务器本地文件路径 |

### 要素类型 (Feature Types) — 矢量图层资源

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出要素类型 | GET | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes.json` | 列出数据存储下的要素类型 |
| 发布要素类型 | POST | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes` | 发布新要素类型（即发布矢量图层） |
| 获取要素类型详情 | GET | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes/{ft}.json` | 获取指定要素类型 |
| 修改要素类型 | PUT | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes/{ft}` | 更新要素类型配置 |
| 删除要素类型 | DELETE | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes/{ft}?recurse=true` | 删除要素类型 |

### 覆盖存储 (Coverage Stores) — 栅格数据

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出覆盖存储 | GET | `/rest/workspaces/{ws}/coveragestores.json` | 列出工作空间下的栅格数据存储 |
| 创建覆盖存储 | POST | `/rest/workspaces/{ws}/coveragestores` | 创建新覆盖存储 |
| 获取覆盖存储详情 | GET | `/rest/workspaces/{ws}/coveragestores/{cs}.json` | 获取指定覆盖存储 |
| 修改覆盖存储 | PUT | `/rest/workspaces/{ws}/coveragestores/{cs}` | 更新覆盖存储配置 |
| 删除覆盖存储 | DELETE | `/rest/workspaces/{ws}/coveragestores/{cs}?recurse=true` | 删除覆盖存储 |
| 上传栅格文件 | PUT | `/rest/workspaces/{ws}/coveragestores/{cs}/file.{ext}` | 上传 GeoTIFF 等文件（ext: geotiff, worldimage 等） |

### 覆盖 (Coverages) — 栅格图层资源

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出覆盖 | GET | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages.json` | 列出覆盖存储下的栅格资源 |
| 发布覆盖 | POST | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages` | 发布新覆盖 |
| 获取覆盖详情 | GET | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages/{c}.json` | 获取指定覆盖 |
| 修改覆盖 | PUT | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages/{c}` | 更新覆盖配置 |
| 删除覆盖 | DELETE | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages/{c}?recurse=true` | 删除覆盖 |

### 图层 (Layers)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出所有图层 | GET | `/rest/layers.json` | 返回所有已发布图层 |
| 获取图层详情 | GET | `/rest/layers/{layer}.json` | 获取指定图层信息 |
| 修改图层 | PUT | `/rest/layers/{layer}` | 更新图层配置（如默认样式） |
| 删除图层 | DELETE | `/rest/layers/{layer}` | 删除图层 |

### 图层组 (Layer Groups)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出图层组（全局） | GET | `/rest/layergroups.json` | 返回全局图层组列表 |
| 列出图层组（工作空间） | GET | `/rest/workspaces/{ws}/layergroups.json` | 返回工作空间下的图层组 |
| 创建图层组 | POST | `/rest/layergroups` | 创建全局图层组 |
| 获取图层组详情 | GET | `/rest/layergroups/{lg}.json` | 获取指定图层组 |
| 修改图层组 | PUT | `/rest/layergroups/{lg}` | 更新图层组配置 |
| 删除图层组 | DELETE | `/rest/layergroups/{lg}` | 删除图层组 |

### 样式 (Styles)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出样式（全局） | GET | `/rest/styles.json` | 返回全局样式列表 |
| 列出样式（工作空间） | GET | `/rest/workspaces/{ws}/styles.json` | 返回工作空间下的样式 |
| 创建样式 | POST | `/rest/styles` | 创建新样式（上传 SLD/CSS） |
| 获取样式详情 | GET | `/rest/styles/{style}.json` | 获取样式元数据 |
| 获取样式文件内容 | GET | `/rest/styles/{style}.sld` | 获取 SLD 原始文件 |
| 更新样式 | PUT | `/rest/styles/{style}` | 更新样式内容 |
| 删除样式 | DELETE | `/rest/styles/{style}?purge=true` | 删除样式（purge=true 同时删除文件） |

### OGC 服务设置

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 获取 WMS 全局设置 | GET | `/rest/services/wms/settings.json` | 获取 WMS 服务配置 |
| 修改 WMS 全局设置 | PUT | `/rest/services/wms/settings` | 更新 WMS 配置 |
| 获取 WFS 全局设置 | GET | `/rest/services/wfs/settings.json` | 获取 WFS 服务配置 |
| 修改 WFS 全局设置 | PUT | `/rest/services/wfs/settings` | 更新 WFS 配置 |
| 获取 WCS 全局设置 | GET | `/rest/services/wcs/settings.json` | 获取 WCS 服务配置 |
| 修改 WCS 全局设置 | PUT | `/rest/services/wcs/settings` | 更新 WCS 配置 |
| 获取 WMTS 全局设置 | GET | `/rest/services/wmts/settings.json` | 获取 WMTS 服务配置 |
| 修改 WMTS 全局设置 | PUT | `/rest/services/wmts/settings` | 更新 WMTS 配置 |
| 工作空间级别服务设置 | GET/PUT | `/rest/services/wms/workspaces/{ws}/settings.json` | 工作空间级别 WMS 配置 |

### 安全管理 (Security)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 获取主密码信息 | GET | `/rest/security/masterpw.json` | 获取主密码状态 |
| 修改主密码 | PUT | `/rest/security/masterpw` | 更新主密码 |
| 获取数据安全规则 | GET | `/rest/security/acl/layers.json` | 获取图层访问控制规则 |
| 设置数据安全规则 | POST | `/rest/security/acl/layers` | 添加图层访问控制规则 |
| 获取服务安全规则 | GET | `/rest/security/acl/services.json` | 获取服务访问控制规则 |
| 获取 REST 安全规则 | GET | `/rest/security/acl/rest.json` | 获取 REST 端点访问规则 |
| 列出用户 | GET | `/rest/security/usergroup/users.json` | 列出所有用户 |
| 创建用户 | POST | `/rest/security/usergroup/users` | 创建新用户 |
| 列出角色 | GET | `/rest/security/roles.json` | 列出所有角色 |

### GeoWebCache 集成

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 获取图层缓存设置 | GET | `/rest/layers/{layer}/gwc` | 获取图层的 GWC 缓存配置 |
| 修改图层缓存设置 | PUT | `/rest/layers/{layer}/gwc` | 更新图层缓存配置 |
| 清空图层缓存 (Seed) | POST | `/gwc/rest/seed/{layer}.json` | 发起缓存 seed/reseed/truncate 任务 |
| 查看缓存任务状态 | GET | `/gwc/rest/seed/{layer}.json` | 获取缓存任务进度 |
| 终止缓存任务 | POST | `/gwc/rest/seed/{layer}` | 终止正在运行的缓存任务 |
| 批量截断 | POST | `/gwc/rest/masstruncate` | 批量清空缓存 |

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

```
1. POST /rest/workspaces               → 创建工作空间
2. PUT  .../datastores/{ds}/file.shp   → 上传 Shapefile（自动创建数据存储和图层）
3. POST /rest/workspaces/{ws}/styles   → 创建样式
4. PUT  .../styles/{style}             → 上传 SLD 文件
5. PUT  /rest/layers/{layer}           → 绑定样式到图层
```

### 发布矢量数据（PostGIS）完整流程

```
1. POST /rest/workspaces                       → 创建工作空间
2. POST .../datastores                          → 创建 PostGIS 数据存储
3. POST .../datastores/{ds}/featuretypes        → 发布数据库表为图层
4. PUT  /rest/layers/{layer}                    → 配置图层样式
```

### 发布栅格数据（GeoTIFF）完整流程

```
1. POST /rest/workspaces                            → 创建工作空间
2. PUT  .../coveragestores/{cs}/file.geotiff        → 上传 GeoTIFF（自动创建存储和覆盖）
3. PUT  /rest/layers/{layer}                        → 配置图层样式
```

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

## 参考链接

- GeoServer 源码仓库：<https://github.com/geoserver/geoserver>
- REST API 概述：<https://docs.geoserver.org/latest/en/user/rest/index.html>
- REST API 参考：<https://docs.geoserver.org/stable/en/user/rest/api/index.html>
- GeoServer 用户手册：<https://docs.geoserver.org/stable/en/user/>

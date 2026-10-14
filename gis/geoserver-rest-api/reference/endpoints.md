# GeoServer REST API 端点清单

> 这是 [../SKILL.md](../SKILL.md) 的补充文件，收录 GeoServer REST API 全部端点分组清单（系统管理、工作空间、命名空间、数据存储、要素类型、覆盖存储、覆盖、图层、图层组、样式、OGC 服务设置、安全、GeoWebCache）。

**基础 URL：** `http://{host}:{port}/geoserver/rest`

---

## 系统管理

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 获取版本信息 | GET | `/rest/about/version.json` | 返回 GeoServer 版本与组件信息 |
| 获取系统状态 | GET | `/rest/about/system-status.json` | 返回系统运行状态 |
| 获取清单 | GET | `/rest/about/manifest.json` | 返回已加载模块清单 |
| 重新加载配置 | POST | `/rest/reload` | 从磁盘重新加载配置 |
| 重置缓存 | POST | `/rest/reset` | 重置内存中的资源缓存 |

## 工作空间 (Workspaces)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出所有工作空间 | GET | `/rest/workspaces.json` | 返回工作空间列表 |
| 创建工作空间 | POST | `/rest/workspaces` | 创建新工作空间 |
| 获取工作空间详情 | GET | `/rest/workspaces/{ws}.json` | 获取指定工作空间信息 |
| 修改工作空间 | PUT | `/rest/workspaces/{ws}` | 更新工作空间配置 |
| 删除工作空间 | DELETE | `/rest/workspaces/{ws}?recurse=true` | 删除工作空间（recurse=true 级联删除） |
| 获取默认工作空间 | GET | `/rest/workspaces/default.json` | 获取默认工作空间 |
| 设置默认工作空间 | PUT | `/rest/workspaces/default` | 设置默认工作空间 |

## 命名空间 (Namespaces)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出所有命名空间 | GET | `/rest/namespaces.json` | 返回命名空间列表 |
| 创建命名空间 | POST | `/rest/namespaces` | 创建新命名空间 |
| 获取命名空间详情 | GET | `/rest/namespaces/{ns}.json` | 获取指定命名空间 |
| 修改命名空间 | PUT | `/rest/namespaces/{ns}` | 更新命名空间 |
| 删除命名空间 | DELETE | `/rest/namespaces/{ns}` | 删除命名空间 |

## 数据存储 (Data Stores) — 矢量数据

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

## 要素类型 (Feature Types) — 矢量图层资源

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出要素类型 | GET | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes.json` | 列出数据存储下的要素类型 |
| 发布要素类型 | POST | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes` | 发布新要素类型（即发布矢量图层） |
| 获取要素类型详情 | GET | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes/{ft}.json` | 获取指定要素类型 |
| 修改要素类型 | PUT | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes/{ft}` | 更新要素类型配置 |
| 删除要素类型 | DELETE | `/rest/workspaces/{ws}/datastores/{ds}/featuretypes/{ft}?recurse=true` | 删除要素类型 |

## 覆盖存储 (Coverage Stores) — 栅格数据

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出覆盖存储 | GET | `/rest/workspaces/{ws}/coveragestores.json` | 列出工作空间下的栅格数据存储 |
| 创建覆盖存储 | POST | `/rest/workspaces/{ws}/coveragestores` | 创建新覆盖存储 |
| 获取覆盖存储详情 | GET | `/rest/workspaces/{ws}/coveragestores/{cs}.json` | 获取指定覆盖存储 |
| 修改覆盖存储 | PUT | `/rest/workspaces/{ws}/coveragestores/{cs}` | 更新覆盖存储配置 |
| 删除覆盖存储 | DELETE | `/rest/workspaces/{ws}/coveragestores/{cs}?recurse=true` | 删除覆盖存储 |
| 上传栅格文件 | PUT | `/rest/workspaces/{ws}/coveragestores/{cs}/file.{ext}` | 上传 GeoTIFF 等文件（ext: geotiff, worldimage 等） |

## 覆盖 (Coverages) — 栅格图层资源

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出覆盖 | GET | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages.json` | 列出覆盖存储下的栅格资源 |
| 发布覆盖 | POST | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages` | 发布新覆盖 |
| 获取覆盖详情 | GET | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages/{c}.json` | 获取指定覆盖 |
| 修改覆盖 | PUT | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages/{c}` | 更新覆盖配置 |
| 删除覆盖 | DELETE | `/rest/workspaces/{ws}/coveragestores/{cs}/coverages/{c}?recurse=true` | 删除覆盖 |

## 图层 (Layers)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出所有图层 | GET | `/rest/layers.json` | 返回所有已发布图层 |
| 获取图层详情 | GET | `/rest/layers/{layer}.json` | 获取指定图层信息 |
| 修改图层 | PUT | `/rest/layers/{layer}` | 更新图层配置（如默认样式） |
| 删除图层 | DELETE | `/rest/layers/{layer}` | 删除图层 |

## 图层组 (Layer Groups)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出图层组（全局） | GET | `/rest/layergroups.json` | 返回全局图层组列表 |
| 列出图层组（工作空间） | GET | `/rest/workspaces/{ws}/layergroups.json` | 返回工作空间下的图层组 |
| 创建图层组 | POST | `/rest/layergroups` | 创建全局图层组 |
| 获取图层组详情 | GET | `/rest/layergroups/{lg}.json` | 获取指定图层组 |
| 修改图层组 | PUT | `/rest/layergroups/{lg}` | 更新图层组配置 |
| 删除图层组 | DELETE | `/rest/layergroups/{lg}` | 删除图层组 |

## 样式 (Styles)

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 列出样式（全局） | GET | `/rest/styles.json` | 返回全局样式列表 |
| 列出样式（工作空间） | GET | `/rest/workspaces/{ws}/styles.json` | 返回工作空间下的样式 |
| 创建样式 | POST | `/rest/styles` | 创建新样式（上传 SLD/CSS） |
| 获取样式详情 | GET | `/rest/styles/{style}.json` | 获取样式元数据 |
| 获取样式文件内容 | GET | `/rest/styles/{style}.sld` | 获取 SLD 原始文件 |
| 更新样式 | PUT | `/rest/styles/{style}` | 更新样式内容 |
| 删除样式 | DELETE | `/rest/styles/{style}?purge=true` | 删除样式（purge=true 同时删除文件） |

## OGC 服务设置

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

## 安全管理 (Security)

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

## GeoWebCache 集成

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 获取图层缓存设置 | GET | `/gwc/rest/layers/{layer}.xml` | 获取 GWC 图层缓存配置（官方推荐 XML） |
| 新增/修改图层缓存设置 | PUT | `/gwc/rest/layers/{layer}.xml` | 新增或修改 GWC 图层配置 |
| 删除图层缓存设置 | DELETE | `/gwc/rest/layers/{layer}.xml` | 删除 GWC 图层配置 |
| 清空图层缓存 (Seed) | POST | `/gwc/rest/seed/{layer}.json` | 发起缓存 seed/reseed/truncate 任务 |
| 查看缓存任务状态 | GET | `/gwc/rest/seed/{layer}.json` | 获取缓存任务进度 |
| 终止缓存任务 | POST | `/gwc/rest/seed/{layer}` | 终止正在运行的缓存任务 |
| 批量截断 | POST | `/gwc/rest/masstruncate` | 批量清空缓存 |

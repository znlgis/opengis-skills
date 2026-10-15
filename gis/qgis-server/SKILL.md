---
name: qgis-server
description: "Use when publishing QGIS projects (.qgs/.qgz) as OGC web services (WMS, WFS, WMTS, OGC API Features) via FastCGI, Docker, or Apache/Nginx, and when tuning QGIS_SERVER_* environment variables. QGIS Server: the C++ map server that renders QGIS Desktop projects over HTTP."
tags:
  - qgis
  - server
  - wms
  - wfs
  - wmts
  - ogc
  - fcgi
  - map
  - web
---

> **项目地址：** <https://github.com/qgis/QGIS>
>
> **官方文档：** <https://docs.qgis.org/latest/en/docs/server_manual/>
>
> **最新版本：** 4.2.3（截至 2026-10）；LTR 3.44.15
>
> **许可证：** GPL-2.0

> 该 SKILL 关注 QGIS Server 的部署与 OGC 服务发布；使用 Python 编写服务端逻辑请配合 `gis/pyqgis`，桌面端处理算法请配合 `gis/qgis-process`。

## 概述

QGIS Server 是 QGIS 源码中的服务端组件，复用 QGIS Desktop 的渲染与项目引擎，把 `.qgs`/`.qgz` 项目文件直接发布为标准 OGC 服务。它通过 FastCGI（`qgis_mapserv.fcgi`）由 Apache、Nginx 或容器托管，无需重新配置样式与图层。主要能力包括：

- **WMS**：1.1.1 / 1.3.0，支持 `GetMap`、`GetFeatureInfo`、`GetLegendGraphic`、`GetPrint`（基于 QGIS 布局的打印）
- **WFS**：1.0.0 / 1.1.0，支持 `GetFeature`、`DescribeFeatureType`、`Transaction`（WFS-T）
- **WMTS**：1.0.0，支持 `GetTile`、`GetFeatureInfo`
- **OGC API - Features**（WFS3）：JSON 表述的现代 REST 接口
- **服务端插件**：Python 插件在服务端加载，用于自定义过滤与输出

QGIS Server 与 QGIS Desktop 共享同一份代码与项目格式，因此服务行为与桌面所见基本一致。

---

## 环境准备

### 方式一：Debian / Ubuntu 软件包

使用官方 QGIS 仓库安装（建议安装 LTR 或最新稳定版）：

```bash
# 添加官方仓库后安装（仓库配置见 https://qgis.org/resources/installation-guide/）
sudo apt install qgis-server
# FastCGI 可执行文件
ls -l /usr/lib/cgi-bin/qgis_mapserv.fcgi
```

### 方式二：Windows（OSGeo4W）

使用 OSGeo4W 网络安装器，勾选 `QGIS Desktop`、`QGIS Server`、`apache`、`mod_fcgid`：

```text
以管理员运行 apache-install.bat
编辑 httpd.conf：配置 ScriptAlias 与 AddHandler cgi-script .cgi .exe
运行 apache-restart.bat
```

### 方式三：Docker 容器

官方文档给出基于 `debian:bookworm-slim` 的本地镜像构建（镜像名 `qgis-server`，容器内监听 FastCGI 端口 `5555`，由独立 nginx 容器暴露 80 端口）：

```bash
docker run -d --rm --name qgis-server --net=qgis \
  -v $(pwd)/data:/data:ro \
  -e QGIS_PROJECT_FILE=/data/osm.qgs \
  -e QGIS_SERVER_LOG_LEVEL=0 \
  qgis-server:latest
```

### 验证安装

直接执行 FCGI 二进制，若返回 `ServiceExceptionReport` 且内容为 “Service unknown or unsupported”，说明服务本身可用：

```bash
/usr/lib/cgi-bin/qgis_mapserv.fcgi
# 或通过 HTTP 验证能力文档
curl "http://localhost/cgi-bin/qgis_mapserv.fcgi?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
```

---

## 核心 API / 命令

### 项目文件与服务入口

QGIS Server 通过 `MAP` 参数或 `QGIS_PROJECT_FILE` 环境变量定位项目文件：

```text
?MAP=/home/qgis/projects/world.qgs&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=countries&CRS=EPSG:4326&WIDTH=400&HEIGHT=200&BBOX=-90,-180,90,180&FORMAT=image/png
```

`MAP` 是 QGIS 扩展参数，在 `GetCapabilities`、`GetMap`、`GetFeatureInfo`、`GetLegendGraphic`、`GetPrint`、`GetProjectSettings` 等请求中均为必填。设置 `QGIS_PROJECT_FILE` 可提供默认项目。

### 各服务请求示例

```text
# WMS GetMap（支持 png/jpg/webp/pdf/dxf 等 FORMAT）
/cgi-bin/qgis_mapserv.fcgi?MAP=/data/world.qgz&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=countries&CRS=EPSG:3857&BBOX=...&WIDTH=1024&HEIGHT=768&FORMAT=image/png

# WMS GetFeatureInfo
/cgi-bin/qgis_mapserv.fcgi?MAP=/data/world.qgz&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&QUERY_LAYERS=countries&INFO_FORMAT=application/json&I=100&J=100

# WFS GetFeature（GeoJSON 输出）
/cgi-bin/qgis_mapserv.fcgi?MAP=/data/world.qgz&SERVICE=WFS&VERSION=1.1.0&REQUEST=GetFeature&TYPENAME=countries&OUTPUTFORMAT=application/json

# WMTS GetTile
/cgi-bin/qgis_mapserv.fcgi?MAP=/data/world.qgz&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&TILEMATRIXSET=EPSG:3857&TILEMATRIX=0&TILEROW=0&TILECOL=0&FORMAT=image/png

# WMS GetPrint（基于 QGIS 布局出图，支持 pdf/svg/png）
/cgi-bin/qgis_mapserv.fcgi?MAP=/data/world.qgz&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetPrint&TEMPLATE=layout_a4&FORMAT=pdf&map0:LAYERS=countries&map0:SCALE=1000000
```

WMS 的 `LAYERS` 支持按短名或图层 ID 选择，多个图层用逗号分隔；`STYLES` 与之对应（默认样式名为 `default`）；`OPACITIES` 为每图层 0–255 的不透明度列表。`GetFeatureInfo` 的 `INFO_FORMAT` 可取 `text/xml`、`text/html`、`text/plain`、`application/vnd.ogc.gml`、`application/json`。

WMTS 的 `TILEMATRIXSET` 定义金字塔所用 CRS（形如 `EPSG:XXXX`），`TILEMATRIX`/`TILEROW`/`TILECOL` 定位具体瓦片；`FORMAT` 仅支持 `jpg`/`jpeg`/`image/jpeg`/`image/png`，其余值回退为 PNG。`GetFeatureInfo` 的 `INFOFORMAT` 默认 `text/plain`，用 `I`/`J` 指定像素坐标。

OGC API - Features（WFS3）是面向 REST 的 JSON 接口，按项目发布，端点位于服务根路径下（如 `/wfs3/collections`、`/wfs3/collections/{id}/items`），支持 `limit`、`bbox`、`datetime` 等查询参数。该服务是否可用取决于项目 `OWS Server` 页的发布设置。

### 在项目中启用服务

服务不是由 URL 决定，而是由项目配置决定：`项目 ▸ 属性 ▸ QGIS Server` 勾选要发布的服务；`OWS Server` 页逐个图层设置 `published`（是否发布）与 `queryable`（是否可查询），并可用 “Use layer ids as names” 将图层 ID 作为服务图层名。WMS 的 JPEG 压缩质量、`Add geometry to feature response` 等选项也在同一对话框配置。

### 服务端环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `QGIS_SERVER_LOG_LEVEL` | `0` | 日志级别：`0`/`INFO`、`1`/`WARNING`、`2`/`CRITICAL` |
| `QGIS_SERVER_LOG_STDERR` | `false` | 输出日志到 stderr（推荐，替代已废弃的 `QGIS_SERVER_LOG_FILE`） |
| `QGIS_SERVER_MAX_THREADS` | `-1` | 并行渲染线程数，`-1` 表示使用全部 CPU 核心 |
| `QGIS_SERVER_PARALLEL_RENDERING` | `false` | 为 WMS `GetMap` 启用并行渲染（仅 WMS） |
| `QGIS_SERVER_CACHE_SIZE` | `50` MB | 网络缓存大小（字节） |
| `QGIS_SERVER_PROJECT_CACHE_SIZE` | `100` | 缓存的 `.qgs`/`.qgz` 项目数量上限 |
| `QGIS_SERVER_LANDING_PAGE_PROJECTS_DIRECTORIES` | 空 | Landing Page 服务扫描项目文件的目录 |
| `QGIS_SERVER_IGNORE_BAD_LAYERS` | `false` | 忽略无法加载的图层，使项目仍可用 |
| `QGIS_SERVER_OVERRIDE_SYSTEM_LOCALE` | 空 | 覆盖系统 locale，如 `de_CH.utf8` |
| `QGIS_SERVER_APPLICATION_NAME` | `QGIS3 server` | 连接数据库时上报的应用名，便于识别实例 |

启动时服务端会打印一份配置摘要，标注每个参数的当前值与来源（`ENVIRONMENT_VARIABLE` / `INI_FILE` / `DEFAULT_VALUE`）。

---

## 典型工作流

1. **桌面制作项目**：在 QGIS Desktop 中组织图层、样式、坐标系，另存为 `.qgz`（推荐，单文件打包）。
2. **启用服务**：在 `项目 ▸ 属性 ▸ QGIS Server` 勾选要发布的服务；在 `OWS Server` 页设置图层 `published` / `queryable`，并可勾选 “Use layer ids as names” 用图层 ID 作为服务图层名。
3. **部署 FCGI**：将项目目录挂载/复制到服务器，通过 Apache `mod_fcgid`、Nginx `spawn-fcgi`/`fcgiwrap` 或 Docker 暴露 `qgis_mapserv.fcgi`。
4. **配置 Web 服务器**：Apache 使用 `ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/` 与 `FcgidIOTimeout 120`；Nginx 使用 `fastcgi_pass unix:/var/run/qgisserver.socket;`。
5. **验证服务**：先请求 `GetCapabilities` 确认图层清单，再测试 `GetMap`/`GetFeature`/`GetTile`。
6. **调优**：按负载设置 `QGIS_SERVER_MAX_THREADS`、开启并行渲染与项目缓存，并统一用 stderr 收集日志。

### Apache 部署片段

```apache
ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
<Directory "/usr/lib/cgi-bin">
    AllowOverride None
    Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
    Require all granted
    SetEnv QGIS_SERVER_LOG_STDERR 1
    SetEnv QGIS_SERVER_LOG_LEVEL 0
    SetEnv QGIS_PROJECT_FILE /home/qgis/projects/world.qgz
    FcgidIOTimeout 120
</Directory>
```

### Nginx 部署片段

```nginx
location /qgis {
    include fastcgi_params;
    fastcgi_pass unix:/var/run/qgisserver.socket;
    fastcgi_param QGIS_PROJECT_FILE /data/world.qgz;
    fastcgi_param QGIS_SERVER_LOG_STDERR 1;
}
```

---

## 最佳实践

1. **版本对齐**：QGIS Server 与生成项目的 QGIS Desktop 尽量使用相同主版本；跨大版本打开旧项目可能因图层/表达式不兼容而报错。生产环境优先 LTR。
2. **优先 `.qgz`**：`.qgz` 是压缩的单文件项目，便于分发并避免路径遗漏；配合 `QGIS_PROJECT_FILE` 固定默认项目。
3. **日志走 stderr**：使用 `QGIS_SERVER_LOG_STDERR` 交给系统日志收集，`QGIS_SERVER_LOG_FILE` 已废弃并计划在 QGIS 5.0 移除。
4. **并行渲染与线程**：高并发栅格出图时设置 `QGIS_SERVER_PARALLEL_RENDERING=true`，并用 `QGIS_SERVER_MAX_THREADS` 控制 CPU 占用。
5. **项目缓存**：多项目场景调大 `QGIS_SERVER_PROJECT_CACHE_SIZE`，减少重复加载开销。
6. **容错**：允许部分图层缺失时设 `QGIS_SERVER_IGNORE_BAD_LAYERS=true`，避免整份项目不可用。
7. **打印依赖**：`GetPrint` 在无 X 服务端的 Linux 上需借助 `Xvfb`（`DISPLAY=:99`）才能渲染布局。

---

## 常见问题

| 问题 | 原因 / 解决 |
|------|-------------|
| 访问 FCGI 返回 `Service unknown or unsupported` | 服务本身正常，只是未携带有效 `SERVICE`/`MAP` 参数，补全参数即可 |
| `GetMap` 返回空白或 500 | 检查 `MAP` 路径是否可读、图层是否在 `OWS Server` 页勾选 `published`，以及 CRS/BBOX 是否正确 |
| `GetCapabilities` 中图层名是长 ID | 在 `QGIS Server` 页取消 “Use layer ids as names”，改用图层短名 |
| 中文/非 ASCII 输出乱码 | 设置 `QGIS_SERVER_OVERRIDE_SYSTEM_LOCALE`（如 `en_US.UTF-8`）并确保项目属性编码一致 |
| 桌面能打开、服务端报项目不可用 | Server 与 Desktop 版本不匹配，或存在坏图层；升级版本或设 `QGIS_SERVER_IGNORE_BAD_LAYERS=true` |
| `GetPrint` 报错或输出空白 | Linux 无 X 环境，需安装并启动 `Xvfb`，在 Web 服务器配置 `DISPLAY=:99` |
| WFS `Transaction` 提交失败 | 需通过 POST 提交（删除可用 `OPERATION`），且数据源必须可写、图层勾选相应发布权限 |
| 高并发下响应缓慢 | 开启 `QGIS_SERVER_PARALLEL_RENDERING`、调大 `QGIS_SERVER_MAX_THREADS` 与项目缓存 |

---

## 参考资源

- QGIS Server 手册：<https://docs.qgis.org/latest/en/docs/server_manual/>
- 配置与环境变量：<https://docs.qgis.org/latest/en/docs/server_manual/config.html>
- WMS 服务：<https://docs.qgis.org/latest/en/docs/server_manual/services/wms.html>
- WFS 服务：<https://docs.qgis.org/latest/en/docs/server_manual/services/wfs.html>
- WMTS 服务：<https://docs.qgis.org/latest/en/docs/server_manual/services/wmts.html>
- 容器化部署：<https://docs.qgis.org/latest/en/docs/server_manual/containerized_deployment.html>

---

## 相关技能

- **pyqgis** — 服务端插件与 Python 自动化：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **qgis-process** — 桌面端处理算法与批处理：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **geoserver** — 另一套 OGC 服务方案（Java，Web UI 管理）：[../geoserver/SKILL.md](../geoserver/SKILL.md)
- **postgis** — QGIS Server 常用矢量数据源：[../postgis/SKILL.md](../postgis/SKILL.md)

---

## AI 使用建议

### 关键注意事项

- **`MAP` 必填**：几乎所有 QGIS 扩展请求都要求 `MAP` 指向存在的项目文件；用 `QGIS_PROJECT_FILE` 可设默认值。
- **版本匹配**：生成项目的 Desktop 与服务端版本尽量一致，跨大版本先在小环境验证。
- **日志优先 stderr**：`QGIS_SERVER_LOG_FILE` 已废弃，统一用 `QGIS_SERVER_LOG_STDERR`。
- **发布开关**：图层是否出现在服务中取决于项目 `OWS Server` 页的 `published`/`queryable` 设置，而非仅由 URL 决定。

### 常见配置模式

```text
QGIS Desktop 项目 (.qgz)
  └── 项目属性 ▸ QGIS Server / OWS Server ──→ 启用 WMS/WFS/WMTS
        └── FastCGI (qgis_mapserv.fcgi)
              ├── Apache mod_fcgid
              ├── Nginx + spawn-fcgi / fcgiwrap
              └── Docker (qgis-server + nginx)
                    └── MAP / QGIS_PROJECT_FILE + QGIS_SERVER_* 环境变量
```

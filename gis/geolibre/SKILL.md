---
name: geolibre
description: "Use when scripting or self-hosting the GeoLibre GIS app — geolibre Python anywidget (Map/add_geojson/add_cog/save_project), geolibre-mcp stdio server for AI agents, ghcr.io/opengeos/geolibre Docker image, DuckDB-WASM SQL workspace, ?data= and ?url= deep links; also for a blank window on Linux WebKitGTK, sidecar path not allowed from GEOLIBRE_CONVERSION_ROOTS, and Jupyter relay not connected. GeoLibre 3.5.1."
tags:
  - geolibre
  - gis
  - python
  - jupyter
  - mcp
  - duckdb
  - docker
  - webgis
  - tauri
  - geospatial
---

> **项目地址：** <https://github.com/opengeos/GeoLibre>
>
> **官方文档：** <https://geolibre.app/getting-started/>
>
> **在线版：** <https://web.geolibre.app>
>
> **PyPI：** geolibre 3.5.1（要求 Python >= 3.11，截至 2026-10）；conda-forge 渠道为 3.5.0
>
> **许可证：** MIT

## 概述

GeoLibre 是一个云原生 GIS 应用，同一份代码可运行在浏览器、桌面（Tauri v2）、移动端与 Jupyter Notebook 里。它把地图渲染、矢量/栅格/点云浏览、SQL 分析与上千个地理处理工具装进一个前端应用，数据默认留在本机。

对脚本与自动化最相关的四个入口：

- **Python 包**：geolibre.Map（anywidget）把整个应用嵌进 Notebook，并暴露 leafmap 风格的 API
- **MCP 服务器**：geolibre-mcp 以无头方式读写 .geolibre.json 工程，供 AI 客户端调用
- **Docker 镜像**：ghcr.io/opengeos/geolibre:latest 自托管 Web 版，可选 sidecar 与 Basic Auth
- **SQL 工作区**：DuckDB-WASM 加 spatial 扩展，把地图上的每个矢量图层当成 SQL 表

技术栈为 Tauri v2 + React + TypeScript + MapLibre GL JS + DuckDB-WASM Spatial + deck.gl；渲染引擎可在 MapLibre、Mapbox、CesiumJS、ArcGIS 之间切换。地理处理工具（地形、水文、点云、遥感、矢量分析）通过 WebAssembly 在浏览器里执行，不需要服务端。

## 环境准备

### 路径一：零安装（浏览器）

访问 <https://web.geolibre.app>。网页版可读浏览器能选择的数据、URL 服务、COG 与远程 GeoParquet，但没有本地文件对话框，也不能读本地 MBTiles/栅格。

### 路径二：桌面应用

| 平台 | 命令 / 入口 |
|------|-------------|
| Windows（Store，推荐） | <https://apps.microsoft.com/detail/9nwt67rv531x> |
| Windows（winget，未签名构建） | `winget install OpenGeos.GeoLibre` |
| macOS（Homebrew Cask） | `brew install --cask geolibre` |
| Arch / Manjaro | `yay -S geolibre-bin` |
| Fedora / RHEL（COPR） | `sudo dnf copr enable giswqs/geolibre && sudo dnf install geolibre` |
| Flatpak | `flatpak install flatpark app.geolibre.GeoLibre` |
| Debian / Ubuntu | `sudo apt install ./GeoLibre.Desktop_<version>_amd64.deb` |

验证：启动后 **Help → About** 核对版本为 3.5.1，**Help → Diagnostics** 应无红色错误项。

### 路径三：Python 包（Notebook / 脚本）

```bash
pip install geolibre==3.5.1

# 或 conda-forge
conda install -c conda-forge geolibre

# 可选 extras
pip install "geolibre[dash]"      # DashMap 组件
pip install "geolibre[mcp]"       # geolibre-mcp 控制台脚本
```

```python
from geolibre import Map
print(Map.__module__)   # 能 import 即为安装成功
```

### 路径四：Docker 自托管

```bash
docker pull ghcr.io/opengeos/geolibre:latest
docker run --rm -p 8080:80 ghcr.io/opengeos/geolibre:latest
# 打开 http://localhost:8080
```

需要 sidecar（转换、栅格、PostGIS 等本地工具）时挂载数据目录并限制可访问路径：

```bash
docker run --rm -p 8080:80 \
  -v "$PWD/data:/data" \
  -e GEOLIBRE_CONVERSION_ROOTS=/data \
  ghcr.io/opengeos/geolibre:latest
```

加共享密码（应用与 /sidecar 都启用 HTTP Basic Auth，/healthz 除外）：

```bash
docker run --rm -p 8080:80 \
  -e GEOLIBRE_AUTH_USER=admin \
  -e GEOLIBRE_AUTH_PASSWORD='change-me' \
  ghcr.io/opengeos/geolibre:latest
```

### 路径五：源码运行

```bash
git clone https://github.com/opengeos/GeoLibre.git
cd GeoLibre
npm install                 # 需要 Node 22+
npm run dev                 # 浏览器开发服务器 http://localhost:5173
npm run tauri:dev           # 桌面应用（需要 Rust 工具链）
npm run build               # Web 生产构建
```

## 核心接口

### Python：geolibre.Map

| 方法 | 说明 |
|------|------|
| Map(center=(lng, lat), zoom=4) | 创建内嵌应用；参数决定初始视图 |
| add_geojson(data, name=, **style) | 加矢量图层，接受 URL、dict、GeoDataFrame、JSON 字符串 |
| add_tile_layer(url, name=, attribution=) | XYZ 栅格瓦片 |
| add_cog(url, name=, colormap=) | 云优化 GeoTIFF |
| add_basemap(name) | 切换底图（如 "dark"） |
| set_center(lng, lat, zoom=) | 移动相机 |
| save_project(path) / load_project(path) | 读写 .geolibre.json 工程 |
| to_project() | 取当前工程状态（dict），用于回读 UI 侧编辑 |

```python
from geolibre import Map

m = Map(center=(-100, 40), zoom=4)
m.add_geojson("https://example.com/data.geojson", name="Data")
m.add_tile_layer(
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    name="OpenStreetMap",
    attribution="(c) OpenStreetMap contributors",
)
m.add_cog("https://example.com/dem.tif", name="DEM", colormap="terrain")
m.add_basemap("dark")
m.set_center(-120, 47, zoom=8)
m.save_project("my-map.geolibre.json")
m        # 最后一行放在单元格末尾才会渲染
```

工程状态双向同步：Python 加的图层会出现在 UI，UI 里平移/缩放后再 to_project() 能读回新的 mapView.center。

```python
m2 = Map()
m2.load_project("my-map.geolibre.json")
print(m2.to_project()["mapView"]["center"])
```

### Python：Google Earth Engine 图层

```bash
pip install earthengine-api
```

```python
import ee
ee.Authenticate()                          # 每台机器一次
ee.Initialize(project="your-gcp-project")

from geolibre import Map
m = Map()
m.add_ee_layer(ee.Image("USGS/SRTMGL1_003"), {"min": 0, "max": 3000}, name="SRTM")
m
```

### MCP 服务器：geolibre-mcp

无头写工程：不需要浏览器、不需要运行中的应用，产出与桌面/网页版能加载的工程同构。

```bash
pip install "geolibre[mcp]"
geolibre-mcp --root ~/maps
```

| 参数 / 变量 | 说明 |
|-------------|------|
| --root | 可重复，声明工作区根目录 |
| GEOLIBRE_MCP_ROOTS | 环境变量版，冒号分隔（Windows 用分号） |
| --transport | stdio（默认，客户端 spawn 用）、streamable-http、sse |

客户端配置（Claude Desktop 等）：

```json
{
  "mcpServers": {
    "geolibre": {
      "command": "geolibre-mcp",
      "args": ["--root", "C:/Users/you/maps"]
    }
  }
}
```

Claude Code 一行安装：

```bash
claude mcp add geolibre -- geolibre-mcp --root ~/maps
```

常用工具分组：

| 分组 | 工具 |
|------|------|
| 工程生命周期 | create_project、describe_project、list_catalog |
| 加图层 | add_geojson_layer、add_vector_layer、add_raster_layer、add_tile_layer、add_ogc_layer、add_3d_tiles_layer |
| 编辑 | update_layer、remove_layer、style_layer、set_layer_metadata、set_layer_filter |
| 取景与装饰 | set_view、set_basemap、add_legend、add_colorbar、add_swipe |
| 导出 | export_html（独立页面）、show_map（支持 MCP Apps 的客户端内联预览） |
| 实时地图 | live_status、live_fly_to、live_add_geojson、live_run_algorithm |

list_catalog 应该是第一个调用的工具：底图、色带、图例预设、插件 id 都以它为准，猜错名字不会报错，只会静默不生效。

工作区安全模型（决定为什么有些路径写不进去）：

| 闸门 | 规则 |
|------|------|
| 路径解析 | 每次调用的路径都按允许根解析，根之外与"根内指向根外的符号链接"一律拒绝 |
| 扩展名 | 只写 .json（工程）或 .html（导出） |
| 覆盖 | 不带 overwrite 不覆盖已存在文件 |
| 大小 | 内联 GeoJSON 不超过 50 MB，工程文件读取不超过 256 MB |

给它一个专门放地图的目录，不要给家目录。

### SQL 工作区（DuckDB-WASM）

**Processing → SQL Workspace** 打开，面板停靠在地图下方。地图上每个矢量图层同时是一张 SQL 表：

- 表名规则：小写、非字母数字压成下划线、数字开头加 t_ 前缀、保留字加前缀、重名追加 _2
- 几何列名：DuckDB 与 PostGIS 引擎为 geom，Sedona 为 geometry
- 支持三种引擎：DuckDB（默认，可直读远程文件）、PostGIS（PGlite）、Apache Sedona（CereusDB，单层上限 5 万要素）

```sql
-- 两个图层直接 JOIN：城市点落在哪个国家
SELECT c.NAME AS country, p.name AS city, p.geom
FROM cities p
JOIN countries c
  ON ST_Intersects(c.geom, p.geom)
WHERE c.CONTINENT = 'Africa';
```

结果区可 **Add as layer**（物化）或 **Add as query layer**（活查询，仅 DuckDB）。

### Web 版 URL 参数（分享与嵌入）

| 参数 | 作用 |
|------|------|
| url= | 打开一个公开 .geolibre 工程 |
| data= | 直接打开托管数据，可重复（GeoJSON、GeoParquet、PMTiles、COG、LiDAR 等） |
| style= | 给 data= 应用样式 JSON |
| layout=compact | 图标化工具栏，适合窄嵌入 |
| layout=viewer | 只读查看器预设 |
| panels=none / maponly | 隐藏面板 / 完全去掉工具栏与状态栏 |

```text
https://web.geolibre.app/?data=https://example.org/places.geojson&layout=compact&panels=none
```

### 关键环境变量

| 变量 | 作用 |
|------|------|
| GEOLIBRE_CONVERSION_ROOTS | sidecar 允许读写的目录白名单（Docker 镜像内默认 /data） |
| GEOLIBRE_DISABLE_SIDECAR=1 | 纯静态 Web 行为，不起 sidecar |
| GEOLIBRE_AUTH_USER / GEOLIBRE_AUTH_PASSWORD | nginx 层 HTTP Basic Auth |
| GEOLIBRE_CAPABILITIES | 逗号分隔的能力白名单（或 none），用于只读门户/展厅 |
| GEOLIBRE_EMBED_ORIGINS | 允许通过 iframe/postMessage 驱动应用的来源 |
| GEOLIBRE_STORE_BUILD / GEOLIBRE_MAS_BUILD | 商店构建开关（移除自动更新 / sidecar 能力） |

## 典型工作流：MCP 生成工程 → 桌面打开 → 导出独立 HTML

目标：不打开应用，用 AI 客户端生成一张城市地图，人工在桌面版微调后导出为可分发的单页。

**步骤 1：装 MCP 并准备目录**

```bash
pip install "geolibre[mcp]"
mkdir -p ~/maps
claude mcp add geolibre -- geolibre-mcp --root ~/maps
```

**步骤 2：让客户端依次调用工具（工具序列）**

```text
list_catalog()                                   # 先查有哪些底图/色带/插件 id
create_project(name="beijing", center=[116.39, 39.90], zoom=10)
add_geojson_layer(url="https://example.org/poi.geojson", name="POI")
style_layer(layer="POI", fillColor="#f97316", circleRadius=6)
set_view(center=[116.39, 39.90], zoom=11)        # 精确取景用 center+zoom，不要用 bbox
```

产出一个 .geolibre.json（工作区内，扩展名只能是 .json 或 .html）。

**步骤 3：桌面版打开并微调**

双击工程文件（桌面安装包已注册文件关联），调整样式、加图例（add_legend / set_map_legend），必要时用 **Project → Save** 写回。

**步骤 4：导出可分发的 HTML**

```text
export_html(path="beijing.html", app_url="https://web.geolibre.app")
```

export_html 会剥掉凭据；指向本地文件的图层在别人机器上不会加载，要分享就用托管 URL。app_url 是信任边界——工程内容会被 POST 到那个来源，只填你本来就信任的地址。

**步骤 5：验证**

```bash
python -c "import json;d=json.load(open('beijing.geolibre.json'));print(len(d.get('layers',[])),'layers')"
```

再在浏览器打开 beijing.html，确认底图与图层能渲染、点击要素有弹窗。

## 最佳实践

1. **生成用 MCP 或 Python 包，审阅用 GUI**：无头路径可重复、可测试，GUI 微调难以复现。
2. **工程文件走版本控制**：.geolibre.json 是纯 JSON，diff 友好；大 GeoJSON 放外部 URL 而不是内联。
3. **sidecar 路径走白名单目录**：自托管时把数据挂到 GEOLIBRE_CONVERSION_ROOTS 声明的目录下。
4. **只读门户用能力策略**：GEOLIBRE_CAPABILITIES 受限或 none，配 layout=viewer，避免把编辑能力暴露出去。
5. **嵌入要声明来源**：iframe 驱动需要 GEOLIBRE_EMBED_ORIGINS 白名单，否则命令会被丢弃。
6. **实时工具有前提**：桌面版每次启动后要先打开一次 **Processing → Jupyter Notebook** 启动中继；网页版与 JupyterLite 没有中继。

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Linux 桌面版窗口空白或地图闪烁 | WebKitGTK 的 DMA-BUF 渲染器与驱动不兼容 | 用传统渲染器启动：WEBKIT_DISABLE_DMABUF_RENDERER=1 geolibre-desktop；若被自动降到传统渲染器后很慢，改回 0 再试 |
| 无 AVX 的老 CPU 上窗口永不绘制 | JavaScriptCore 的 WebAssembly JIT 触发 SIGILL | 成对设置 JSC_useWasmOSR=false 与 JSC_useBBQTierUpChecks=false |
| MCP 返回路径不允许或工具直接拒绝 | 路径不在 --root 或 GEOLIBRE_MCP_ROOTS 内，或是指向根外的符号链接 | 把工程目录加进 --root，或把文件移到根内；不要给家目录 |
| geolibre-mcp 不在客户端 PATH 里 | 装在 virtualenv 中，客户端 spawn 时用系统 PATH | 配置里改用解释器：command 指向 venv 的 python，args 用 -m geolibre.mcp --root ... |
| live_ 工具报没连接或超时 | 桌面版中继没启动，或大 FeatureCollection 超过约 5 秒 | 先打开一次 Processing → Jupyter Notebook；超时不代表失败，用 live_list_layers 回查而不是重发 |
| add_geojson / list_layers 返回 None 或抛 GeoLibreNotConnectedError | 没有窗口在监听，或读回在网页版不可用 | 确认至少一个桌面窗口连到同一 Jupyter 服务器；同步读回只在桌面版可用 |
| SQL 工作区里 ST_Intersects 报函数不存在 | 引擎未加载空间扩展，或图层未按几何列注册 | 检查 Queryable layers 里的表名与几何列名（DuckDB/PostGIS 是 geom，Sedona 是 geometry） |
| 自托管转换报路径不允许 | 触到 GEOLIBRE_CONVERSION_ROOTS 白名单 | 输出到白名单目录内，或调整该变量 |
| 网页版打开本地文件后刷新就没了 | 浏览器安全模型不给持久文件路径 | 用桌面版做本地文件工作，或用 data= 指向托管 URL |
| 沙盒（Mac App Store）版加载松散 Shapefile 丢属性 | 沙盒授权只覆盖显式选择的文件 | 一次选中所有分片（.shp/.dbf/.prj）或用压缩包 |

## DeepSeek Harness 使用建议

- **加载技能**：skill("geolibre")；技能目录只读，生成的 .geolibre.json、.html 与脚本写到会话工作区。
- **先确认版本与入口**：pip show geolibre 看版本，geolibre-mcp --help 看参数；桌面版看 Help → About。教程可能对应 3.4，遇到差异以 3.5.1 的实际行为为准。
- **装包前确认 Python 版本**：PyPI 的 geolibre 3.5.1 要求 Python >= 3.11；低版本解释器会直接安装失败，不要误判为网络问题。
- **MCP 路径要显式**：Windows 上 JSON 里写正向斜杠（C:/Users/you/maps），反斜杠需成对转义，容易出错。
- **验证产物**：写完工程先 json.load 检查图层数与 mapView，再用浏览器打开导出的 HTML 看渲染；不要只看工具返回的成功。
- **写操作确认**：export_html、save_project 与 MCP 的覆盖写会改写磁盘文件；覆盖前确认目标，或先写新文件名。

## 相关技能

- **duckdb-spatial** — SQL 工作区背后的空间分析引擎：[../duckdb-spatial/SKILL.md](../duckdb-spatial/SKILL.md)
- **openlayers** — 自建 Web 地图前端时的核心库：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **cesiumjs** — GeoLibre 的 3D 球渲染引擎之一：[../cesiumjs/SKILL.md](../cesiumjs/SKILL.md)
- **qgis-process** — 桌面 GIS 的另一种无头批处理路径：[../qgis-process/SKILL.md](../qgis-process/SKILL.md)
- **opengis-all** — 全流程 GIS 索引：[../opengis-all/SKILL.md](../opengis-all/SKILL.md)

## 参考资源
- 官方文档：<https://geolibre.app/getting-started/>
- 下载页：<https://geolibre.app/downloads/>
- Python 包文档：<https://geolibre.app/python/>
- 功能列表：<https://geolibre.app/features/>
- 渲染引擎对比：<https://geolibre.app/user-guide/rendering-engines/>

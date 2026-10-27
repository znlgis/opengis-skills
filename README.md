# opengis-skills

> 面向 **AI 编程助手 / Agent** 的开源 GIS、CAD、C#、AI、IoT、3D 技能及通用工具（Skill）集合。
>
> 本仓库与 [znlgis.github.io](https://github.com/znlgis/znlgis.github.io) 上游博客分类完全对齐，便于双向导航与学习。

---

## 🤖 AI 入口提示

> **对于 AI 编程助手（Claude / Cursor / Cline / Copilot Chat / DeepSeek 等）：**
>
> 本仓库的主入口是根目录下的 **[`SKILL.md`](./SKILL.md)**。该文件包含完整的技能索引、标签搜索系统和按需加载指南，是 AI 工具理解和使用本仓库的**第一站**。
>
> - 加载 **根 `SKILL.md`** → 获取全局索引、标签导航和加载策略
> - 加载 **分类 `*/SKILL.md`**（如 `gis/SKILL.md`）→ 获取某个领域的技能概要
> - 加载 **项目 `*/<project>/SKILL.md`** → 获取单个工具的深度知识
>
> 推荐先用 `@SKILL.md` 或 `@gis/gdal/SKILL.md` 等方式按需加载，避免全量注入导致上下文膨胀。

---

## 🚀 快速开始

### AI 工具如何使用本仓库

本仓库采用 **三层索引结构**，AI 工具可根据用户需求灵活选择加载层级：

| 层级 | 文件 | 内容 | 适用场景 |
|------|------|------|---------|
| **L1 全局入口** | [`SKILL.md`](./SKILL.md)（根目录） | 114 个技能的全量索引、标签搜索、按场景推荐 | 不确定具体工具时，先加载此文件获取全貌 |
| **L2 分类索引** | `gis/SKILL.md`、`cad/SKILL.md`、`csharp/SKILL.md`、`ai/SKILL.md`、`iot/SKILL.md`、`3d/SKILL.md`、`demos/SKILL.md`、`others/SKILL.md` | 某个分类下的技能列表与领域概述 | 明确大类（如 GIS、CAD）但不确定具体工具 |
| **L3 项目技能** | `<category>/<project>/SKILL.md` | 单个开源项目的深度知识（API、工作流、FAQ） | 已确定使用哪个工具，需要精准的编码指导 |

### 典型使用流程

```
用户提问："帮我把 Shapefile 转成 GeoJSON"
    ↓
AI 加载 @SKILL.md（根），搜索标签 #conversion #vector
    ↓ 或直接定位
AI 加载 @gis/gdal/SKILL.md，获取 GDAL 命令行转换指导
    ↓
AI 根据 SKILL.md 中的 API/命令示例生成代码
```

### 加载方式速查

```bash
# Claude Code / Claude
@SKILL.md                    # 加载根入口（推荐首次使用）
@gis/gdal/SKILL.md           # 加载 GDAL 技能
@gis/opengis-all/SKILL.md    # 加载 GIS 全流程索引

# Cursor
在 .cursorrules 中引用或在对话中使用 @file 语法

# Cline / Roo Code
直接使用 @ 语法或通过 .clinerules 配置

# VS Code Copilot Chat
通过 /addContext 或 .github/copilot-instructions.md 配置

# DeepSeek Chat
对话中粘贴 SKILL.md 内容或引用文件路径
```

---

## 📂 目录结构

```
opengis-skills/
├── SKILL.md         # 🌐 根入口：全局索引 + 标签搜索 + 使用指南
├── gis/             # GIS 类（40 个）
│   └── SKILL.md     # GIS 分类索引
├── cad/             # CAD 类（21 个）
│   └── SKILL.md     # CAD 分类索引
├── csharp/          # C# 框架/库（12 个）
│   └── SKILL.md     # C# 分类索引
├── ai/              # AI 智能体/平台（17 个）
│   └── SKILL.md     # AI 分类索引
├── iot/             # 物联网（4 个）
│   └── SKILL.md     # IoT 分类索引
├── 3d/              # 3D / 高斯泼溅 / 全景 / BIM / CSG（6 个）
│   └── SKILL.md     # 3D 分类索引
├── demos/           # 项目演示（4 个：全景联动 / 地图大屏 / 水务前端 / GeoServer 图层树）
│   └── SKILL.md     # demos 分类索引
└── others/          # 其它（10 个）
    └── SKILL.md     # Others 分类索引
```

每个 SKILL 都是一个独立目录，包含一份 `SKILL.md`，可被 Claude / Cursor / Cline / Copilot Chat / VS Code 等 AI 工具按需加载，作为「领域知识」注入到对话中，从而获得更准确的代码生成与问题排查能力。

---

## 📑 分类索引文件

除了根目录的 [`SKILL.md`](./SKILL.md) 作为全局入口外，每个分类目录下也设有 **分类索引文件**（`<category>/SKILL.md`），作为该领域的二级入口：

| 分类索引 | 涵盖内容 | 适用场景 |
|---------|---------|---------|
| [`gis/SKILL.md`](./gis/SKILL.md) | 40 个 GIS 技能概要（GDAL、QGIS、GeoServer、PostGIS、JTS、OpenGisDAF 等） | 空间数据处理、地图服务、Web GIS |
| [`cad/SKILL.md`](./cad/SKILL.md) | 21 个 CAD 技能概要（FreeCAD、OCCT、OpenSCAD、KiCad 等） | 参数化建模、几何运算、BIM/PCB |
| [`csharp/SKILL.md`](./csharp/SKILL.md) | 12 个 C#/.NET 技能概要（Furion、NPOI、SqlSugar、Sentry、Serilog、Polly、Hangfire 等） | .NET Web 开发、ORM、Office 操作、错误追踪 |
| [`ai/SKILL.md`](./ai/SKILL.md) | 17 个 AI 技能概要（Dify、LangChain、LlamaIndex、Ollama、vLLM、CrewAI、MinerU、Pi、OpenCode、DeepSeek Harness、DocuTranslate 等） | LLM 应用、智能体、文档解析、推理服务 |
| [`iot/SKILL.md`](./iot/SKILL.md) | 4 个 IoT 技能概要（Raspberry Pi Pico、Node-RED、Home Assistant、ESPHome） | 嵌入式、传感器、流编排 |
| [`3d/SKILL.md`](./3d/SKILL.md) | 6 个 3D 技能概要（SuperSplat 高斯泼溅编辑器、Ara3D-SDK 高性能 .NET 三维/BIM 库、Photo-Sphere-Viewer 360° 全景、Elements BIM 编程生成库、OpenCSG.NET CSG 建模库、Open3D 三维数据处理） | 3D 高斯泼溅、AEC/BIM、全景展示、CSG 建模 |
| [`others/SKILL.md`](./others/SKILL.md) | 10 个其它技能概要（Go 语言、RobotGo、robotgo-flow、邮件平台、Java 脚手架、acme.sh、CHAGS 儿童游戏合集、Docker Compose、BambooBuddy 儿童养成游戏、FFmpeg） | 通用工具、Go 开发、自动化、SSL 证书、H5 游戏 |
| [`demos/SKILL.md`](./demos/SKILL.md) | 4 个演示项目技能概要（map-360-demo 全景地图联动、vue3-map-dashboard 可视化大屏、ai-water-front 智慧水务前端、openlayers-vue3-demo 图层树） | Vue3 演示工程、地图可视化、学习参考 |

> **设计理念：** 分类索引文件让 AI 工具在**已知用户需求领域**时，无需加载 114 个技能的全量索引（根 `SKILL.md`），只需加载对应分类索引即可快速定位目标技能。如果用户跨领域提问，再回退到根 `SKILL.md`。

---

## 🌍 GIS 类（gis/）

地理信息系统、空间数据处理、地图服务与渲染相关。

| SKILL | 简介 |
|-------|------|
| [opengis-all](./gis/opengis-all/SKILL.md) | 一站式 GIS 索引：GDAL + QGIS + GeoServer 全流程 |
| [gdal](./gis/gdal/SKILL.md) | GDAL 命令行：栅格/矢量处理事实标准 |
| [gdal-api](./gis/gdal-api/SKILL.md) | GDAL/OGR 编程 API（C/C++/Python/.NET） |
| [geotools](./gis/geotools/SKILL.md) | Java GIS 工具集 |
| [geoserver](./gis/geoserver/SKILL.md) | 开源地图服务器（WMS/WFS/WMTS/WCS） |
| [geoserver-rest-api](./gis/geoserver-rest-api/SKILL.md) | GeoServer REST API 自动化管理 |
| [geoserver-cloud](./gis/geoserver-cloud/SKILL.md) | GeoServer 云原生微服务架构 |
| [pyqgis](./gis/pyqgis/SKILL.md) | QGIS Python 二次开发 |
| [qgis-process](./gis/qgis-process/SKILL.md) | QGIS 命令行批处理 |
| [postgis](./gis/postgis/SKILL.md) | PostgreSQL 空间数据库扩展 |
| [cesiumjs](./gis/cesiumjs/SKILL.md) | 高性能 3D 地球可视化 |
| [openlayers](./gis/openlayers/SKILL.md) | 高性能 Web 2D 地图库 |
| [geopandas](./gis/geopandas/SKILL.md) | Python 矢量空间数据处理 |
| [shapely](./gis/shapely/SKILL.md) | Python 几何对象与运算 |
| [jts](./gis/jts/SKILL.md) | Java Topology Suite 几何引擎 |
| [nettopologysuite](./gis/nettopologysuite/SKILL.md) | JTS 的 .NET 移植 |
| [geometry-api-java](./gis/geometry-api-java/SKILL.md) | Esri Geometry API for Java |
| [geometry-api-net](./gis/geometry-api-net/SKILL.md) | Esri Geometry API for .NET |
| [sharpmap](./gis/sharpmap/SKILL.md) | .NET WinForms/Web 地图渲染库 |
| [mapsui](./gis/mapsui/SKILL.md) | .NET 跨平台地图控件 |
| [opengis-utils-for-java](./gis/opengis-utils-for-java/SKILL.md) | OpenGIS Java 实用工具集 |
| [opengis-utils-for-net](./gis/opengis-utils-for-net/SKILL.md) | OpenGIS .NET 实用工具集 |
| [geopipe-agent](./gis/geopipe-agent/SKILL.md) | GIS 数据流水线 Agent（YAML 驱动） |
| [opengis-daf](./gis/opengis-daf/SKILL.md) | 方案驱动 GIS 分析与质检框架（.NET） |
| [mapserver](./gis/mapserver/SKILL.md) | MapServer：C 语言 OGC 地图服务引擎 |
| [qgis-server](./gis/qgis-server/SKILL.md) | QGIS Server：发布 QGIS 工程为 OGC 服务 |
| [leaflet](./gis/leaflet/SKILL.md) | Leaflet：轻量级 Web 2D 地图库 |
| [proj](./gis/proj/SKILL.md) | PROJ：坐标转换与投影引擎 |
| [grass-gis](./gis/grass-gis/SKILL.md) | GRASS GIS：模块化地理处理套件 |
| [pdal](./gis/pdal/SKILL.md) | PDAL：点云与 LiDAR 处理流水线 |
| [mapbox-gl-js](./gis/mapbox-gl-js/SKILL.md) | Mapbox GL JS：矢量瓦片 WebGL 地图 |
| [deck-gl](./gis/deck-gl/SKILL.md) | deck.gl：GPU 大规模数据可视化 |
| [geolibre](./gis/geolibre/SKILL.md) | 云原生 GIS 应用：浏览器/桌面/Notebook/MCP |
| [geonode](./gis/geonode/SKILL.md) | 地理空间 CMS：Django + GeoServer + PostGIS 数据门户 |
| [duckdb-spatial](./gis/duckdb-spatial/SKILL.md) | DuckDB 空间扩展：空间 SQL 与 GeoParquet |
| [spatialite](./gis/spatialite/SKILL.md) | SQLite 空间扩展：单文件空间数据库 |
| [whitebox-tools](./gis/whitebox-tools/SKILL.md) | Rust 地形/水文/LiDAR 分析引擎（CLI + Python） |
| [kepler-gl](./gis/kepler-gl/SKILL.md) | React/Redux 地理数据可视化应用与组件库 |
| [projnet4geoapi](./gis/projnet4geoapi/SKILL.md) | .NET 坐标参考系与投影引擎（NuGet ProjNet 2.x） |
| [brutile](./gis/brutile/SKILL.md) | .NET 瓦片访问库（HTTP 瓦片源 + MBTiles 离线） |

## 📐 CAD 类（cad/）

计算机辅助设计、参数化建模、几何运算、BIM 与 PCB 等。

| SKILL | 简介 |
|-------|------|
| [ifoxcad](./cad/ifoxcad/SKILL.md) | AutoCAD .NET 二次开发框架 |
| [fy_layout](./cad/fy_layout/SKILL.md) | 施工场地布置插件（LightCAD 二次开发示例） |
| [clipper2](./cad/clipper2/SKILL.md) | 高性能 2D 多边形布尔运算与偏移 |
| [clipper1](./cad/clipper1/SKILL.md) | Clipper 1.x（旧版本，仍广泛使用） |
| [chili3d](./cad/chili3d/SKILL.md) | 纯 Web 3D CAD（基于 OCCT.js） |
| [libredwg](./cad/libredwg/SKILL.md) | 自由 DWG 读写库 |
| [qcad](./cad/qcad/SKILL.md) | 开源 2D CAD（DXF 编辑器） |
| [astral3d](./cad/astral3d/SKILL.md) | 工业 3D 可视化与编辑框架 |
| [kicad](./cad/kicad/SKILL.md) | 开源 EDA/PCB 设计套件 |
| [solvespace](./cad/solvespace/SKILL.md) | 轻量参数化 2D/3D CAD |
| [cadquery](./cad/cadquery/SKILL.md) | Python 脚本化参数化 3D CAD |
| [librecad](./cad/librecad/SKILL.md) | 开源 2D CAD（C++/Qt） |
| [freecad](./cad/freecad/SKILL.md) | 开源参数化 3D CAD/BIM |
| [occt](./cad/occt/SKILL.md) | Open CASCADE Technology 几何内核 |
| [openscad](./cad/openscad/SKILL.md) | 脚本式 3D CAD（CSG） |
| [xbim](./cad/xbim/SKILL.md) | .NET BIM/IFC 工具集 |
| [lightcad](./cad/lightcad/SKILL.md) | 飞扬集成设计平台：C#/.NET 开源 CAD/BIM |
| [lightningcad](./cad/lightningcad/SKILL.md) | 建筑围护深化设计插件（AutoCAD/ZWCAD） |
| [tongwen](./cad/tongwen/SKILL.md) | CAD/BIM 工程图纸无损翻译套件（AutoCAD 2019-2026） |
| [design-drawing-svg-md](./cad/design-drawing-svg-md/SKILL.md) | 设计图 SVG+MD 双载体记录（钢结构施工图→可复现图纸描述） |
| [blender](./cad/blender/SKILL.md) | Blender：Python 脚本化 3D 建模与导出 |

## 🛠️ C# 类（csharp/）

.NET 生态常用框架、ORM、报表与保护工具。

| SKILL | 简介 |
|-------|------|
| [admin-net-backend](./csharp/admin-net-backend/SKILL.md) | Admin.NET 后端（基于 Furion） |
| [admin-net-frontend](./csharp/admin-net-frontend/SKILL.md) | Admin.NET 前端（Vue 3） |
| [furion](./csharp/furion/SKILL.md) | .NET 极简企业级 Web 框架 |
| [sod](./csharp/sod/SKILL.md) | PDF.NET SOD：ORM + SQL-MAP + OQL |
| [npoi](./csharp/npoi/SKILL.md) | .NET Excel/Word 读写 |
| [reogrid](./csharp/reogrid/SKILL.md) | .NET 电子表格控件 |
| [sqlsugar](./csharp/sqlsugar/SKILL.md) | 国产高性能多数据库 ORM |
| [dotnet-reactor](./csharp/dotnet-reactor/SKILL.md) | .NET 商业级混淆/加壳/授权 |
| [sentry](./csharp/sentry/SKILL.md) | Sentry .NET SDK：错误追踪与性能监控 |
| [serilog](./csharp/serilog/SKILL.md) | Serilog：结构化日志（sink / enricher / JSON） |
| [polly](./csharp/polly/SKILL.md) | Polly：v8 ResiliencePipeline 重试/超时/断路器 |
| [hangfire](./csharp/hangfire/SKILL.md) | Hangfire：持久化后台任务与 Cron 调度 |

## 🤖 AI 类（ai/）

LLM 应用、智能体、个人 AI 助手与 AI 编程方法论。

| SKILL | 简介 |
|-------|------|
| [dify](./ai/dify/SKILL.md) | 开源 LLM 应用开发平台 |
| [oh-my-openagent](./ai/oh-my-openagent/SKILL.md) | OpenCode 多模型编排插件（Agent Harness） |
| [superpowers-zh](./ai/superpowers-zh/SKILL.md) | 中文 AI 编程方法论 Skills 集合 |
| [hermes-agent](./ai/hermes-agent/SKILL.md) | 自学习通用型 AI 智能体（终端优先） |
| [openclaw](./ai/openclaw/SKILL.md) | 多通道个人 AI 助手 Gateway |
| [pi](./ai/pi/SKILL.md) | 极简可扩展终端 AI 编码代理（Agent Harness） |
| [opencode](./ai/opencode/SKILL.md) | 模型无关的终端 AI 编码代理（配置即代码） |
| [docutranslate](./ai/docutranslate/SKILL.md) | 基于 LLM 的本地多格式文件翻译工具 |
| [deepseek-harness](./ai/deepseek-harness/SKILL.md) | DeepSeek Harness（dsh）：插件化智能体框架 |
| [my-opencode-deepseek-config](./ai/my-opencode-deepseek-config/SKILL.md) | OpenCode × DeepSeek V4 最优配置 |
| [langchain](./ai/langchain/SKILL.md) | LangChain：LLM 应用与 Agent 框架 |
| [ollama](./ai/ollama/SKILL.md) | Ollama：本地大模型推理运行时 |
| [llamaindex](./ai/llamaindex/SKILL.md) | LlamaIndex：RAG 索引与查询框架 |
| [huggingface-transformers](./ai/huggingface-transformers/SKILL.md) | Transformers：模型推理与微调框架 |
| [vllm](./ai/vllm/SKILL.md) | 高吞吐 LLM 推理服务（OpenAI 兼容 API） |
| [crewai](./ai/crewai/SKILL.md) | 角色化多 Agent 协作框架（Agent/Task/Crew/Flows） |
| [mineru](./ai/mineru/SKILL.md) | 文档解析引擎：PDF/Office → Markdown/JSON |

## 📡 IoT 类（iot/）

| SKILL | 简介 |
|-------|------|
| [ke3036-keyes-pico](./iot/ke3036-keyes-pico/SKILL.md) | Keyes Raspberry Pi Pico 学习套件 |
| [node-red](./iot/node-red/SKILL.md) | Node-RED：低代码 IoT 数据流编排 |
| [home-assistant](./iot/home-assistant/SKILL.md) | Home Assistant：本地优先家居自动化平台 |
| [esphome](./iot/esphome/SKILL.md) | ESPHome：YAML 生成 ESP32/ESP8266 固件 |

## 🧊 3D 类（3d/）

3D 高斯泼溅（3DGS）、Web 三维可视化与高性能 AEC/BIM 三维数据处理。

| SKILL | 简介 |
|-------|------|
| [supersplat](./3d/supersplat/SKILL.md) | 浏览器端开源 3D 高斯泼溅编辑器（PlayCanvas） |
| [ara3d-sdk](./3d/ara3d-sdk/SKILL.md) | 面向 AEC 的高性能 .NET 三维/BIM 库集合（.NET 8） |
| [photo-sphere-viewer](./3d/photo-sphere-viewer/SKILL.md) | JavaScript 360° 全景照片/球体查看器（Three.js 驱动） |
| [elements](./3d/elements/SKILL.md) | Hypar Elements：纯 C# BIM 编程生成库 |
| [opencsg-net](./3d/opencsg-net/SKILL.md) | OpenCSG.NET：零依赖 .NET CSG 建模库 |
| [open3d](./3d/open3d/SKILL.md) | Open3D：点云与网格处理库 |

## 🎯 项目演示（demos/）

上游博客「项目演示」分类对应的四个可运行示例工程（Vue 3 + Vite）。

| SKILL | 简介 |
|-------|------|
| [map-360-demo](./demos/map-360-demo/SKILL.md) | 360° 全景与 Leaflet 地图双向联动演示（PSV v5） |
| [vue3-map-dashboard](./demos/vue3-map-dashboard/SKILL.md) | 天地图 + Element Plus 企业级可视化大屏 |
| [ai-water-front](./demos/ai-water-front/SKILL.md) | OpenLayers + Dify AI 助手的智慧水务前端 |
| [openlayers-vue3-demo](./demos/openlayers-vue3-demo/SKILL.md) | vue3-openlayers 声明式地图 + GeoServer 图层树 |

## 🗂️ 其它（others/）

| SKILL | 简介 |
|-------|------|
| [billionmail](./others/billionmail/SKILL.md) | 自托管邮件营销与事务邮件平台 |
| [ruoyi-cloud](./others/ruoyi-cloud/SKILL.md) | 若依微服务版 Java 后台脚手架 |
| [acme.sh](./others/acme.sh/SKILL.md) | 纯 Shell 的 ACME 客户端，自动签发/续期 SSL 证书 |
| [go](./others/go/SKILL.md) | Go 语言核心语法与工程实践 |
| [robotgo](./others/robotgo/SKILL.md) | Go 跨平台桌面自动化（RPA）库 |
| [robotgo-flow](./others/robotgo-flow/SKILL.md) | 基于 robotgo 的 YAML 驱动 Windows RPA 框架 |
| [chags](./others/chags/SKILL.md) | 中国历史典故儿童游戏合集（Vue3 + Phaser，17 典故） |
| [docker-compose](./others/docker-compose/SKILL.md) | Docker Compose：多容器应用编排工具 |
| [bamboobuddy](./others/bamboobuddy/SKILL.md) | 儿童日常养成游戏（Vue3 + Phaser，17 章教程） |
| [ffmpeg](./others/ffmpeg/SKILL.md) | FFmpeg：音视频转码、切片与纹理帧提取 |

## 📝 SKILL 编写规范

每个 `<category>/<project>/SKILL.md` 遵循统一规范，便于 AI 工具与人类阅读：

1. **YAML frontmatter**（必填字段）：

   ```yaml
   ---
   name: 项目英文名
   description: Use when <触发条件>. <项目定位>. Covers <关键特性>.   # 英文 "Use when..." 格式，≤500 字符
   tags:                 # 用于 AI 工具按标签搜索技能
     - <语言/平台>
     - <功能领域>
     - <...>
   ---
   ```

   > **`description` 规范：** 采用英文 `Use when...` 格式，描述**何时使用**该技能（而非描述项目本身），遵循 [Anthropic Skill 最佳实践](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills)。分类索引用 `Use when... Index of N skills: ...` 格式。所有 description 均以 `Use when` 开头、第三人称、≤500 字符。
   >
   > **`tags` 字段说明：** 每个 SKILL.md 的 frontmatter 中必须包含 `tags` 数组（**必须使用多行 `- tag` 格式**，不使用内联 `[tag1, tag2]` 格式），列出该技能的关键标签（如 `python`、`geometry`、`cli`、`3d` 等）。这些标签被根 `SKILL.md` 的标签索引系统使用，让 AI 工具可以通过标签快速定位相关技能，无需扫描全部文件。

2. **头部引用块**：项目地址、官方文档、许可证

3. **正文章节**（按需取用，顺序保持稳定）：
   - **概述**：定位、特性矩阵
   - **环境准备 / 安装**
   - **核心 API / 命令**
   - **典型工作流**
   - **最佳实践 / 性能优化**
   - **常见问题（FAQ 表，≥5 行）**
   - **AI 使用建议**（dsh 场景下部分技能写作「DeepSeek Harness 使用建议」，两者等价）
   - **相关技能**
   - **参考资源**

4. **风格**：中文为主，配合代码示例；命令、API、字段使用代码格式
5. **大小**：主文件建议 ≤500 行；超过时将详细参数/示例拆分到 `reference/*.md`（参见 GDAL 拆分示例：[主文件](./gis/gdal/SKILL.md) 500 行 + [矢量工具参考](./gis/gdal/reference/vector-tools.md) + [栅格工具参考](./gis/gdal/reference/raster-tools.md)），主文件与 reference 合计通常 300–1500 行
6. **示例**：基于上游官方文档实地核对，避免编造 API；版本号需以 `npm view` / PyPI JSON / NuGet flatcontainer / GitHub `releases/latest` 实测，并在头块注明「截至 YYYY-MM」
7. **无 emoji、代码块必须带语言标识、正文中文而 API/命令保留英文原文**

参考样板：[`gis/gdal/SKILL.md`](./gis/gdal/SKILL.md)、[`gis/jts/SKILL.md`](./gis/jts/SKILL.md)。

## ✅ 校验工具

提交前在仓库根目录执行：

```bash
# 结构 + frontmatter + 相对链接 + 索引一致性（CI 同款）
python scripts/validate-skills.py .

# 外部链接连通性（可选，需联网；403/SSL 抖动属正常，重点看 404）
python scripts/check-links.py . --workers 32 --timeout 12
```

`validate-skills.py` 会检查：frontmatter 三字段、`name` 与目录名一致、`description` 以 `Use when` 开头且 ≤500 字符全英文、tags 5-10 个且格式合法、L3 必备章节（概述/安装/工作流/FAQ/相关）、FAQ 表格 ≥5 行、无 emoji、代码围栏带语言、单文件 ≤500 行、相对链接可达，以及根 `SKILL.md`、8 个分类索引与 `README.md` 是否覆盖全部技能。

---

## 🔗 相关项目

- [znlgis.github.io](https://github.com/znlgis/znlgis.github.io) — 上游中文教程博客（与本仓库分类一一对应）
- [Anthropic Claude Skills](https://docs.claude.com/) — Skill 概念与规范
- [Cursor Rules](https://docs.cursor.com/) / [Cline Rules](https://github.com/cline/cline) — 客户端约定文件

---

## 📜 License

本仓库自身代码与文档遵循 [LICENSE](./LICENSE)（MIT）。各 SKILL 中引用、介绍的上游开源项目，请以其各自仓库的许可证为准。
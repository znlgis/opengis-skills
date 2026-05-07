# opengis-skills

> 面向 **AI 编程助手 / Agent** 的开源 GIS、CAD、C#、AI、IoT 技能（Skill）集合。
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
| **L1 全局入口** | [`SKILL.md`](./SKILL.md)（根目录） | 56 个技能的全量索引、标签搜索、按场景推荐 | 不确定具体工具时，先加载此文件获取全貌 |
| **L2 分类索引** | `gis/SKILL.md`、`cad/SKILL.md`、`csharp/SKILL.md`、`ai/SKILL.md`、`iot/SKILL.md`、`others/SKILL.md` | 某个分类下的技能列表与领域概述 | 明确大类（如 GIS、CAD）但不确定具体工具 |
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
├── gis/             # GIS 类（23 个）
│   └── SKILL.md     # GIS 分类索引
├── cad/             # CAD 类（17 个）
│   └── SKILL.md     # CAD 分类索引
├── csharp/          # C# 框架/库（8 个）
│   └── SKILL.md     # C# 分类索引
├── ai/              # AI 智能体/平台（5 个）
│   └── SKILL.md     # AI 分类索引
├── iot/             # 物联网（1 个）
│   └── SKILL.md     # IoT 分类索引
└── others/          # 其它（2 个）
    └── SKILL.md     # Others 分类索引
```

每个 SKILL 都是一个独立目录，包含一份 `SKILL.md`，可被 Claude / Cursor / Cline / Copilot Chat / VS Code 等 AI 工具按需加载，作为「领域知识」注入到对话中，从而获得更准确的代码生成与问题排查能力。

---

## 📑 分类索引文件

除了根目录的 [`SKILL.md`](./SKILL.md) 作为全局入口外，每个分类目录下也设有 **分类索引文件**（`<category>/SKILL.md`），作为该领域的二级入口：

| 分类索引 | 涵盖内容 | 适用场景 |
|---------|---------|---------|
| [`gis/SKILL.md`](./gis/SKILL.md) | 23 个 GIS 技能概要（GDAL、QGIS、GeoServer、PostGIS、JTS 等） | 空间数据处理、地图服务、Web GIS |
| [`cad/SKILL.md`](./cad/SKILL.md) | 17 个 CAD 技能概要（FreeCAD、OCCT、OpenSCAD、KiCad 等） | 参数化建模、几何运算、BIM/PCB |
| [`csharp/SKILL.md`](./csharp/SKILL.md) | 8 个 C#/.NET 技能概要（Furion、NPOI、SqlSugar 等） | .NET Web 开发、ORM、Office 操作 |
| [`ai/SKILL.md`](./ai/SKILL.md) | 5 个 AI 技能概要（Dify、Agent 框架、提示词工程） | LLM 应用、Agent 编排 |
| [`iot/SKILL.md`](./iot/SKILL.md) | 1 个 IoT 技能概要（Raspberry Pi Pico） | 嵌入式、传感器 |
| [`others/SKILL.md`](./others/SKILL.md) | 2 个其它技能概要（邮件平台、Java 脚手架） | 通用工具 |

> **设计理念：** 分类索引文件让 AI 工具在**已知用户需求领域**时，无需加载 56 个技能的全量索引（根 `SKILL.md`），只需加载对应分类索引即可快速定位目标技能。如果用户跨领域提问，再回退到根 `SKILL.md`。

---

## 🌍 GIS 类（gis/）

地理信息系统、空间数据处理、地图服务与渲染相关。

| SKILL | 简介 |
|-------|------|
| [opengis-all](./gis/opengis-all/SKILL.md) | 综合一站式 GIS 索引（保留作为顶层入口） |
| [gdal](./gis/gdal/SKILL.md) | GDAL/OGR 命令行：栅格/矢量数据处理事实标准 |
| [gdal-api](./gis/gdal-api/SKILL.md) | GDAL/OGR 编程 API（C/C++/Python/.NET） |
| [geotools](./gis/geotools/SKILL.md) | Java GIS 工具集 |
| [geoserver](./gis/geoserver/SKILL.md) | 开源地图服务器（WMS/WFS/WMTS/WCS） |
| [geoserver-rest-api](./gis/geoserver-rest-api/SKILL.md) | GeoServer REST API 自动化管理 |
| [geoserver-cloud](./gis/geoserver-cloud/SKILL.md) | GeoServer 云原生微服务架构 |
| [pyqgis](./gis/pyqgis/SKILL.md) | QGIS Python 二次开发 |
| [qgis-process](./gis/qgis-process/SKILL.md) | QGIS 命令行批处理 |
| [postgis](./gis/postgis/SKILL.md) | PostgreSQL 空间数据库扩展 |
| [cesiumjs](./gis/cesiumjs/SKILL.md) | 高性能 3D 地球与场景可视化 |
| [openlayers](./gis/openlayers/SKILL.md) | 高性能 Web 2D 地图库 |
| [geopandas](./gis/geopandas/SKILL.md) | Python 矢量空间数据处理 |
| [shapely](./gis/shapely/SKILL.md) | Python 几何对象与运算 |
| [jts](./gis/jts/SKILL.md) | Java Topology Suite 几何引擎 |
| [nettopologysuite](./gis/nettopologysuite/SKILL.md) | JTS 的 .NET 移植 |
| [geometry-api-java](./gis/geometry-api-java/SKILL.md) | Esri Geometry API for Java |
| [geometry-api-net](./gis/geometry-api-net/SKILL.md) | Esri Geometry API for .NET |
| [sharpmap](./gis/sharpmap/SKILL.md) | .NET WinForms / Web 地图渲染库 |
| [mapsui](./gis/mapsui/SKILL.md) | .NET 跨平台地图控件（MAUI/WPF/Avalonia） |
| [opengis-utils-for-java](./gis/opengis-utils-for-java/SKILL.md) | OpenGIS Java 实用工具集 |
| [opengis-utils-for-net](./gis/opengis-utils-for-net/SKILL.md) | OpenGIS .NET 实用工具集 |
| [geopipe-agent](./gis/geopipe-agent/SKILL.md) | GIS 数据流水线 Agent |

---

## 📐 CAD 类（cad/）

计算机辅助设计、参数化建模、几何运算、BIM 与 PCB 等。

| SKILL | 简介 |
|-------|------|
| [ifoxcad](./cad/ifoxcad/SKILL.md) | AutoCAD .NET 二次开发框架 |
| [fy_layout](./cad/fy_layout/SKILL.md) | AutoCAD 自动布图工具 |
| [clipper2](./cad/clipper2/SKILL.md) | 高性能 2D 多边形布尔运算与偏移（Angus Johnson） |
| [clipper1](./cad/clipper1/SKILL.md) | Clipper 1.x（旧版本，仍广泛使用） |
| [chili3d](./cad/chili3d/SKILL.md) | 基于 OCCT.js 的纯 Web 3D CAD |
| [libredwg](./cad/libredwg/SKILL.md) | 自由 DWG 读写库 |
| [qcad](./cad/qcad/SKILL.md) | 开源 2D CAD（DXF 编辑器） |
| [astral3d](./cad/astral3d/SKILL.md) | 工业 3D 可视化与编辑框架 |
| [kicad](./cad/kicad/SKILL.md) | 开源 EDA / PCB 设计套件 |
| [solvespace](./cad/solvespace/SKILL.md) | 轻量参数化 2D/3D CAD |
| [cadquery](./cad/cadquery/SKILL.md) | Python 脚本化参数化 3D CAD（基于 OCCT） |
| [librecad](./cad/librecad/SKILL.md) | 开源 2D CAD（C++/Qt） |
| [freecad](./cad/freecad/SKILL.md) | 开源参数化 3D CAD / BIM |
| [occt](./cad/occt/SKILL.md) | Open CASCADE Technology 三维几何内核 |
| [openscad](./cad/openscad/SKILL.md) | 脚本式 3D CAD（CSG） |
| [xbim](./cad/xbim/SKILL.md) | .NET BIM / IFC 工具集 |
| [lightcad](./cad/lightcad/SKILL.md) | 轻量级 Web 2D CAD 框架 |

---

## 🛠️ C# 类（csharp/）

.NET 生态常用框架、ORM、报表与保护工具。

| SKILL | 简介 |
|-------|------|
| [admin-net-backend](./csharp/admin-net-backend/SKILL.md) | Admin.NET 后端（基于 Furion） |
| [admin-net-frontend](./csharp/admin-net-frontend/SKILL.md) | Admin.NET 前端（Vue 3） |
| [furion](./csharp/furion/SKILL.md) | .NET 极简企业级 Web 框架 |
| [sod](./csharp/sod/SKILL.md) | PDF.NET SOD：ORM + SQL-MAP + OQL |
| [npoi](./csharp/npoi/SKILL.md) | .NET Excel/Word 读写（Apache POI 移植） |
| [reogrid](./csharp/reogrid/SKILL.md) | .NET 电子表格控件 |
| [sqlsugar](./csharp/sqlsugar/SKILL.md) | 国产高性能多数据库 ORM |
| [dotnet-reactor](./csharp/dotnet-reactor/SKILL.md) | .NET 商业级混淆/加壳/授权工具 |

---

## 🤖 AI 类（ai/）

LLM 应用、Agent 框架与提示词工程。

| SKILL | 简介 |
|-------|------|
| [dify](./ai/dify/SKILL.md) | 开源 LLM 应用开发平台（RAG + 工作流 + Agent） |
| [oh-my-openagent](./ai/oh-my-openagent/SKILL.md) | 中文 AI Agent 工程化模板集合 |
| [superpowers-zh](./ai/superpowers-zh/SKILL.md) | 中文优化提示词与 Skill 库 |
| [hermes-agent](./ai/hermes-agent/SKILL.md) | LLM Agent 编排与工具调用框架 |
| [openclaw](./ai/openclaw/SKILL.md) | 开源 Computer Use / 桌面操作 Agent |

---

## 📡 IoT 类（iot/）

| SKILL | 简介 |
|-------|------|
| [ke3036-keyes-pico](./iot/ke3036-keyes-pico/SKILL.md) | Keyes Raspberry Pi Pico 学习套件 |

---

## 🗂️ 其它（others/）

| SKILL | 简介 |
|-------|------|
| [billionmail](./others/billionmail/SKILL.md) | 自托管邮件营销与事务邮件平台 |
| [ruoyi-cloud](./others/ruoyi-cloud/SKILL.md) | 若依微服务版 Java 后台脚手架 |

---

## 📝 SKILL 编写规范

每个 `<category>/<project>/SKILL.md` 遵循统一规范，便于 AI 工具与人类阅读：

1. **YAML frontmatter**（必填字段）：

   ```yaml
   ---
   name: 项目英文名
   description: 一句话中文简介，说明定位、核心能力与典型用途
   tags:                 # ← 新增必填字段：用于 AI 工具按标签搜索技能
     - <语言/平台>
     - <功能领域>
     - <...>
   ---
   ```

   > **`tags` 字段说明：** 每个 SKILL.md 的 frontmatter 中必须包含 `tags` 数组，列出该技能的关键标签（如 `python`、`geometry`、`cli`、`3d` 等）。这些标签被根 `SKILL.md` 的标签索引系统使用，让 AI 工具可以通过标签快速定位相关技能，无需扫描全部 56 个文件。

2. **头部引用块**：项目地址、官方文档、许可证

3. **正文章节**（按需取用，顺序保持稳定）：
   - **概述**：定位、特性矩阵
   - **环境准备 / 安装**
   - **核心 API / 命令**
   - **典型工作流**
   - **最佳实践 / 性能优化**
   - **常见问题（FAQ 表）**
   - **参考资源**

4. **风格**：中文为主，配合代码示例；命令、API、字段使用代码格式
5. **大小**：通常 300–1500 行；过长内容拆分到 `reference/*.md`
6. **示例**：基于上游官方文档实地核对，避免编造 API

参考样板：[`gis/gdal/SKILL.md`](./gis/gdal/SKILL.md)、[`gis/jts/SKILL.md`](./gis/jts/SKILL.md)。

---

## 🔗 相关项目

- [znlgis.github.io](https://github.com/znlgis/znlgis.github.io) — 上游中文教程博客（与本仓库分类一一对应）
- [Anthropic Claude Skills](https://docs.claude.com/) — Skill 概念与规范
- [Cursor Rules](https://docs.cursor.com/) / [Cline Rules](https://github.com/cline/cline) — 客户端约定文件

---

## 📜 License

本仓库自身代码与文档遵循 [LICENSE](./LICENSE)（MIT）。各 SKILL 中引用、介绍的上游开源项目，请以其各自仓库的许可证为准。

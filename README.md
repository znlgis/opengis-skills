# opengis-skills

> 面向 **AI 编程助手 / Agent** 的开源 GIS、CAD、C#、AI、IoT 技能（Skill）集合。
>
> 本仓库与 [znlgis.github.io](https://github.com/znlgis/znlgis.github.io) 上游博客分类完全对齐，便于双向导航与学习。

每个 SKILL 都是一个独立目录，包含一份 `SKILL.md`，可被 Claude / Cursor / Cline / Copilot Chat / VS Code 等 AI 工具按需加载，作为「领域知识」注入到对话中，从而获得更准确的代码生成与问题排查能力。

---

## 📂 目录结构

```
opengis-skills/
├── gis/        # GIS 类（24 个）
├── cad/        # CAD 类（17 个）
├── csharp/     # C# 框架/库（8 个）
├── ai/         # AI 智能体/平台（5 个）
├── iot/        # 物联网（1 个）
└── others/     # 其它（2 个）
```

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

1. **YAML frontmatter**：

   ```yaml
   ---
   name: 项目英文名
   description: 一句话中文简介，说明定位、核心能力与典型用途
   ---
   ```

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

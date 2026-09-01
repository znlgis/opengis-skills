---
name: opengis-skills
description: "Use when AI coding assistant needs GIS/CAD/C#/AI/IoT/3D domain expertise for 72+ open-source projects. One-stop skill index with tag-based search and on-demand loading for GDAL, GeoServer, QGIS, PostGIS, JTS, CesiumJS, FreeCAD, OpenSCAD, OCCT, NPOI, SqlSugar, Furion, Dify, SuperSplat, Go and more."
tags:
  - gis
  - cad
  - csharp
  - ai
  - iot
  - opensource
  - skills
  - geospatial
  - spatial-analysis
  - mapping
  - 3d-modeling
  - dotnet
  - python
  - java
  - javascript
  - go
  - typescript
  - cpp
---

> **仓库地址：** <https://github.com/znlgis/opengis-skills>
>
> **上游博客（对应分类）：** <https://znlgis.github.io/>
>
> **许可证：** MIT

## 概述

本仓库是一个面向 **AI 编程助手 / Agent**（Claude、Cursor、Cline、Copilot Chat、DeepSeek 等）的技能（Skill）集合，涵盖开源 GIS、CAD、C#、AI、IoT、3D 六大领域及通用工具（others），共 7 个分类、72 个技能文件。

每个技能以独立的 `SKILL.md` 文件组织，AI 工具可按需加载，作为「领域知识」注入到对话上下文，从而获得更准确的 API 调用、代码生成、错误排查和最佳实践建议。

### 你需要什么？

- **需要 GIS 空间数据处理？** → 加载 `gis/gdal/SKILL.md`
- **需要用 QGIS 做批处理？** → 加载 `gis/qgis-process/SKILL.md`
- **需要用 Java 做几何运算？** → 加载 `gis/jts/SKILL.md`
- **需要发布地图服务？** → 加载 `gis/geoserver-rest-api/SKILL.md`
- **需要一站式 GIS 全流程？** → 加载 `gis/opengis-all/SKILL.md`
- **需要 CAD 参数化建模？** → 加载 `cad/freecad/SKILL.md`
- **需要用 .NET 操作 Excel？** → 加载 `csharp/npoi/SKILL.md`
- **需要搭建 LLM 应用？** → 加载 `ai/dify/SKILL.md`
- **需要用纯 C# 生成建筑模型？** → 加载 `3d/elements/SKILL.md`
- **需要 CSG 布尔运算建模？** → 加载 `3d/opencsg-net/SKILL.md`
- **需要 .NET 错误追踪？** → 加载 `csharp/sentry/SKILL.md`
- **需要 DeepSeek 智能体框架？** → 加载 `ai/deepseek-harness/SKILL.md`

> **AI 使用提示：** 优先使用下方标签系统精准定位所需技能，按需加载 1-3 个 SKILL.md，避免全量加载导致上下文膨胀。

---

## 技能索引

### 🌍 GIS — 地理信息系统（23 个）

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [opengis-all](./gis/opengis-all/SKILL.md) | **一站式 GIS 索引**：GDAL + QGIS + GeoServer 全流程 | `entrypoint` `workflow` `fullstack` |
| [gdal](./gis/gdal/SKILL.md) | GDAL 命令行：栅格/矢量处理事实标准 | `cli` `raster` `vector` `conversion` |
| [gdal-api](./gis/gdal-api/SKILL.md) | GDAL/OGR 编程 API（C/C++/Python/.NET） | `api` `python` `cpp` `dotnet` |
| [geotools](./gis/geotools/SKILL.md) | Java GIS 工具集 | `java` `geotools` `feature` |
| [geoserver](./gis/geoserver/SKILL.md) | 开源地图服务器（WMS/WFS/WMTS/WCS） | `server` `wms` `wfs` `ogc` |
| [geoserver-rest-api](./gis/geoserver-rest-api/SKILL.md) | GeoServer REST API 自动化管理 | `rest` `automation` `publish` |
| [geoserver-cloud](./gis/geoserver-cloud/SKILL.md) | GeoServer 云原生微服务架构 | `cloud` `kubernetes` `docker` |
| [pyqgis](./gis/pyqgis/SKILL.md) | QGIS Python 二次开发 | `python` `qgis` `plugin` |
| [qgis-process](./gis/qgis-process/SKILL.md) | QGIS 命令行批处理 | `cli` `processing` `headless` |
| [postgis](./gis/postgis/SKILL.md) | PostgreSQL 空间数据库扩展 | `database` `sql` `spatial` |
| [cesiumjs](./gis/cesiumjs/SKILL.md) | 高性能 3D 地球可视化 | `javascript` `3d` `webgl` |
| [openlayers](./gis/openlayers/SKILL.md) | 高性能 Web 2D 地图库 | `javascript` `webmapping` `2d` |
| [geopandas](./gis/geopandas/SKILL.md) | Python 矢量空间数据处理 | `python` `pandas` `vector` |
| [shapely](./gis/shapely/SKILL.md) | Python 几何对象与运算 | `python` `geometry` `analysis` |
| [jts](./gis/jts/SKILL.md) | Java Topology Suite 几何引擎 | `java` `geometry` `spatial` |
| [nettopologysuite](./gis/nettopologysuite/SKILL.md) | JTS 的 .NET 移植 | `dotnet` `geometry` `nuget` |
| [geometry-api-java](./gis/geometry-api-java/SKILL.md) | Esri Geometry API for Java | `java` `esri` `geometry` |
| [geometry-api-net](./gis/geometry-api-net/SKILL.md) | Esri Geometry API for .NET | `dotnet` `esri` `geometry` |
| [sharpmap](./gis/sharpmap/SKILL.md) | .NET WinForms/Web 地图渲染库 | `dotnet` `legacy` `winforms` |
| [mapsui](./gis/mapsui/SKILL.md) | .NET 跨平台地图控件 | `dotnet` `crossplatform` `maui` |
| [opengis-utils-for-java](./gis/opengis-utils-for-java/SKILL.md) | OpenGIS Java 实用工具集 | `java` `utils` `toolkit` |
| [opengis-utils-for-net](./gis/opengis-utils-for-net/SKILL.md) | OpenGIS .NET 实用工具集 | `dotnet` `utils` `toolkit` |
| [geopipe-agent](./gis/geopipe-agent/SKILL.md) | GIS 数据流水线 Agent（YAML 驱动） | `agent` `pipeline` `yaml` `qc` |

### 📐 CAD — 计算机辅助设计（19 个）

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [ifoxcad](./cad/ifoxcad/SKILL.md) | AutoCAD .NET 二次开发框架 | `autocad` `dotnet` `plugin` |
| [fy_layout](./cad/fy_layout/SKILL.md) | 施工场地布置插件（LightCAD 二次开发示例） | `lightcad` `construction` `dotnet` |
| [clipper2](./cad/clipper2/SKILL.md) | 高性能 2D 多边形布尔运算与偏移 | `geometry` `polygon` `clipping` |
| [clipper1](./cad/clipper1/SKILL.md) | Clipper 1.x（旧版本，仍广泛使用） | `geometry` `legacy` `polygon` |
| [chili3d](./cad/chili3d/SKILL.md) | 纯 Web 3D CAD（基于 OCCT.js） | `web` `typescript` `wasm` `3d` |
| [libredwg](./cad/libredwg/SKILL.md) | 自由 DWG 读写库 | `dwg` `converter` `library` |
| [qcad](./cad/qcad/SKILL.md) | 开源 2D CAD（DXF 编辑器） | `dxf` `2d` `editor` |
| [astral3d](./cad/astral3d/SKILL.md) | 工业 3D 可视化与编辑框架 | `visualization` `3d` `rendering` |
| [kicad](./cad/kicad/SKILL.md) | 开源 EDA/PCB 设计套件 | `eda` `pcb` `electronics` |
| [solvespace](./cad/solvespace/SKILL.md) | 轻量参数化 2D/3D CAD | `parametric` `constraint` `lightweight` |
| [cadquery](./cad/cadquery/SKILL.md) | Python 脚本化参数化 3D CAD | `python` `scripting` `occt` |
| [librecad](./cad/librecad/SKILL.md) | 开源 2D CAD（C++/Qt） | `dxf` `2d` `qt` |
| [freecad](./cad/freecad/SKILL.md) | 开源参数化 3D CAD/BIM | `parametric` `bim` `python` |
| [occt](./cad/occt/SKILL.md) | Open CASCADE Technology 几何内核 | `kernel` `geometry` `cpp` |
| [openscad](./cad/openscad/SKILL.md) | 脚本式 3D CAD（CSG） | `scripting` `csg` `programmatic` |
| [xbim](./cad/xbim/SKILL.md) | .NET BIM/IFC 工具集 | `dotnet` `bim` `ifc` |
| [lightcad](./cad/lightcad/SKILL.md) | 轻量级 Web 2D CAD 框架 | `web` `2d` `lightweight` |
| [lightningcad](./cad/lightningcad/SKILL.md) | 建筑围护深化设计插件（AutoCAD/ZWCAD） | `autocad` `zwcad` `panel-layout` |
| [tongwen](./cad/tongwen/SKILL.md) | CAD/BIM 工程图纸无损翻译套件（AutoCAD 2019-2026） | `autocad` `translation` `i18n` `bim` |

### 🛠️ C# — .NET 生态（9 个）

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [admin-net-backend](./csharp/admin-net-backend/SKILL.md) | Admin.NET 后端（基于 Furion） | `dotnet` `backend` `admin` |
| [admin-net-frontend](./csharp/admin-net-frontend/SKILL.md) | Admin.NET 前端（Vue 3） | `vue` `frontend` `admin` |
| [furion](./csharp/furion/SKILL.md) | .NET 极简企业级 Web 框架 | `dotnet` `webapi` `framework` |
| [sod](./csharp/sod/SKILL.md) | PDF.NET SOD：ORM + SQL-MAP + OQL | `orm` `dotnet` `database` |
| [npoi](./csharp/npoi/SKILL.md) | .NET Excel/Word 读写 | `excel` `office` `dotnet` |
| [reogrid](./csharp/reogrid/SKILL.md) | .NET 电子表格控件 | `dotnet` `spreadsheet` `ui` |
| [sqlsugar](./csharp/sqlsugar/SKILL.md) | 国产高性能多数据库 ORM | `orm` `dotnet` `database` |
| [dotnet-reactor](./csharp/dotnet-reactor/SKILL.md) | .NET 商业级混淆/加壳/授权 | `dotnet` `obfuscation` `security` |
| [sentry](./csharp/sentry/SKILL.md) | Sentry .NET SDK：错误追踪与性能监控 | `dotnet` `error-tracking` `monitoring` |

### 🤖 AI — LLM/Agent（9 个）

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [dify](./ai/dify/SKILL.md) | 开源 LLM 应用开发平台 | `llm` `rag` `workflow` `agent` |
| [oh-my-openagent](./ai/oh-my-openagent/SKILL.md) | OpenCode 多模型编排插件（Agent Harness） | `agent` `opencode` `orchestration` |
| [superpowers-zh](./ai/superpowers-zh/SKILL.md) | 中文 AI 编程方法论 Skills 集合 | `methodology` `chinese` `skill` |
| [hermes-agent](./ai/hermes-agent/SKILL.md) | 自学习通用型 AI 智能体（终端优先） | `agent` `self-improving` `terminal` |
| [openclaw](./ai/openclaw/SKILL.md) | 多通道个人 AI 助手 Gateway | `agent` `gateway` `assistant` |
| [pi](./ai/pi/SKILL.md) | 极简可扩展终端 AI 编码代理（Agent Harness） | `agent` `coding-agent` `terminal` `typescript` |
| [opencode](./ai/opencode/SKILL.md) | 模型无关的终端 AI 编码代理（配置即代码） | `agent` `coding-agent` `terminal` `mcp` |
| [docutranslate](./ai/docutranslate/SKILL.md) | 基于 LLM 的本地多格式文件翻译工具 | `llm` `translation` `pdf` `mcp` |
| [deepseek-harness](./ai/deepseek-harness/SKILL.md) | DeepSeek Harness（dsh）：插件化智能体框架 | `agent` `deepseek` `plugin` `cordis` |

### 📡 IoT — 物联网（1 个）

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [ke3036-keyes-pico](./iot/ke3036-keyes-pico/SKILL.md) | Keyes Raspberry Pi Pico 学习套件 | `micropython` `rp2040` `sensor` |

### 🧊 3D — 三维/高斯泼溅/全景（5 个）

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [supersplat](./3d/supersplat/SKILL.md) | 浏览器端开源 3D 高斯泼溅编辑器（PlayCanvas） | `3dgs` `webgl` `typescript` `editor` |
| [ara3d-sdk](./3d/ara3d-sdk/SKILL.md) | 面向 AEC 的高性能 .NET 三维/BIM 库集合（.NET 8） | `bim` `aec` `dotnet` `geometry` `ifc` |
| [photo-sphere-viewer](./3d/photo-sphere-viewer/SKILL.md) | JavaScript 360° 全景照片/球体查看器（Three.js 驱动） | `javascript` `threejs` `panorama` `webgl` |
| [elements](./3d/elements/SKILL.md) | Hypar Elements：纯 C# BIM 编程生成库 | `dotnet` `bim` `geometry` `ifc` `gltf` |
| [opencsg-net](./3d/opencsg-net/SKILL.md) | OpenCSG.NET：零依赖 .NET CSG 建模库 | `dotnet` `csg` `3d` `stl` |

### 🗂️ Others — 其它（6 个）

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [billionmail](./others/billionmail/SKILL.md) | 自托管邮件营销与事务邮件平台 | `email` `selfhosted` `marketing` |
| [ruoyi-cloud](./others/ruoyi-cloud/SKILL.md) | 若依微服务版 Java 后台脚手架 | `java` `springcloud` `scaffold` |
| [acme.sh](./others/acme.sh/SKILL.md) | 纯 Shell 的 ACME 客户端，自动签发/续期 SSL 证书 | `ssl` `acme` `lets-encrypt` `shell` |
| [go](./others/go/SKILL.md) | Go 语言核心语法与工程实践 | `go` `golang` `backend` `concurrency` |
| [robotgo](./others/robotgo/SKILL.md) | Go 跨平台桌面自动化（RPA）库 | `go` `rpa` `automation` `desktop` |
| [robotgo-flow](./others/robotgo-flow/SKILL.md) | 基于 robotgo 的 YAML 驱动 Windows RPA 框架 | `go` `rpa` `yaml` `windows` |

---

## 标签索引

通过标签快速定位目标技能：

### 按语言/平台

| 标签 | 相关技能 |
|------|---------|
| `python` | gdal-api, pyqgis, geopandas, shapely, cadquery, clipper1, freecad, kicad, libredwg, geopipe-agent, deepseek-harness, docutranslate, hermes-agent |
| `java` | gdal-api, geotools, jts, geometry-api-java, opengis-utils-for-java, geoserver, geoserver-cloud, ruoyi-cloud |
| `dotnet` / `csharp` | gdal-api, nettopologysuite, geometry-api-net, sharpmap, mapsui, opengis-utils-for-net, fy_layout, ifoxcad, lightningcad, tongwen, xbim, clipper1, clipper2, furion, sod, npoi, reogrid, sqlsugar, dotnet-reactor, admin-net-backend, ara3d-sdk, sentry, elements, opencsg-net |
| `javascript` / `typescript` | cesiumjs, openlayers, qcad, chili3d, lightcad, admin-net-frontend, deepseek-harness, openclaw, pi, photo-sphere-viewer, supersplat |
| `cpp` / `c` | gdal-api, occt, clipper1, clipper2, librecad, libredwg |
| `go` | go, robotgo, robotgo-flow |
| `shell` | qgis-process, acme.sh |
| `vue` | admin-net-frontend |
| `micropython` | ke3036-keyes-pico |

### 按功能领域

| 标签 | 相关技能 |
|------|---------|
| `geometry` | jts, nettopologysuite, shapely, geometry-api-java, geometry-api-net, geopandas, postgis, opengis-utils-for-java, opengis-utils-for-net, occt, xbim, clipper1, clipper2, ara3d-sdk, elements, opencsg-net |
| `raster` | gdal, gdal-api, qgis-process, geopipe-agent, geotools, postgis, pyqgis |
| `vector` | gdal, gdal-api, geopandas, geopipe-agent, geotools, opengis-utils-for-java, opengis-utils-for-net, postgis, pyqgis |
| `server` / `wms` / `wfs` | geoserver, geoserver-cloud, geoserver-rest-api, geotools, mapsui, openlayers, sharpmap |
| `3d` | cesiumjs, chili3d, freecad, occt, openscad, cadquery, solvespace, astral3d, fy_layout, photo-sphere-viewer, supersplat, ara3d-sdk, elements, opencsg-net |
| `2d` | openlayers, qcad, librecad, sharpmap, lightcad, clipper1, clipper2, fy_layout, solvespace |
| `orm` / `database` | sod, sqlsugar, postgis |
| `agent` / `llm` | dify, hermes-agent, openclaw, opencode, pi, oh-my-openagent, geopipe-agent, docutranslate, deepseek-harness |
| `pipeline` / `workflow` | dify, opengis-all, geopipe-agent, qgis-process, robotgo-flow |
| `automation` / `rpa` | geoserver-rest-api, qgis-process, acme.sh, robotgo, robotgo-flow |
| `autocad` | ifoxcad, lightningcad, tongwen |

---

## AI 工具使用指南

### 按需加载（推荐）

根据用户问题，只加载 1-3 个最相关的 SKILL.md：

**场景示例：**

| 用户需求 | 加载技能 |
|---------|---------|
| "帮我把 Shapefile 转成 GeoJSON" | `gis/gdal/SKILL.md` |
| "用 Python 计算两个面的交集" | `gis/shapely/SKILL.md` |
| "用 QGIS 批处理做缓冲区分析" | `gis/qgis-process/SKILL.md` |
| "如何发布矢量数据到 GeoServer？" | `gis/geoserver-rest-api/SKILL.md` |
| "PostGIS 怎么建空间索引？" | `gis/postgis/SKILL.md` |
| "用 .NET 读取 Shapefile" | `gis/nettopologysuite/SKILL.md` |
| "Java 几何运算怎么做？" | `gis/jts/SKILL.md` |
| "前端展示 WMS 地图图层" | `gis/openlayers/SKILL.md` 或 `gis/cesiumjs/SKILL.md` |
| "用 CAD 画个简单的 3D 零件" | `cad/openscad/SKILL.md` 或 `cad/cadquery/SKILL.md` |
| "用 .NET 写一个 Web API 接口" | `csharp/furion/SKILL.md` |

### 全量加载

当用户需求横跨多个领域或不确定具体工具时，先加载本文件（根 SKILL.md）获取全局索引，再按需加载子技能。

### Skill 加载方式

不同 AI 工具加载 Skill 的方式：

```bash
# Claude Code / Claude
@SKILL.md                    # 加载根入口（推荐）
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

## Skill 编写规范

每个技能文件遵循统一规范：

1. **YAML frontmatter** — `name`、`description`（英文 Use when... 格式）、`tags`（多行 YAML 数组格式，用于搜索）
2. **引用块** — 项目地址、官方文档、许可证
3. **概述** — 定位与特性矩阵
4. **环境准备/安装**
5. **核心 API/命令** — 含代码示例
6. **典型工作流** — 端到端操作步骤
7. **AI 使用建议** — AI 助手专项指导
8. **常见问题（FAQ）**
9. **参考资源**

参考样板：`gis/gdal/SKILL.md`、`gis/jts/SKILL.md`

---

## 贡献指南

1. 每个 Skill 以独立目录组织：`<category>/<project>/SKILL.md`
2. 如需引用数据或大型文件，放在 `reference/` 子目录
3. 基于上游官方文档编写，避免编造 API
4. 保持中文为主，代码、命令、API 使用原文格式
5. 提交 PR 时确保 YAML frontmatter 格式正确（`tags` 必须使用多行 `- tag` 格式，而非内联 `[tag1, tag2]` 格式）

---

## 许可证

本仓库自身代码与文档遵循 MIT License。各 SKILL 中引用、介绍的上游开源项目，请以其各自仓库的许可证为准。

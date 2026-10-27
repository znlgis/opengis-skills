---
name: cad-skills
description: "Use when doing parametric 3D modeling, 2D drafting, geometric kernel development, BIM/IFC processing, PCB design, or AutoCAD .NET development. Index of 21 skills: FreeCAD, OpenSCAD, OCCT, CadQuery, Blender, KiCad, SolveSpace, QCAD, xBIM, Clipper2, TongWen and more."
tags:
  - cad
  - 3d-modeling
  - 2d-drafting
  - parametric
  - geometry
  - bim
  - pcb
  - opensource
---

> **父级入口：** [../SKILL.md](../SKILL.md) — 全仓 114 技能总索引

## 概述

本分类涵盖 **21 个 CAD 项目**的技能文件，从底层几何内核到用户界面覆盖 CAD 全栈：

```
几何内核 → 参数化建模 → CAD 应用 → 数据交换 → 可视化
  (OCCT)    (FreeCAD)   (QCAD)    (LibreDWG) (Chili3D)
```

### 何时加载此索引？

- 用户问题涉及「CAD」「建模」「3D 打印」「DWG/DXF」「PCB」「BIM」
- 不确定该用 FreeCAD、OpenSCAD 还是 SolveSpace
- 需要 .NET 平台的 AutoCAD 二次开发指导

---

## 技能列表

### 🧩 几何内核与算法

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [occt](./occt/SKILL.md) | Open CASCADE Technology 三维几何内核 | `kernel` `geometry` `cpp` |
| [clipper2](./clipper2/SKILL.md) | 高性能 2D 多边形布尔运算与偏移 | `geometry` `polygon` `2d` `boolean` |
| [clipper1](./clipper1/SKILL.md) | Clipper 1.x（旧版本，仍广泛使用） | `geometry` `polygon` `2d` `boolean` |

### 🏗️ 参数化 3D CAD

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [freecad](./freecad/SKILL.md) | 开源参数化 3D CAD/BIM | `parametric` `bim` `python` |
| [openscad](./openscad/SKILL.md) | 脚本式 3D CAD（CSG） | `scripting` `csg` `3d` `parametric` |
| [cadquery](./cadquery/SKILL.md) | Python 脚本化参数化 3D CAD | `python` `occt` `3d` `parametric` |
| [solvespace](./solvespace/SKILL.md) | 轻量参数化 2D/3D CAD | `parametric` `3d` `2d` `cad` |
| [chili3d](./chili3d/SKILL.md) | 纯 Web 3D CAD（Three.js + 自研 chili-wasm/OCCT） | `web` `typescript` `wasm` `3d` |
| [blender](./blender/SKILL.md) | 开源 3D 创作套件（Python bpy API） | `3d` `python` `bpy` `gltf` |

### 📐 2D CAD 与制图

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [qcad](./qcad/SKILL.md) | 开源 2D CAD（DXF 编辑器） | `dxf` `2d` `cad` `dwg` |
| [librecad](./librecad/SKILL.md) | 开源 2D CAD（C++/Qt） | `dxf` `2d` `qt` |
| [lightcad](./lightcad/SKILL.md) | 国产开源 C# 平台（2D/3D/BIM 设计，可作二次开发底座） | `2d` `csharp` `dotnet` `cad` |
| [fy_layout](./fy_layout/SKILL.md) | 施工场地布置插件（LightCAD 二次开发示例） | `construction` `dotnet` `2d` `3d` |
| [design-drawing-svg-md](./design-drawing-svg-md/SKILL.md) | 设计图 SVG+MD 双载体记录（钢结构施工图→可复现图纸描述） | `svg` `markdown` `pdf` `steel-structure` `llm` |

### 🔌 PCB/EDA 设计

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [kicad](./kicad/SKILL.md) | 开源 EDA/PCB 设计套件 | `eda` `pcb` `electronics` |

### 🏛️ BIM 与 IFC

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [xbim](./xbim/SKILL.md) | .NET BIM/IFC 工具集 | `dotnet` `bim` `ifc` |

### 🛠️ .NET AutoCAD 开发

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [ifoxcad](./ifoxcad/SKILL.md) | AutoCAD .NET 二次开发框架 | `autocad` `dotnet` `plugin` |
| [lightningcad](./lightningcad/SKILL.md) | 建筑围护深化设计插件（AutoCAD/ZWCAD） | `autocad` `zwcad` `panel-layout` |
| [tongwen](./tongwen/SKILL.md) | CAD/BIM 工程图纸无损翻译套件（AutoCAD 2019/2021/2025/2026） | `autocad` `translation` `i18n` `bim` |

### 🔄 数据交换与可视化

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [libredwg](./libredwg/SKILL.md) | 自由 DWG 读写库 | `dwg` `dxf` `cad` `c` |
| [astral3d](./astral3d/SKILL.md) | 工业 3D 可视化与编辑框架 | `visualization` `3d` `web` `threejs` |

---

## 快速导航

| 用户需求 | 推荐加载 |
|---------|---------|
| "画个 3D 零件" | `openscad/SKILL.md` 或 `cadquery/SKILL.md` |
| "参数化机械设计" | `freecad/SKILL.md` |
| "轻量快速建模" | `solvespace/SKILL.md` |
| "浏览器里做 CAD" | `chili3d/SKILL.md` |
| "编辑 DXF 图纸" | `qcad/SKILL.md` 或 `librecad/SKILL.md` |
| "Python 脚本建模" | `cadquery/SKILL.md` |
| "AutoCAD .NET 插件" | `ifoxcad/SKILL.md` |
| "建筑围护板材排布/深化设计" | `lightningcad/SKILL.md` |
| "CAD 图纸多语言翻译" | `tongwen/SKILL.md` |
| "PCB 电路板设计" | `kicad/SKILL.md` |
| "BIM/IFC 数据处理" | `xbim/SKILL.md` |
| "2D 多边形布尔运算" | `clipper2/SKILL.md` |
| "DWG 文件读写" | `libredwg/SKILL.md` |
| "三维几何底层操作" | `occt/SKILL.md` |
| "把钢结构施工图转成 LLM 可读的 SVG+MD" | `design-drawing-svg-md/SKILL.md` |

---

## 相关分类

- **[gis/](../gis/SKILL.md)** — 空间数据处理、地图服务、Web GIS
- **[csharp/](../csharp/SKILL.md)** — .NET 框架、ORM、Office 操作
- **[ai/](../ai/SKILL.md)** — LLM 应用、Agent 框架
- **[3d/](../3d/SKILL.md)** — 3D 高斯泼溅与 Web 三维可视化

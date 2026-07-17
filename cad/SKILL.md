---
name: cad-skills
description: "Use when doing parametric 3D modeling, 2D drafting, geometric kernel development, BIM/IFC processing, PCB design, or AutoCAD .NET development. Index of 18 skills: FreeCAD, OpenSCAD, OCCT, CadQuery, KiCad, SolveSpace, QCAD, xBIM, Clipper2 and more."
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

> **父级入口 -- ?* [../SKILL.md](../SKILL.md)  -- ?全仓 66 技能总索 -- ?

## 概述

本分类涵 -- ?**18  -- ?CAD 项目**的技能文件，从底层几何内核到用户界面覆盖 CAD 全栈 -- ?

```
几何内核  -- ?参数化建 -- ? -- ?CAD 应用  -- ?数据交换  -- ?可视 -- ?
  (OCCT)    (FreeCAD)   (QCAD)    (LibreDWG) (Chili3D)
```

### 何时加载此索引？

- 用户问题涉及「CAD」「建模」 -- ?D 打印」「DWG/DXF」「PCB」「BIM -- ?
- 不确定该 -- ?FreeCAD、OpenSCAD 还是 SolveSpace
- 需 -- ?.NET 平台 -- ?AutoCAD 二次开发指 -- ?

---

## 技能列 -- ?

### 🧩 几何内核与算 -- ?

| 技 -- ?| 简 -- ?| 关键标签 |
|------|------|---------|
| [occt](./occt/SKILL.md) | Open CASCADE Technology 三维几何内核 | `kernel` `geometry` `cpp` |
| [clipper2](./clipper2/SKILL.md) | 高性能 2D 多边形布尔运算与偏移 | `geometry` `polygon` `clipping` |
| [clipper1](./clipper1/SKILL.md) | Clipper 1.x（旧版本，仍广泛使用 -- ?| `geometry` `legacy` `polygon` |

### 🏗 -- ?参数 -- ?3D CAD

| 技 -- ?| 简 -- ?| 关键标签 |
|------|------|---------|
| [freecad](./freecad/SKILL.md) | 开源参数化 3D CAD/BIM | `parametric` `bim` `python` |
| [openscad](./openscad/SKILL.md) | 脚本 -- ?3D CAD（CSG -- ?| `scripting` `csg` `programmatic` |
| [cadquery](./cadquery/SKILL.md) | Python 脚本化参数化 3D CAD | `python` `scripting` `occt` |
| [solvespace](./solvespace/SKILL.md) | 轻量参数 -- ?2D/3D CAD | `parametric` `constraint` `lightweight` |
| [chili3d](./chili3d/SKILL.md) |  -- ?Web 3D CAD（OCCT.js + WASM -- ?| `web` `typescript` `wasm` `3d` |

### 📐 2D CAD 与制 -- ?

| 技 -- ?| 简 -- ?| 关键标签 |
|------|------|---------|
| [qcad](./qcad/SKILL.md) | 开 -- ?2D CAD（DXF 编辑器） | `dxf` `2d` `editor` |
| [librecad](./librecad/SKILL.md) | 开 -- ?2D CAD（C++/Qt -- ?| `dxf` `2d` `qt` |
| [lightcad](./lightcad/SKILL.md) | 轻量 -- ?Web 2D CAD 框架 | `web` `2d` `lightweight` |

### 🔌 PCB/EDA 设计

| 技 -- ?| 简 -- ?| 关键标签 |
|------|------|---------|
| [kicad](./kicad/SKILL.md) | 开 -- ?EDA/PCB 设计套件 | `eda` `pcb` `electronics` |

### 🏛 -- ?BIM  -- ?IFC

| 技 -- ?| 简 -- ?| 关键标签 |
|------|------|---------|
| [xbim](./xbim/SKILL.md) | .NET BIM/IFC 工具 -- ?| `dotnet` `bim` `ifc` |
| [freecad](./freecad/SKILL.md) | 也包 -- ?BIM 工作 -- ?| `bim` `parametric` |

### 🛠 -- ?.NET AutoCAD 开 -- ?

| 技 -- ?| 简 -- ?| 关键标签 |
|------|------|---------|
| [ifoxcad](./ifoxcad/SKILL.md) | AutoCAD .NET 二次开发框 -- ?| `autocad` `dotnet` `plugin` |
| [fy_layout](./fy_layout/SKILL.md) | AutoCAD 自动布图工具 | `autocad` `layout` `automation` |
| [lightningcad](./lightningcad/SKILL.md) | 建筑围护深化设计插件（AutoCAD/ZWCAD -- ?| `autocad` `zwcad` `panel-layout` |

### 🔄 数据交换与可视化

| 技 -- ?| 简 -- ?| 关键标签 |
|------|------|---------|
| [libredwg](./libredwg/SKILL.md) | 自由 DWG 读写 -- ?| `dwg` `converter` `library` |
| [astral3d](./astral3d/SKILL.md) | 工业 3D 可视化与编辑框架 | `visualization` `3d` `rendering` |

---

## 快速导 -- ?

| 用户需 -- ?| 推荐加载 |
|---------|---------|
| "画个 3D 零件" | `openscad/SKILL.md`  -- ?`cadquery/SKILL.md` |
| "参数化机械设 -- ? | `freecad/SKILL.md` |
| "轻量快速建 -- ? | `solvespace/SKILL.md` |
| "浏览器里 -- ?CAD" | `chili3d/SKILL.md` |
| "编辑 DXF 图纸" | `qcad/SKILL.md`  -- ?`librecad/SKILL.md` |
| "Python 脚本建模" | `cadquery/SKILL.md` |
| "AutoCAD .NET 插件" | `ifoxcad/SKILL.md` |
| "建筑围护板材排布/深化设计" | `lightningcad/SKILL.md` |
| "PCB 电路板设 -- ? | `kicad/SKILL.md` |
| "BIM/IFC 数据处理" | `xbim/SKILL.md` |
| "2D 多边形布尔运 -- ? | `clipper2/SKILL.md` |
| "DWG 文件读写" | `libredwg/SKILL.md` |
| "三维几何底层操作" | `occt/SKILL.md` |

---

## 相关分类

- **[gis/](../gis/SKILL.md)**  -- ?空间数据处理、地图服务、Web GIS
- **[csharp/](../csharp/SKILL.md)**  -- ?.NET 框架、ORM、Office 操作
- **[ai/](../ai/SKILL.md)**  -- ?LLM 应用、Agent 框架
- **[3d/](../3d/SKILL.md)**  -- ?3D 高斯泼溅 -- ?Web 三维可视 -- ?

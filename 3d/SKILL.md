---
name: 3d-skills
description: "Use when working with 3D Gaussian Splatting (3DGS), .ply model cleanup/compression/publishing, WebGL/WebGPU 3D visualization, or AEC/BIM 3D data processing. Index of 2 skills: SuperSplat and Ara3D-SDK."
tags:
  - 3d
  - gaussian-splatting
  - 3dgs
  - webgl
  - webgpu
  - visualization
  - bim
  - aec
  - dotnet
  - opensource
---

> **父级入口：** [../SKILL.md](../SKILL.md) — 全仓 66 技能总索引

## 概述

本分类涵盖 **3D / 三维可视化 / 三维数据处理** 相关的开源项目技能，涵盖 **3D 高斯泼溅（3DGS）** 这一新型实时辐射场表达方法的工程化工具链，以及面向 **AEC/BIM** 的高性能 .NET 三维数据引擎。

- **3DGS 编辑器**：SuperSplat（浏览器端清理、裁剪、变换、调色、动画、发布）
- **AEC/BIM 三维 SDK**：Ara3D-SDK（.NET 8 高性能几何/网格/BIM 处理、SIMD 数学、多格式 I/O、Studio 插件）

### 何时加载此索引？

- 需要处理 3D 高斯泼溅（3DGS）训练产出的 `.ply` 模型
- 想清理噪点、压缩体积并发布到网页
- 需要基于 PlayCanvas / WebGL / WebGPU 的 Web 三维工具二次开发
- 需要用 .NET/C# 做海量三维网格建模、BIM/IFC 数据处理或三维格式转换（IFC/STEP/PLY↔glTF/GLB/VIM）

> 提示：若你的需求偏向 **3D 地球 / 倾斜摄影场景可视化**，可参考 GIS 分类的 [cesiumjs](../gis/cesiumjs/SKILL.md)；若偏向 **3D CAD 建模**，参考 CAD 分类（occt、freecad、cadquery 等）。

---

## 技能列表

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [supersplat](./supersplat/SKILL.md) | 浏览器端开源 3D 高斯泼溅编辑器（PlayCanvas） | `3dgs` `webgl` `typescript` `editor` |
| [ara3d-sdk](./ara3d-sdk/SKILL.md) | 面向 AEC 的高性能 .NET 三维/BIM 库集合（.NET 8） | `bim` `aec` `dotnet` `geometry` `ifc` |

---

## 快速导航

| 用户需求 | 推荐加载 |
|---------|---------|
| "清理高斯泼溅 .ply 的噪点" | `supersplat/SKILL.md` |
| "把高斯模型压缩后放到网页" | `supersplat/SKILL.md` |
| "给高斯泼溅做相机动画并发布" | `supersplat/SKILL.md` |
| "SuperSplat 源码架构与二次开发" | `supersplat/SKILL.md` |
| "用 C# 生成/变换三维网格并导出 glTF" | `ara3d-sdk/SKILL.md` |
| "把 IFC/Revit 模型转成 BOS/Parquet 分析" | `ara3d-sdk/SKILL.md` |
| "开发 Ara 3D Studio 插件（生成器/修改器）" | `ara3d-sdk/SKILL.md` |

---

## 相关分类

- **[gis/](../gis/SKILL.md)** — 3D 地球与场景可视化（CesiumJS）
- **[cad/](../cad/SKILL.md)** — 3D CAD 建模与几何内核（OCCT、FreeCAD、CadQuery）
- **[ai/](../ai/SKILL.md)** — LLM 应用与 Agent 框架

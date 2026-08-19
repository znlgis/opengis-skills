---
name: 3d-skills
description: "Use when working with 3D Gaussian Splatting (3DGS), .ply model cleanup/compression/publishing, interactive 360-degree panorama visualization and virtual tours, AEC/BIM 3D data processing, or CSG solid modeling. Index of 5 skills: SuperSplat, Photo-Sphere-Viewer, Ara3D-SDK, Elements, and OpenCSG.NET."
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

> **父级入口：** [../SKILL.md](../SKILL.md) — 全仓 68 技能总索引

## 概述

本分类涵盖 **3D / 三维可视化 / 三维数据处理 / 360° 全景 / CSG 建模** 相关的开源项目技能：

- **3DGS 编辑器**：SuperSplat（浏览器端清理、裁剪、变换、调色、动画、发布）
- **全景查看器**：Photo-Sphere-Viewer（Web 360° 全景展示、标记、虚拟导览、VR）
- **AEC/BIM 三维 SDK**：Ara3D-SDK（.NET 8 高性能几何/网格/BIM 处理、SIMD 数学、多格式 I/O、Studio 插件）
- **BIM 编程生成库**：Elements（Hypar Elements，纯 C# 创建建筑构件，无需 Revit/Rhino）
- **CSG 建模库**：OpenCSG.NET（零依赖 .NET 构造实体几何库，布尔运算 + STL 导出）

### 何时加载此索引？

- 需要处理 3D 高斯泼溅（3DGS）训练产出的 `.ply` 模型
- 想清理噪点、压缩体积并发布到网页
- 需要基于 PlayCanvas / WebGL / WebGPU 的 Web 三维工具二次开发
- 需要在前端展示 360° 全景照片/视频，带标记、导览、陀螺仪交互
- 需要用 .NET/C# 做海量三维网格建模、BIM/IFC 数据处理或三维格式转换（IFC/STEP/PLY↔glTF/GLB/VIM）
- 需要纯 C# 编程生成建筑模型（墙/梁/柱/楼板）
- 需要 CSG 构造实体几何建模（立方体/球体/圆柱体布尔运算 + STL 导出）

> 提示：若你的需求偏向 **3D 地球 / 倾斜摄影场景可视化**，可参考 GIS 分类的 [cesiumjs](../gis/cesiumjs/SKILL.md)；若偏向 **3D CAD 建模**，参考 CAD 分类（occt、freecad、cadquery 等）。

---

## 技能列表

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [supersplat](./supersplat/SKILL.md) | 浏览器端开源 3D 高斯泼溅编辑器（PlayCanvas） | `3dgs` `webgl` `typescript` `editor` |
| [photo-sphere-viewer](./photo-sphere-viewer/SKILL.md) | JavaScript 360° 全景照片/球体查看器（Three.js 驱动） | `javascript` `threejs` `panorama` `webgl` |
| [ara3d-sdk](./ara3d-sdk/SKILL.md) | 面向 AEC 的高性能 .NET 三维/BIM 库集合（.NET 8） | `bim` `aec` `dotnet` `geometry` `ifc` |
| [elements](./elements/SKILL.md) | Hypar Elements：纯 C# BIM 编程生成库 | `dotnet` `bim` `aec` `geometry` `ifc` `gltf` |
| [opencsg-net](./opencsg-net/SKILL.md) | OpenCSG.NET：零依赖 .NET CSG 建模库 | `dotnet` `csg` `3d` `geometry` `stl` |

---

## 快速导航

| 用户需求 | 推荐加载 |
|---------|---------|
| "清理高斯泼溅 .ply 的噪点" | `supersplat/SKILL.md` |
| "把高斯模型压缩后放到网页" | `supersplat/SKILL.md` |
| "给高斯泼溅做相机动画并发布" | `supersplat/SKILL.md` |
| "SuperSplat 源码架构与二次开发" | `supersplat/SKILL.md` |
| "网页端展示 360° 全景照片" | `photo-sphere-viewer/SKILL.md` |
| "构建带标记的全景虚拟导览" | `photo-sphere-viewer/SKILL.md` |
| "移动端陀螺仪 VR 全景" | `photo-sphere-viewer/SKILL.md` |
| "用 C# 生成/变换三维网格并导出 glTF" | `ara3d-sdk/SKILL.md` |
| "把 IFC/Revit 模型转成 BOS/Parquet 分析" | `ara3d-sdk/SKILL.md` |
| "开发 Ara 3D Studio 插件（生成器/修改器）" | `ara3d-sdk/SKILL.md` |
| "用纯 C# 编程生成建筑模型" | `elements/SKILL.md` |
| "CSG 布尔运算建模 + STL 导出" | `opencsg-net/SKILL.md` |

---

## 相关分类

- **[gis/](../gis/SKILL.md)** — 3D 地球与场景可视化（CesiumJS）
- **[cad/](../cad/SKILL.md)** — 3D CAD 建模与几何内核（OCCT、FreeCAD、CadQuery）
- **[ai/](../ai/SKILL.md)** — LLM 应用与 Agent 框架

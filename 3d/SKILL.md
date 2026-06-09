---
name: 3d-skills
description: 3D 技能分类索引，覆盖 3D 高斯泼溅（3DGS）编辑与 Web 三维可视化领域，当前收录浏览器端开源高斯泼溅编辑器 SuperSplat，按需加载即可获得 .ply 高斯模型清理、裁剪、压缩、动画与发布的精准 AI 辅助。
tags:
  - 3d
  - gaussian-splatting
  - 3dgs
  - webgl
  - webgpu
  - visualization
  - opensource
---

> **父级入口：** [../SKILL.md](../SKILL.md) — 全仓技能总索引

## 概述

本分类涵盖 **3D / 三维可视化** 相关的开源项目技能，重点是 **3D 高斯泼溅（3DGS）** 这一新型实时辐射场表达方法的工程化工具链。

- **3DGS 编辑器**：SuperSplat（浏览器端清理、裁剪、变换、调色、动画、发布）

### 何时加载此索引？

- 需要处理 3D 高斯泼溅（3DGS）训练产出的 `.ply` 模型
- 想清理噪点、压缩体积并发布到网页
- 需要基于 PlayCanvas / WebGL / WebGPU 的 Web 三维工具二次开发

> 提示：若你的需求偏向 **3D 地球 / 倾斜摄影场景可视化**，可参考 GIS 分类的 [cesiumjs](../gis/cesiumjs/SKILL.md)；若偏向 **3D CAD 建模**，参考 CAD 分类（occt、freecad、cadquery 等）。

---

## 技能列表

| 技能 | 简介 | 关键标签 |
|------|------|---------|
| [supersplat](./supersplat/SKILL.md) | 浏览器端开源 3D 高斯泼溅编辑器（PlayCanvas） | `3dgs` `webgl` `typescript` `editor` |

---

## 快速导航

| 用户需求 | 推荐加载 |
|---------|---------|
| "清理高斯泼溅 .ply 的噪点" | `supersplat/SKILL.md` |
| "把高斯模型压缩后放到网页" | `supersplat/SKILL.md` |
| "给高斯泼溅做相机动画并发布" | `supersplat/SKILL.md` |
| "SuperSplat 源码架构与二次开发" | `supersplat/SKILL.md` |

---

## 相关分类

- **[gis/](../gis/SKILL.md)** — 3D 地球与场景可视化（CesiumJS）
- **[cad/](../cad/SKILL.md)** — 3D CAD 建模与几何内核（OCCT、FreeCAD、CadQuery）
- **[ai/](../ai/SKILL.md)** — LLM 应用与 Agent 框架

---
name: opencsg-net
description: "Use when doing constructive solid geometry (CSG) modeling in .NET — cube/sphere/cylinder primitives, union/subtract/intersect boolean operations, mesh transformations, STL export. OpenCSG.NET: zero-dependency C# CSG library ported from OpenJsCad's csg.js with merged improvements from praeclarum/Csg and hypar-io/Csg."
tags:
  - dotnet
  - csharp
  - csg
  - 3d
  - geometry
  - stl
  - modeling
  - mesh
---

> **项目地址：** <https://github.com/znlgis/OpenCSG.NET>
>
> **NuGet：** <https://www.nuget.org/packages/OpenCSG.NET>
>
> **许可证：** MIT

## 概述

OpenCSG.NET 是一个面向 .NET 的 **构造实体几何（CSG）建模库**。提供基础形体（立方体、球体、圆柱体）、布尔运算（并集、差集、交集）以及 STL 文件导出。**零依赖，netstandard2.0，MIT 授权**。

### 核心特性

| 特性 | 说明 |
|------|------|
| 零依赖 | 无任何外部 NuGet 依赖 |
| 跨平台 | netstandard2.0，支持 .NET 6/7/8/9+ |
| CSG 布尔运算 | Union / Subtract / Intersect |
| 基础形体 | Cube / Sphere / Cylinder |
| 变换 | Translate / RotateX/Y/Z / Scale |
| STL 导出 | ASCII + Binary 两种格式 |
| BSP 树 | 迭代式 BSP 树实现（非递归） |

### 上游关系

```
OpenJsCad csg.js (JavaScript)
└── praeclarum/Csg (手工 C# 移植)
    └── hypar-io/Csg
        ├── Csg (Union 原点居中修复、NaN 校验)
        └── DotNetCsg (二进制 STL、迭代 BSP、RotateX/Y/Z)
            └── OpenCSG.NET (本项目 — 合并两者改进)
```

---

## 环境准备

### 安装

```bash
dotnet add package OpenCSG.NET
```

### 前置条件

- .NET Standard 2.0+（库本身）
- .NET 8+（构建/测试/示例）
- 构建解决方案需要 .NET 9+ SDK：`dotnet build OpenCSG.NET.slnx`

---

## 核心 API

### 基础形体

```csharp
using Csg;
using static Csg.Solids;

// 立方体
var cube = Cube(size: 2, center: true);
var cube2 = Cube(x: 3, y: 2, z: 1);        // 自定义尺寸

// 球体
var sphere = Sphere(r: 1, center: true);

// 圆柱体
var cylinder = Cylinder(r: 0.5, h: 3, center: true);
```

### 布尔运算

```csharp
// 并集
var union = Union(cube, sphere);

// 差集
var difference = cube.Subtract(sphere);

// 交集
var intersection = cube.Intersect(sphere);
```

### 变换

```csharp
var transformed = cube
    .Translate(x: 5, y: 0, z: 0)
    .RotateZ(45)
    .Scale(0.5);

// 单独旋转
var rotated = cube.RotateX(30);
var rotated2 = cube.RotateY(45);
var rotated3 = cube.RotateZ(60);
```

### STL 导出

```csharp
// ASCII STL
using (var fs = File.Create("output.stl"))
using (var wr = new StreamWriter(fs))
{
    union.WriteStl("union", wr);
}

// Binary STL（更小的文件体积）
using (var fs = File.Create("output.stl"))
using (var wr = new BinaryWriter(fs))
{
    union.WriteStl("union", wr);
}
```

---

## 典型工作流

### 创建机械零件

```csharp
using Csg;
using static Csg.Solids;

// 创建一个带孔的圆柱体
var cylinder = Cylinder(r: 2, h: 3, center: true);
var hole = Cylinder(r: 0.5, h: 3.1, center: true);  // 稍高确保穿透
var part = cylinder.Subtract(hole);

// 添加侧面凸台
var boss = Cylinder(r: 0.8, h: 1.5, center: true)
    .RotateY(90)
    .Translate(x: 2, y: 0, z: 0);
var result = part.Union(boss);

// 导出
using var fs = File.Create("part.stl");
using var wr = new BinaryWriter(fs);
result.WriteStl("mechanical_part", wr);
```

---

## 构建与测试

```bash
# 使用 .NET 9+ SDK 构建完整解决方案
dotnet build OpenCSG.NET.slnx

# 仅构建核心库（.NET 8 SDK）
dotnet build src/OpenCSG.NET/OpenCSG.NET.csproj -c Release

# 运行测试
dotnet test tests/OpenCSG.NET.Tests/
```

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 需要什么版本的 .NET？ | 核心库 netstandard2.0（兼容 .NET 6+），测试需要 .NET 8+ |
| Union 结果位置异常？ | 本库已修复 origin-centering 问题（来自 Csg fork 的修复） |
| 与 Hypar.Elements 的 CSG 有何区别？ | OpenCSG.NET 是独立的零依赖 CSG 库，Elements 内置了自己的 CSG 内核 |
| 如何处理复杂网格？ | BSP 树实现为迭代式（非递归），避免栈溢出 |

---

## AI 使用建议

### 推荐工作流

1. **创建基本体**：使用 `Solids.Cube()`、`Solids.Sphere()`、`Solids.Cylinder()` 创建基础形体
2. **布尔运算**：`.Subtract()`（差集）、`.Intersect()`（交集）、`Union()`（并集）
3. **变换**：`.Translate()`、`.RotateX/Y/Z()`、`.Scale()` 链式调用
4. **导出**：使用 `BinaryWriter` + `WriteStl()` 导出 Binary STL（更小文件体积）

### 关键注意事项

- **零依赖**：无任何外部 NuGet 依赖，netstandard2.0 兼容所有现代 .NET
- **Union 位置修复**：本库已修复上游 Csg fork 的 origin-centering 问题
- **Binary STL 优先**：Binary STL 比 ASCII STL 文件体积更小，推荐使用
- **圆柱体穿透**：布尔运算时让减去的形体稍大（如高 0.1）确保完全穿透
- **非递归 BSP**：迭代式 BSP 树实现，处理复杂网格不会栈溢出

---

## 相关技能

- **elements** — Hypar Elements BIM 编程生成库（内置 CSG 内核）：[../elements/SKILL.md](../elements/SKILL.md)
- **ara3d-sdk** — .NET 高性能三维/BIM 库：[../ara3d-sdk/SKILL.md](../ara3d-sdk/SKILL.md)
- **clipper2** — 2D 多边形布尔运算：[../../cad/clipper2/SKILL.md](../../cad/clipper2/SKILL.md)
- **openscad** — 脚本式 3D CAD（CSG）：[../../cad/openscad/SKILL.md](../../cad/openscad/SKILL.md)

---

## 参考资源

- [OpenCSG.NET GitHub](https://github.com/znlgis/OpenCSG.NET) — 源码与示例
- [上游 praeclarum/Csg](https://github.com/praeclarum/Csg) — 原始 C# 移植
- [上游 hypar-io/Csg](https://github.com/hypar-io/Csg) — Hypar 的改进 fork
- [OpenJsCad](https://openjscad.xyz/) — 原始 JavaScript 实现

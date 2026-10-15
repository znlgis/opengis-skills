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
> **许可证：** MIT ｜ **最新版本：** `1.4.0`（GitHub tag `v1.4.0` 与 NuGet 一致；csproj 里 `<Version>0.0.0</Version>` 只是占位，版本由 CI 在打包时注入）

## 概述

OpenCSG.NET 是一个面向 .NET 的 **构造实体几何（CSG）建模库**。提供基础形体（立方体、球体、圆柱体、圆锥、拉伸体、楔形体）、布尔运算（并集、差集、交集）、型钢截面库、声明式 CSG 树（含 JSON 序列化）、STL 导出，以及把实体投影成三视图的制图能力。`netstandard2.0`，MIT 授权。

### 核心特性

| 特性 | 说明 |
|------|------|
| 依赖 | 唯一 PackageReference 是 `System.Text.Json` 8.0.6（供 CSG 树 JSON 序列化用），其余无外部依赖 |
| 跨平台 | netstandard2.0；测试/样例/性能工程为 net8.0 |
| CSG 布尔运算 | Union / Subtract / Intersect（`params` 支持一次传多个） |
| 基础形体 | Cube / Sphere / Cylinder / Cone / Extrude / Wedge |
| 变换 | Translate / RotateX-Y-Z / Scale / Transform（Matrix4x4） |
| 声明式 CSG 树 | `CsgNode` 记录类型 + `CsgNodes` 工厂 + `CsgEvaluator.Evaluate` + `CsgSerialization` JSON 往返 |
| 型钢截面 | `Profiles`：Rectangle / HBeam / Channel / SquareTube / Trapezoid / Capsule / LShape |
| STL 导出 | `Solid.WriteStl`（TextWriter / BinaryWriter）与 `StlWriter.WriteAscii/WriteBinary(path)` |
| 三视图投影 | `ViewProjector` + `ViewDirections`（主/俯/左）+ `ViewArcFitter`（投影线段的圆弧识别） |
| BSP 树 | 迭代式 BSP 树实现（非递归），不会栈溢出 |

### 上游关系

```text
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
- 构建整个解决方案需要 .NET 9+ SDK：`dotnet build OpenCSG.NET.slnx`
- 数值口径：布尔运算按 **绝对容差 1e-5** 合并顶点/平面，坐标量级到 1e6 仍然正确（仓库有测量坐标回归测试）

### 精度与网格约定（官方 README 固化）

- 布尔结果可能出现 **T 顶点接缝**（没有 T 顶点清理 pass）：面没有面积洞（按体积累等式 `A ∪ B = A + B − A ∩ B` 验证过），但不保证是严格闭合的二维流形
- 负缩放（镜像）矩阵会按行列式识别并翻转顶点缠绕与平面法线，镜像体仍朝外

---

## 核心 API

### 基础形体

```csharp
using Csg;
using static Csg.Solids;

// 立方体
var cube = Cube(size: 2, center: true);
var cube2 = Cube(width: 3, height: 2, depth: 1);          // 三边尺寸
var cube3 = Cube(new Vector3D(3, 2, 1), center: false);   // 或按向量给尺寸

// 球体
var sphere = Sphere(r: 1, center: true);

// 圆柱体
var cylinder = Cylinder(r: 0.5, h: 3, center: true);
```

形体落位与轴向（仓库用 `PrimitiveConventionTest` 固化）：

| 形体 | 落位 | 轴向 |
|------|------|------|
| `Cube(size)` | 占据 `[0, size]³`，从原点沿正轴生长 | — |
| `Cube(size, center: true)` / `Cube(size, centerPoint)` | 以原点 / 指定点为中心 | — |
| `Sphere(r)` | 默认 `center: true` 以原点为心；`false` 时占 `[0, 2r]³` | 两极在 ±Z |
| `Cylinder(r, h)` | `center` 指轴中点 | 高度沿 ±Y |
| `CylinderOptions` | 体沿 `Start → End` | `End − Start` |
| `ExtrudeNode` | 截面在 X-Y 平面，从 Z=0 拉伸到 `Height` | +Z |
| `WedgeNode` | `Corner` 是底矩形中心，底在 `Corner.Z`，脊在 `Corner.Y` | 宽 X / 深 Y / 高 Z |

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

也可直接用 `StlWriter` 写文件路径（`WriteBinary` / `WriteAscii` 返回写出的字节数），配合 `CsgMesh.TrianglesOf(solid)` 取三角网格。

### 声明式 CSG 树与 JSON 往返

不需要手写一连串方法调用时，用 `CsgNode` 记录类型描述整棵树，再一次性求值；树本身可序列化成 JSON 存储/传输：

```csharp
using Csg;

var node = CsgNodes.Subtract(
    CsgNodes.Box(0, 0, 0, 40, 30, 20),                          // Box 有数值重载
    CsgNodes.Cylinder(new Vector3D(0, 0, 0), 5, 40),            // 其余节点用 Vector3D 定位
    CsgNodes.Wedge(new Vector3D(0, 0, 0), 10, 10, 10));

var json = CsgSerialization.ToJson(node);       // indented 默认 true
var back = CsgSerialization.FromJson(json);
var solid = CsgEvaluator.Evaluate(back);        // CsgNode → Solid

// 多个节点可用 ToJson(IEnumerable<CsgNode>) / FromJsonArray(...) 批量往返
```

节点类型：`BoxNode` / `SphereNode` / `CylinderNode` / `ConeNode` / `ExtrudeNode` / `WedgeNode` / `UnionNode` / `SubtractNode` / `IntersectNode` / `TransformNode`；`TransformNode` 先平移再绕**全局原点**按 X→Y→Z 旋转（即 `T · R`）。

### 型钢截面（Profiles）

```csharp
// 截面轮廓 → 拉伸成体
var h = Profiles.HBeam(webHeight: 200, flangeWidth: 100,
                       webThickness: 6, flangeThickness: 8);
var node = CsgNodes.Extrude(h, height: 1000);   // 沿 +Z 拉伸
// 其余工厂：Rectangle(width, height) / Channel(webHeight, flangeWidth, webThickness, flangeThickness)
//          SquareTube(width, height, thickness) / Trapezoid(topWidth, bottomWidth, height)
//          Capsule(rectWidth, radius) / LShape(vertical, horizontal, thickness)
```

`Profiles` 返回 `Profile2D` 记录（另有 `PolygonProfile` 可给任意逆时针闭合点列），与 `CsgNodes.Extrude(profile, height)` / `ExtrudeNode` 配合生成实体。

### 三视图投影与圆弧识别

```csharp
// 实体 → STL → 读回三角网格 → 投影出正交视图（主视 / 俯视 / 左视，第一角法）
using var fs = File.Create("part.stl");
using var bw = new BinaryWriter(fs);
solid.WriteStl("part", bw);
fs.Close();

var triangles = ViewMeshReader.ReadStlFile("part.stl");   // IReadOnlyList<ViewTriangle>
var projector = new ViewProjector(triangles);
var views = projector.Project(ViewDirections.OrthographicThree);
// 单视图：projector.ProjectView(ViewDirections.Front)

// 每个 ViewProjection 的线段带 IsVisible（实线/虚线，已做遮挡判断），
// 再用 ViewArcFitter 把投影折线拟合回圆弧
```

`CsgMesh.FromCsg` / `CsgMesh.TrianglesOf` 走的是 `MeshTriangle` 网格（Y-up → Z-up 换算），供 `StlWriter` 直接写成文件；`Tessellation` 可设弦高容差控制圆角细分；`HalfPlaneCut` 提供半平面切割体（用于剖切视图）。

---

## 典型工作流

### 工作流一：创建机械零件

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

### 工作流二：带冲孔的冷弯型钢构件（建模 → 导出 → 校验）

1. 按截面尺寸拆件：腹板/上下翼缘/卷边各用 `Cube` 建板（注意 Cube 从原点正轴生长，用 `center:` 或包围盒推算落位）
2. 冲孔用"pill 形"拼法：两端圆 + 中间矩形（示例见仓库 `samples/Runner.CPurlin/CpurlinModel.cs` 的 `Punching`）
3. 逐段 `Subtract` 冲孔，再 `Union` 拼回整体；需要圆角过渡时用 `RotateX/Y/Z` 摆放圆柱体切角
4. 同时导 ASCII 与 Binary 两份 STL，用体积累等式 `A ∪ B = A + B − A ∩ B` 或外部工具做体积校验
5. 无头环境别自动弹查看器，仓库样例用 `OPENCSG_OPEN_VIEWER=1` 显式开关控制

### 工作流三：生成三视图

1. 实体先写出 STL：`WriteStl` 或 `StlWriter.WriteBinary(path, CsgMesh.TrianglesOf(solid))`
2. `ViewMeshReader.ReadStlFile(path)` 读回三角网格 → `new ViewProjector(triangles)`
3. `Project(ViewDirections.OrthographicThree)` 拿主/俯/左三视图，`ViewSegment.IsVisible` 区分实线与虚线
4. `ViewArcFitter` 把折线拟合回圆弧，落到自己的图纸坐标系
5. 需要剖视时用 `HalfPlaneCut` 先切体再投影

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
| 需要什么版本的 .NET？ | 核心库 netstandard2.0（兼容 .NET 6+），测试需要 .NET 8+，整仓 slnx 需 .NET 9+ SDK |
| Union 结果位置异常？ | 本库已修复 origin-centering 问题（来自 Csg fork 的修复） |
| 与 Hypar.Elements 的 CSG 有何区别？ | OpenCSG.NET 是独立的 CSG 库（仅依赖 System.Text.Json），Elements 内置了自己的 CSG 内核 |
| 如何处理复杂网格？ | BSP 树实现为迭代式（非递归），避免栈溢出 |
| 布尔结果有接缝/不是闭合流形 | 已知行为：没有 T 顶点清理 pass，面不会有面积洞（体积累等式可验证），但不保证严格 2-manifold |
| 镜像（负缩放）后法线错乱 | 库会按矩阵行列式识别负缩放并翻转顶点缠绕与法线，用 `Scale(-1)` / 镜像矩阵即可，不必手工修 |
| 大坐标（测量坐标）能算吗？ | 容差是绝对值 1e-5，坐标量级到 1e6 仍正确（仓库有 LargeCoordinateBooleanTest） |
| 想要"先建树再求值" | 用 `CsgNodes` 构造 `CsgNode` 树，`CsgSerialization` 转 JSON 存储，`CsgEvaluator.Evaluate` 求值 |

---

## AI 使用建议

### 推荐工作流

1. **创建基本体**：使用 `Solids.Cube()`、`Solids.Sphere()`、`Solids.Cylinder()` 创建基础形体
2. **布尔运算**：`.Subtract()`（差集）、`.Intersect()`（交集）、`Union()`（并集）
3. **变换**：`.Translate()`、`.RotateX/Y/Z()`、`.Scale()` 链式调用
4. **导出**：使用 `BinaryWriter` + `WriteStl()` 导出 Binary STL（更小文件体积）

### 关键注意事项

- **依赖**：唯一外部包是 `System.Text.Json` 8.0.6（CSG 树 JSON 用），其余零依赖，netstandard2.0 兼容现代 .NET
- **Union 位置修复**：本库已修复上游 Csg fork 的 origin-centering 问题
- **Binary STL 优先**：Binary STL 比 ASCII STL 文件体积更小，推荐使用
- **圆柱体穿透**：布尔运算时让减去的形体稍大（如高 0.1）确保完全穿透
- **非递归 BSP**：迭代式 BSP 树实现，处理复杂网格不会栈溢出
- **不要臆造**：`Cube` 只有 `(size)` / `(width,height,depth)` / `(Vector3D size, ...)` 这几种重载，没有 `Cube(x:, y:, z:)`；`CsgNodes` 里只有 `Box` 提供纯数值重载，`Cylinder`/`Cone`/`Wedge` 要用 `Vector3D` 定位；`ViewProjector` 吃 `ViewTriangle` 列表（由 `ViewMeshReader.ReadStlFile` 读入），不是 `CsgMesh` 的 `MeshTriangle`。签名以仓库源码为准

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

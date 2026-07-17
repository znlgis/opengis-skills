---
name: ara3d-sdk
description: "Use when processing AEC/BIM 3D data in .NET 8 �?mesh generation and transformation, SIMD-accelerated math, IFC/STEP/PLY to glTF/GLB/VIM conversion, plugin development. Ara3D-SDK: high-performance .NET 3D geometry and BIM library suite."
tags:
  - 3d
  - bim
  - aec
  - dotnet
  - csharp
  - geometry
  - simd
  - ifc
  - mesh
  - gltf
  - studio-plugin
---

> **项目地址�?* <https://github.com/ara3d/ara3d-sdk>
>
> **NuGet 元包�?* [`Ara3D.SDK`](https://www.nuget.org/packages/Ara3D.SDK) �?**Ara 3D 官网�?* <https://ara3d.com>
>
> **许可证：** MIT �?**最新版本：** `1.6.1`（由仓库 `Directory.Build.props` �?`Ara3DVersion` 统一管理，所有包共享同一版本号）�?**默认分支�?* `main` �?**目标框架�?* `net8.0` / `net8.0-windows`

## 概述

**Ara3D-SDK** 是面�?**AEC / BIM / 数字孪生 / 三维 GIS** 场景的高性能 .NET 三维数据处理引擎�?Studio 插件框架。它有两大定位：

1. **独立的高性能三维/BIM 工具�?*：加载、生成、变换、导出海量三维几何与 BIM 数据�?
2. **Ara 3D Studio 桌面应用的扩展底�?*：通过 `Ara3D.Studio.API` 编写生成器、修改器、命令与工具，把自研算法接入 Studio 的可视化流程图（Flow Graph）�?

核心工程亮点�?

| 能力 | 说明 |
|------|------|
| **统一高性能内存模型** | `Ara3D.Memory` 提供 64 字节对齐的非托管缓冲区、`ByteSlice`、内存映射文件视图，服务 SIMD 与超大数据集 |
| **SIMD 加速数�?* | `Ara3D.F8`（AVX 8 �?`float`�? **Plato DSL** 生成�?`Vector3`/`Matrix4x4`/`Quaternion`/`Number`/`Angle` 等数学类�?|
| **不可变几何内�?* | `TriangleMesh3D`/`QuadGrid3D` 的所有变换均返回新对象，天然适合函数式管线与并行 |
| **BIM 开放模式（BOS�?* | �?IFC/Revit 数据规约为列�?EAV 结构，可落地�?Parquet / DuckDB / Excel |
| **可插�?Studio 框架** | 几十行代码写出参数化生成器或网格修改器，实时预览 |
| **�?少外部依�?* | 大多数库零外�?NuGet 依赖，便于审计与集成 |

> 一句话定位：Ara3D-SDK 是「面�?AEC 的高性能 .NET 三维数据处理引擎 + Studio 插件框架」，代码结构清晰、几乎零外部依赖，也是学习现代高性能 .NET 图形/BIM 工程的范本�?

> **版本提示�?* Ara3D-SDK 处于活跃开发中，具体类名与方法签名可能随版本演进。请以你实际引用�?NuGet 包版本与源码为准，并让所�?Ara3D 包保�?*同一版本�?*�?

---

## 仓库结构（monorepo�?

| 目录 | 职责 |
| --- | --- |
| `src/` | **受支持的 SDK �?*�?NuGet 元包（跨平台基础、几何、I/O、BIM、Studio API�?|
| `ext/` | Windows 专属扩展：`Ara3D.IfcLoader`（原�?IFC 加载）、`Ara3D.Utils.Wpf`（WPF 辅助�?|
| `apps/` | 独立桌面应用（如 BOS Browser�?|
| `examples/` | 示例与用法演示（Workshop 课程、Studio 脚本示例、Tools 工具�?|
| `plugins/` | 宿主插件（Bowerbird 实时脚本、Revit 加载项） |
| `integrations/` | 可选第三方适配器（�?Assimp�?|
| `tests/` | NUnit 单元测试、回归测试、开发者测�?|
| `vendor/` | 必需的第三方原生库（�?`web-ifc-library.dll`�?|
| `toolchain/` | 开发工具（�?IfcTypeGen），`IsPackable=false`，不打包 |
| `deprecated/` | 已不再维护的旧项�?|
| `build/` | 打包清单 `packages.txt` �?`PackAll.proj` |
| `docs/` | 工作流、包依赖图、发布流程等文档 |

**关键原则**：只�?`src/` �?`ext/` 下的库会被打包成 NuGet（见 `build/packages.txt`）；`toolchain/`、`tests/`、`apps/`、`examples/` 等永不进入发布产物�?

---

## 四个元包与分层架�?

Ara3D-SDK 提供四个**元包（meta-package�?*——它们不含源码，只捆绑依赖，方便按需选择最小可用集合：

```
Ara3D.SDK  (net8.0-windows �?完整 Windows 技术栈)
├── Ara3D.SDK.Core            net8.0         �?跨平台基础（Utils/Logging/Memory/Collections/...�?
├── Ara3D.SDK.Geometry        net8.0         �?网格、模型、SIMD 数学
├── Ara3D.SDK.IO              net8.0-windows �?文件格式、BOS、IFC
├── Ara3D.Studio.API          �?Studio 插件 API
└── Ara3D.Utils.Wpf           �?WPF 辅助（ext/�?
```

**选择建议�?*

- 只需**跨平�?*基础工具或几何计�?�?`Ara3D.SDK.Core` �?`Ara3D.SDK.Geometry`（Linux/macOS 亦可）；
- 需要在 **Windows** 上读写各种三�?BIM 文件 �?`Ara3D.SDK.IO`�?
- 想「一包搞定几乎所有事情」（�?WPF、IFC、Studio API）→ `Ara3D.SDK`�?

**依赖层次（自底向上五层）�?*

1. **基础层（零内部依赖）**：`Collections`、`Events`、`F8`、`Memory`、`Utils`、`WorkItems`�?
2. **核心�?*：`Logging→Utils`、`Utils.Roslyn→Logging`、`Geometry→Collections+Memory+Utils`、`PropKit→Geometry+Utils`�?
3. **数据�?*：`DataTable→Collections+PropKit`、`Models→Collections+F8+Memory+Geometry`�?
4. **I/O �?*：`IO.BFAST→Memory+Utils`、`IO.G3D→Collections+BFAST`、`IO.StepParser→Memory+Logging+Utils` 等；
5. **BIM �?*：`BimOpenSchema→DataTable+Geometry+Models`、`IfcLoader→BimOpenSchema+StepParser+Models`、`BimOpenSchema.IO→BimOpenSchema+IfcLoader`�?

> 大多数库**零外�?NuGet 依赖**。少数例外：`Utils.Roslyn`（Roslyn 编译器）、`IO.GltfExporter`（Newtonsoft.Json）、`BimOpenSchema.IO`（ClosedXML/DuckDB.NET/Parquet.Net），以及 `IfcLoader` 携带的原�?`web-ifc-library.dll`�?

### 核心库一�?

| 元包 | 主要�?| 说明 |
|------|--------|------|
| **Core** (`net8.0`) | `Ara3D.Collections` | 只读列表视图、稀疏矩阵、LINQ 辅助 |
| | `Ara3D.DataTable` | 列式内存数据接口（struct-of-arrays�?|
| | `Ara3D.Events` | 线程安全事件总线 |
| | `Ara3D.F8` | SIMD（AVX�? �?`float` 数学 |
| | `Ara3D.Logging` | 日志、进度与任务管理 |
| | `Ara3D.Memory` | 对齐缓冲区、切片、内存映射文件视�?|
| | `Ara3D.PropKit` | 运行时属性描述符（UI 绑定�?|
| | `Ara3D.Utils` / `Ara3D.Utils.Roslyn` | 通用工具 / Roslyn 编译辅助 |
| | `Ara3D.WorkItems` | 后台工作项队�?|
| **Geometry** (`net8.0`) | `Ara3D.Geometry` | 网格、拓扑、空间查询、程序化建模、导�?|
| | `Ara3D.Models` | 场景模型、实例、渲染缓冲区 |
| | `Ara3D.F8` + Plato 生成数学 | `Vector3`/`Matrix4x4`/`Quaternion`/`Number`/`Angle`（`src/Plato.Generated`、`src/Plato.Intrinsics`�?|
| **IO** (`net8.0-windows`) | `Ara3D.IO.BFAST` | 数组序列化二进制容器格式 |
| | `Ara3D.IO.G3D` | G3D 几何交换格式（基�?BFAST�?|
| | `Ara3D.IO.PLY` | PLY 网格导入/导出 |
| | `Ara3D.IO.GltfExporter` / `Ara3D.IO.SharpGLTF` | glTF/GLB 导出 / 导入操作 |
| | `Ara3D.IO.VIM` | VIM BIM 二进制格�?|
| | `Ara3D.IO.StepParser` | ISO STEP 分词与解�?|
| | `Ara3D.IO.GeoJson` | GeoJSON �?IMDF 室内地图 |
| **BIM** | `Ara3D.BimOpenSchema` | BIM 开放模式（BOS）对象模�?|
| | `Ara3D.BimOpenSchema.IO` | Parquet/DuckDB/Excel 序列化与 IFC 导入 |
| | `Ara3D.IfcLoader`（ext/�?| IFC �?BOS 转换（原�?web-ifc�?|
| **Studio** | `Ara3D.Studio.API` | 流程图、资产与修改器管线类�?|

---

## 环境准备与安�?

### 环境要求

- **.NET 8 SDK**（`dotnet --version` 输出 `8.x`）；
- IDE�?*Visual Studio 2022**�?7.8+）�?*JetBrains Rider** �?**VS Code + C# Dev Kit**�?
- **文件 I/O、IFC、WPF** 等功能需 **Windows x64**（目标框�?`net8.0-windows`，`Ara3D.IfcLoader` 依赖原生 64 �?DLL）；
- 仅做**跨平�?*基础工具与几何计算（Core / Geometry）时，Linux / macOS 亦可�?

> **CPU 提示�?* `Ara3D.F8` 使用 **AVX**�?56 位）指令，`Ara3D.Memory` �?64 字节对齐以适配 AVX-512。现�?x64 CPU 均支�?AVX，SDK 在不支持时有回退路径，但要获得最佳性能建议使用较新�?x64 处理器�?

### 目标框架（TFM）分�?

| �?| TFM | 原因 |
| --- | --- | --- |
| `Ara3D.SDK.Core` / `Ara3D.SDK.Geometry` | `net8.0` | 跨平�?|
| `Ara3D.SDK.IO` / `Ara3D.SDK` | `net8.0-windows` | I/O、BOS、IfcLoader、WPF 需 Windows |
| `Ara3D.Utils.Wpf` / `Ara3D.IfcLoader`（ext/�?| `net8.0-windows` | WPF / 原生 x64 DLL |

### 通过 NuGet 引用（推荐）

```bash
dotnet new console -n MyAra3DApp
cd MyAra3DApp
dotnet add package Ara3D.SDK.Core       # 跨平台基础
dotnet add package Ara3D.SDK.Geometry   # 或几何栈
dotnet add package Ara3D.SDK            # 或完�?Windows 栈（TFM 需改为 net8.0-windows�?
```

对应 `.csproj`�?

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <!-- 引用 Ara3D.SDK / Ara3D.SDK.IO 时改�?net8.0-windows -->
    <TargetFramework>net8.0-windows</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <!-- F8/SIMD 与部�?IO 使用 unsafe 指针，必须开�?-->
    <AllowUnsafeBlocks>true</AllowUnsafeBlocks>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Ara3D.SDK" Version="1.6.1" />
  </ItemGroup>
</Project>
```

也可只引用单个库以缩小依赖面（请保持版本一致）�?

```xml
<PackageReference Include="Ara3D.Collections" Version="1.6.1" />
<PackageReference Include="Ara3D.Geometry" Version="1.6.1" />
<PackageReference Include="Ara3D.IO.PLY" Version="1.6.1" />
<PackageReference Include="Ara3D.BimOpenSchema.IO" Version="1.6.1" />
```

> `Ara3D.IfcLoader` 需 `web-ifc-library.dll`（来自仓�?`vendor/`）出现在输出目录，通过 NuGet 引用时会随包携带；平台须�?**x64 Windows**�?

### 从源码构建（二次开发）

仓库提供一�?Windows 批处理脚本（底层�?`dotnet build`/`test`/`msbuild`）：

```bat
build.bat              :: 构建整个解决方案（Debug�?
build.bat Release      :: Release 构建
test.bat               :: 运行完整测试套件（含 Slow�?
test.bat fast          :: 全部区域，跳�?Slow 的文�?I/O 测试
test.bat geometry      :: 只跑某区域（all|sdk|geometry|bim|devtools|knownissues�?
pack.bat               :: �?build/packages.txt 打包所�?NuGet（Release�?
```

打出�?`.nupkg` 写入�?gitignore �?`artifacts/` 目录。在自己的项目引用本地构建包�?

```bash
dotnet nuget add source /path/to/ara3d-sdk/artifacts --name ara3d-local
dotnet add package Ara3D.SDK --version 1.6.1 --source ara3d-local
```

---

## 快速上�?

### Hello Ara3D（验证环境）

```csharp
using System;
using System.Linq;

// Vector3 定义�?Ara3D.Geometry 命名空间
var asm = typeof(Ara3D.Geometry.Vector3).Assembly;
var types = asm.GetTypes().Where(t => t.IsPublic).OrderBy(t => t.Name).ToList();
Console.WriteLine($"Found {types.Count} types in Ara3D.Geometry");
```

### 生成并导出网格（Windows / `net8.0-windows`�?

```csharp
using Ara3D.Geometry;   // 几何类型
using Ara3D.IO.PLY;     // PLY 导入/导出

// PlatonicSolids 提供常见基本体（已三角化的立方体�?
TriangleMesh3D cube = PlatonicSolids.TriangulatedCube;

// 所有变换都是不可变的：返回新网格，可链式组�?
var transformed = cube
    .Scale(new Vector3(2, 1, 1))                                   // 非均匀缩放
    .Rotate(Quaternion.CreateFromAxisAngle(Vector3.UnitY, Angle.Degrees(30)))
    .Translate(new Vector3(0, 0, 5));

Console.WriteLine($"顶点�? {transformed.Points.Count}, 面数: {transformed.Triangles.Count}");
Console.WriteLine($"包围�? {transformed.Bounds.Min} .. {transformed.Bounds.Max}");

transformed.WritePly("cube.ply");   // WritePly �?TriangleMesh3D 的扩展方法（Ara3D.IO.PLY�?
```

### 全局 using（提升体验）

```csharp
// GlobalUsings.cs
global using Ara3D.Collections;
global using Ara3D.DataTable;
global using Ara3D.Geometry;
global using Ara3D.Logging;
global using Ara3D.Memory;
global using Ara3D.Models;
global using Ara3D.PropKit;
global using Ara3D.Studio.API;
global using Ara3D.Utils;
```

---

## 几何与网格建模（Ara3D.Geometry�?

### 不可变链式管�?

```csharp
var mesh = PlatonicSolids.TriangulatedCube
    .Scale(new Vector3(2, 1, 1))
    .RotateY(Angle.Degrees(45))
    .Translate(new Vector3(0, 0, 5));
```

`Scale`/`Rotate`/`RotateY`/`Translate` 均返�?*新对�?*（不可变），便于链式与并行�?

### 自定义变形与程序化几�?

```csharp
// �?Deform 做自定义逐点变形（如扭转�?
var twisted = mesh.Deform(p => /* 依据 p 归一化位置返回新位置 */);

// 基本体、曲线、扫掠（Sweep）、旋转成型（Revolve�?
var profile = Curves.Circle.RotateX(0.25f.Turns());
var path    = Curves.Helix(height: 3, revolutions: 3);
QuadGrid3D tube = profile.Sample(16).Sweep(path.GetTransforms(16), connectU: true, connectV: false);
TriangleMesh3D cylinder = Primitives.Cylinder(sides: 32, radius: 1, height: 3, segments: 1).Triangulate();
```

常用高层辅助：`PlatonicSolids`（`TriangulatedCube`/`Icosahedron`…）、`Primitives.Cylinder(...)`、`Curves.Circle`/`Curves.Helix(...)`（`.Sample(n)` 采样、`.GetTransforms(n)` 生成沿路径坐标系）�?

### 空间查询

- `Bounds3D`（包围体）：`mesh.Bounds` 提供 `Min`/`Max`�?
- **AABB �?*：对 `model.Meshes.Select(m => m.Bounds)` 构建，实�?`IAabbTreeQuery` �?`struct` 后用 `tree.Traverse(ref query)` 做高性能碰撞/拾取查询�?

---

## 文件 I/O 与三维格式（Ara3D.SDK.IO，Windows�?

| 场景 | API 示例 |
|------|----------|
| 读取 PLY 网格 | `PlyImporter.LoadMesh(path)` |
| 写出 PLY | `mesh.WritePly(path)` |
| 导出 glTF/GLB | `model.WriteGlb(path)`（`GltfExporter`�?|
| 导入 glTF | `ModelRoot.Load(path)`（`Ara3D.IO.SharpGLTF`�?|
| BFAST/G3D | `Ara3D.IO.BFAST` / `Ara3D.IO.G3D`（数组序列化与几何交换） |
| STEP 解析 | `Ara3D.IO.StepParser`（ISO STEP 分词/解析�?|
| VIM / GeoJSON | `Ara3D.IO.VIM` / `Ara3D.IO.GeoJson`（含 IMDF 室内地图�?|

典型「格式转换器」流程：�?IFC/STEP/PLY �?变换/轻量�?�?�?glTF/GLB�?

---

## BIM �?IFC 数据处理（BimOpenSchema�?

**BIM 开放模式（BOS�?* �?IFC/Revit 数据规约为列�?**EAV**（Entity-Attribute-Value）结构，便于查询与分析：

- **对象模型**：`IBimData` 聚合 `entities`（`EntityIndex`）、`geometry`（`BimGeometry`）、参数（`Parameters`）、关系（`EntityRelation` + `RelationType`：`ContainedIn`/`Contains`/`HostedBy`/`Hosts`/`BoundedBy`/`AssignedTo`/`GroupedBy`/`AggregatedInto`/`ConnectedTo`/`FillsVoid`/`VoidsElement`/`TypeOf`/`HasType` 等）�?
- **IFC 导入**：`IfcToBosConverter.Convert()`（底层经 `Ara3D.IfcLoader` + 原生 web-ifc）把 IFC 转为 BOS�?
- **落地导出**：`ParquetUtils`（Parquet）、`DuckDbUtils`（DuckDB）、`ExcelUtils`（`.xlsx`）、`DataTableExportUtils`，可直接进数据湖/分析引擎�?

> 用途：�?Revit/IFC 模型导出�?BOS（Parquet）进 DuckDB/数据湖做批量分析与质检�?

---

## Ara3D Studio 插件开发（Ara3D.Studio.API�?

�?C# 脚本扩展 Studio：写一个实现特定接口的类，Studio 就把它变成可交互节点/命令，参数自动生�?UI�?

### 接口体系

```csharp
public interface IScriptedComponent { FlowObject Eval(EvalContext context, FlowObject input); }
public interface IGenerator : IScriptedComponent { }   // 无输入，纯生�?
public interface IModifier  : IScriptedComponent { }   // 修改上游输入
public interface IExporter  { void Export(FlowObject obj, string path); }
```

三种语义：`IGenerator`（凭空造）、`IModifier`（改造上游）、`ILoader`（从外部读），都归约�?`IScriptedComponent.Eval`�?

### FlowObject（不可变数据流对象）

节点之间传�?`FlowObject`——把**内容、表现、属性、附�?*打包在一起：

```csharp
public class FlowObject
{
    public FlowObject WithContent(object content);
    public FlowObject WithPresentation(PresentationData p);
    public FlowObject WithAttributes(IReadOnlyList<FlowAttribute> a);
    public FlowObject WithAttachment(FlowAttachment a);
}
```

### 最小生成器示例（参数由特性自动生�?UI�?

```csharp
public class TorusGenerator : IGenerator
{
    // 用属性特性声明可调参数，Studio 自动生成滑块/输入�?
    public FlowObject Eval(EvalContext ctx, FlowObject input)
    {
        TriangleMesh3D mesh = /* �?Primitives/Curves 生成参数化网�?*/;
        return input.WithContent((IModel3D)mesh);
    }
}
```

常见范式：纯生成器（Generator）、修改器（Modifier）、加载器（Loader）、导出器（Exporter）、命�?工具（Command/Tool）�?

---

## 典型应用场景

- **三维格式转换�?*：读 IFC/STEP/PLY，写 glTF/GLB，批量转换与轻量化；
- **参数化建模工�?*：用 `IGenerator`/`IModifier` �?Studio 中生成楼梯、幕墙、屋架、管道等�?
- **BIM 数据平台**：把 Revit/IFC 导出�?BOS（Parquet）进 DuckDB / 数据湖分析；
- **自定义查看器/编辑�?*：基�?`RenderModelData` �?GPU 就绪缓冲区接入自研渲染器�?
- **Revit 加载�?*：借助 Bowerbird 实时脚本�?BOS 导出插件扩展 Revit�?

---

## AI 使用建议

- **推荐场景**：用户需�?**.NET/C# 处理三维网格、BIM/IFC 数据、格式转换（IFC/STEP/PLY↔glTF/GLB/VIM）、或开�?Ara 3D Studio 插件**时加载本技能；�?Web 3DGS 编辑请改�?[supersplat](../supersplat/SKILL.md)�?
- **TFM 选择**：只做几�?跨平�?�?`Ara3D.SDK.Geometry`（`net8.0`）；需要文�?I/O、IFC、WPF �?`Ara3D.SDK`/`Ara3D.SDK.IO`（`net8.0-windows`，仅 Windows x64）�?
- **必开 `AllowUnsafeBlocks`**：`F8`/`Memory`/`StepParser` 使用 `unsafe` 指针，`.csproj` 须设 `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>`�?
- **版本一�?*：所�?Ara3D 包共享同一版本号（当前 `1.6.1`），生成代码时不要混用不同版本�?
- **不可变几�?*：`Scale`/`Rotate`/`Translate`/`Deform` 都返回新对象，务必接收返回值（`var m2 = m.Scale(...)`），不要期望原地修改�?
- **谨慎编�?API**：SDK 活跃迭代，若不确定签名，建议先反射或查源�?NuGet 包，避免臆造类名与方法�?

---

## 常见问题（FAQ�?

| 问题 | 解答 |
|------|------|
| `AllowUnsafeBlocks` 报错 | `F8`/`Memory`/`StepParser` 使用 `unsafe` 指针，须�?`.csproj` 打开 `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>` |
| 找不�?`web-ifc-library.dll` | 使用 `Ara3D.IfcLoader` 时确保原�?DLL 复制到输出目录，且平台为 **x64 Windows**（勿�?AnyCPU 32 位） |
| `net8.0` 引用�?Windows 专属包报 TFM 不兼�?| �?`TargetFramework` 改为 `net8.0-windows` |
| 版本冲突 / API 不匹�?| 确保所�?Ara3D 包版本一致（同为 `1.6.1`�?|
| Linux/macOS 想用 IFC/PLY | 这些�?`net8.0-windows` 目标，无法在�?Windows 直接运行；可仅用 `Ara3D.SDK.Geometry` 的跨平台能力 |
| �?Xbim / OCCT 有何区别 | Xbim 专注 .NET BIM/IFC；OCCT �?C++ 几何内核。Ara3D-SDK 强调**高性能海量三维数据处理 + SIMD + BOS + Studio 插件**的一体化 .NET 方案 |

---

## 参考资�?

- **GitHub 仓库�?* <https://github.com/ara3d/ara3d-sdk>（`docs/` 含工作流、包依赖图、发布流程；`examples/Workshop` 为入门课程）
- **NuGet�?* <https://www.nuget.org/packages/Ara3D.SDK>
- **Ara 3D 官网�?* <https://ara3d.com>
- **上游中文教程�?* <https://znlgis.github.io/3d/ara3d-sdk/>�?0 章系统教程）
- **相关技能：** [supersplat](../supersplat/SKILL.md)（Web 3DGS 编辑）、[xbim](../../cad/xbim/SKILL.md)�?NET BIM/IFC）、[occt](../../cad/occt/SKILL.md)（几何内核）、[cadquery](../../cad/cadquery/SKILL.md)（参数化建模�?

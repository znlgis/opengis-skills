---
name: ifoxcad
description: "Use when developing AutoCAD plugins with .NET/C# — entity creation, layer management, block references, transaction handling. iFoxCAD: AutoCAD .NET secondary development framework with simplified API wrappers."
tags:
  - autocad
  - dotnet
  - csharp
  - cad
  - dxf
  - dwg
  - plugin
---

> **项目地址：** <https://gitee.com/inspirefunction/ifoxcad>
>
> **GitHub 镜像：** <https://github.com/inspirefunction/ifoxcad>
>
> **NuGet：** `IFox.CAD.ACAD`（AutoCAD）｜`IFox.CAD.ZCAD`（中望）｜`IFox.CAD.GCAD`（浩辰）
>
> **许可证：** MIT
>
> **版本：** 仓库默认分支为 `v0.9`（`src/Directory.Build.props` 中 `<Version>0.9.9.1</Version>`），NuGet 上 `IFox.CAD.ACAD` / `IFox.CAD.ZCAD` 已发到 0.9.12；旧包 `IFoxCAD.Cad` 停在 0.4.0，GitHub tag 只到 `v0.7.3-beta8`——**tag 不是 v0.9 线的发布信号，以默认分支与 NuGet 版本为准**

## 概述

IFoxCAD 通过统一的事务封装和大量扩展方法，让 AutoCAD .NET API 的开发体验大幅提升：

- **统一事务**：`using var tr = new DBTrans();`
- **链式扩展**：`tr.CurrentSpace.AddEntity(line, circle, ...)` 一次加入多个实体
- **多 CAD 兼容**：`src/` 下按平台分工程（`IFoxCAD.AutoCad` / `IFoxCAD.ZwCad` / `IFoxCAD.GstarCad`），共享代码在 `CADShared`，平台差异靠各自工程的 `GlobalUsings.cs` 与少量条件编译消化
- **常用工具**：选择集、用户交互、图层、块与属性、文字、标注、坐标变换、几何
- **符号表泛型封装**：`tr.LayerTable.AddOrChange("name", l => ...)`
- **菜单与命令**：`[CommandMethod]` 声明式注册

---

## 安装

### NuGet（推荐）

```bash
dotnet add package IFox.CAD.ACAD    # AutoCAD
dotnet add package IFox.CAD.ZCAD    # 中望CAD
dotnet add package IFox.CAD.GCAD    # 浩辰CAD
```

旧包名 `IFoxCAD.Cad` 对应 0.7 及更早版本，0.9 线已按平台拆包。

CAD 依赖 DLL 推荐用官方 NuGet 包，带 `ExcludeAssets="runtime"`（等价于「Copy Local=false」，不把 CAD 程序集拷进输出目录）：

```xml
<ItemGroup Condition="'$(TargetFramework)' == 'net8.0-windows'">
  <PackageReference Include="AutoCAD.NET" Version="25.0.1" ExcludeAssets="runtime" />
</ItemGroup>
```

仓库自身的组合：AutoCAD 目标 `net8.0-windows`（`AutoCAD.NET` 25.0.1，条件编译符号 `acad;a2025`）与 `net48`（`AutoCAD.NET` 20.0.0，符号 `acad;a2024`）；中望目标 `net48;net472`（符号 `zcad;z2025`）。

### 项目模板

参考官方仓库工程结构：<https://gitee.com/inspirefunction/ifoxcad>

---

## 项目骨架

```csharp
using IFoxCAD.Cad;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: ExtensionApplication(typeof(MyApp))]
[assembly: CommandClass(typeof(MyCommands))]

public class MyApp : IExtensionApplication
{
    public void Initialize() { /* 加载时执行 */ }
    public void Terminate()  { /* 卸载时执行 */ }
}
```

---

## 事务封装：DBTrans

```csharp
[CommandMethod("DRAWLINE")]
public void DrawLine()
{
    using var tr = new DBTrans();           // 自动管理 Database/Transaction
    var line = new Line(Point3d.Origin, new Point3d(100, 100, 0));
    tr.CurrentSpace.AddEntity(line);        // 加入当前空间
    tr.Commit();
}
```

`DBTrans` 自动持有：

- `Database` / `Transaction`
- `BlockTable` / `BlockTableRecord` / `LayerTable` / `TextStyleTable` / `LinetypeTable` ...
- `CurrentSpace` / `ModelSpace` / `PaperSpace`

---

## 用户交互（Editor 扩展）

```csharp
var ed = Env.Editor;

// 取点：普通单点用原厂 Editor.GetPoint(options)，先判状态再取值
var ppr = ed.GetPoint(new PromptPointOptions("\n请选择起点："));
if (ppr.Status == PromptStatus.OK)
    var p = ppr.Value;

// 带基点橡皮筋的取点用 EditorEx 扩展：GetPoint(this Editor, string message, Point3d basePoint)
var p2 = ed.GetPoint("\n下一点：", Point3d.Origin);

// 取数值：EditorEx 提供 defaultValue 重载，返回原厂 PromptResult
var dr = ed.GetDouble("\n请输入半径：", 1.0);
if (dr.Status == PromptStatus.OK) { /* dr.Value */ }

// 选择集：SSGet 支持 AutoCAD 风格的模式串（:S 单选、:A 空格拾取等）与关键字回调
var psr = ed.SSGet(filter: new SelectionFilter(new[] {
    new TypedValue((int)DxfCode.Start, "LINE")
}));
```

`Env` 是静态类，直接读运行中的 CAD：`Env.Database`、`Env.Document`、`Env.Editor`、`Env.GsManager`，另有 `Env.GetVar/SetVar`、`Env.OSMode`、`Env.OrthoMode`、`Env.AppendSupportPath(...)` 等封装。`EditorEx` 还提供 `SelectAtPoint`、`SelectByLineWeight`、`ZoomWindow/ZoomExtents/ZoomObject`、`DrawVectors/DrawCircles`（临时图形）、`GetMatrixFromUcsToWcs` 等。

---

## 实体创建与样式

```csharp
using var tr = new DBTrans();

var line = new Line(Point3d.Origin, new Point3d(10, 0, 0)) {
    LayerId    = tr.LayerTable.Add("墙体", (short)1),   // 扩展：Add(name, colorIndex)
    ColorIndex = 1
};
var circle = new Circle(new Point3d(5, 0, 0), Vector3d.ZAxis, 2);
var text   = new DBText { Position = new Point3d(0, -5, 0),
                          TextString = "Hello", Height = 2 };

tr.CurrentSpace.AddEntity(line, circle, text);   // 扩展方法支持 params Entity[]
tr.Commit();
```

---

## 块（Block）

```csharp
using var tr = new DBTrans();

// 1. 创建块定义（Add(name, Action<TRecord>) 回调里用 AppendEntity 填内容）
ObjectId btrId = tr.BlockTable.Add("MyBlock", btr => {
    btr.Origin = Point3d.Origin;
    btr.AppendEntity(new Circle(Point3d.Origin, Vector3d.ZAxis, 1));
    btr.AppendEntity(new Line(new Point3d(-1,0,0), new Point3d(1,0,0)));
});

// 2. 插入块参照
var br = new BlockReference(new Point3d(10, 10, 0), btrId);
tr.CurrentSpace.AddEntity(br);

// 3. 改块属性：BlockReferenceEx 扩展，按 tag→value 字典批量更新
br.ChangeBlockAttribute(new Dictionary<string, string> { ["TAG1"] = "VALUE1" });

tr.Commit();
```

---

## 图层

```csharp
using var tr = new DBTrans();

// 扩展方法：Add(name, colorIndex)
var layerId = tr.LayerTable.Add("钢筋", (short)2);

// 或走泛型符号表：AddOrChange(name, Action<TRecord>)
tr.LayerTable.AddOrChange("钢筋", l => {
    l.Color = Color.FromColorIndex(ColorMethod.ByColor, 2);
    l.LineWeight = LineWeight.LineWeight030;
});
```

`SymbolTable<TTable, TRecord>` 还提供 `Has(name)`、`GetRecord(name)`、`Remove(name)`、`Change(name, action)`、`ForEach(...)`、`GetRecordNames()`，各符号表（Layer/TextStyle/Linetype/DimStyle/RegApp/Ucs/View/Viewport）都走同一泛型封装。

---

## 几何运算

IFoxCAD 在 AutoCAD `Geometry` 之上补齐常用计算与转换（`CurveEx` / `GeometryEx`）：

```csharp
var line = new Line(p1, p2);
double angle = line.Angle;              // 原厂属性
double len   = line.GetLength();        // 扩展：同 Curve 的 GetLength

// 曲线打断 / 拆分
var parts = line.GetSplitCurves(new[] { 5.0 });     // 按参数拆分
var segs  = new List<Curve> { arc, circle }.BreakCurve();

// 转换为几何库对象，便于求交/求最近点
var c3d = line.ToCurve3d();
var nrb = circle.ToNurbCurve3d();

// 向量夹角（带工作平面）
double a = Vector3d.XAxis.AngleOnPlane(Plane.XY);
```

---

## 选择集与过滤

```csharp
var ed = Env.Editor;

var res = ed.GetSelection(new SelectionFilter(new[] {
    new TypedValue(0, "LINE,LWPOLYLINE"),
    new TypedValue(8, "钢筋")    // 限定图层
}));

if (res.Status == PromptStatus.OK)
{
    using var tr = new DBTrans();
    foreach (var id in res.Value.GetObjectIds())
    {
        var ent = tr.GetObject<Entity>(id);
        ent.ColorIndex = 1;
    }
    tr.Commit();
}
```

---

## 命令注册

```csharp
public class MyCommands
{
    [CommandMethod("MY_HELLO", CommandFlags.Modal)]
    public void Hello() => Env.Editor.WriteMessage("\nHello IFoxCAD");

    [CommandMethod("MY_PUR", CommandFlags.Session)]
    public void Purge() { /* ... */ }
}
```

---

## 多 CAD 兼容

v0.9 线把平台差异拆到各自工程里（`src/IFoxCAD.AutoCad`、`src/IFoxCAD.ZwCad`、`src/IFoxCAD.GstarCad`），共享代码在 `src/CADShared`。主要手法是**每个平台工程一个 `GlobalUsings.cs` 做全局 using 与别名对齐**（如把 `Application` 别名成 `Acap`、`Core.Application` 别名成 `Acaop`），少量差异点再用条件编译：

| 平台 | 符号 | 命名空间根 | 目标框架（仓库自身） |
|------|------|------------|----------------------|
| AutoCAD | `acad` + `a2024` / `a2025` | `Autodesk.AutoCAD.*` | `net48` / `net8.0-windows` |
| 中望CAD | `zcad` + `z2025` | `ZwSoft.ZwCAD.*` | `net48;net472` |
| 浩辰CAD | `gcad` | `Gssoft.Gscad.*` | 工程保留，打包暂时屏蔽 |

```csharp
#if zcad
    using ZwSoft.ZwCAD.DatabaseServices;
#else
    using Autodesk.AutoCAD.DatabaseServices;
#endif
```

自己写跨平台插件时，按同样思路：每个平台一个 csproj + 一份全局 using，引用对应平台的 NuGet 包（`IFox.CAD.ACAD` / `IFox.CAD.ZCAD` / `IFox.CAD.GCAD`），不要在同一 `csproj` 里同时引用几家的 CAD DLL。

---

## 典型工作流

### 工作流一：新建 AutoCAD 插件项目

1. `dotnet new classlib` 创建 .NET 类库项目
2. 通过 NuGet 添加 `IFox.CAD.ACAD` 包，并按 TFM 引用 `AutoCAD.NET` 包（`ExcludeAssets="runtime"`）
3. 创建 `IExtensionApplication` 实现类，添加 `[assembly: ExtensionApplication]` 和 `[assembly: CommandClass]` 特性
4. 在 `[CommandMethod]` 方法中编写业务逻辑：`using var tr = new DBTrans()` → 创建/修改实体 → `tr.Commit()`
5. 编译后通过 NETLOAD 加载到 AutoCAD 中运行

### 工作流二：批量处理 DWG 文件

1. 用文件名构造 `new DBTrans(fileName, commit: ...)`——内部走**侧边数据库**（`FileOpenMode`、`password`、`activeOpen` 可配），不依赖当前文档
2. 遍历 `tr.CurrentSpace`（或 `tr.ModelSpace`）中的实体，`tr.GetObject<T>(id)` 获取强类型对象
3. 根据实体类型（Line/Circle/Polyline/...）执行批量修改，修改可包在 `ent.ForWrite(e => ...)` 里
4. `tr.Commit()` 保存，输出到新 DWG

---

## 性能优化

1. **批量操作必用事务**，不要在循环里频繁开关事务
2. **嵌套调用复用顶层事务**：`DBTrans.GetTopTransaction(db)` / `DBTrans.GetTop(db)` 拿到已有事务，避免重入
3. **`Editor.Regen()`** 仅必要时调用
4. **块的修改**用 `BlockTableRecord.UpdateAnonymousBlocks` 同步实例
5. **换用 `Span<T>` / `Stream` 等现代 API**，少用 `ArrayList`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `eNotInDatabase` | 实体未加入 BlockTableRecord 即访问 Id |
| 修改后界面不刷新 | `ent.RecordGraphicsModified(true)` 或 `Editor.Regen()` |
| 引用 `acdbmgd` 报错 | 改用 `AutoCAD.NET` NuGet 包并设 `ExcludeAssets="runtime"`（等价 Copy Local=false） |
| 想在 CAD 外做单元测试 | 仓库的测试工程（`tests/TestAcad2025`、`TestGcad2025`、`TestZcad2025`）都是引用真机 `AutoCAD.NET` 包、在 CAD 进程内跑；纯脱离 CAD 的 Mock 方案官方没有提供 |
| 命令执行完实体却不存在 | `DBTrans` 走的是事务：没有 `tr.Commit()` 就 Dispose，等于回滚。`using var tr = new DBTrans();` 后务必显式提交 |
| `new DBTrans()` 直接抛异常 | 事务需要已激活的文档上下文——只能在 `[CommandMethod]` 体内或已初始化的 `IExtensionApplication` 之后使用 |
| 用户按 Esc 后读到了默认值 | 交互结果先判 `Status == PromptStatus.OK` 再取 `Value`；`GetDouble/GetInteger` 的 defaultValue 只在用户直接回车时生效 |
| 同一套代码要兼容中望/浩辰 | 按「多 CAD 兼容」章：每平台一个工程 + 一份 `GlobalUsings.cs` 做命名空间别名，别把 `Autodesk` 与国产 CAD 的 DLL 混在同一 `csproj` 引用里 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应遵循「命令定义 → DBTrans 事务 → 实体创建/修改 → Commit」的标准模式。`using var tr = new DBTrans()` 是几乎所有操作的起点，自动管理 Database 和 Transaction。
- **关键注意事项**：① 实体必须先加入 BlockTableRecord 再访问 Id，否则报 `eNotInDatabase`；② CAD 依赖优先用 `AutoCAD.NET` NuGet 包 + `ExcludeAssets="runtime"`；③ 多 CAD 兼容靠「每平台一个工程 + 全局 using 别名」，条件编译符号是小写的 `acad`/`zcad`/`gcad` 加年份；④ 插件入口需实现 `IExtensionApplication`，命令通过 `[CommandMethod]` 注册；⑤ `Env.Database`/`Env.Editor` 读的是运行中的 CAD，脱离进程不可用。
- **常用代码模式**：`using var tr = new DBTrans()` → `tr.CurrentSpace.AddEntity(...)` → `tr.Commit()`；图层用 `tr.LayerTable.Add("名称", (short)色号)` 或 `tr.LayerTable.AddOrChange("名称", l => ...)`。选择集：`ed.SSGet(filter: ...)` 或原厂 `ed.GetSelection(...)` → `tr.GetObject<T>(id)` → 修改 → `tr.Commit()`。
- **不要臆造**：不存在 `AddEntityToModelSpace`、`GetOrCreate`、`AddAttributes`、`UsingTrans()`、`Env.Application`、`GetPointResult/GetDoubleResult/GetKeyword` 这些 API；交互扩展只有 `GetPoint(message, basePoint)`、`GetDouble(message, defaultValue)`、`GetInteger`、`GetString`、`SSGet` 等。类名与签名以仓库源码（`src/CADShared`）与 API 文档为准。

---

## 相关技能

- **qcad** — 2D CAD 软件，ECMAScript 扩展与 DWG/DXF 处理：[../qcad/SKILL.md](../qcad/SKILL.md)
- **librecad** — 开源 2D CAD，DXF 编辑：[../librecad/SKILL.md](../librecad/SKILL.md)
- **libredwg** — DWG/DXF 文件格式读写库：[../libredwg/SKILL.md](../libredwg/SKILL.md)
- **lightcad** — Web 2D CAD 框架（类似二次开发场景）：[../lightcad/SKILL.md](../lightcad/SKILL.md)

---

## 参考资源

- 仓库：<https://gitee.com/inspirefunction/ifoxcad>
- API 文档：<https://inspirefunction.github.io/ifoxdoc/>
- 教程《IFoxCAD 类库从入门到精通》：<https://www.kdocs.cn/l/cc6ZXSa0vMgD>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/IFoxCAD/>

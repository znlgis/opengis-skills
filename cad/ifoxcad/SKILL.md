---
name: ifoxcad
description: IFoxCAD 是一个开源的 AutoCAD .NET 二次开发框架（基于 ObjectARX/AutoCAD .NET API），通过事务管理、扩展方法、链式 API 极大简化 AutoCAD 插件开发，支持 AutoCAD、ZWCAD、GstarCAD、BricsCAD 等主流国产/国际 CAD。
---

> **项目地址：** <https://gitee.com/inspirefunction/ifoxcad>
>
> **GitHub 镜像：** <https://github.com/inspirefunction/ifoxcad>
>
> **NuGet：** `IFoxCAD.Cad`
>
> **许可证：** LGPL-2.1

## 概述

IFoxCAD 通过统一的事务封装和大量扩展方法，让 AutoCAD .NET API 的开发体验大幅提升：

- **统一事务**：`using var tr = new DBTrans();`
- **链式扩展**：`db.AddEntityToModelSpace(line, circle, ...)`
- **多 CAD 兼容**：源码版宏控制 AutoCAD/ZWCAD/GstarCAD
- **常用工具**：选择集、用户交互、图层、块、文字、标注、坐标变换、几何
- **依赖注入**：内置 IoC 容器
- **菜单与命令**：声明式命令注册

---

## 安装

### NuGet（推荐）

```bash
dotnet add package IFoxCAD.Cad
```

项目需引用对应 CAD 的 `acdbmgd`、`acmgd`、`accoremgd`，并设置 `Copy Local = false`。

### 项目模板

参考官方模板：<https://gitee.com/inspirefunction/ifoxcad/tree/master/Examples>

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

// 取一个点
if (ed.GetPoint("\n请选择起点：").GetPointResult(out var p)) {
    // p 是 Point3d
}

// 取角度、整数、关键字
ed.GetDouble("\n请输入半径：").GetDoubleResult(out var r);
ed.GetKeyword("\n请选择 [圆(C)/矩形(R)]：", "C", "R").GetStringResult(out var k);

// 选择集
var sel = ed.SelectAll(new SelectionFilter(new[] {
    new TypedValue((int)DxfCode.Start, "LINE")
}));
```

---

## 实体创建与样式

```csharp
using var tr = new DBTrans();

var line = new Line(Point3d.Origin, new Point3d(10, 0, 0)) {
    LayerId  = tr.LayerTable.GetOrCreate("墙体", l => l.Color = ColorIndex.Red),
    ColorIndex = 1
};
var circle = new Circle(new Point3d(5, 0, 0), Vector3d.ZAxis, 2);
var text   = new DBText { Position = new Point3d(0, -5, 0),
                          TextString = "Hello", Height = 2 };

tr.CurrentSpace.AddEntity(line, circle, text);
tr.Commit();
```

---

## 块（Block）

```csharp
using var tr = new DBTrans();

// 1. 创建块定义
ObjectId btrId = tr.BlockTable.Add("MyBlock", btr => {
    btr.Origin = Point3d.Origin;
    btr.AppendEntity(new Circle(Point3d.Origin, Vector3d.ZAxis, 1));
    btr.AppendEntity(new Line(new Point3d(-1,0,0), new Point3d(1,0,0)));
});

// 2. 插入块参照
var br = new BlockReference(new Point3d(10, 10, 0), btrId);
tr.CurrentSpace.AddEntity(br);

// 3. 块属性
br.AddAttributes(("TAG1", "VALUE1"), ("TAG2", "VALUE2"));

tr.Commit();
```

---

## 图层

```csharp
using var tr = new DBTrans();
var layerId = tr.LayerTable.GetOrCreate("钢筋", l => {
    l.Color = ColorIndex.Yellow;
    l.LineWeight = LineWeight.LineWeight030;
});
```

---

## 几何运算

IFoxCAD 提供大量基于 AutoCAD `Geometry` 的扩展：

```csharp
var line = new Line(p1, p2);
double angle = line.Angle();
double len   = line.Length;

var poly = new Polyline();
poly.AddVertexAt(0, new Point2d(0, 0), 0, 0, 0);
poly.AddVertexAt(1, new Point2d(10, 0), 0, 0, 0);
poly.AddVertexAt(2, new Point2d(10, 10), 0, 0, 0);
poly.Closed = true;
double area = poly.Area;
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

IFoxCAD 通过条件编译支持：

- `IFOX_CAD2025` / `IFOX_CAD2024` ...
- `ZWCAD` / `GCAD` 等

```csharp
#if ZWCAD
    using ZwSoft.ZwCAD.DatabaseServices;
#else
    using Autodesk.AutoCAD.DatabaseServices;
#endif
```

---

## 性能优化

1. **批量操作必用事务**，不要在循环里频繁开关事务
2. **`db.UsingTrans()`** 在跨命令操作时使用
3. **`Editor.Regen()`** 仅必要时调用
4. **块的修改**用 `BlockTableRecord.UpdateAnonymousBlocks` 同步实例
5. **Span/Stream 替代 ArrayList**

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `eNotInDatabase` | 实体未加入 BlockTableRecord 即访问 Id |
| 修改后界面不刷新 | `ent.RecordGraphicsModified(true)` 或 `Editor.Regen()` |
| 引用 `acdbmgd` 报错 | 设置 `Copy Local=false` |
| 脱离 CAD 单元测试 | 用 `HostMgd` Mock 或 IFoxCAD 提供的测试基类 |

---

## 参考资源

- 仓库：<https://gitee.com/inspirefunction/ifoxcad>
- 文档与示例：<https://gitee.com/inspirefunction/ifoxcad/wikis>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/ifoxcad/>

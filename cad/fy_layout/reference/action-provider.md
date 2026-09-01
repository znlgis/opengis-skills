# FY Layout Action and Provider Patterns

Action mode, provider mode and typical secondary development scenarios split from SKILL.md.

---

## Action 模式说明

每个场布元素通常包含以下文件：

| 文件 | 说明 |
|------|------|
| `Qd{Element}.cs` | 元素实体类，继承自 LightCAD 基类，定义元素属性和序列化 |
| `Qd{Element}Def.cs` | 元素定义类 |
| `{Element}Action.cs` | ★ 2D Action——处理用户交互、参数输入、元素创建和编辑 |
| `{Element}3dAction.cs` | 3D Action——生成元素的三维模型 |
| `{Element}Set.cs` / `.Designer.cs` | 可选的属性设置面板（WinForms） |

Action 类常用方法模式：

| 方法 | 说明 |
|------|------|
| `ExecCreatePoly(args)` | 任意多边形方式创建元素（交互式点拾取） |
| `ExecCreateRec(args)` | 矩形方式创建元素 |
| `ExecCreate(args)` | 选择已有多段线转换为元素 |

---

## Provider 模式说明（QdLayoutProvider）

Provider 项目负责元素的二维形状生成（Shape）和三维实体生成（Solid），通过 `IDllProviderImporter` 接口注册。

### Provider 注册入口

```csharp
using LightCAD.Core;

namespace QdLayoutProvider
{
    public class QdLayoutDllProviderImporter : IDllProviderImporter
    {
        internal static ShapeProviderCollection ShapeProviders = new ShapeProviderCollection();
        internal static SolidProviderCollection SolidProviders = new SolidProviderCollection();

        public (ShapeProviderCollection shapeProviders, SolidProviderCollection solidProviders) GetImportProviders()
        {
            QdFenceProvider.RegistProviders();
            QdLawnProvider.RegistProviders();
            QdFoundationPitProvider.RegistProviders();
            QdGroundProvider.RegistProviders();
            QdEarthworkProvider.RegistProviders();
            QdBermProvider.RegistProviders();
            QdHardenProvider.RegistProviders();
            QdSiteProvider.RegistProviders();
            QdIntersectionProvider.RegistProviders();
            return (ShapeProviders, SolidProviders);
        }
    }
}
```

### 编写自定义 Provider 示例

以场地（Site）Provider 为例，展示如何注册一个二维形状 Provider：

```csharp
using LightCAD.Core.Component;
using LightCAD.MathLib.Csg;
using ThreeJs4Net;

namespace QdLayoutProvider
{
    internal static class QdSiteProvider
    {
        internal static void RegistProviders()
        {
            // 注册二维形状 Provider
            ConvertToProviders(new List<(string uuid, string name, CreateShape creator)>
            {
                ("61C3A847-E445-83E6-DEB7-724A1248B04D", "场地", 场地)
            });
        }

        // 二维形状生成方法
        internal static Curve2dGroupCollection 场地(LcParameterSet pset, ShapeCreator creator)
        {
            var curves = new List<Curve2d>();
            var outline = pset.GetValue<Polyline2d>("Outline");
            curves = outline.Curve2ds.Clone();
            var baseCurveGrp = new Curve2dGroup { Curve2ds = curves.ToListEx() };
            return new Curve2dGroupCollection { baseCurveGrp };
        }
    }
}
```

### 包含三维实体的 Provider 示例（出土道路）

```csharp
namespace QdLayoutProvider
{
    internal static class QdBermProvider
    {
        internal static void RegistProviders()
        {
            // 注册二维形状
            ConvertToProviders(new List<(string uuid, string name, CreateShape creator)>
            {
                ("A2802FC8-94B2-ABFD-8AA2-5CABD9CC8FAB", "出土道路", 出土道路)
            });
            // 注册三维实体
            ConvertToProvider(
                "C55AD616-A858-F513-48D9-A577B2696D94",
                nameof(GetSolid_出土道路),
                GetSolid_出土道路,
                GetSolidMats
            );
        }

        // 二维形状：基线 + 左右偏移线 + 端线
        internal static Curve2dGroupCollection 出土道路(LcParameterSet pset, ShapeCreator creator)
        {
            var width = pset.GetValue<double>("Width");
            var baseline = pset.GetValue<Line2d>("Baseline");
            var normal = baseline.Dir.Clone().RotateAround(new Vector2(), Math.PI / 2);
            var leftL = baseline.Clone().Translate(normal.Clone().MultiplyScalar(width / 2)) as Line2d;
            var rightL = baseline.Clone().Translate(normal.Clone().MultiplyScalar(-width / 2)) as Line2d;
            var curves = new List<Curve2d> { baseline.Clone(), leftL, rightL,
                new Line2d(leftL.Start.Clone(), rightL.Start.Clone()),
                new Line2d(leftL.End.Clone(), rightL.End.Clone()) };
            return new Curve2dGroupCollection { new Curve2dGroup { Curve2ds = curves.ToListEx() } };
        }

        // 三维实体：根据标高和放坡系数生成立体
        private static Solid3dCollection GetSolid_出土道路(
            LcComponentDefinition definition, LcParameterSet pset, SolidCreator creator)
        {
            var line = pset.GetValue<Line2d>("Baseline");
            var bottom = pset.GetValue<double>("Bottom");
            var factor = pset.GetValue<double>("Factor");
            var width = pset.GetValue<double>("Width");
            var eleStart = pset.GetValue<double>("ElevationStart");
            var eleEnd = pset.GetValue<double>("ElevationEnd");
            // ... 通过顶面、底面、侧面构造 Solid3d
            // 返回 Solid3dCollection
        }

        // 材质回调
        private static MaterialInfo[] GetSolidMats(
            LcComponentDefinition definition, LcParameterSet pset,
            SolidCreator creator, Solid3d solid)
        {
            return new MaterialInfo[] { pset.GetValue<MaterialInfo>("Material") };
        }
    }
}
```

---

## 典型二次开发场景

| 场景 | 涉及类/模式 | 说明 |
|------|-----------|------|
| 添加新的场布元素类型 | `LayoutElementType` + `ILcPlugin.Loaded()` | 定义新的 `ElementType`（含唯一 GUID），在插件 `Loaded()` 中注册 |
| 注册新命令 | `[CommandClass]` + `[CommandMethod]` | 在命令类中添加新方法，指定 Name 和 ShortCuts |
| 实现 2D 绘制交互 | `{Element}Action` + `IDocumentEditor` | 实现 `ExecCreatePoly` / `ExecCreateRec` / `ExecCreate` 方法 |
| 实现 3D 建模 | `{Element}3dAction` + Provider | 在 Provider 中用 `Curve2dGroupCollection` 和 `Solid3dCollection` 生成模型 |
| 添加属性设置面板 | `{Element}Set` (WinForms Form) | 创建 WinForms 面板供用户编辑元素参数 |
| 自定义 UI 菜单按钮 | `TabItem` / `TabButtonGroup` / `TabButton` | 在 `LayoutPlugin` 中添加新的按钮定义 |
| 注册形状/实体 Provider | `IDllProviderImporter` + `ConvertToProviders` | 在 Provider 项目中实现 `CreateShape` 和 `CreateSolid` 委托 |
| 曲线转换为闭合环 | `LcCurveChangeLoop.CheckLoops()` | 将多条线段/弧线拼接为闭合多段线 |

---


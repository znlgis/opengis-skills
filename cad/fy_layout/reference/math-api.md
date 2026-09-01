# FY Layout Math API Reference

Common mathematics library API reference split from SKILL.md.

---

## 常用数学库 API

| 类 | 命名空间 | 说明 |
|----|---------|------|
| `Vector2` | `LightCAD.MathLib` | 二维向量，支持加减、缩放、旋转、距离计算 |
| `Vector3` | `LightCAD.MathLib` | 三维向量 |
| `Line2d` | `LightCAD.MathLib` | 二维线段（Start / End / Dir） |
| `Line3d` | `LightCAD.MathLib` | 三维线段 |
| `Arc2d` | `LightCAD.MathLib` | 二维弧线（Center / Radius / StartAngle / EndAngle） |
| `Polyline2d` | `LightCAD.MathLib` | 二维多段线（Curve2ds / IsClosed） |
| `Circle2d` | `LightCAD.MathLib` | 二维圆 |
| `Plane` | `LightCAD.MathLib` | 平面（法向量定义） |
| `Curve2dGroup` | `LightCAD.MathLib` | 二维曲线组 |
| `Curve2dGroupCollection` | `LightCAD.MathLib` | 二维曲线组集合（Shape 返回类型） |
| `Solid3d` | `LightCAD.MathLib` | 三维实体（Name / Geometry） |
| `Solid3dCollection` | `LightCAD.MathLib` | 三维实体集合（Solid 返回类型） |
| `PlanarSurface3d` | `LightCAD.MathLib.Csg` | 平面表面，支持三角化 `Trianglate()` |
| `GeometryData` | `LightCAD.MathLib` | 几何数据（Vertices / Indices / Groups） |
| `Intersect2d` | `LightCAD.MathLib` | 二维相交计算（线线、线圆、圆圆） |

常用向量操作：

```csharp
// 向量旋转 90°
var normal = line.Dir.Clone().RotateAround(new Vector2(), Math.PI / 2);

// 向量平移
line.Clone().Translate(normal.Clone().MultiplyScalar(width / 2));

// 二维转三维
var point3d = point2d.ToVector3(elevation);

// 叉积计算法向量
var faceNormal = new Vector3().CrossVectors(dir1, dir2);

// 点相似性判断（闭合检测）
startPoint.Similarity(endPoint, 0);
```

---

$h$faq`

1. **GUID 唯一性**：每个 `ElementType` 和 Provider 的 UUID 必须全局唯一，使用 `Guid.ParseExact(..., "B")` 格式。
2. **多段线方向**：闭合多段线需检查绕行方向，使用 `ShapeUtils.isClockWise()` 判断并在必要时调用 `Reverse()`。
3. **Clone 习惯**：几何对象（`Vector2`、`Line2d`、`Polyline2d` 等）在变换前务必 `Clone()`，避免修改原始数据。
4. **Provider 项目独立**：`QdLayoutProvider` 输出到 `Build/Providers` 目录，与插件主体分离部署。
5. **调试方式**：编译后通过 VS2022 附加进程到 `lightcad.EXE` 进行断点调试。
6. **UI 注册时机**：`TabItem` 应在 `Completed()` 中通过 `AppRuntime.UISystem.AddInitTabItems()` 注册，不要在 `Loaded()` 中操作 UI。

---


---
name: projnet4geoapi
description: "Use when transforming coordinates or reading CRS definitions in .NET with ProjNet 2.1.0 (NuGet ProjNet, repo ProjNet4GeoAPI) — CoordinateSystemFactory.CreateFromWkt, CoordinateTransformationFactory.CreateFromCoordinateSystems, MathTransform.Transform, CoordinateSystemServices SRID registration. Also for 'no suitable transformation' / null from GetCoordinateSystem, EPSG codes beyond 4326 and 3857 returning null, and SharpMap projects needing the legacy ProjNet4GeoAPI 1.4.1 GeoAPI build."
tags:
  - dotnet
  - csharp
  - coordinate-systems
  - projection
  - epsg
  - wkt
  - geospatial
  - netstandard
  - sharpmap
---

> **项目地址：** <https://github.com/NetTopologySuite/ProjNet4GeoAPI>
>
> **NuGet（2.x）：** `ProjNet` 2.1.0（netstandard2.0 / netstandard2.1，截至 2026-10）
>
> **NuGet（1.x，旧版）：** `ProjNet4GeoAPI` 1.4.1（面向 GeoAPI 接口的项目，如 SharpMap 1.2）
>
> **官方文档：** <https://github.com/NetTopologySuite/ProjNet4GeoAPI/wiki>
>
> **许可证：** LGPL-2.1-or-later
>
> **维护状态：** 上游 README 明确说明维护资源不足，官方给出的替代方案是 SharpProj、DotSpatial.Projections、GDAL；新项目在需要完整 EPSG 支持时应优先考虑这些方案。

## 概述

ProjNet 是 SharpMap 时代延续下来的 .NET 坐标参考系与投影引擎，按 OGC Simple Features 模型描述坐标系，负责「点对点」的坐标转换：源坐标系 → 目标坐标系，中间可能包含基准面转换（datum transformation）。它不提供地图渲染，也不自带 EPSG 数据库，坐标系定义要么用内置常量（WGS84、WebMercator），要么由调用方提供 WKT。

- **坐标系模型**：地理坐标系、地心坐标系、投影坐标系、垂直坐标系、复合坐标系
- **转换能力**：基准面转换、地理↔投影、投影↔投影，支持 Albers、Mercator、Transverse Mercator、Lambert Conformal Conic、Polar Stereographic、Krovak 等常用投影
- **定义读写**：WKT 与 XML 互转（`CreateFromWkt` / `CreateFromXml`）
- **服务容器**：`CoordinateSystemServices` 维护 SRID → 坐标系映射与转换工厂，默认只注册 EPSG:4326 与 EPSG:3857
- **两代包**：2.x 用自带类型体系（`ProjNet.CoordinateSystems`），1.x 实现 GeoAPI 接口供 SharpMap 等老库使用

---

## 环境准备

### 安装（.NET 6+ / netstandard2.0 兼容项目）

```bash
# 2.x 系列（推荐）
dotnet add package ProjNet --version 2.1.0

# 1.x 系列：只在必须实现 GeoAPI 接口的老项目里使用（如 SharpMap 1.2）
dotnet add package ProjNet4GeoAPI --version 1.4.1
```

```powershell
# Package Manager Console
Install-Package ProjNet -Version 2.1.0
```

两个包的程序集名都是 `ProjNET.dll`，**不能同时引用**；同时引用会出现类型冲突与「找到多个同名类型」的编译错误。

### 验证

```csharp
using ProjNet.CoordinateSystems;
using ProjNet.CoordinateSystems.Transformations;

var src = GeographicCoordinateSystem.WGS84;
var tgt = ProjectedCoordinateSystem.WebMercator;
var transform = new CoordinateTransformationFactory()
    .CreateFromCoordinateSystems(src, tgt);

double[] xy = transform.MathTransform.Transform(new[] {116.397, 39.908});
Console.WriteLine($"{xy[0]:F2}, {xy[1]:F2}");   // 约 12957254.80, 4852582.10
```

```bash
dotnet run   # 能打印出 Web Mercator 米制坐标即环境正常
```

### 目标框架

| 包 | 目标框架 | 说明 |
|----|----------|------|
| `ProjNet` 2.1.0 | netstandard2.0 / netstandard2.1 | .NET Framework 4.6.1+、.NET 6/8/9 均可引用；netstandard2.0 版本额外依赖 `System.Memory` 4.6.0 |
| `ProjNet4GeoAPI` 1.4.1 | net35-client / net40-client / net45 / netstandard2.0 | 2018 年发布，只为兼容 GeoAPI 生态 |

---

## 核心 API

### 坐标系工厂

```csharp
using ProjNet.CoordinateSystems;

var factory = new CoordinateSystemFactory();

// 从 WKT 解析（EPSG 官网、GDAL 的 projinfo、QGIS 都能导出 WKT）
CoordinateSystem wgs84Utm50 = factory.CreateFromWkt(wktText);

// 从 XML 解析
CoordinateSystem fromXml = factory.CreateFromXml(xmlText);

// 组合式构造：以已有地理坐标系 + 投影参数创建投影坐标系
var gcs = GeographicCoordinateSystem.WGS84;
```

| 成员 | 说明 |
|------|------|
| `CreateFromWkt(string)` | 解析 WKT，返回 `CoordinateSystem`；失败时可能返回 `null` |
| `CreateFromXml(string)` | 解析 ProjNet 自身的 XML 表示 |
| `CreateProjectedCoordinateSystem(...)` | 手工组装投影坐标系（名称、地理坐标系、投影、线性单位、轴） |
| `CreateGeographicCoordinateSystem(...)` | 手工组装地理坐标系（角度单位、基准面、本初子午线、轴） |
| `CreateProjection(name, className, parameters)` | 按投影类名与参数创建投影 |

内置常量只有少数几个：`GeographicCoordinateSystem.WGS84`、`ProjectedCoordinateSystem.WebMercator`。其余坐标系必须自带 WKT。

### 坐标转换

```csharp
using ProjNet.CoordinateSystems;
using ProjNet.CoordinateSystems.Transformations;

var ctFactory = new CoordinateTransformationFactory();
ICoordinateTransformation ct = ctFactory.CreateFromCoordinateSystems(
    sourceCS: factory.CreateFromWkt(wgs84Wkt),
    targetCS: factory.CreateFromWkt(cgcs2000GaussKrugerWkt));

MathTransform mt = ct.MathTransform;

// 单点
double[] projected = mt.Transform(new[] {116.397, 39.908});

// 单点（元组重载，免去数组分配）
var (x, y) = mt.Transform(116.397, 39.908);

// 多点：一次调用处理整批，比循环 new 数组快得多
double[][] points = {new[] {116.0, 39.0}, new[] {117.0, 40.0}};
IList<double[]> projectedPoints = mt.TransformList(points);
```

| 类型 / 成员 | 说明 |
|-------------|------|
| `ICoordinateTransformation.SourceCS` / `TargetCS` | 源与目标坐标系 |
| `ICoordinateTransformation.MathTransform` | 实际执行数值转换的数学变换 |
| `MathTransform.Transform(double[])` | 单点转换，输入 `[x, y]` 或 `[x, y, z]`，维度由变换决定 |
| `MathTransform.Transform(double x, double y)` | 元组重载，返回 `(x, y)` |
| `MathTransform.TransformList(IList<double[]>)` | 批量转换，返回转换后的点数组列表 |
| `MathTransform.Transform(Span<double> xs, Span<double> ys)` | 分离数组的 SOA 批量转换，适合大数组 |
| `MathTransform.Inverse()` | 取逆变换，用于反向换算 |

坐标按 `x, y` 顺序解释（经度/东坐标在前，纬度/北坐标在后），ProjNet **不做轴序交换**；若拿到的 WKT 声明了 `AXIS["Latitude", NORTH]` 之类的轴序，需要调用方自行判断是否交换。

### CoordinateSystemServices：SRID 与转换缓存

```csharp
using ProjNet.CoordinateSystems;
using ProjNet.CoordinateSystems.Transformations;

var services = new CoordinateSystemServices();

// 默认只有 4326 与 3857
var wgs84 = services.GetCoordinateSystem(4326);
var mercator = services.GetCoordinateSystem(3857);

// 注册任意 EPSG 编码（值为 WKT 字符串）
var defs = new[]
{
    new KeyValuePair<int, string>(4490, cgcs2000Wkt),
    new KeyValuePair<int, string>(4547, cgcs2000GkCmwWkt),
};
var withDefs = new CoordinateSystemServices(defs);

ICoordinateTransformation ct = withDefs.CreateTransformation(4490, 4547);
double[] xy = ct.MathTransform.Transform(new[] {116.397, 39.908});
```

| 成员 | 说明 |
|------|------|
| `new CoordinateSystemServices()` | 默认注册 4326、3857 两个坐标系 |
| `new CoordinateSystemServices(IEnumerable<KeyValuePair<int,string>>)` | 用 SRID → WKT 批量注册 |
| `GetCoordinateSystem(int srid)` | 按 SRID 取坐标系；未注册返回 `null` |
| `GetCoordinateSystem(string authority, long code)` | 按授权名与编码取（内部仍走 SRID 映射） |
| `GetSRID(string authority, long code)` | 反查 SRID，未注册返回 `null` |
| `CreateTransformation(int sourceSrid, int targetSrid)` | 按 SRID 建转换，最常用 |
| `CreateTransformation(CoordinateSystem, CoordinateSystem)` | 按对象建转换 |

失败的 WKT 会被静默跳过：`CreateCoordinateSystem` 内部捕获异常并返回 `null`，因此「注册了但查不到」优先怀疑 WKT 本身不被支持（例如带 `ELLIPSOID` 关键字或使用了未实现的投影）。

---

## 典型工作流

把一批 WGS84 经纬度点位转换到 CGCS2000 3 度带高斯-克吕格投影（EPSG:4547），并写回 CSV：

**输入**：`points.csv`（`lon,lat`）
**输出**：`points_projected.csv`（`lon,lat,x,y`）

1. 用 `projinfo`（PROJ 命令行）导出目标坐标系的 WKT，避免手写投影参数
2. 在代码里用 `CoordinateSystemServices` 注册 4490 与 4547
3. 批量读取点位，调用 `MathTransform.Transform` 逐点或打包转换
4. 输出前校验坐标量级（高斯投影的东坐标通常在 6 位数字量级）

```bash
# 导出 WKT（PROJ 9.x）
projinfo EPSG:4547 -o WKT2:2019
```

```csharp
using System.Globalization;
using ProjNet.CoordinateSystems;
using ProjNet.CoordinateSystems.Transformations;

var cgcs2000 = File.ReadAllText("wkt/epsg4490.wkt");
var gk3d = File.ReadAllText("wkt/epsg4547.wkt");

var services = new CoordinateSystemServices(new[]
{
    new KeyValuePair<int, string>(4490, cgcs2000),
    new KeyValuePair<int, string>(4547, gk3d),
});

var ct = services.CreateTransformation(4490, 4547);
var mt = ct.MathTransform;

using var reader = new StreamReader("points.csv");
using var writer = new StreamWriter("points_projected.csv");
writer.WriteLine("lon,lat,x,y");

reader.ReadLine();   // 跳过表头
string? line;
while ((line = reader.ReadLine()) is not null)
{
    var parts = line.Split(',');
    double lon = double.Parse(parts[0], CultureInfo.InvariantCulture);
    double lat = double.Parse(parts[1], CultureInfo.InvariantCulture);

    double[] xy = mt.Transform(new[] {lon, lat});
    writer.WriteLine(string.Join(",",
        lon.ToString(CultureInfo.InvariantCulture),
        lat.ToString(CultureInfo.InvariantCulture),
        xy[0].ToString("F3", CultureInfo.InvariantCulture),
        xy[1].ToString("F3", CultureInfo.InvariantCulture)));
}
```

**检查点**：转换后东坐标应是 6 位数（含带号则 8 位），北坐标在 0–5000000 量级；若数值仍是 116 / 39 这样的量级，说明取错了坐标系或 WKT 解析失败被静默跳过。

---

## 最佳实践

1. **WKT 由专业工具生成**：用 `projinfo`、`gdalsrsinfo` 或 EPSG 官网导出，不要手写 `PROJCS` 字符串，参数顺序错一位结果就偏
2. **一次构造、复用实例**：`CoordinateTransformationFactory`、`CoordinateSystemFactory` 与 `MathTransform` 都可复用，避免在循环里重复解析 WKT
3. **批量用 `TransformList` 或 `Span` 重载**：`MathTransform.TransformList(IList<double[]>)` 一次处理整批点；SOA 结构的大数组用 `Transform(Span<double> xs, Span<double> ys)` 避免装箱
4. **校验转换前后的量级与范围**：投影坐标是米，经纬度是度；写一条断言比肉眼检查可靠
5. **明确轴序**：ProjNet 只做 `x, y` 算术，不理会 WKT 的 `AXIS` 声明，跨系统交换数据时显式约定顺序
6. **坐标是数值不是几何**：ProjNet 只处理点数组，几何对象的转换要自己遍历坐标（或用 NTS 的坐标过滤器）
7. **考虑替代方案**：需要完整 EPSG 库、网格文件（NTv2/GTX）或 3D 基准转换时，用 SharpProj 或 GDAL，不要指望 ProjNet 覆盖

---

## 常见问题

| 问题 | 原因与解决 |
|------|------------|
| `CreateFromCoordinateSystems` 返回 `null` 或抛异常 | 源/目标坐标系类型组合不受支持（如两个地理坐标系之间只差基准面而缺少转换参数）：改用「地理 → 投影」或先转 WGS84 再转目标 |
| `GetCoordinateSystem(4490)` 返回 `null` | `CoordinateSystemServices` 默认只注册 4326 与 3857：用 SRID → WKT 的构造函数注册，或直接 `CreateFromWkt` |
| 转换结果与 QGIS/GDAL 差几十米 | ProjNet 没有网格文件与最新基准面参数，只做近似七参数/三参数转换：高精度场景改用 SharpProj 或 GDAL |
| 注册了 WKT 但查不到坐标系 | `CreateCoordinateSystem` 会吞掉解析异常：先用 `new CoordinateSystemFactory().CreateFromWkt(wkt)` 单独验证，确认返回非 `null` |
| 经纬度转换结果是反的 | 输入数组按 `[x, y]` 解释，即经度在前：把 `[lat, lon]` 改成 `[lon, lat]` |
| 同时引用两个包后大量类型冲突 | `ProjNet` 2.x 与 `ProjNet4GeoAPI` 1.x 程序集同名：只保留一个；SharpMap 1.2 项目必须用 1.4.1 |
| 老项目里 `CoordinateTransformation` 赋值编译失败 | SharpMap 1.2 期望 GeoAPI 的 `ICoordinateTransformation`，2.x 不再实现该接口：换成 `ProjNet4GeoAPI` 1.4.1 |
| 大文件转换极慢 | 在循环里反复解析 WKT 或逐点 new 转换对象：把工厂、坐标系、`MathTransform` 提到循环外，并用打包数组接口 |

---

## AI 使用建议

- **执行环境**：`dotnet add package`、`dotnet build`、`dotnet run` 在终端中执行；首次 restore 需要访问 NuGet，失败时先看是否离线。
- **先探测版本**：`dotnet list package` 确认是 `ProjNet 2.1.0` 还是 `ProjNet4GeoAPI 1.4.1`——两者的命名空间与接口完全不同，写代码前必须确认，不要凭 `using ProjNet.CoordinateSystems` 猜。
- **WKT 来源**：让用户提供或先跑 `projinfo EPSG:xxxx -o WKT2:2019` 生成，再写进示例；不要凭空编造 `PROJCS` 参数。
- **验证产物**：编译后运行最小断言（如 116.397, 39.908 → Web Mercator 约 (12957254.8, 4852582.1)），数值量级不对就说明坐标系或轴序取错。
- **失败信号**：`null` 返回值优先怀疑 WKT 解析；结果偏差固定为几十米量级，是缺少网格文件而非代码错误。
- **安全与权限**：新建工程、装包前征得用户同意；示例里的 WKT 文件路径用占位符，不要写入用户真实数据路径。

## 相关技能

- **nettopologysuite** — .NET 几何运算，常与 ProjNet 搭配做「几何转换 + 空间分析」：[../nettopologysuite/SKILL.md](../nettopologysuite/SKILL.md)
- **sharpmap** — 旧版 .NET 地图渲染库，坐标变换依赖 ProjNet/ProjNet4GeoAPI：[../sharpmap/SKILL.md](../sharpmap/SKILL.md)
- **mapsui** — 现代跨平台 .NET 地图组件，新项目优先考虑：[../mapsui/SKILL.md](../mapsui/SKILL.md)
- **proj** — PROJ 命令行，用于导出 WKT 与核对转换结果：[../proj/SKILL.md](../proj/SKILL.md)
- **gdal** — GDAL/OGR 命令行，可做高精度重投影与批量转换：[../gdal/SKILL.md](../gdal/SKILL.md)

## 参考资源

- Wiki（FAQ、常用 WKT）：<https://github.com/NetTopologySuite/ProjNet4GeoAPI/wiki>
- 源码：<https://github.com/NetTopologySuite/ProjNet4GeoAPI>
- NuGet（2.x）：<https://www.nuget.org/packages/ProjNet>
- NuGet（1.x）：<https://www.nuget.org/packages/ProjNet4GeoAPI>
- EPSG 坐标系查询：<https://epsg.org/>（EPSG 官方注册库；<https://spatialreference.org/> 可查 OGC WKT）

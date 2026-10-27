---
name: nettopologysuite
description: "Use when doing 2D computational geometry in .NET with NuGet NetTopologySuite 2.6.0 — GeometryFactory with SRID, Contains/Intersects predicates, Intersection/Union/Buffer overlays, STRtree, GeometryFixer, WKT/WKB/GeoJSON I/O, Shapefile via IO.Esri, and EF Core spatial queries on SQL Server/Npgsql."
tags:
  - dotnet
  - csharp
  - geometry
  - spatial
  - wkt
  - wkb
  - geojson
  - ef-core
  - npgsql
---

> **项目地址：** <https://github.com/NetTopologySuite/NetTopologySuite>
>
> **NuGet：** `NetTopologySuite`（最新稳定版 2.6.0，截至 2026-10，NuGet）
>
> **官方文档：** <https://nettopologysuite.github.io/NetTopologySuite/>
>
> **许可证：** BSD-3-Clause

## 概述

NTS 与 JTS API 几乎一一对应（C# 命名风格）：

- **几何模型**：`Point`/`LineString`/`Polygon`/`Multi*`/`GeometryCollection`
- **空间关系**：`Equals`/`Contains`/`Within`/`Intersects`/`Touches`/`Crosses`/`Overlaps`/`Disjoint`/`Relate`
- **集合运算**：`Intersection`/`Union`/`Difference`/`SymmetricDifference`/`Buffer`
- **几何分析**：`ConvexHull`/`Centroid`/`Area`/`Length`/`Distance`/`IsValid`/`Simplify`
- **空间索引**：`STRtree`/`Quadtree`
- **格式读写**：WKT、WKB、GeoJSON、Shapefile（独立 NuGet）
- **EF Core 集成**：SqlServer 与 PostgreSQL 自动翻译为空间 SQL

---

## 环境准备

```bash
dotnet add package NetTopologySuite --version 2.6.0

# GeoJSON：按序列化框架二选一（不要同时装）
dotnet add package NetTopologySuite.IO.GeoJSON --version 4.0.0       # Newtonsoft.Json
dotnet add package NetTopologySuite.IO.GeoJSON4STJ --version 4.0.0    # System.Text.Json

dotnet add package NetTopologySuite.IO.Esri.Shapefile --version 1.2.0 # Shapefile 读写
dotnet add package ProjNet --version 2.1.0                            # 坐标变换（可选）
```

**.NET 6+** 推荐；各 IO 包需与主库 2.6 对齐（IO.GeoJSON / IO.GeoJSON4STJ / IO.Esri.Shapefile 均为 4.0.0、1.2.0 一档，ProjNet 2.1.0）。

---

## 核心 API：几何工厂

```csharp
using NetTopologySuite;
using NetTopologySuite.Geometries;

// 推荐：由 NtsGeometryServices 提供工厂（也可继续用 new GeometryFactory(new PrecisionModel(), 4326)）
var gf = NtsGeometryServices.Instance.CreateGeometryFactory(srid: 4326);

// 等价旧写法：var gf = new GeometryFactory(new PrecisionModel(), 4326);

var p  = gf.CreatePoint(new Coordinate(116.397, 39.908));
var ls = gf.CreateLineString(new[] {
    new Coordinate(116, 39), new Coordinate(117, 40)
});
var poly = gf.CreatePolygon(new[] {
    new Coordinate(0,0), new Coordinate(10,0),
    new Coordinate(10,10), new Coordinate(0,10), new Coordinate(0,0)
});
```

---

## 空间关系与运算

```csharp
bool b   = polyA.Intersects(polyB);
var inter = polyA.Intersection(polyB);
var union = polyA.Union(polyB);
var diff  = polyA.Difference(polyB);

var buf  = p.Buffer(100);
var hull = mp.ConvexHull();
double area = poly.Area;
double len  = ls.Length;
double dist = polyA.Distance(polyB);

string rel = polyA.Relate(polyB).ToString();
bool ok    = polyA.Relate(polyB, "T*F**F***");
```

---

## WKT / WKB / GeoJSON

```csharp
using NetTopologySuite;
using NetTopologySuite.IO;

// NTS 2.6 起推荐由 NtsGeometryServices 提供工厂（WKTReader(GeometryFactory) 已标记过时）
var services = NtsGeometryServices.Instance;
var rdr = new WKTReader(services);
var g = rdr.Read("POINT (116.4 39.9)");

string wkt = new WKTWriter().Write(g);
byte[] wkb = new WKBWriter().Write(g);
```

GeoJSON 有两种包，按序列化框架二选一（两者都需与主库 2.6 对齐，均取 4.0.0）：

| 包 | 序列化框架 | 用法 |
|---|---|---|
| `NetTopologySuite.IO.GeoJSON` | Newtonsoft.Json 13.x | `new GeoJsonReader()` / `new GeoJsonWriter()` |
| `NetTopologySuite.IO.GeoJSON4STJ` | System.Text.Json | `opts.Converters.Add(new GeoJsonConverterFactory())` |

```csharp
using NetTopologySuite.IO.Converters;   // 来自 NetTopologySuite.IO.GeoJSON4STJ
using System.Text.Json;

var opts = new JsonSerializerOptions();
opts.Converters.Add(new GeoJsonConverterFactory());
string json = JsonSerializer.Serialize(g, opts);
var g2 = JsonSerializer.Deserialize<Geometry>(json, opts);
```

Newtonsoft 方案：

```csharp
using NetTopologySuite.IO;

var writer = new GeoJsonWriter();
string json2 = writer.Write(g);
var g3 = new GeoJsonReader().Read(json2);
```

---

## Shapefile

```csharp
using NetTopologySuite.IO.Esri;
foreach (var f in Shapefile.ReadAllFeatures("input.shp"))
    Console.WriteLine($"{f.Geometry} {f.Attributes["NAME"]}");

Shapefile.WriteAllFeatures(features, "output.shp");
```

---

## 空间索引

```csharp
using NetTopologySuite.Index.Strtree;

var tree = new STRtree<Geometry>();
foreach (var g in geometries)
    tree.Insert(g.EnvelopeInternal, g);
tree.Build();

var hits   = tree.Query(queryEnv);
var nearby = tree.NearestNeighbour(p.EnvelopeInternal, p, new GeometryItemDistance());
```

---

## 几何修复与简化

```csharp
using NetTopologySuite.Operation.Valid;
using NetTopologySuite.Simplify;
using NetTopologySuite.Geometries.Utilities;

if (!poly.IsValid)
    poly = (Polygon)GeometryFixer.Fix(poly);

var simp = TopologyPreservingSimplifier.Simplify(poly, 0.001);
```

---

## EF Core + SQL Server / PostgreSQL

```bash
dotnet add package Microsoft.EntityFrameworkCore.SqlServer.NetTopologySuite
# 或
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL.NetTopologySuite
```

```csharp
public class City {
    public int Id { get; set; }
    public string Name { get; set; }
    public Point Location { get; set; }
    public Geometry Boundary { get; set; }
}

services.AddDbContext<AppDb>(o =>
    o.UseSqlServer(conn, x => x.UseNetTopologySuite()));

var nearby = db.Cities
    .Where(c => c.Location.Distance(target) < 5000)
    .OrderBy(c => c.Location.Distance(target))
    .Take(10)
    .ToList();   // 自动翻译为空间 SQL
```

---

## 坐标系转换（ProjNet）

```csharp
using ProjNet.CoordinateSystems;
using ProjNet.CoordinateSystems.Transformations;

var src = GeographicCoordinateSystem.WGS84;
var tgt = ProjectedCoordinateSystem.WebMercator;
var ct  = new CoordinateTransformationFactory()
            .CreateFromCoordinateSystems(src, tgt);
double[] xy = ct.MathTransform.Transform(new[] { 116.397, 39.908 });
```

---

## 典型工作流

端到端：WKT 读入 → 有效性修复 → 空间运算 → 写 GeoJSON / 入库。

```csharp
using NetTopologySuite;
using NetTopologySuite.Geometries;
using NetTopologySuite.Geometries.Utilities;
using NetTopologySuite.IO;
using NetTopologySuite.IO.Converters;   // NetTopologySuite.IO.GeoJSON4STJ
using System.Text.Json;

// 1. 读入两个输入几何（第二个是自相交的"蝴蝶结"，无效）
var services = NtsGeometryServices.Instance;
var reader = new WKTReader(services);
Geometry parcel = reader.Read("POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))");
Geometry zone = reader.Read("POLYGON ((5 5, 15 15, 15 5, 5 15, 5 5))");

// 2. 校验并修复（GeometryFixer 可能把无效面拆成 MultiPolygon）
Console.WriteLine(zone.IsValid);                 // False
if (!zone.IsValid)
    zone = GeometryFixer.Fix(zone);               // 修成 MultiPolygon，IsValid=True

// 3. 空间运算：求交 + 缓冲
Geometry overlap = parcel.Intersection(zone);
Geometry buffered = overlap.Buffer(1.0);
Console.WriteLine(overlap.Area);                  // 12.5（两三角形在方形内的部分）

// 4. 写 GeoJSON（System.Text.Json 转换器，需 GeoJSON4STJ 包）
var opts = new JsonSerializerOptions();
opts.Converters.Add(new GeoJsonConverterFactory());
string geoJson = JsonSerializer.Serialize(buffered, opts);

// 5. 回读校验
Geometry back = JsonSerializer.Deserialize<Geometry>(geoJson, opts);
Console.WriteLine(back.IsValid);                  // True
```

**输出与验收**：`geoJson` 能以 `JsonSerializer.Deserialize<Geometry>` 读回且 `back.IsValid` 为 `true`；`overlap.Area` 为 12.5（面积只在投影/平面坐标下有实际含义，经纬度下是平面近似值）。

**其他常用步骤**：

1. **创建几何工厂**：跨方法共享同一个 `GeometryFactory` 并固定 SRID，避免几何间 SRID 不一致
2. **空间索引**：数据量超过几千条时先建 `STRtree`，再做批量 `Intersects` 粗筛
3. **格式读写**：`WKTReader`/`WKTWriter`、`GeoJsonConverterFactory`；Shapefile 走 `NetTopologySuite.IO.Esri`
4. **EF Core 集成**：`UseNetTopologySuite()` 让 `Distance()`/`Intersects()` 翻译为空间 SQL

---

## 性能优化

1. 共享 `GeometryFactory`，固定 SRID
2. 大批量空间查询用 STRtree
3. WKB 比 WKT 更快更紧凑
4. 多次空间关系判断使用 `PreparedGeometry`：

```csharp
using NetTopologySuite.Geometries.Prepared;
var prep = PreparedGeometryFactory.Prepare(largePoly);
foreach (var p in points) if (prep.Contains(p)) ...
```

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `TopologyException` | `GeometryFixer.Fix` 修复无效几何 |
| EF Core 类型冲突 | 用 `UseNetTopologySuite()` 而非 `Microsoft.SqlServer.Types` |
| Z/M 坐标丢失 | 配置 `WKBWriter` 的 `HandleOrdinates` |
| 找不到 `GeoJsonConverterFactory` | 该类属于 `NetTopologySuite.IO.GeoJSON4STJ`（System.Text.Json），不是 `NetTopologySuite.IO.GeoJSON`（Newtonsoft） |
| Buffer 慢 | 减小 quadrantSegments、并行处理 |
| Shapefile 读取写法报错 | 使用 `NetTopologySuite.IO.Esri.Shapefile` 包与 `NetTopologySuite.IO.Esri` 命名空间（`Shapefile.ReadAllFeatures`） |
| 依赖版本不匹配（NTS 2.6 与旧 IO 包） | 对齐版本：IO.GeoJSON 4.0.0、IO.Esri.Shapefile 1.2.0、ProjNet 2.1.0 |

---

## DeepSeek Harness 使用建议

- **加载与引用**：`skill("nettopologysuite")` 加载；技能目录只读，示例工程与测试数据写到会话工作区。
- **执行环境**：命令交给 dsh 的 `pwsh`；先 `dotnet --version` 确认 SDK 6.0+，`dotnet restore` 需要访问 NuGet。
- **先探测版本**：`dotnet list package` 核对 `NetTopologySuite` 2.6.0、`NetTopologySuite.IO.GeoJSON`（或 `IO.GeoJSON4STJ`）4.0.0、`NetTopologySuite.IO.Esri.Shapefile` 1.2.0、`ProjNet` 2.1.0；IO 包与主库错配是常见编译/运行期报错源。
- **验证产物**：`dotnet build` 后跑 `dotnet test`，或最小控制台做 WKT 往返 + `IsValid` 断言；`GeoJsonConverterFactory` 序列化后再反序列化，比对坐标数而不是只打日志。
- **失败信号**：`TopologyException` 先 `GeometryFixer.Fix`；程序集加载/`TypeInitializationException` 多为 IO 包版本不匹配；EF Core 类型冲突是同时引了 `Microsoft.SqlServer.Types`。
- **注意事项**：NTS 的 SRID 只是元数据、计算在平面进行，跨投影交给 ProjNet；`WKBWriter` 默认丢 Z/M，需设 `HandleOrdinates`。
- **按需读文件**：本 SKILL 代码块较多，先按章节标题定位再用 `read` 取行区间，比整篇读更省上下文。

## NTS 家族与相关库

| 包 | 用途 |
|----|------|
| `NetTopologySuite.IO.VectorTiles` | Mapbox Vector Tiles（MVT）读写 |
| `NetTopologySuite.IO.GeoJSON` | GeoJSON 读写（Newtonsoft.Json） |
| `NetTopologySuite.IO.GeoJSON4STJ` | GeoJSON 读写（System.Text.Json，提供 `GeoJsonConverterFactory`） |
| `NetTopologySuite.IO.Esri.Shapefile` | Shapefile 读写（命名空间 `NetTopologySuite.IO.Esri`） |
| `ProjNet` | 坐标参考系与投影变换（当前主线 2.1.0；旧包 `ProjNet4GeoAPI` 停在 1.4.1，新项目用 `ProjNet`） |

## 相关技能

- **jts** — JTS Topology Suite（Java 原版）：[../jts/SKILL.md](../jts/SKILL.md)
- **geometry-api-net** — Esri Geometry API for .NET：[../geometry-api-net/SKILL.md](../geometry-api-net/SKILL.md)
- **mapsui** — .NET 跨平台地图组件：[../mapsui/SKILL.md](../mapsui/SKILL.md)
- **opengis-utils-for-net** — .NET GIS 统一工具包：[../opengis-utils-for-net/SKILL.md](../opengis-utils-for-net/SKILL.md)

## 参考资源

- 文档：<https://nettopologysuite.github.io/NetTopologySuite/>
- API：<https://nettopologysuite.github.io/NetTopologySuite/>
- JTS Javadoc（API 等价）：<https://locationtech.github.io/jts/javadoc>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/NetTopologySuite/>

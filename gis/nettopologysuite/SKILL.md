---
name: nettopologysuite
description: NetTopologySuite (NTS) 是 JTS Topology Suite 的 .NET 移植版本，是 .NET 平台上功能最完整的开源二维矢量几何计算库，提供几何模型、空间关系、集合运算、空间索引、WKT/WKB/GeoJSON 读写等能力，被 EF Core、Npgsql 等广泛集成。
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
> **NuGet：** `NetTopologySuite`
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
dotnet add package NetTopologySuite
dotnet add package NetTopologySuite.IO.GeoJSON
dotnet add package NetTopologySuite.IO.ShapeFile
dotnet add package ProjNet                          # 坐标变换（可选）
```

**.NET 6+** 推荐。

---

## 几何工厂

```csharp
using NetTopologySuite.Geometries;

var gf = new GeometryFactory(new PrecisionModel(), 4326);

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
using NetTopologySuite.IO;

var rdr = new WKTReader();
var g = rdr.Read("POINT (116.4 39.9)");

string wkt = new WKTWriter().Write(g);
byte[] wkb = new WKBWriter().Write(g);

using NetTopologySuite.IO.Converters;
using System.Text.Json;
var opts = new JsonSerializerOptions();
opts.Converters.Add(new GeoJsonConverterFactory());
string json = JsonSerializer.Serialize(g, opts);
var g2 = JsonSerializer.Deserialize<Geometry>(json, opts);
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
| Buffer 慢 | 减小 quadrantSegments、并行处理 |

---

## AI 使用建议

### 推荐工作流

1. **创建几何工厂**：使用 `new GeometryFactory(new PrecisionModel(), 4326)` 创建工厂，SRID 指定坐标系
2. **创建几何对象**：通过工厂方法 `CreatePoint()`、`CreateLineString()`、`CreatePolygon()` 创建几何
3. **空间运算**：直接调用几何对象方法 `Intersects()`、`Intersection()`、`Buffer()` 等
4. **格式读写**：使用 `WKTReader`/`WKTWriter`、`GeoJsonConverterFactory` 进行序列化
5. **EF Core 集成**：`UseNetTopologySuite()` 启用空间查询翻译为 SQL

### 关键注意事项

- **GeometryFactory 共享**：固定 SRID，复用 `GeometryFactory` 实例
- **拓扑异常修复**：无效几何使用 `GeometryFixer.Fix()` 修复
- **PreparedGeometry**：重复空间关系判断时使用 `PreparedGeometryFactory.Prepare()` 大幅提速
- **STRtree 批量查询**：先 `Build()` 再 `Query()`，大数据量场景优于逐几何判断
- **WKB vs WKT**：WKB 比 WKT 更快更紧凑，数据库交互优先使用 WKB
- **Z/M 坐标**：`WKBWriter` 需配置 `HandleOrdinates` 保留 Z/M 坐标

## 相关技能

- **jts** — JTS Topology Suite（Java 原版）：[../jts/SKILL.md](../jts/SKILL.md)
- **geometry-api-net** — Esri Geometry API for .NET：[../geometry-api-net/SKILL.md](../geometry-api-net/SKILL.md)
- **mapsui** — .NET 跨平台地图组件：[../mapsui/SKILL.md](../mapsui/SKILL.md)
- **opengis-utils-for-net** — .NET GIS 统一工具包：[../opengis-utils-for-net/SKILL.md](../opengis-utils-for-net/SKILL.md)

## 参考资源

- 文档：<https://nettopologysuite.github.io/NetTopologySuite/>
- API：<https://nettopologysuite.github.io/NetTopologySuite/api/>
- JTS Javadoc（API 等价）：<https://locationtech.github.io/jts/javadoc>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/nettopologysuite/>

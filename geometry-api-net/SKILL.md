---
name: geometry-api-net
description: geometry-api-net 是一个 .NET Standard 2.0 的空间几何计算库，提供对二维和三维几何对象的创建、解析、序列化以及空间关系运算能力。
---

> **项目地址：** https://github.com/znlgis/geometry-api-net
> 
> 本文件旨在帮助 AI 快速理解并使用 geometry-api-net 库进行空间几何开发。

## 项目概述

这是一个 .NET Standard 2.0 的空间几何计算库，提供 6 种几何类型、25+ 空间运算算子和 4 种序列化格式。

- **核心包**: `Esri.Geometry.Core`
- **JSON 扩展包**: `Esri.Geometry.Json`
- **许可证**: LGPL-2.1-only

## 快速开始

```bash
dotnet add package Esri.Geometry.Core
dotnet add package Esri.Geometry.Json    # 可选，System.Text.Json 支持
```

---

## 命名空间

| 命名空间 | 用途 |
|---------|------|
| `OpenGIS.Esri.Geometry.Core` | 核心入口，GeometryEngine 便捷 API |
| `OpenGIS.Esri.Geometry.Core.Geometries` | 几何类型（Point, Polygon 等） |
| `OpenGIS.Esri.Geometry.Core.Operators` | 空间运算算子 |
| `OpenGIS.Esri.Geometry.Core.SpatialReference` | 空间参考 / 坐标系统 |
| `OpenGIS.Esri.Geometry.Core.IO` | 序列化（WKT, WKB, GeoJSON, EsriJson） |
| `OpenGIS.Esri.Geometry.Json.Converters` | System.Text.Json 转换器 |

---

## 几何类型

### GeometryType 枚举

```csharp
public enum GeometryType
{
    Unknown = 0,
    Point = 1,
    Line = 2,
    Envelope = 3,
    MultiPoint = 4,
    Polyline = 5,
    Polygon = 6
}
```

### Geometry 基类（抽象）

所有几何类型继承自 `Geometry`，共有属性和方法：

```csharp
// 属性
geometry.Type        // GeometryType 枚举
geometry.IsEmpty     // 是否为空
geometry.Dimension   // 维度（Point=0, Line/Polyline=1, Polygon/Envelope=2）
geometry.IsPoint     // 是否为点类型
geometry.IsLinear    // 是否为线类型
geometry.IsArea      // 是否为面类型

// 方法
geometry.GetEnvelope()       // 获取外包矩形
geometry.CalculateArea2D()   // 计算面积
geometry.CalculateLength2D() // 计算长度
geometry.Copy()              // 深拷贝
geometry.IsValid()           // 是否有效
```

### Point — 点

```csharp
var p = new Point();               // 空点 (NaN)
var p = new Point(10, 20);         // 2D 点
var p = new Point(10, 20, 30);     // 3D 点 (带 Z)

p.X    // double, X 坐标
p.Y    // double, Y 坐标
p.Z    // double?, Z 坐标（可空）
p.M    // double?, M 值（可空）

p.Distance(otherPoint)                    // 计算两点距离
p.Equals(otherPoint, tolerance)           // 容差比较
```

### Line — 线段

```csharp
var line = new Line();                         // 空线段
var line = new Line(new Point(0, 0), new Point(10, 10));

line.Start    // Point, 起点
line.End      // Point, 终点
line.Length    // double, 长度
```

### Envelope — 外包矩形

```csharp
var env = new Envelope();                          // 空包围盒
var env = new Envelope(0, 0, 100, 100);            // xMin, yMin, xMax, yMax

env.XMin, env.YMin, env.XMax, env.YMax   // 边界坐标
env.Width       // 宽度
env.Height      // 高度
env.Center      // Point, 中心点
env.Area        // 面积

env.Contains(point)          // 是否包含点
env.Intersects(otherEnv)     // 是否与另一个包围盒相交
env.Merge(point)             // 合并点到包围盒
env.Merge(otherEnv)          // 合并另一个包围盒
```

### MultiPoint — 多点

```csharp
var mp = new MultiPoint();
var mp = new MultiPoint(new[] { new Point(1, 2), new Point(3, 4) });

mp.Add(new Point(5, 6));     // 添加点
mp.Count                     // 点数量
mp.GetPoint(0)               // 获取指定索引的点
mp.GetPoints()               // 获取所有点 (IEnumerable<Point>)
```

### Polyline — 折线

```csharp
var polyline = new Polyline();

// 添加路径（path），每条路径是一组连续的点
polyline.AddPath(new[] {
    new Point(0, 0), new Point(10, 0), new Point(10, 10)
});

polyline.PathCount            // 路径数量
polyline.Length                // 总长度
polyline.GetPath(0)           // 获取指定索引的路径 (IReadOnlyList<Point>)
polyline.GetPaths()           // 获取所有路径
```

### Polygon — 多边形

```csharp
var polygon = new Polygon();

// 添加环（ring），首尾点必须闭合
polygon.AddRing(new[] {
    new Point(0, 0), new Point(10, 0), new Point(10, 10),
    new Point(0, 10), new Point(0, 0)   // ← 首尾闭合
});

polygon.RingCount             // 环数量
polygon.Area                  // 面积（Shoelace 公式）
polygon.GetRing(0)            // 获取指定索引的环 (IReadOnlyList<Point>)
polygon.GetRings()            // 获取所有环
```

---

## 两种 API 风格

### 风格 1：GeometryEngine 静态方法（推荐）

`GeometryEngine` 提供所有操作的便捷静态方法入口，是最简洁的使用方式：

```csharp
using OpenGIS.Esri.Geometry.Core;

// 空间关系判断
bool result = GeometryEngine.Contains(geometry1, geometry2);
bool result = GeometryEngine.Intersects(geometry1, geometry2);
bool result = GeometryEngine.Within(geometry1, geometry2);
bool result = GeometryEngine.Disjoint(geometry1, geometry2);
bool result = GeometryEngine.Crosses(geometry1, geometry2);
bool result = GeometryEngine.Touches(geometry1, geometry2);
bool result = GeometryEngine.Overlaps(geometry1, geometry2);
bool result = GeometryEngine.Equals(geometry1, geometry2);
double dist = GeometryEngine.Distance(geometry1, geometry2);

// 集合运算
Geometry result = GeometryEngine.Union(geometry1, geometry2);
Geometry result = GeometryEngine.Intersection(geometry1, geometry2);
Geometry result = GeometryEngine.Difference(geometry1, geometry2);
Geometry result = GeometryEngine.SymmetricDifference(geometry1, geometry2);

// 几何运算
Geometry buffer   = GeometryEngine.Buffer(geometry, distance);
Geometry hull     = GeometryEngine.ConvexHull(geometry);
Geometry simple   = GeometryEngine.Simplify(geometry, tolerance);
Geometry simpleOGC = GeometryEngine.SimplifyOGC(geometry, spatialRef);
bool     isSimple = GeometryEngine.IsSimpleOGC(geometry, spatialRef);
Geometry general  = GeometryEngine.Generalize(geometry, maxDeviation);
Geometry dense    = GeometryEngine.Densify(geometry, maxSegmentLength);
Geometry clipped  = GeometryEngine.Clip(geometry, clipEnvelope);
Geometry offset   = GeometryEngine.Offset(geometry, distance);
Point    center   = GeometryEngine.Centroid(geometry);
Geometry boundary = GeometryEngine.Boundary(geometry);
double   area     = GeometryEngine.Area(geometry);
double   length   = GeometryEngine.Length(geometry);

// 大地测量
double geodesicDist = GeometryEngine.GeodesicDistance(point1, point2);
double geodesicArea = GeometryEngine.GeodesicArea(polygon);

// 邻近搜索
Proximity2DResult nearest = GeometryEngine.GetNearestCoordinate(geometry, point, testPolygonInterior);
Proximity2DResult nearest = GeometryEngine.GetNearestVertex(geometry, point);
Proximity2DResult[] results = GeometryEngine.GetNearestVertices(geometry, point, searchRadius, maxVertexCount);

// 序列化 / 反序列化
string   wkt     = GeometryEngine.GeometryToWkt(geometry);
Geometry fromWkt = GeometryEngine.GeometryFromWkt(wktString);
byte[]   wkb     = GeometryEngine.GeometryToWkb(geometry, bigEndian);
Geometry fromWkb = GeometryEngine.GeometryFromWkb(wkbBytes);
string   json    = GeometryEngine.GeometryToGeoJson(geometry);
Geometry fromJson = GeometryEngine.GeometryFromGeoJson(geoJsonString);
string   esri    = GeometryEngine.GeometryToEsriJson(geometry);
Geometry fromEsri = GeometryEngine.GeometryFromEsriJson(esriJsonString);
```

### 风格 2：Operator 单例模式

每个算子都通过 `Instance` 单例属性获取（Lazy 初始化），适合需要更精细控制的场景：

```csharp
using OpenGIS.Esri.Geometry.Core.Operators;

// 空间关系
bool contains   = ContainsOperator.Instance.Execute(geom1, geom2);
bool intersects = IntersectsOperator.Instance.Execute(geom1, geom2);
double distance = DistanceOperator.Instance.Execute(geom1, geom2);
bool equals     = EqualsOperator.Instance.Execute(geom1, geom2);
bool disjoint   = DisjointOperator.Instance.Execute(geom1, geom2);
bool within     = WithinOperator.Instance.Execute(geom1, geom2);
bool crosses    = CrossesOperator.Instance.Execute(geom1, geom2);
bool touches    = TouchesOperator.Instance.Execute(geom1, geom2);
bool overlaps   = OverlapsOperator.Instance.Execute(geom1, geom2);

// 集合运算
Geometry union        = UnionOperator.Instance.Execute(geom1, geom2);
Geometry intersection = IntersectionOperator.Instance.Execute(geom1, geom2);
Geometry difference   = DifferenceOperator.Instance.Execute(geom1, geom2);
Geometry symDiff      = SymmetricDifferenceOperator.Instance.Execute(geom1, geom2);

// 一元运算
Geometry buffer     = BufferOperator.Instance.Execute(geometry, distance);
Geometry convexHull = ConvexHullOperator.Instance.Execute(geometry);
Geometry simplified = SimplifyOperator.Instance.Execute(geometry, tolerance);
Point    centroid   = CentroidOperator.Instance.Execute(geometry);
Geometry boundary   = BoundaryOperator.Instance.Execute(geometry);
double   area       = AreaOperator.Instance.Execute(geometry);
double   length     = LengthOperator.Instance.Execute(geometry);
Geometry offset     = OffsetOperator.Instance.Execute(geometry, distance);

// 大地测量
double geodesicDist = GeodesicDistanceOperator.Instance.Execute(point1, point2);
double geodesicArea = GeodesicAreaOperator.Instance.Execute(polygon);

// 邻近搜索
Proximity2DResult result = Proximity2DOperator.Instance.GetNearestCoordinate(geometry, point, testPolygonInterior);
Proximity2DResult result = Proximity2DOperator.Instance.GetNearestVertex(geometry, point);
Proximity2DResult[] results = Proximity2DOperator.Instance.GetNearestVertices(geometry, point, searchRadius, maxVertexCount);
```

---

## 序列化格式

### WKT（Well-Known Text）

```csharp
using OpenGIS.Esri.Geometry.Core.IO;

// 导出
string wkt = WktExportOperator.ExportToWkt(geometry);
// "POINT (10.5 20.7)"
// "POINT Z (10.5 20.7 30.1)"
// "LINESTRING (0 0, 10 0, 10 10)"
// "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))"
// "MULTIPOINT ((1 2), (3 4))"

// 导入
Geometry geometry = WktImportOperator.ImportFromWkt("POINT (10.5 20.7)");
```

### WKB（Well-Known Binary）

```csharp
// 导出（默认小端序）
byte[] wkb = WkbExportOperator.ExportToWkb(geometry);
byte[] wkb = WkbExportOperator.ExportToWkb(geometry, bigEndian: true);

// 导入（自动检测字节序）
Geometry geometry = WkbImportOperator.ImportFromWkb(wkbBytes);
```

### GeoJSON

```csharp
// 导出
string geoJson = GeoJsonExportOperator.ExportToGeoJson(geometry);
// {"type":"Point","coordinates":[10.5,20.7]}

// 导入
Geometry geometry = GeoJsonImportOperator.ImportFromGeoJson(geoJsonString);
```

### Esri JSON

```csharp
// 导出
string esriJson = EsriJsonExportOperator.Instance.Execute(geometry);
// Point:      {"x":10.5,"y":20.7}
// MultiPoint: {"points":[[1,2],[3,4]]}
// Polyline:   {"paths":[[[0,0],[10,0],[10,10]]]}
// Polygon:    {"rings":[[[0,0],[10,0],[10,10],[0,10],[0,0]]]}
// Envelope:   {"xmin":0,"ymin":0,"xmax":10,"ymax":10}

// 导入
Geometry geometry = EsriJsonImportOperator.ImportFromEsriJson(esriJsonString);
```

### System.Text.Json 集成

```csharp
using OpenGIS.Esri.Geometry.Json.Converters;

var options = new JsonSerializerOptions();
options.Converters.Add(new PointJsonConverter());

string json = JsonSerializer.Serialize(point, options);
Point point = JsonSerializer.Deserialize<Point>(json, options);
```

---

## 空间参考

```csharp
using OpenGIS.Esri.Geometry.Core.SpatialReference;

// 预定义空间参考
var wgs84 = SpatialReference.Wgs84();          // EPSG:4326 (经纬度)
var webMercator = SpatialReference.WebMercator(); // EPSG:3857 (Web 墨卡托)

// 自定义 WKID
var sr = new SpatialReference(4490);            // CGCS2000

// 属性
sr.Wkid         // int?, WKID 编号
sr.LatestWkid   // int?, 最新 WKID
sr.Wkt          // string?, WKT 表示

// 组合几何与空间参考
var mapGeom = new MapGeometry(geometry, SpatialReference.Wgs84());
mapGeom.Geometry         // Geometry 对象
mapGeom.SpatialReference // SpatialReference 对象
```

---

## Proximity2DResult（邻近搜索结果）

```csharp
Proximity2DResult result = GeometryEngine.GetNearestCoordinate(geometry, point);

result.IsEmpty       // bool, 结果是否为空
result.Coordinate    // Point, 最近坐标点
result.VertexIndex   // int, 最近顶点索引
result.Distance      // double, 距离
result.IsRightSide   // bool, 是否在多路径几何的右侧
```

---

## 常见开发场景

### 场景 1：判断点是否在多边形内

```csharp
var polygon = new Polygon();
polygon.AddRing(new[] {
    new Point(0, 0), new Point(10, 0), new Point(10, 10),
    new Point(0, 10), new Point(0, 0)
});
var point = new Point(5, 5);

bool inside = GeometryEngine.Contains(polygon, point);  // true
```

### 场景 2：计算两个经纬度点之间的大地距离（米）

```csharp
var beijing = new Point(116.4074, 39.9042);
var shanghai = new Point(121.4737, 31.2304);

double meters = GeometryEngine.GeodesicDistance(beijing, shanghai);
```

### 场景 3：创建缓冲区

```csharp
var point = new Point(10, 20);
Geometry buffer = GeometryEngine.Buffer(point, 5.0);  // 半径为 5 的缓冲区

var envelope = buffer.GetEnvelope();
// XMin=5, YMin=15, XMax=15, YMax=25
```

### 场景 4：计算两个区域的交集

```csharp
var env1 = new Envelope(0, 0, 10, 10);
var env2 = new Envelope(5, 5, 15, 15);

Geometry result = GeometryEngine.Intersection(env1, env2);
// 交集区域: (5,5) 到 (10,10)
```

### 场景 5：合并多个几何体

```csharp
var p1 = new Point(0, 0);
var p2 = new Point(10, 10);

Geometry merged = GeometryEngine.Union(p1, p2);
// 结果为 MultiPoint，包含两个点
```

### 场景 6：GeoJSON 往返序列化

```csharp
var polygon = new Polygon();
polygon.AddRing(new[] {
    new Point(0, 0), new Point(1, 0), new Point(1, 1),
    new Point(0, 1), new Point(0, 0)
});

string geoJson = GeometryEngine.GeometryToGeoJson(polygon);
Geometry restored = GeometryEngine.GeometryFromGeoJson(geoJson);
```

### 场景 7：从 WKT 导入几何体并做空间分析

```csharp
var geom1 = GeometryEngine.GeometryFromWkt("POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))");
var geom2 = GeometryEngine.GeometryFromWkt("POINT (5 5)");

bool contains = GeometryEngine.Contains(geom1, geom2);  // true
double distance = GeometryEngine.Distance(geom1, geom2); // 0
```

### 场景 8：获取几何体的凸包

```csharp
var multiPoint = new MultiPoint(new[] {
    new Point(0, 0), new Point(10, 0), new Point(5, 10),
    new Point(3, 3), new Point(7, 2)
});

Geometry hull = GeometryEngine.ConvexHull(multiPoint);
// 结果为包围所有点的最小凸多边形
```

### 场景 9：计算多边形的质心

```csharp
var polygon = new Polygon();
polygon.AddRing(new[] {
    new Point(0, 0), new Point(10, 0), new Point(10, 10),
    new Point(0, 10), new Point(0, 0)
});

Point centroid = GeometryEngine.Centroid(polygon);
// centroid.X = 5, centroid.Y = 5
```

### 场景 10：线的简化与加密

```csharp
var polyline = new Polyline();
polyline.AddPath(new[] {
    new Point(0, 0), new Point(5, 0.1), new Point(10, 0),
    new Point(10, 5), new Point(10, 10)
});

// 简化：移除偏差小于 tolerance 的顶点
Geometry simplified = GeometryEngine.Simplify(polyline, 0.5);

// 加密：确保每段不超过 maxSegmentLength
Geometry densified = GeometryEngine.Densify(polyline, 2.0);

// 泛化：保持形状前提下减少顶点
Geometry generalized = GeometryEngine.Generalize(polyline, 1.0);
```

---

## 构建与测试

```bash
# 构建
dotnet build

# 运行测试（xUnit）
dotnet test

# 运行示例
dotnet run --project samples/OpenGIS.Esri.Geometry.Samples
```

---

## 注意事项

1. **Polygon 环必须闭合**：首尾点必须相同
2. **浮点容差**：内部使用 `GeometryConstants.DefaultTolerance`（1e-10）进行浮点比较，该值为内部常量，不可外部配置
3. **返回类型需转换**：集合运算返回 `Geometry` 基类，需根据实际类型做类型转换
4. **Operator 使用 Lazy 单例**：所有 Operator 类通过 `Instance` 属性获取单例实例
5. **集合 getter 返回只读视图**：`GetRing()`, `GetPath()` 等返回 `IReadOnlyList<Point>`
6. **大地测量基于 WGS84**：`GeodesicDistance` 使用 Vincenty 公式，`GeodesicArea` 使用球面超量公式
7. **GeoJSON 导出规则**：单路径 Polyline 导出为 `LineString`，多路径导出为 `MultiLineString`；Envelope 导出为 `Polygon`

# Geometry API for .NET Geometry Types Reference

Geometry type system and dual API style details split from SKILL.md.

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


---
name: jts
description: JTS Topology Suite 是 Java 平台上功能最全面的开源二维矢量几何计算库，提供几何对象建模、空间关系判断、集合运算、线性参考、空间索引及多种格式读写能力。
---

> **项目地址：** <https://github.com/locationtech/jts>
>
> **Maven Central：** `org.locationtech.jts:jts-core`
>
> **许可证：** Eclipse Public License 2.0 / Eclipse Distribution License 1.0（BSD 风格）
>
> **Javadoc：** <https://locationtech.github.io/jts/javadoc>

## 概述

JTS Topology Suite（简称 JTS）是 LocationTech 项目组下的开源 Java 二维矢量几何库，是 GeoTools、GeoServer 等众多开源 GIS 项目的几何计算核心。它提供：

- **几何对象模型**：Point、LineString、Polygon、MultiPoint、MultiLineString、MultiPolygon、GeometryCollection
- **空间关系判断**：equals、contains、within、intersects、touches、crosses、overlaps、disjoint、relate（DE-9IM）
- **集合运算**：intersection、union、difference、symDifference、buffer
- **几何分析**：convexHull、centroid、area、length、distance、isValid、simplify
- **线性参考**：沿线距离定位、线上插值
- **空间索引**：STRtree、Quadtree，加速批量空间查询
- **格式读写**：WKT、WKB、GeoJSON

**环境要求：** JDK 8+

---

## 快速集成

### Maven

```xml
<properties>
    <jts.version>1.20.0</jts.version>
</properties>

<dependency>
    <groupId>org.locationtech.jts</groupId>
    <artifactId>jts-core</artifactId>
    <version>${jts.version}</version>
</dependency>
```

如需 GeoJSON 等 I/O 支持：

```xml
<dependency>
    <groupId>org.locationtech.jts.io</groupId>
    <artifactId>jts-io-common</artifactId>
    <version>${jts.version}</version>
</dependency>
```

### Gradle

```groovy
implementation 'org.locationtech.jts:jts-core:1.20.0'
implementation 'org.locationtech.jts.io:jts-io-common:1.20.0'
```

---

## 项目模块一览

| 模块 | artifactId | 用途 |
|---|---|---|
| jts-core | `jts-core` | ★ 核心——几何模型、算法、空间操作、索引 |
| jts-io-common | `jts-io-common` | 通用 I/O：WKT、WKB、GeoJSON 读写 |
| jts-io-ora | `jts-io-ora` | Oracle Spatial SDO_GEOMETRY 读写 |
| jts-io-sde | `jts-io-sde` | ArcSDE 几何读写 |

---

## 核心类一览

| 类 | 包 | 用途 |
|---|---|---|
| `GeometryFactory` | `org.locationtech.jts.geom` | ★ **推荐入口**——创建所有几何对象的工厂 |
| `Geometry` | `org.locationtech.jts.geom` | 几何抽象基类，提供空间操作与关系判断方法 |
| `Point` | `org.locationtech.jts.geom` | 点（0 维） |
| `LineString` | `org.locationtech.jts.geom` | 线串（1 维） |
| `LinearRing` | `org.locationtech.jts.geom` | 闭合线环（用于构建 Polygon） |
| `Polygon` | `org.locationtech.jts.geom` | 面（2 维，含外环与可选内环） |
| `MultiPoint` | `org.locationtech.jts.geom` | 多点集合 |
| `MultiLineString` | `org.locationtech.jts.geom` | 多线集合 |
| `MultiPolygon` | `org.locationtech.jts.geom` | 多面集合 |
| `GeometryCollection` | `org.locationtech.jts.geom` | 任意几何集合 |
| `Coordinate` | `org.locationtech.jts.geom` | 坐标值（x, y, z） |
| `Envelope` | `org.locationtech.jts.geom` | 外接矩形（MBR） |
| `PrecisionModel` | `org.locationtech.jts.geom` | 坐标精度模型 |
| `WKTReader` | `org.locationtech.jts.io` | WKT 格式解析 |
| `WKTWriter` | `org.locationtech.jts.io` | WKT 格式输出 |
| `WKBReader` | `org.locationtech.jts.io` | WKB 格式解析 |
| `WKBWriter` | `org.locationtech.jts.io` | WKB 格式输出 |
| `GeoJsonReader` | `org.locationtech.jts.io.geojson` | GeoJSON 解析 |
| `GeoJsonWriter` | `org.locationtech.jts.io.geojson` | GeoJSON 输出 |
| `STRtree` | `org.locationtech.jts.index.strtree` | R-tree 空间索引（批量加载，查询高效） |
| `Quadtree` | `org.locationtech.jts.index.quadtree` | 四叉树空间索引（支持动态插入删除） |
| `PreparedGeometry` | `org.locationtech.jts.geom.prep` | 预处理几何，加速重复空间关系判断 |
| `PreparedGeometryFactory` | `org.locationtech.jts.geom.prep` | 创建 PreparedGeometry 的工厂 |
| `BufferOp` | `org.locationtech.jts.operation.buffer` | 缓冲区运算（可精细控制端头、连接样式） |
| `OverlayNGRobust` | `org.locationtech.jts.operation.overlayng` | 鲁棒叠加运算（推荐使用的新一代叠加引擎） |
| `TopologyPreservingSimplifier` | `org.locationtech.jts.simplify` | 保持拓扑的几何简化 |
| `DouglasPeuckerSimplifier` | `org.locationtech.jts.simplify` | Douglas-Peucker 几何简化 |
| `IsValidOp` | `org.locationtech.jts.operation.valid` | 几何有效性检测 |
| `LengthIndexedLine` | `org.locationtech.jts.linearref` | 按长度进行线性参考 |
| `LocationIndexedLine` | `org.locationtech.jts.linearref` | 按位置进行线性参考 |

---

## 几何对象创建

```java
import org.locationtech.jts.geom.*;

GeometryFactory gf = new GeometryFactory();

// 点
Point point = gf.createPoint(new Coordinate(116.4, 39.9));

// 带 Z 值的点
Point point3d = gf.createPoint(new Coordinate(116.4, 39.9, 50.0));

// 线串
LineString line = gf.createLineString(new Coordinate[]{
    new Coordinate(0, 0),
    new Coordinate(10, 10),
    new Coordinate(20, 0)
});

// 线环（必须闭合）
LinearRing ring = gf.createLinearRing(new Coordinate[]{
    new Coordinate(0, 0), new Coordinate(10, 0),
    new Coordinate(10, 10), new Coordinate(0, 10),
    new Coordinate(0, 0)  // 首尾相同
});

// 面（无洞）
Polygon polygon = gf.createPolygon(new Coordinate[]{
    new Coordinate(0, 0), new Coordinate(10, 0),
    new Coordinate(10, 10), new Coordinate(0, 10),
    new Coordinate(0, 0)
});

// 面（带洞）
LinearRing shell = gf.createLinearRing(new Coordinate[]{
    new Coordinate(0, 0), new Coordinate(20, 0),
    new Coordinate(20, 20), new Coordinate(0, 20),
    new Coordinate(0, 0)
});
LinearRing hole = gf.createLinearRing(new Coordinate[]{
    new Coordinate(5, 5), new Coordinate(15, 5),
    new Coordinate(15, 15), new Coordinate(5, 15),
    new Coordinate(5, 5)
});
Polygon polygonWithHole = gf.createPolygon(shell, new LinearRing[]{hole});

// 多点
MultiPoint multiPoint = gf.createMultiPointFromCoords(new Coordinate[]{
    new Coordinate(1, 2), new Coordinate(3, 4)
});

// 多线
MultiLineString multiLine = gf.createMultiLineString(new LineString[]{line});

// 多面
MultiPolygon multiPolygon = gf.createMultiPolygon(new Polygon[]{polygon});

// 几何集合
GeometryCollection gc = gf.createGeometryCollection(new Geometry[]{point, line, polygon});
```

---

## 空间关系判断

```java
// 八大空间谓词
boolean eq  = geomA.equals(geomB);           // 几何相等
boolean dj  = geomA.disjoint(geomB);         // 相离
boolean ix  = geomA.intersects(geomB);       // 相交
boolean tc  = geomA.touches(geomB);          // 接触
boolean cr  = geomA.crosses(geomB);          // 穿越
boolean wn  = geomA.within(geomB);           // A 在 B 内
boolean ct  = geomA.contains(geomB);         // A 包含 B
boolean ol  = geomA.overlaps(geomB);         // 重叠

// DE-9IM 关系矩阵
boolean rel = geomA.relate(geomB, "T*F**FFF*");
String matrix = geomA.relate(geomB).toString();  // 返回 "212101212" 等

// 距离判断
boolean near = geomA.isWithinDistance(geomB, 100.0);
```

---

## 集合运算

```java
// 交集
Geometry intersection = geomA.intersection(geomB);

// 合并
Geometry union = geomA.union(geomB);

// 差集
Geometry difference = geomA.difference(geomB);

// 对称差
Geometry symDiff = geomA.symDifference(geomB);

// 缓冲区
Geometry buffer = geometry.buffer(10.0);               // 默认圆弧端头
Geometry bufferFlat = geometry.buffer(10.0, 8, BufferOp.CAP_FLAT);  // 平头端

// 多几何合并（高性能）
import org.locationtech.jts.operation.union.UnaryUnionOp;
Geometry merged = UnaryUnionOp.union(geometryCollection);

// 鲁棒叠加运算（推荐）
import org.locationtech.jts.operation.overlayng.OverlayNGRobust;
Geometry robustIntersection = OverlayNGRobust.overlay(geomA, geomB, OverlayNG.INTERSECTION);
Geometry robustUnion = OverlayNGRobust.overlay(geomA, geomB, OverlayNG.UNION);
```

---

## 几何分析

```java
// 面积与长度
double area = polygon.getArea();
double length = line.getLength();

// 距离
double dist = geomA.distance(geomB);

// 质心
Point centroid = geometry.getCentroid();

// 内部点（保证在几何内部）
Point interiorPoint = geometry.getInteriorPoint();

// 凸包
Geometry hull = geometry.convexHull();

// 外接矩形
Envelope env = geometry.getEnvelopeInternal();

// 有效性检测
boolean valid = geometry.isValid();

// 详细有效性诊断
import org.locationtech.jts.operation.valid.IsValidOp;
IsValidOp validator = new IsValidOp(geometry);
if (!validator.isValid()) {
    System.out.println(validator.getValidationError());
}

// 几何修复
import org.locationtech.jts.geom.util.GeometryFixer;
Geometry fixed = GeometryFixer.fix(geometry);
```

---

## 几何简化

```java
import org.locationtech.jts.simplify.TopologyPreservingSimplifier;
import org.locationtech.jts.simplify.DouglasPeuckerSimplifier;

// 保持拓扑的简化（推荐）
Geometry simplified = TopologyPreservingSimplifier.simplify(geometry, 0.001);

// Douglas-Peucker 简化（更快，但可能产生自相交）
Geometry dpSimplified = DouglasPeuckerSimplifier.simplify(geometry, 0.001);
```

---

## 精度模型

```java
// 浮点精度（默认）
PrecisionModel pmFloat = new PrecisionModel();

// 固定精度（如保留 6 位小数 → scale = 1000000）
PrecisionModel pmFixed = new PrecisionModel(1000000);

// 使用精度模型创建工厂
GeometryFactory gf = new GeometryFactory(pmFixed);

// 带 SRID 的工厂
GeometryFactory gfSrid = new GeometryFactory(pmFloat, 4326);
```

---

## 格式读写

### WKT（Well-Known Text）

```java
import org.locationtech.jts.io.WKTReader;
import org.locationtech.jts.io.WKTWriter;

WKTReader reader = new WKTReader();

// 读取
Geometry point = reader.read("POINT (116.4 39.9)");
Geometry line  = reader.read("LINESTRING (0 0, 10 10, 20 0)");
Geometry poly  = reader.read("POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))");

// 写入
WKTWriter writer = new WKTWriter();
String wkt = writer.write(point);   // "POINT (116.4 39.9)"

// 3D WKT
WKTWriter writer3d = new WKTWriter(3);
String wkt3d = writer3d.write(gf.createPoint(new Coordinate(1, 2, 3)));
```

### WKB（Well-Known Binary）

```java
import org.locationtech.jts.io.WKBReader;
import org.locationtech.jts.io.WKBWriter;

// 写入
WKBWriter wkbWriter = new WKBWriter();
byte[] wkb = wkbWriter.write(geometry);

// 读取
WKBReader wkbReader = new WKBReader();
Geometry geom = wkbReader.read(wkb);

// 输出 Hex 字符串（常用于数据库交互）
String hex = WKBWriter.toHex(wkb);
byte[] fromHex = WKBReader.hexToBytes(hex);
```

### GeoJSON

```java
import org.locationtech.jts.io.geojson.GeoJsonReader;
import org.locationtech.jts.io.geojson.GeoJsonWriter;

// 读取
GeoJsonReader gjReader = new GeoJsonReader();
Geometry geom = gjReader.read("{\"type\":\"Point\",\"coordinates\":[116.4,39.9]}");

// 写入
GeoJsonWriter gjWriter = new GeoJsonWriter();
String json = gjWriter.write(geom);
```

---

## 空间索引

### STRtree（R-tree，推荐用于批量查询）

```java
import org.locationtech.jts.index.strtree.STRtree;

STRtree index = new STRtree();

// 批量插入（插入后首次查询时自动构建索引）
for (Geometry geom : geometries) {
    index.insert(geom.getEnvelopeInternal(), geom);
}

// 矩形范围查询
Envelope searchEnv = new Envelope(10, 20, 10, 20);
List<?> candidates = index.query(searchEnv);

// 最近邻查询
import org.locationtech.jts.index.strtree.ItemDistance;
Object nearest = index.nearestNeighbour(
    point.getEnvelopeInternal(), point,
    (ItemDistance) (itemBoundable1, itemBoundable2) -> {
        Geometry g1 = (Geometry) itemBoundable1.getItem();
        Geometry g2 = (Geometry) itemBoundable2.getItem();
        return g1.distance(g2);
    }
);
```

### Quadtree（四叉树，支持动态增删）

```java
import org.locationtech.jts.index.quadtree.Quadtree;

Quadtree qtree = new Quadtree();
qtree.insert(geom.getEnvelopeInternal(), geom);
List<?> results = qtree.query(searchEnv);
qtree.remove(geom.getEnvelopeInternal(), geom);
```

---

## PreparedGeometry（加速重复判断）

当需要对同一个几何反复进行空间关系判断时（如判断大量点是否在某面内），使用 `PreparedGeometry` 可显著提升性能：

```java
import org.locationtech.jts.geom.prep.PreparedGeometry;
import org.locationtech.jts.geom.prep.PreparedGeometryFactory;

PreparedGeometry prepared = PreparedGeometryFactory.prepare(polygon);

for (Point pt : points) {
    if (prepared.contains(pt)) {
        // 命中
    }
}
```

---

## 线性参考

```java
import org.locationtech.jts.linearref.LengthIndexedLine;
import org.locationtech.jts.linearref.LocationIndexedLine;

LengthIndexedLine lil = new LengthIndexedLine(line);

// 按长度获取坐标
Coordinate midPoint = lil.extractPoint(line.getLength() / 2);

// 截取子线
Geometry subLine = lil.extractLine(10.0, 50.0);

// 计算某点在线上的投影位置（距起点长度）
double index = lil.indexOf(new Coordinate(5, 5));

// 按位置引用
LocationIndexedLine locLine = new LocationIndexedLine(line);
```

---

## 仿射变换

```java
import org.locationtech.jts.geom.util.AffineTransformation;

// 平移
AffineTransformation translate = AffineTransformation.translationInstance(10, 20);
Geometry moved = translate.transform(geometry);

// 旋转（弧度，绕原点）
AffineTransformation rotate = AffineTransformation.rotationInstance(Math.PI / 4);
Geometry rotated = rotate.transform(geometry);

// 缩放
AffineTransformation scale = AffineTransformation.scaleInstance(2.0, 2.0);
Geometry scaled = scale.transform(geometry);

// 组合变换
AffineTransformation combo = new AffineTransformation();
combo.translate(10, 0);
combo.rotate(Math.PI / 6);
Geometry result = combo.transform(geometry);
```

---

## 典型应用场景

| 场景 | 关键类 / 方法 |
|---|---|
| 创建几何对象 | `GeometryFactory.createPoint()` / `createLineString()` / `createPolygon()` |
| 地理围栏 / 点在面内判断 | `Geometry.contains()` / `within()`，高频场景用 `PreparedGeometry` |
| 计算两个几何的距离 | `Geometry.distance()` |
| 缓冲区分析 | `Geometry.buffer()` 或 `BufferOp` |
| 面叠加分析（交并差） | `Geometry.intersection()` / `union()` / `difference()` |
| 鲁棒叠加运算 | `OverlayNGRobust.overlay()` |
| 几何格式互转 | `WKTReader` / `WKTWriter` / `WKBReader` / `WKBWriter` / `GeoJsonReader` / `GeoJsonWriter` |
| 批量空间查询加速 | `STRtree` / `Quadtree` |
| 最近邻搜索 | `STRtree.nearestNeighbour()` |
| 几何简化（抽稀） | `TopologyPreservingSimplifier` / `DouglasPeuckerSimplifier` |
| 几何有效性校验与修复 | `IsValidOp` / `GeometryFixer` |
| 线性参考 / 沿线定位 | `LengthIndexedLine` / `LocationIndexedLine` |
| 凸包计算 | `Geometry.convexHull()` |
| 几何仿射变换 | `AffineTransformation` |
| 数据库 WKB 交互 | `WKBReader.hexToBytes()` / `WKBWriter.toHex()` |

---

## 常见注意事项

1. **使用 GeometryFactory 创建几何**：不要直接 `new Point()`，始终通过 `GeometryFactory` 的工厂方法创建几何对象。
2. **面必须闭合**：Polygon 的外环和内环坐标数组的首尾坐标必须相同。
3. **坐标顺序**：JTS 使用 `(x, y)` 即 `(经度, 纬度)` 的顺序，注意与某些 GIS 系统的 `(纬度, 经度)` 区分。
4. **几何有效性**：从外部导入的几何数据应使用 `geometry.isValid()` 检查有效性，无效几何可用 `GeometryFixer.fix()` 修复。
5. **SRID 不参与计算**：JTS 的 SRID 仅作为元数据标记，不影响空间运算；JTS 所有计算都在笛卡尔平面上进行，不处理投影。
6. **性能优化**：批量空间查询使用 `STRtree`；重复空间关系判断使用 `PreparedGeometry`；大量几何合并使用 `UnaryUnionOp`。
7. **线程安全**：`GeometryFactory` 是线程安全的；`Geometry` 对象本身不可变，可安全共享；但 Reader/Writer 实例非线程安全，需为每个线程创建独立实例。
8. **包名迁移**：JTS 1.15+ 包名由 `com.vividsolutions.jts` 迁移为 `org.locationtech.jts`，注意旧代码升级。
9. **OverlayNG**：对于叠加运算（intersection / union / difference），推荐使用 `OverlayNGRobust`，它比传统叠加引擎更加鲁棒，能处理更多边界情况。

---

## 参考链接

- **GitHub 仓库：** <https://github.com/locationtech/jts>
- **Javadoc：** <https://locationtech.github.io/jts/javadoc>
- **用户指南：** <https://github.com/locationtech/jts/blob/master/USING.md>
- **FAQ：** <https://locationtech.github.io/jts/jts-faq.html>
- **Maven Central：** <https://mvnrepository.com/artifact/org.locationtech.jts>
- **LocationTech 主页：** <https://locationtech.org/projects/technology.jts>
- **版本历史：** <https://github.com/locationtech/jts/blob/master/doc/JTS_Version_History.md>
- **衍生项目 — GEOS（C++ 移植）：** <https://trac.osgeo.org/geos>
- **衍生项目 — NetTopologySuite（.NET 移植）：** <https://github.com/NetTopologySuite/NetTopologySuite>
- **衍生项目 — JSTS（JavaScript 移植）：** <https://github.com/bjornharrtell/jsts>

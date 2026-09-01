# JTS Geometry Operations and Index Reference

Spatial relations, set operations, geometry analysis, format I/O and spatial indexing split from SKILL.md.

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


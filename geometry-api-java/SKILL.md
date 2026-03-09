# SKILL.md — Esri Geometry API for Java

> **项目地址：** <https://github.com/Esri/geometry-api-java>
>
> **Maven Central：** `com.esri.geometry:esri-geometry-api`
>
> **许可证：** Apache License 2.0

## 概述

Esri Geometry API for Java 是一个自包含的空间几何计算库，提供对二维和三维几何对象的创建、解析、序列化以及空间关系运算能力。它无需任何外部 GIS 依赖，可直接嵌入 Java 应用、Hadoop MapReduce、Hive UDF、Spark 等大数据处理框架中。

---

## 快速集成

### Maven

```xml
<dependency>
  <groupId>com.esri.geometry</groupId>
  <artifactId>esri-geometry-api</artifactId>
  <version>2.2.4</version>
</dependency>
```

### Gradle

```groovy
implementation 'com.esri.geometry:esri-geometry-api:2.2.4'
```

**环境要求：** JDK 1.7+；运行时依赖 `jackson-core`（JSON 处理）。

---

## 核心类一览

| 类 | 包 | 用途 |
|---|---|---|
| `GeometryEngine` | `com.esri.core.geometry` | **推荐入口**——提供几何操作的静态便捷方法 |
| `OperatorFactoryLocal` | `com.esri.core.geometry` | 算子工厂，适用于高性能批量处理 |
| `SpatialReference` | `com.esri.core.geometry` | 空间参考 / 坐标系（通过 WKID 或 WKT 创建） |
| `MapGeometry` | `com.esri.core.geometry` | 将 Geometry 与 SpatialReference 打包在一起 |
| `Point` | `com.esri.core.geometry` | 点（0 维） |
| `MultiPoint` | `com.esri.core.geometry` | 多点集合（0 维） |
| `Polyline` | `com.esri.core.geometry` | 折线 / 路径集合（1 维） |
| `Polygon` | `com.esri.core.geometry` | 面 / 环集合（2 维） |
| `Envelope` | `com.esri.core.geometry` | 外接矩形（2 维） |

---

## 几何对象创建

```java
import com.esri.core.geometry.*;

// 点
Point pt = new Point(116.4, 39.9);          // 2D
Point pt3d = new Point(116.4, 39.9, 50.0);  // 3D

// 折线
Polyline line = new Polyline();
line.startPath(0, 0);
line.lineTo(10, 10);
line.lineTo(20, 0);

// 面
Polygon polygon = new Polygon();
polygon.startPath(0, 0);
polygon.lineTo(10, 0);
polygon.lineTo(10, 10);
polygon.lineTo(0, 10);
// 自动闭合

// 外接矩形
Envelope env = new Envelope(0, 0, 10, 10);

// 多点
MultiPoint mp = new MultiPoint();
mp.add(1, 2);
mp.add(3, 4);
```

---

## 空间参考

```java
// 按 WKID 创建（WGS 84 = 4326）
SpatialReference srWGS84 = SpatialReference.create(4326);

// 按 WKT 字符串创建
SpatialReference srCustom = SpatialReference.create("GEOGCS[\"GCS_WGS_1984\",...]]");

// 与几何对象绑定
MapGeometry mapGeom = new MapGeometry(pt, srWGS84);
```

---

## 空间操作（通过 GeometryEngine）

### 集合运算

```java
SpatialReference sr = SpatialReference.create(4326);

// 缓冲区
Geometry buffered = GeometryEngine.buffer(point, sr, 100.0);

// 交集
Geometry inter = GeometryEngine.intersect(polygon1, polygon2, sr);

// 合并
Geometry united = GeometryEngine.union(new Geometry[]{poly1, poly2, poly3}, sr);

// 差集
Geometry diff = GeometryEngine.difference(polygon1, polygon2, sr);

// 对称差
Geometry symDiff = GeometryEngine.symmetricDifference(geom1, geom2, sr);

// 裁剪（按矩形）
Geometry clipped = GeometryEngine.clip(geometry, envelope, sr);

// 切割（用折线切割面或线）
Geometry[] parts = GeometryEngine.cut(polygon, cuttingLine, sr);
```

### 距离与邻近

```java
double dist = GeometryEngine.distance(geom1, geom2, sr);
```

### 空间关系判断

```java
boolean eq   = GeometryEngine.equals(g1, g2, sr);
boolean wn   = GeometryEngine.within(point, polygon, sr);
boolean ct   = GeometryEngine.contains(polygon, point, sr);
boolean ix   = GeometryEngine.intersects(g1, g2, sr);
boolean dj   = GeometryEngine.disjoint(g1, g2, sr);
boolean tc   = GeometryEngine.touches(g1, g2, sr);
boolean cr   = GeometryEngine.crosses(line, polygon, sr);
boolean ol   = GeometryEngine.overlaps(poly1, poly2, sr);

// DE-9IM 关系矩阵
boolean rel  = GeometryEngine.relate(g1, g2, sr, "T*F**FFF*");
```

### 几何分析

```java
// 凸包
Geometry hull = GeometryEngine.convexHull(geometry);

// 简化
Geometry simplified = GeometryEngine.simplify(geometry, sr);

// 泛化（简化顶点）
Geometry generalized = GeometryEngine.generalize(geometry, maxDeviation, true, sr);

// 质心 / 标注点
Point centroid = GeometryEngine.getLabelPoint(polygon, sr);
```

### 大地测量（椭球面计算）

```java
// 大地测量缓冲区（结果更精确，适用于地理坐标系）
Geometry geoBuffer = GeometryEngine.geodesicBuffer(geometry, sr, 1000.0);

// 大地测量长度
double geoLen = GeometryEngine.geodesicLength(polyline, sr, null);

// 大地测量面积
double geoArea = GeometryEngine.geodesicArea(polygon, sr, null);
```

---

## 格式转换

### JSON（Esri JSON）

```java
// 导入
MapGeometry mg = GeometryEngine.jsonToGeometry(jsonString);
Geometry geom = mg.getGeometry();
SpatialReference sr = mg.getSpatialReference();

// 导出（附带 WKID）
String json = GeometryEngine.geometryToJson(4326, geometry);
```

### GeoJSON

```java
// 导入
MapGeometry mg = GeometryEngine.geoJsonToGeometry(geoJsonString, 0, Geometry.Type.Unknown);

// 导出
String geoJson = GeometryEngine.geometryToGeoJson(geometry);
```

### WKT（Well-Known Text）

```java
// 导入
Geometry geom = GeometryEngine.geometryFromWkt(
    "POLYGON((0 0,10 0,10 10,0 10,0 0))",
    0,
    Geometry.Type.Polygon
);

// 导出
String wkt = GeometryEngine.geometryToWkt(geometry, 0);
```

### WKB（Well-Known Binary）

```java
// 导入
Geometry geom = GeometryEngine.geometryFromWkb(byteBuffer, Geometry.Type.Unknown);

// 导出
ByteBuffer wkb = GeometryEngine.geometryToWkb(geometry, 0);
```

### Esri Shape

```java
// 导入
Geometry geom = GeometryEngine.geometryFromEsriShape(byteBuffer, Geometry.Type.Polygon);

// 导出
byte[] shape = GeometryEngine.geometryToEsriShape(geometry);
```

---

## 高级用法：Operator 直接调用

当需要批量处理大量几何对象时，使用 `OperatorFactoryLocal` 获取算子并配合 `GeometryCursor` 可获得更好的性能：

```java
OperatorFactoryLocal factory = OperatorFactoryLocal.getInstance();
OperatorBuffer bufferOp = (OperatorBuffer) factory.getOperator(Operator.Type.Buffer);

// 使用 SimpleGeometryCursor 包装输入
SimpleGeometryCursor inputCursor = new SimpleGeometryCursor(geometryArray);
double[] distances = {100.0};
GeometryCursor resultCursor = bufferOp.execute(inputCursor, sr, distances, false, null);

// 逐个取出结果
Geometry result;
while ((result = resultCursor.next()) != null) {
    // 处理每个缓冲区结果
}
```

---

## 几何类型判断

```java
Geometry.Type type = geometry.getType();

switch (type) {
    case Point:      Point p = (Point) geometry; break;
    case Polygon:    Polygon pg = (Polygon) geometry; break;
    case Polyline:   Polyline pl = (Polyline) geometry; break;
    case MultiPoint: MultiPoint mp = (MultiPoint) geometry; break;
    case Envelope:   Envelope ev = (Envelope) geometry; break;
}

// 按维度判断
boolean isPoint  = Geometry.isPoint(type.value());
boolean isLinear = Geometry.isLinear(type.value());
boolean isArea   = Geometry.isArea(type.value());
```

---

## 顶点属性（Z / M / ID）

```java
// 检查属性
geometry.hasZ();
geometry.hasM();
geometry.hasID();

// 添加属性
geometry.addAttribute(VertexDescription.Semantics.Z);
geometry.addAttribute(VertexDescription.Semantics.M);
```

---

## 典型应用场景

| 场景 | 关键方法 |
|---|---|
| 地理围栏 / 点在面内判断 | `GeometryEngine.contains()` 或 `within()` |
| 计算两点距离 | `GeometryEngine.distance()` 或 `geodesicLength()` |
| 创建缓冲区（如 POI 周边范围） | `GeometryEngine.buffer()` 或 `geodesicBuffer()` |
| 面求交 / 叠加分析 | `GeometryEngine.intersect()` / `union()` / `difference()` |
| 坐标格式互转 | `jsonToGeometry()` / `geometryToGeoJson()` / `geometryFromWkt()` 等 |
| 几何有效性检查与修复 | `GeometryEngine.simplify()` |
| Hadoop / Spark 空间处理 | 搭配 Operator + GeometryCursor 批量处理 |

---

## 常见注意事项

1. **坐标系一致**：进行空间运算前，确保所有几何对象使用相同的 `SpatialReference`。
2. **简化几何**：导入外部数据后，使用 `GeometryEngine.simplify()` 确保拓扑正确。
3. **大地测量 vs 平面**：对地理坐标（经纬度）执行面积/长度计算时，优先使用 `geodesicArea()` / `geodesicLength()` 以获得椭球面精确结果。
4. **性能优化**：批量操作建议使用 `OperatorFactoryLocal` + `GeometryCursor`，而非逐个调用 `GeometryEngine` 静态方法。
5. **线程安全**：`GeometryEngine` 的静态方法是线程安全的。

---

## 参考链接

- **GitHub 仓库：** <https://github.com/Esri/geometry-api-java>
- **官方 Wiki：** <https://github.com/Esri/geometry-api-java/wiki>
- **Javadoc：** <http://Esri.github.io/geometry-api-java/javadoc/>
- **Maven Central：** <https://repo1.maven.org/maven2/com/esri/geometry/>
- **相关项目 — Spatial Framework for Hadoop：** <https://github.com/Esri/spatial-framework-for-hadoop>

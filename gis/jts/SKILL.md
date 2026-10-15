---
name: jts
description: "Use when performing precise 2D computational geometry in Java — spatial predicates (contains, intersects), overlay operations, buffering, triangulation. JTS (Java Topology Suite): the canonical geometry engine used as blueprint for GEOS, Shapely, and NetTopologySuite."

tags:
  - java
  - geometry
  - topology
  - spatial
  - de9im
  - wkt
  - wkb
  - geojson
  - gis
---

> **项目地址：** <https://github.com/locationtech/jts>
>
> **Maven Central：** `org.locationtech.jts:jts-core`
>
> **最新版本：** 1.20.0（截至 2026-10，[Maven Central](https://central.sonatype.com/artifact/org.locationtech.jts/jts-core)）
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

## 环境准备与快速集成

### Maven

```xml
<properties>
    <jts.version>1.20.0</jts.version><!-- Maven Central 最新稳定版；列表见 https://central.sonatype.com/artifact/org.locationtech.jts/jts-core -->
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
| jts-core | `jts-core` | （推荐）核心——几何模型、算法、空间操作、索引 |
| jts-io-common | `jts-io-common` | 通用 I/O：WKT、WKB、GeoJSON 读写 |
| jts-io-ora | `jts-io-ora` | Oracle Spatial SDO_GEOMETRY 读写——源码模块，需 `-Pall`（oracle profile）本地构建，未发布到 Maven Central |
| jts-io-sde | `jts-io-sde` | ArcSDE 几何读写——源码保留，构建中已注释禁用，无发布产物 |

---

## 核心类一览

| 类 | 包 | 用途 |
|---|---|---|
| `GeometryFactory` | `org.locationtech.jts.geom` | **推荐入口**——创建所有几何对象的工厂 |
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

> 空间关系、集合运算、几何分析、格式读写与空间索引的完整参考见 [reference/geometry-operations.md](reference/geometry-operations.md)

## 典型工作流：WKT → 缓冲区 → 空间判断 → GeoJSON

```java
import org.locationtech.jts.geom.*;
import org.locationtech.jts.geom.prep.PreparedGeometry;
import org.locationtech.jts.geom.prep.PreparedGeometryFactory;
import org.locationtech.jts.io.WKTReader;
import org.locationtech.jts.io.geojson.GeoJsonWriter;

// 1. 从 WKT 解析输入几何
Geometry polygon = new WKTReader().read("POLYGON((0 0,10 0,10 10,0 10,0 0))");

// 2. 缓冲区分析并校验有效性
Geometry buffered = polygon.buffer(2.0);
boolean valid = buffered.isValid();

// 3. 点在面内判断（批量场景先做 PreparedGeometry 预处理）
PreparedGeometry prep = PreparedGeometryFactory.prepare(polygon);
boolean hit = prep.contains(new GeometryFactory().createPoint(new Coordinate(5, 5)));

// 4. 导出 GeoJSON
String geoJson = new GeoJsonWriter().write(buffered);
```

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

## 常见问题

| 问题 | 解决 |
|------|------|
| 无法直接 `new Point(...)` / 构造几何 | 始终通过 `GeometryFactory` 的工厂方法创建几何对象 |
| 面数据无效（环未闭合） | Polygon 外环与内环坐标数组首尾必须相同 |
| 经纬度顺序写反 | JTS 使用 `(x, y)` 即 `(经度, 纬度)`，注意与 `(纬度, 经度)` 的系统区分 |
| 外部几何 `isValid()` 为 false | 用 `GeometryFixer.fix()` 修复后再参与运算 |
| 跨坐标系计算结果失真 | JTS 的 SRID 仅是元数据，所有计算在笛卡尔平面进行，不处理投影 |
| 批量空间查询慢 | 用 `STRtree` 建索引；重复关系判断用 `PreparedGeometry`；大量合并用 `UnaryUnionOp` |
| 多线程复用 Reader/Writer 出错 | `GeometryFactory` 与 `Geometry` 线程安全；`WKTReader` / `WKTWriter` 等非线程安全，每线程独立创建 |
| 叠加运算抛 TopologyException | 优先用 `OverlayNGRobust.overlay()`，比传统叠加引擎更鲁棒 |
| 旧代码升级后 import 报错 | JTS 1.15+ 包名由 `com.vividsolutions.jts` 迁移为 `org.locationtech.jts` |

---

## AI 使用建议

### 推荐工作流

1. **创建几何对象**：始终通过 `GeometryFactory` 工厂方法创建，不要直接 `new`
2. **格式解析**：从 WKT/WKB/GeoJSON 读入外部数据，使用对应的 Reader
3. **空间运算**：用 `PreparedGeometry` 加速批量 contains/intersects 判断
4. **批量查询**：用 `STRtree` 建空间索引后查询
5. **结果导出**：用 Writer 输出为 WKT/WKB/GeoJSON

### 关键注意事项

- **坐标顺序**：JTS 使用 `(x, y)` 即 `(经度, 纬度)`，注意与部分 GIS 系统的 `(y, x)` 区分
- **SRID 不参与计算**：JTS 所有计算在笛卡尔平面进行，不处理地球曲率
- **OverlayNG 优先**：叠加运算优先使用 `OverlayNGRobust.overlay()`，比传统方法更鲁棒
- **线程安全**：`GeometryFactory` 和 `Geometry` 线程安全；Reader/Writer 非线程安全
- **有效性检查**：外部导入的几何用 `isValid()` 检查后用 `GeometryFixer.fix()` 修复

## 相关技能

- **nettopologysuite** — JTS 的 .NET 移植：[../nettopologysuite/SKILL.md](../nettopologysuite/SKILL.md)
- **shapely** — Python 几何运算库（GEOS 绑定）：[../shapely/SKILL.md](../shapely/SKILL.md)
- **geotools** — Java GIS 工具集（基于 JTS）：[../geotools/SKILL.md](../geotools/SKILL.md)
- **geometry-api-java** — Esri Geometry API for Java：[../geometry-api-java/SKILL.md](../geometry-api-java/SKILL.md)
- **geoserver** — 基于 JTS 的地图服务器：[../geoserver/SKILL.md](../geoserver/SKILL.md)

## 参考资源

- **GitHub 仓库：** <https://github.com/locationtech/jts>
- **Javadoc：** <https://locationtech.github.io/jts/javadoc>
- **用户指南：** <https://github.com/locationtech/jts/blob/master/USING.md>
- **FAQ：** <https://locationtech.github.io/jts/jts-faq.html>
- **Maven Central：** <https://mvnrepository.com/artifact/org.locationtech.jts>
- **LocationTech 主页：** <https://locationtech.org/projects/technology.jts>
- **版本历史：** <https://github.com/locationtech/jts/blob/master/doc/JTS_Version_History.md>
- **衍生项目 — GEOS（C++ 移植）：** <https://libgeos.org/>
- **衍生项目 — NetTopologySuite（.NET 移植）：** <https://github.com/NetTopologySuite/NetTopologySuite>
- **衍生项目 — JSTS（JavaScript 移植）：** <https://github.com/bjornharrtell/jsts>

---
name: geotools
description: GeoTools 是一个开源的 Java GIS 工具库，提供符合 OGC 标准的矢量/栅格数据访问、坐标参考系统转换、空间查询过滤、地图渲染及 OGC Web 服务客户端等全栈地理空间开发能力。
---

> **项目地址：** <https://github.com/geotools/geotools>
>
> **Maven GroupId：** `org.geotools`
>
> **许可证：** LGPL 2.1
>
> **文档链接：** <https://docs.geotools.org/>

## 概述

GeoTools 是一个成熟、模块化的开源 Java GIS 工具库，由 OSGeo 基金会管理，广泛应用于 GeoServer、uDig 等知名 GIS 平台。它提供：

- **矢量数据访问**：Shapefile、GeoPackage、GeoJSON、PostGIS、Oracle Spatial、SQL Server 等
- **栅格数据访问**：GeoTIFF、NetCDF、ImageMosaic 等
- **坐标参考系统 (CRS)**：基于 EPSG 数据库的投影定义与坐标转换
- **空间查询与过滤**：CQL / ECQL、OGC Filter 编码
- **地图渲染**：基于 SLD/SE 的制图样式与图片输出
- **OGC Web 服务**：WMS / WFS / WCS 客户端
- **几何运算**：基于 JTS Topology Suite 的全套几何计算

**环境要求：** JDK 11+（GeoTools 21–30）；JDK 17+（GeoTools 31+）

---

## 快速集成

### Maven 仓库配置

GeoTools 发布在 OSGeo Maven 仓库，需在 `pom.xml` 中添加：

```xml
<repositories>
    <repository>
        <id>osgeo</id>
        <name>OSGeo Release Repository</name>
        <url>https://repo.osgeo.org/repository/release/</url>
    </repository>
</repositories>
```

### 常用模块依赖

```xml
<properties>
    <geotools.version>34.3</geotools.version>
</properties>

<dependencies>
    <!-- 核心 -->
    <dependency>
        <groupId>org.geotools</groupId>
        <artifactId>gt-main</artifactId>
        <version>${geotools.version}</version>
    </dependency>
    <!-- Shapefile -->
    <dependency>
        <groupId>org.geotools</groupId>
        <artifactId>gt-shapefile</artifactId>
        <version>${geotools.version}</version>
    </dependency>
    <!-- GeoTIFF 栅格 -->
    <dependency>
        <groupId>org.geotools</groupId>
        <artifactId>gt-geotiff</artifactId>
        <version>${geotools.version}</version>
    </dependency>
    <!-- GeoPackage -->
    <dependency>
        <groupId>org.geotools</groupId>
        <artifactId>gt-geopkg</artifactId>
        <version>${geotools.version}</version>
    </dependency>
    <!-- EPSG 坐标系数据库（HSQL 嵌入式） -->
    <dependency>
        <groupId>org.geotools</groupId>
        <artifactId>gt-epsg-hsql</artifactId>
        <version>${geotools.version}</version>
    </dependency>
    <!-- PostGIS -->
    <dependency>
        <groupId>org.geotools.jdbc</groupId>
        <artifactId>gt-jdbc-postgis</artifactId>
        <version>${geotools.version}</version>
    </dependency>
    <!-- CQL 查询语言 -->
    <dependency>
        <groupId>org.geotools</groupId>
        <artifactId>gt-cql</artifactId>
        <version>${geotools.version}</version>
    </dependency>
    <!-- 地图渲染 -->
    <dependency>
        <groupId>org.geotools</groupId>
        <artifactId>gt-render</artifactId>
        <version>${geotools.version}</version>
    </dependency>
    <!-- GeoJSON 数据格式 -->
    <dependency>
        <groupId>org.geotools</groupId>
        <artifactId>gt-geojson-core</artifactId>
        <version>${geotools.version}</version>
    </dependency>
</dependencies>
```

---

## 核心模块一览

| 模块 | artifactId | 用途 |
|---|---|---|
| gt-main | `gt-main` | ★ 核心接口与实现——Feature / DataStore / Filter |
| gt-api | `gt-api` | 高层 API 接口定义（Feature、CRS、Filter 等） |
| gt-referencing | `gt-referencing` | 坐标参考系统定义与转换 |
| gt-epsg-hsql | `gt-epsg-hsql` | 嵌入式 EPSG 数据库（基于 HSQL） |
| gt-shapefile | `gt-shapefile` | Shapefile 矢量读写 |
| gt-geopkg | `gt-geopkg` | GeoPackage 矢量 / 栅格读写 |
| gt-geotiff | `gt-geotiff` | GeoTIFF 栅格读写 |
| gt-coverage | `gt-coverage` | 栅格覆盖（GridCoverage）处理 |
| gt-cql | `gt-cql` | CQL / ECQL 查询语言解析 |
| gt-render | `gt-render` | 地图渲染输出（PNG、SVG 等） |
| gt-jdbc-postgis | `gt-jdbc-postgis` | PostGIS 数据库连接 |
| gt-geojson-core | `gt-geojson-core` | GeoJSON 读写 |
| gt-wms | `gt-wms` | OGC WMS 客户端 |
| gt-wfs-ng | `gt-wfs-ng` | OGC WFS 客户端 |
| gt-process | `gt-process` | 地理处理框架 |

---

## 核心类一览

| 类 / 接口 | 包 | 用途 |
|---|---|---|
| `DataStore` | `org.geotools.data` | ★ 矢量数据源的统一抽象入口 |
| `DataStoreFinder` | `org.geotools.data` | 通过参数自动定位并创建 DataStore |
| `FileDataStoreFinder` | `org.geotools.data` | 快速打开单文件数据源（Shapefile 等） |
| `SimpleFeatureType` | `org.opengis.feature.simple` | 要素类型定义（字段名、类型、CRS） |
| `SimpleFeature` | `org.opengis.feature.simple` | 单个矢量要素（属性 + 几何） |
| `SimpleFeatureSource` | `org.geotools.data.simple` | 只读要素数据源 |
| `SimpleFeatureStore` | `org.geotools.data.simple` | 可读写要素数据源 |
| `SimpleFeatureCollection` | `org.geotools.data.simple` | 要素集合 |
| `SimpleFeatureBuilder` | `org.geotools.feature.simple` | 构建 SimpleFeature 实例 |
| `SimpleFeatureTypeBuilder` | `org.geotools.feature.simple` | 构建 SimpleFeatureType 定义 |
| `Geometry` | `org.locationtech.jts.geom` | JTS 几何基类（Point、LineString、Polygon 等） |
| `GeometryFactory` | `org.locationtech.jts.geom` | 创建几何对象的工厂 |
| `JTSFactoryFinder` | `org.geotools.geometry.jts` | GeoTools 推荐的 GeometryFactory 获取方式 |
| `JTS` | `org.geotools.geometry.jts` | JTS 几何工具类（坐标转换、Envelope 转换等） |
| `CRS` | `org.geotools.referencing.CRS` | ★ 坐标参考系统工具类（解码 EPSG、查找转换） |
| `CoordinateReferenceSystem` | `org.opengis.referencing.crs` | CRS 接口 |
| `MathTransform` | `org.opengis.referencing.operation` | 坐标转换数学变换 |
| `Filter` | `org.opengis.filter` | OGC 过滤器接口 |
| `CQL` | `org.geotools.filter.text.cql2` | CQL 查询语言解析器 |
| `ECQL` | `org.geotools.filter.text.ecql` | 扩展 CQL 解析器（支持更多语法） |
| `Style` | `org.geotools.styling` | SLD 制图样式 |
| `SLD` | `org.geotools.styling.SLD` | 快速创建简单样式的工具类 |
| `MapContent` | `org.geotools.map` | 地图容器（管理图层集合） |
| `FeatureLayer` | `org.geotools.map` | 矢量图层 |
| `GridCoverage2D` | `org.geotools.coverage.grid` | 二维栅格覆盖数据 |
| `GeoTiffReader` | `org.geotools.gce.geotiff` | GeoTIFF 读取器 |
| `GeoTiffWriter` | `org.geotools.gce.geotiff` | GeoTIFF 写入器 |
| `ReferencedEnvelope` | `org.geotools.geometry.jts` | 带 CRS 的矩形范围 |
| `DataUtilities` | `org.geotools.data` | 数据工具类（类型创建、集合转换等） |

---

## 矢量数据读取

### 读取 Shapefile

```java
import org.geotools.data.*;
import org.geotools.data.simple.*;
import org.opengis.feature.simple.SimpleFeature;

File file = new File("data/cities.shp");
FileDataStore store = FileDataStoreFinder.getDataStore(file);
SimpleFeatureSource source = store.getFeatureSource();
SimpleFeatureCollection features = source.getFeatures();

try (SimpleFeatureIterator iter = features.features()) {
    while (iter.hasNext()) {
        SimpleFeature f = iter.next();
        System.out.println(f.getID() + " " + f.getAttribute("NAME"));
    }
}
store.dispose();
```

### 读取 GeoPackage

```java
Map<String, Object> params = new HashMap<>();
params.put("dbtype", "geopkg");
params.put("database", new File("data/world.gpkg").getAbsolutePath());

DataStore store = DataStoreFinder.getDataStore(params);
String[] typeNames = store.getTypeNames();  // 列出所有图层
SimpleFeatureSource source = store.getFeatureSource(typeNames[0]);
SimpleFeatureCollection features = source.getFeatures();
// 遍历同 Shapefile
store.dispose();
```

### 连接 PostGIS

```java
Map<String, Object> params = new HashMap<>();
params.put("dbtype", "postgis");
params.put("host", "localhost");
params.put("port", 5432);
params.put("schema", "public");
params.put("database", "gisdb");
params.put("user", "postgres");
params.put("passwd", "password");

DataStore store = DataStoreFinder.getDataStore(params);
SimpleFeatureSource source = store.getFeatureSource("buildings");
SimpleFeatureCollection features = source.getFeatures();
// 遍历处理...
store.dispose();
```

---

## 矢量数据写入

### 创建 FeatureType 并写入 Shapefile

```java
import org.geotools.feature.simple.*;
import org.geotools.data.shapefile.*;
import org.locationtech.jts.geom.Point;
import org.geotools.referencing.crs.DefaultGeographicCRS;

// 1. 定义 FeatureType
SimpleFeatureTypeBuilder typeBuilder = new SimpleFeatureTypeBuilder();
typeBuilder.setName("POI");
typeBuilder.setCRS(DefaultGeographicCRS.WGS84);
typeBuilder.add("the_geom", Point.class);
typeBuilder.add("name", String.class);
typeBuilder.add("population", Integer.class);
SimpleFeatureType featureType = typeBuilder.buildFeatureType();

// 2. 构建要素
GeometryFactory gf = JTSFactoryFinder.getGeometryFactory();
SimpleFeatureBuilder fb = new SimpleFeatureBuilder(featureType);
fb.add(gf.createPoint(new Coordinate(116.4, 39.9)));
fb.add("北京");
fb.add(21540000);
SimpleFeature feature = fb.buildFeature(null);

// 3. 写入 Shapefile
ShapefileDataStoreFactory factory = new ShapefileDataStoreFactory();
Map<String, Object> params = new HashMap<>();
params.put("url", new File("output/poi.shp").toURI().toURL());
ShapefileDataStore dataStore = (ShapefileDataStore) factory.createNewDataStore(params);
dataStore.createSchema(featureType);

SimpleFeatureStore featureStore =
    (SimpleFeatureStore) dataStore.getFeatureSource(dataStore.getTypeNames()[0]);
featureStore.addFeatures(DataUtilities.collection(feature));
dataStore.dispose();
```

---

## 坐标参考系统 (CRS) 与坐标转换

```java
import org.geotools.referencing.CRS;
import org.geotools.geometry.jts.JTS;
import org.opengis.referencing.crs.CoordinateReferenceSystem;
import org.opengis.referencing.operation.MathTransform;

// 解码 EPSG
CoordinateReferenceSystem wgs84 = CRS.decode("EPSG:4326");
CoordinateReferenceSystem webMercator = CRS.decode("EPSG:3857");
CoordinateReferenceSystem cgcs2000 = CRS.decode("EPSG:4490");

// 查找坐标转换
MathTransform transform = CRS.findMathTransform(wgs84, webMercator, true);

// 转换几何对象
Geometry projected = JTS.transform(originalGeometry, transform);

// 转换单个坐标
Coordinate source = new Coordinate(116.4, 39.9);
Coordinate target = JTS.transform(source, null, transform);

// 获取 CRS 的 EPSG 编码
Integer code = CRS.lookupEpsgCode(wgs84, false);

// 从 WKT 创建 CRS
CoordinateReferenceSystem custom = CRS.parseWKT("GEOGCS[...]");
```

---

## 空间查询与过滤（CQL / ECQL）

```java
import org.geotools.filter.text.cql2.CQL;
import org.geotools.filter.text.ecql.ECQL;
import org.opengis.filter.Filter;

// 属性过滤
Filter nameFilter = CQL.toFilter("NAME = '北京'");
Filter popFilter = CQL.toFilter("POPULATION > 1000000");

// 空间过滤（BBOX）
Filter bboxFilter = CQL.toFilter(
    "BBOX(the_geom, 116.0, 39.0, 117.0, 40.0)"
);

// 空间关系
Filter containsFilter = CQL.toFilter(
    "CONTAINS(the_geom, POINT(116.4 39.9))"
);
Filter intersectsFilter = CQL.toFilter(
    "INTERSECTS(the_geom, POLYGON((116 39, 117 39, 117 40, 116 40, 116 39)))"
);

// 组合过滤（ECQL 支持更丰富语法）
Filter combined = ECQL.toFilter(
    "NAME LIKE '北%' AND POPULATION > 500000"
);

// 应用过滤查询
SimpleFeatureCollection filtered = featureSource.getFeatures(nameFilter);
```

---

## 几何操作（基于 JTS）

```java
import org.locationtech.jts.geom.*;
import org.geotools.geometry.jts.JTSFactoryFinder;

GeometryFactory gf = JTSFactoryFinder.getGeometryFactory();

// 创建几何对象
Point point = gf.createPoint(new Coordinate(116.4, 39.9));
LineString line = gf.createLineString(new Coordinate[]{
    new Coordinate(0, 0), new Coordinate(10, 10), new Coordinate(20, 0)
});
Polygon polygon = gf.createPolygon(new Coordinate[]{
    new Coordinate(0, 0), new Coordinate(10, 0),
    new Coordinate(10, 10), new Coordinate(0, 10),
    new Coordinate(0, 0)  // 闭合
});

// 缓冲区
Geometry buffered = point.buffer(0.01);

// 空间关系
boolean contains = polygon.contains(point);
boolean intersects = line.intersects(polygon);
boolean within = point.within(polygon);

// 集合运算
Geometry union = polygon1.union(polygon2);
Geometry intersection = polygon1.intersection(polygon2);
Geometry difference = polygon1.difference(polygon2);
Geometry symDiff = polygon1.symDifference(polygon2);

// 几何属性
double area = polygon.getArea();
double length = line.getLength();
Point centroid = polygon.getCentroid();
Envelope env = polygon.getEnvelopeInternal();
double distance = point.distance(line);

// 凸包
Geometry convexHull = geometry.convexHull();

// 简化
import org.locationtech.jts.simplify.TopologyPreservingSimplifier;
Geometry simplified = TopologyPreservingSimplifier.simplify(geometry, 0.001);

// WKT 读写
import org.locationtech.jts.io.WKTReader;
import org.locationtech.jts.io.WKTWriter;
WKTReader wktReader = new WKTReader();
Geometry geom = wktReader.read("POINT (116.4 39.9)");
String wkt = new WKTWriter().write(geom);
```

---

## 栅格数据（GeoTIFF）

### 读取 GeoTIFF

```java
import org.geotools.gce.geotiff.GeoTiffReader;
import org.geotools.coverage.grid.GridCoverage2D;

File file = new File("data/dem.tif");
GeoTiffReader reader = new GeoTiffReader(file);
GridCoverage2D coverage = reader.read(null);

// 获取 CRS
CoordinateReferenceSystem crs = coverage.getCoordinateReferenceSystem();

// 获取范围
ReferencedEnvelope envelope = new ReferencedEnvelope(coverage.getEnvelope());

// 获取像素值
double[] values = coverage.evaluate(
    new DirectPosition2D(crs, 116.4, 39.9), (double[]) null
);

// 获取栅格图像
RenderedImage image = coverage.getRenderedImage();

reader.dispose();
```

### 写入 GeoTIFF

```java
import org.geotools.gce.geotiff.GeoTiffWriter;

File output = new File("output/result.tif");
GeoTiffWriter writer = new GeoTiffWriter(output);
writer.write(coverage, null);
writer.dispose();
```

---

## 地图渲染

### 渲染为 PNG 图片

```java
import org.geotools.map.*;
import org.geotools.styling.*;
import org.geotools.renderer.lite.StreamingRenderer;
import java.awt.image.BufferedImage;
import java.awt.*;

// 创建地图
MapContent map = new MapContent();
map.setTitle("城市分布图");

// 添加矢量图层
Style style = SLD.createSimpleStyle(featureSource.getSchema());
map.addLayer(new FeatureLayer(featureSource, style));

// 渲染为图片
int width = 800, height = 600;
BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);
Graphics2D g2d = image.createGraphics();
g2d.setColor(Color.WHITE);
g2d.fillRect(0, 0, width, height);

StreamingRenderer renderer = new StreamingRenderer();
renderer.setMapContent(map);
renderer.paint(g2d, new Rectangle(width, height), map.getMaxBounds());
g2d.dispose();

// 保存
javax.imageio.ImageIO.write(image, "png", new File("output/map.png"));
map.dispose();
```

### 使用 SLD 样式

```java
import org.geotools.styling.*;
import org.geotools.factory.CommonFactoryFinder;

StyleFactory sf = CommonFactoryFinder.getStyleFactory();
FilterFactory2 ff = CommonFactoryFinder.getFilterFactory2();

// 创建面填充样式
Fill fill = sf.createFill(ff.literal(new Color(0, 128, 255, 128)));
Stroke stroke = sf.createStroke(ff.literal(Color.BLACK), ff.literal(1.0));
PolygonSymbolizer sym = sf.createPolygonSymbolizer(stroke, fill, null);

Rule rule = sf.createRule();
rule.symbolizers().add(sym);

FeatureTypeStyle fts = sf.createFeatureTypeStyle(new Rule[]{rule});
Style style = sf.createStyle();
style.featureTypeStyles().add(fts);
```

---

## GeoJSON 读写

```java
import org.geotools.geojson.feature.FeatureJSON;
import org.geotools.geojson.geom.GeometryJSON;

// 读取 GeoJSON 要素集
FeatureJSON fjson = new FeatureJSON();
SimpleFeatureCollection fc = fjson.readFeatureCollection(
    new FileInputStream("data/points.geojson")
);

// 写入 GeoJSON
fjson.writeFeatureCollection(fc, new FileOutputStream("output/result.geojson"));

// 单个几何体 GeoJSON
GeometryJSON gjson = new GeometryJSON();
Geometry geom = gjson.read(new StringReader("{\"type\":\"Point\",\"coordinates\":[116.4,39.9]}"));
StringWriter sw = new StringWriter();
gjson.write(geom, sw);
```

---

## WKT / WKB 格式转换

```java
import org.locationtech.jts.io.*;

// WKT
WKTReader wktReader = new WKTReader();
Geometry geom = wktReader.read("POLYGON((0 0,10 0,10 10,0 10,0 0))");
String wkt = new WKTWriter().write(geom);

// WKB
WKBReader wkbReader = new WKBReader();
Geometry geom2 = wkbReader.read(wkbBytes);
byte[] wkb = new WKBWriter().write(geom);
```

---

## 典型应用场景

| 场景 | 关键类 / 方法 |
|---|---|
| 读取 Shapefile 数据 | `FileDataStoreFinder` → `SimpleFeatureSource.getFeatures()` |
| 读写 GeoPackage | `DataStoreFinder`（dbtype=geopkg）→ `SimpleFeatureStore` |
| 连接 PostGIS 数据库 | `DataStoreFinder`（dbtype=postgis）→ `SimpleFeatureStore` |
| 读写 GeoJSON | `FeatureJSON.readFeatureCollection()` / `writeFeatureCollection()` |
| 坐标系转换（如 WGS84 → Web Mercator） | `CRS.decode()` → `CRS.findMathTransform()` → `JTS.transform()` |
| 属性查询 | `CQL.toFilter("NAME = 'xxx'")` → `featureSource.getFeatures(filter)` |
| 空间查询（范围过滤） | `CQL.toFilter("BBOX(the_geom, ...)")` |
| 空间关系判断（包含、相交等） | `Geometry.contains()` / `intersects()` / `within()` |
| 缓冲区分析 | `Geometry.buffer(distance)` |
| 面叠加分析（交集 / 合并 / 差集） | `Geometry.intersection()` / `union()` / `difference()` |
| 读取 GeoTIFF 栅格 | `GeoTiffReader.read()` → `GridCoverage2D` |
| 地图渲染输出 PNG | `MapContent` + `StreamingRenderer.paint()` |
| 创建矢量要素并写入 | `SimpleFeatureTypeBuilder` → `SimpleFeatureBuilder` → `SimpleFeatureStore` |
| SLD 样式制图 | `StyleFactory` + `PolygonSymbolizer` / `PointSymbolizer` / `LineSymbolizer` |

---

## 常见注意事项

1. **Maven 仓库**：GeoTools 不在 Maven Central 上，必须配置 OSGeo 仓库（`https://repo.osgeo.org/repository/release/`）。
2. **EPSG 数据库**：使用 CRS 功能时，需引入 `gt-epsg-hsql`（嵌入式）或 `gt-epsg-wkt`（轻量）模块，否则 `CRS.decode()` 会抛出异常。
3. **坐标轴顺序**：GeoTools 默认遵循 EPSG 规范（纬度在前），调用 `CRS.decode("EPSG:4326", true)` 可强制经度在前（lon/lat 顺序）。
4. **资源释放**：`DataStore`、`Reader`、`Writer`、`MapContent` 使用后必须调用 `dispose()` 释放资源。`SimpleFeatureIterator` 需在 try-with-resources 或 finally 中关闭。
5. **线程安全**：`DataStore` 实例是线程安全的，可在多线程间共享；但 `SimpleFeatureIterator` 不是线程安全的。
6. **SPI 机制**：GeoTools 使用 Java SPI（ServiceLoader）自动发现 DataStore 工厂、CRS 工厂等，确保相关模块 JAR 在 classpath 中。
7. **JTS 版本**：GeoTools 28+ 使用 `org.locationtech.jts`（而非旧版 `com.vividsolutions.jts`），注意包名差异。
8. **性能优化**：对大数据量场景，使用 `Query` 对象限制返回属性和空间范围，避免全量加载；PostGIS 场景建议开启 `preparedStatements`。
9. **中文属性**：Shapefile 中文乱码时，创建 `ShapefileDataStore` 后调用 `store.setCharset(Charset.forName("GBK"))` 设置编码。

---

## 参考链接

- **GitHub 仓库：** <https://github.com/geotools/geotools>
- **官方文档：** <https://docs.geotools.org/>
- **用户指南：** <https://docs.geotools.org/stable/userguide/>
- **Javadoc：** <https://docs.geotools.org/stable/javadocs/>
- **教程（Quickstart）：** <https://docs.geotools.org/stable/userguide/tutorial/quickstart/index.html>
- **OSGeo Maven 仓库：** <https://repo.osgeo.org/repository/release/>
- **JTS Topology Suite：** <https://github.com/locationtech/jts>

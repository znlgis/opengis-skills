# GeoTools Vector I/O Reference

Vector read/write and GeoJSON/WKT format examples split from SKILL.md.

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


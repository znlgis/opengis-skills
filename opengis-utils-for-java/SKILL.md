---
name: opengis-utils-for-java
description: opengis-utils-for-java 是一个基于 GeoTools、JTS、GDAL/OGR 和 ESRI Geometry API 的统一 Java GIS 工具包，提供图层读写、几何操作、双引擎架构和坐标参考系统管理等功能。
---

> **项目地址：** https://github.com/znlgis/opengis-utils-for-java
> 
> This document is designed to help AI assistants (and developers) quickly understand and use the OGU4J library for GIS development in Java.

## Library Overview

**OGU4J** (OpenGIS Utils for Java) is a unified Java GIS toolkit built on GeoTools, JTS, GDAL/OGR, and ESRI Geometry API. It provides:

- A unified layer model (`OguLayer`) for reading/writing GIS data across formats
- Geometry operations (60+ methods) via `GeometryUtil`
- Dual-engine architecture (GeoTools pure-Java & GDAL native)
- Coordinate reference system management (CGCS2000 built-in)

**Java Version:** 17+  
**Build Tool:** Maven  
**Group ID:** `com.znlgis.ogu4j` | **Artifact ID:** `ogu4j` | **Version:** `1.0.0`

---

## Project Structure

```
com.znlgis.ogu4j
├── datasource/                  # High-level data I/O
│   ├── OguLayerUtil             # ★ Primary entry point for reading/writing layers
│   └── GtTxtUtil                # National land TXT format support
├── engine/                      # GIS engine core
│   ├── GisEngine                # Engine interface
│   ├── GisEngineFactory         # Engine factory (auto-selects best engine)
│   ├── GeoToolsEngine           # GeoTools implementation (pure Java, always available)
│   ├── GdalEngine               # GDAL implementation (requires native GDAL)
│   ├── GeoToolsLayerReader/Writer  # GeoTools format I/O
│   ├── GdalLayerReader/Writer      # GDAL format I/O
│   ├── enums/                   # Enumerations
│   │   ├── DataFormatType       # SHP, GEOJSON, FILEGDB, POSTGIS, TXT, WKT, ESRIJSON, ARCSDE
│   │   ├── FieldDataType        # INTEGER, DOUBLE, STRING, BINARY, DATE, TIME, DATETIME, LONG
│   │   ├── GeometryType         # POINT, MULTIPOINT, LINESTRING, POLYGON, etc.
│   │   ├── GisEngineType        # GEOTOOLS, GDAL, AUTO
│   │   └── TopologyValidationErrorType
│   ├── io/                      # Reader/Writer interfaces
│   │   ├── LayerReader          # read(path, layerName, attributeFilter, spatialFilterWkt)
│   │   └── LayerWriter          # write(layer, path, layerName, options)
│   ├── model/
│   │   ├── layer/               # ★ Core data model
│   │   │   ├── OguLayer         # Layer: name, wkid, geometryType, fields, features
│   │   │   ├── OguFeature       # Feature: id, geometry (WKT), attributes
│   │   │   ├── OguField         # Field definition: name, alias, dataType, length
│   │   │   ├── OguFieldValue    # Field value with type conversion methods
│   │   │   ├── OguCoordinate    # Coordinate point (x, y, z)
│   │   │   ├── OguFeatureFilter # Functional interface for filtering
│   │   │   └── OguLayerMetadata # Extended metadata (CRS, projection, etc.)
│   │   ├── DbConnBaseModel      # PostGIS connection configuration
│   │   ├── GdbGroupModel        # FileGDB structure
│   │   ├── TopologyValidationResult
│   │   └── SimpleGeometryResult
│   └── util/
│       ├── CrsUtil              # Coordinate system management & transformation
│       ├── GeotoolsUtil         # GeoTools feature filtering
│       ├── OgrUtil              # GDAL/OGR initialization & resource management
│       ├── PostgisUtil          # PostGIS connection helpers
│       ├── ShpUtil              # Shapefile encoding & field name handling
│       └── GdalCmdUtil          # GDAL command-line wrapper (ogrinfo)
├── geometry/
│   └── GeometryUtil             # ★ 60+ geometry operation methods
├── exception/
│   ├── OguException             # Base checked exception
│   ├── DataSourceException      # Data source connection failures
│   ├── EngineNotSupportedException
│   ├── FormatParseException     # Format parsing failures
│   ├── LayerValidationException # Unchecked (RuntimeException)
│   └── TopologyException
└── utils/
    ├── ZipUtil                  # ZIP compress/decompress
    ├── EncodingUtil             # File encoding detection
    ├── SortUtil                 # Natural string sorting
    └── NumUtil                  # Number formatting (remove scientific notation)
```

---

## Quick Reference: Common Tasks

### 1. Read a GIS Layer (Shapefile / GeoJSON / PostGIS / FileGDB / TXT)

```java
import com.znlgis.ogu4j.datasource.OguLayerUtil;
import com.znlgis.ogu4j.engine.enums.DataFormatType;
import com.znlgis.ogu4j.engine.enums.GisEngineType;
import com.znlgis.ogu4j.engine.model.layer.OguLayer;

// Read Shapefile (GeoTools engine)
OguLayer layer = OguLayerUtil.readLayer(
    DataFormatType.SHP,          // format
    "/path/to/file.shp",        // path or connection string
    null,                        // layer name (null for single-layer formats)
    null,                        // attribute filter (CQL expression, e.g. "NAME = 'Beijing'")
    null,                        // spatial filter (WKT geometry)
    GisEngineType.AUTO           // engine: AUTO, GEOTOOLS, or GDAL
);

// Read GeoJSON
OguLayer layer = OguLayerUtil.readLayer(
    DataFormatType.GEOJSON, "/path/to/file.geojson",
    null, null, null, GisEngineType.GEOTOOLS
);

// Read FileGDB layer (requires GDAL)
OguLayer layer = OguLayerUtil.readLayer(
    DataFormatType.FILEGDB, "/path/to/data.gdb",
    "layerName", null, null, GisEngineType.GDAL
);

// Read PostGIS (use environment variables or secure config for credentials in production)
String connStr = "PG: host=localhost port=5432 dbname=gisdb user=postgres password=*** active_schema=public";
OguLayer layer = OguLayerUtil.readLayer(
    DataFormatType.POSTGIS, connStr,
    "table_name", null, null, GisEngineType.GEOTOOLS
);

// Read National Land TXT
import com.znlgis.ogu4j.datasource.GtTxtUtil;
OguLayer layer = GtTxtUtil.loadTxt("/path/to/file.txt", null);  // null = auto-detect fields
```

### 2. Write a GIS Layer

```java
import com.znlgis.ogu4j.datasource.OguLayerUtil;

// Write to Shapefile
OguLayerUtil.writeLayer(
    DataFormatType.SHP,
    layer,                       // OguLayer object
    "/path/to/output.shp",      // output path
    null,                        // layer name
    null,                        // options map (format-specific)
    GisEngineType.GEOTOOLS
);

// Write to GeoJSON
OguLayerUtil.writeLayer(
    DataFormatType.GEOJSON, layer,
    "/path/to/output.geojson", null, null, GisEngineType.GEOTOOLS
);

// Write to FileGDB (with options)
Map<String, Object> options = new HashMap<>();
options.put("featureDataset", "datasetName");
OguLayerUtil.writeLayer(
    DataFormatType.FILEGDB, layer,
    "/path/to/data.gdb", "layerName", options, GisEngineType.GDAL
);

// Write to PostGIS
OguLayerUtil.writeLayer(
    DataFormatType.POSTGIS, layer,
    connStr, "table_name", null, GisEngineType.GEOTOOLS
);

// Write National Land TXT
import com.znlgis.ogu4j.engine.model.layer.OguLayerMetadata;
OguLayerMetadata metadata = new OguLayerMetadata();
metadata.setCoordinateSystemName("2000国家大地坐标系");
metadata.setZoneDivision("3");
metadata.setProjectionType("高斯克吕格");
metadata.setMeasureUnit("米");
GtTxtUtil.saveTxt(layer, "/path/to/output.txt", metadata, null, 39);
```

### 3. Format Conversion (One-Step)

```java
// SHP → GeoJSON
OguLayer layer = OguLayerUtil.readLayer(DataFormatType.SHP, shpPath, null, null, null, GisEngineType.AUTO);
OguLayerUtil.writeLayer(DataFormatType.GEOJSON, layer, geojsonPath, null, null, GisEngineType.AUTO);

// GeoJSON → PostGIS
OguLayer layer = OguLayerUtil.readLayer(DataFormatType.GEOJSON, geojsonPath, null, null, null, GisEngineType.AUTO);
OguLayerUtil.writeLayer(DataFormatType.POSTGIS, layer, connStr, "tableName", null, GisEngineType.AUTO);
```

### 4. Work with the Layer Model

```java
import com.znlgis.ogu4j.engine.model.layer.*;
import com.znlgis.ogu4j.engine.enums.*;

// Create a layer from scratch
OguLayer layer = new OguLayer();
layer.setName("cities");
layer.setWkid(4490);  // CGCS2000 geographic
layer.setGeometryType(GeometryType.POINT);

// Define fields
List<OguField> fields = new ArrayList<>();
fields.add(new OguField("name", "城市名称", FieldDataType.STRING));
fields.add(new OguField("population", "人口", FieldDataType.INTEGER));
layer.setFields(fields);

// Create features
OguFeature feature = new OguFeature();
feature.setId("1");
feature.setGeometry("POINT(116.4 39.9)");  // WKT format
List<OguFieldValue> attrs = new ArrayList<>();
attrs.add(new OguFieldValue(fields.get(0), "北京"));
attrs.add(new OguFieldValue(fields.get(1), 21540000));
feature.setAttributes(attrs);
layer.setFeatures(List.of(feature));

// Validate layer
layer.validate();  // throws LayerValidationException if invalid

// Serialize to/from JSON
String json = layer.toJSON();
OguLayer restored = OguLayer.fromJSON(json);

// Filter features by attribute
List<OguFeature> filtered = layer.filter(f -> {
    Integer pop = f.getAttribute("population").getIntValue();
    return pop != null && pop > 10000000;  // population > 10 million
});

// Access feature attributes
OguFeature f = layer.getFeatures().get(0);
String name = f.getAttribute("name").getStringValue();
Object val = f.getValue("name");
f.setValue("name", "新名称");

// Get counts
int featureCount = layer.getFeatureCount();
int fieldCount = layer.getFieldCount();
```

### 5. Geometry Operations (GeometryUtil)

```java
import com.znlgis.ogu4j.geometry.GeometryUtil;
import org.locationtech.jts.geom.Geometry;

// === Format Conversions ===
Geometry geom = GeometryUtil.wkt2Geometry("POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))");
String wkt = GeometryUtil.geometry2Wkt(geom);
String geojson = GeometryUtil.geometry2Geojson(geom);
String esriJson = GeometryUtil.geometry2EsriJson(geom, 4490);

// WKT ↔ GeoJSON
String geojson = GeometryUtil.wkt2Geojson(wkt);
String wkt = GeometryUtil.geojson2Wkt(geojson);

// WKT ↔ ESRI JSON
String esriJson = GeometryUtil.wkt2EsriJson(wkt, 4490);
String wkt = GeometryUtil.esriJson2Wkt(esriJson);

// GeoJSON ↔ ESRI JSON
String esriJson = GeometryUtil.geoJson2EsriJson(4490, geojson);
String geojson = GeometryUtil.esriJson2GeoJson(esriJson);

// GeoJSON / ESRI JSON → JTS Geometry
Geometry geom = GeometryUtil.geojson2Geometry(geojson);
Geometry geom = GeometryUtil.esriJson2Geometry(esriJson);

// === Spatial Relations (JTS Geometry-based) ===
boolean result = GeometryUtil.intersects(geomA, geomB);
boolean result = GeometryUtil.contains(geomA, geomB);
boolean result = GeometryUtil.within(geomA, geomB);
boolean result = GeometryUtil.touches(geomA, geomB);
boolean result = GeometryUtil.crosses(geomA, geomB);
boolean result = GeometryUtil.overlaps(geomA, geomB);
boolean result = GeometryUtil.disjoint(geomA, geomB);
String de9im = GeometryUtil.relate(geomA, geomB);
boolean result = GeometryUtil.relatePattern(geomA, geomB, "T*T***FF*");

// === Spatial Analysis (JTS Geometry-based) ===
Geometry buffer = GeometryUtil.buffer(geom, 100.0);
Geometry intersection = GeometryUtil.intersection(geomA, geomB);
Geometry union = GeometryUtil.union(geomA, geomB);   // also accepts varargs
Geometry difference = GeometryUtil.difference(geomA, geomB);
Geometry symDiff = GeometryUtil.symDifference(geomA, geomB);
Geometry convexHull = GeometryUtil.convexHull(geom);
Geometry concaveHull = GeometryUtil.concaveHull(geom);
Geometry splitResult = GeometryUtil.splitPolygon(polygon, line);
Geometry polygonized = GeometryUtil.polygonize(geom);

// === Geometry Properties ===
double area = GeometryUtil.area(geom);
double length = GeometryUtil.length(geom);
double distance = GeometryUtil.distance(geomA, geomB);
boolean withinDist = GeometryUtil.isWithinDistance(geomA, geomB, 500.0);
Geometry centroid = GeometryUtil.centroid(geom);
Geometry interiorPt = GeometryUtil.interiorPoint(geom);
Geometry boundary = GeometryUtil.boundary(geom);
Geometry envelope = GeometryUtil.envelope(geom);
int dimension = GeometryUtil.dimension(geom);
int numPts = GeometryUtil.numPoints(geom);
boolean empty = GeometryUtil.isEmpty(geom);
GeometryType type = GeometryUtil.geometryType(geom);

// === Topology Validation ===
TopologyValidationResult validResult = GeometryUtil.isValid(geom);
// validResult.isValid(), .getErrorType(), .getCoordinate(), .getMessage()

SimpleGeometryResult simpleResult = GeometryUtil.isSimple(geom);
// simpleResult.isSimple(), .getNonSimplePts()

Geometry validated = GeometryUtil.validate(geom);  // auto-fix invalid geometry

// === Simplification & Densification ===
Geometry simplified = GeometryUtil.simplify(geom, 1.0);
Geometry densified = GeometryUtil.densify(geom, 0.5);

// === Geometry Equality ===
boolean exact = GeometryUtil.equalsExact(geomA, geomB);
boolean exactTol = GeometryUtil.equalsExactTolerance(geomA, geomB, 0.001);
boolean norm = GeometryUtil.equalsNorm(geomA, geomB);
boolean topo = GeometryUtil.equalsTopo(geomA, geomB);
```

### 6. WKT-Based Geometry Operations (ESRI Geometry API)

These methods work directly with WKT strings, without creating JTS Geometry objects. Useful when geometry data is in WKT format. Method names end with `Wkt`.

```java
// Spatial relations (require wkid for coordinate system context)
boolean result = GeometryUtil.intersectsWkt(wktA, wktB, 4490);
boolean result = GeometryUtil.containsWkt(wktA, wktB, 4490);
boolean result = GeometryUtil.withinWkt(wktA, wktB, 4490);
boolean result = GeometryUtil.touchesWkt(wktA, wktB, 4490);
boolean result = GeometryUtil.crossesWkt(wktA, wktB, 4490);
boolean result = GeometryUtil.overlapsWkt(wktA, wktB, 4490);
boolean result = GeometryUtil.disjointWkt(wktA, wktB, 4490);
boolean result = GeometryUtil.equalsWkt(wktA, wktB, 4490);
boolean result = GeometryUtil.relatePatternWkt(wktA, wktB, 4490, "T*T***FF*");

// Spatial analysis (returns WKT strings)
String buffer = GeometryUtil.bufferWkt(wkt, 4490, 100.0);
String intersection = GeometryUtil.intersectionWkt(wktA, wktB, 4490);
String union = GeometryUtil.unionWkt(wktList, 4490);  // List<String>
String difference = GeometryUtil.differenceWkt(wktA, wktB, 4490);
String symDiff = GeometryUtil.symDifferenceWkt(wktA, wktB, 4490);
String convexHull = GeometryUtil.convexHullWkt(wkt);
String boundary = GeometryUtil.boundaryWkt(wkt);

// Properties (WKT-based)
double area = GeometryUtil.areaWkt(wkt);
double length = GeometryUtil.lengthWkt(wkt);
double distance = GeometryUtil.distanceWkt(wktA, wktB, 4490);
String centroid = GeometryUtil.centroidWkt(wkt);
int dimension = GeometryUtil.dimensionWkt(wkt);
boolean empty = GeometryUtil.isEmptyWkt(wkt);
GeometryType type = GeometryUtil.geometryTypeWkt(wkt);
boolean simple = GeometryUtil.isSimpleWkt(wkt, 4490);

// Simplification
String simplified = GeometryUtil.simplifyWkt(wkt, 4490);
```

### 7. Coordinate Reference System (CrsUtil)

```java
import com.znlgis.ogu4j.engine.util.CrsUtil;

// Transform WKT geometry between coordinate systems
String transformedWkt = CrsUtil.transform(wkt, 4490, 4528);  // CGCS2000 geo → CGCS2000 / 3-degree zone 39

// Transform JTS Geometry
Geometry transformed = CrsUtil.transform(geometry, 4490, 4528);

// Reproject an entire layer
OguLayer reprojected = CrsUtil.reproject(layer, 4528);

// Get zone number
int zoneNumber = CrsUtil.getDh(geometry);  // from JTS Geometry
int zoneNumber = CrsUtil.getDh(wkt);       // from WKT string
int zoneNumber = CrsUtil.getDh(4528);      // from projected WKID

// Get WKID for geometry
Integer wkid = CrsUtil.getWkid(geometry);

// Get projected WKID from zone number
Integer projectedWkid = CrsUtil.getProjectedWkid(39);          // zone number
Integer projectedWkid = CrsUtil.getProjectedWkid(geometry);    // from geometry

// Check CRS type
boolean isProjected = CrsUtil.isProjectedCRS(crs);

// Get tolerance for CRS
double tolerance = CrsUtil.getTolerance(4490);

// Get all supported CRS (EPSG 4490-4554, CGCS2000 series)
Map<Integer, CoordinateReferenceSystem> crsList = CrsUtil.getSupportedCRSList();
Map.Entry<Integer, CoordinateReferenceSystem> entry = CrsUtil.getSupportedCRS(4490);
```

### 8. Engine API (Advanced Usage)

```java
import com.znlgis.ogu4j.engine.*;
import com.znlgis.ogu4j.engine.enums.*;

// Get engine via factory
GisEngine engine = GisEngineFactory.getEngine(GisEngineType.AUTO);
GisEngine engine = GisEngineFactory.getEngine(DataFormatType.GEOJSON);  // auto-select
GisEngine engine = GisEngineFactory.getEngine(GisEngineType.GEOTOOLS, DataFormatType.SHP);

// Check engine capabilities
boolean available = engine.isAvailable();
boolean supports = engine.supports(DataFormatType.FILEGDB);

// Read/write via engine
OguLayer layer = engine.readLayer(DataFormatType.SHP, path, layerName, attrFilter, spatialFilter);
engine.writeLayer(DataFormatType.SHP, layer, path, layerName, options);

// Get reader/writer directly
LayerReader reader = engine.getReader(DataFormatType.GEOJSON);
LayerWriter writer = engine.getWriter(DataFormatType.GEOJSON);
OguLayer layer = reader.read(path, layerName, attrFilter, spatialFilterWkt);
writer.write(layer, path, layerName, options);
```

### 9. Utility Classes

```java
// ZIP operations
import com.znlgis.ogu4j.utils.ZipUtil;
ZipUtil.zip(folder, "output.zip");                           // default GBK encoding
ZipUtil.zip(folder, "output.zip", StandardCharsets.UTF_8);   // custom encoding
ZipUtil.unzip("input.zip", destPath);
ZipUtil.unzip(zipFile, destPath);

// File encoding detection
import com.znlgis.ogu4j.utils.EncodingUtil;
Charset charset = EncodingUtil.getFileEncoding(file);  // detects UTF-8, GBK, GB2312, GB18030

// Natural sorting (handles numbers within strings)
import com.znlgis.ogu4j.utils.SortUtil;
int cmp = SortUtil.compareString("item2", "item10");  // returns negative (2 < 10)

// Remove scientific notation
import com.znlgis.ogu4j.utils.NumUtil;
String plain = NumUtil.getPlainString(1.234E10);  // "12340000000"

// FileGDB structure inspection (requires GDAL)
import com.znlgis.ogu4j.engine.util.GdalCmdUtil;
GdbGroupModel structure = GdalCmdUtil.getGdbDataStructure("/path/to/data.gdb");

// PostGIS helpers
import com.znlgis.ogu4j.engine.util.PostgisUtil;
String gdalConn = PostgisUtil.toGdalPostgisConnStr(dbConnModel);
JDBCDataStore ds = PostgisUtil.getGeotoolsPostgisDataSource(dbConnModel);

// Shapefile helpers
import com.znlgis.ogu4j.engine.util.ShpUtil;
ShpUtil.formatFieldName(fields);                   // truncate to 10 chars
Charset charset = ShpUtil.check("/path/to/file.shp");  // verify & detect encoding
```

---

## Data Format Support Matrix

| Format | DataFormatType | GeoTools | GDAL | Read | Write | Notes |
|--------|---------------|----------|------|------|-------|-------|
| Shapefile | `SHP` | ✅ | ✅ | ✅ | ✅ | Field names limited to 10 chars |
| GeoJSON | `GEOJSON` | ✅ | ✅ | ✅ | ✅ | |
| FileGDB | `FILEGDB` | ❌ | ✅ | ✅ | ✅ | Requires GDAL native library |
| PostGIS | `POSTGIS` | ✅ | ✅ | ✅ | ✅ | Connection string as path |
| National Land TXT | `TXT` | ✅ | ❌ | ✅ | ✅ | Use `GtTxtUtil` directly |
| WKT | `WKT` | ✅ | ❌ | ✅ | ❌ | Geometry-only format |
| ESRI JSON | `ESRIJSON` | ❌ | ❌ | ✅* | ❌ | *Via `GeometryUtil` conversion |

---

## Data Model Reference

### OguLayer (Core)

| Property | Type | Description |
|----------|------|-------------|
| `name` | `String` | Layer name |
| `alias` | `String` | Layer display name |
| `wkid` | `Integer` | EPSG code (e.g. 4490 for CGCS2000) |
| `geometryType` | `GeometryType` | POINT, POLYGON, LINESTRING, etc. |
| `tolerance` | `Double` | Geometric tolerance |
| `fields` | `List<OguField>` | Field definitions |
| `features` | `List<OguFeature>` | Feature collection |
| `metadata` | `OguLayerMetadata` | Extended metadata |

**Methods:** `fromJSON(String)`, `toJSON()`, `validate()`, `filter(OguFeatureFilter)`, `getFeatureCount()`, `getFieldCount()`

### OguFeature

| Property | Type | Description |
|----------|------|-------------|
| `id` | `String` | Feature identifier |
| `geometry` | `String` | Geometry in WKT format |
| `attributes` | `List<OguFieldValue>` | Attribute values |
| `coordinates` | `List<OguCoordinate>` | Coordinate points (TXT format) |
| `rawValues` | `List<String>` | Raw values (TXT format) |

**Methods:** `getAttribute(String fieldName)`, `getValue(String fieldName)`, `setValue(String fieldName, Object value)`

### OguField

| Property | Type | Description |
|----------|------|-------------|
| `name` | `String` | Field name |
| `alias` | `String` | Display name |
| `description` | `String` | Description |
| `dataType` | `FieldDataType` | INTEGER, DOUBLE, STRING, DATE, etc. |
| `length` | `Integer` | Max length (for STRING) |
| `nullable` | `Boolean` | Nullable flag |
| `defaultValue` | `Object` | Default value |

**Constructors:** `OguField(name, alias, dataType)`, `OguField(name, alias, description, dataType)`

### OguFieldValue

| Property | Type | Description |
|----------|------|-------------|
| `field` | `OguField` | Field definition |
| `value` | `Object` | Raw value |

**Methods:** `getFieldName()`, `getStringValue()`, `getIntValue()`, `getDoubleValue()`

### OguCoordinate

| Property | Type | Description |
|----------|------|-------------|
| `x` | `Double` | X coordinate (longitude) |
| `y` | `Double` | Y coordinate (latitude) |
| `z` | `Double` | Z coordinate (elevation, optional) |
| `pointNumber` | `String` | Point identifier |
| `ringNumber` | `Integer` | Ring/loop number |

**Constructors:** `OguCoordinate(x, y)`, `OguCoordinate(x, y, z)`

### DbConnBaseModel (PostGIS connection)

| Property | Type | Description |
|----------|------|-------------|
| `dbType` | `String` | Database type |
| `host` | `String` | Host address |
| `port` | `String` | Port number |
| `schema` | `String` | Schema name |
| `database` | `String` | Database name |
| `user` | `String` | Username |
| `passwd` | `String` | Password |

---

## Enumerations Quick Reference

### GeometryType

`POINT`, `MULTIPOINT`, `LINESTRING`, `LINEARRING`, `MULTILINESTRING`, `POLYGON`, `MULTIPOLYGON`, `GEOMETRYCOLLECTION`

**Lookup methods:** `valueOfByTypeName(String)`, `valueOfByTypeCode(int)`, `valueOfByTypeClass(Class<?>)`, `valueOfByWkbGeometryType(int)`

### FieldDataType

`INTEGER`, `DOUBLE`, `STRING`, `BINARY`, `DATE`, `TIME`, `DATETIME`, `LONG`

**Lookup methods:** `fieldDataTypeByGdalCode(int)`, `fieldDataTypeByTypeClass(Class<?>)`

### DataFormatType

`WKT`, `GEOJSON`, `ESRIJSON`, `SHP`, `TXT`, `FILEGDB`, `POSTGIS`, `ARCSDE`

**Properties per value:** `desc` (description), `gdalDriverName` (GDAL driver name)

### GisEngineType

`GEOTOOLS`, `GDAL`, `AUTO`

---

## Exception Hierarchy

```
Exception
└── OguException                      # Base checked exception
    ├── DataSourceException           # Data source connection/access failure
    ├── EngineNotSupportedException   # Engine doesn't support the operation/format
    ├── FormatParseException          # Data format parsing failure
    └── TopologyException             # Geometry topology error

RuntimeException
└── LayerValidationException          # Layer data validation failure (unchecked)
```

---

## Architecture & Design Patterns

- **Factory Pattern:** `GisEngineFactory` creates engine instances; use `GisEngineType.AUTO` for automatic selection (prefers GDAL if available)
- **Strategy Pattern:** `LayerReader` / `LayerWriter` interfaces define pluggable format-specific I/O strategies
- **Adapter Pattern:** `GisEngine` provides a unified API over GeoTools and GDAL
- **Functional Interface:** `OguFeatureFilter` enables lambda-based feature filtering
- **Geometry is WKT:** Features store geometry as WKT strings in `OguFeature.geometry`; use `GeometryUtil` for conversion/operations

---

## Important Notes for AI Developers

1. **Always use `OguLayerUtil` as the primary entry point** for reading/writing GIS data. It handles engine selection and format routing.

2. **Geometry in features is stored as WKT strings.** Convert to JTS `Geometry` objects via `GeometryUtil.wkt2Geometry()` when you need spatial operations.

3. **Engine selection:**
   - `GisEngineType.AUTO` — library auto-selects (prefers GDAL if available)
   - `GisEngineType.GEOTOOLS` — pure Java, always available, no native dependencies
   - `GisEngineType.GDAL` — requires native GDAL library installed; needed for FileGDB format

4. **CGCS2000 coordinate system** (EPSG:4490) is the default/primary CRS. Projected CRS range: EPSG 4502-4554 (3-degree zones). Use `CrsUtil` for transformation.

5. **PostGIS connection strings** follow the format:
   `"PG: host=<host> port=<port> dbname=<db> user=<user> password=<pwd> active_schema=<schema>"`

6. **Resource management:**
   - `DataStore` objects (ShapefileDataStore, JDBCDataStore) must be disposed in finally blocks
   - OGR `DataSource` objects must be closed via `OgrUtil.closeDataSource()`

7. **Shapefile field names** are limited to 10 characters. Use `ShpUtil.formatFieldName()` to auto-truncate.

8. **OguLayer can be serialized to/from JSON** using `layer.toJSON()` and `OguLayer.fromJSON(json)` (backed by FastJSON2).

9. **Attribute filtering** uses CQL expression syntax (e.g., `"population > 1000000 AND name LIKE '%京%'"`).

10. **Spatial filtering** accepts WKT geometry strings (e.g., `"POLYGON((115 39, 117 39, 117 41, 115 41, 115 39))"`).

11. **Two geometry operation styles:**
    - JTS-based: Pass `Geometry` objects, get `Geometry` back (e.g., `GeometryUtil.buffer(geom, dist)`)
    - WKT-based (suffix `Wkt`): Pass WKT strings and WKID, get WKT back (e.g., `GeometryUtil.bufferWkt(wkt, wkid, dist)`)

12. **Build with Maven:** `mvn compile` — requires the OSGeo repository for GeoTools dependencies:
    ```xml
    <repository>
        <id>osgeo</id>
        <url>https://repo.osgeo.org/repository/release/</url>
    </repository>
    ```

---

## Typical Workflow Example

```java
import com.znlgis.ogu4j.datasource.OguLayerUtil;
import com.znlgis.ogu4j.engine.enums.*;
import com.znlgis.ogu4j.engine.model.layer.*;
import com.znlgis.ogu4j.engine.util.CrsUtil;
import com.znlgis.ogu4j.geometry.GeometryUtil;
import org.locationtech.jts.geom.Geometry;

// Step 1: Read a Shapefile
OguLayer layer = OguLayerUtil.readLayer(
    DataFormatType.SHP, "/data/parcels.shp",
    null, null, null, GisEngineType.AUTO
);

// Step 2: Filter features by area > 10,000 square units
List<OguFeature> largeParcels = layer.filter(f -> {
    Geometry geom = GeometryUtil.wkt2Geometry(f.getGeometry());
    return GeometryUtil.area(geom) > 10000;
});

// Step 3: Buffer each geometry
for (OguFeature f : largeParcels) {
    Geometry geom = GeometryUtil.wkt2Geometry(f.getGeometry());
    Geometry buffered = GeometryUtil.buffer(geom, 50.0);
    f.setGeometry(GeometryUtil.geometry2Wkt(buffered));
}

// Step 4: Reproject to projected CRS
OguLayer projected = CrsUtil.reproject(layer, 4528);

// Step 5: Export to GeoJSON
OguLayerUtil.writeLayer(
    DataFormatType.GEOJSON, projected,
    "/data/output.geojson", null, null, GisEngineType.AUTO
);
```

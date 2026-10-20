---
name: opengis-utils-for-java
description: "Use when needing common GIS utilities in Java — OguLayerUtil layer read/write, GeometryUtil 60+ ops, CrsUtil CGCS2000 (EPSG:4490, 4502-4554), Shapefile/GeoJSON/FileGDB/PostGIS/land TXT I/O, topology validation; also for GDAL UnsatisfiedLinkError on gdal_jni, missing osgeo repo on GeoTools, or resolving com.znlgis.ogu4j:ogu4j:1.0.0 that is not on Maven Central. OGU4J."
tags:
  - java
  - gis
  - geotools
  - jts
  - gdal
  - geometry
  - vector
  - crs
  - cgcs2000
---

> **项目地址：** <https://github.com/znlgis/opengis-utils-for-java>
>
> **官方文档：** <https://github.com/znlgis/opengis-utils-for-java#readme>
>
> **Maven 坐标：** `com.znlgis.ogu4j:ogu4j:1.0.0`（截至2026-10 尚未发布到 Maven Central，需从源码 `mvn install` 安装到本地仓库）
>
> **许可证：** LGPL-2.1-or-later

## 概述

**OGU4J** (OpenGIS Utils for Java) is a unified Java GIS toolkit built on GeoTools, JTS, GDAL/OGR, and ESRI Geometry API. It provides:

- A unified layer model (`OguLayer`) for reading/writing GIS data across formats
- Geometry operations (60+ methods) via `GeometryUtil`
- Dual-engine architecture (GeoTools pure-Java & GDAL native)
- Coordinate reference system management (CGCS2000 built-in)

**Java Version:** 17+  
**Build Tool:** Maven  
**Group ID:** `com.znlgis.ogu4j` | **Artifact ID:** `ogu4j` | **Version:** `1.0.0`

---

## 环境准备

```bash
# 前置：JDK 17+ 与 Maven 3.8+
java -version
mvn -version

# 克隆并构建（安装到本地 Maven 仓库）
git clone https://github.com/znlgis/opengis-utils-for-java.git
cd opengis-utils-for-java
mvn install -DskipTests
```

在业务项目的 `pom.xml` 中引入依赖（GeoTools 依赖通过 osgeo 仓库解析）：

```xml
<repositories>
    <repository>
        <id>osgeo</id>
        <url>https://repo.osgeo.org/repository/release/</url>
    </repository>
</repositories>

<dependency>
    <groupId>com.znlgis.ogu4j</groupId>
    <artifactId>ogu4j</artifactId>
    <version>1.0.0</version>
</dependency>
```

**环境要求：** JDK 17+；GDAL 引擎需本地原生 GDAL 库（与 `org.gdal:gdal` 绑定版本 3.13.0 匹配）；纯 GeoTools 引擎无需原生库。验证：`mvn dependency:tree` 中出现 `com.znlgis.ogu4j:ogu4j:1.0.0`，且代码中 `import com.znlgis.ogu4j.datasource.OguLayerUtil;` 可编译。

---

## 核心 API：包结构与入口类

```text
com.znlgis.ogu4j
├── datasource/                  # High-level data I/O
│   ├── OguLayerUtil             # Primary entry point for reading/writing layers
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
│   │   ├── layer/               # Core data model
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
│   └── GeometryUtil             # 60+ geometry operation methods
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

> 常见任务快速参考（Quick Reference: Common Tasks）完整内容见 [reference/common-tasks.md](reference/common-tasks.md)

## Data Format Support Matrix

| Format | DataFormatType | GeoTools | GDAL | Read | Write | Notes |
|--------|---------------|----------|------|------|-------|-------|
| Shapefile | `SHP` | Yes | Yes | Yes | Yes | Field names limited to 10 chars |
| GeoJSON | `GEOJSON` | Yes | Yes | Yes | Yes | |
| FileGDB | `FILEGDB` | No | Yes | Yes | Yes | Requires GDAL native library |
| PostGIS | `POSTGIS` | Yes | Yes | Yes | Yes | Connection string as path |
| National Land TXT | `TXT` | Yes | No | Yes | Yes | Use `GtTxtUtil` directly |
| WKT | `WKT` | Yes | No | Yes | No | Geometry-only format |
| ESRI JSON | `ESRIJSON` | No | No | Yes* | No | *Via `GeometryUtil` conversion |

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

```text
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

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("opengis-utils-for-java")` 加载（用户也可输入 `/opengis-utils-for-java`）；`reference/common-tasks.md` 按需 `read`，路径相对加载结果中的 Base directory；技能目录只读，验证工程建在会话工作区。
- **执行环境**：先 `java -version` 与 `mvn -version`（需 JDK 17+、Maven 3.8+），Windows 用 `pwsh`；`mvn -v` 里显示的 JDK 才是 Maven 实际使用的，与 shell 的 `java` 不一致时改 `JAVA_HOME` 再重试。
- **源码安装（本库未发布到 Central）**：`git clone https://github.com/znlgis/opengis-utils-for-java.git` 后 `mvn install -DskipTests`，产物落在 `~/.m2/repository/com/znlgis/ogu4j/ogu4j/1.0.0/`；用 `mvn dependency:tree -Dincludes=com.znlgis.ogu4j` 确认坐标可解析。不要在 `pom.xml` 里直接写 `ogu4j:1.0.0` 后指望从 Central 下载。
- **仓库与网络**：GeoTools 依赖不在 Central，`pom.xml` 必须带 `https://repo.osgeo.org/repository/release/`，否则 `Could not resolve dependencies for org.geotools:*`；离线或私服缺包时如实报告依赖不可下载，不要自行换版本或加未知仓库。
- **原生 GDAL 匹配**：GDAL 引擎绑定 `org.gdal:gdal` 3.13.0，本机需装 GDAL 3.13.x 且 `java.library.path` 能找到 `gdal_jni`（Windows 上 `java -XshowSettings:properties -version 2>&1 | Select-String library.path`）；报 `UnsatisfiedLinkError: no gdal_jni in java.library.path` 说明原生库缺失或版本不符，此时改用 `GisEngineType.GEOTOOLS`。
- **验证产物**：写最小 main 读一个 Shapefile/GeoJSON → `OguLayerUtil.readLayer(DataFormatType.SHP, path, null, null, null, GisEngineType.AUTO)`，打印 `layer.getWkid()`、`layer.getFeatureCount()`，再 `writeLayer` 成 GeoJSON 并重新读回比对要素数与 CRS；`mvn -q -DskipTests package` 只说明能编译。
- **常见误操**：`AUTO` 在本机有原生 GDAL 时会优先走 GDAL，想复现纯 Java 结果必须显式传 `GisEngineType.GEOTOOLS`；`OguFeature.geometry` 是 WKT 字符串，做运算前先 `GeometryUtil.wkt2Geometry()`；`DataStore` 与 OGR `DataSource` 要在 `finally` 里释放，否则文件被占用后 `writeLayer` 覆盖失败。
- **安全与权限**：PostGIS 连接串（`PG: host=... password=...`）里的密码不要回显到输出；`mvn install` 会写 `~/.m2`、示例代码会写 `/data` 等绝对路径，覆盖已有数据前先确认路径并征得用户同意。

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

## 常见问题

| 问题 | 解决 |
|------|------|
| `mvn install` 依赖解析失败 | 配置 osgeo 仓库（GeoTools 依赖不在 Maven Central）；确认 Maven 3.8+ 与 JDK 17+ |
| 找不到 `com.znlgis.ogu4j:ogu4j` 依赖 | 该库尚未发布到 Maven Central，先在本仓库执行 `mvn install` 安装到本地仓库 |
| 运行时报 GDAL 相关 `UnsatisfiedLinkError` | 本地缺少与 `org.gdal:gdal` 3.13.0 匹配的原生 GDAL；安装 GDAL 3.13.x，或改用 `GisEngineType.GEOTOOLS` |
| FileGDB 读写失败 | FileGDB 仅 GDAL 引擎支持：安装原生 GDAL 并使用 `GisEngineType.GDAL` 或 `AUTO` |
| Shapefile 字段名被截断 | DBF 规范限制 10 字符，使用 `ShpUtil.formatFieldName()` 自动截断 |
| PostGIS 连接失败 | 检查连接串格式（`PG: host=... port=... dbname=... user=... password=... active_schema=...`）与 schema 名称 |

---

## 相关技能

- **geotools** — Java GIS 工具库：[../geotools/SKILL.md](../geotools/SKILL.md)
- **jts** — JTS Topology Suite：[../jts/SKILL.md](../jts/SKILL.md)
- **geometry-api-java** — Esri Geometry API：[../geometry-api-java/SKILL.md](../geometry-api-java/SKILL.md)
- **gdal** — 命令行数据处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **gdal-api** — GDAL 编程 API：[../gdal-api/SKILL.md](../gdal-api/SKILL.md)

## 典型工作流示例

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

## 参考资源

- **GitHub 仓库：** <https://github.com/znlgis/opengis-utils-for-java>
- **OSGeo 发布仓库（GeoTools 依赖）：** <https://repo.osgeo.org/repository/release/>
- **GeoTools 官网：** <https://geotools.org/>
- **中文教程（znlgis）：** <https://znlgis.github.io/gis/tutorial/opengis-utils-for-java/>

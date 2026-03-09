---
name: opengis-utils-for-net
description: opengis-utils-for-net 是一个基于 GDAL/OGR 的 .NET GIS 工具包，提供图层读写、几何操作、双引擎架构和坐标参考系统管理等功能。
---

> **项目地址：** https://github.com/znlgis/opengis-utils-for-net
> AI-friendly reference for developing with this library.
> Package: `OpenGIS.Utils` | Target: .NET Standard 2.0 | Engine: GDAL/OGR

## Installation

```bash
dotnet add package OpenGIS.Utils
```

## Build & Test

```bash
dotnet build OpenGIS.Utils.sln
dotnet test tests/OpenGIS.Utils.Tests/
```

---

## Project Structure

```
src/OpenGIS.Utils/
├── Configuration/        # GdalConfiguration, LibrarySettings
├── DataSource/           # OguLayerUtil (high-level I/O), GtTxtUtil (National Land Survey TXT)
├── Engine/
│   ├── Enums/            # GeometryType, FieldDataType, DataFormatType, GisEngineType, TopologyValidationErrorType
│   ├── IO/               # ILayerReader, ILayerWriter
│   ├── Model/
│   │   └── Layer/        # OguLayer, OguFeature, OguField, OguFieldValue, OguCoordinate, OguLayerMetadata
│   ├── Util/             # CrsUtil, OgrUtil, ShpUtil, PostgisUtil, GdalCmdUtil
│   ├── GdalEngine.cs     # GDAL implementation of GisEngine
│   ├── GdalReader.cs     # ILayerReader implementation
│   ├── GdalWriter.cs     # ILayerWriter implementation
│   ├── GisEngine.cs      # Abstract base class
│   └── GisEngineFactory.cs
├── Exception/            # OguException, DataSourceException, FormatParseException, etc.
├── Geometry/             # GeometryUtil (50+ static methods)
└── Utils/                # EncodingUtil, NumUtil, SortUtil, ZipUtil
```

---

## Namespaces

| Namespace | Key Classes |
|---|---|
| `OpenGIS.Utils.Configuration` | `GdalConfiguration`, `LibrarySettings` |
| `OpenGIS.Utils.DataSource` | `OguLayerUtil`, `GtTxtUtil` |
| `OpenGIS.Utils.Engine` | `GisEngine`, `GisEngineFactory`, `GdalEngine`, `GdalReader`, `GdalWriter` |
| `OpenGIS.Utils.Engine.Enums` | `GeometryType`, `FieldDataType`, `DataFormatType`, `GisEngineType`, `TopologyValidationErrorType` |
| `OpenGIS.Utils.Engine.IO` | `ILayerReader`, `ILayerWriter` |
| `OpenGIS.Utils.Engine.Model` | `DbConnBaseModel`, `GdbGroupModel`, `TopologyValidationResult`, `SimpleGeometryResult` |
| `OpenGIS.Utils.Engine.Model.Layer` | `OguLayer`, `OguFeature`, `OguField`, `OguFieldValue`, `OguCoordinate`, `OguLayerMetadata` |
| `OpenGIS.Utils.Engine.Util` | `CrsUtil`, `OgrUtil`, `ShpUtil`, `PostgisUtil`, `GdalCmdUtil` |
| `OpenGIS.Utils.Exception` | `OguException`, `DataSourceException`, `FormatParseException`, `EngineNotSupportedException`, `LayerValidationException`, `TopologyException` |
| `OpenGIS.Utils.Geometry` | `GeometryUtil` |
| `OpenGIS.Utils.Utils` | `EncodingUtil`, `NumUtil`, `SortUtil`, `ZipUtil` |

---

## Enums

### GeometryType

```
POINT, LINESTRING, POLYGON, MULTIPOINT, MULTILINESTRING, MULTIPOLYGON, GEOMETRYCOLLECTION, UNKNOWN
```

### FieldDataType

```
STRING, INTEGER, LONG, DOUBLE, FLOAT, BOOLEAN, DATE, DATETIME, BINARY, UNKNOWN
```

### DataFormatType

```
SHP, GEOJSON, FILEGDB, POSTGIS, TXT, GEOPACKAGE, KML, DXF, UNKNOWN
```

### GisEngineType

```
GEOTOOLS, GDAL
```

### TopologyValidationErrorType

```
ERROR, REPEATED_POINT, HOLE_OUTSIDE_SHELL, NESTED_HOLES, DISCONNECTED_INTERIOR,
SELF_INTERSECTION, RING_SELF_INTERSECTION, NESTED_SHELLS, DUPLICATE_RINGS,
TOO_FEW_POINTS, INVALID_COORDINATE, RING_NOT_CLOSED
```

---

## Core Model Classes

### OguLayer

```csharp
using OpenGIS.Utils.Engine.Model.Layer;
using OpenGIS.Utils.Engine.Enums;
```

| Property | Type | Description |
|---|---|---|
| `Name` | `string` | Layer name |
| `Wkid` | `int?` | Coordinate system WKID (e.g. 4326 for WGS84) |
| `GeometryType` | `GeometryType` | Geometry type |
| `Fields` | `IList<OguField>` | Field definitions |
| `Features` | `IList<OguFeature>` | Feature collection |
| `Metadata` | `OguLayerMetadata?` | Optional metadata |

| Method | Returns | Description |
|---|---|---|
| `Validate()` | `void` | Validates layer integrity; throws `LayerValidationException` |
| `Filter(Func<OguFeature, bool>)` | `IList<OguFeature>` | Filters features by predicate |
| `GetFeatureCount()` | `int` | Feature count |
| `ToJson()` | `string` | Serializes to JSON |
| `FromJson(string json)` | `OguLayer?` | *static* — Deserializes from JSON |
| `Clone()` | `OguLayer` | Deep copy |
| `GetField(string fieldName)` | `OguField?` | Gets field by name |
| `AddField(OguField field)` | `void` | Adds a field definition |
| `AddFeature(OguFeature feature)` | `void` | Adds a feature |
| `RemoveFeature(int fid)` | `bool` | Removes feature by FID |

### OguFeature

| Property | Type | Description |
|---|---|---|
| `Fid` | `int` | Feature ID |
| `Wkt` | `string?` | Geometry in WKT format |
| `Attributes` | `Dictionary<string, OguFieldValue>` | Attribute values |

| Method | Returns | Description |
|---|---|---|
| `GetValue(string fieldName)` | `object?` | Gets raw attribute value |
| `SetValue(string fieldName, object? value)` | `void` | Sets attribute value |
| `GetAttribute(string fieldName)` | `OguFieldValue?` | Gets field value object |
| `HasAttribute(string fieldName)` | `bool` | Checks if attribute exists |
| `ToJson()` | `string` | Serializes to JSON |
| `FromJson(string json)` | `OguFeature?` | *static* — Deserializes from JSON |
| `Clone()` | `OguFeature` | Deep copy |

### OguField

| Property | Type | Description |
|---|---|---|
| `Name` | `string` | Field name |
| `Alias` | `string?` | Display alias |
| `DataType` | `FieldDataType` | Data type |
| `Length` | `int?` | String length |
| `Precision` | `int?` | Numeric precision |
| `Scale` | `int?` | Decimal places |
| `IsNullable` | `bool` | Whether nullable |
| `DefaultValue` | `object?` | Default value |

Methods: `ToJson()`, `FromJson(string)`, `Clone()`

### OguFieldValue

| Property | Type |
|---|---|
| `Value` | `object?` |
| `IsNull` | `bool` |

Type-safe getters: `GetStringValue()`, `GetIntValue()`, `GetLongValue()`, `GetDoubleValue()`, `GetFloatValue()`, `GetBoolValue()`, `GetDateTimeValue()`, `GetDecimalValue()`

### OguCoordinate

| Property | Type | Description |
|---|---|---|
| `X` | `double` | X coordinate (longitude) |
| `Y` | `double` | Y coordinate (latitude) |
| `Z` | `double?` | Z coordinate (elevation, optional) |
| `PointNumber` | `string?` | Point number |
| `RingNumber` | `string?` | Ring number |
| `Remark` | `string?` | Remark text |

Methods: `ToWkt()` → `string`, `FromWkt(string wkt)` → `OguCoordinate` *(static)*

### OguLayerMetadata

| Property | Type |
|---|---|
| `DataSource` | `string?` |
| `CoordinateSystemName` | `string?` |
| `ZoneDivision` | `string?` |
| `ProjectionType` | `string?` |
| `MeasureUnit` | `string?` |
| `ExtendedProperties` | `Dictionary<string, object>` |
| `CreateTime` | `DateTime?` |
| `ModifyTime` | `DateTime?` |

---

## Data I/O — OguLayerUtil (Recommended Entry Point)

```csharp
using OpenGIS.Utils.DataSource;
using OpenGIS.Utils.Engine.Enums;
```

### Read

```csharp
OguLayer layer = OguLayerUtil.ReadLayer(
    DataFormatType.SHP,            // format
    "data/cities.shp",            // path
    layerName: null,               // optional: layer name
    attributeFilter: "POP > 1000", // optional: SQL where clause
    spatialFilterWkt: null,        // optional: WKT spatial filter
    engineType: null,              // optional: defaults to GDAL
    options: null                   // optional: driver-specific options
);

// Async version
OguLayer layer = await OguLayerUtil.ReadLayerAsync(DataFormatType.GEOJSON, "data.geojson");
```

### Write

```csharp
OguLayerUtil.WriteLayer(
    DataFormatType.GEOJSON,        // output format
    layer,                          // OguLayer
    "output/cities.geojson",       // output path
    layerName: null,               // optional
    engineType: null,              // optional
    options: null                   // optional
);

// Async version
await OguLayerUtil.WriteLayerAsync(DataFormatType.SHP, layer, "output.shp");
```

### Format Conversion

```csharp
OguLayerUtil.ConvertFormat(
    "input.shp", DataFormatType.SHP,
    "output.geojson", DataFormatType.GEOJSON
);

// Async
await OguLayerUtil.ConvertFormatAsync(
    "input.shp", DataFormatType.SHP,
    "output.gpkg", DataFormatType.GEOPACKAGE
);
```

### Utilities

```csharp
IList<string> names = OguLayerUtil.GetLayerNames(DataFormatType.FILEGDB, "data.gdb");
```

### Supported Format ↔ Driver

| DataFormatType | Driver Name | Extension |
|---|---|---|
| `SHP` | ESRI Shapefile | .shp |
| `GEOJSON` | GeoJSON | .geojson / .json |
| `FILEGDB` | FileGDB | .gdb |
| `GEOPACKAGE` | GPKG | .gpkg |
| `KML` | KML | .kml |
| `DXF` | DXF | .dxf |
| `POSTGIS` | PostGIS | (database) |
| `TXT` | Custom | .txt |

---

## Geometry Operations — GeometryUtil

```csharp
using OpenGIS.Utils.Geometry;
```

All methods are `public static`.

### Format Conversion

```csharp
OgrGeometry geom = GeometryUtil.Wkt2Geometry(string wkt);
string wkt       = GeometryUtil.Geometry2Wkt(OgrGeometry geom);
string geojson   = GeometryUtil.Wkt2Geojson(string wkt);
string geojson   = GeometryUtil.Geometry2Geojson(OgrGeometry geom);
```

> **⚠️ Limitation:** `Geojson2Wkt(string)` and `Geojson2Geometry(string)` throw `NotSupportedException`. To parse GeoJSON, load from file via `GdalReader`.

### Spatial Relationships (OgrGeometry)

```csharp
bool GeometryUtil.Intersects(OgrGeometry a, OgrGeometry b)
bool GeometryUtil.Contains(OgrGeometry a, OgrGeometry b)
bool GeometryUtil.Within(OgrGeometry a, OgrGeometry b)
bool GeometryUtil.Touches(OgrGeometry a, OgrGeometry b)
bool GeometryUtil.Crosses(OgrGeometry a, OgrGeometry b)
bool GeometryUtil.Overlaps(OgrGeometry a, OgrGeometry b)
bool GeometryUtil.Disjoint(OgrGeometry a, OgrGeometry b)
```

### Spatial Relationships (WKT convenience)

```csharp
bool GeometryUtil.IntersectsWkt(string wktA, string wktB)
bool GeometryUtil.ContainsWkt(string wktA, string wktB)
```

### Spatial Analysis (OgrGeometry)

```csharp
OgrGeometry GeometryUtil.Buffer(OgrGeometry geom, double distance)
OgrGeometry GeometryUtil.Intersection(OgrGeometry a, OgrGeometry b)
OgrGeometry GeometryUtil.Union(OgrGeometry a, OgrGeometry b)
OgrGeometry GeometryUtil.Union(IEnumerable<OgrGeometry> geometries)
OgrGeometry GeometryUtil.Difference(OgrGeometry a, OgrGeometry b)
OgrGeometry GeometryUtil.SymDifference(OgrGeometry a, OgrGeometry b)
```

### Spatial Analysis (WKT convenience)

```csharp
string GeometryUtil.BufferWkt(string wkt, double distance)
string GeometryUtil.IntersectionWkt(string wktA, string wktB)
string GeometryUtil.UnionWkt(IEnumerable<string> wktList)
```

### Geometry Properties

```csharp
double       GeometryUtil.Area(OgrGeometry geom)
double       GeometryUtil.Length(OgrGeometry geom)
OgrGeometry  GeometryUtil.Centroid(OgrGeometry geom)
OgrGeometry  GeometryUtil.InteriorPoint(OgrGeometry geom)
int          GeometryUtil.Dimension(OgrGeometry geom)
int          GeometryUtil.NumPoints(OgrGeometry geom)
GeometryType GeometryUtil.GetGeometryType(OgrGeometry geom)
bool         GeometryUtil.IsEmpty(OgrGeometry geom)
```

### Geometry Properties (WKT convenience)

```csharp
double GeometryUtil.AreaWkt(string wkt)
double GeometryUtil.LengthWkt(string wkt)
string GeometryUtil.CentroidWkt(string wkt)
```

### Geometry Operations

```csharp
OgrGeometry GeometryUtil.Boundary(OgrGeometry geom)
OgrGeometry GeometryUtil.Envelope(OgrGeometry geom)
OgrGeometry GeometryUtil.ConvexHull(OgrGeometry geom)
OgrGeometry GeometryUtil.Simplify(OgrGeometry geom, double tolerance)
OgrGeometry GeometryUtil.Densify(OgrGeometry geom, double distanceTolerance)
string      GeometryUtil.SimplifyWkt(string wkt, double tolerance)
```

### Topology Validation

```csharp
TopologyValidationResult GeometryUtil.IsValid(OgrGeometry geom)
SimpleGeometryResult     GeometryUtil.IsSimple(OgrGeometry geom)
```

### Equality & Distance

```csharp
bool   GeometryUtil.EqualsExact(OgrGeometry a, OgrGeometry b)
bool   GeometryUtil.EqualsExactTolerance(OgrGeometry a, OgrGeometry b, double tolerance)
bool   GeometryUtil.EqualsTopo(OgrGeometry a, OgrGeometry b)
double GeometryUtil.Distance(OgrGeometry a, OgrGeometry b)
bool   GeometryUtil.IsWithinDistance(OgrGeometry a, OgrGeometry b, double maxDistance)
```

---

## Coordinate Reference Systems — CrsUtil

```csharp
using OpenGIS.Utils.Engine.Util;
```

```csharp
// Coordinate transformation
string      CrsUtil.Transform(string wkt, int sourceWkid, int targetWkid)
OgrGeometry CrsUtil.Transform(OgrGeometry geometry, int sourceWkid, int targetWkid)

// CGCS2000 zone calculations
int  CrsUtil.GetDh(OgrGeometry geometry)   // 3-degree zone from centroid
int  CrsUtil.GetDh(double longitude)       // 3-degree zone from longitude
int  CrsUtil.GetDh6(double longitude)      // 6-degree zone from longitude
int  CrsUtil.GetDhFromWkid(int projectedWkid) // Zone from WKID

// CGCS2000 projected WKID lookup
int  CrsUtil.GetProjectedWkid(int zoneNumber)  // 3-degree zone → WKID
int  CrsUtil.GetProjectedWkid6(int zoneNumber) // 6-degree zone → WKID

// Properties
double CrsUtil.GetTolerance(int wkid)       // Recommended tolerance
bool   CrsUtil.IsProjectedCRS(int wkid)     // Is projected CRS?
```

---

## Shapefile Utilities — ShpUtil

```csharp
using OpenGIS.Utils.Engine.Util;
```

```csharp
OguLayer  ShpUtil.ReadShapefile(string shpPath, Encoding? encoding = null)
void      ShpUtil.WriteShapefile(OguLayer layer, string shpPath, Encoding? encoding = null)
Encoding  ShpUtil.GetShapefileEncoding(string shpPath)
void      ShpUtil.CreateCpgFile(string shpPath, Encoding encoding)
Envelope? ShpUtil.GetShapefileBounds(string shpPath)
void      ShpUtil.RepairShapefile(string shpPath)
```

---

## PostGIS Utilities — PostgisUtil

```csharp
using OpenGIS.Utils.Engine.Util;
```

```csharp
OguLayer PostgisUtil.ReadPostGIS(string connectionString, string tableName, string? filter = null)
void     PostgisUtil.WritePostGIS(OguLayer layer, string connectionString, string tableName)
bool     PostgisUtil.TableExists(string connectionString, string tableName)
void     PostgisUtil.CreateSpatialIndex(string connectionString, string tableName, string geomColumn = "geom")
```

---

## National Land Survey TXT Format — GtTxtUtil

```csharp
using OpenGIS.Utils.DataSource;
```

```csharp
OguLayer      GtTxtUtil.LoadTxt(string txtPath, Encoding? encoding = null)
void          GtTxtUtil.SaveTxt(OguLayer layer, string txtPath, OguLayerMetadata? metadata = null, Encoding? encoding = null, int? zoneNumber = null)
OguCoordinate? GtTxtUtil.ParseTxtLine(string line)
string        GtTxtUtil.FormatTxtLine(OguCoordinate coordinate, int zoneNumber)
```

---

## GDAL Configuration

```csharp
using OpenGIS.Utils.Configuration;
```

```csharp
GdalConfiguration.ConfigureGdal()            // Auto-called, thread-safe
GdalConfiguration.RegisterAllDrivers()
string       GdalConfiguration.GetGdalVersion()
IList<string> GdalConfiguration.GetSupportedDrivers()
bool         GdalConfiguration.IsDriverAvailable(string driverName)
```

### LibrarySettings (Global Defaults)

| Property | Type | Default | Description |
|---|---|---|---|
| `DefaultTolerance` | `double` | `0.0001` | Default geometry tolerance |
| `AutoCreateSpatialIndex` | `bool` | `true` | Auto-create spatial index |
| `SpatialIndexThreshold` | `int` | `1000` | Feature count threshold for index |
| `DefaultBufferSegments` | `int` | `8` | Buffer curve segments |
| `UseGdalExceptions` | `bool` | `true` | GDAL exception mode |

---

## Engine Architecture

```csharp
using OpenGIS.Utils.Engine;
```

```csharp
// Abstract base
public abstract class GisEngine
{
    public abstract GisEngineType EngineType { get; }
    public abstract IList<DataFormatType> SupportedFormats { get; }
    public abstract ILayerReader CreateReader();
    public abstract ILayerWriter CreateWriter();
    public virtual bool SupportsFormat(DataFormatType format);
}

// Factory
GisEngine engine = GisEngineFactory.GetEngine(GisEngineType.GDAL);
GisEngine engine = GisEngineFactory.GetEngine(DataFormatType.SHP);
bool ok = GisEngineFactory.TryGetEngine(DataFormatType.GEOJSON, out GisEngine? engine);
```

### ILayerReader / ILayerWriter

```csharp
public interface ILayerReader
{
    OguLayer Read(string path, string? layerName = null, string? attributeFilter = null,
        string? spatialFilterWkt = null, Dictionary<string, object>? options = null);
    IList<string> GetLayerNames(string path);
}

public interface ILayerWriter
{
    void Write(OguLayer layer, string path, string? layerName = null,
        Dictionary<string, object>? options = null);
    void Append(OguLayer layer, string path, string? layerName = null,
        Dictionary<string, object>? options = null);
}
```

---

## General Utilities

### EncodingUtil

```csharp
using OpenGIS.Utils.Utils;
```

```csharp
Encoding EncodingUtil.GetFileEncoding(string filePath)
Encoding EncodingUtil.GetFileEncoding(Stream stream)
Encoding EncodingUtil.DetectEncoding(byte[] buffer)
Encoding EncodingUtil.DetectEncoding(byte[] buffer, int length)
void     EncodingUtil.ConvertFileEncoding(string filePath, Encoding targetEncoding)
```

### ZipUtil

```csharp
void ZipUtil.Zip(string folderPath, string zipPath)
void ZipUtil.Zip(string folderPath, string zipPath, Encoding encoding)
void ZipUtil.Unzip(string zipPath, string destPath)
void ZipUtil.Unzip(string zipPath, string destPath, Encoding encoding)
void ZipUtil.CompressFiles(IEnumerable<string> filePaths, string zipPath)
```

### SortUtil

```csharp
int SortUtil.CompareString(string a, string b)  // Natural sort comparison
IOrderedEnumerable<T> SortUtil.NaturalSort<T>(IEnumerable<T> source, Func<T, string> keySelector)
```

### NumUtil

```csharp
string NumUtil.GetPlainString(double number)   // No scientific notation
string NumUtil.GetPlainString(decimal number)
double NumUtil.Round(double value, int decimals)
string NumUtil.FormatNumber(double value, int decimals)
```

---

## Exception Hierarchy

```
System.Exception
└── OguException (ErrorCode, Context)
    ├── DataSourceException        — Data source access errors
    ├── EngineNotSupportedException — Unsupported engine type
    ├── FormatParseException       — Format parsing errors
    ├── LayerValidationException   — Layer validation failures
    └── TopologyException          — Topology validation/operation errors
```

---

## Result Models

### TopologyValidationResult

| Property | Type |
|---|---|
| `IsValid` | `bool` |
| `ErrorType` | `TopologyValidationErrorType?` |
| `ErrorMessage` | `string?` |
| `ErrorLocation` | `string?` (WKT) |

### SimpleGeometryResult

| Property | Type |
|---|---|
| `IsSimple` | `bool` |
| `Reason` | `string?` |
| `NonSimpleLocation` | `string?` (WKT) |

### DbConnBaseModel

Properties: `Host`, `Port`, `Database`, `Username`, `Password`, `Schema`, `ConnectionString` (all nullable)

### GdbGroupModel

Properties: `GdbPath` (`string?`), `LayerNames` (`List<string>`)

---

## Common Code Patterns

### Create a Layer from Scratch

```csharp
using OpenGIS.Utils.Engine.Model.Layer;
using OpenGIS.Utils.Engine.Enums;

var layer = new OguLayer
{
    Name = "cities",
    GeometryType = GeometryType.POINT,
    Wkid = 4326
};

layer.AddField(new OguField { Name = "ID", DataType = FieldDataType.INTEGER });
layer.AddField(new OguField { Name = "Name", DataType = FieldDataType.STRING, Length = 100 });
layer.AddField(new OguField { Name = "Population", DataType = FieldDataType.LONG });

var feature = new OguFeature { Fid = 1, Wkt = "POINT (116.404 39.915)" };
feature.SetValue("ID", 1);
feature.SetValue("Name", "Beijing");
feature.SetValue("Population", 21540000L);
layer.AddFeature(feature);

layer.Validate();
```

### Read → Process → Write

```csharp
using OpenGIS.Utils.DataSource;
using OpenGIS.Utils.Engine.Enums;
using OpenGIS.Utils.Geometry;

var layer = OguLayerUtil.ReadLayer(DataFormatType.SHP, "input.shp");

// Filter features
var largeCities = layer.Filter(f =>
{
    var pop = f.GetAttribute("Population")?.GetLongValue();
    return pop.HasValue && pop.Value > 1000000;
});

// Buffer each geometry
foreach (var feature in layer.Features)
{
    if (feature.Wkt != null)
    {
        feature.Wkt = GeometryUtil.BufferWkt(feature.Wkt, 0.01);
    }
}

OguLayerUtil.WriteLayer(DataFormatType.GEOJSON, layer, "output.geojson");
```

### Coordinate Transformation

```csharp
using OpenGIS.Utils.Engine.Util;

string wktWgs84 = "POINT (116.404 39.915)";
string wktCgcs2000 = CrsUtil.Transform(wktWgs84, 4326, 4490);

int zone = CrsUtil.GetDh(116.404);           // 3-degree zone number
int wkid = CrsUtil.GetProjectedWkid(zone);   // Projected WKID
string projected = CrsUtil.Transform(wktWgs84, 4326, wkid);
```

### Geometry Analysis

```csharp
using OpenGIS.Utils.Geometry;

string polygon = "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))";
string point = "POINT (5 5)";

bool contains = GeometryUtil.ContainsWkt(polygon, point);   // true
double area   = GeometryUtil.AreaWkt(polygon);               // 100.0
string center = GeometryUtil.CentroidWkt(polygon);           // "POINT (5 5)"
string buffer = GeometryUtil.BufferWkt(point, 1.0);          // Buffered polygon WKT
```

### Format Conversion (One Line)

```csharp
OguLayerUtil.ConvertFormat("input.shp", DataFormatType.SHP, "output.gpkg", DataFormatType.GEOPACKAGE);
```

### JSON Serialization

```csharp
string json = layer.ToJson();
OguLayer? restored = OguLayer.FromJson(json);
```

### Shapefile with Encoding

```csharp
using OpenGIS.Utils.Engine.Util;
using System.Text;

var layer = ShpUtil.ReadShapefile("data.shp", Encoding.GetEncoding("GBK"));
ShpUtil.WriteShapefile(layer, "output.shp", Encoding.UTF8);
```

### Natural Sorting

```csharp
using OpenGIS.Utils.Utils;

var files = new[] { "file1.txt", "file10.txt", "file2.txt" };
var sorted = SortUtil.NaturalSort(files, f => f);
// Result: file1.txt, file2.txt, file10.txt
```

---

## Important Notes

1. **GDAL auto-initializes** — No manual `GdalConfiguration.ConfigureGdal()` call needed.
2. **GeoJSON string parsing not supported** — `Geojson2Wkt()` and `Geojson2Geometry()` throw `NotSupportedException`. Load GeoJSON from files via `GdalReader` or `OguLayerUtil.ReadLayer(DataFormatType.GEOJSON, path)`.
3. **Geometry uses WKT strings** — `OguFeature.Wkt` stores geometry as WKT. Use `GeometryUtil` for conversions and operations.
4. **Thread safety** — GDAL initialization is thread-safe. Individual GDAL geometry objects are NOT thread-safe.
5. **Cross-platform** — .NET Standard 2.0: works on .NET Core 2.0+, .NET 5+, .NET Framework 4.6.1+.
6. **Encoding support** — `EncodingUtil` detects UTF-8, UTF-16 LE/BE, GBK, GB2312. Register CodePages with `Encoding.RegisterProvider(CodePagesEncodingProvider.Instance)` if needed.
7. **WKT convenience methods** — Most `GeometryUtil` methods have `*Wkt` variants that accept/return WKT strings directly, avoiding the need to manage `OgrGeometry` objects.

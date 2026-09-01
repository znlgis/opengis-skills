# OpenGIS Utils for .NET Utility Classes Reference

OguLayerUtil, GeometryUtil, CrsUtil, ShpUtil, PostgisUtil, GtTxtUtil and GDAL configuration split from SKILL.md.

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


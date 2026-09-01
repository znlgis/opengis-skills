---
name: opengis-utils-for-net
description: "Use when needing common GIS utility functions in .NET/C# — CRS utilities, geometry helpers, format converters, spatial validation. OpenGIS Utils for .NET: convenience toolkit for .NET GIS projects."
tags:
  - dotnet
  - csharp
  - gdal
  - ogr
  - geometry
  - vector
  - crs
  - cgcs2000
---

> **项目地址：** <https://github.com/znlgis/opengis-utils-for-net>
>
> **官方文档：** <https://github.com/znlgis/opengis-utils-for-net#readme>
>
> **NuGet 包：** `OpenGIS.Utils`
>
> **许可证：** Apache-2.0

## 概述

**OGU4N** (OpenGIS Utils for .NET) 是一个面向 .NET 的 GIS 实用工具集，提供矢量数据读写、几何运算、坐标系管理等能力。核心特性：

- **统一数据读写**：`OguLayerUtil` 一站式读取/写出 Shapefile、GeoJSON、FileGDB、GeoPackage、KML、DXF、PostGIS、TXT 等格式
- **几何运算**：`GeometryUtil` 提供 50+ 静态方法（空间关系、集合运算、属性查询、拓扑验证）
- **坐标系管理**：`CrsUtil` 支持 CGCS2000 系列坐标系变换与分区计算
- **辅助工具**：编码检测、文件压缩、自然排序、数字格式化等
- **仅 GDAL 引擎**：.NET 版本基于 GDAL/OGR 实现（与 Java 版本不同，后者同时支持 GeoTools 和 GDAL）

**环境要求：** .NET Standard 2.0+（兼容 .NET Core 2.0+、.NET 5+、.NET Framework 4.6.1+）

---

## 环境准备

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
GDAL
```

> **注意：** .NET 版本仅支持 GDAL 引擎，与 Java 版本不同（Java 版本同时支持 GEOTOOLS 和 GDAL）。

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

> OguLayerUtil、GeometryUtil、CrsUtil、ShpUtil、PostgisUtil、GtTxtUtil 等工具类与 GDAL 配置的完整 API 见 [reference/util-classes.md](reference/util-classes.md)

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

> 常用代码模式完整示例见 [reference/code-patterns.md](reference/code-patterns.md)

## AI 使用建议

### 推荐工作流

1. **读取数据**：使用 `OguLayerUtil.ReadLayer()` 统一入口读取各类矢量格式
2. **几何运算**：使用 `GeometryUtil.Wkt2Geometry()` 转换后操作，或直接用 `*Wkt` 后缀方法
3. **坐标转换**：使用 `CrsUtil.Transform()` 进行坐标系变换（CGCS2000 系列）
4. **写出结果**：使用 `OguLayerUtil.WriteLayer()` 写出为目标格式
5. **格式转换**：使用 `OguLayerUtil.ConvertFormat()` 一步完成

### 关键注意事项

- **GDAL 自动初始化**：无需手动调用 `GdalConfiguration.ConfigureGdal()`
- **GeoJSON 字符串解析不支持**：`Geojson2Wkt()` 和 `Geojson2Geometry()` 抛出 `NotSupportedException`，需从文件加载
- **几何以 WKT 存储**：`OguFeature.Wkt` 存储 WKT 字符串；多数 `GeometryUtil` 方法有 `*Wkt` 变体
- **.NET 仅支持 GDAL 引擎**：与 Java 版本不同，无 GeoTools 引擎
- **线程安全**：GDAL 初始化线程安全，但单个 GDAL 几何对象非线程安全

## 相关技能

- **nettopologysuite** — .NET 几何计算核心：[../nettopologysuite/SKILL.md](../nettopologysuite/SKILL.md)
- **geometry-api-net** — Esri Geometry API for .NET：[../geometry-api-net/SKILL.md](../geometry-api-net/SKILL.md)
- **gdal** — 命令行数据处理：[../gdal/SKILL.md](../gdal/SKILL.md)
- **gdal-api** — GDAL 编程 API：[../gdal-api/SKILL.md](../gdal-api/SKILL.md)

## Important Notes

1. **GDAL auto-initializes** — No manual `GdalConfiguration.ConfigureGdal()` call needed.
2. **GeoJSON string parsing not supported** — `Geojson2Wkt()` and `Geojson2Geometry()` throw `NotSupportedException`. Load GeoJSON from files via `GdalReader` or `OguLayerUtil.ReadLayer(DataFormatType.GEOJSON, path)`.
3. **Geometry uses WKT strings** — `OguFeature.Wkt` stores geometry as WKT. Use `GeometryUtil` for conversions and operations.
4. **Thread safety** — GDAL initialization is thread-safe. Individual GDAL geometry objects are NOT thread-safe.
5. **Cross-platform** — .NET Standard 2.0: works on .NET Core 2.0+, .NET 5+, .NET Framework 4.6.1+.
6. **Encoding support** — `EncodingUtil` detects UTF-8, UTF-16 LE/BE, GBK, GB2312. Register CodePages with `Encoding.RegisterProvider(CodePagesEncodingProvider.Instance)` if needed.
7. **WKT convenience methods** — Most `GeometryUtil` methods have `*Wkt` variants that accept/return WKT strings directly, avoiding the need to manage `OgrGeometry` objects.

# OpenGIS Utils for .NET Common Code Patterns

Common code patterns and examples split from SKILL.md.

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


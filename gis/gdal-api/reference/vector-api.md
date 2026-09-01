# GDAL Python Vector API Reference

Vector read/write, format conversion, geometry ops and GeoPackage details split from SKILL.md.

---

## 矢量数据读取

### C++

```cpp
#include "ogrsf_frmts.h"

GDALAllRegister();

GDALDataset *ds = (GDALDataset *)GDALOpenEx("cities.shp", GDAL_OF_VECTOR, nullptr, nullptr, nullptr);
if (ds == nullptr) { /* 错误处理 */ }

OGRLayer *layer = ds->GetLayer(0);
layer->ResetReading();

OGRFeature *feature;
while ((feature = layer->GetNextFeature()) != nullptr) {
    // 读取属性
    const char *name = feature->GetFieldAsString("NAME");
    int pop = feature->GetFieldAsInteger("POPULATION");

    // 读取几何
    OGRGeometry *geom = feature->GetGeometryRef();
    if (geom != nullptr && wkbFlatten(geom->getGeometryType()) == wkbPoint) {
        OGRPoint *pt = (OGRPoint *)geom;
        double x = pt->getX();
        double y = pt->getY();
    }
    OGRFeature::DestroyFeature(feature);
}

GDALClose(ds);
```

### Python

```python
from osgeo import ogr

ds = ogr.Open("cities.shp", 0)  # 0 = 只读
if ds is None:
    raise RuntimeError("无法打开数据源")

layer = ds.GetLayer(0)

for feature in layer:
    # 读取属性
    name = feature.GetField("NAME")
    pop  = feature.GetField("POPULATION")

    # 读取几何
    geom = feature.GetGeometryRef()
    if geom is not None and geom.GetGeometryType() == ogr.wkbPoint:
        x = geom.GetX()
        y = geom.GetY()

ds = None
```

### Java

```java
import org.gdal.ogr.ogr;
import org.gdal.ogr.DataSource;
import org.gdal.ogr.Layer;
import org.gdal.ogr.Feature;
import org.gdal.ogr.Geometry;

ogr.RegisterAll();

DataSource ds = ogr.Open("cities.shp", false);  // false = 只读
if (ds == null) { throw new RuntimeException("无法打开数据源"); }

Layer layer = ds.GetLayer(0);

Feature feature;
while ((feature = layer.GetNextFeature()) != null) {
    // 读取属性
    String name = feature.GetFieldAsString("NAME");
    int pop = feature.GetFieldAsInteger("POPULATION");

    // 读取几何
    Geometry geom = feature.GetGeometryRef();
    if (geom != null && geom.GetGeometryType() == ogr.wkbPoint) {
        double x = geom.GetX(0);
        double y = geom.GetY(0);
    }
    feature.delete();
}

ds.delete();
```

### C#

```csharp
using OSGeo.OGR;

Ogr.RegisterAll();

DataSource ds = Ogr.Open("cities.shp", 0);  // 0 = 只读
if (ds == null) { throw new Exception("无法打开数据源"); }

Layer layer = ds.GetLayerByIndex(0);

Feature feature;
while ((feature = layer.GetNextFeature()) != null) {
    // 读取属性
    string name = feature.GetFieldAsString("NAME");
    int pop = feature.GetFieldAsInteger("POPULATION");

    // 读取几何
    Geometry geom = feature.GetGeometryRef();
    if (geom != null && geom.GetGeometryType() == wkbGeometryType.wkbPoint) {
        double x = geom.GetX(0);
        double y = geom.GetY(0);
    }
    feature.Dispose();
}

ds.Dispose();
```

---

## 矢量数据创建与写入

### C++

```cpp
#include "ogrsf_frmts.h"

GDALAllRegister();

GDALDriver *driver = GetGDALDriverManager()->GetDriverByName("ESRI Shapefile");
GDALDataset *ds = driver->Create("output.shp", 0, 0, 0, GDT_Unknown, nullptr);

// 创建图层
OGRSpatialReference srs;
srs.SetWellKnownGeogCS("WGS84");
OGRLayer *layer = ds->CreateLayer("output", &srs, wkbPoint, nullptr);

// 定义字段
OGRFieldDefn nameField("NAME", OFTString);
nameField.SetWidth(64);
layer->CreateField(&nameField);

OGRFieldDefn popField("POPULATION", OFTInteger);
layer->CreateField(&popField);

// 创建要素
OGRFeature *feature = OGRFeature::CreateFeature(layer->GetLayerDefn());
feature->SetField("NAME", "Beijing");
feature->SetField("POPULATION", 21540000);

OGRPoint pt;
pt.setX(116.4);
pt.setY(39.9);
feature->SetGeometry(&pt);

layer->CreateFeature(feature);
OGRFeature::DestroyFeature(feature);

GDALClose(ds);
```

### Python

```python
from osgeo import ogr, osr

driver = ogr.GetDriverByName("ESRI Shapefile")
ds = driver.CreateDataSource("output.shp")

# 创建图层
srs = osr.SpatialReference()
srs.SetWellKnownGeogCS("WGS84")
layer = ds.CreateLayer("output", srs, ogr.wkbPoint)

# 定义字段
layer.CreateField(ogr.FieldDefn("NAME", ogr.OFTString))
layer.CreateField(ogr.FieldDefn("POPULATION", ogr.OFTInteger))

# 创建要素
feature = ogr.Feature(layer.GetLayerDefn())
feature.SetField("NAME", "Beijing")
feature.SetField("POPULATION", 21540000)

pt = ogr.Geometry(ogr.wkbPoint)
pt.SetPoint_2D(0, 116.4, 39.9)
feature.SetGeometry(pt)

layer.CreateFeature(feature)
feature = None

ds = None
```

### Java

```java
import org.gdal.ogr.*;
import org.gdal.osr.SpatialReference;

ogr.RegisterAll();

Driver driver = ogr.GetDriverByName("ESRI Shapefile");
DataSource ds = driver.CreateDataSource("output.shp");

// 创建图层
SpatialReference srs = new SpatialReference();
srs.SetWellKnownGeogCS("WGS84");
Layer layer = ds.CreateLayer("output", srs, ogr.wkbPoint);

// 定义字段
FieldDefn nameField = new FieldDefn("NAME", ogr.OFTString);
nameField.SetWidth(64);
layer.CreateField(nameField);

FieldDefn popField = new FieldDefn("POPULATION", ogr.OFTInteger);
layer.CreateField(popField);

// 创建要素
Feature feature = new Feature(layer.GetLayerDefn());
feature.SetField("NAME", "Beijing");
feature.SetField("POPULATION", 21540000);

Geometry pt = new Geometry(ogr.wkbPoint);
pt.SetPoint_2D(0, 116.4, 39.9);
feature.SetGeometry(pt);

layer.CreateFeature(feature);
feature.delete();

ds.delete();
```

### C#

```csharp
using OSGeo.OGR;
using OSGeo.OSR;

Ogr.RegisterAll();

Driver driver = Ogr.GetDriverByName("ESRI Shapefile");
DataSource ds = driver.CreateDataSource("output.shp", null);

// 创建图层
SpatialReference srs = new SpatialReference("");
srs.SetWellKnownGeogCS("WGS84");
Layer layer = ds.CreateLayer("output", srs, wkbGeometryType.wkbPoint, null);

// 定义字段
FieldDefn nameField = new FieldDefn("NAME", FieldType.OFTString);
nameField.SetWidth(64);
layer.CreateField(nameField, 1);

FieldDefn popField = new FieldDefn("POPULATION", FieldType.OFTInteger);
layer.CreateField(popField, 1);

// 创建要素
Feature feature = new Feature(layer.GetLayerDefn());
feature.SetField("NAME", "Beijing");
feature.SetField("POPULATION", 21540000);

Geometry pt = new Geometry(wkbGeometryType.wkbPoint);
pt.SetPoint_2D(0, 116.4, 39.9);
feature.SetGeometry(pt);

layer.CreateFeature(feature);
feature.Dispose();

ds.Dispose();
```

---

## 矢量格式转换与空间过滤

### C++

```cpp
#include "ogrsf_frmts.h"

GDALAllRegister();

// Shapefile → GeoJSON
GDALDataset *srcDs = (GDALDataset *)GDALOpenEx("input.shp", GDAL_OF_VECTOR, nullptr, nullptr, nullptr);
GDALDriver *jsonDriver = GetGDALDriverManager()->GetDriverByName("GeoJSON");
GDALDataset *dstDs = jsonDriver->Create("output.geojson", 0, 0, 0, GDT_Unknown, nullptr);

OGRLayer *srcLayer = srcDs->GetLayer(0);

// 空间过滤（仅北京周边）
OGREnvelope env;
env.MinX = 116.0; env.MaxX = 117.0;
env.MinY = 39.5;  env.MaxY = 40.5;
srcLayer->SetSpatialFilterRect(env.MinX, env.MinY, env.MaxX, env.MaxY);

// 属性过滤
srcLayer->SetAttributeFilter("POPULATION > 1000000");

// 复制图层
OGRLayer *dstLayer = dstDs->CopyLayer(srcLayer, "filtered");

GDALClose(dstDs);
GDALClose(srcDs);
```

### Python

```python
from osgeo import ogr

# Shapefile → GeoJSON
src_ds = ogr.Open("input.shp")
src_layer = src_ds.GetLayer(0)

# 空间过滤
src_layer.SetSpatialFilterRect(116.0, 39.5, 117.0, 40.5)

# 属性过滤
src_layer.SetAttributeFilter("POPULATION > 1000000")

# 输出
json_driver = ogr.GetDriverByName("GeoJSON")
dst_ds = json_driver.CreateDataSource("output.geojson")
dst_ds.CopyLayer(src_layer, "filtered")

dst_ds = None
src_ds = None

# 或使用 gdal.VectorTranslate（更高级）
from osgeo import gdal

gdal.VectorTranslate(
    "output.geojson",
    "input.shp",
    format="GeoJSON",
    spatFilter=[116.0, 39.5, 117.0, 40.5],
    where="POPULATION > 1000000"
)
```

### Java

```java
import org.gdal.ogr.*;

ogr.RegisterAll();

// Shapefile → GeoJSON
DataSource srcDs = ogr.Open("input.shp", false);
Layer srcLayer = srcDs.GetLayer(0);

// 空间过滤
srcLayer.SetSpatialFilterRect(116.0, 39.5, 117.0, 40.5);

// 属性过滤
srcLayer.SetAttributeFilter("POPULATION > 1000000");

// 输出
Driver jsonDriver = ogr.GetDriverByName("GeoJSON");
DataSource dstDs = jsonDriver.CreateDataSource("output.geojson");
dstDs.CopyLayer(srcLayer, "filtered");

dstDs.delete();
srcDs.delete();
```

### C#

```csharp
using OSGeo.OGR;

Ogr.RegisterAll();

// Shapefile → GeoJSON
DataSource srcDs = Ogr.Open("input.shp", 0);
Layer srcLayer = srcDs.GetLayerByIndex(0);

// 空间过滤
srcLayer.SetSpatialFilterRect(116.0, 39.5, 117.0, 40.5);

// 属性过滤
srcLayer.SetAttributeFilter("POPULATION > 1000000");

// 输出
Driver jsonDriver = Ogr.GetDriverByName("GeoJSON");
DataSource dstDs = jsonDriver.CreateDataSource("output.geojson", null);
dstDs.CopyLayer(srcLayer, "filtered", null);

dstDs.Dispose();
srcDs.Dispose();
```

---

## 几何操作

### C++

```cpp
#include "ogr_geometry.h"

// 创建几何对象
OGRPoint pt(116.4, 39.9);

OGRLinearRing ring;
ring.addPoint(0, 0);
ring.addPoint(10, 0);
ring.addPoint(10, 10);
ring.addPoint(0, 10);
ring.closeRings();

OGRPolygon polygon;
polygon.addRing(&ring);

// WKT / WKB 互转
char *wkt = nullptr;
polygon.exportToWkt(&wkt);
CPLFree(wkt);

OGRGeometry *geomFromWkt = nullptr;
OGRGeometryFactory::createFromWkt("POINT(116.4 39.9)", nullptr, &geomFromWkt);
OGRGeometryFactory::destroyGeometry(geomFromWkt);

// 空间操作
OGRGeometry *buffer = pt.Buffer(1.0);           // 缓冲区
OGRGeometry *inter  = polygon.Intersection(&pt); // 交集
OGRGeometry *united = polygon.Union(&pt);         // 合并
double dist = polygon.Distance(&pt);              // 距离
bool contains = polygon.Contains(&pt);            // 包含判断
bool intersects = polygon.Intersects(&pt);        // 相交判断
double area = polygon.get_Area();                  // 面积
double length = polygon.get_Length();              // 周长

OGRGeometryFactory::destroyGeometry(buffer);
OGRGeometryFactory::destroyGeometry(inter);
OGRGeometryFactory::destroyGeometry(united);
```

### Python

```python
from osgeo import ogr

# 创建几何对象
pt = ogr.Geometry(ogr.wkbPoint)
pt.SetPoint_2D(0, 116.4, 39.9)

ring = ogr.Geometry(ogr.wkbLinearRing)
ring.AddPoint(0, 0)
ring.AddPoint(10, 0)
ring.AddPoint(10, 10)
ring.AddPoint(0, 10)
ring.CloseRings()

polygon = ogr.Geometry(ogr.wkbPolygon)
polygon.AddGeometry(ring)

# WKT / WKB 互转
wkt = polygon.ExportToWkt()
geom_from_wkt = ogr.CreateGeometryFromWkt("POINT(116.4 39.9)")
geom_from_json = ogr.CreateGeometryFromJson('{"type":"Point","coordinates":[116.4,39.9]}')

# 空间操作
buffer    = pt.Buffer(1.0)              # 缓冲区
inter     = polygon.Intersection(pt)     # 交集
united    = polygon.Union(pt)            # 合并
dist      = polygon.Distance(pt)         # 距离
contains  = polygon.Contains(pt)         # 包含判断
intersects = polygon.Intersects(pt)      # 相交判断
area      = polygon.GetArea()            # 面积
length    = polygon.Length()             # 周长
```

### Java

```java
import org.gdal.ogr.Geometry;
import org.gdal.ogr.ogr;

// 创建几何对象
Geometry pt = new Geometry(ogr.wkbPoint);
pt.SetPoint_2D(0, 116.4, 39.9);

Geometry ring = new Geometry(ogr.wkbLinearRing);
ring.AddPoint(0, 0, 0);
ring.AddPoint(10, 0, 0);
ring.AddPoint(10, 10, 0);
ring.AddPoint(0, 10, 0);
ring.CloseRings();

Geometry polygon = new Geometry(ogr.wkbPolygon);
polygon.AddGeometry(ring);

// WKT / WKB 互转
String wkt = polygon.ExportToWkt();
Geometry geomFromWkt = Geometry.CreateFromWkt("POINT(116.4 39.9)");

// 空间操作
Geometry buffer  = pt.Buffer(1.0);              // 缓冲区
Geometry inter   = polygon.Intersection(pt);     // 交集
Geometry united  = polygon.Union(pt);            // 合并
double dist      = polygon.Distance(pt);         // 距离
boolean contains = polygon.Contains(pt);         // 包含判断
boolean intersects = polygon.Intersects(pt);     // 相交判断
double area      = polygon.GetArea();            // 面积
```

### C#

```csharp
using OSGeo.OGR;

// 创建几何对象
Geometry pt = new Geometry(wkbGeometryType.wkbPoint);
pt.SetPoint_2D(0, 116.4, 39.9);

Geometry ring = new Geometry(wkbGeometryType.wkbLinearRing);
ring.AddPoint(0, 0, 0);
ring.AddPoint(10, 0, 0);
ring.AddPoint(10, 10, 0);
ring.AddPoint(0, 10, 0);
ring.CloseRings();

Geometry polygon = new Geometry(wkbGeometryType.wkbPolygon);
polygon.AddGeometry(ring);

// WKT / WKB 互转
string wkt;
polygon.ExportToWkt(out wkt);
Geometry geomFromWkt = Geometry.CreateFromWkt("POINT(116.4 39.9)");

// 空间操作
Geometry buffer  = pt.Buffer(1.0, 30);          // 缓冲区
Geometry inter   = polygon.Intersection(pt);     // 交集
Geometry united  = polygon.Union(pt);            // 合并
double dist      = polygon.Distance(pt);         // 距离
bool contains    = polygon.Contains(pt);         // 包含判断
bool intersects  = polygon.Intersects(pt);       // 相交判断
double area      = polygon.GetArea();            // 面积
```

---

## GeoPackage 读写

GeoPackage 是 OGC 标准的轻量级地理数据库格式，适合替代 Shapefile。

### C++

```cpp
#include "ogrsf_frmts.h"

GDALAllRegister();

// 创建 GeoPackage
GDALDriver *driver = GetGDALDriverManager()->GetDriverByName("GPKG");
GDALDataset *ds = driver->Create("data.gpkg", 0, 0, 0, GDT_Unknown, nullptr);

OGRSpatialReference srs;
srs.importFromEPSG(4326);
OGRLayer *layer = ds->CreateLayer("points", &srs, wkbPoint, nullptr);

OGRFieldDefn field("name", OFTString);
layer->CreateField(&field);

OGRFeature *f = OGRFeature::CreateFeature(layer->GetLayerDefn());
f->SetField("name", "TestPoint");
OGRPoint pt(116.4, 39.9);
f->SetGeometry(&pt);
layer->CreateFeature(f);
OGRFeature::DestroyFeature(f);

GDALClose(ds);

// 读取 GeoPackage
GDALDataset *readDs = (GDALDataset *)GDALOpenEx("data.gpkg", GDAL_OF_VECTOR, nullptr, nullptr, nullptr);
OGRLayer *readLayer = readDs->GetLayerByName("points");
readLayer->ResetReading();
OGRFeature *rf;
while ((rf = readLayer->GetNextFeature()) != nullptr) {
    printf("%s\n", rf->GetFieldAsString("name"));
    OGRFeature::DestroyFeature(rf);
}
GDALClose(readDs);
```

### Python

```python
from osgeo import ogr, osr

# 创建 GeoPackage
driver = ogr.GetDriverByName("GPKG")
ds = driver.CreateDataSource("data.gpkg")

srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)
layer = ds.CreateLayer("points", srs, ogr.wkbPoint)

layer.CreateField(ogr.FieldDefn("name", ogr.OFTString))

feature = ogr.Feature(layer.GetLayerDefn())
feature.SetField("name", "TestPoint")
pt = ogr.Geometry(ogr.wkbPoint)
pt.SetPoint_2D(0, 116.4, 39.9)
feature.SetGeometry(pt)
layer.CreateFeature(feature)

ds = None

# 读取 GeoPackage
ds = ogr.Open("data.gpkg")
layer = ds.GetLayerByName("points")
for f in layer:
    print(f.GetField("name"))
ds = None
```

### Java

```java
import org.gdal.ogr.*;
import org.gdal.osr.SpatialReference;

ogr.RegisterAll();

// 创建 GeoPackage
Driver driver = ogr.GetDriverByName("GPKG");
DataSource ds = driver.CreateDataSource("data.gpkg");

SpatialReference srs = new SpatialReference();
srs.ImportFromEPSG(4326);
Layer layer = ds.CreateLayer("points", srs, ogr.wkbPoint);

layer.CreateField(new FieldDefn("name", ogr.OFTString));

Feature feature = new Feature(layer.GetLayerDefn());
feature.SetField("name", "TestPoint");
Geometry pt = new Geometry(ogr.wkbPoint);
pt.SetPoint_2D(0, 116.4, 39.9);
feature.SetGeometry(pt);
layer.CreateFeature(feature);

ds.delete();

// 读取 GeoPackage
DataSource readDs = ogr.Open("data.gpkg", false);
Layer readLayer = readDs.GetLayerByName("points");
Feature f;
while ((f = readLayer.GetNextFeature()) != null) {
    System.out.println(f.GetFieldAsString("name"));
    f.delete();
}
readDs.delete();
```

### C#

```csharp
using OSGeo.OGR;
using OSGeo.OSR;

Ogr.RegisterAll();

// 创建 GeoPackage
Driver driver = Ogr.GetDriverByName("GPKG");
DataSource ds = driver.CreateDataSource("data.gpkg", null);

SpatialReference srs = new SpatialReference("");
srs.ImportFromEPSG(4326);
Layer layer = ds.CreateLayer("points", srs, wkbGeometryType.wkbPoint, null);

layer.CreateField(new FieldDefn("name", FieldType.OFTString), 1);

Feature feature = new Feature(layer.GetLayerDefn());
feature.SetField("name", "TestPoint");
Geometry pt = new Geometry(wkbGeometryType.wkbPoint);
pt.SetPoint_2D(0, 116.4, 39.9);
feature.SetGeometry(pt);
layer.CreateFeature(feature);

ds.Dispose();

// 读取 GeoPackage
DataSource readDs = Ogr.Open("data.gpkg", 0);
Layer readLayer = readDs.GetLayerByName("points");
Feature f;
while ((f = readLayer.GetNextFeature()) != null) {
    Console.WriteLine(f.GetFieldAsString("name"));
    f.Dispose();
}
readDs.Dispose();
```

---

## 常用矢量数据格式

| 驱动名 | 扩展名 | 说明 |
|---|---|---|
| `ESRI Shapefile` | `.shp` | ESRI Shapefile，经典矢量格式 |
| `GeoJSON` | `.geojson` | GeoJSON，Web 友好格式 |
| `GPKG` | `.gpkg` | GeoPackage，OGC 标准轻量数据库 |
| `PostgreSQL` / `PostGIS` | — | PostGIS 空间数据库 |
| `FlatGeobuf` | `.fgb` | 高性能流式二进制格式 |
| `GML` | `.gml` | OGC GML 格式 |
| `KML` | `.kml` | Google Earth 格式 |
| `CSV` | `.csv` | 逗号分隔值（配合 VRT 指定几何列） |
| `SQLite` | `.sqlite` | SQLite / SpatiaLite 数据库 |
| `XLSX` | `.xlsx` | Excel 表格（只读） |

---


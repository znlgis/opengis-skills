---
name: gdal-api
description: GDAL (Geospatial Data Abstraction Library) 是 OSGeo 基金会的核心开源地理数据处理库，提供 C++ 原生 API 以及基于 SWIG 的 Python、Java、C# 语言绑定，支持 200+ 种栅格与矢量数据格式的读写、坐标变换、栅格分析和矢量空间操作。本文件旨在帮助 AI 使用 GDAL API 进行地理空间数据编程开发。
---

> **项目地址：** <https://github.com/OSGeo/gdal>
>
> **API 总览文档：** <https://gdal.org/en/stable/api/index.html>
>
> **C/C++ API 参考：** <https://gdal.org/en/stable/api/index.html#c-api>
>
> **Python API 参考：** <https://gdal.org/en/stable/api/python/index.html>
>
> **Java API 参考：** <https://gdal.org/en/stable/api/java/index.html>
>
> **C# API 参考：** <https://gdal.org/en/stable/api/csharp/index.html>
>
> **许可证：** MIT License

## 概述

GDAL 是地理空间数据处理的事实标准库，由 OSGeo 基金会维护。它提供：

- **200+ 栅格驱动**：GeoTIFF、NetCDF、HDF5、COG、JPEG2000 等
- **100+ 矢量驱动**：Shapefile、GeoJSON、GeoPackage、PostGIS、FlatGeobuf 等
- **坐标参考系统**：基于 PROJ 的坐标变换与投影转换
- **栅格分析**：重采样、镶嵌、裁剪、波段运算、DEM 分析等
- **矢量操作**：空间过滤、属性查询、要素创建与编辑等

GDAL 核心以 C++ 实现，同时通过 SWIG 提供 **Python**、**Java**、**C#** 三种语言绑定，各语言 API 与 C++ 保持一致的类与方法命名。

---

## 环境准备

### C++ 环境

```bash
# Linux (Debian/Ubuntu)
apt-get install libgdal-dev

# macOS (Homebrew)
brew install gdal

# CMake 项目中链接 GDAL
# CMakeLists.txt
find_package(GDAL REQUIRED)
target_link_libraries(myapp PRIVATE GDAL::GDAL)
```

### Python 环境

```bash
# pip 安装（需系统已安装 GDAL 库）
pip install gdal

# Conda 安装（推荐，自动处理 C 库依赖）
conda install -c conda-forge gdal

# 验证
python -c "from osgeo import gdal; print(gdal.VersionInfo())"
```

### Java 环境

```xml
<!-- Maven 依赖 -->
<dependency>
    <groupId>org.gdal</groupId>
    <artifactId>gdal</artifactId>
    <version>3.10.0</version>
</dependency>
```

```groovy
// Gradle
implementation 'org.gdal:gdal:3.10.0'
```

**注意：** Java 绑定需要在系统 `PATH`（Windows）或 `LD_LIBRARY_PATH`（Linux）中找到 `gdalalljni` 本地库。

### C# 环境

```bash
# .NET Core / .NET 5+ 项目
dotnet add package MaxRev.Gdal.Core
dotnet add package MaxRev.Gdal.LinuxRuntime.Minimal   # Linux
dotnet add package MaxRev.Gdal.WindowsRuntime.Minimal  # Windows
```

**注意：** 官方 SWIG 绑定命名空间为 `OSGeo.GDAL`、`OSGeo.OGR`、`OSGeo.OSR`。NuGet 包 `MaxRev.Gdal.Core` 是社区维护的跨平台封装。

---

## 核心类一览

GDAL API 在四种语言中保持一致的类结构，下表列出核心类及其作用：

### 栅格 API 核心类

| 类 | C++ 头文件 / 模块 | 用途 |
|---|---|---|
| `GDALDriver` | `gdal_priv.h` / `osgeo.gdal` | 栅格驱动——注册格式、创建数据集 |
| `GDALDataset` | `gdal_priv.h` / `osgeo.gdal` | ★ 栅格数据集——打开、读写、获取元数据 |
| `GDALRasterBand` | `gdal_priv.h` / `osgeo.gdal` | 栅格波段——读写像素、获取统计信息 |
| `GDALColorTable` | `gdal_priv.h` / `osgeo.gdal` | 颜色表——索引颜色映射 |
| `GDALRasterAttributeTable` | `gdal_priv.h` / `osgeo.gdal` | 栅格属性表 |

### 矢量 API 核心类（OGR）

| 类 | C++ 头文件 / 模块 | 用途 |
|---|---|---|
| `OGRSFDriver` / `GDALDriver` | `ogrsf_frmts.h` / `osgeo.ogr` | 矢量驱动 |
| `GDALDataset` / `OGRDataSource` | `ogrsf_frmts.h` / `osgeo.ogr` | ★ 矢量数据源——管理图层集合 |
| `OGRLayer` | `ogrsf_frmts.h` / `osgeo.ogr` | ★ 矢量图层——读写要素、空间过滤 |
| `OGRFeature` | `ogr_feature.h` / `osgeo.ogr` | 矢量要素——属性 + 几何 |
| `OGRFeatureDefn` | `ogr_feature.h` / `osgeo.ogr` | 要素定义——字段结构 |
| `OGRFieldDefn` | `ogr_feature.h` / `osgeo.ogr` | 字段定义——名称、类型 |
| `OGRGeometry` | `ogr_geometry.h` / `osgeo.ogr` | 几何基类（Point、LineString、Polygon 等） |

### 空间参考类（OSR）

| 类 | C++ 头文件 / 模块 | 用途 |
|---|---|---|
| `OGRSpatialReference` | `ogr_spatialref.h` / `osgeo.osr` | ★ 空间参考系统——定义 CRS |
| `OGRCoordinateTransformation` | `ogr_spatialref.h` / `osgeo.osr` | ★ 坐标变换——在不同 CRS 间转换坐标 |

### 各语言模块 / 命名空间对照

| 功能域 | C++ | Python | Java | C# |
|---|---|---|---|---|
| 栅格 | `#include "gdal_priv.h"` | `from osgeo import gdal` | `import org.gdal.gdal.*` | `using OSGeo.GDAL;` |
| 矢量 | `#include "ogrsf_frmts.h"` | `from osgeo import ogr` | `import org.gdal.ogr.*` | `using OSGeo.OGR;` |
| 空间参考 | `#include "ogr_spatialref.h"` | `from osgeo import osr` | `import org.gdal.osr.*` | `using OSGeo.OSR;` |

---

## 栅格数据读取

### C++

```cpp
#include "gdal_priv.h"

GDALAllRegister();

GDALDataset *ds = (GDALDataset *)GDALOpen("dem.tif", GA_ReadOnly);
if (ds == nullptr) { /* 错误处理 */ }

// 基本信息
int width  = ds->GetRasterXSize();
int height = ds->GetRasterYSize();
int bands  = ds->GetRasterCount();

// 仿射变换参数 [左上X, 像素宽度, 旋转, 左上Y, 旋转, 像素高度(负)]
double gt[6];
ds->GetGeoTransform(gt);

// 投影信息
const char *proj = ds->GetProjectionRef();

// 读取第一个波段
GDALRasterBand *band = ds->GetRasterBand(1);
float *buf = new float[width * height];
band->RasterIO(GF_Read, 0, 0, width, height, buf, width, height, GDT_Float32, 0, 0);

// 获取 NoData 值
int hasNoData;
double nodata = band->GetNoDataValue(&hasNoData);

delete[] buf;
GDALClose(ds);
```

### Python

```python
from osgeo import gdal

ds = gdal.Open("dem.tif", gdal.GA_ReadOnly)
if ds is None:
    raise RuntimeError("无法打开文件")

# 基本信息
width  = ds.RasterXSize
height = ds.RasterYSize
bands  = ds.RasterCount

# 仿射变换参数
gt = ds.GetGeoTransform()

# 投影信息
proj = ds.GetProjection()

# 读取第一个波段为 NumPy 数组
band = ds.GetRasterBand(1)
data = band.ReadAsArray()  # numpy.ndarray

# 获取 NoData 值
nodata = band.GetNoDataValue()

ds = None  # 关闭数据集
```

### Java

```java
import org.gdal.gdal.gdal;
import org.gdal.gdal.Dataset;
import org.gdal.gdal.Band;
import org.gdal.gdalconst.gdalconstConstants;

gdal.AllRegister();

Dataset ds = gdal.Open("dem.tif", gdalconstConstants.GA_ReadOnly);
if (ds == null) { throw new RuntimeException("无法打开文件"); }

// 基本信息
int width  = ds.getRasterXSize();
int height = ds.getRasterYSize();
int bands  = ds.getRasterCount();

// 仿射变换参数
double[] gt = new double[6];
ds.GetGeoTransform(gt);

// 投影信息
String proj = ds.GetProjection();

// 读取第一个波段
Band band = ds.GetRasterBand(1);
float[] buf = new float[width * height];
band.ReadRaster(0, 0, width, height, buf);

// 获取 NoData 值
Double[] nodata = new Double[1];
band.GetNoDataValue(nodata);

ds.delete();
```

### C#

```csharp
using OSGeo.GDAL;

Gdal.AllRegister();

Dataset ds = Gdal.Open("dem.tif", Access.GA_ReadOnly);
if (ds == null) { throw new Exception("无法打开文件"); }

// 基本信息
int width  = ds.RasterXSize;
int height = ds.RasterYSize;
int bands  = ds.RasterCount;

// 仿射变换参数
double[] gt = new double[6];
ds.GetGeoTransform(gt);

// 投影信息
string proj = ds.GetProjection();

// 读取第一个波段
Band band = ds.GetRasterBand(1);
float[] buf = new float[width * height];
band.ReadRaster(0, 0, width, height, buf, width, height, 0, 0);

// 获取 NoData 值
double nodata;
int hasNoData;
band.GetNoDataValue(out nodata, out hasNoData);

ds.Dispose();
```

---

## 栅格数据创建与写入

### C++

```cpp
#include "gdal_priv.h"

GDALAllRegister();

GDALDriver *driver = GetGDALDriverManager()->GetDriverByName("GTiff");
GDALDataset *ds = driver->Create("output.tif", 256, 256, 1, GDT_Float32, nullptr);

// 设置仿射变换
double gt[6] = {116.0, 0.01, 0, 40.0, 0, -0.01};
ds->SetGeoTransform(gt);

// 设置投影
OGRSpatialReference srs;
srs.SetWellKnownGeogCS("WGS84");
char *wkt = nullptr;
srs.exportToWkt(&wkt);
ds->SetProjection(wkt);
CPLFree(wkt);

// 写入像素数据
GDALRasterBand *band = ds->GetRasterBand(1);
float *data = new float[256 * 256];
for (int i = 0; i < 256 * 256; i++) data[i] = (float)i;
band->RasterIO(GF_Write, 0, 0, 256, 256, data, 256, 256, GDT_Float32, 0, 0);
band->SetNoDataValue(-9999.0);

delete[] data;
GDALClose(ds);
```

### Python

```python
from osgeo import gdal, osr
import numpy as np

driver = gdal.GetDriverByName("GTiff")
ds = driver.Create("output.tif", 256, 256, 1, gdal.GDT_Float32)

# 设置仿射变换
ds.SetGeoTransform([116.0, 0.01, 0, 40.0, 0, -0.01])

# 设置投影
srs = osr.SpatialReference()
srs.SetWellKnownGeogCS("WGS84")
ds.SetProjection(srs.ExportToWkt())

# 写入 NumPy 数组
band = ds.GetRasterBand(1)
data = np.arange(256 * 256, dtype=np.float32).reshape(256, 256)
band.WriteArray(data)
band.SetNoDataValue(-9999.0)

ds.FlushCache()
ds = None
```

### Java

```java
import org.gdal.gdal.gdal;
import org.gdal.gdal.Dataset;
import org.gdal.gdal.Driver;
import org.gdal.gdal.Band;
import org.gdal.osr.SpatialReference;

gdal.AllRegister();

Driver driver = gdal.GetDriverByName("GTiff");
Dataset ds = driver.Create("output.tif", 256, 256, 1, org.gdal.gdalconst.gdalconstConstants.GDT_Float32);

// 设置仿射变换
ds.SetGeoTransform(new double[]{116.0, 0.01, 0, 40.0, 0, -0.01});

// 设置投影
SpatialReference srs = new SpatialReference();
srs.SetWellKnownGeogCS("WGS84");
ds.SetProjection(srs.ExportToWkt());

// 写入像素数据
Band band = ds.GetRasterBand(1);
float[] data = new float[256 * 256];
for (int i = 0; i < data.length; i++) data[i] = (float) i;
band.WriteRaster(0, 0, 256, 256, data);
band.SetNoDataValue(-9999.0);

ds.FlushCache();
ds.delete();
```

### C#

```csharp
using OSGeo.GDAL;
using OSGeo.OSR;

Gdal.AllRegister();

Driver driver = Gdal.GetDriverByName("GTiff");
Dataset ds = driver.Create("output.tif", 256, 256, 1, DataType.GDT_Float32, null);

// 设置仿射变换
ds.SetGeoTransform(new double[] { 116.0, 0.01, 0, 40.0, 0, -0.01 });

// 设置投影
SpatialReference srs = new SpatialReference("");
srs.SetWellKnownGeogCS("WGS84");
string wkt;
srs.ExportToWkt(out wkt);
ds.SetProjection(wkt);

// 写入像素数据
Band band = ds.GetRasterBand(1);
float[] data = new float[256 * 256];
for (int i = 0; i < data.Length; i++) data[i] = (float)i;
band.WriteRaster(0, 0, 256, 256, data, 256, 256, 0, 0);
band.SetNoDataValue(-9999.0);

ds.FlushCache();
ds.Dispose();
```

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

## 坐标参考系统与坐标变换

### C++

```cpp
#include "ogr_spatialref.h"

// 定义坐标系
OGRSpatialReference srcSRS, dstSRS;
srcSRS.SetWellKnownGeogCS("WGS84");        // EPSG:4326
dstSRS.importFromEPSG(3857);               // Web Mercator

// 创建坐标变换
OGRCoordinateTransformation *transform =
    OGRCreateCoordinateTransformation(&srcSRS, &dstSRS);

// 变换坐标
double x = 116.4, y = 39.9;
if (transform->Transform(1, &x, &y)) {
    // x, y 已变换为 EPSG:3857 坐标
}

OCTDestroyCoordinateTransformation(transform);
```

### Python

```python
from osgeo import osr

# 定义坐标系
src_srs = osr.SpatialReference()
src_srs.SetWellKnownGeogCS("WGS84")        # EPSG:4326

dst_srs = osr.SpatialReference()
dst_srs.ImportFromEPSG(3857)               # Web Mercator

# 创建坐标变换
transform = osr.CoordinateTransformation(src_srs, dst_srs)

# 变换坐标
x, y, z = transform.TransformPoint(116.4, 39.9)
```

### Java

```java
import org.gdal.osr.SpatialReference;
import org.gdal.osr.CoordinateTransformation;
import org.gdal.osr.osr;

// 定义坐标系
SpatialReference srcSRS = new SpatialReference();
srcSRS.SetWellKnownGeogCS("WGS84");        // EPSG:4326

SpatialReference dstSRS = new SpatialReference();
dstSRS.ImportFromEPSG(3857);               // Web Mercator

// 创建坐标变换
CoordinateTransformation transform =
    osr.CreateCoordinateTransformation(srcSRS, dstSRS);

// 变换坐标
double[] point = new double[]{116.4, 39.9, 0};
transform.TransformPoint(point);
// point[0], point[1] 已变换为 EPSG:3857 坐标
```

### C#

```csharp
using OSGeo.OSR;

// 定义坐标系
SpatialReference srcSRS = new SpatialReference("");
srcSRS.SetWellKnownGeogCS("WGS84");        // EPSG:4326

SpatialReference dstSRS = new SpatialReference("");
dstSRS.ImportFromEPSG(3857);               // Web Mercator

// 创建坐标变换
CoordinateTransformation transform =
    new CoordinateTransformation(srcSRS, dstSRS);

// 变换坐标
double[] point = new double[3] { 116.4, 39.9, 0 };
transform.TransformPoint(point);
// point[0], point[1] 已变换为 EPSG:3857 坐标
```

---

## 栅格格式转换与重投影

### C++

```cpp
#include "gdal_priv.h"
#include "gdalwarper.h"

GDALAllRegister();

// 格式转换（GeoTIFF → PNG）
GDALDataset *src = (GDALDataset *)GDALOpen("input.tif", GA_ReadOnly);
GDALDriver *pngDriver = GetGDALDriverManager()->GetDriverByName("PNG");
GDALDataset *dst = pngDriver->CreateCopy("output.png", src, FALSE, nullptr, nullptr, nullptr);
GDALClose(dst);
GDALClose(src);

// 重投影（Warp）
GDALDataset *srcDs = (GDALDataset *)GDALOpen("input.tif", GA_ReadOnly);
const char *dstWKT = nullptr;
OGRSpatialReference dstSRS;
dstSRS.importFromEPSG(3857);
dstSRS.exportToWkt(const_cast<char **>(&dstWKT));

GDALWarpOptions *warpOpts = GDALCreateWarpOptions();
warpOpts->hSrcDS = srcDs;
warpOpts->nBandCount = 1;
warpOpts->panSrcBands = (int *)CPLMalloc(sizeof(int));
warpOpts->panSrcBands[0] = 1;
warpOpts->panDstBands = (int *)CPLMalloc(sizeof(int));
warpOpts->panDstBands[0] = 1;

GDALDataset *dstDs = (GDALDataset *)GDALAutoCreateWarpedVRT(
    srcDs, nullptr, dstWKT, GRA_Bilinear, 0.0, nullptr);
GDALDriver *tiffDriver = GetGDALDriverManager()->GetDriverByName("GTiff");
GDALDataset *outDs = tiffDriver->CreateCopy("reprojected.tif", dstDs, FALSE, nullptr, nullptr, nullptr);

GDALClose(outDs);
GDALClose(dstDs);
GDALClose(srcDs);
```

### Python

```python
from osgeo import gdal

# 格式转换（GeoTIFF → PNG）
src = gdal.Open("input.tif")
gdal.GetDriverByName("PNG").CreateCopy("output.png", src)
src = None

# 重投影（Warp）
gdal.Warp(
    "reprojected.tif",
    "input.tif",
    dstSRS="EPSG:3857",
    resampleAlg="bilinear"
)

# 带更多参数的 Warp
gdal.Warp(
    "clipped.tif",
    "input.tif",
    dstSRS="EPSG:3857",
    outputBounds=[12000000, 4000000, 13000000, 5000000],
    xRes=100, yRes=100,
    resampleAlg="cubic",
    creationOptions=["COMPRESS=LZW", "TILED=YES"]
)
```

### Java

```java
import org.gdal.gdal.gdal;
import org.gdal.gdal.Dataset;
import org.gdal.gdal.Driver;
import org.gdal.gdal.WarpOptions;
import java.util.Vector;

gdal.AllRegister();

// 格式转换（GeoTIFF → PNG）
Dataset src = gdal.Open("input.tif");
Driver pngDriver = gdal.GetDriverByName("PNG");
Dataset dst = pngDriver.CreateCopy("output.png", src);
dst.delete();
src.delete();

// 重投影（Warp）
Dataset srcDs = gdal.Open("input.tif");
Vector<String> options = new Vector<>();
options.add("-t_srs");
options.add("EPSG:3857");
options.add("-r");
options.add("bilinear");

WarpOptions warpOpts = new WarpOptions(options);
Dataset[] srcArray = new Dataset[]{srcDs};
Dataset dstDs = gdal.Warp("reprojected.tif", srcArray, warpOpts);
dstDs.delete();
srcDs.delete();
```

### C#

```csharp
using OSGeo.GDAL;

Gdal.AllRegister();

// 格式转换（GeoTIFF → PNG）
Dataset src = Gdal.Open("input.tif", Access.GA_ReadOnly);
Driver pngDriver = Gdal.GetDriverByName("PNG");
Dataset dst = pngDriver.CreateCopy("output.png", src, 0, null, null, null);
dst.Dispose();
src.Dispose();

// 重投影（Warp）
Dataset srcDs = Gdal.Open("input.tif", Access.GA_ReadOnly);
string[] warpArgs = new string[] {
    "-t_srs", "EPSG:3857",
    "-r", "bilinear"
};
GDALWarpAppOptions warpOpts = new GDALWarpAppOptions(warpArgs);
Dataset dstDs = Gdal.Warp("reprojected.tif", new Dataset[] { srcDs }, warpOpts, null, null);
dstDs.Dispose();
srcDs.Dispose();
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

## 常用栅格数据格式与创建选项

| 驱动名 | 扩展名 | 说明 | 常用创建选项 |
|---|---|---|---|
| `GTiff` | `.tif` | GeoTIFF，最常用的栅格格式 | `COMPRESS=LZW/DEFLATE/ZSTD`、`TILED=YES`、`BLOCKXSIZE=256` |
| `COG` | `.tif` | Cloud Optimized GeoTIFF | `COMPRESS=DEFLATE`、`OVERVIEW_RESAMPLING=CUBIC` |
| `PNG` | `.png` | PNG 图片 | `ZLEVEL=6` |
| `JPEG` | `.jpg` | JPEG 图片 | `QUALITY=85` |
| `GPKG` | `.gpkg` | GeoPackage 栅格 | `TILE_FORMAT=PNG/JPEG/WEBP` |
| `netCDF` | `.nc` | NetCDF 科学数据格式 | `FORMAT=NC4`、`COMPRESS=DEFLATE` |
| `HFA` | `.img` | Erdas Imagine | — |
| `VRT` | `.vrt` | 虚拟数据集（XML 引用） | — |

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

## 典型应用场景

| 场景 | C++ | Python | Java | C# |
|---|---|---|---|---|
| 读取栅格元数据 | `GDALOpen` + `GetGeoTransform` | `gdal.Open` + `GetGeoTransform` | `gdal.Open` + `GetGeoTransform` | `Gdal.Open` + `GetGeoTransform` |
| 栅格格式转换 | `CreateCopy` | `gdal.Translate` | `gdal.Translate` | `Gdal.wrapper_GDALTranslate` |
| 栅格重投影 | `GDALAutoCreateWarpedVRT` | `gdal.Warp` | `gdal.Warp` | `Gdal.Warp` |
| 读取矢量要素 | `GDALOpenEx` + `GetNextFeature` | `ogr.Open` + 迭代 | `ogr.Open` + `GetNextFeature` | `Ogr.Open` + `GetNextFeature` |
| 矢量格式转换 | `CopyLayer` / `CreateFeature` | `gdal.VectorTranslate` | `ogr.CopyLayer` | `Ogr.CopyLayer` |
| 坐标变换 | `OGRCreateCoordinateTransformation` | `osr.CoordinateTransformation` | `osr.CreateCoordinateTransformation` | `new CoordinateTransformation` |
| 创建缓冲区 | `OGRGeometry::Buffer` | `geom.Buffer` | `geom.Buffer` | `geom.Buffer` |
| 空间查询 | `SetSpatialFilterRect` | `SetSpatialFilterRect` | `SetSpatialFilterRect` | `SetSpatialFilterRect` |
| SQL 查询 | `ExecuteSQL` | `ExecuteSQL` | `ExecuteSQL` | `ExecuteSQL` |
| 波段运算 | `RasterIO` 手动计算 | `gdal_calc.py` / NumPy | `RasterIO` 手动计算 | `RasterIO` 手动计算 |

---

## 常见注意事项

### 通用注意事项

1. **驱动注册**：使用任何 GDAL 功能前，必须调用注册函数。C++ 和 Python 使用 `GDALAllRegister()`，Java 使用 `gdal.AllRegister()`，C# 使用 `Gdal.AllRegister()`。矢量操作还需 `OGRRegisterAll()` / `ogr.RegisterAll()`。
2. **资源释放**：C++ 使用 `GDALClose()` / `OGRFeature::DestroyFeature()`；Python 赋值 `None` 触发释放；Java 调用 `.delete()`；C# 调用 `.Dispose()`。未释放资源可能导致文件损坏。
3. **坐标轴顺序**：GDAL 3.0+ 默认遵循 EPSG 规范（纬度在前），可通过 `OGRSpatialReference::SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER)` 强制经度在前。
4. **线程安全**：GDAL 全局状态非线程安全，多线程环境需注意：每个线程使用独立的 `GDALDataset`；避免并发写入同一数据集。
5. **大文件处理**：对大型栅格使用分块读写（`RasterIO` 指定窗口），避免一次性读取整个影像到内存。
6. **错误处理**：使用 `CPLGetLastErrorMsg()`（C++）、`gdal.GetLastErrorMsg()`（Python）获取详细错误信息。

### C++ 特有注意事项

7. **内存管理**：使用 `CPLFree()` 释放 GDAL 分配的 C 字符串（如 `exportToWkt` 返回的 WKT）。几何对象使用 `OGRGeometryFactory::destroyGeometry()` 销毁。
8. **编译链接**：确保使用 `gdal-config --cflags --libs` 或 CMake `find_package(GDAL)` 正确配置编译参数。

### Python 特有注意事项

9. **异常模式**：默认 GDAL Python 不抛出异常。启用异常模式：`gdal.UseExceptions()`（推荐在脚本开头调用）。
10. **NumPy 集成**：`band.ReadAsArray()` 直接返回 NumPy 数组，`band.WriteArray(array)` 直接写入，是 Python 最大的便利之一。

### Java 特有注意事项

11. **本地库加载**：必须确保 `gdalalljni`（Linux: `libgdalalljni.so`，Windows: `gdalalljni.dll`）在 `java.library.path` 中。
12. **Vector 参数**：Java 绑定中许多方法使用 `java.util.Vector<String>` 传递选项参数。

### C# 特有注意事项

13. **平台运行时**：需要根据目标平台引入对应的 NuGet 运行时包（Linux / Windows / macOS），否则本地库加载失败。
14. **字符串编码**：C# 绑定中字符串参数默认使用 UTF-8 编码，处理中文路径时注意编码一致性。

---

## 参考链接

- **GitHub 仓库：** <https://github.com/OSGeo/gdal>
- **API 总览：** <https://gdal.org/en/stable/api/index.html>
- **C/C++ API 文档：** <https://gdal.org/en/stable/api/index.html#c-api>
- **Python API 文档：** <https://gdal.org/en/stable/api/python/index.html>
- **Python 绑定说明：** <https://gdal.org/en/stable/api/python/python_bindings.html>
- **Java API 文档：** <https://gdal.org/en/stable/api/java/index.html>
- **C# API 文档：** <https://gdal.org/en/stable/api/csharp/index.html>
- **SWIG 绑定源码：** <https://github.com/OSGeo/gdal/tree/master/swig>
- **官方文档首页：** <https://gdal.org/en/stable/>
- **GDAL 教程：** <https://gdal.org/en/stable/tutorials/index.html>
- **驱动格式列表：** <https://gdal.org/en/stable/drivers/index.html>
- **问题追踪：** <https://github.com/OSGeo/gdal/issues>

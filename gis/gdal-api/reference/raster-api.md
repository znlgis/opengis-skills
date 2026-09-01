# GDAL Python Raster API Reference

Raster read/write, format conversion and reprojection details split from SKILL.md.

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


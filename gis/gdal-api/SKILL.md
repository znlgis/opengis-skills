---
name: gdal-api
description: "Use when programming against GDAL/OGR in C, C++, Python, or .NET for raster/vector I/O, coordinate transformation, or custom geospatial algorithms. GDAL API: low-level programming interface for reading/writing 70+ geospatial formats."

tags:
  - gdal
  - api
  - python
  - cpp
  - dotnet
  - java
  - raster
  - vector
  - gis
  - geospatial
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
> **许可证：** MIT

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
pip install GDAL

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
    <version><!-- 请查看 Maven Central 获取最新版：https://central.sonatype.com/artifact/org.gdal/gdal --></version>
</dependency>
```

```groovy
// Gradle
implementation 'org.gdal:gdal:3.13.1'
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

> 栅格数据读取与创建写入的完整 API 与代码示例见 [reference/raster-api.md](reference/raster-api.md)
> 矢量数据读取与创建写入的完整 API 与代码示例见 [reference/vector-api.md](reference/vector-api.md)

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

> 栅格格式转换与重投影的完整示例见 [reference/raster-api.md](reference/raster-api.md)
> 矢量格式转换、空间过滤、几何操作与 GeoPackage 读写的完整示例见 [reference/vector-api.md](reference/vector-api.md)
> 常用栅格数据格式与创建选项详见 [reference/raster-api.md](reference/raster-api.md)
> 常用矢量数据格式详见 [reference/vector-api.md](reference/vector-api.md)

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

## AI 使用建议

### 推荐工作流

1. **语言选择**：Python 优先（NumPy 集成、语法简洁），性能敏感用 C++，.NET 项目用 C#，Java 项目用 Java
2. **驱动注册**：任何 GDAL 操作前先调用注册函数（C++: `GDALAllRegister()`, Python 默认已注册）
3. **探索数据**：先 `gdalinfo`/`ogrinfo` 命令行查数据结构，再编写 API 代码
4. **异常处理**：Python 脚本开头加 `gdal.UseExceptions()` 启用异常模式
5. **分块读写**：大栅格使用 `RasterIO` 指定窗口，避免全量加载到内存

### 关键注意事项

- **资源释放**：C++ 用 `GDALClose()`，Python 赋值 `None`，Java 用 `.delete()`，C# 用 `.Dispose()`
- **坐标轴顺序**：GDAL 3.0+ 默认纬度在前，可用 `SetAxisMappingStrategy` 切换
- **Python NumPy 集成**：`ReadAsArray()` 直接返回 NumPy 数组，是 Python 最大优势
- **CS 平台依赖**：C# 需安装对应平台运行时包（Linux/Windows）
- **JA 本地库**：Java 需确保 `gdalalljni` 在 `java.library.path` 中

### 各语言适用场景

| 场景 | Python | C++ | Java | C# |
|------|--------|-----|------|-----|
| 数据处理脚本 | ★ 首选 | | | |
| 生产级服务 | | ★ 首选 | ★ | ★ |
| GIS 桌面插件 | ★ | | | |
| .NET 企业应用 | | | | ★ |
| Android GIS | | | ★ | |
| 嵌入式系统 | | ★ | | |

## 相关技能

- **gdal** — GDAL 命令行工具：[../gdal/SKILL.md](../gdal/SKILL.md)
- **jts** — Java 几何引擎（比 OGR 几何更丰富）：[../jts/SKILL.md](../jts/SKILL.md)
- **pyqgis** — QGIS Python 开发（内部使用 GDAL）：[../pyqgis/SKILL.md](../pyqgis/SKILL.md)
- **postgis** — PostgreSQL 空间数据库（与 GDAL 配合导入导出）：[../postgis/SKILL.md](../postgis/SKILL.md)
- **opengis-all** — 一站式 GIS 全流程：[../opengis-all/SKILL.md](../opengis-all/SKILL.md)

## 参考资源

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

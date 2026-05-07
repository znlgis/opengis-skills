---
name: sharpmap
description: SharpMap 是.NET 平台上的开源地图渲染引擎，支持 WinForms / WPF / ASP.NET / WMS 等多种宿主，提供矢量与栅格数据访问、样式渲染、坐标变换、专题图与图例输出能力，适合构建 .NET 桌面/Web GIS 应用。
tags:
  - dotnet
  - csharp
  - map
  - rendering
  - wms
  - shapefile
  - postgis
  - winforms
---

> **项目地址：** <https://github.com/SharpMap/SharpMap>
>
> **官方 Wiki：** <https://github.com/SharpMap/SharpMap/wiki>
>
> **NuGet：** `SharpMap`、`SharpMap.UI.WinForms`
>
> **许可证：** LGPL-2.1

## 概述

SharpMap 提供：

- **数据源**：Shapefile、PostGIS、SQL Server Spatial、Oracle Spatial、SQLite/SpatiaLite、WMS、WFS、TileSource（OSM/Bing）
- **图层模型**：`VectorLayer`、`LabelLayer`、`TileLayer`、`WmsLayer`
- **样式**：`VectorStyle`、`LabelStyle`、按属性主题样式
- **坐标变换**：通过 `ProjNet`
- **几何**：基于 NetTopologySuite
- **渲染**：System.Drawing 位图 / WMS 服务输出
- **UI 控件**：WinForms `MapBox`

> **注意**：SharpMap 主要面向 .NET Framework / 较旧 .NET，新项目建议改用 Mapsui。

---

## 安装

```bash
dotnet add package SharpMap
dotnet add package SharpMap.UI.WinForms
dotnet add package SharpMap.Extensions
dotnet add package ProjNet
```

---

## 核心对象

| 类型 | 说明 |
|------|------|
| `Map` | 地图 |
| `ILayer` / `VectorLayer` / `LabelLayer` / `TileLayer` | 图层 |
| `IProvider` | 数据提供者 |
| `VectorStyle` / `LabelStyle` | 样式 |

---

## WinForms 入门

```csharp
using SharpMap;
using SharpMap.Layers;
using SharpMap.Data.Providers;
using SharpMap.Styles;
using System.Drawing;

var map = new Map(new Size(800, 600));

var prov = new ShapeFile("countries.shp", true);
var layer = new VectorLayer("countries", prov)
{
    Style = new VectorStyle {
        Fill = new SolidBrush(Color.LightGreen),
        Outline = Pens.Black,
        EnableOutline = true
    }
};
map.Layers.Add(layer);

var labels = new LabelLayer("labels") {
    DataSource = prov,
    LabelColumn = "NAME",
    Style = new LabelStyle { Font = new Font("Arial", 10) }
};
map.Layers.Add(labels);

map.ZoomToExtents();
mapBox1.Map = map;
mapBox1.Refresh();
```

---

## PostGIS 数据源

```csharp
var conn = "Host=localhost;Database=gisdb;User Id=postgres;Password=pg";
var prov = new PostGIS(conn, "poi", "geom", "id");
map.Layers.Add(new VectorLayer("poi", prov));
```

---

## OSM 瓦片底图

```csharp
using BruTile.Predefined;
var src = KnownTileSources.Create(KnownTileSource.OpenStreetMap);
map.Layers.Add(new TileAsyncLayer(src, "OSM"));
map.SRID = 3857;
```

---

## 主题样式

```csharp
using SharpMap.Rendering.Thematics;

var theme = new CustomTheme(row => {
    var pop = (int)row["POP"];
    return new VectorStyle {
        Fill = new SolidBrush(pop > 1_000_000 ? Color.Red : Color.Blue)
    };
});
layer.Theme = theme;
```

---

## 坐标变换

```csharp
using ProjNet.CoordinateSystems;
using ProjNet.CoordinateSystems.Transformations;

var ctf = new CoordinateTransformationFactory();
layer.CoordinateTransformation = ctf.CreateFromCoordinateSystems(
    GeographicCoordinateSystem.WGS84,
    ProjectedCoordinateSystem.WebMercator);
map.SRID = 3857;
```

---

## 输出图像与 WMS

```csharp
using var img = map.GetMap();
img.Save("map.png");

// ASP.NET WMS
public void ProcessRequest(HttpContext ctx)
{
    var map = MapHelper.InitializeMap();
    SharpMap.Web.Wms.WmsServer.ProcessRequest(ctx, map);
}
```

---

## 拾取与查询

```csharp
mapBox1.MouseDown += (s, e) => {
    var pt = mapBox1.Map.ImageToWorld(new PointF(e.X, e.Y));
    var ds = new SharpMap.Data.FeatureDataSet();
    layer.DataSource.ExecuteIntersectionQuery(
        new NetTopologySuite.Geometries.Envelope(pt.X-1e-3, pt.X+1e-3,
                                                 pt.Y-1e-3, pt.Y+1e-3), ds);
    foreach (FeatureDataRow row in ds.Tables[0].Rows)
        Console.WriteLine(row["NAME"]);
};
```

---

## 性能建议

1. 预建空间索引（Shapefile `.qix`、PostGIS GiST）
2. `TileAsyncLayer` 用于在线底图
3. 避免主线程加载大数据
4. `LabelLayer` 启用优先级与碰撞检测
5. 复用 `Brush/Pen/VectorStyle`

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 无图 | 检查 SRID、`ZoomToExtents` |
| 文字模糊 | 设置高 DPI Aware、`MapBox.MapTransform` |
| GDI+ 内存泄漏 | 释放 `Brush/Pen/Bitmap` |
| Shapefile 中文乱码 | `new ShapeFile(path, true, false, Encoding.UTF8)` |

---

## AI 使用建议

### 推荐工作流

1. **创建 Map**：`new Map(new Size(width, height))` → 设置 SRID
2. **添加数据源**：`ShapeFile(path)` / `PostGIS(conn, table, geomCol, idCol)` 等方式连接数据
3. **创建图层**：`VectorLayer(name, provider)` 并设置 `Style`；按需添加 `LabelLayer`
4. **添加底图**：`TileAsyncLayer` + `BruTile` 加载 OSM 在线底图
5. **渲染输出**：`map.GetMap()` 获取 `Image` 对象 → 保存为 PNG 或通过 ASP.NET WMS 发布

### 关键注意事项

- **新项目建议 Mapsui**：SharpMap 主要面向 .NET Framework，新项目推荐使用 Mapsui（更活跃、跨平台更好）
- **SRID 一致性**：图层与地图 SRID 必须一致，必要时通过 `CoordinateTransformation` 转换
- **空间索引**：Shapefile 需预建 `.qix` 索引，PostGIS 用 GiST 索引加速查询
- **资源释放**：GDI+ `Brush`/`Pen`/`Bitmap` 需及时释放避免内存泄漏
- **Shapefile 编码**：中文数据需指定 `Encoding.UTF8` 或 `Encoding.GetEncoding("GBK")`

## 典型工作流

### 工作流 1：Shapefile 渲染 + 主题样式 + 输出图片

```csharp
using SharpMap;
using SharpMap.Layers;
using SharpMap.Data.Providers;
using SharpMap.Styles;
using SharpMap.Rendering.Thematics;
using System.Drawing;

// 创建地图
var map = new Map(new Size(1024, 768));
map.SRID = 4326;

// 添加 Shapefile 图层
var prov = new ShapeFile("countries.shp", true);
var layer = new VectorLayer("Countries", prov)
{
    Style = new VectorStyle
    {
        Fill = Brushes.LightGreen,
        Outline = Pens.Black,
        EnableOutline = true
    }
};

// 按人口设置主题样式
layer.Theme = new CustomTheme(row =>
{
    var pop = (int)row["POP_EST"];
    return new VectorStyle
    {
        Fill = new SolidBrush(pop > 100_000_000 ? Color.Red : Color.LightBlue)
    };
});
map.Layers.Add(layer);

// 添加行政标注
var labels = new LabelLayer("Labels")
{
    DataSource = prov, LabelColumn = "NAME",
    Style = new LabelStyle { Font = new Font("Arial", 10) }
};
map.Layers.Add(labels);

// 渲染
map.ZoomToExtents();
using var img = map.GetMap();
img.Save("output.png");
```

### 工作流 2：PostGIS 数据 + OSM 底图 + WMS 发布

```csharp
// PostGIS 数据
var pgConn = "Host=localhost;Database=gisdb;User Id=postgres;Password=pg";
var poiProvider = new PostGIS(pgConn, "poi", "geom", "id");
map.Layers.Add(new VectorLayer("POI", poiProvider)
{
    Style = new VectorStyle { Fill = Brushes.OrangeRed }
});

// OSM 底图
using BruTile.Predefined;
var tileSrc = KnownTileSources.Create(KnownTileSource.OpenStreetMap);
map.Layers.Add(new TileAsyncLayer(tileSrc, "OSM"));
map.SRID = 3857;
```

## 相关技能

- **mapsui** — .NET 现代跨平台地图组件（推荐替代）：[../mapsui/SKILL.md](../mapsui/SKILL.md)
- **nettopologysuite** — .NET 几何计算核心：[../nettopologysuite/SKILL.md](../nettopologysuite/SKILL.md)
- **openlayers** — Web 二维地图库：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **postgis** — 空间数据库：[../postgis/SKILL.md](../postgis/SKILL.md)

## 参考资源

- Wiki：<https://github.com/SharpMap/SharpMap/wiki>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/sharpmap/>

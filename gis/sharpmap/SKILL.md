---
name: sharpmap
description: SharpMap 是.NET 平台上的开源地图渲染引擎，支持 WinForms / WPF / ASP.NET / WMS 等多种宿主，提供矢量与栅格数据访问、样式渲染、坐标变换、专题图与图例输出能力，适合构建 .NET 桌面/Web GIS 应用。
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

## 参考资源

- Wiki：<https://github.com/SharpMap/SharpMap/wiki>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/sharpmap/>

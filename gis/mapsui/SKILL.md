---
name: mapsui
description: "Use when embedding interactive 2D maps in .NET desktop (WPF/WinUI/WinForms) or mobile (MAUI/Avalonia/Blazor) apps with Mapsui 5.1.0 (net8.0/net9.0) — Mapsui.Wpf/Mapsui.Maui packages, Map and Layers, OpenStreetMap.CreateTileLayer, Shapefile/GeoJSON via Mapsui.Nts, SphericalMercator.FromLonLat, or fixing a blank MapControl."
tags:
  - dotnet
  - csharp
  - map
  - wpf
  - maui
  - avalonia
  - blazor
  - skia
  - wms
  - tiles
---

> **项目地址：** <https://github.com/Mapsui/Mapsui>
>
> **官方文档：** <https://mapsui.com/v5/documentation/index.html>
>
> **最新版本：** 5.1.0（截至 2026-10，NuGet 稳定版；5.2.0-beta.1 为预发布）
>
> **许可证：** MIT

## 概述

- 跨 UI 框架：WPF / WinUI / MAUI / Avalonia / Uno / Blazor / WinForms
- SkiaSharp 渲染，性能优于 GDI+
- 数据源：OSM / WMS / WMTS / TMS / XYZ / Shapefile / GeoJSON / MBTiles / PostGIS
- 几何基于 NetTopologySuite
- 投影：`ProjNet` / `Mapsui.Projections`
- 内置交互：拖动、缩放、旋转、捏合、命中

---

## 安装

```bash
dotnet add package Mapsui.Wpf            # 或 Mapsui.Maui / Mapsui.Avalonia / ...
dotnet add package Mapsui.Tiling
dotnet add package Mapsui.Nts
```

---

## WPF 入门

```xml
<Window xmlns:mapsui="clr-namespace:Mapsui.UI.Wpf;assembly=Mapsui.UI.Wpf">
    <mapsui:MapControl x:Name="MapControl"/>
</Window>
```

```csharp
using Mapsui;
using Mapsui.Tiling;
using Mapsui.Projections;

var map = new Map();
map.Layers.Add(OpenStreetMap.CreateTileLayer());

var pt = SphericalMercator.FromLonLat(116.397, 39.908).ToMPoint();
map.Navigator.CenterOnAndZoomTo(pt, map.Navigator.Resolutions[10]);

MapControl.Map = map;
```

---

## 核心概念

| 类型 | 说明 |
|------|------|
| `Map` | 地图 |
| `Layer` / `MemoryLayer` / `ImageLayer` / `TileLayer` | 图层 |
| `IProvider` | 数据提供者 |
| `IFeature` / `GeometryFeature` | 要素（NTS 几何） |
| `IStyle` / `VectorStyle` / `LabelStyle` / `SymbolStyle` | 样式 |
| `Navigator` | 视图操作 |

---

## 矢量图层

```csharp
using Mapsui.Nts;
using Mapsui.Styles;

var features = new List<IFeature>();
foreach (var f in geoJsonFeatures)
    features.Add(new GeometryFeature(f.Geometry) {
        Styles = { new VectorStyle {
            Fill = new Brush(Color.Red),
            Outline = new Pen(Color.Black, 1)
        }}
    });

map.Layers.Add(new MemoryLayer("Roads") { Features = features, Style = null });
```

---

## Shapefile

```csharp
using Mapsui.Nts.Providers.Shapefile;
var prov = new ShapeFile("china.shp", true);
map.Layers.Add(new Layer("China") { DataSource = prov });
```

---

## 瓦片图层

```csharp
map.Layers.Add(OpenStreetMap.CreateTileLayer());

var src = new HttpTileSource(
    new GlobalSphericalMercator(0, 18),
    "https://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
    name: "AMap");
map.Layers.Add(new TileLayer(src) { Name = "AMap" });

// MBTiles
var mb = new MbTilesTileSource(new SQLiteConnectionString("city.mbtiles", false));
map.Layers.Add(new TileLayer(mb));
```

---

## WMS

```csharp
using Mapsui.Providers.Wms;
var wms = new WmsProvider("https://demo.mapserver.org/cgi-bin/wms?",
    new[] { "continents" });
map.Layers.Add(new ImageLayer("WMS") { DataSource = wms });
```

---

## 样式

```csharp
new SymbolStyle { SymbolScale = 0.7, Fill = new Brush(Color.Red) };

new LabelStyle {
    Text = "{name}",
    Font = new Font { Size = 14 },
    BackColor = new Brush(Color.WhiteSmoke),
    Halo = new Pen(Color.White, 2)
};
```

---

## 主题样式

```csharp
public class PopulationStyle : IThemeStyle {
    public IStyle? GetStyle(IFeature f) {
        var pop = (int)f["population"];
        return new VectorStyle { Fill = new Brush(pop > 1_000_000 ? Color.Red : Color.Blue) };
    }
}
layer.Style = new PopulationStyle();
```

---

## 交互

```csharp
MapControl.Info += (s, e) => {
    if (e.MapInfo?.Feature is GeometryFeature gf)
        Debug.WriteLine($"clicked {gf["name"]}");
};
```

---

## 性能优化

1. 海量点 → `RasterizingTileLayer` 包一层（按瓦片预渲染）
2. 优先 `MemoryLayer` + 缓存 Feature
3. 异步加载 + `await Layer.WaitForFinishedRefresh()`
4. 共享 Brush/Pen/Style 实例
5. SkiaSharp 关闭抗锯齿对极小符号有性能提升

---

## 常见问题

| 问题 | 解决 |
|------|------|
| WPF 无图 | NuGet 缺 `Mapsui.Wpf` 或没设置 `MapControl.Map` |
| 找不到 `Mapsui.UI.Wpf` 包 | NuGet 包名为 `Mapsui.Wpf`（v3 起启用该名称；程序集仍为 `Mapsui.UI.Wpf.dll`） |
| 投影错误 | `SphericalMercator.FromLonLat` 转换 |
| MAUI 空白 | `MauiProgram` 中 `UseSkiaSharp()` + `UseMapsui()` |
| Shapefile 中文乱码 | 指定 Encoding |
| `GeometryFeature` / 瓦片类型找不到 | 矢量要素需安装 `Mapsui.Nts`，瓦片图层需安装 `Mapsui.Tiling` |

---

## 典型工作流

### 工作流 1：加载底图 + GeoJSON 矢量数据

```csharp
using Mapsui;
using Mapsui.Tiling;
using Mapsui.Nts;
using Mapsui.Styles;
using NetTopologySuite.IO;

var map = new Map();

// 1. 添加 OSM 底图
map.Layers.Add(OpenStreetMap.CreateTileLayer());

// 2. 读取 GeoJSON 并添加为矢量图层
var gjReader = new GeoJsonReader();
var features = new List<IFeature>();
foreach (var f in geojsonFeatures)
{
    features.Add(new GeometryFeature(f.Geometry)
    {
        Styles = { new VectorStyle { Fill = new Brush(Color.Red) } }
    });
}
map.Layers.Add(new MemoryLayer("Data") { Features = features });

// 3. 定位
var center = SphericalMercator.FromLonLat(116.4, 39.9).ToMPoint();
map.Navigator.CenterOnAndZoomTo(center, map.Navigator.Resolutions[10]);

MapControl.Map = map;
```

### 工作流 2：Shapefile + WMS 叠加

```csharp
// Shapefile 图层
var shpProvider = new ShapeFile("china.shp", true);
map.Layers.Add(new Layer("China") { DataSource = shpProvider });

// WMS 图层（叠加）
var wmsProvider = new WmsProvider("https://geo.example.com/wms?", new[] { "rivers" });
map.Layers.Add(new ImageLayer("Rivers") { DataSource = wmsProvider });

map.ZoomToExtents();
```

## DeepSeek Harness 使用建议

- **加载与引用**：用 `skill("mapsui")` 加载（用户也可输入 `/mapsui`）；示例写入会话工作区的 .NET 工程，技能目录只读。
- **执行环境**：先 `dotnet --list-sdks`；Mapsui 5.1.0 的目标框架是 net8.0/net9.0（`Mapsui.Wpf` 为 net8.0-windows/net9.0-windows），低于 .NET 8 的工程不能直接引用。命令交给 `pwsh`，例如 `dotnet add package Mapsui.Wpf --version 5.1.0`。
- **验证产物**：`dotnet build` 只证明编译通过；无头渲染用 `Mapsui.Rendering.Skia.MapRenderer.RenderToBitmapStream(map, ...)` 输出 PNG 的 MemoryStream（参数以 IntelliSense 为准），落盘后 `read_image` 检查；WinForms/WPF 窗口 DSH 看不到，需用户运行后提供截图。
- **投影**：定位坐标必须 `SphericalMercator.FromLonLat(lon, lat)` 转换，直接用经纬度会定位到南太平洋。
- **数据**：Shapefile 中文要指定 `Encoding`（UTF8 或 GBK）；矢量要素装 `Mapsui.Nts`，瓦片装 `Mapsui.Tiling`，UI 包装 `Mapsui.Wpf`/`Mapsui.Maui`。
- **常见症状**：`MapControl` 空白先查是否赋值 `MapControl.Map`；MAUI 空白查 `UseSkiaSharp()` 与 `UseMapsui()` 是否注册。
- **安全与权限**：新建工程、装包、运行桌面程序前先征得用户同意；PostGIS/瓦片服务的密码不要写进代码或回答。

## 相关技能

- **openlayers** — Web 二维地图库（JavaScript）：[../openlayers/SKILL.md](../openlayers/SKILL.md)
- **sharpmap** — .NET 传统地图渲染引擎：[../sharpmap/SKILL.md](../sharpmap/SKILL.md)
- **nettopologysuite** — .NET 几何计算核心：[../nettopologysuite/SKILL.md](../nettopologysuite/SKILL.md)
- **geoserver** — 地图服务发布：[../geoserver/SKILL.md](../geoserver/SKILL.md)

## 参考资源

- 文档：<https://mapsui.com/v5/documentation/index.html>
- 示例：<https://mapsui.com/v5/samples/>
- 中文教程（znlgis）：<https://znlgis.github.io/gis/tutorial/Mapsui/>

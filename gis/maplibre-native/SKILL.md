---
name: maplibre-native
description: "Use when embedding GPU-accelerated vector maps natively in Android, iOS, macOS, Linux, Windows or Node.js with MapLibre Native (C++ core, BSD-2-Clause) — org.maplibre.gl:android-sdk MapView/MapLibre.getInstance/getMapAsync, CocoaPods MapLibre MLNMapView, @maplibre/maplibre-gl-native mbgl.Map render, offline caching, Bazel/CMake builds, or debugging green map screens, missing submodules and NDK build failures."
license: MIT
metadata:
  category: gis
  tags: "cpp, android, ios, macos, linux, nodejs, vector-tiles, opengl, metal, offline"
---

> **项目地址：** <https://github.com/maplibre/maplibre-native>
>
> **开发者文档：** <https://maplibre.org/maplibre-native/docs/book/>（架构、构建与贡献指南）
>
> **最新版本：** Android `13.5.4`（[GitHub Latest](https://github.com/maplibre/maplibre-native/releases)、[Maven](https://central.sonatype.com/artifact/org.maplibre.gl/android-sdk/versions)，13.x 特性线同时有 `13.7.1`）/ iOS `7.0.0`（CocoaPods `MapLibre`）/ Node `@maplibre/maplibre-gl-native` `6.4.1`（截至 2026-11，[发布记录](https://github.com/maplibre/maplibre-native/releases)；另有 `*-YYYY.MM.DD-globe` 实验线，非稳定版）
>
> **许可证：** BSD-2-Clause（含部分 FreeType 等第三方组件，见 `LICENSES.core.md`）

## 概述

MapLibre Native 是 Mapbox GL Native 的非商业许可分叉（2020-12 上游改为专有许可后分出），核心是一套 C++ 渲染引擎：解析 MapLibre Style Spec，按需拉取矢量/栅格瓦片，在 GPU 上批量绘制标注与几何。各平台只是同一内核的绑定层，因此样式、瓦片与交互语义在 Android/iOS/桌面/Node 之间保持一致。

- **GPU 矢量渲染**：OpenGL ES（Android）、Metal（iOS/macOS）等后端驱动，支持连续缩放与运行时样式切换
- **Style Spec 驱动**：与 maplibre-gl-js 共用样式规范，同一份 JSON 可在前端与原生端复用
- **平台绑定**：Android（`org.maplibre.gl:android-sdk`）、iOS/macOS（CocoaPods `MapLibre`、SPM）、Node.js（`@maplibre/maplibre-gl-native`）、Qt（maplibre-native-qt）、Compose Multiplatform（maplibre-compose）
- **离线能力**：瓦片缓存与离线区域下载，弱网/移动端场景可预置底图
- **可嵌入 C++**：Linux/Windows 构建产出 `.a`/库文件与渲染工具，可嵌入自有 C++ 应用
- **免 token**：不依赖商业账号，底图可用 demotiles 或自建瓦片服务

与相邻技术的差异：maplibre-gl-js 是浏览器端 JS 实现，适合网页；MapLibre Native 面向原生应用与离线场景，性能与内存控制更贴近移动端；CesiumJS/Cesium Native 偏三维地球，MapLibre Native 以二维矢量地图为主（三维地形为辅助能力）。

---

## 环境准备

### Android

Maven 坐标在 Maven Central，版本以 [Maven 元数据](https://repo1.maven.org/maven2/org/maplibre/gl/android-sdk/maven-metadata.xml) 为准。2026-11 时 `13.x` 特性线最新为 `13.7.1`，而 GitHub 标为 Latest 的是更晚发布的维护版 `13.5.4`——两者都在维护，按项目策略选用并保持一致。

```gradle
dependencies {
    implementation 'org.maplibre.gl:android-sdk:13.5.4'
}
```

```xml
<org.maplibre.android.maps.MapView
    android:id="@+id/mapView"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

```kotlin
import org.maplibre.android.MapLibre
import org.maplibre.android.camera.CameraPosition
import org.maplibre.android.geometry.LatLng
import org.maplibre.android.maps.MapView

class MainActivity : AppCompatActivity() {
    private lateinit var mapView: MapView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        MapLibre.getInstance(this)                 // 必须在 MapView 之前初始化
        setContentView(R.layout.activity_main)

        mapView = findViewById(R.id.mapView)
        mapView.getMapAsync { map ->
            map.setStyle("https://demotiles.maplibre.org/style.json")
            map.cameraPosition = CameraPosition.Builder()
                .target(LatLng(0.0, 0.0))
                .zoom(1.0)
                .build()
        }
    }

    override fun onStart() { super.onStart(); mapView.onStart() }
    override fun onResume() { super.onResume(); mapView.onResume() }
    override fun onPause() { super.onPause(); mapView.onPause() }
    override fun onStop() { super.onStop(); mapView.onStop() }
    override fun onLowMemory() { super.onLowMemory(); mapView.onLowMemory() }
    override fun onDestroy() { super.onDestroy(); mapView.onDestroy() }
}
```

`MapView` 的生命周期回调必须逐一转发，漏掉 `onDestroy()` 会泄漏原生渲染线程与显存。

### iOS / macOS

CocoaPods 或 Swift Package Index 均可接入，模块名为 `MapLibre`。

```ruby
# Podfile
pod 'MapLibre', '7.0.0'
```

```swift
import MapLibre

class SimpleMap: UIViewController, MLNMapViewDelegate {
    var mapView: MLNMapView!

    override func viewDidLoad() {
        super.viewDidLoad()
        mapView = MLNMapView(frame: view.bounds)
        mapView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        mapView.delegate = self
        view.addSubview(mapView)
    }

    func mapView(_ mapView: MLNMapView, didFinishLoading style: MLNStyle) {
        // 样式就绪后再加 source / layer
    }
}
```

iOS 7.0.0 是破坏性版本：最低 iOS 提高到 15.5，伞头文件由 `Mapbox.h` 改为 `MapLibre.h`，`MapLibre.xcframework` 不再附带 `Mapbox.h`。Objective-C 代码需把 `#import <Mapbox/Mapbox.h>` 改为 `#import <MapLibre/MapLibre.h>`。

### Node.js

预编译二进制在安装时下载，支持 Ubuntu 24.04、macOS、Windows（amd64/arm64）与 Node.js 22/24/26。

```bash
npm install @maplibre/maplibre-gl-native
npm ls @maplibre/maplibre-gl-native     # 验证：6.4.1
```

```javascript
const mbgl = require('@maplibre/maplibre-gl-native');
const sharp = require('sharp');

const map = new mbgl.Map({ request: (req, callback) => { /* 自定义瓦片/样式加载 */ } });
map.load(require('./style.json'));

map.render({ width: 512, height: 512, zoom: 2, center: [0, 0] }, (err, buffer) => {
  if (err) throw err;
  map.release();
  sharp(buffer, { raw: { width: 512, height: 512, channels: 4 } }).toFile('tile.png');
});
```

Node 端适合服务端静态出图、瓦片预生成与 CI 中的样式回归，不提供交互。

### C++ 核心（Linux/Windows）

贡献级构建需要带子模块克隆，Linux 以 Ubuntu 22.04+ 为目标：

```bash
git clone --recurse-submodules -j8 https://github.com/maplibre/maplibre-native.git
cd maplibre-native
```

Android 侧可直接用 Android Studio 打开 `platform/android`，或在仓库根用 Nix：`nix develop .#android`。iOS 用 Bazel（`brew install bazelisk`）生成 Xcode 工程：

```bash
bazel run //platform/ios:xcodeproj --@rules_xcodeproj//xcodeproj:extra_common_flags="--//:renderer=metal"
xed platform/ios/MapLibre.xcodeproj
```

完整依赖与构建选项见 [开发者文档](https://maplibre.org/maplibre-native/docs/book/)。

### 验证

```bash
# Android：确认依赖树里的 SDK 版本
./gradlew :app:dependencies --configuration debugRuntimeClasspath | grep maplibre
# Node：确认二进制与版本
node -e "const m=require('@maplibre/maplibre-gl-native'); console.log(typeof m.Map)"
```

地图能显示 demotiles 世界地图且可拖拽缩放，即接入成功。

---

## 核心 API

### 平台 API 对照

| 能力 | Android | iOS / macOS | Node.js |
|------|---------|-------------|---------|
| 地图视图 | `MapView` + `getMapAsync` | `MLNMapView` | `mbgl.Map` |
| 初始化 | `MapLibre.getInstance(context)` | 直接创建视图 | `new mbgl.Map(options)` |
| 样式 | `map.setStyle(json or url)` | `styleURL` / `MLNStyle` | `map.load(style)` |
| 相机 | `map.cameraPosition = ...` | `setCenterCoordinate` 等 | `render({center, zoom, bearing, pitch})` |
| 数据源 | `GeoJsonSource` / `VectorSource` | `MLNShapeSource` / `MLNVectorTileSource` | 通过 `request` 回调供给 |
| 出图 | `MapSnapshotter` | `MLNMapSnapshotter` | `map.render(callback)` |
| 生命周期 | `onStart/onResume/onPause/onStop/onDestroy` | UIViewController 生命周期 | `map.release()` |

### 样式与图层

原生端与 maplibre-gl-js 共用 Style Spec，样式 JSON 可以直接复用。运行时改样式的三种方式：

```kotlin
// Android：整体换样式（会重建图层）
map.setStyle("https://demotiles.maplibre.org/style.json")

// 用 builder 构造样式，便于插入自定义字体与图层
val style = Style.Builder()
    .fromUri("https://demotiles.maplibre.org/style.json")
    .withSource(GeoJsonSource("pois", GeoJsonSourceOptions().data(geojson)))
    .withLayer(CircleLayer("pois-layer", "pois"))
map.setStyle(style)
```

```swift
// iOS：通过 MLNStyle 追加 source 与 layer
let source = MLNShapeSource(identifier: "pois", shape: shape, options: nil)
style.addSource(source)
let layer = MLNCircleStyleLayer(identifier: "pois-layer", source: source)
layer.circleRadius = NSExpression(forConstantValue: 6)
style.addLayer(layer)
```

### 相机与交互

```kotlin
import org.maplibre.android.camera.CameraUpdateFactory

map.animateCamera(CameraUpdateFactory.newLatLngZoom(LatLng(39.91, 116.39), 10.0), 1000)
map.cameraPosition = CameraPosition.Builder()
    .target(LatLng(39.91, 116.39))
    .zoom(12.0).tilt(45.0).bearing(30.0)
    .build()
```

```swift
mapView.setCenter(CLLocationCoordinate2D(latitude: 39.91, longitude: 116.39), zoomLevel: 10, animated: true)
mapView.setDirection(30, animated: false)
```

手势（平移、缩放、旋转、倾斜）默认开启；`MapView` 的点击/长按回调在 Android 侧通过 `map.addOnMapClickListener` 等注册，iOS 侧走 `MLNMapViewDelegate`。

### 离线地图与缓存

Android 的 `OfflineManager` / `OfflineRegion` 可把指定 bbox 与缩放范围的瓦片预下载到本地数据库，之后无网仍可渲染。要点：

1. 定义 `OfflineTilePyramidRegionDefinition`（样式 URL + bbox + min/max zoom + 像素比）
2. `OfflineManager.createOfflineRegion` 提交下载任务，监听进度回调
3. 下载受瓦片服务端的 `Cache-Control` 与服务条款约束，公共底图不保证允许批量离线
4. 清理用 `deleteOfflineRegion`，避免移动端存储长期膨胀

### 自定义图层与扩展

C++ 内核支持自定义图层钩子，但各平台暴露程度不同。实际项目更常见的是：

- 用 Style Spec 的 `symbol` / `fill-extrusion` 等原生图层满足需求，避免自写渲染代码
- 标注与交互覆盖物用平台原生控件叠加（Android `SymbolManager`、iOS annotation）
- 需要真正自定义 GPU 绘制时，走 C++ 层并在目标平台重新绑定，成本高，先确认没有样式层解法

---

## 典型工作流

### 链路一：Android 离线底图 + 业务点位

输入：底图样式 URL、业务点位 GeoJSON、目标区域 bbox；输出：可离线使用的点位地图。

1. `MapLibre.getInstance(context)` 初始化（单例，早于任何 MapView）
2. 建立 `MapView` 并转发全部生命周期回调
3. `getMapAsync` 中 `setStyle`，再加 `GeoJsonSource` 与 `CircleLayer`
4. 用 `OfflineManager` 按 bbox + zoom 范围创建离线区域，展示下载进度
5. 断网重启应用验证：底图与点位仍可见
6. 校验：`adb logcat` 无渲染线程崩溃、`MapView.onDestroy()` 已调用

```kotlin
mapView.getMapAsync { map ->
    map.setStyle("https://demotiles.maplibre.org/style.json")
    map.addOnStyleLoadedListener {
        val source = GeoJsonSource("pois", GeoJsonSourceOptions().data(poiGeoJson))
        map.addSource(source)
        map.addLayer(CircleLayer("pois-layer", "pois").withProperties(
            PropertyFactory.circleRadius(6f),
            PropertyFactory.circleColor("#d7301f")
        ))
    }
}
```

### 链路二：iOS 样式热切换 + 标注

输入：两套样式 JSON；输出：运行时可切换主题、标注不丢的地图。

1. 首次进入用远程样式 URL 加载，`didFinishLoading style` 回调里补业务 source/layer
2. 换主题时再次设置 `mapView.styleURL`，在回调里重新补业务图层（换样式会清空自定义图层）
3. 标注用 `MLNPointAnnotation` 或 ShapeSource，注意换样式后的重建
4. 校验：切换两次主题后业务图层不重复、不消失，无内存增长

```swift
func mapView(_ mapView: MLNMapView, didFinishLoading style: MLNStyle) {
    guard style.source(withIdentifier: "pois") == nil else { return }   // 防重复添加
    let source = MLNShapeSource(identifier: "pois", shape: poiShape, options: nil)
    style.addSource(source)
    let layer = MLNCircleStyleLayer(identifier: "pois-layer", source: source)
    style.addLayer(layer)
}
```

### 链路三：Node 服务端瓦片出图

输入：样式 JSON 与 z/x/y 瓦片坐标；输出：PNG 图片文件（CI 回归或离线切片）。

1. `new mbgl.Map({ request })`，`request` 里返回本地或远程的样式/瓦片数据
2. `map.load(style)` 载入样式
3. `map.render({ width, height, zoom, center }, cb)` 拿 RGBA 缓冲
4. 用 sharp 等库编码为 PNG 落盘，务必 `map.release()` 释放原生资源
5. 校验：输出图片尺寸与坐标范围符合预期，多瓦片循环时无内存持续上涨

```javascript
const mbgl = require('@maplibre/maplibre-gl-native');

function renderTile(z, x, y) {
  const map = new mbgl.Map({ request: (req, cb) => cb(null, loadResource(req.url)) });
  map.load(styleJson);
  return new Promise((resolve, reject) => {
    map.render({ width: 512, height: 512, zoom: z, center: tileCenter(x, y, z) }, (err, buf) => {
      map.release();
      err ? reject(err) : resolve(buf);
    });
  });
}
```

---

## 性能与工程实践

1. **生命周期别漏**：Android 少转发一个回调就可能让渲染线程常驻；`onDestroy` 必须调用
2. **样式切换会重建图层**：`setStyle` 后自定义 source/layer 消失，需在回调里幂等重建（先查 `source(withIdentifier:)`）
3. **缓存要设上限**：默认磁盘缓存随浏览增长，长时间运行的 kiosk/车载应用要显式管理离线区域与缓存大小
4. **大 GeoJSON 预先切片**：客户端解析 GeoJSON 会把要素展开进内存，超过数万要素改用矢量瓦片源
5. **出图复用 Map 实例**：Node 端每次渲染都新建 Map 会重复解析样式，批量出图时按样式复用并在结束时统一 `release()`
6. **控制标注数量**：原生端标注布局在 CPU 侧，密集标注要依赖 `text-allow-overlap`/`symbol-sort-key` 收敛
7. **按平台选版本线**：`13.x` 与 `*-globe` 实验线不要混用，升级前看 release notes 的破坏性变更段

---

## 常见问题

| 问题 | 原因 | 处置 |
|------|------|------|
| Android 地图为绿屏或纯色块 | `MapLibre.getInstance()` 未调用、或在 `MapView` 之后才调用，渲染初始化失败 | 在 `onCreate` 最前面调用 `MapLibre.getInstance(this)`，再 `setContentView` 与创建 MapView |
| Android 退出后崩溃 / 内存持续增长 | `MapView` 生命周期回调未全部转发，原生资源未释放 | 在 `onStart/onResume/onPause/onStop/onLowMemory/onDestroy` 中逐一调用同名 `mapView.*` 方法 |
| 编译报找不到 `org.maplibre.android.*` | 依赖坐标或版本写错，仍用旧的 Mapbox 包名 | 依赖应为 `org.maplibre.gl:android-sdk`，包名 `org.maplibre.android`；`./gradlew :app:dependencies` 核对实际版本 |
| 克隆后编译报缺少子模块头文件 | 仓库依赖 git submodules，普通 clone 没拉取 | `git clone --recurse-submodules`，或补 `git submodule update --init --recursive` |
| iOS 升级 7.0.0 后 `Mapbox.h` 找不到 | 伞头文件改名，xcframework 不再附带 `Mapbox.h` | Objective-C 改为 `#import <MapLibre/MapLibre.h>`；Swift 继续 `import MapLibre` |
| iOS 7.0.0 起要求更高系统版本 | 该版本把最低 iOS 提高到 15.5 | 提升部署目标，或暂时停留在 6.x 线 |
| 换样式后业务图层消失 | `setStyle` 会替换整份样式，自定义 source/layer 被清空 | 在 `didFinishLoading`（iOS）/`addOnStyleLoadedListener`（Android）里幂等重建 |
| Node 渲染报找不到模块或二进制 | 预编译二进制只覆盖特定平台与 Node 版本（22/24/26） | 确认操作系统与 Node 大版本在支持列表内；换 Node LTS 或自行编译 |
| 地图整块空白且无瓦片请求 | 样式 URL 不可达，或 `request` 回调没有正确返回数据 | 先确认样式 JSON 能下载，再检查自定义 `request` 是否对每种 `kind` 都 `callback` |
| 离线区域下载失败 | 底图服务端的 `Cache-Control` 或服务条款不允许批量抓取 | 改用允许离线的自建瓦片服务，并遵守其条款 |

---

## AI 使用建议

- **执行环境**：Android 构建用 `./gradlew`，iOS 用 Bazel 或 Xcode，Node 用 `npm`；这些都需要各自 SDK，AI 助手应先用 `java -version`、`xcodebuild -version`、`node -v` 探测环境，缺失时不要臆造构建成功。
- **先探测版本**：Android 查依赖树（`./gradlew :app:dependencies`）或 Maven 元数据；iOS 查 `Podfile.lock`；Node 用 `npm ls @maplibre/maplibre-gl-native`。本技能按 Android 13.x、iOS 7.0.0、Node 6.4.1 编写。
- **验证产物**：Android 用模拟器/真机看画面并 `adb logcat` 查渲染报错；iOS 用 Simulator；Node 直接检查输出 PNG 的尺寸与内容；构建通过不等于渲染正确。
- **无设备环境**：CI/无头机器无法验证 GPU 渲染，不要报告"地图已显示"；只能验证编译与产物生成。
- **坐标顺序**：经纬度按平台类型使用（`LatLng(lat, lng)` 在 Android 是纬度在前，`CLLocationCoordinate2D(latitude:longitude:)` 亦然），与 JS 的 `[lng, lat]` 相反，跨端复用时最容易出错。
- **版本线选择**：`13.x` 为常规线，`*-globe` 是实验线（球体投影）；回答先给出目标平台与所需版本线，再给依赖坐标。
- **安全与权限**：安装 SDK/NDK、跑模拟器、下载依赖前先征得用户同意；离线批量抓取瓦片需确认底图服务条款允许。

## 相关技能

- **maplibre-gl-js** — 同体系的浏览器端实现，样式 JSON 可共用：[../maplibre-gl-js/SKILL.md](../maplibre-gl-js/SKILL.md)
- **mapbox-gl-js** — 上游血统的商业版本，概念对应关系可参考：[../mapbox-gl-js/SKILL.md](../mapbox-gl-js/SKILL.md)
- **cesiumjs** — 三维地球与 3D Tiles，三维场景的另一条路线：[../cesiumjs/SKILL.md](../cesiumjs/SKILL.md)
- **gdal** — 瓦片与栅格数据的前置处理（切片、重投影、COG）：[../gdal/SKILL.md](../gdal/SKILL.md)
- **pdal** — 点云数据处理，与地形/高程数据配合：[../pdal/SKILL.md](../pdal/SKILL.md)
- **postgis** — 矢量瓦片的数据源与空间查询后端：[../postgis/SKILL.md](../postgis/SKILL.md)

## 参考资源

- 源码仓库：<https://github.com/maplibre/maplibre-native>
- 开发者文档：<https://maplibre.org/maplibre-native/docs/book/>
- Android API：<https://maplibre.org/maplibre-native/android/api/>
- Android 入门示例：<https://maplibre.org/maplibre-native/android/examples/getting-started/>
- iOS 文档：<https://maplibre.org/maplibre-native/ios/latest/documentation/maplibre/>
- C++ API（不稳定）：<https://maplibre.org/maplibre-native/cpp/api/>
- Maven 版本列表：<https://central.sonatype.com/artifact/org.maplibre.gl/android-sdk/versions>
- CocoaPods：<https://cocoapods.org/pods/MapLibre>
- 发布记录：<https://github.com/maplibre/maplibre-native/releases>
- 中文教程：<https://znlgis.github.io/gis/tutorial/maplibre-native/>

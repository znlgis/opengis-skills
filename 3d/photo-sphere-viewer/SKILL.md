---
name: photo-sphere-viewer
description: "Use when displaying 360-degree panoramic images (equirectangular/cubemap/dual-fisheye) in web applications, building virtual tours with markers and transitions, embedding interactive panoramas in Vue/React/vanilla JS, or creating 360-degree video players with gyroscope VR support. Photo-Sphere-Viewer v5: JavaScript panorama viewer based on Three.js. Covers Viewer class, 6 adapters, 14 plugins, and markers system."
tags:
  - javascript
  - typescript
  - threejs
  - webgl
  - 3d
  - panorama
  - 360-photo
  - virtual-tour
---

> **仓库地址：** <https://github.com/mistic100/Photo-Sphere-Viewer>
>
> **文档：** <https://photo-sphere-viewer.js.org>
>
> **演示：** <https://photo-sphere-viewer.js.org/demos/>
>
> **API 参考：** <https://photo-sphere-viewer.js.org/api/>
>
> **Playground：** <https://photo-sphere-viewer.js.org/playground.html>
>
> **许可证：** MIT
>
> **最新版本：** v5.15.0（2026-07）

## 概述

**Photo-Sphere-Viewer (PSV)** 是一个基于 **Three.js** 的纯 JavaScript 库，用于在 Web 浏览器中显示 360° 全景照片/球体图像。支持从简单的照片球体到复杂的带标记、导航、陀螺仪和 VR 的虚拟导览。

| 特性 | 说明 |
|------|------|
| **全景格式** | 等距柱状图、立方体贴图（6面/条纹/展开图）、双鱼眼原始格式 |
| **分块加载** | 大图分块（Equirectangular/Cubemap Tiles Adapter） |
| **360° 视频** | 等距柱状图 + 立方体贴图视频支持 |
| **标记系统** | 图片/HTML/视频/SVG/多边形/折线标记，含提示框和动态缩放 |
| **VR 支持** | 移动端陀螺仪 + 立体视差模式（需 GyroscopePlugin + StereoPlugin） |
| **虚拟导览** | 多全景场景链接，支持平滑过渡与双向箭头指示 |
| **插件生态** | 14 个官方插件（Markers、Gallery、VirtualTour、Autorotate、Map 等） |
| **框架集成** | 原生 ES 模块，React wrapper 可用 |

> **唯一运行时依赖：** Three.js（`^0.185.1`）。所有适配器和插件作为 `@photo-sphere-viewer/*` 独立 NPM 包发布。

---

## 环境准备与安装

### 安装核心包

```bash
npm install @photo-sphere-viewer/core
```

### 安装适配器和插件（按需）

```bash
# 适配器
npm install @photo-sphere-viewer/cubemap-adapter          # 立方体贴图
npm install @photo-sphere-viewer/equirectangular-video-adapter  # 360° 视频
npm install @photo-sphere-viewer/equirectangular-tiles-adapter  # 分块加载大图
npm install @photo-sphere-viewer/dual-fisheye-adapter     # 双鱼眼（Ricoh Theta 等）

# 常用插件
npm install @photo-sphere-viewer/markers-plugin           # 标记系统
npm install @photo-sphere-viewer/gallery-plugin           # 底部画廊
npm install @photo-sphere-viewer/virtual-tour-plugin      # 虚拟导览
npm install @photo-sphere-viewer/gyroscope-plugin         # 陀螺仪
npm install @photo-sphere-viewer/stereo-plugin            # 立体/VR
npm install @photo-sphere-viewer/autorotate-plugin        # 自动旋转
npm install @photo-sphere-viewer/video-plugin             # 视频控制条
npm install @photo-sphere-viewer/compass-plugin           # 罗盘
npm install @photo-sphere-viewer/map-plugin               # 地图集成
```

### 直接 HTML 引入

```html
<div id="viewer" style="width: 100%; height: 100vh;"></div>

<script type="module">
  import { Viewer } from '@photo-sphere-viewer/core';
  import '@photo-sphere-viewer/core/index.css';

  const viewer = new Viewer({
    container: '#viewer',
    panorama: 'pano.jpg',
  });
</script>
```

> **注意：** 需要 WebGL 支持（现代浏览器均支持）。移动端陀螺仪和立体 VR 功能需 HTTPS。

---

## 快速上手

### 基础全景查看器

```ts
import { Viewer } from '@photo-sphere-viewer/core';
import '@photo-sphere-viewer/core/index.css';

const viewer = new Viewer({
  container: document.querySelector('#viewer'),
  panorama: 'https://example.com/panorama.jpg',
  caption: '山顶全景',
  description: '拍摄于 2026 年 7 月',
  defaultYaw: '45deg',
  defaultPitch: '10deg',
  defaultZoomLvl: 50,
  navbar: ['zoom', 'fullscreen', 'caption'],
  loadingTxt: '加载中...',
  lang: {
    zoom: '缩放',
    fullscreen: '全屏',
  },
});
```

### 带标记和画廊

```ts
import { Viewer } from '@photo-sphere-viewer/core';
import { MarkersPlugin } from '@photo-sphere-viewer/markers-plugin';
import { GalleryPlugin } from '@photo-sphere-viewer/gallery-plugin';
import '@photo-sphere-viewer/markers-plugin/index.css';

const viewer = new Viewer({
  container: '#viewer',
  panorama: 'room1.jpg',
  navbar: ['zoom', 'fullscreen', 'markers', 'gallery'],
  plugins: [
    MarkersPlugin.withConfig({
      markers: [
        {
          id: 'door',
          position: { yaw: '30deg', pitch: 0 },
          image: 'pin.png',
          size: { width: 40, height: 40 },
          tooltip: '入口',
          content: '<h3>入口大门</h3><p>由此进入主展厅</p>',
        },
        {
          id: 'window',
          position: { yaw: '-90deg', pitch: '5deg' },
          html: '<div class="hotspot">窗</div>',
          tooltip: '落地窗 - 点击查看详情',
        },
      ],
    }),
    GalleryPlugin.withConfig({
      items: [
        { id: '1', name: '客厅', panorama: 'room1.jpg', thumbnail: 'thumb1.jpg' },
        { id: '2', name: '餐厅', panorama: 'room2.jpg', thumbnail: 'thumb2.jpg' },
        { id: '3', name: '卧室', panorama: 'room3.jpg', thumbnail: 'thumb3.jpg' },
      ],
      visibleOnLoad: true,
      hideOnClick: false,
    }),
  ],
});

viewer.addEventListener('ready', () => {
  console.log('全景加载完成');
});
```

### 立方体贴图

```ts
import { Viewer } from '@photo-sphere-viewer/core';
import { CubemapAdapter } from '@photo-sphere-viewer/cubemap-adapter';

const viewer = new Viewer({
  container: '#viewer',
  adapter: CubemapAdapter,
  panorama: {
    left: 'cubemap/left.jpg',
    front: 'cubemap/front.jpg',
    right: 'cubemap/right.jpg',
    back: 'cubemap/back.jpg',
    top: 'cubemap/top.jpg',
    bottom: 'cubemap/bottom.jpg',
  },
});
```

---

## 核心 API

### Viewer 类

**`new Viewer(config: ViewerConfig)`** — 创建查看器实例，返回已初始化的 Viewer。

**关键配置项：**

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `container` | `HTMLElement \| string` | 必填 | 容器元素 |
| `panorama` | `string \| object` | 必填 | 全景源（URL 或适配器对象） |
| `adapter` | `AdapterConstructor` | `EquirectangularAdapter` | 适配器类 |
| `plugins` | `PluginDefinition[]` | `[]` | 插件数组 |
| `defaultYaw` | `number \| string` | `0` | 默认水平角 |
| `defaultPitch` | `number \| string` | `0` | 默认俯仰角 |
| `defaultZoomLvl` | `number` | `50` | 默认缩放 (0-100) |
| `minFov` / `maxFov` | `number` | `30` / `90` | 视场角范围（度） |
| `fisheye` | `boolean \| number` | `false` | 鱼眼效果（0-1 或 true） |
| `moveSpeed` | `number` | `1` | 拖拽灵敏度 |
| `zoomSpeed` | `number` | `1` | 滚轮缩放灵敏度 |
| `moveInertia` | `boolean \| number` | `0.8` | 惯性移动（false 关闭） |
| `navbar` | `NavbarConfig` | — | 导航栏按钮配置 |
| `keyboard` | `boolean \| string` | `'fullscreen'` | 键盘控制 |
| `canvasBackground` | `string` | `'#000'` | 画布背景色 |
| `lang` | `object` | — | 国际化覆盖（覆盖默认英文） |

**主要方法：**

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `animate(options)` | `Animation` | 平滑旋转/缩放（`yaw, pitch, zoom, speed`） |
| `rotate(position)` | — | 立即旋转到指定视角 |
| `setPanorama(url, options?)` | `Promise` | 切换全景图（支持过渡动画） |
| `zoom(level)` / `zoomIn(step?)` / `zoomOut(step?)` | — | 缩放控制 |
| `getPosition()` | `{ yaw, pitch }` | 获取当前视角 |
| `getZoomLevel()` | `number` | 获取当前缩放 (0-100) |
| `getPlugin(PluginClass)` | `PluginInstance` | 获取插件实例 |
| `setOption(key, value)` | — | 更新单个选项 |
| `setOptions(obj)` | — | 批量更新选项 |
| `destroy()` | — | 销毁查看器，释放 Three.js 资源 |

**主要事件：**

| 事件 | 回调参数 | 触发时机 |
|------|---------|---------|
| `ready` | — | 全景加载完成，首次渲染就绪 |
| `click` | `{ rightclick, data: { yaw, pitch, ... } }` | 点击全景 |
| `position-updated` | `{ position: { yaw, pitch } }` | 视角变化 |
| `zoom-updated` | `{ zoomLevel }` | 缩放变化 |
| `panorama-loaded` | `{ data }` | 新全景加载完成 |
| `load-progress` | `{ progress }` | 加载进度 (0-100) |
| `fullscreen-updated` | `{ fullscreen }` | 全屏状态变化 |

---

## 适配器（全景格式）

| 适配器 | NPM 包 | 适用场景 | 配置要点 |
|--------|--------|---------|---------|
| **EquirectangularAdapter** | `@photo-sphere-viewer/core`（内置） | 标准 2:1 全景图 | 默认即用，自动读取 XMP 元数据 |
| **CubemapAdapter** | `@photo-sphere-viewer/cubemap-adapter` | 立方体贴图（6 面/条纹/展开图） | `panorama: { left, front, ... }` |
| **EquirectangularTilesAdapter** | `@photo-sphere-viewer/equirectangular-tiles-adapter` | 大图分块加载 | 配置多级 `tiles` 尺寸 |
| **CubemapTilesAdapter** | `@photo-sphere-viewer/cubemap-tiles-adapter` | 立方体贴图分块 | 类似上者，六面分块 |
| **EquirectangularVideoAdapter** | `@photo-sphere-viewer/equirectangular-video-adapter` | 360° 视频（等距柱状） | `panorama: { source: 'video.mp4' }` |
| **CubemapVideoAdapter** | `@photo-sphere-viewer/cubemap-video-adapter` | 360° 视频（立方体贴图） | 需配合 VideoPlugin |
| **DualFisheyeAdapter** | `@photo-sphere-viewer/dual-fisheye-adapter` | 双鱼眼原始格式（Ricoh Theta Z1 等） | v5.15+ 含 `DualFisheyeVideoAdapter` |

### 适配器的全景数据配置（PanoData）

```ts
const viewer = new Viewer({
  adapter: EquirectangularAdapter,
  panorama: 'crop.jpg',
  panoData: {
    fullWidth: 4096,   // 源图像完整宽度
    fullHeight: 2048,   // 源图像完整高度
    croppedWidth: 2048, // 裁剪后宽度
    croppedHeight: 1024,// 裁剪后高度
    croppedX: 1024,     // 裁剪 X 偏移
    croppedY: 512,      // 裁剪 Y 偏移
  },
});
```

> 等距柱状图适配器默认使用 `useXmpData: true` 自动读取图像 XMP 元数据获取裁剪信息。v5.14.2+ 新增 `shader` 选项（默认 `false`，可设为 `true` 用像素着色器消除极点扭曲）。

---

## 插件系统

### 使用方式

```ts
// 方式 1：无配置项（自动使用默认值）
const viewer = new Viewer({ plugins: [GyroscopePlugin] });

// 方式 2：带类型安全的配置
const viewer = new Viewer({
  plugins: [
    AutorotatePlugin.withConfig({ autorotateSpeed: '3rpm' }),
    MarkersPlugin.withConfig({ markers: [...] }),
  ],
});

// 方式 3：混合
const viewer = new Viewer({
  plugins: [
    { plugin: MarkersPlugin, config: { markers: [...] } },
  ],
});

// 运行时获取插件实例
const markers = viewer.getPlugin(MarkersPlugin);
markers.addMarker({ ... });
```

### 所有插件速览

| 插件 | 导入类 | 说明 |
|------|--------|------|
| **MarkersPlugin** | `@photo-sphere-viewer/markers-plugin` | 标记系统——最重要插件 |
| **GalleryPlugin** | `@photo-sphere-viewer/gallery-plugin` | 底部画廊，切换全景 |
| **VirtualTourPlugin** | `@photo-sphere-viewer/virtual-tour-plugin` | 虚拟导览，多全景节点链接 |
| **AutorotatePlugin** | `@photo-sphere-viewer/autorotate-plugin` | 自动旋转（含关键点停留） |
| **GyroscopePlugin** | `@photo-sphere-viewer/gyroscope-plugin` | 移动端陀螺仪控制 |
| **StereoPlugin** | `@photo-sphere-viewer/stereo-plugin` | 立体/VR 模式（需 GyroscopePlugin） |
| **VideoPlugin** | `@photo-sphere-viewer/video-plugin` | 视频控制条（播放/音量/进度） |
| **CompassPlugin** | `@photo-sphere-viewer/compass-plugin` | 罗盘指示器 |
| **MapPlugin** | `@photo-sphere-viewer/map-plugin` | Leaflet 地图热点 |
| **PlanPlugin** | `@photo-sphere-viewer/plan-plugin` | 平面图热区 |
| **ResolutionPlugin** | `@photo-sphere-viewer/resolution-plugin` | 多分辨率视频切换 |
| **SettingsPlugin** | `@photo-sphere-viewer/settings-plugin` | 设置面板 |
| **OverlaysPlugin** | `@photo-sphere-viewer/overlays-plugin` | 叠加层渲染 |
| **VisibleRangePlugin** | `@photo-sphere-viewer/visible-range-plugin` | 限制可见视角范围 |

---

## MarkersPlugin 详解

标记是 PSV 最核心的交互功能，支持二维（CSS 定位）和三维（场景内渲染）两种渲染模式。

### 标记类型

| 类型 | 渲染模式 | 说明 |
|------|---------|------|
| `image` | CSS | PNG/SVG 标记图片 |
| `imageLayer` | 3D 场景内 | 图片，随全景自然缩放（更逼真） |
| `html` | CSS | 自定义 HTML 内容 |
| `element` / `elementLayer` | CSS / 3D | 已存在的 DOM 元素 / Web Component |
| `square` / `rect` / `circle` / `ellipse` / `path` | 3D SVG | 基本形状 |
| `polygon` / `polygonPixels` | 3D SVG | 多边形（球面坐标/像素坐标，支持孔洞） |
| `polyline` / `polylinePixels` | 3D SVG | 折线 |
| `videoLayer` | 3D 场景内 | 视频贴图 |

### 位置系统

```ts
// 球面坐标（推荐）
position: { yaw: '45deg', pitch: '10deg' }

// 像素坐标
position: { textureX: 1024, textureY: 512 }

// 数组简写（仅球面坐标）
position: [Math.PI / 4, 0.2]  // [yaw, pitch]
```

### 标记配置完整示例

```ts
const markersPlugin = viewer.getPlugin(MarkersPlugin);

markersPlugin.addMarker({
  id: 'building-a',
  position: { yaw: '30deg', pitch: '5deg' },
  image: 'marker.svg',
  size: { width: 36, height: 36 },
  scale: { zoom: [30, 80], yaw: [0, 15] },  // 缩放范围 [min, max] 内显示
  opacity: 0.9,
  anchor: 'bottom center',      // 对齐方式
  tooltip: {
    content: 'A 栋办公楼',
    position: 'right',           // 'top' | 'right' | 'bottom' | 'left'
    className: 'custom-tooltip',
  },
  content: '<div class="popup"><h2>A 栋</h2><p>建筑面积 12000m²</p></div>',
  data: { floor: 15, year: 2025 },  // 自定义数据
  style: { cursor: 'pointer' },
});

// 监听标记事件
markersPlugin.addEventListener('select-marker', ({ marker }) => {
  console.log('选中标记:', marker.id, marker.data);
});
```

### 标记事件

| 事件 | 说明 |
|------|------|
| `select-marker` | 标记被选中（点击） |
| `unselect-marker` | 取消选中 |
| `enter-marker` | 鼠标进入标记区域 |
| `leave-marker` | 鼠标离开标记区域 |
| `over-marker` | 鼠标悬停（持续） |
| `goto-marker-done` | `gotoMarker()` 动画完成 |

---

## 虚拟导览（VirtualTourPlugin）

```ts
import { VirtualTourPlugin } from '@photo-sphere-viewer/virtual-tour-plugin';

const viewer = new Viewer({
  container: '#viewer',
  plugins: [
    VirtualTourPlugin.withConfig({
      dataMode: 'client',           // 'client'（手动提供） | 'server'（远程加载）
      positionMode: 'manual',       // 'manual'（手动指定） | 'gps'（GPS 坐标映射）
      renderMode: 'markers',        // 'markers' | 'arrows' | '3d-arrows'
      startNodeId: 'entrance',
      transitionOptions: { speed: 2000, effect: 'fade' },
      nodes: [
        {
          id: 'entrance',
          panorama: 'entrance.jpg',
          caption: '入口大厅',
          links: [
            { nodeId: 'hall', position: { yaw: '90deg', pitch: 0 }, name: '进入展厅' },
          ],
        },
        {
          id: 'hall',
          panorama: 'hall.jpg',
          caption: '主展厅',
          links: [
            { nodeId: 'entrance', position: { yaw: '-90deg', pitch: 0 }, name: '返回入口' },
            { nodeId: 'garden', position: { yaw: '45deg', pitch: '10deg' }, name: '户外花园' },
          ],
        },
        {
          id: 'garden',
          panorama: 'garden.jpg',
          caption: '户外花园',
          links: [
            { nodeId: 'hall', position: { yaw: '-135deg', pitch: 0 }, name: '返回展厅' },
          ],
        },
      ],
    }),
  ],
});

const tourPlugin = viewer.getPlugin(VirtualTourPlugin);

// 监听节点切换
tourPlugin.addEventListener('node-changed', ({ node }) => {
  console.log('切换到节点:', node.id, node.caption);
});

// 程序化导览
tourPlugin.setCurrentNode('garden');
```

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 全景图模糊 | 确保图像分辨率 >= 4096x2048；使用 `EquirectangularTilesAdapter` 分块加载高清图 |
| 移动端性能卡顿 | 降低 `rendererParameters.antialias: false`；减少同时显示的标记数量；使用 `imageLayer` 替代 `html` 标记 |
| 陀螺仪不生效 | 确认 HTTPS 访问；iOS 13+ 需用户授权 DeviceOrientation；使用 `GyroscopePlugin` |
| 立方体贴图显示黑屏 | 检查 `panorama` 对象所有六面 URL 均可访问；确认文件格式为 jpg/png |
| 标记点击无反应 | 确认 `tooltip` 或 `content` 已配置；检查 `visible: true` 和 `opacity > 0` |
| `setPanorama` 后标记丢失 | 标记绑定到当前全景；切换后需重新 `setMarkers()` 或使用 `VirtualTourPlugin` 管理器 |
| 图片跨域报错 | 服务器配置 `Access-Control-Allow-Origin: *` 或 `crossorigin="anonymous"`；或设置 `withCredentials: true` |
| CJS 项目引入 ES 模块报错 | 使用动态 `import()` 或配置打包工具（Webpack/Vite）支持 ESM |
| React 项目集成 | 使用 `react-photo-sphere-viewer` wrapper (<https://www.npmjs.com/package/react-photo-sphere-viewer>)，封装 Viewer 为 React 组件 |
| v4 迁移到 v5 变量名变化 | `longitude/latitude` → `yaw/pitch`；`x/y` → `textureX/textureY`；`polygonRad` → `polygon`；`polygonPx` → `polygonPixels` |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应将全景项目组织为「Viewer 核心配置 → 适配器选择 → 插件组合 → 标记定义」的结构。初始用 `EquirectangularAdapter` + `MarkersPlugin` + `GalleryPlugin` 组合覆盖 80% 场景，后续按需添加 `VirtualTourPlugin` 或 `GyroscopePlugin`。
- **关键注意事项**：① `panorama` 路径需确保 CORS 头正确配置（`Access-Control-Allow-Origin: *`）；② 所有时长/速度参数以毫秒为单位（`speed: 1500` = 1.5 秒）或 `'3rpm'` 格式（每分钟旋转次数计算）；③ `MarkersPlugin` 的 CSS 样式需通过 `className` + 外部 CSS 控制，不建议内联大量样式；④ `setPanorama()` 后标记需重新设置，除非使用 `VirtualTourPlugin` 管理节点。
- **常用代码模式**：
  - **基础查看器**：`new Viewer({ container, panorama })` + `@photo-sphere-viewer/core/index.css`
  - **标记**：`MarkersPlugin.withConfig({ markers: [{ id, position, image, tooltip }] })`
  - **画廊**：`GalleryPlugin.withConfig({ items: [{ id, name, panorama, thumbnail }] })`
  - **导览**：`VirtualTourPlugin.withConfig({ nodes, startNodeId, positionMode: 'manual' })`
  - **动画**：`viewer.animate({ yaw, pitch, zoom, speed: 1500 })`
  - **获取插件**：`viewer.getPlugin(MarkersPlugin).addMarker(...)`

---

## 参考资源

- 官方文档：<https://photo-sphere-viewer.js.org>
- API 参考：<https://photo-sphere-viewer.js.org/api/>
- 在线演示：<https://photo-sphere-viewer.js.org/demos/>
- Playground：<https://photo-sphere-viewer.js.org/playground.html>
- GitHub 仓库：<https://github.com/mistic100/Photo-Sphere-Viewer>
- 发布说明：<https://github.com/mistic100/Photo-Sphere-Viewer/releases>
- React wrapper：<https://www.npmjs.com/package/react-photo-sphere-viewer>
- 中文教程（znlgis）：<https://znlgis.github.io/3d/tutorial/photo-sphere-viewer/>
- NPM（core）：<https://www.npmjs.com/package/@photo-sphere-viewer/core>

---

## 相关技能

- **cesiumjs** — 3D 地球与大规模场景可视化：[../../gis/cesiumjs/SKILL.md](../../gis/cesiumjs/SKILL.md)
- **supersplat** — 3D 高斯泼溅编辑器与查看器：[../supersplat/SKILL.md](../supersplat/SKILL.md)

# Photo Sphere Viewer Plugins Reference

Plugin system, MarkersPlugin and VirtualTourPlugin details split from SKILL.md.

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

$h$faq`

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


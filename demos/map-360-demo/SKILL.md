---
name: map-360-demo
description: "Use when wiring a 360° panorama viewer to a plan map — Photo Sphere Viewer v5 markers with data.plan positions, two-way link between panorama yaw/pitch and Leaflet coordinates, virtual-tour arrows, marker CRUD with search and JSON import/export, cubemap vs equirectangular adapters, localStorage persistence; also for a black canvas from a missing CubemapAdapter, marker drift after yaw-to-GPS conversion, and PlanPlugin bounds that do not match the image. Vue 3 + Vite + TypeScript."
tags:
  - vue
  - typescript
  - vite
  - photo-sphere-viewer
  - panorama
  - leaflet
  - virtual-tour
  - webgis
  - demo
---

> **项目地址：** <https://github.com/znlgis/map-360-demo>
>
> **教程：** <https://znlgis.github.io/demos/map-360-demo/>
>
> **依赖版本：** Photo Sphere Viewer 5.15.1（core/markers/plan/cubemap 等插件同版本，取自仓库 `package.json`，截至 2026-10）
>
> **许可证：** 以仓库为准

## 概述

map-360-demo 是一个纯前端演示项目，核心目标是实现 **360° 全景与真实地图的双向联动**：全景由 Photo Sphere Viewer v5 渲染，右下角平面地图由 Leaflet（经 PlanPlugin 嵌入）渲染，两者通过标记的 `data.plan` 字段互相关联。项目基于 Vue 3 + Vite + TypeScript，不依赖后端，标记数据通过 `localStorage` 持久化，克隆后即可本地运行。配套教程共 12 章，覆盖组件封装、联动机制、坐标换算、状态管理与二次开发。

### 核心特性

| 特性 | 说明 |
|------|------|
| 多种全景格式 | 等距圆柱（Equirectangular）4 个互连场景 + 立方体贴图（Cubemap）独立场景 |
| 虚拟导览 | 等距圆柱场景间 3D 箭头导航，点击带转场动画切换场景 |
| 地图联动 | 全景标记与 Leaflet 地图热点双向联动，点击地图热点自动旋转视角 |
| 标记管理 | 添加/编辑/删除/搜索/导入导出 JSON/恢复默认，自动持久化 |
| 功能面板 | 自动旋转、罗盘、陀螺仪、设置面板、缩略图画廊实时开关 |
| 坐标换算 | 全景 yaw/pitch 与 GPS 经纬度互推（`src/utils/geo.ts`） |
| 安全处理 | 标记名称/描述 HTML 转义，防 XSS 注入 |

### 技术栈

| 依赖 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5 | UI 框架（组合式 API + `<script setup>`） |
| Vite | 8.x | 构建工具 |
| TypeScript | 6.0 | 类型系统 |
| @photo-sphere-viewer/* | 5.15 | 核心 + markers/plan/virtual-tour/gallery/autorotate/compass/gyroscope/settings 插件与 cubemap 适配器 |
| leaflet | 1.9 | 平面地图渲染（由 PlanPlugin 内置） |

## 环境准备 / 快速开始

```bash
git clone https://github.com/znlgis/map-360-demo.git
cd map-360-demo
npm install          # 安装依赖
npm run dev          # 开发服务器，默认 http://localhost:5173
npm run typecheck    # 仅类型检查（vue-tsc -b，含 vite.config.ts）
npm run build        # 类型检查 + 生产构建，输出 dist/
npm run preview      # 预览生产构建
```

- Node.js 20+（Vite 8 对 Node 版本要求较高，教程建议 20 或更高）
- 全景图片与地图瓦片均来自公共资源（PSV 官方 CDN / OpenStreetMap），**运行与预览均需联网**

## 项目结构

```text
map-360-demo/
├── public/icons/link-pin.svg      # 场景跳转标记图标（本地资源）
├── src/
│   ├── App.vue                    # 根组件：编排状态、跳转逻辑、导入导出
│   ├── main.ts                    # 入口
│   ├── components/
│   │   ├── PsvContainer.vue       # 核心：PSV Viewer 生命周期与全部插件
│   │   ├── FeaturePanel.vue       # 功能演示面板（各项能力开关）
│   │   ├── SceneSelector.vue      # 场景下拉选择
│   │   ├── MarkerModal.vue        # 添加/编辑标记弹窗
│   │   ├── MarkerList.vue         # 底部标记列表（搜索/折叠/导入导出）
│   │   └── ToastHost.vue          # 全局 Toast 反馈
│   ├── composables/
│   │   ├── useAppState.ts         # 全局状态 + localStorage 持久化 + 导入导出
│   │   ├── useAddMarkerFlow.ts    # 添加/编辑标记状态机
│   │   └── useToast.ts            # Toast 单例
│   ├── data/scenes.ts             # 预设场景、默认标记、PSV 配置转换
│   ├── styles/psv.css             # PSV 全局样式覆盖
│   ├── types/index.ts             # Scene/MarkerData/FeatureFlags 等类型
│   └── utils/geo.ts               # 方位角换算（点击位置 <-> 经纬度）
├── vite.config.ts                 # 别名 @ -> ./src、manualChunks 分包
└── tsconfig*.json                 # project references（app/node）
```

## 核心功能实现

### 1. PsvContainer：PSV 封装与插件体系

`PsvContainer.vue` 是唯一直接操作 Photo Sphere Viewer 的组件，负责创建/销毁 viewer、注册全部插件，并通过 `defineExpose` 暴露语义化接口：

```typescript
viewer = new Viewer({
  container: containerRef.value,
  panorama: props.scene.panorama,
  caption: props.scene.name,
  navbar: ['zoom', 'fullscreen', 'caption', 'gallery', 'markers', 'markersList', 'settings'],
  plugins: [
    PlanPlugin.withConfig({
      coordinates: props.scene.coordinates,
      bearing: props.scene.bearing,
      defaultZoom: props.scene.defaultZoom,
      position: 'bottom left',
      visibleOnLoad: true,
    }),
    MarkersPlugin.withConfig({}),
    // 等距圆柱场景才挂虚拟导览；立方体贴图场景独立渲染
    VirtualTourPlugin.withConfig({
      dataMode: 'client',
      positionMode: 'manual',
      renderMode: '3d',
      nodes: props.scenes
        .filter(s => (s.adapter ?? 'equirectangular') === 'equirectangular')
        .map(toTourNode),
      startNodeId: props.scene.id,
    }),
    // GalleryPlugin / AutorotatePlugin / CompassPlugin / GyroscopePlugin / SettingsPlugin
  ],
})

// 立方体贴图场景：挂 CubemapAdapter（六面独立图片）
if (isCubemap) viewerConfig.adapter = CubemapAdapter

markersPlugin = viewer.getPlugin<MarkersPlugin>(MarkersPlugin)
planPlugin = viewer.getPlugin<PlanPlugin>(PlanPlugin)

defineExpose({ gotoMarker })   // 语义化接口，不直接暴露插件实例
```

### 2. 全景与地图双向联动

联动的关键是标记的 `data.plan` 字段：`position`（yaw/pitch）决定全景位置，`data.plan.coordinates` 决定地图热点位置，二者通过同一个 marker id 关联：

```typescript
// src/data/scenes.ts：标记配置转换
export function toPsvMarkerConfig(m: MarkerData): PsvMarkerConfig {
  return {
    id: m.id,
    tooltip,
    content: `<div class="psv-marker-content"><h3>${safeName}</h3><p>${safeDesc}</p></div>`,
    position: m.position,
    image: isLink ? LINK_ICON : BASE_URL + 'pictos/pin-blue.png',
    size: { width: 32, height: 32 },
    anchor: 'bottom center',
    data: {
      plan: {                 // PlanPlugin 读取此字段在地图上渲染热点
        coordinates: m.coordinates,
        size: 28,
        image: isLink ? LINK_ICON : BASE_URL + 'pictos/pin-blue.png',
      },
    },
  }
}
```

全景标记与地图热点点击统一 emit `marker-click`，由 App 决定行为（info 标记旋转视角、link 标记切换场景）：

```typescript
markersPlugin?.addEventListener('select-marker', ({ marker }) => emit('marker-click', marker.id))

planPlugin?.addEventListener('select-hotspot', ({ hotspotId }) => {
  if (hotspotId.startsWith('__marker__')) {
    emit('marker-click', hotspotId.slice('__marker__'.length))
  }
})

// info 标记：旋转视角（MarkersPlugin.gotoMarker）
function gotoMarker(id: string) { markersPlugin?.gotoMarker(id) }
// link 标记：switchScene(marker.targetSceneId)
```

场景切换时复用 viewer，仅更新地图参数与全景图（适配器变化时才重建）：

```typescript
planPlugin?.setOptions({ bearing: props.scene.bearing })
planPlugin?.setCoordinates(props.scene.coordinates)
planPlugin?.setZoom(props.scene.defaultZoom)
virtualTour?.setCurrentNode(id)     // 等距圆柱场景走虚拟导览节点
viewer?.setPanorama(props.scene.panorama, { caption: props.scene.name, showLoader: true })
```

### 3. 标记管理：添加/编辑状态机

`useAddMarkerFlow.ts` 维护选点、预览与弹窗状态，并协调全景与地图两种选点方式：

```typescript
const adding = ref(false)                                              // 添加模式
const pendingPosition = ref<{ yaw: number, pitch: number } | null>(null)
const pendingCoords = ref<[number, number] | null>(null)

// 全景点击选点：保存球形坐标，估算经纬度
function onClickEmpty(position: { yaw: number, pitch: number }) {
  pendingPosition.value = position
  pendingCoords.value = estimateGps(scene, position.yaw, position.pitch)
}

// 地图点击选点：保存经纬度，反推 yaw 让预览朝向正确
function onMapPick(coords: [number, number]) {
  pendingCoords.value = coords
  pendingPosition.value = { yaw: yawFromGps(scene, coords), pitch: 0 }
}
```

预览 pin 使用固定 id `__preview__`、红色 `pin-red.png` 与 `psv-marker--preview` 脉冲动画类；`markersPlugin.setMarkers()` 会清空包括预览在内的标记，因此同步场景数据后需按需重新补挂预览。

### 4. 坐标换算：米空间分解

`src/utils/geo.ts` 的核心原则：经度/纬度每度地面距离相差 cos(纬度) 因子，必须先在米空间按方位角分解，再换算回度：

```typescript
const M_PER_DEG_LAT = 110574                                      // 每度纬度米数
const mPerDegLng = (lat: number) => 111320 * Math.cos((lat * Math.PI) / 180)

// 全景点击 -> 经纬度：距离随 pitch 线性估算，钳制到 [120, 1100] 米
export function estimateGps(scene: Scene, yaw: number, pitch: number): [number, number]

// 地图坐标 -> 全景 yaw：先求真实方位角，再扣除场景 bearing，归一到 (-π, π]
export function yawFromGps(scene: Scene, coords: [number, number]): number
```

### 5. 状态与持久化：模块级单例

项目不使用 Pinia；`useAppState.ts` 以模块顶层 `ref` 实现单例，多处调用共享同一份响应式数据：

```typescript
const STORAGE_KEY = 'map-360-demo:markers:v1'

// 深度监听自动持久化；配额溢出等异常静默忽略
watch(markers, (val) => {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(val)) } catch { /* 静默处理 */ }
}, { deep: true })

// 读取时逐字段校验（isValidMarker），非法数据回退默认标记
// 导入时过滤非法/场景缺失标记、重新分配 id 后合并
```

## 典型工作流

### 端到端：新增一个场景并接入虚拟导览与地图联动

```typescript
// 1. 在 src/data/scenes.ts 的 SCENES 中追加场景
{
  id: 'my-scene',
  name: '我的新场景',
  description: '拍摄点描述',
  panorama: '/panoramas/my-scene.jpg',   // public/ 下资源；立方体贴图传六面对象并设 adapter: 'cubemap'
  thumbnail: '/panoramas/my-scene-thumb.jpg',  // 画廊缩略图，缺省回退全景图
  coordinates: [116.397, 39.908],        // [lng, lat] 拍摄点
  bearing: '90deg',                      // 全景正前方对应的地理方位角
  defaultZoom: 15,
  links: [{ targetSceneId: 'mercantour', position: { yaw: 1.0, pitch: 0.1 }, name: '返回默康图尔' }],
}
```

1. 准备全景图片放到 `public/` 或使用 CDN 地址（Cubemap 场景需六面图并设置 `adapter: 'cubemap'`）
2. 在已有场景的 `links` 中添加指向新场景的 `SceneLink`（可选，用于 3D 箭头导航）
3. 在 `DEFAULT_MARKERS` 中按需补充初始标记（`sceneId` 指向新场景）
4. `npm run dev` 验证：顶部下拉、底部画廊、3D 箭头、地图中心/方位角同步、标记热点联动
5. `npm run typecheck` 与 `npm run build` 确认类型与构建通过

### 端到端：添加标记并确认持久化

1. 点击「添加标记」进入添加模式
2. 点击全景空白处选点（自动估算经纬度），或点击右下角地图精确定位（自动反推 yaw）
3. 红色脉冲预览 pin 即时反馈；弹窗中确认名称/描述/类型（info 或 link + 目标场景）
4. 确认后写入 `markers`，watch 自动持久化到 `localStorage`（key：`map-360-demo:markers:v1`）
5. 刷新页面验证标记仍在；「导出」下载 JSON，「导入」合并外部 JSON

## 最佳实践 / 常见陷阱

- **不要使用 `configureLeaflet` 选项**：它的语义是「完全接管 Leaflet 配置」，传入后默认 OSM 底图不会被添加，地图会变成灰色空面板；点击监听应在创建后通过 `planPlugin.getLeaflet().on('click', ...)` 挂载
- **场景切换复用 viewer**：仅当适配器变化（等距圆柱 <-> 立方体贴图）时才重建，避免丢失 WebGL 上下文与瓦片缓存
- **米空间分解**：直接对经纬度做方位角分解会让标记方向偏转（中纬度可达约 10 度）
- **预览 pin 与全量刷新**：`setMarkers()` 会清空包括预览 pin 在内的标记，同步场景数据后要按需恢复预览
- **HTML 转义**：标记名称/描述渲染进 PSV tooltip 前必须转义（`escapeHtml`），防止注入
- **编辑模式避免重叠**：位置未变化时不显示预览 pin，避免与已有标记重叠
- **Cubemap 六面映射**：采用 three.js 命名（px/nx/py/ny/pz/nz），PSV 按材质顺序 [left,right,top,bottom,back,front] 对应 [px,nx,py,ny,pz,nz]
- **导入合并策略**：校验数组结构、过滤非法标记、丢弃场景不存在与 link 目标缺失的标记、重新分配 id

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 全景图或地图瓦片加载失败 | 图片与瓦片来自公共资源（PSV CDN / OpenStreetMap），确认网络可访问外网 |
| 5173 端口被占用 | 使用 `npm run dev -- --port 8080` 指定其他端口 |
| 提示 Node 版本过低 | 升级到 Node 20+（Vite 8 要求较高 Node 版本），可用 nvm 切换 |
| 地图显示为灰色空面板 | 检查是否误用 `configureLeaflet`；移除该选项，改用 `getLeaflet()` 挂载事件 |
| 导入 JSON 后标记没有全部出现 | 导入会过滤非法数据、场景不存在及 link 目标缺失的标记，并重新分配 id；用「导出」的 JSON 做对照检查 |
| 刷新后标记丢失或想还原 | 数据由 `localStorage` 持久化；「恢复默认」深拷贝 `DEFAULT_MARKERS` 一键还原 |
| 陀螺仪开关无效 | 仅移动设备浏览器支持且需用户授权，不可用时会触发 gyroscope-error 提示 |
| 场景切换后地图未同步 | 检查新场景的 `coordinates`/`bearing`/`defaultZoom` 配置是否有效 |

## AI 使用建议

1. **核心文件**：`src/components/PsvContainer.vue` 是唯一直接操作 Photo Sphere Viewer 的组件（创建 / 销毁 viewer、注册全部插件），联动状态在 `src/composables/useAppState.ts`，场景与默认标记数据在 `src/data/scenes.ts`。
2. **常见改造点**：换全景内容改 `src/data/scenes.ts`（新场景放入 `public/`，等距圆柱场景补 `links` 接入虚拟导览）；坐标换算算法集中在 `src/utils/geo.ts`；类型定义在 `src/types/index.ts`。
3. **联动约定**：标记的 `position`（yaw/pitch）与 `data.plan.coordinates` 通过同一 id 关联全景与地图；全景 / 地图点击统一 emit `marker-click` 由 `App.vue` 分发（info 旋转视角、link 切换场景）。
4. **不要用 `configureLeaflet`**：会导致默认 OSM 底图不加载（灰色空面板）；地图点击监听用 `planPlugin.getLeaflet().on('click', ...)`。
5. **持久化与导入**：标记存 localStorage（key `map-360-demo:markers:v1`），改标记结构时同步更新 `isValidMarker` 校验与「恢复默认」逻辑；导入会过滤非法数据并重新分配 id。
6. **插件细节参考**：PSV 插件（markers / plan / virtual-tour 等）的配置与 API 见同批 `3d/photo-sphere-viewer` 技能。

## 相关技能

- **photo-sphere-viewer** — PSV v5 全景查看器能力技能，本项目的全景内核：[../../3d/photo-sphere-viewer/SKILL.md](../../3d/photo-sphere-viewer/SKILL.md)
- **openlayers** — Web 端二维地图渲染与交互（替换或扩展 Leaflet 方案的参考）：[../../gis/openlayers/SKILL.md](../../gis/openlayers/SKILL.md)
- **openlayers-vue3-demo** — 同批演示：Vue 3 + OpenLayers（vue3-openlayers）声明式地图与 GeoServer 图层树：[../openlayers-vue3-demo/SKILL.md](../openlayers-vue3-demo/SKILL.md)

## 参考资源

- [map-360-demo GitHub 仓库](https://github.com/znlgis/map-360-demo) — 源码与 README
- [map-360-demo 教程（12 章）](https://znlgis.github.io/demos/map-360-demo/) — 项目结构、联动机制、坐标换算与二次开发
- [Photo Sphere Viewer 官方文档](https://photo-sphere-viewer.js.org/) — 核心与插件 API
- [MarkersPlugin 文档](https://photo-sphere-viewer.js.org/plugins/markers.html) — 标记配置与 `gotoMarker`
- [PlanPlugin 文档](https://photo-sphere-viewer.js.org/plugins/plan.html) — Leaflet 平面地图与 `data.plan`
- [Leaflet 官方文档](https://leafletjs.com/) — 底图与交互事件

---
name: ai-water-front
description: "Use when building a Vue 3 smart-water map dashboard demo that pairs OpenLayers with a Dify AI chat assistant — natural-language queries rendered as GeoJSON highlights, GeoServer REST layer management, streaming SSE replies, and resizable panels. Stack: Vue 3.3 + Vite 4 + ol 8 + axios, dev proxy carrying Basic auth to GeoServer."
tags:
  - vue
  - javascript
  - vite
  - openlayers
  - webmapping
  - geojson
  - geoserver
  - dify
  - dashboard
---

> **项目地址：** <https://github.com/znlgis/ai-water-front>
>
> **教程：** <https://znlgis.github.io/demos/ai-water-front/>
>
> **许可证：** LGPL-2.1（以仓库为准）

## 概述

AI 水务前端（ai-water-front）是一个基于 Vue 3 + OpenLayers + Dify AI 的智能水务地理信息系统演示项目。地图部分使用 OpenLayers 原生 API 加载 OpenStreetMap 底图（默认北京视图）。AI 助手对接 Dify Chat Messages 接口，以 SSE 流式输出回复，回复中的 GeoJSON 会被自动提取、转换投影后渲染并高亮闪烁。图层管理通过 Vite 开发代理调用 GeoServer REST API，凭据只在代理层注入。项目同时演示可拖拽面板布局与 localStorage 状态持久化。

### 核心特性

| 特性 | 说明 |
|------|------|
| 地图展示 | `ol` 8 + OSM 底图，默认中心北京 `[116.4074, 39.9042]`，zoom 10 |
| AI 助手 | Dify `/v1/chat-messages`，支持 `streaming` / `blocking` 两种模式，可取消生成 |
| GeoJSON 渲染 | 从回复中提取几何数据，自动贴合视图并红框闪烁高亮约 5 秒 |
| 图层管理 | 拉取 GeoServer `/rest/layers`，按几何类型排序（面 / 线 / 点）加载 WMS |
| GeoServer 代理 | Vite 代理 `/geoserver` → `127.0.0.1:8765`，Basic 认证在代理层注入 |
| 面板布局 | 左右 / 上下可拖拽分隔条，尺寸保存到 localStorage |
| 调试工具 | DEV 模式注入 `window.testGeoJson` / `window.clearGeoJsonLayers` |

## 环境准备 / 快速开始

### 环境要求

- Node.js >= 16.0.0，npm >= 7.0.0（可用 nvm-windows 管理多版本）
- 可选：Docker Desktop（本地运行 GeoServer + PostGIS）
- 可选：Dify 账号或自建 Dify 服务（用于获取 API Key）

### 安装与启动

```bash
# 1. 克隆并安装依赖
git clone https://github.com/znlgis/ai-water-front.git
cd ai-water-front
npm install

# 2. 新建 .env.local（优先于 .env 读取，且不会被提交），配置 Dify
# VITE_DIFY_API_KEY=app-xxxxxxxxxxxx
# VITE_DIFY_BASE_URL=https://api.dify.ai   # 自建 Dify 改为自己的服务地址

# 3. 启动开发服务器（默认 http://localhost:3000，自动打开浏览器）
npm run dev

# 4. 生产构建与本地预览
npm run build
npm run preview
```

### 验证

- 打开页面后地图中心应为北京，可拖拽平移、滚轮缩放。
- AI 助手面板若提示「未配置 VITE_DIFY_API_KEY」，说明环境变量未生效，需检查 `.env.local` 并重启 dev server。
- 图层面板能列出 GeoServer 图层（要求 GeoServer 已在 `127.0.0.1:8765` 运行）。

### 可选：Docker 启动 GeoServer + PostGIS

```bash
docker pull postgis/postgis
docker run -d -p 5432:5432 --name postgis \
  -e POSTGRES_PASSWORD=postgres -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v //d/docker/data/postgis:/var/lib/postgresql/data postgis/postgis

docker pull kartoza/geoserver
docker run -d -p 8765:8080 --name geoserver --link postgis:postgis \
  -e SAMPLE_DATA=true -e GEOSERVER_ADMIN_PASSWORD=geoserver \
  -e GEOSERVER_DATA_DIR=/data/geoserver/data_dir \
  -v //d/docker/data/geoserver:/data/geoserver/data_dir kartoza/geoserver
```

启动后访问 `http://localhost:8765/geoserver`，默认账号 `admin` / `geoserver`。

## 项目结构

```text
ai-water-front/
├── .env                        # Dify 配置占位（VITE_DIFY_BASE_URL / VITE_DIFY_API_KEY）
├── vite.config.js              # 端口 3000 + /geoserver 代理（Basic 认证、路径重写）
├── index.html
└── src/
    ├── main.js                 # 应用入口（createApp + mount）
    ├── App.vue                 # 布局装配：Header / 左面板 / 地图 / Footer，拖拽分隔条
    ├── mapInstance.js          # 全局地图实例（setMap / mapInstance）
    ├── style.css
    ├── components/
    │   ├── DemoMap.vue         # OpenLayers 地图（OSM 底图 + 北京默认视图）
    │   ├── layout/
    │   │   ├── AppHeader.vue
    │   │   └── AppFooter.vue
    │   └── panels/
    │       ├── LayerPanel.vue        # GeoServer 图层列表（点/线/面标签，WMS 加载）
    │       └── AIAssistantPanel.vue  # 对话界面（流式渲染、表格、取消、清除）
    ├── geoserver/
    │   ├── GeoServerRestApi.js # REST API 聚合入口（about + layers）
    │   ├── About.js            # /rest/about/{manifest,status,system-status,version}
    │   └── Layers.js           # /rest/layers、/rest/layergroups
    ├── services/
    │   ├── difyClient.js       # Dify Chat API 封装（SSE 流式解析 + 取消）
    │   └── geoJsonService.js   # GeoJSON 提取、渲染、高亮闪烁、清除
    └── utils/
        └── geoJsonTestUtils.js # DEV 模式控制台测试工具
```

## 核心功能实现

### 地图初始化与全局实例

```javascript
// src/components/DemoMap.vue
import 'ol/ol.css'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'
import { fromLonLat } from 'ol/proj'
import { setMap } from '../mapInstance.js'

const osmLayer = new TileLayer({
  source: new OSM(),
  properties: { name: 'OpenStreetMap', isBase: true }
})

const map = new Map({
  target: 'map',
  layers: [osmLayer],
  view: new View({
    center: fromLonLat([116.4074, 39.9042]), // 北京
    zoom: 10
  })
})
setMap(map)
```

```javascript
// src/mapInstance.js —— 模块级变量，供 services / panels 跨组件复用
export let mapInstance = null
export function setMap(instance) { mapInstance = instance }
```

### Dify 流式对话客户端

```javascript
// src/services/difyClient.js —— 调用方式
import { sendChatMessage } from './services/difyClient'

sendChatMessage('查询北京市的水系分布', {
  onMessage: (chunk) => { /* 流式增量文本，逐段追加到消息气泡 */ },
  onCompleted: () => { /* 回复完成 */ },
  onError: (err) => { /* HTTP 错误，或 abort 后的「已取消」 */ },
  onGeoJsonDetected: (geoJson) => { /* 流结束时检出 GeoJSON */ },
  abortSignal: controller.signal,           // AbortController 支持取消
  inputs: { area: '北京市', dataType: 'water_system' }, // 传给 Dify 的自定义变量
  stream: true,                             // streaming；false 则用 blocking
  user: 'web-user'
})
```

实现要点：

- 请求 `POST {VITE_DIFY_BASE_URL}/v1/chat-messages`，头为 `Authorization: Bearer <API_KEY>`，体含 `query`、`response_mode`、`user`、`inputs`。
- SSE 解析按行读取：仅处理 `data:` 前缀行，`answer` 字段为增量文本，收到 `[DONE]` 视为结束。
- 全量文本累积在 `fullResponseText`，流结束后再执行一次 GeoJSON 提取，避免遗漏。

### GeoJSON 提取与地图渲染

```javascript
// src/services/geoJsonService.js —— 从 AI 回复中提取几何数据
// 约定回复结构：JSON 文本 { "data": "[{ \"geom\": \"{...GeoJSON...}\" }]" }
export function extractGeoJsonFromResponse(responseText) {
  try {
    const parsedData = JSON.parse(responseText)
    const geoJson = []
    if (parsedData?.data) {
      const parsed = JSON.parse(parsedData.data)
      const arr = Array.isArray(parsed) ? parsed : parsed ? [parsed] : []
      for (const item of arr) geoJson.push(JSON.parse(item.geom))
    }
    return geoJson
  } catch (error) {
    console.warn('提取 GeoJSON 时出错:', error)
    return null
  }
}
```

```javascript
// displayGeoJsonOnMap：标准化为 FeatureCollection 后读入矢量图层
const featureCollection = normalizeToFeatureCollection(geoJsonData)

const vectorSource = new VectorSource({
  features: new GeoJSON().readFeatures(featureCollection, {
    featureProjection: 'EPSG:3857', // 地图投影
    dataProjection: 'EPSG:4326'     // 数据投影（经纬度）
  })
})

const vectorLayer = new VectorLayer({
  source: vectorSource,
  style: createHighlightStyle(), // 红色虚线 stroke + 半透明 fill + Circle 点样式
  properties: { name: 'geojson-highlight', isGeoJsonLayer: true, timestamp: Date.now() }
})

mapInstance.addLayer(vectorLayer)
addBlinkingAnimation(vectorLayer) // requestAnimationFrame 调整 setOpacity，闪烁 5 秒
fitViewToGeoJson(vectorSource)    // 视图贴合数据范围
```

```javascript
// 清除全部 AI 渲染图层
export function clearGeoJsonLayers() {
  const layersToRemove = []
  mapInstance.getLayers().forEach(layer => {
    if (layer.get('isGeoJsonLayer')) layersToRemove.push(layer)
  })
  layersToRemove.forEach(layer => mapInstance.removeLayer(layer))
}
```

### GeoServer REST 集成与开发代理

```javascript
// src/geoserver/GeoServerRestApi.js —— 聚合入口
export default class GeoServerRestApi {
  constructor() {
    this.about = new About()    // 服务器信息
    this.layers = new Layers()  // 图层与图层组
  }
}
```

```javascript
// src/geoserver/Layers.js —— 统一走相对路径，由 Vite 代理转发
const response = await axios.get('/geoserver/rest/layers')             // 图层列表
const groups = await axios.get('/geoserver/rest/layergroups')          // 图层组列表
const group = await axios.get(`/geoserver/rest/layergroups/${name}`)   // 组内 published 明细
```

```javascript
// vite.config.js —— 代理注入 Basic 认证，业务代码无需携带凭据
import base64 from 'base-64'

const AUTH = { user: 'admin', pass: 'geoserver' }
const AUTH_BASE64 = base64.encode(`${AUTH.user}:${AUTH.pass}`)

server: {
  port: 3000,
  open: true,
  proxy: {
    '/geoserver': {
      target: 'http://127.0.0.1:8765/geoserver',
      headers: { Accept: 'application/json', Authorization: `Basic ${AUTH_BASE64}` },
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/geoserver/, '')
    }
  }
}
```

LayerPanel.vue 挂载后拉取 `/rest/layers`，把图层按几何类型排序（面 → 线 → 点），并结合 bbox 与 `transformExtent` 以 WMS 瓦片图层加载到地图。

### 面板布局与调试工具

```javascript
// App.vue —— 拖拽结束保存尺寸，挂载时读取
localStorage.setItem('layerPanelHeight', String(topHeight.value))
localStorage.setItem('leftPanelWidth', String(leftWidth.value))

const storedHeight = parseInt(localStorage.getItem('layerPanelHeight') || '0', 10)
const storedWidth = parseInt(localStorage.getItem('leftPanelWidth') || '0', 10)
```

```javascript
// App.vue —— DEV 模式自动加载控制台测试工具
if (import.meta.env.DEV) {
  import('./utils/geoJsonTestUtils.js')
}
```

## 典型工作流

端到端：自然语言查询 → 流式回复 → GeoJSON 自动上屏 → 清除高亮。

1. 准备环境：启动 GeoServer（可选），确认 `.env.local` 中已配置 `VITE_DIFY_API_KEY`，执行 `npm run dev`。
2. 在 AI 助手面板输入「查询北京市的水系分布」，按 Enter 发送（Shift+Enter 换行）。
3. `sendChatMessage` 建立 SSE 连接，`onMessage` 把增量文本逐段追加到消息气泡；生成中可点击「取消」中断请求。
4. Dify 按约定返回 JSON（`data[].geom` 为 GeoJSON 字符串），流结束触发 `onGeoJsonDetected`。
5. `displayGeoJsonOnMap` 将几何标准化为 FeatureCollection，按 `EPSG:4326 → EPSG:3857` 投影加为高亮图层，视图自动定位，图层闪烁约 5 秒。
6. 点击面板「清除」按钮调用 `clearGeoJsonLayers()`，移除所有带 `isGeoJsonLayer` 属性的图层。

开发调试（DEV 模式控制台）：

```javascript
window.testGeoJson(window.testData.point)     // 渲染测试点
window.testGeoJson(window.testData.polygon)   // 渲染测试面
window.clearGeoJsonLayers()                   // 清除高亮图层
```

## 最佳实践 / 常见陷阱

- API Key 只放 `.env.local`（不入库）；仓库自带的 `.env` 是示例配置，使用前替换为自己的 Key。
- SSE 解析要处理跨 chunk 的「半行」：用 buffer 累积字符串并按 `\n` 切分，只解析 `data:` 行。
- GeoJSON 提取必须容错：AI 回复可能不是约定结构，解析失败返回 `null`，调用方不要抛错中断对话。
- 投影别搞反：`dataProjection` 是数据坐标系（示例约定 EPSG:4326），`featureProjection` 是地图坐标系（ol 默认 EPSG:3857）。
- 大数据量不要用 Overlay 逐点渲染，改用矢量图层一次性渲染（项目做法）。
- GeoServer 凭据只配置在 `vite.config.js` 代理层；生产部署改由 Nginx 代理注入 `Authorization` 头。
- 闪烁动画结束后要恢复 `setOpacity(1)`，否则图层会停留在半透明状态。
- `mapInstance` 是模块级单例，地图挂载前为 `null`，服务函数使用前需判空。

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `npm install` 失败或缓慢 | `npm cache clean --force` 后重装，或切换镜像 `npm config set registry http://registry.npmmirror.com` |
| AI 助手一直提示未配置 | 检查 `.env.local` 是否存在且含 `VITE_DIFY_API_KEY`；改环境变量后需重启 dev server |
| 地图空白 | OSM 瓦片依赖外网；同时检查控制台报错与 `ol` 依赖是否安装完整 |
| GeoServer 图层加载失败 | 确认 GeoServer 运行在 8765 端口，代理 `target` 与账号密码匹配 |
| AI 回复正常但地图无高亮 | 回复须匹配 `{data:[{geom}]}` 约定；查看控制台「提取 GeoJSON 时出错」告警 |
| 面板尺寸不保存 | 检查浏览器是否禁用了 localStorage |
| 生产环境 GeoServer 返回 401 | Nginx 代理需带上 `Authorization`（Base64 Basic）头，不能只代理路径 |
| `npm run dev` 端口被占用 | 修改 `vite.config.js` 中的 `server.port` |

## 相关技能

- **openlayers** — OpenLayers 核心地图库（图层、投影、样式、交互）：[../../gis/openlayers/SKILL.md](../../gis/openlayers/SKILL.md)
- **dify** — Dify 平台：LLM 应用编排与 Chat API：[../../ai/dify/SKILL.md](../../ai/dify/SKILL.md)
- **geoserver-rest-api** — GeoServer REST API 完整参考（图层 / 样式 / 工作区管理）：[../../gis/geoserver-rest-api/SKILL.md](../../gis/geoserver-rest-api/SKILL.md)
- **openlayers-vue3-demo** — 同批演示项目：vue3-openlayers 声明式组件 + GeoServer 图层树的另一套写法：[../openlayers-vue3-demo/SKILL.md](../openlayers-vue3-demo/SKILL.md)

## 参考资源

- [ai-water-front GitHub](https://github.com/znlgis/ai-water-front) — 源码与提交历史
- [博客教程索引](https://znlgis.github.io/demos/ai-water-front/) — 项目概述 / 环境搭建 / 项目启动 / 核心功能详解 / 开发指南
- [核心功能详解教程](https://znlgis.github.io/demos/ai-water-front/核心功能详解/) — 地图、GeoJSON、Dify、GeoServer 模块逐一拆解
- [OpenLayers 官方文档](https://openlayers.org/doc/)
- [Dify API 参考](https://docs.dify.ai/api-reference)
- [GeoServer REST API](https://docs.geoserver.org/stable/en/user/rest/)

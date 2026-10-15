---
name: openlayers-vue3-demo
description: "Use when building OpenLayers maps with Vue 3 declarative components (vue3-openlayers) — WMS tile layers, dynamic layer trees loaded from the GeoServer REST API, layer-switcher/zoom/scale-line/context-menu controls, and a Vite dev proxy injecting Basic auth. Bilibili livestream demo for a one-map GIS dashboard on Docker GeoServer + PostGIS."
tags:
  - vue
  - typescript
  - javascript
  - vite
  - openlayers
  - vue3-openlayers
  - webmapping
  - geoserver
  - wms
  - demo
---

> **项目地址：** <https://github.com/znlgis/openlayers-vue3-demo>
>
> **教程：** <https://znlgis.github.io/demos/vue3-openlayers/>
>
> **许可证：** LGPL-2.1（以仓库为准）

## 概述

openlayers-vue3-demo 是 B 站直播配套的 OpenLayers + Vue 3 集成演示项目，围绕「一张图 DEMO」实现最小闭环：地图展示 + GeoServer 图层树。与直接调用 ol 内核 API 的写法不同，本项目全程使用 vue3-openlayers 声明式组件，在模板中完成地图装配。应用启动后通过 GeoServer REST API 拉取图层与图层组，动态生成可勾选的图层树并渲染 WMS 瓦片。配套教程覆盖 NVM / Node 环境、Vue 3 基础环境、OpenLayers 概念、Docker 化 GeoServer / PostGIS / Nginx。适合作为学习 vue3-openlayers 组件库与 GeoServer 对接的起点。

### 核心特性

| 特性 | 说明 |
|------|------|
| 声明式地图 | `Map.OlMap` / `Map.OlView` 等组件装配地图，无需手写 Map 实例 |
| 动态图层树 | 从 `/rest/layers`、`/rest/layergroups` 拉取，模板 `v-for` 生成图层组件 |
| WMS 渲染 | `Sources.OlSourceTileWms` 加载 GeoServer WMS（url 统一为 `/geoserver/wms`） |
| 地图控件 | 图层切换器、缩放、右键菜单、比例尺（`MapControls` 系列） |
| 开发代理 | Vite `/geoserver` 代理 + Basic 认证头，规避 CORS 与明文凭据 |
| Docker 环境 | postgis + kartoza/geoserver + nginx 三容器可复现环境 |
| 一张图定位 | 地图展示（EPSG:4326 视图）+ 服务管理（教程规划的增删改查） |

## 环境准备 / 快速开始

### 环境要求

- Node.js 18+（教程以 20.15.0 为例，可用 nvm-windows 管理；`npm config set registry http://registry.npmmirror.com` 加速）
- Docker Desktop（运行 GeoServer / PostGIS / Nginx）
- 参考教程：<https://znlgis.github.io/demos/vue3-openlayers/>

### 创建与安装

```bash
# 1. 基于 Vite 模板创建 Vue 3 工程
npm create vite@latest openlayers-vue3-demo -- --template vue
cd openlayers-vue3-demo

# 2. 安装组件库与请求依赖
npm install vue3-openlayers axios base-64

# 3. 启动开发服务器
npm run dev

# 4. 生产构建 / 本地预览
npm run build
npm run preview
```

### Docker 环境（GeoServer + PostGIS + Nginx）

```bash
# PostGIS 数据库
docker pull postgis/postgis
docker run -d -p 5432:5432 --name postgis \
  -e POSTGRES_PASSWORD=postgres -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v //d/docker/data/postgis:/var/lib/postgresql/data postgis/postgis

# GeoServer（首次运行加 SAMPLE_DATA=true 导入示例数据；8765:8080 端口映射）
docker pull kartoza/geoserver
docker run -d -p 8765:8080 --name geoserver --link postgis:postgis \
  -e SAMPLE_DATA=true -e GEOSERVER_ADMIN_PASSWORD=geoserver \
  -e GEOSERVER_DATA_DIR=/data/geoserver/data_dir \
  -e GEOWEBCACHE_CACHE_DIR=/data/geoserver/data_dir/gwc \
  -v //d/docker/data/geoserver:/data/geoserver/data_dir \
  -v //d/docker/data/geoserver/gwc:/data/geoserver/data_dir/gwc \
  kartoza/geoserver

# Nginx（8080:80，挂载自定义 nginx.conf）
docker pull nginx
docker run --name nginx -d -p 8080:80 \
  -v //d/docker/data/nginx/nginx.conf:/etc/nginx/nginx.conf:ro nginx
```

### 验证

- 访问 `http://localhost:8765/geoserver`（`admin` / `geoserver`），确认示例图层（如 `ne:countries`）存在。
- `npm run dev` 打开页面：地图可交互，右上角有默认展开的图层切换器与比例尺控件。
- 浏览器 Network 面板中 `/geoserver/rest/layers` 应返回 200 JSON。

## 项目结构

```text
openlayers-vue3-demo/
├── index.html
├── package.json              # vue3-openlayers ^11.2 / vue ^3.5 / vite ^5.4
├── vite.config.js            # /geoserver 代理（Basic 认证头 + 路径重写）
└── src/
    ├── main.js               # createApp + app.use(OpenLayersMap)
    ├── App.vue               # 渲染 DemoMap
    ├── style.css
    ├── components/
    │   └── DemoMap.vue       # 声明式地图 + 动态图层/图层组 + 控件
    └── geoserver/
        ├── GeoServerRestApi.js  # 聚合入口（about + layers）
        ├── Layers.js            # /rest/layers 与 /rest/layergroups
        └── About.js             # /rest/about/{manifest,status,system-status,version}
```

## 核心功能实现

### 插件注册（main.js）

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import OpenLayersMap from 'vue3-openlayers'

const app = createApp(App)
app.use(OpenLayersMap) // 注册 Map / Layers / Sources / MapControls 组件
app.mount('#app')
```

### 声明式地图组件（components/DemoMap.vue）

```vue
<template>
  <Map.OlMap id="map" ref="mapRef" :controls="[]">
    <Map.OlView ref="view" :center="center" :projection="projection" :zoom="zoom" />

    <!-- 动态图层组：来自 GeoServer layer groups -->
    <Layers.OlLayerGroup v-for="group in dynamicLayerGroupList" :key="group.name"
                         :title="group.name" :visible="group.visible">
      <Layers.OlTileLayer v-for="layer in group.layers" :key="layer.name"
                          :title="layer.name" :visible="layer.visible">
        <Sources.OlSourceTileWms :layers="layer.name" :url="layer.url" />
      </Layers.OlTileLayer>
    </Layers.OlLayerGroup>

    <!-- 动态图层：来自 GeoServer layers -->
    <Layers.OlTileLayer v-for="layer in dynamicLayerList" :key="layer.name"
                        :title="layer.name" :visible="layer.visible">
      <Sources.OlSourceTileWms :layers="layer.name" :url="layer.url" />
    </Layers.OlTileLayer>

    <!-- 控件：默认展开的图层切换器 + 缩放 + 右键菜单 + 比例尺 -->
    <MapControls.OlLayerswitcherControl :collapsed="false" />
    <MapControls.OlZoomControl />
    <MapControls.OlContextMenuControl />
    <MapControls.OlScalelineControl />
  </Map.OlMap>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import type MapRef from 'ol/Map'
import { Layers, Map, MapControls, Sources } from 'vue3-openlayers'
import GeoServerRestApi from '../geoserver/GeoServerRestApi'

const center = ref([40, 40])
const projection = ref('EPSG:4326')
const zoom = ref(0)
const dynamicLayerList = ref([])
const dynamicLayerGroupList = ref([])
const mapRef = ref<MapRef | null>(null)

onMounted(async () => {
  try {
    const api = new GeoServerRestApi()

    // 单独图层：仅 ne:countries 默认可见
    const layers = await api.layers.getLayers()
    layers.layers.layer.forEach((layer: any) => {
      dynamicLayerList.value.push({
        name: layer.name,
        url: '/geoserver/wms',
        visible: layer.name === 'ne:countries'
      })
    })

    // 图层组：逐组拉取明细，只保留 publishables 中类型为 layer 的对象
    const groups = await api.layers.getLayerGroups()
    for (const group of groups.layerGroups.layerGroup) {
      const detail = await api.layers.getLayerGroup(group.name)
      const groupLayers: any[] = []
      detail.layerGroup.publishables.published.forEach((item: any) => {
        if (item['@type'] !== 'layer') return
        groupLayers.push({ name: item.name, url: '/geoserver/wms', visible: false })
      })
      dynamicLayerGroupList.value.push({ name: group.name, layers: groupLayers, visible: false })
    }
  } catch (error) {
    console.error('Failed to load layers:', error)
  }
})
</script>
```

### GeoServer REST 封装（geoserver/）

```javascript
// src/geoserver/Layers.js —— axios 使用相对路径，经 Vite 代理转发
export default class Layers {
  async getLayers() {
    const response = await axios.get('/geoserver/rest/layers')
    return response.data // data.layers.layer 为图层数组
  }

  async getLayerGroups() {
    const response = await axios.get('/geoserver/rest/layergroups')
    return response.data // data.layerGroups.layerGroup 为图层组数组
  }

  async getLayerGroup(name) {
    const response = await axios.get(`/geoserver/rest/layergroups/${name}`)
    return response.data // data.layerGroup.publishables.published 为组内对象
  }
}
```

```javascript
// src/geoserver/GeoServerRestApi.js —— 聚合入口
export default class GeoServerRestApi {
  constructor() {
    this.about = new About()    // 服务器信息
    this.layers = new Layers()  // 图层与图层组
  }
}
```

端点速查（均经 `/geoserver` 代理转发）：

| 方法 | 端点 | 用途 |
|------|------|------|
| `about.getManifest()` | `GET /rest/about/manifest` | 已安装模块 / JAR 清单 |
| `about.getStatus()` | `GET /rest/about/status` | 服务器运行状态 |
| `about.getSystemStatus()` | `GET /rest/about/system-status` | 内存 / 线程等系统状态 |
| `about.getVersion()` | `GET /rest/about/version` | GeoServer 版本信息 |
| `layers.getLayers()` | `GET /rest/layers` | 图层列表 |
| `layers.getLayerGroups()` | `GET /rest/layergroups` | 图层组列表 |
| `layers.getLayerGroup(name)` | `GET /rest/layergroups/{name}` | 组内 published 明细 |

### 开发代理（vite.config.js）

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import base64 from 'base-64'

const AUTH = { user: 'admin', pass: 'geoserver' }
const AUTH_BASE64 = base64.encode(`${AUTH.user}:${AUTH.pass}`)

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/geoserver': {
        target: 'http://127.0.0.1:8765/geoserver',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          Authorization: `Basic ${AUTH_BASE64}`
        },
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/geoserver/, '')
      }
    }
  }
})
```

请求 `/geoserver/rest/layers` 时，代理去掉前缀后实际命中 `http://127.0.0.1:8765/geoserver/rest/layers`，认证头由代理注入。

### 与 vue3-openlayers 组件库的关系

- vue3-openlayers 是 ol 内核的 Vue 3 组件封装（本 demo 使用 `^11.2.0`），组件按 ol 模块命名空间组织：`Map.OlMap`、`Layers.OlTileLayer`、`Sources.OlSourceTileWms`、`MapControls.OlZoomControl` 等，属性与 ol 选项一一对应。
- 本 demo 把「图层数据」与「组件渲染」解耦：REST 返回的图层列表映射为数组，模板 `v-for` 生成组件，`visible` 控制显隐。
- 对照项目：ai-water-front 使用原生 ol API 命令式创建地图与图层，可作为两种集成方式的对比样本。

## 典型工作流

从零到「一张图」（端到端）：

1. 用 Docker 启动 PostGIS 与 GeoServer（首次带 `SAMPLE_DATA=true`），浏览器访问 `http://localhost:8765/geoserver` 确认可登录。
2. `npm install && npm run dev` 启动前端；Vite 代理把 `/geoserver/*` 转发到 8765 并注入认证头。
3. 页面挂载后 DemoMap.vue 的 `onMounted` 依次调用 `getLayers()` 与 `getLayerGroups()`；`ne:countries` 默认可见，其余图层与图层组默认 `visible: false`。
4. 在图层切换器中勾选图层 → 对应 `OlTileLayer` 的 `visible` 变为 true → `OlSourceTileWms` 请求 `/geoserver/wms` 瓦片并渲染到地图。
5. 服务管理扩展：沿用同一套 REST 封装继续实现工作区 / 图层的增删改查，达成教程「功能需求」中的树状服务管理能力。

## 最佳实践 / 常见陷阱

- 前端只引用相对路径 `/geoserver/...`，认证头由代理注入；生产部署改为 Nginx 反向代理并同样注入 `Authorization`。
- 视图投影示例为 EPSG:4326（经纬度视图）；若 GeoServer 图层坐标系不同，需在 `OlSourceTileWms` 上显式声明投影或 `SRS` 参数。
- 图层默认 `visible: false` 惰性加载，避免一次请求几十个 WMS 图层造成首屏卡顿。
- `getLayerGroup(name)` 的 `publishables.published` 可能混入非图层对象（如样式），需过滤 `@type !== 'layer'`。
- `Map`、`Layers` 等是 vue3-openlayers 的组件命名空间而非 ol 类；与原生 ol 混用时注意两种 API 的对象类型不同。
- Windows 下 Docker 卷挂载用 `//d/docker/...` 双斜杠表示 D 盘。
- 首次启动 GeoServer 容器需初始化数据目录，等待 1-2 分钟再访问。
- 右键菜单等控件对触屏设备支持有限，移动端需另行适配。

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 图层树为空 | 确认 GeoServer 已启动、代理 `target` 端口（8765）正确；查看 `/geoserver/rest/layers` 返回状态 |
| 控制台 CORS 报错 | 不要直连 `http://localhost:8765`，统一走 `/geoserver` 代理 |
| 图层勾选后无瓦片 | 确认图层已发布且有数据，WMS 图层名与 GeoServer 完全一致（如 `ne:countries`） |
| 401 / 403 认证失败 | 核对 `vite.config.js` 中 AUTH 与 GeoServer 管理员密码是否一致 |
| `docker run` 挂载报错 | Windows 使用 `//d/...` 双斜杠路径，并确认 Docker Desktop 已共享对应盘符 |
| npm 安装缓慢 | 切换镜像 `npm config set registry http://registry.npmmirror.com` |
| 端口冲突（8080 / 8765 / 5432） | 修改 `docker run -p` 映射，并同步调整代理 target |
| 接口 200 但地图空白 | 确认 `#map` 容器有宽高（DemoMap.vue 中 `width/height: 100%`） |

## 相关技能

- **openlayers** — OpenLayers 内核 API（原生写法、投影、样式、交互），理解组件库底层：[../../gis/openlayers/SKILL.md](../../gis/openlayers/SKILL.md)
- **geoserver-rest-api** — GeoServer REST API 完整参考（工作区 / 数据存储 / 图层 / 样式）：[../../gis/geoserver-rest-api/SKILL.md](../../gis/geoserver-rest-api/SKILL.md)
- **geoserver** — GeoServer 服务端安装、配置与 WMS / WFS 发布：[../../gis/geoserver/SKILL.md](../../gis/geoserver/SKILL.md)
- **ai-water-front** — 同批演示项目：原生 ol + Dify AI 助手 + GeoServer 图层管理：[../ai-water-front/SKILL.md](../ai-water-front/SKILL.md)

## 参考资源

- [openlayers-vue3-demo GitHub](https://github.com/znlgis/openlayers-vue3-demo) — 源码
- [博客教程索引](https://znlgis.github.io/demos/vue3-openlayers/) — NVM/Node 环境、Vue 3 基础、OpenLayers 简介、Docker、demo 创建说明
- [Docker 环境安装教程](https://znlgis.github.io/demos/vue3-openlayers/docker/) — PostGIS / GeoServer / Nginx 容器化步骤
- [vue3-openlayers 官方文档](https://vue3openlayers.netlify.app/)
- [OpenLayers 官方文档](https://openlayers.org/doc/)
- [GeoServer REST API](https://docs.geoserver.org/stable/en/user/rest/)

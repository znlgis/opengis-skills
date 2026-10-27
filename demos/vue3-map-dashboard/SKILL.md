---
name: vue3-map-dashboard
description: "Use when running, studying or extending a Vue 3 enterprise data-wall demo — Element Plus layout, Tianditu JS API v4 dark basemap, realtime personnel tracking, QWeather integration, pinyin search, XLSX loading from public/data, composable architecture plus cache and leveled logging; also for a blank Tianditu map from a missing tk key, \"T is not defined\" script loading order, and pinyin filtering that breaks on polyphonic names."
tags:
  - vue
  - javascript
  - vite
  - element-plus
  - dashboard
  - tianditu
  - visualization
  - demo
---

> **项目地址：** <https://github.com/znlgis/vue3-map-dashboard>
>
> **教程：** <https://znlgis.github.io/demos/vue3-map-dashboard/>
>
> **依赖版本：** Vue 3.4 / Element Plus 2.5 / Vite 6 / pinyin-pro 3.27 / xlsx 0.20.3（取自仓库 `package.json`，截至 2026-10）
>
> **许可证：** 以仓库为准

## 概述

vue3-map-dashboard 是一个企业级数据可视化大屏演示项目：Vue 3 Composition API 组织逻辑，Element Plus 提供组件，中心区域嵌入天地图 JavaScript API（深色样式），配合和风天气与 Excel 数据源展示人员实时动态与统计信息。项目无后端依赖，数据来自 `public/data/` 下的 Excel 文件与本地 mock 生成，工程化配套齐全（统一配置、四级日志、内存缓存、拼音搜索）。注意：教程与 README 提到 ECharts，但当前 `package.json` 未内置 echarts 依赖，`ChartCard` 只是带装饰边框的插槽容器。

### 核心特性

| 特性 | 说明 |
|------|------|
| 天地图集成 | Tianditu JS API v4.0，深色 styleJson 底图，缩放/移动事件联动 |
| 人员实时追踪 | 从 Excel 加载人员数据，定时批量更新位置，点击弹出人员详情 |
| 天气系统 | 和风天气 API + 天地图逆地理编码，按位置更新，缓存与失败重试 |
| 实时数据 | mock 生成的统计指标，渲染为统计卡片 |
| 智能搜索 | pinyin-pro 支持中文/拼音/首字母模糊搜索与高亮 |
| 工具系统 | 四级日志 + PerformanceTimer、内存缓存（过期时间 + 容量上限） |
| 配置系统 | dashboard.config.js 按环境切换，主题色集中于 theme.config.js |
| 专利展示 | 专利 PDF 与图片展示（pdfjs-dist 渲染） |

### 技术栈

| 依赖 | 版本 | 用途 |
|------|------|------|
| Vue | ^3.4 | UI 框架（Composition API） |
| Element Plus | ^2.5 | 组件库（含 dark css-vars） |
| Vite | ^8.2.2 | 构建工具（Rolldown codeSplitting 分组） |
| Sass | ^1.103 | 全局样式预处理 |
| dayjs | ^1.11 | 时间格式化 |
| pinyin-pro | ^3.27 | 拼音/首字母搜索 |
| xlsx | 0.20.3 | Excel 数据读取（SheetJS 分发地址） |
| pdfjs-dist | ^6.3 | 专利 PDF 渲染 |
| qweather-icons | ^1.8 | 天气图标 |

## 环境准备 / 快速开始

```bash
git clone https://github.com/znlgis/vue3-map-dashboard.git
cd vue3-map-dashboard
npm install

# 复制 .env.example 为 .env，填入天地图密钥（浏览器端）
# VITE_TIANDITU_KEY=你的天地图密钥

# 在 src/config/map.config.js 的 WEATHER_CONFIG.key 填入和风天气密钥

npm run dev        # http://localhost:3000（host 0.0.0.0，自动打开浏览器）
npm run lint       # ESLint 检查
npm run build      # 生产构建，输出 dist/
npm run preview    # 预览构建结果
```

- Node.js >= 22.12.0（仓库 README 要求；Vite 8 需要 Node 20.19+ / 22.12+）
- 天地图密钥：<https://console.tianditu.gov.cn/> 申请「浏览器端」key，经 `.env` 注入 `index.html` 的 script 标签
- 和风天气密钥：<https://dev.qweather.com/> 申请，免费订阅 baseUrl 用 `https://devapi.qweather.com/v7`
- `.env` 已在 `.gitignore` 中，密钥不要提交仓库

## 项目结构

```text
vue3-map-dashboard/
├── .env.example                   # VITE_TIANDITU_KEY 模板
├── index.html                     # 天地图 script 标签（%VITE_TIANDITU_KEY% 注入）
├── vite.config.js                 # @ 别名、port 3000、codeSplitting 分组
├── public/data/
│   ├── excel/                     # personnel.xlsx / qa-data.xlsx / realtime-data.xlsx
│   └── patent/                    # 专利 PDF 与图片
├── src/
│   ├── main.js                    # createApp + Element Plus（含 dark css-vars）
│   ├── App.vue
│   ├── views/Dashboard.vue        # 主仪表盘：头部/地图/弹窗/统计卡片编排
│   ├── components/
│   │   ├── Header/                # 头部（时间、天气、菜单）
│   │   ├── Map/                   # 天地图组件（T.Map + 深色样式 + 人员标注）
│   │   ├── ChartCard/ StatCard/   # 卡片容器与统计卡片
│   │   ├── SearchBox/             # 智能搜索框
│   │   └── PersonnelDialog/ PatentDialog/ AnswerDialog/   # 各类弹窗
│   ├── composables/
│   │   ├── usePersonnel.js        # 人员数据加载与定时位置更新
│   │   ├── useWeather.js          # 天气获取、缓存与重试
│   │   └── useRealtimeData.js     # 实时统计刷新
│   ├── config/
│   │   ├── index.js               # 大屏标题与菜单
│   │   ├── dashboard.config.js    # 性能/间隔/日志/缓存配置（getConfig 环境切换）
│   │   ├── map.config.js          # 天地图与和风天气配置
│   │   └── theme.config.js        # 主题色与图表色板
│   ├── utils/                     # logger/cache/search/personnel/weather/patent/date/mock
│   └── assets/styles/global.scss  # 全局样式
```

## 核心功能实现

### 1. Composables 架构

逻辑拆分在三个可复用组合式函数中，`Dashboard.vue` 通过 `Promise.all` 并行初始化：

```javascript
// src/views/Dashboard.vue
const { personnelMarkers, showPersonnel, initPersonnelData } = usePersonnel()
const { weatherData, showWeather, updateWeather } = useWeather()
const { realtimeStats, loadRealtimeStats } = useRealtimeData()

// 并行加载数据以提高性能
await Promise.all([loadRealtimeStats(), initPersonnelData()])
```

- `usePersonnel`：`loadPersonnelDataFromExcel()` 读取 Excel → `convertPersonnelToMarkers()` 转地图标注；按 `config.personnel.enableAutoUpdate` 启动定时器，组件卸载自动清理
- `useWeather`：按经纬度（保留 2 位小数）生成缓存键，未命中再调用 `getWeatherByLocation`；失败按 `retryAttempts` 重试
- `useRealtimeData`：`generateRealtimeStats()` 生成统计数据，支持自动刷新开关

### 2. 天地图集成（Map 组件）

```javascript
// src/components/Map/index.vue
if (typeof T === 'undefined') {
  logError('天地图API未加载，请检查script标签')
  return
}

map = new T.Map('tianditu-map')
map.centerAndZoom(new T.LngLat(MAP_CONFIG.center[0], MAP_CONFIG.center[1]), MAP_CONFIG.zoom)
map.enableScrollWheelZoom()
map.setMinZoom(MAP_CONFIG.minZoom)
map.setMaxZoom(MAP_CONFIG.maxZoom)

// 深色主题通过 styleJson 覆盖（background/water/land 等逐层配色）
// zoomend / moveend 事件 emit('mapChange')，驱动天气按地图位置更新
```

- 人员标注由 `personnelMarkers` 渲染，点击 emit `personnelClick` → `PersonnelDialog` 展示详情
- 天地图 API 必须由 `index.html` 的 script 标签加载，组件内通过全局 `T` 访问

### 3. 天气与逆地理编码

```javascript
// src/utils/weather.js：天地图逆地理编码（回调式 API，带 5 秒超时兜底）
geocoder.getLocation(new T.LngLat(lng, lat), (result) => {
  // result.getAddressComponent() 取 city（缺省回退 province）
})

// src/composables/useWeather.js：缓存键 + 缓存读取
const cacheKey = `weather_${lng.toFixed(2)}_${lat.toFixed(2)}`
const cached = getCache(cacheKey)
```

### 4. 工具系统：日志与缓存

```javascript
// 四级日志 + 性能计时（src/utils/logger.js）
import { logInfo, logError, PerformanceTimer } from '@/utils/logger'
const timer = new PerformanceTimer('初始化人员数据')
// ... 执行操作
timer.end()   // 输出耗时：初始化人员数据 took 123ms

// 内存缓存（src/utils/cache.js，支持过期时间与容量上限）
import { setCache, getCache, getCacheStats } from '@/utils/cache'
setCache('weather_data', data, 600000)   // 10 分钟过期
```

### 5. 配置系统

```javascript
// src/config/dashboard.config.js：按环境返回配置
// 开发环境：debug 日志 + 性能日志；生产环境：精简日志 + 性能优化
import { getConfig } from '@/config/dashboard.config'
const config = getConfig()
config.personnel.updateInterval   // 1000ms（人员位置更新间隔）
config.weather.retryAttempts      // 3（天气失败重试次数）

// src/config/map.config.js
// MAP_CONFIG：key/center/zoom/minZoom/maxZoom/mapType/style
// WEATHER_CONFIG：key/baseUrl/lang
```

```javascript
// src/config/theme.config.js：大屏配色集中管理
export const THEME_CONFIG = {
  primaryColor: '#2C58A6',
  backgroundColor: '#001d58',
  cardBgColor: '#034c6a',
  textColor: '#ffffff',
  chartColors: ['#5490CB', '#63B2EE', '#76DA91', /* ... */],
}
```

### 6. 智能搜索

```javascript
// src/components/SearchBox/ + src/utils/search.js
import { loadData, fuzzySearch, highlightText } from '@/utils/search'

const results = fuzzySearch(data, 'zhangsan')   // 中文/全拼/首字母模糊匹配
const html = highlightText(text, keyword)       // 命中文本高亮
```

- 搜索数据经 `loadData()` 从 `public/data/excel/` 加载（支持 Excel/JSON）
- `pinyin-pro` 负责中文转拼音与首字母，实现「zhangsan」「zs」均可命中「张三」

### 7. 组件与数据流

```text
Dashboard.vue
  ├── Header          <- weatherData / DASHBOARD_CONFIG.menuItems
  ├── MapComponent    <- personnelMarkers；mapChange 事件触发天气按位置更新
  ├── ChartCard + StatCard  <- realtimeStats（mock 生成）
  └── PersonnelDialog <- 地图点击人员后传入 selectedPersonnel
```

## 典型工作流

### 端到端：从零启动并验证大屏

1. `git clone` 仓库并 `npm install`
2. 复制 `.env.example` 为 `.env`，填入 `VITE_TIANDITU_KEY`（天地图控制台申请浏览器端 key）
3. 在 `src/config/map.config.js` 配置 `WEATHER_CONFIG.key`（和风天气免费订阅 key）
4. `npm run dev` 打开 `http://localhost:3000`
5. 验证：中心地图出现深色底图与人员点位；点击人员弹出详情；拖动/缩放地图后天气按新位置更新（逆地理编码取城市名）
6. `npm run lint` 与 `npm run build`，再 `npm run preview` 验证生产构建

### 端到端：新增一个可复用的数据模块

1. 在 `src/composables/` 新建 `useXxx.js`：用 `ref` 暴露数据与 `load/refresh` 方法，`onUnmounted` 清理定时器
2. 数据获取封装到 `src/utils/`（参考 `weather.js` 的缓存读取与超时兜底写法）
3. 更新间隔与开关放入 `src/config/dashboard.config.js`，组件内用 `getConfig()` 读取
4. 在 `src/views/Dashboard.vue` 通过 `Promise.all` 并行初始化，UI 放入 `ChartCard` 插槽

## 最佳实践 / 常见陷阱

- **密钥管理**：`.env` 已在 `.gitignore` 中；不要把密钥硬编码进会提交的文件
- **定时器清理**：所有 composable 在 `onUnmounted` 清理 interval/timeout，避免内存泄漏与重复刷新
- **回调式 API 加超时**：天地图 `T.Geocoder` 回调可能不触发，`weather.js` 已内置 5 秒超时兜底，仿写时保留该模式
- **免费额度**：和风天气免费订阅有调用限额，依赖缓存（10 分钟）与控制刷新间隔，不要随意缩短 `weather.updateInterval`
- **配置驱动**：更新间隔、重试次数、缓存开关统一走 `dashboard.config.js`，不要散落魔法数字
- **图表组件**：自研 ECharts 等图表组件时，`onUnmounted` 移除 window resize 监听并 `dispose()` 实例
- **文档滞后**：README/教程中的 Vite 5 与 echarts-vendor 分包配置与当前仓库（Vite 8 + Rolldown codeSplitting、无 echarts）不一致，以 `package.json` 与源码为准

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 地图不显示 | 检查 `.env` 中 `VITE_TIANDITU_KEY` 是否配置且 key 已激活；控制台确认天地图 script 是否加载报错 |
| 天气信息不显示 | 检查 `WEATHER_CONFIG.key` 与 `baseUrl`（免费订阅用 `https://devapi.qweather.com/v7`），确认免费额度未用尽 |
| npm install 失败或很慢 | `npm cache clean --force` 后重装；或切换镜像 `npm config set registry http://registry.npmmirror.com` |
| 人员位置不更新 | 检查 `dashboard.config.js` 中 `personnel.enableAutoUpdate` 与 `updateInterval`；查看控制台 `logInfo` 输出 |
| 页面卡顿 | 调大人员/实时数据更新间隔；关闭调试日志（`logging.enableConsoleLog`）；关注 FPS 性能警告 |
| 构建后部署白屏或样式错乱 | `vite.config.js` 已设 `base: './'`；子路径部署与 Nginx `try_files` 配置参考教程「项目启动」章节 |
| 需要 ECharts 图表 | 当前仓库未内置 echarts，需自行 `npm install echarts`，并把图表组件放进 `ChartCard` 的插槽 |
| 智能搜索查不到结果 | 确认 `public/data/excel/` 数据文件存在且能被 `loadData()` 读取；拼音/首字母匹配依赖 pinyin-pro 转换 |
| 关闭控制台日志 | 在 `dashboard.config.js` 设置 `logging.enableConsoleLog: false`，或交由环境配置自动切换 |

## AI 使用建议

1. **架构入口**：先读 `src/views/Dashboard.vue`（编排与 `Promise.all` 并行初始化）和三个 composable（`usePersonnel` / `useWeather` / `useRealtimeData`），组件集中在 `src/components/`。
2. **常见改造点**：地图中心 / 缩放 / 深色样式改 `src/config/map.config.js`；配色改 `src/config/theme.config.js`；更新间隔、重试次数、日志开关改 `src/config/dashboard.config.js`，不要散落魔法数字。
3. **密钥管理**：天地图 key 经 `.env`（`VITE_TIANDITU_KEY`）注入 `index.html` script 标签；和风天气 key 在 `map.config.js`；两者都不要提交仓库。
4. **工具复用**：日志 / 计时用 `src/utils/logger.js`，缓存用 `src/utils/cache.js`（过期 + 容量上限），拼音搜索用 `src/utils/search.js`；新增数据模块参考「新增一个可复用的数据模块」工作流。
5. **遵守既有约定**：composable 在 `onUnmounted` 清理定时器；回调式 API（如 `T.Geocoder`）保留超时兜底模式；免费额度下依赖缓存与控制刷新间隔。
6. **注意文档滞后**：README / 教程提到的 Vite 5 与 echarts 分包与当前仓库不符（实际 Vite 8 + Rolldown codeSplitting、未内置 echarts），以 `package.json` 与源码为准；要图表需自行安装 echarts 并放入 `ChartCard` 插槽。

## 相关技能

- **openlayers** — Web 端二维地图渲染与交互（替换或扩展天地图组件的参考）：[../../gis/openlayers/SKILL.md](../../gis/openlayers/SKILL.md)
- **cesiumjs** — 三维地球与三维大屏可视化方向：[../../gis/cesiumjs/SKILL.md](../../gis/cesiumjs/SKILL.md)
- **openlayers-vue3-demo** — 同批演示：Vue 3 + OpenLayers（vue3-openlayers）声明式地图与 GeoServer 图层树对接：[../openlayers-vue3-demo/SKILL.md](../openlayers-vue3-demo/SKILL.md)
- **ai-water-front** — 同批演示：Vue 3 智慧水务大屏，OpenLayers 与 Dify AI 助手结合：[../ai-water-front/SKILL.md](../ai-water-front/SKILL.md)

## 参考资源

- [vue3-map-dashboard GitHub 仓库](https://github.com/znlgis/vue3-map-dashboard) — 源码与 README
- [vue3-map-dashboard 教程](https://znlgis.github.io/demos/vue3-map-dashboard/) — 项目概述、环境搭建、核心功能与开发指南
- [天地图开放平台（控制台）](https://console.tianditu.gov.cn/) — 申请浏览器端 API Key
- [天地图 API 服务文档](https://lbs.tianditu.gov.cn/server/MapService.html) — JS API 与地理编码
- [和风天气开发文档](https://dev.qweather.com/docs/api/) — 实时天气与城市查询 API
- [Element Plus 文档](https://element-plus.org/zh-CN/) — 组件库用法

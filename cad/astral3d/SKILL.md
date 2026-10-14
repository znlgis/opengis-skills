---
name: astral3d
description: "Use when building Web 3D scenes, digital twins or BIM lightweight viewing with Astral3D — the Vue 3 + Three.js editor monorepo and its @astral3d/engine SDK. Covers source-build workflow (pnpm sdk:build then editor:dev), Viewer/App/Loader/Package APIs, scene pack/unpack ZIP delivery, plugin and script runtime extension, DXF and IFC preview."
tags:
  - web
  - 3d
  - threejs
  - vue
  - typescript
  - visualization
  - digital-twin
  - bim
---

> **项目地址：** <https://github.com/mlt131220/Astral3D>（Gitee 镜像 <https://gitee.com/mlt131220/Astral3D>）
>
> **在线编辑器：** <https://editor.astraljs.com/> ｜ **文档中心：** <http://editor-doc.astraljs.com/>
>
> **许可证：** Apache-2.0（README 声明个人学习与二次开发免费、商业使用需授权，以仓库为准）
>
> **最新版本：** `1.0.0`（GitHub tag / Release 2025-10-04，与 npm 包 `astral3d` 版本一致；master 仍在持续开发，截至 2026-10）
>
> **中文教程（12 章）：** <https://znlgis.github.io/cad/Astral3D/>

## 概述

Astral3D 是杭州星孪数字科技团队开源的「Web 3D 编辑器 + 三维引擎」一体化项目，仓库是 pnpm monorepo：`packages/editor` 是 Vue 3 + Naive UI 的可视化编辑器，`packages/sdk`（工作区包名 `@astral3d/engine`）抽出渲染、加载、特效、脚本等运行时能力，`packages/docs` 是文档站。定位面向数字孪生与工程可视化：30+ 模型格式、BIM（RVT/IFC）轻量化展示、CAD 图纸（DWG/DXF）解析预览、场景分包存储与按需加载、关键帧动画编辑器、插件系统、脚本运行时、粒子与天气系统。

| 能力 | 实现依赖（取自仓库 catalog 与 package.json） |
|------|------|
| 3D 渲染 | three 0.176.0（WebGL），three-gpu-pathtracer、three-mesh-bvh、three-viewport-gizmo |
| 前端框架 | vue ^3.5.22 + naive-ui ^2.43.1 + unocss + pinia ^2.1.4 + vue-i18n |
| 构建 | vite ^6.2.5、typescript ^5.4.5、@vitejs/plugin-vue ^6 |
| 相机控制 | camera-controls ^2.9.0（配合 three 的 TransformControls） |
| 事件 | signals ^1.0.0（Viewer 的 `registerSignal` 模块） |
| BIM | web-ifc-three ^0.0.126（IFC 解析，含 `IFCWorker.js`） |
| CAD | 内置 `DxfParser` / `DxfViewer` |
| 瓦片/倾斜摄影 | 3d-tiles-renderer（`TilesManage` 模块） |
| 粒子 | three-nebula（以 `Particle` 命名空间导出） |
| 序列化 | localforage、jszip、pako（场景分包与离线包） |

> 开源版 / 商业版 / 企业版功能差异较大；本 SKILL 只覆盖开源仓库源码与已发布类型声明能够核对的用法。

---

## 环境准备

### 前置要求

- Node.js **≥ 23.0.0**（根 `package.json` 的 `engines` 声明）
- pnpm（`packageManager: pnpm@10.8.1`）
- 支持 WebGL2 的现代浏览器；编辑器是纯前端工程，本地跑通不依赖后端

### 源码克隆与运行（推荐路径）

```bash
git clone https://github.com/mlt131220/Astral3D.git
cd Astral3D
pnpm install

# 1) 先构建 SDK：编辑器依赖工作区包 @astral3d/engine 的产物
pnpm run sdk:build

# 2) 启动编辑器开发服务器
pnpm run editor:dev
```

### 其它构建目标

```bash
pnpm run editor:build      # = sdk:build + editor build，产出静态站点
pnpm run editor:preview    # 预览生产构建
pnpm run editor:tsc        # 编辑器类型检查
pnpm run docs:dev          # 本地文档站
pnpm run examples:dev      # 示例工程
```

**验证**：`editor:dev` 启动后进入编辑器界面，拖入一个 glTF 模型能渲染出阴影即环境就绪；`pnpm run editor:build` 成功产出 `packages/editor/dist` 说明 SDK 与编辑器链路完整。

### npm 包现状（重要）

npm 上的 `astral3d@1.0.0` 是 SDK 构建产物（`dist/astral3d.es.js` + `dist/types/index.d.ts`），但发布包的 `dependencies` 保留了 `"three": "catalog:"` 这类 pnpm workspace 协议字段，用 npm/yarn 直接安装会失败：

```bash
npm install astral3d
# npm error code EUNSUPPORTEDPROTOCOL
# npm error Unsupported URL Type "catalog:": catalog:
```

结论：集成以源码 monorepo 为准（把 `packages/sdk` 纳入工作区，或 `pnpm run sdk:build` 后引用产物），不要假设可以 `npm i astral3d` 直接接入。

---

## 核心 API

SDK 类型声明（`packages/sdk` 产物 `dist/types/lib/index.d.ts`）导出的主要成员：

| 导出 | 说明 |
|------|------|
| `App` | 全局场景管理静态类：`scene` / `sceneHelpers` / `camera` / `viewportCamera` / `viewportShading` / `selected` / `locked` / `geometries` / `materials` / `textures` / `scripts` / `helpers` / `metadata`，并挂 `Config` `Storage` `Project` `Selector` `History` `Resource` `CSM` 模块 |
| `Viewer` | 渲染视口，继承 `THREE.EventDispatcher`，持有 `renderer` `camera` `scene` `sceneHelpers` `raycaster` `grid` `box` `selectionBox` `sceneBox3` `css2DRenderer` `css3DRenderer` `timer` `pathtracer` 与 `modules` |
| `Preview` | 不带编辑器 UI 的轻量预览容器 |
| `Loader` | 模型 / 纹理加载单例（GLTF、DRACO、KTX2、RGBE、TGA、EXR、MTL、ObjectLoader、IFC） |
| `Package` | 场景打包与解包（ZIP 分片上传 / 按 URL 还原场景） |
| `DxfViewer` / `DxfParser` | DXF 图纸解析与预览 |
| `Plugin`（类型） | 插件契约：`name` / `version` / `icon` / `install()` / `uninstall()` / `run()` |
| `Script` `Hooks` `Utils` `Timeline` `Particle` `Commands` | 脚本运行时、组合式钩子、工具、时间轴、粒子、命令 |
| `objects` `geometries` `tools` `points` `BasicObject3D` `Particles` | 场景对象、几何、工具、点云与内建资产 |

### Viewer 与能力模块

```ts
import { Viewer } from '@astral3d/engine';

const viewer = new Viewer({ container });   // options 类型为 IViewerSetting

// viewer.modules（类型 ViewerModules）是能力入口：
//   plugin: PluginManager            viewHelper: Helper
//   cameraManage: CameraManage       controls: CameraControls
//   transformControls?: TransformControls
//   effect: Effect                   weather: Weather
//   registerSignal: Signals          shaderMaterialManager: ShaderMaterialManager
//   particleSystem: ParticleSystem   dragControl: Drag   tilesManage: TilesManage
viewer.initModules();
viewer.initEvent();
viewer.loadEnv(true);         // 载入默认环境贴图与背景
viewer.computedSceneBox3();   // 计算整体包围盒，供聚焦使用
viewer.updateAspectRatio();   // 容器尺寸变化时调用
```

`enableEdit` 与 `enableScript` 是可读写属性，分别控制编辑态与脚本运行；渲染引擎可通过 `createEngine()` / `engineCreated(renderer)` 替换。

### 事件（ViewerEventMap）

`Viewer` 是 `THREE.EventDispatcher` 子类，用 `addEventListener` 按事件名订阅：

```ts
viewer.addEventListener('loaded', () => console.log('scene ready'));

viewer.addEventListener('onPick', ({ intersect, object }) => {
    console.log('clicked', object.name, intersect.point);
});

viewer.addEventListener('afterAnimation', ({ delta, toBeRender }) => {
    if (Math.random() < 0.5) toBeRender(false);   // 无需重绘时跳帧降载
});
```

可用事件名：`loaded`、`beforeAnimation`、`afterAnimation`、`beforeRender`、`afterRender`、`beforeDestroy`、`afterDestroy`、`onPick`、`onDoubleClick`、`onKeyDown`、`onKeyUp`、`onPointerDown`、`onPointerUp`、`onPointerMove`、`onTouchStart`、`onTouchEnd`、`onSceneBackgroundChange`、`onSceneEnvironmentChange`。

### 模型加载

```ts
import { Loader } from '@astral3d/engine';

// Loader 是单例；glTF 走带 DRACO / KTX2 的 loader
const gltfLoader = await Loader.createGLTFLoader();
Loader.dracoLoader.setDecoderPath('/draco/');

await Loader.loadFile(file, undefined, null, true);   // 第四个参数 addToScene
await Loader.loadFiles(files, filesMap);              // 批量加载（含 MTL 关联材质）
await Loader.handleJSON(sceneJson, true);             // 编辑器导出的 JSON 场景
await Loader.handleZIP(zipContents, true);            // 场景包
Loader.disposeGLTFLoaderEffects(gltfLoader);          // 用完释放
```

发布产物中可见的格式 loader：GLTF/GLB（+ DRACO、KTX2）、OBJ（+ MTL）、FBX、3MF、AMF、IFC（web-ifc + `IFCWorker`）、KMZ、PCD、PLY、STL、VTK、SVGLoader，另有 GLTF/OBJ/PLY/STL 导出器与 DXF 解析器。**没有 STEP loader**：STEP 需先在桌面端（FreeCAD/OCCT）转成 glTF 或 IFC 再入库。

### 场景分包（Package）

大场景以 ZIP 分片交付，首包保存场景基本信息、图纸信息与基础配置：

```ts
import { Package } from '@astral3d/engine';

const pack = new Package(viewer);

// 打包：业务侧提供 zip 上传函数
const result = await pack.pack({
    name: 'factory',
    layer: 1,
    zipUploadFun: async (zip) => (await fetch('/api/upload', { method: 'POST', body: zip })).json(),
    onProgress: (p) => console.log(`${p}%`),
    onComplete: ({ totalSize, totalZipNumber }) => console.log(totalSize, totalZipNumber)
});

// 解包：从首包开始按 URL 还原（回调式，不返回 Promise）
pack.unpack({
    url: '/scenes/factory.zip',
    onSceneLoad: (sceneJson, configJson) => { /* 交由 App / Loader 组装 */ },
    onProgress: (p) => {},
    onComplete: () => {}
});

pack.dispose();   // 不再需要时释放
```

### 插件系统

插件契约是 `Plugin` 接口（`version` 为 number），由 `viewer.modules.plugin`（`PluginManager`）管理：

```ts
import type { Plugin } from '@astral3d/engine';

const myPlugin: Plugin = {
    name: 'MyPlugin',
    version: 1,
    icon: 'link',
    install(config) { /* 注册信号、工具栏、自定义材质 */ },
    uninstall() { /* 还原副作用 */ },
    run() { /* 启用交互 */ }
};

viewer.modules.plugin.use(myPlugin, { /* config */ });
await viewer.modules.plugin.loadAsync('/plugins/extra.js', true);   // 远程加载并自动注册
const p = viewer.modules.plugin.getPlugin<Plugin>('MyPlugin');
```

### 脚本运行时

场景对象可挂脚本，支持按 UUID 热更新：

```ts
viewer.installScripts();                        // 组装全部脚本
viewer.installScripts(object.uuid, 'rotate');   // 仅组装指定对象、指定名称的脚本
viewer.uninstallScriptsByUuid(object.uuid);     // 卸载该对象脚本（热更新前调用）
viewer.unInstallScripts();                      // 全部卸载
```

---

## 典型工作流

### 工作流一：编辑器搭场景，自有页面轻量展示

1. 打开 <https://editor.astraljs.com/>，或本地 `pnpm run sdk:build && pnpm run editor:dev`
2. 新建场景 → 导入模型（glTF 优先；BIM 用 IFC，图纸用 DXF）→ 布光、材质、动画与脚本
3. 导出场景包（ZIP 分片，含场景 JSON 与资源），上传到静态资源服务或业务后端
4. 业务页面用 SDK 创建 `Viewer`，通过 `Package.unpack({ url })` 还原场景（或用 `Loader.handleZIP`）
5. `viewer.addEventListener('onPick', ...)` 做设备选中，选中对象在 `App.selected`
6. 容器 resize 调 `viewer.updateAspectRatio()`；离开页面前 `unInstallScripts()` 并清理监听

### 工作流二：源码二次开发（新增插件与自定义材质）

1. 克隆仓库 → `pnpm install` → `pnpm run sdk:dev` / `editor:dev` 建立热更闭环
2. 在 `packages/sdk` 内扩展能力；SDK 改动后重新 `pnpm run sdk:build`
3. 以 `Plugin` 暴露功能：`install()` 注册信号（`viewer.modules.registerSignal`）与 UI，`run()` 绑定交互
4. 自定义着色器走 `viewer.modules.shaderMaterialManager`
5. `pnpm run editor:tsc` 与 `pnpm run editor:build` 全绿后再提交

---

## 最佳实践

1. **先 sdk:build 再 editor:dev**：编辑器依赖 `@astral3d/engine` 产物，跳过会在编辑器包里报模块解析失败
2. **不要 npm 装 `astral3d`**：发布包保留 `catalog:` 协议依赖，集成走源码工作区
3. **glTF + DRACO + KTX2** 是体积与首屏主力组合；`Loader.disposeGLTFLoaderEffects()` 用完释放
4. **大场景靠分包**：`Package` 的 ZIP 分片 + `loadOfflineScene()`，不要让单个场景 JSON 膨胀
5. **事件名以 `ViewerEventMap` 为准**：`viewer.on('pick')` 之类的写法不存在
6. **每帧逻辑放 `beforeRender` / `afterAnimation`**：后者提供 `toBeRender(need)` 可主动跳帧
7. **移动端降载**：关闭实时阴影与 pathtracer、降低渲染分辨率，天气与粒子按需启用
8. **脚本热更新成对调用**：`uninstallScriptsByUuid(uuid)` 后 `installScripts(uuid)`，避免重复装配

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `npm i astral3d` 报 `EUNSUPPORTEDPROTOCOL: catalog:` | 发布包保留 pnpm `catalog:` 依赖；改用源码 monorepo 或引用 `sdk:build` 产物 |
| 编辑器启动报找不到 `@astral3d/engine` | 未先构建 SDK；执行 `pnpm run sdk:build` |
| 安装依赖提示 Node 版本不满足 | 根 `package.json` 要求 Node ≥ 23.0.0，用 nvm 切换后重装 |
| 用 npm/yarn 装依赖失败 | 仓库是 pnpm workspace（`packageManager: pnpm@10.8.1`），必须用 pnpm |
| STEP 文件打不开 | SDK 无 STEP loader，先用 FreeCAD/OCCT 转 glTF 或 IFC |
| IFC/RVT 打开失败或内存暴涨 | 上游先减面与拆分，浏览器侧按楼层/子树加载 |
| 大场景首屏很慢 | 用 `Package` 分包 + DRACO/KTX2，检查 `onProgress` 卡在哪一类资源 |
| 页面切走后再进来画面异常 | 卸载时 `unInstallScripts()` 并移除事件监听，避免残留 WebGL 上下文 |

---

## AI 使用建议

- **区分两条路径**：「用编辑器产出场景」与「用 SDK 嵌入自有工程」，前者不需要写渲染代码。
- **优先场景包而非手工搭树**：以编辑器导出的 ZIP/JSON 为基础，再用 API 注入实时数据与交互。
- **API 以类型声明为准**：`Viewer` / `App` / `Loader` / `Package` 成员可从 `dist/types/**.d.ts` 核对；不要臆造 `viewer.scene.findById()`、`viewer.camera.flyTo()`、`MqttBridge` 这类不存在的方法。
- **数据接入属业务侧**：MQTT/WebSocket 由上层实现，SDK 只负责把数据写回对象属性与材质；断线重连与节流自行处理。

---

## 相关技能

- **chili3d** — 浏览器内参数化 CAD（OCCT.js + WASM）：[../chili3d/SKILL.md](../chili3d/SKILL.md)
- **occt** — 底层几何内核（STEP/IGES/BREP），STEP 转换的上游：[../occt/SKILL.md](../occt/SKILL.md)
- **lightcad** — C#/.NET 桌面 CAD 与 BIM 平台（工程侧对照）：[../lightcad/SKILL.md](../lightcad/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/mlt131220/Astral3D> ｜ Gitee：<https://gitee.com/mlt131220/Astral3D>
- 在线编辑器：<https://editor.astraljs.com/> ｜ 文档中心：<http://editor-doc.astraljs.com/>
- 后端实现参考：<https://github.com/yx8663/astral-service>
- 中文教程（12 章）：<https://znlgis.github.io/cad/Astral3D/>
- Three.js：<https://threejs.org/docs/> ｜ camera-controls：<https://github.com/yotsen99/camera-controls>

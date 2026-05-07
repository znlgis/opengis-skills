---
name: astral3d
description: Astral3D 是开源的 3D 工业可视化与编辑框架，提供基于 Web 的轻量三维场景搭建、模型导入（glTF/OBJ/FBX/STEP）、设备孪生、动画与交互编辑能力，常用于工业 IoT、数字孪生、智慧园区、CAD/BIM 轻量化展示。
---

> **项目地址：** <https://github.com/AstralEngine/astral3d>（如仓库迁移请以 znlgis.github.io 链接为准）
>
> **演示：** <https://astral3d.com/>
>
> **许可证：** Apache-2.0 / MIT（视具体仓库）

## 概述

Astral3D 主要特性：

- **基于 Three.js / Babylon.js** 的高层封装
- **场景编辑器**：可视化拖拽、属性面板、节点树
- **资产管理**：模型库、材质库、HDR 环境
- **动画与状态机**：物体动画、相机路径、时间轴
- **交互**：射线拾取、点击、悬浮、UI 弹窗
- **数据接入**：MQTT、WebSocket 实时推送
- **导出**：JSON 场景、glTF、嵌入 SDK

> 不同发行版（开源版 / 商业版 / 企业版）功能差异较大，本 SKILL 聚焦开源版与通用 SDK 用法。

---

## 安装

```bash
# Web SDK（npm）
npm install astral3d

# 编辑器（如有桌面版）：从官网下载
```

CDN：

```html
<script src="https://cdn.jsdelivr.net/npm/astral3d/dist/astral3d.umd.js"></script>
```

---

## 入门：嵌入页面

```html
<div id="scene" style="width:100%;height:100vh"></div>
<script type="module">
  import { Viewer } from 'astral3d';

  const viewer = new Viewer({
    container: document.getElementById('scene'),
    scene: '/scenes/factory.json',     // 由编辑器导出
    background: 'env/sky.hdr'
  });

  await viewer.load();

  // 监听点击事件
  viewer.on('pick', (obj) => console.log('clicked', obj.name));
</script>
```

---

## 场景模型

| 概念 | 说明 |
|------|------|
| `Scene` | 场景容器（场景树、灯光、相机） |
| `Asset` | 资源（模型、纹理、HDR） |
| `Entity` | 场景节点 |
| `Component` | 实体组件（Transform、Mesh、Light、Animator、Script） |
| `Plugin` | 编辑器/运行时插件 |

---

## 加载模型

```js
import { ModelLoader } from 'astral3d';

const car = await ModelLoader.load('/models/car.glb');
viewer.scene.add(car);

// 设置位置 / 旋转
car.position.set(10, 0, 0);
car.rotation.y = Math.PI / 4;
```

支持格式：glTF/GLB（首选）、OBJ、FBX、STL、IFC、STEP（通过 OCCT.js）。

---

## 场景编辑器

Astral3D 通常配套桌面/Web 编辑器：

1. 新建场景 → 选模板（空 / 工业园区 / 数据中心）
2. 拖入模型库资产
3. 编辑材质、灯光、HDR
4. 设置交互（点击事件、动画轨道）
5. 导出 `.json` 场景文件 → 由 Viewer 加载

---

## 数据驱动（IoT 实时）

```js
import { MqttBridge } from 'astral3d';

const bridge = new MqttBridge('wss://broker:8083/mqtt');
bridge.subscribe('factory/device/+/temp', (topic, payload) => {
    const id = topic.split('/')[2];
    const dev = viewer.scene.findById(id);
    dev.userData.temp = +payload;
    dev.material.color.setHSL(0.6 - payload/100, 1, 0.5);
});
```

或 WebSocket：

```js
const ws = new WebSocket('wss://server/iot');
ws.onmessage = ({ data }) => {
    const { id, status } = JSON.parse(data);
    viewer.scene.findById(id).visible = status === 'on';
};
```

---

## 交互与拾取

```js
viewer.on('hover', (e) => {
    const obj = e.intersect?.object;
    if (obj) viewer.outline(obj);
});

viewer.on('pick', (e) => {
    const obj = e.intersect?.object;
    viewer.popup({
        target: obj,
        html: `<div class="card">${obj.name} 状态：${obj.userData.status}</div>`
    });
});
```

---

## 相机控制与漫游

```js
viewer.camera.flyTo({
    position: [50, 30, 80],
    target:   [0, 0, 0],
    duration: 2000
});

viewer.camera.firstPerson(true);     // 第一人称漫游
viewer.camera.followPath('path1');   // 路径漫游
```

---

## 动画

```js
const animator = viewer.scene.findById('door').getComponent('Animator');
animator.play('open');         // 编辑器内定义的动画片段

// 时间轴 API
viewer.timeline
   .add('door.position.x', { from: 0, to: 5, duration: 1000 })
   .add('door.rotation.y', { to: Math.PI/2, duration: 1500 })
   .play();
```

---

## 性能优化

1. **glTF Draco 压缩 + KTX2 纹理** 减小加载体积
2. **静态合批**：场景导出时启用 `mergeStatic`
3. **LOD**：编辑器为模型生成 3 级 LOD
4. **物理光照贴图**：烘焙到资产中
5. **Frustum culling + occlusion culling** 默认开启
6. **Worker 解码**：DRACO/KTX2/FBX 使用独立 Worker
7. **PBR 关闭高反射时改 `unlit` 材质**

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 模型加载失败 | 检查 CORS；统一用 glTF 2.0 |
| 中文按钮乱码 | 字体子集中包含 CJK |
| 实时推送延迟 | MQTT QoS 0；服务器 → 浏览器 WebSocket 直连 |
| 移动端发热 | 关闭实时阴影、降低分辨率 `viewer.setPixelRatio(1)` |
| 相机穿透 | 启用碰撞或限制 minDistance |

---

## 参考资源

- 仓库：<https://github.com/AstralEngine/astral3d>
- 演示：<https://astral3d.com/>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/astral3d/>

> 如官方文档/仓库地址有调整，请以 znlgis.github.io 中的最新链接为准。

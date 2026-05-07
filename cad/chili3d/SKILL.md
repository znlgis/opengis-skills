---
name: chili3d
description: Chili3D 是基于 Web 的开源 CAD 软件，使用 TypeScript + WebAssembly（封装 OCCT）实现，可在浏览器中完成参数化 3D 建模、装配、布尔运算与 STEP/IGES/STL 导入导出，目标是打造无需安装的工业级开源 Web CAD。
---

> **项目地址：** <https://github.com/xiangechen/chili3d>
>
> **在线体验：** <https://chili3d.com/>
>
> **许可证：** AGPL-3.0

## 概述

Chili3D 主要特性：

- **纯前端 CAD**：基于 Three.js + OCCT.js（WebAssembly）
- **参数化建模**：草图、特征树、约束求解
- **基础几何**：立方体、圆柱、棱柱、扫掠、放样、布尔
- **修饰**：圆角、倒角、抽壳
- **数据交换**：STEP / IGES / BREP / STL / OBJ / glTF
- **保存格式**：自有 JSON 项目格式
- **国际化**：内置中/英文

---

## 在线使用

直接打开 <https://chili3d.com/>：

1. 选择「新建」或导入 STEP/IGES
2. 左侧工具栏：Sketch / Box / Cylinder / Sphere / ...
3. 右侧属性面板：编辑参数、变换
4. 顶部菜单：Boolean / Fillet / Chamfer / Shell
5. 文件 → 导出（STEP/STL/glTF）

---

## 本地部署 / 二次开发

```bash
git clone https://github.com/xiangechen/chili3d.git
cd chili3d
pnpm install
pnpm dev          # 本地开发服务器（http://localhost:5173）
pnpm build        # 静态构建
```

构建产物可直接部署到任何静态托管（Nginx / Cloudflare Pages / GitHub Pages）。

---

## 项目结构

```
packages/
├── chili-core/         # 模型、命令、应用框架
├── chili-geo/          # 几何抽象、Visual
├── chili-three/        # Three.js 渲染
├── chili-occ/          # OCCT.js WebAssembly 桥接
├── chili-controls/     # 草图控件、操控器
├── chili-builder/      # 拉伸/扫掠/放样等特征构建器
├── chili-ui/           # UI 组件
└── chili-web/          # 主 Web 应用
```

---

## 嵌入到自有应用

```html
<div id="cad" style="width:100%;height:100vh"></div>
<script type="module">
  import { Application } from '@chili3d/web';
  const app = new Application(document.getElementById('cad'));
  await app.start();
</script>
```

或作为 iframe：

```html
<iframe src="https://chili3d.com/" allow="cross-origin-isolated"
        style="width:100%;height:100vh;border:0"></iframe>
```

> WebAssembly OCC 需要启用 `SharedArrayBuffer`，要求站点设置 `Cross-Origin-Opener-Policy: same-origin` 与 `Cross-Origin-Embedder-Policy: require-corp`。

---

## 使用 OCCT.js 直接构造（脚本扩展）

```ts
import { occt } from '@chili3d/occ';

const oc = await occt();
const box = new oc.BRepPrimAPI_MakeBox_2(100, 60, 30).Shape();
// 进一步通过 chili-core 的 Visual 对象包装显示
```

---

## 命令系统

Chili3D 命令通过 `Command` 注册：

```ts
import { Command } from '@chili3d/core';

@Command({ id: 'my.line', display: '我的直线' })
export class MyLineCommand {
    async execute(app) {
        const p1 = await app.input.getPoint('选择起点');
        const p2 = await app.input.getPoint('选择终点');
        app.activeView.document.add(LineFactory.byPoints(p1, p2));
    }
}
```

---

## 文件 I/O

- **保存项目**：菜单 File → Save → `.chili` JSON
- **导出**：File → Export → STEP/IGES/BREP/STL/OBJ/glTF
- **导入**：File → Import → 同上 + .chili

---

## 与 Three.js 集成

Chili3D 渲染层在 `chili-three`，可定制材质、光照、PBR：

```ts
import { ThreeView } from '@chili3d/three';
const view = ThreeView.fromCanvas(canvas);
view.scene.add(new THREE.AmbientLight(0xffffff, 0.5));
```

---

## 性能要点

1. WebAssembly OCCT 单线程（除非启用 pthreads + COOP/COEP）
2. 大模型加载前先压缩 STEP，导入后转 BREP 缓存
3. 渲染端使用 LOD：用 BVH 或 Decimator 减面
4. 频繁布尔操作建议在 Worker 线程中执行
5. 浏览器内存限制：模型大小通常不超过 100MB STEP

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 加载 OCCT.wasm 失败 | 站点未启用 COOP/COEP；改用 `cross-origin-isolated` |
| 无法导入 DWG | 暂不支持 DWG，先转 DXF/STEP |
| 中文菜单 | Settings → Language 切换为中文 |
| 性能差 | 确认 Vite 构建为 production；启用浏览器 SIMD |
| 模型透视错乱 | 检查相机近/远裁剪面与单位 |

---

## 适用场景

✅ 教育、Web 演示、轻量 3D 建模、定制配置器、嵌入业务系统
❌ 大型工业装配、复杂曲面（仍推荐 FreeCAD/OCCT 桌面）

---

## 参考资源

- 仓库：<https://github.com/xiangechen/chili3d>
- 在线：<https://chili3d.com/>
- OCCT.js：<https://github.com/donalffons/opencascade.js>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/chili3d/>

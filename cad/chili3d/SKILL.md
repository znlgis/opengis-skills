---
name: chili3d
description: "Use when building browser-based 3D CAD applications with WebAssembly  -- ?STEP/B-Rep visualization, measurement tools, sectioning. Chili3D: pure Web 3D CAD built on OCCT.js compiled to WASM with TypeScript API."
tags: [web, 3d, typescript, wasm, occ, parametric, step, stl]
---

> **项目地址 -- ?* <https://github.com/xiangechen/chili3d>
>
> **在线体验 -- ?* <https://chili3d.com/>
>
> **许可证：** AGPL-3.0

## 概述

Chili3D 主要特性：

- **纯前 -- ?CAD**：基 -- ?Three.js + OCCT.js（WebAssembly -- ?
- **参数化建 -- ?*：草图、特征树、约束求 -- ?
- **基础几何**：立方体、圆柱、棱柱、扫掠、放样、布 -- ?
- **修饰**：圆角、倒角、抽 -- ?
- **数据交换**：STEP / IGES / BREP / STL / OBJ / glTF
- **保存格式**：自 -- ?JSON 项目格式
- **国际 -- ?*：内置中/英文

---

## 在线使用

直接打开 <https://chili3d.com/> -- ?

1. 选择「新建」或导入 STEP/IGES
2. 左侧工具栏：Sketch / Box / Cylinder / Sphere / ...
3. 右侧属性面板：编辑参数、变 -- ?
4. 顶部菜单：Boolean / Fillet / Chamfer / Shell
5. 文件  -- ?导出（STEP/STL/glTF -- ?

---

## 本地部署 / 二次开 -- ?

```bash
git clone https://github.com/xiangechen/chili3d.git
cd chili3d
pnpm install
pnpm dev          # 本地开发服务器（http://localhost:5173 -- ?
pnpm build        # 静态构 -- ?
```

构建产物可直接部署到任何静态托管（Nginx / Cloudflare Pages / GitHub Pages） -- ?

---

## 项目结构

```
packages/
├── chili-core/         # 模型、命令、应用框 -- ?
├── chili-geo/          # 几何抽象、Visual
├── chili-three/        # Three.js 渲染
├── chili-occ/          # OCCT.js WebAssembly 桥接
├── chili-controls/     # 草图控件、操控器
├── chili-builder/      # 拉伸/扫掠/放样等特征构建器
├── chili-ui/           # UI 组件
└── chili-web/          #  -- ?Web 应用
```

---

## 嵌入到自有应 -- ?

```html
<div id="cad" style="width:100%;height:100vh"></div>
<script type="module">
  import { Application } from '@chili3d/web';
  const app = new Application(document.getElementById('cad'));
  await app.start();
</script>
```

或作 -- ?iframe -- ?

```html
<iframe src="https://chili3d.com/" allow="cross-origin-isolated"
        style="width:100%;height:100vh;border:0"></iframe>
```

> WebAssembly OCC 需要启 -- ?`SharedArrayBuffer`，要求站点设 -- ?`Cross-Origin-Opener-Policy: same-origin`  -- ?`Cross-Origin-Embedder-Policy: require-corp` -- ?

---

## 使用 OCCT.js 直接构造（脚本扩展 -- ?

```ts
import { occt } from '@chili3d/occ';

const oc = await occt();
const box = new oc.BRepPrimAPI_MakeBox_2(100, 60, 30).Shape();
// 进一步通过 chili-core  -- ?Visual 对象包装显示
```

---

## 命令系统

Chili3D 命令通过 `Command` 注册 -- ?

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

- **保存项目**：菜 -- ?File  -- ?Save  -- ?`.chili` JSON
- **导出**：File  -- ?Export  -- ?STEP/IGES/BREP/STL/OBJ/glTF
- **导入**：File  -- ?Import  -- ?同上 + .chili

---

##  -- ?Three.js 集成

Chili3D 渲染层在 `chili-three`，可定制材质、光照、PBR -- ?

```ts
import { ThreeView } from '@chili3d/three';
const view = ThreeView.fromCanvas(canvas);
view.scene.add(new THREE.AmbientLight(0xffffff, 0.5));
```

---

## 典型工作 -- ?

### 工作流一：在线参数化建模与导 -- ?

1. 打开 <https://chili3d.com/> 或本地部署实 -- ?
2. 新建项目，使 -- ?Sketch 工具绘制 2D 轮廓
3. 通过 Extrude/Revolve 将草图转 -- ?3D 实体
4. 添加圆角、倒角等修饰特 -- ?
5. 使用布尔运算（Union/Cut/Intersect）组合多个实 -- ?
6. 导出 -- ?STEP/STL 用于下游加工 -- ?3D 打印

### 工作流二：嵌入业务系统作 -- ?Web CAD 组件

1. 在项目中安装 `@chili3d/web`  -- ?
2. 在页面中创建容器 `<div>`，实例化 `Application`
3. 通过 Command 系统注册自定义绘图命 -- ?
4. 监听文档变更事件，同步模型数据到后端
5. 利用 OCCT.js 直接构造几何进行批量参数化生成
6. 构建为静态资源部署到生产环境

---

## 性能要点

1. WebAssembly OCCT 单线程（除非启用 pthreads + COOP/COEP -- ?
2. 大模型加载前先压 -- ?STEP，导入后 -- ?BREP 缓存
3. 渲染端使 -- ?LOD：用 BVH  -- ?Decimator 减面
4. 频繁布尔操作建议 -- ?Worker 线程中执 -- ?
5. 浏览器内存限制：模型大小通常不超 -- ?100MB STEP

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 加载 OCCT.wasm 失败 | 站点未启 -- ?COOP/COEP；改 -- ?`cross-origin-isolated` |
| 无法导入 DWG | 暂不支持 DWG，先 -- ?DXF/STEP |
| 中文菜单 | Settings  -- ?Language 切换为中 -- ?|
| 性能 -- ?| 确认 Vite 构建 -- ?production；启用浏览器 SIMD |
| 模型透视错乱 | 检查相机近/远裁剪面与单 -- ?|

---

## 适用场景

 -- ?教育、Web 演示、轻 -- ?3D 建模、定制配置器、嵌入业务系 -- ?
 -- ?大型工业装配、复杂曲面（仍推 -- ?FreeCAD/OCCT 桌面 -- ?

---

## AI 使用建议

- **推荐工作流模 -- ?*：AI 助手应区分两种使用场景——在线建模（引导用户通过 GUI 操作）与二次开发（通过 TypeScript SDK 嵌入）。对后者，优先使用 `@chili3d/occ` 直接调用 OCCT.js 进行几何构造，而非通过 UI 层间接操作 -- ?
- **关键注意事项**：① WebAssembly OCCT 需 -- ?COOP/COEP 头，部署时必须正确配置； -- ?`SharedArrayBuffer` 依赖 HTTPS  -- ?localhost；③ OCCT.js 加载较慢（首次约 5-15s），需显示加载进度；④ 浏览器内存有限，大模型应考虑服务端处理 -- ?
- **常用代码模式**：`occt()` 初始 -- ? -- ?`BRepPrimAPI_MakeBox` 等构造几 -- ? -- ?`chili-core`  -- ?Visual/Document 包装  -- ?渲染显示。自定义命令继承 `Command` 类，通过 `app.input.getPoint()` 获取用户交互 -- ?

---

## 相关技 -- ?

- **astral3d**  -- ?Web 3D 可视化与数字孪生框架：[../astral3d/SKILL.md](../astral3d/SKILL.md)
- **lightcad**  -- ?轻量 Web 2D CAD 框架：[../lightcad/SKILL.md](../lightcad/SKILL.md)
- **occt**  -- ?底层 OCCT 几何内核（C++/PythonOCC）：[../occt/SKILL.md](../occt/SKILL.md)
- **freecad**  -- ?桌面参数 -- ?CAD（同基于 OCCT）：[../freecad/SKILL.md](../freecad/SKILL.md)

---

## 参考资 -- ?

- 仓库 -- ?https://github.com/xiangechen/chili3d>
- 在线 -- ?https://chili3d.com/>
- OCCT.js -- ?https://github.com/donalffons/opencascade.js>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/chili3d/>

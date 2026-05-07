---
name: lightcad
description: LightCAD 是开源的轻量级 Web CAD 框架/应用，定位类似 AutoCAD 的二维制图但完全运行在浏览器中，提供命令行、图层、块、DWG/DXF 兼容、绘图与编辑命令，并暴露 JS API 供二次开发与嵌入业务系统。
tags: [web, 2d, cad, dxf, typescript, drafting]
---

> **项目地址：** <https://github.com/light-CAD/lightcad>（如仓库迁移请以 znlgis.github.io 为准）
>
> **官网/演示：** <https://lightcad.cn/>
>
> **许可证：** MIT / Apache-2.0（视仓库声明）

## 概述

LightCAD 主要特性：

- **纯前端 CAD**：HTML5 Canvas / WebGL 渲染，无插件
- **AutoCAD 风格命令行**：line / circle / pline / trim / mirror …
- **DXF 互通**：导入导出 DXF（基于 dxf-parser/dxf-writer）
- **图层 / 块 / 标注 / 文字**
- **可嵌入**：iframe 或 Web Component
- **二次开发 API**：JS/TS 对应实体、命令、事件、UI

> 该项目处于活跃迭代阶段，下文以通用 Web CAD 二次开发为视角，如细节差异请以仓库 README 与 znlgis 教程为准。

---

## 安装与试用

### 在线试用

直接打开 <https://lightcad.cn/> 体验。

### 嵌入 iframe

```html
<iframe src="https://lightcad.cn/" style="width:100%;height:100vh;border:0"></iframe>
```

### 本地部署

```bash
git clone https://github.com/light-CAD/lightcad.git
cd lightcad
pnpm install
pnpm dev      # http://localhost:5173
pnpm build
```

构建产物为静态资源，可托管到任意 CDN。

---

## 嵌入到自有应用（SDK）

```html
<div id="cad" style="width:100%;height:100vh"></div>
<script type="module">
  import { LightCAD } from '@lightcad/sdk';

  const app = new LightCAD({
    container: '#cad',
    locale: 'zh-CN'
  });
  await app.init();

  // 直接执行命令
  app.exec('line 0,0 100,100');
</script>
```

---

## 命令行用法（与 AutoCAD 类似）

| 命令 | 功能 | 示例 |
|------|------|------|
| `line` / `l` | 直线 | `line 0,0 100,0` |
| `circle` / `c` | 圆 | `c 50,50 r 20` |
| `pline` / `pl` | 多段线 | `pl 0,0 10,0 10,10` |
| `arc` / `a` | 圆弧（3点 / 起-中-终） | `a 0,0 10,10 20,0` |
| `rect` / `re` | 矩形 | `re 0,0 100,50` |
| `text` | 文字 | `text 0,0 "Hello"` |
| `dimlinear` | 线性标注 | |
| `move/mv` | 平移 | |
| `copy/cp` | 复制 | |
| `mirror/mi` | 镜像 | |
| `trim/tr` | 修剪 | |
| `extend/ex` | 延伸 | |
| `fillet/f` | 圆角 | `f 10` 后选两条线 |
| `chamfer/cha` | 倒角 | |

---

## 实体与图层（API）

```ts
// 添加实体
const id = app.add('LINE', { p1: [0,0], p2: [100,100] });
app.add('CIRCLE', { center: [50,50], radius: 20, layer: 'WALL' });

// 修改
app.update(id, { color: '#ff0000', lineWeight: 0.3 });

// 查询
const entities = app.query({ type: 'LINE', layer: 'WALL' });

// 删除
app.remove(id);

// 图层
app.layers.add('WALL', { color: '#0000ff', lineType: 'CONTINUOUS' });
app.layers.setCurrent('WALL');
app.layers.set('WALL', { visible: false });
```

---

## 块（Block）

```ts
const blkId = app.blocks.create('CHAIR', {
    base: [0, 0],
    entities: [
        { type: 'CIRCLE', center: [0,0], radius: 5 },
        { type: 'LINE',   p1: [-5,0],    p2: [5,0] }
    ]
});

app.add('INSERT', { block: 'CHAIR', position: [10,10], rotation: 0, scale: 1 });
```

---

## DXF 导入 / 导出

```ts
// 导入
const dxfText = await fetch('/files/plan.dxf').then(r => r.text());
app.io.importDXF(dxfText);

// 导出
const dxf = app.io.exportDXF();
saveAs(new Blob([dxf]), 'out.dxf');

// 导出 SVG / PNG
const svg = app.io.exportSVG();
const png = await app.io.exportPNG({ width: 1920, height: 1080 });
```

---

## 事件

```ts
app.on('selectionChanged', sel => console.log(sel.length, '已选'));
app.on('commandStarted', name => console.log('命令', name));
app.on('entityModified', e => console.log(e.id));
app.on('mouseClick',  e => console.log(e.world));
```

---

## 自定义命令（插件）

```ts
app.commands.register({
    name: 'mycross',
    handler: async (ctx) => {
        const p = await ctx.input.getPoint('选择中心点');
        ctx.app.add('LINE', { p1: [p.x-5, p.y], p2: [p.x+5, p.y] });
        ctx.app.add('LINE', { p1: [p.x, p.y-5], p2: [p.x, p.y+5] });
    }
});
// 命令行：mycross
```

---

## 视图与导航

```ts
app.view.zoomExtents();
app.view.zoomTo([0,0,100,100]);
app.view.pan(10, 0);
app.view.rotate(15);
```

---

## 性能优化

1. **批量添加实体**用 `app.batch(() => { ... })` 包装，仅刷新一次
2. **大量绘制**关闭实时 OSNAP、网格
3. **DXF 导入大文件**用 Web Worker 解析后再注入
4. **样式复用**：定义图层与块，避免每个实体重复样式
5. **PNG 导出**注意分辨率与字体加载

---

## 常见问题

| 问题 | 解决 |
|------|------|
| DWG 不支持 | 先用 ODA File Converter / LibreDWG 转 DXF |
| 中文乱码 | DXF 文件编码为 UTF-8；字体配置 `Noto Sans CJK SC` |
| 标注比例小 | 设置 `dimstyle.scale` |
| 与业务集成 | 监听 `app.on('entityModified', ...)` 同步到后端 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手应区分「在线使用」（用户直接操作 GUI）和「SDK 嵌入」（`LightCAD` 类实例化）。SDK 模式按「app.init() → app.exec(command) 或 app.add(entity) → app.io.exportDXF()」的流程操作。批量添加实体用 `app.batch(() => {...})` 包装。
- **关键注意事项**：① DWG 不支持直接读写，需先用 ODA/LibreDWG 转 DXF；② DXF 文件编码保持 UTF-8，中文文字配置 `Noto Sans CJK SC` 字体；③ 大文件 DXF 导入建议用 Web Worker 解析；④ 标注比例通过 `dimstyle.scale` 设置。
- **常用代码模式**：SDK 初始化：`new LightCAD({ container: '#cad', locale: 'zh-CN' })` → `app.init()` → `app.exec('line 0,0 100,100')`。自定义命令：`app.commands.register({ name, handler: async (ctx) => { const p = await ctx.input.getPoint('...'); ... } })`。

---

## 相关技能

- **librecad** — 开源桌面 2D CAD，DXF 编辑：[../librecad/SKILL.md](../librecad/SKILL.md)
- **qcad** — 2D CAD 软件，ECMAScript 脚本扩展：[../qcad/SKILL.md](../qcad/SKILL.md)
- **chili3d** — Web 3D CAD，类似的前端架构模式：[../chili3d/SKILL.md](../chili3d/SKILL.md)
- **astral3d** — Web 3D 可视化框架，可配合展示 LightCAD 模型：[../astral3d/SKILL.md](../astral3d/SKILL.md)

---

## 典型工作流

### 工作流一：嵌入业务系统作为在线绘图组件

1. `pnpm install @lightcad/sdk` 或使用 iframe 嵌入
2. 在页面中创建容器 `<div>`，实例化 `LightCAD` 并初始化
3. 注册自定义命令（如绘制特殊符号/标注）
4. 监听 `entityModified`/`selectionChanged` 事件同步数据到后端
5. 提供 DXF 导入/导出按钮，调用 `app.io.importDXF()`/`app.io.exportDXF()`
6. 可选：导出 SVG/PNG 用于报表或预览

### 工作流二：命令行驱动快速绘图

1. 初始化 LightCAD 实例后，通过 `app.exec()` 发送 AutoCAD 风格命令
2. `app.exec('line 0,0 100,100')` 绘制直线
3. `app.exec('circle 50,50 r 20')` 绘制圆
4. `app.exec('rect 0,0 100,50')` 绘制矩形
5. `app.io.exportDXF()` 导出为 DXF 文件

---

## 参考资源

- 仓库：<https://github.com/light-CAD/lightcad>
- 文档与示例：<https://lightcad.cn/docs>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/lightcad/>

> 该 SKILL 基于 Web CAD 通用模式整理，具体 API 命名以最新版本仓库为准。
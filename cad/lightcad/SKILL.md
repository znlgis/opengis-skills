---
name: lightcad
description: LightCAD 是开源的轻量级 Web CAD 框架/应用，定位类似 AutoCAD 的二维制图但完全运行在浏览器中，提供命令行、图层、块、DWG/DXF 兼容、绘图与编辑命令，并暴露 JS API 供二次开发与嵌入业务系统。
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

## 参考资源

- 仓库：<https://github.com/light-CAD/lightcad>
- 文档与示例：<https://lightcad.cn/docs>
- 中文教程（znlgis）：<https://znlgis.github.io/cad/tutorial/lightcad/>

> 该 SKILL 基于 Web CAD 通用模式整理，具体 API 命名以最新版本仓库为准。

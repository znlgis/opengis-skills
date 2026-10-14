---
name: chili3d
description: "Use when building or extending browser-based 3D CAD in TypeScript with Chili3D — npm-workspaces source build (rspack), chili-wasm Open CASCADE bindings, command and Plugin contracts with .chiliplugin packaging, STEP/IGES/BREP/STL exchange, ribbon and i18n contributions, measurement tools. Chili3D: a pure-web parametric CAD that runs OCCT in the browser."
tags:
  - web
  - 3d
  - typescript
  - wasm
  - occt
  - parametric
  - step
  - stl
---

> **项目地址：** <https://github.com/xiangechen/chili3d>
>
> **在线体验：** <https://chili3d.com/>（Cloudflare 部署：<https://chili3d.pages.dev>）
>
> **许可证：** AGPL-3.0
>
> **最新稳定版：** 0.7.1（GitHub tag `0.7.1`，2026-09-19；仓库内各包版本一致，npm 上仅 `@chili3d/core` 已发布 0.7.0）
>
> **中文教程：** <https://znlgis.github.io/cad/chili3d/>

## 概述

Chili3D 主要特性：

- **纯前端 CAD**：基于 Three.js + 自研 `chili-wasm`（Emscripten 直接绑定 Open CASCADE，源码在仓库 `cpp/`，不是 opencascade.js）
- **参数化建模**：草图、特征树、捕捉与追踪（对象捕捉 / 工作平面捕捉 / 轴追踪 / 特征点识别）
- **基础几何**：立方体、圆柱、圆锥、球、棱锥、环面；2D 直线/圆弧/圆/椭圆/矩形/多边形/贝塞尔
- **构造运算**：布尔（并/差/交）、拉伸、旋转、扫掠、放样、偏移曲面与厚实体、线性/圆形阵列、形状检查与修复
- **编辑**：倒角、圆角、修剪、打断、分割、缝合、简化、特征移除、子形状操作、复合体炸开
- **测量**：角度、长度、长度和 / 面积和 / 体积和
- **数据交换**：STEP / IGES / BREP / STL 导入导出，完整撤销重做事务栈
- **插件系统**：`plugins/` 内置 helloworld-js / helloworld-ts / macro / visual-programming 示例，`.chiliplugin` 拖拽安装
- **国际化**：内置中/英文，Office 风格 Ribbon

---

## 在线使用

直接打开 <https://chili3d.com/>：

1. 选择「新建」或导入 STEP/IGES/BREP
2. 左侧工具栏：Sketch / Box / Cylinder / Sphere / ...
3. 右侧属性面板：编辑参数、变换
4. 顶部 Ribbon：Boolean / Fillet / Chamfer / Offset / Array
5. 文件 → 导出（STEP / IGES / BREP / STL）

---

## 环境准备：本地部署与二次开发

仓库使用 npm workspaces（根目录有 `package-lock.json`），Node + npm 即可：

```bash
git clone https://github.com/xiangechen/chili3d.git
cd chili3d
npm install

npm run dev           # rspack dev server，http://localhost:8080
npm run build         # 生产构建

npm run test          # Rstest + Happy-DOM 全量测试
npm run testc         # 带覆盖率
npm run check         # Biome lint + 自动修复
npm run format        # Biome + clang-format（TS 与 C++）
```

自研 WASM 模块已随仓库提供（`packages/wasm/lib`），只有需要改 C++ 绑定时才重新编译：

```bash
npm run setup:wasm    # 一次性准备 Emscripten/CMake 依赖
npm run build:wasm    # cmake --preset release 编译，产物回拷到 wasm 包 lib
```

Docker 部署（`compose.yml` 已在仓库根）：

```bash
docker compose up -d  # 构建并在 http://localhost:8080 提供服务
```

构建产物是静态站点，可直接部署到 Nginx / Cloudflare Pages / GitHub Pages。

---

## 项目结构

```text
chili3d/
├── cpp/                    # chili-wasm：CMake + Emscripten 绑定 Open CASCADE
│   └── src/                # opencascade.cpp / factory.cpp / converter.cpp / shape.cpp / mesher.cpp ...
├── plugins/                # 插件示例（npm workspaces 的一部分）
│   ├── helloworld-js/ helloworld-ts/ macro/ visual-programming/
├── packages/
│   ├── core/               # 模型、命令、应用框架（@chili3d/core）
│   ├── three/              # Three.js 渲染（@chili3d/three）
│   ├── wasm/               # chili-wasm 的 TS 封装（@chili3d/wasm）
│   ├── builder/            # 拉伸/旋转/扫掠/放样等特征构建器（@chili3d/builder）
│   ├── element/            # Web Components 控件（@chili3d/element）
│   ├── parametric/         # 参数化功能定义
│   ├── ui/                 # UI 组件
│   ├── web/                # 主 Web 应用（@chili3d/web）
│   ├── app/                # 应用入口（@chili3d/app）
│   ├── storage/            # 项目存储
│   ├── i18n/               # 国际化
│   └── ai/                 # AI 助手集成（@chili3d/ai，依赖 @anthropic-ai/sdk 与 openai）
├── rspack.config.ts        # 打包与 dev server
├── rstest.config.ts        # 测试（rstest + happy-dom）
└── biome.json              # lint / format（4 空格、110 列、双引号）
```

---

## 二次开发的正确姿势

Chili3D 是**应用 + 插件**模型，不是可 `npm install` 的嵌入式 SDK：`@chili3d/*` 中只有 `@chili3d/core` 发布到了 npm（0.7.0），`web/wasm/app/builder` 等仍是工作区包。因此二次开发有两条路：

1. **写插件**（推荐）：在 `plugins/` 下建包，导出 `Plugin` 对象，`npm run package` 产出 `.chiliplugin`，拖拽进应用安装。
2. **改源码**：fork 仓库，在 `packages/*` 内扩展（`npm run build` 会同时构建应用与 `plugins/`）。

整站嵌入自有系统时可用 iframe，但 WASM 依赖 `SharedArrayBuffer`，宿主站点必须返回 COOP/COEP 头：

```html
<iframe src="https://chili3d.com/" allow="cross-origin-isolated"
        style="width:100%;height:100vh;border:0"></iframe>
```

> 需配置 `Cross-Origin-Opener-Policy: same-origin` 与 `Cross-Origin-Embedder-Policy: require-corp`（或本地 dev server 已是 cross-origin isolated）。

---

## 命令系统

命令是 `ICommand` 实现类，用 `command()` 装饰器注册到 `CommandStore`；元数据是 `CommandData`（`key` / `icon` / `toggle` / `helpText` / `helpUrl` / `isApplicationCommand`）：

```ts
import { command, type I18nKeys, type IApplication, type ICommand, PubSub } from '@chili3d/core';

@command({
    key: 'demo.hello' as any,                       // key 属于 CommandKeys 联合类型
    icon: { type: 'path', value: 'icons/hello.svg' }, // 也可传 svg/png/url 或字符串
    helpText: 'demo.hello.description' as any,
})
export class HelloWorldCommand implements ICommand {
    async execute(application: IApplication): Promise<void> {
        // 应用级通知走 PubSub 默认实例，文案 key 交给 i18n
        PubSub.default.pub('showToast', 'demo.hello.message' as I18nKeys);
    }
}
```

`IApplication` 暴露 `mainWindow` `dataExchange` `visualFactory` `shapeProvider` `services` `storage` `views` `documents` `pluginManager` `lastCommand` `executingCommand` `activeView`，以及 `newDocument(name)` / `openDocument(id)` / `loadDocument(data)` / `loadFileFromUrl(url)`。需要中途取消的命令继承 `CancelableCommand`（实现 `ICancelableCommand`，带 `cancel()` 与 `disposeStack`）。

---

## 插件契约（Plugin）

`@chili3d/core` 的 `Plugin` 类型是声明式的：把命令、Ribbon、i18n、服务与「AI 手册章节」一次性交给框架。

```ts
// plugins/my-plugin/src/index.ts
import type { CommandKeys, Plugin } from '@chili3d/core';
import { MyCommand } from './commands/my';

const MyPlugin: Plugin = {
    commands: [MyCommand],
    ribbons: [
        {
            tabName: 'ribbon.tab.manager',
            groups: [{ groupName: 'ribbon.group.other', items: ['demo.hello' as CommandKeys] }],
        },
    ],
    // 追加到 AI 助手读取的应用手册，让助手知道按钮做什么
    guide: [{ name: 'My Plugin', content: 'The “My” button …' }],
    i18nResources: [
        { language: 'zh-CN', display: '简体中文', translation: { 'command.demo.hello': 'TS 插件' } },
    ],
};

export default MyPlugin;
```

配套文件：`manifest.json`（`name` / `version` / `main: dist/main.js` / `engines.chili3d: ">=0.6"` / `importmap`）与 `importmap.json`（插件运行时外部模块映射）。

---

## 直接调用几何内核

`@chili3d/wasm` 提供 `initWasm()`：浏览器里由 Emscripten 自己取 `.wasm`，Node（如 MCP 服务与集成测试）需传入 `wasmBinary`：

```ts
import { initWasm } from '@chili3d/wasm';

// 浏览器
const wasm = await initWasm();
// Node：需要把二进制读出来
// const wasm = await initWasm({ wasmBinary: fs.readFileSync('packages/wasm/lib/chili-wasm.wasm') });

// wasm 上挂的是 OCCT 暴露出来的 BRep* / Geom* 类，构造结果再交给 @chili3d/wasm 的
// converter / factory / shapeProvider 转成 Chili3D 的 shape 与可视对象
```

`@chili3d/wasm` 的导出面：`initWasm`（wasm.ts）、`converter`、`factory`、`shapeProvider`，另有 `geometry` / `shape` / `surface` / `curve` / `stlWriter` 等内部模块；C++ 侧入口是 `cpp/src/opencascade.cpp`。

---

## 文件 I/O

- **项目文件**：应用内保存为 Chili3D 自有 JSON 文档（`IStorage` + `Serialized`），支持完整撤销/重做
- **导入**：File → Import → STEP / IGES / BREP / STL
- **导出**：File → Export → STEP / IGES / BREP / STL
- **插件包**：`.chiliplugin`（拖拽安装）

---

## 渲染层（@chili3d/three）

渲染包内是 `threeView.ts` / `threeGeometry.ts` / `threeGeometryFactory.ts` / `threeHelper.ts` / `threeHighlighter.ts` / `materials.ts` / `meshExporter.ts` / `cameraController.ts` / `threeAnnotation.ts` / `outlinePass.js`，负责把 shape 转成 three 几何、高亮、剖面、导出与相机控制。改材质与高亮行为从这里入手，命令与文档逻辑保持在 `@chili3d/core`，不要把 OCCT 调用写进 UI 层。

---

## 典型工作流

### 工作流一：在线参数化建模与导出

1. 打开 <https://chili3d.com/> 或本地部署实例
2. 新建项目，使用 Sketch 工具绘制 2D 轮廓
3. 通过 Extrude/Revolve 将草图转为 3D 实体
4. 添加圆角、倒角等修饰特征
5. 使用布尔运算（Union/Cut/Intersect）组合多个实体
6. 导出为 STEP/STL 用于下游加工或 3D 打印

### 工作流二：开发一个插件并装入应用

1. 复制 `plugins/helloworld-ts` 作骨架（`manifest.json` + `importmap.json` + `src/index.ts` + `src/commands/`）
2. 用 `@command({ key, icon, helpText })` 定义命令类，实现 `ICommand.execute(application)`
3. 在 `Plugin` 对象里声明 `commands` / `ribbons` / `i18nResources` / `guide`
4. `npm install && npm run build && npm run package` 产出 `.chiliplugin`
5. 打开 Chili3D，把 `.chiliplugin` 拖进窗口 → Ribbon 出现按钮，点击执行
6. `npm run test` 与 `npm run check` 通过后提交（Biome：4 空格、110 列、双引号）

---

## 适用场景

- 适合：教育、Web 演示、轻量 3D 建模、插件化定制、浏览器内 STEP/IGES 查看与转换
- 不适合：大型工业装配、需要严格约束求解的参数化家族建模（仍推荐 FreeCAD / 桌面 OCCT 应用）

---

## 性能要点

1. WASM 内核走 `SharedArrayBuffer`，未启用 COOP/COEP 时退化为单线程
2. 大模型先压缩 STEP，导入后转 BREP 缓存
3. 渲染端关注 `@chili3d/three` 的几何转换与高亮开销，避免每帧重建 BRep 网格
4. 频繁布尔运算放在命令内一次性提交，减少撤销栈与网格重生成次数
5. 浏览器内存有限，STEP 源文件建议控制在百 MB 以内，超出部分服务端处理

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 加载 chili-wasm 失败 | 站点未启用 COOP/COEP；确认响应头与 `cross-origin-isolated` |
| Node 里 `initWasm()` 取不到 wasm | 浏览器外的环境需显式传 `wasmBinary`（Emscripten 无法 fetch） |
| 无法导入 DWG | 目前不支持 DWG，先转 DXF/STEP |
| 中文菜单 | 在语言设置中切换中文（内置 zh-CN 资源） |
| 构建慢或内存溢出 | 用 `npm run build`（rspack 生产构建）；确认未跑 dev 模式产物 |
| 插件不出现按钮 | 检查 `manifest.json` 的 `main` 路径、`importmap.json` 映射，以及 Ribbon `items` 是否为已注册命令 key |
| 改 C++ 绑定后无效果 | 需要 `npm run setup:wasm` + `npm run build:wasm`，产物才会回拷到 wasm 包 lib |

---

## AI 使用建议

- **推荐工作流模式**：区分「在线建模（引导 GUI 操作）」与「插件开发（TypeScript 写命令）」。插件路径优先复用 `plugins/helloworld-ts` 骨架，按 `Plugin` 契约声明能力，不要臆造应用级启动 API。
- **关键注意事项**：① COOP/COEP 与 `SharedArrayBuffer` 是运行前提；② WASM 首次加载较慢，需要进度反馈；③ 命令 `key` 属于 `CommandKeys` 联合类型，新增命令要同步 i18n key；④ 浏览器内存有限，大模型应服务端预处理。
- **常用代码模式**：`@command(...)` 定义命令 → `application.activeView` / `application.documents` 操作当前文档 → `PubSub.default.pub('showToast', key)` 通知 → 几何构造经 `@chili3d/wasm` 的 factory/converter 得到 shape → `@chili3d/core` 的 visual 层显示。

---

## 相关技能

- **astral3d** — Web 3D 可视化与数字孪生框架（glTF/IFC 展示侧）：[../astral3d/SKILL.md](../astral3d/SKILL.md)
- **occt** — 桌面 C++ 几何内核（chili-wasm 绑定的同一内核）：[../occt/SKILL.md](../occt/SKILL.md)
- **freecad** — 桌面参数化 CAD（同样基于 OCCT）：[../freecad/SKILL.md](../freecad/SKILL.md)
- **openscad** — 脚本化 CSG 建模（代码建模范式对照）：[../openscad/SKILL.md](../openscad/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/xiangechen/chili3d>
- 在线应用：<https://chili3d.com/> ｜ Cloudflare 部署：<https://chili3d.pages.dev>
- 插件示例：仓库 `plugins/helloworld-ts`、`plugins/helloworld-js`
- 中文教程（znlgis）：<https://znlgis.github.io/cad/chili3d/>

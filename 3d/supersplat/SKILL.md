---
name: supersplat
description: "Use when editing 3D Gaussian Splatting (3DGS) .ply models in browser — cleanup noise/floaters, crop, transform, color-adjust, animate camera, publish online. SuperSplat: open-source browser-based 3DGS editor by PlayCanvas with PLY/compressed PLY/Splat/KSplat/SOG export."
tags:
  - 3d
  - gaussian-splatting
  - 3dgs
  - webgl
  - webgpu
  - typescript
  - playcanvas
  - editor
---

> **项目地址：** <https://github.com/playcanvas/supersplat>
>
> **在线编辑器：** <https://superspl.at/editor> ｜ **用户手册：** <https://developer.playcanvas.com/user-manual/gaussian-splatting/editing/supersplat/>
>
> **许可证：** MIT ｜ **最新版本：** 参见 [GitHub Releases](https://github.com/playcanvas/supersplat/releases)｜ **默认分支：** `main`

## 概述

SuperSplat 是「3D 高斯泼溅领域的 Photoshop + 发布平台」：完全基于 Web、免下载安装、源码开源。它专为 3DGS「训练之后、上线之前」的后期处理而生，解决原始 `.ply` 噪点多、体积大、坐标不规范、缺乏清理/动画/发布能力等问题。

- **检查 / 编辑**：加载、查看、选择并删除高斯点（噪点、漂浮物 floaters）。
- **变换 / 裁剪**：平移/旋转/缩放、包围盒裁剪、多模型场景管理。
- **外观优化**：颜色调整、球谐（SH）带数控制。
- **动画**：相机姿态关键帧、时间轴、动画导出。
- **导出 / 发布**：多格式导出（含压缩），或一键发布到 PlayCanvas 托管获得分享链接。
- **技术栈**：TypeScript + PlayCanvas 引擎（`createGraphicsDevice` 初始化 WebGL2/WebGPU）+ PCUI 组件库 + i18next 国际化 + Rollup 构建。

> 3DGS 由 Inria 2023 年论文《3D Gaussian Splatting for Real-Time Radiance Field Rendering》提出，相比 NeRF 具备实时渲染、训练快、画质高的优势。

---

## 在线使用（推荐）

直接打开 <https://superspl.at/editor>，将训练产出的 `.ply`（COLMAP + gaussian-splatting / Postshot / Nerfstudio 等）拖入即可，无需安装。

典型后期处理流程：

1. **导入** `.ply` 高斯模型。
2. **清理**：用选择工具框选/套索选中噪点与漂浮物 → 删除（删除仅打 `deleted` 标记，导出时才真正剔除，可撤销恢复）。
3. **裁剪**：用包围盒裁掉无关区域。
4. **变换**：摆正坐标系、调整朝向与比例（多模型场景可分别变换）。
5. **调色**：调整颜色、设置保留的 SH 带数。
6. **动画**（可选）：设置相机关键帧与时间轴。
7. **导出 / 发布**：选择格式导出，或发布到云端。

---

## 导出格式

导出弹窗（`src/ui/export-popup.ts`）支持：

| 格式 | 扩展名 | 特点 | 适用场景 |
|------|--------|------|----------|
| 标准 PLY | `.ply` | 无损、体积大、通用 | 归档、再编辑、跨工具交换 |
| 压缩 PLY | `.compressed.ply` | PlayCanvas 量化压缩，体积大幅减小，仍是 PLY | Web 加载、平衡体积与兼容性 |
| Splat | `.splat` | antimatter15 紧凑二进制 | 轻量 Web 查看器 |
| KSplat | `.ksplat` | mkkellogg 的分块/可流式格式 | Three.js 高斯查看器 |
| SOG | `.sog` | Self-Organizing Gaussians，WebP 纹理存储，体积极小 | Web 发布、移动端 |

**减小体积三板斧**（常把数百 MB 压到几 MB）：

- **删除噪点**：导出时被标记删除的点不写入，点数 = 原始 − 已删除。
- **Compress PLY**：开启量化压缩。
- **降低 SH Bands**：高阶球谐占绝大多数属性；Web 场景常保留 0–1 阶即可，会损失少量视角相关高光但显著减小体积。

**带查看器导出**：可打包成自包含 **HTML** 或 **ZIP（Package）**，含相机动画与循环模式（`none` / `repeat` / `pingpong`），双击即可在浏览器观看。

---

## 发布到 PlayCanvas 平台

一键发布（`src/publish.ts`、`src/ui/publish-settings-dialog.ts`）获得在线可分享、可嵌入链接：

1. **登录校验**：`fetchUser()` 请求 `/api/id`；未登录引导登录 PlayCanvas 账号。
2. **填写设置**：标题、描述、是否公开列出（`listed`）。
3. **分片上传**：`PublishWriter` 经 `start-upload` → `signed-urls` → 分片 PUT → `complete-upload`。
4. **发布**：调用 `/splats/publish`，格式为 SOG；开启 `generateLods` 则为 `ssog`（多分辨率 LOD，加载更快）。

---

## 本地开发与二次开发

```bash
git clone https://github.com/playcanvas/supersplat.git
cd supersplat
npm install            # 需 Node ≥ 20.19.0
npm run develop        # = watch（Rollup 监听构建）+ serve（静态服务 dist）
```

> ⚠️ SuperSplat 注册了 Service Worker（`src/sw.ts`）。开发调试务必关闭缓存：Chrome DevTools → Application → Service Workers 勾选 “Update on reload”，或 Network 勾选 “Disable cache”，否则可能看到旧版本。

常用脚本（`package.json`）：

| 命令 | 作用 |
|------|------|
| `npm run build` | 生产构建（`rollup -c`） |
| `npm run watch` | 仅监听构建 |
| `npm run serve` | 仅启动静态服务器 |
| `npm run lint` | ESLint 检查 `src` |

### 源码架构速览

| 模块 | 职责 |
|------|------|
| `src/main.ts` | 应用入口，按序装配编辑器；用 PlayCanvas `createGraphicsDevice` 初始化 WebGL2/WebGPU |
| `src/events.ts` | `Events` 类继承 PlayCanvas `EventHandler`，扩展函数注册/调用，是 UI 与逻辑**解耦**的核心 |
| `src/scene.ts` / `src/pc-app.ts` | `Scene` 基于 `PCApp`，管理一组 Element（`ElementType`：`Splat`/`Camera`/grid/叠加层等） |
| `src/splat.ts` / `src/splat-state.ts` | `Splat` 类封装 GSplat 资源与每点状态（含 `deleted`/hidden 标记） |
| `src/splat-serialize.ts` / `src/file-handler.ts` | 序列化与文件读写（导出核心） |
| `src/ui/`（基于 `@playcanvas/pcui`） | `EditorUI` 装配菜单/工具栏/面板；面板通过事件与逻辑通信 |
| `src/ui/localization.ts` | i18next 多语言，语言文件 `static/locales/*.json` |
| `rollup.config.mjs` | TypeScript + node-resolve + SCSS + image/json，生产用 terser 压缩、strip 去调试 |

**二次开发要点**：UI 与逻辑通过 `Events` 事件解耦——新增功能通常是「注册事件/函数 + 新增面板组件」，而非直接耦合调用。

---

## 常见问题（FAQ）

| 问题 | 解决 |
|------|------|
| 删除后文件没变小 | 删除只打标记，**导出时**才真正剔除；导出后点数才下降 |
| 想恢复误删的点 | 用撤销（Undo）恢复 `deleted` 标记；导出前务必确认清理无误 |
| 隐藏(hidden)与删除区别 | 隐藏的点默认仍会导出，删除的点导出时被剔除 |
| 导出文件太大 | 删噪点 + 勾选 Compress PLY + 降低 SH Bands；Web 发布优先压缩 PLY 或 SOG |
| 本地开发看到旧版本 | Service Worker 缓存，按上文关闭缓存 / Update on reload |
| `npm install` 失败 | 确认 Node ≥ 18 |
| 该用哪种格式 | 继续编辑/归档→PLY；网页加载→压缩 PLY 或 SOG；对接特定查看器→splat/ksplat |
| 原始 .ply 从哪来 | 3DGS 训练工具（COLMAP+gaussian-splatting、Postshot、Nerfstudio 等）产出 |

---

## AI 使用建议

- 用户提到「高斯泼溅 / 3DGS 编辑」「清理 .ply 噪点」「压缩高斯模型上网页」「SuperSplat 二次开发」时加载本技能。
- 区分**用工具**（在线 superspl.at/editor 的后期处理流程）与**改源码**（本地 `npm run develop` + 事件驱动架构）两类需求。
- 减体积一律建议「删除噪点 + Compress PLY + 降低 SH Bands」组合，并按目标查看器选格式。
- 提醒本地开发关闭 Service Worker 缓存，否则改动不生效。
- 二次开发强调通过 `src/events.ts` 的 `Events` 解耦，新增功能=注册事件+新增 PCUI 面板。

---

## 参考资源

- 用户手册：<https://developer.playcanvas.com/user-manual/gaussian-splatting/editing/supersplat/>
- PlayCanvas 引擎：<https://github.com/playcanvas/engine>
- 3DGS 论文：《3D Gaussian Splatting for Real-Time Radiance Field Rendering》(Inria, 2023)
- 上游中文教程：<https://znlgis.github.io/>（3d/supersplat 系列）

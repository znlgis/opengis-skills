---
name: chags
description: "Use when building or extending CHAGS (Chinese Historical Anecdotes Game Series): each Chinese historical anecdote is one small kids game built with Phaser 4.2 inside a Vue 3.5 + Pinia shell (TypeScript 5.9.3, Vite 8, pnpm workspace, zh/en bilingual). Covers the GameModule/GameContext contract, gameplay template library, JSON + zod content model, IndexedDB saves with spaced-review scheduling, Vitest/Playwright quality gates, and Tauri/Capacitor packaging."
tags:
  - vue
  - typescript
  - phaser
  - game
  - education
  - i18n
  - vite
  - pnpm
---

> **项目地址：** <https://github.com/znlgis/CHAGS>
>
> **许可证：** MIT ｜ **最新版本：** `v0.0.5`（GitHub tag / Release 一致，截至2026-10）

## 概述

CHAGS（Chinese Historical Anecdotes Game Series，中国历史典故儿童游戏合集）是面向 6–12 岁儿童的开源 H5 游戏合集：「一个典故一个小游戏」，让孩子在「做」故事的过程中记住典故。17 个典故已全部跑通，界面 / 内容 / 语音支持中英双语一键切换。架构是「Phaser 4.2 管游戏 + Vue 3.5 管外壳」的双栈：外壳负责典故馆 / 图鉴 / 路由，每个典故是一个独立游戏包，懒加载、纯代码绘制。无后端、无账号、无广告，进度只存本机 IndexedDB；同一份站点产物还能打成 Windows 便携 exe（约 3.3 MB）与安卓 apk。

### 核心特性

| 特性 | 说明 |
|------|------|
| 典故合集 | 17 部（神话 / 传说 / 信史 / 寓言），每部有一个只属于它的「动词」 |
| 双栈隔离 | Phaser 绝不进外壳首屏包，只在进入游戏时按需加载 |
| 契约层 | `packages/game-kit` 定义 GameModule / GameContext / 事件协议，游戏与外壳互不认识 |
| 玩法模板库 | story / substitution / tap / place / aim / sort / trace / wait / mark / split / burrow / quiz / reward |
| 内容驱动 | 典故 = 一份 JSON（zod schema 构建期校验），换典故不改代码 |
| 记忆工程 | `keyMoment` 关键抉择 + `misconceptions` + transfer 迁移题 + 1/3/7/21/60 天复习调度 |
| 质量门禁 | `pnpm verify` 六连跑 + Playwright 真实鼠标操作通关 + 体积守卫 |
| 多端分发 | Web 静态站点 / Tauri 2 便携 exe / Capacitor 8 apk |

---

## 环境准备 / 快速开始

### 前置条件

- Node.js 24.x（Vite 8 要求现代 Node，CI 统一用 Node 24）
- pnpm 11.x（根 `package.json` 声明 `"packageManager": "pnpm@11.22.0"`）
- Chromium 系浏览器（开发预览与端到端测试）

### 安装与启动

```bash
git clone https://github.com/znlgis/CHAGS.git
cd CHAGS
pnpm install
pnpm dev        # http://127.0.0.1:5183（strictPort，端口被占用会直接报错）
```

### 验证方式

```bash
pnpm verify     # typecheck → lint → test → content:check → build → size，全绿才算「完成」
pnpm e2e        # 首次需 npx playwright install chromium
```

### 常用命令

| 命令 | 作用 |
|------|------|
| `pnpm dev` | 开发服务器 `127.0.0.1:5183`（改 packages/games 即时热更新） |
| `pnpm verify` | 提交前完整门禁：typecheck → lint → test → content:check → build → size |
| `pnpm test` | Vitest 单测（Node 环境，纯逻辑，不碰 DOM / WebGL） |
| `pnpm content:check` | 典故 JSON + 模板关卡脚本 + 双语完整性校验 |
| `pnpm e2e` / `pnpm e2e:dist` | Playwright 端到端（开发服务器 / 生产构建产物） |
| `pnpm audit:i18n` | 双语版面巡检，截图到 `.scratch/i18n-audit/`（不入库） |
| `pnpm dist:win` / `pnpm dist:apk` | 打包 Windows 便携 exe / 安卓 apk |

### 调试直达

```text
http://127.0.0.1:5183/?autoplay=1#/play/caochong-elephant   # 自动通关，用于无头验证
http://127.0.0.1:5183/?lang=en#/play/pangu                  # 强制英文（界面 + 内容 + 语音）
http://127.0.0.1:5183/?seed=fixed#/play/pangu               # 注入确定性种子（预留参数）
```

事件轨迹观测：控制台里 `window.__chags.events`（事件序列）与 `window.__chags.lastError`（最近一次载入失败详情）。

---

## 工程结构

```text
CHAGS/
├─ apps/
│  ├─ site/          # Vue 3.5 外壳：典故馆 / 我的图鉴 / 游戏宿主（唯一产品代码入口）
│  ├─ desktop/       # Tauri 2 桌面壳（Windows 便携 exe）
│  └─ mobile/        # Capacitor 8 安卓壳（apk）
├─ packages/
│  ├─ game-kit/      # 契约层：GameManifest / GameContext / GameModule / 事件 / 平台接口（不含 Phaser）
│  ├─ content/       # 17 份典故 JSON + zod schema + 英文翻译补丁
│  ├─ templates/     # 玩法模板库 + defineGame + 关卡脚本 schema + content:check CLI
│  ├─ phaser-kit/    # Phaser 启动器 / 主题 / BaseScene / 卡通绘制 / 拖拽控制器
│  ├─ platform/      # Web 平台实现：IndexedDB / WebAudio / TTS / 生命周期
│  ├─ progress/      # 存档 + 复习调度（纯 TS，可单测）
│  └─ i18n/          # 界面文案表与取词器
├─ games/<id>/src/   # 17 个游戏包：manifest / logic / art / index (+ 专属 scenes/)
├─ e2e/              # Playwright：冒烟 / 真实操作 / 双语 / 慢设备 / 截图
├─ scripts/          # 体积守卫 / apk 构建 / 图标生成
└─ docs/             # 技术方案、典故方案、打包方案
```

五层分工：**外壳**（apps/site，路由 + Pinia + 宿主）→ **游戏包**（games/*，场景编排 + 绘制 + 纯逻辑）→ **契约**（game-kit）→ **模板 / 渲染工具箱**（templates + phaser-kit）→ **平台 / 进度 / 文案**（platform + progress + i18n）。

依赖方向永远向下，且 `game-kit` 与 `content` 不含 Phaser 依赖（外壳可以安全 import）；所有包都是 private 包，`exports` 直连源码、无构建步骤，改一处全仓即时生效。

---

## 核心契约与机制

### 契约层（packages/game-kit/src/contract.ts）

```ts
export interface GameManifest {
  id: string;                        // 必须与内容 JSON 的 id 一致
  title: string;
  version: string;                   // semver，用于存档迁移
  template: TemplateId;              // 主玩法模板 id
  orientation: 'portrait' | 'landscape';
  designSize: { width: number; height: number };   // 逻辑分辨率 750×1334（DESIGN 常量）
  ageRange: [number, number];
  sessionSeconds: [number, number];
  skills: string[];
  curriculum: { dynasty: string; yearApprox?: number; figures: string[] };
  assets: { cover: string };         // 当前全部 'none'（零图片资源，画面由代码绘制）
}

export interface GameModule {
  manifest: GameManifest;
  mount(ctx: GameContext): Promise<void>;   // 内部 new Phaser.Game(...)
  unmount(): Promise<void>;                 // 必须 game.destroy(true)，零全局残留
  pause(): void;                            // game.loop.sleep()
  resume(): void;                           // game.loop.wake()
}

export interface GameContext {
  container: HTMLElement;
  manifest: GameManifest;
  content: AllusionContent;          // 已是目标语言的翻译结果，游戏内不存在语言分支
  services: PlatformServices;        // 存档 / 音频 / 生命周期 / 分享 / 遥测
  locale: 'zh-CN' | 'en';
  reducedMotion: boolean;
  debug?: DebugOptions;              // ?autoplay=1&seed=... 解析结果
  emit<K extends keyof GameEventMap>(type: K, payload: GameEventMap[K]): void;
  requestExit(): void;               // 把控制权交还外壳
}
```

`PlatformServices` 是唯一的环境出口：`storage`（ProgressStore，Web 端为 IndexedDB）、`audio`（unlock / play / tone / speak / stopSpeech / setMuted）、`lifecycle`、`share`、`telemetry`（默认 no-op）、`now()`。游戏内禁止直接 `localStorage` / `fetch`。

### 事件协议（GameEventMap）

`session:start` / `scene:enter` / `beat:enter` / `choice:made` / `hint:used` / `level:complete` / `card:unlocked` / `session:exit` 八个事件同时打给四个消费者：外壳（`level:complete` 写入存档）、调试桥（`window.__chags.events`，生产也开着）、端到端测试（按事件序列断言流程）、遥测（只做本地缓冲）。模板还会用 `beat:enter:<id>` 报告每一幕、每个槽位、每条里程碑。

### defineGame：三段式装配

```ts
export interface GameDefinition {
  manifest: GameManifest;
  drawBeat?: (g, index, rect) => void;   // 分幕插图：每个典故自己画
  gameplay: (ctx: GameContext, session: SessionState) => GameplayStage;
}
// GameplayStage = { entry: string; scenes: SceneType[] }

export function defineGame(definition: GameDefinition): GameModule;
```

`mount()` 内部按「分幕故事 + 玩法场景（一到多个）+ 典故卡」组装场景列表并启动 Phaser；游戏包只回答「怎么画、怎么拼」。一个真实例子（刻舟求剑的 `src/index.ts`，省略 import）：

```ts
export default defineGame({
  manifest,
  drawBeat,
  gameplay: (ctx, session) => ({
    entry: SCENE_KEYS.mark,
    scenes: [
      createMarkScene(ctx, {
        level: markLevel(ctx.content),      // 关卡数据从内容 JSON 取，不写死数字
        session,
        nextSceneKey: SCENE_KEYS.reward,
        titleKey: 'scene.mark',
        waterY: WATER_TOP,
        drawWorld: (g, state) => drawWorld(g, state),
        drawFinale: (g, state) => drawFinale(g, state),
        reveal: ctx.content.keyMoment.reveal,
      }),
    ],
  }),
});
```

### 内容模型（packages/content）

典故是一份 JSON，由 `AllusionSchema`（zod）在被 import 时构建期解析，字段错误立刻抛错。以下为结构节选（以刻舟求剑为例）：

```jsonc
{
  "id": "kezhou",                              // 小写字母 / 数字 / 连字符
  "kind": "fable",                             // history | myth | legend | fable
  "title": "刻舟求剑", "pinyin": "kè zhōu qiú jiàn",
  "dynasty": "战国", "era": "战国·寓言", "yearApprox": -239,   // 公元前为负数
  "figures": ["楚人"],
  "source": { "book": "《吕氏春秋·察今》", "quote": "楚人有涉江者……" },
  "moral": "世界一直在动，记号要刻在不动的地方。",               // ≤ 90 字，孩子能听懂
  "keywords": ["变化", "记号", "找回来"],
  "story": [ /* 2–6 幕：每屏一句话（text ≤ 90 字符）+ 更长的旁白 narration */ ],
  "keyMoment": { "beatId": "s2", "question": "……", "options": [ /* 恰好 1 个 isCanonical */ ], "reveal": "……" },
  "misconceptions": [ "在哪儿做的记号，就在哪儿下水" ],          // ≥ 1 条
  "quiz": [ /* ≥ 2 题，至少 1 道 transfer 迁移题 */ ],
  "game": { "template": "mark", "stages": [ { "template": "mark", "levelScript": { /* 模板 schema 校验 */ } } ] }
}
```

schema 末尾五条 `refine` 把教学要求变成数据约束：answer 下标越界拒绝；`keyMoment` 恰好一个标准答案；`keyMoment.beatId` 必须命中 story 某一幕；story 的 beat id 不能重复；quiz 至少一道 transfer 题（记忆题证明「记得」，迁移题验证「理解」）。

`stages` 支持一个典故由多段模板拼成（盘古 = tap 撑天 + place 化身；大禹 = tap 筑堤 + trace 疏河）。`stageScript(content, template)` 取脚本、缺失即早失败。

### 玩法模板（packages/templates）

模板 = 交互原语 + 循环 + 纯逻辑判定（`*.logic.ts`）+ 外置绘制回调（`drawStage` / `drawPiece` / `drawWorld` …）。工厂函数返回场景类，画面完全由游戏包绘制 —— 同一个 tap 循环下，盘古撑天、精卫投石、夸父奔跑、愚公挖山，四段画面毫不相干。

| 模板 | 交互原语 | 代表典故 |
|------|---------|---------|
| `story` | 分幕绘本 + 旁白（全部游戏共用开场） | 全部 |
| `substitution` | 拖拽 + 水痕：等量代换 | 曹冲称象 |
| `tap` | 连点 / 长按推进进度 | 盘古 / 精卫 / 夸父 / 愚公 / 大禹 |
| `place` | 把东西拖到该去的地方 | 盘古化身 / 女娲补天 / 杞人忧天 |
| `aim` | 拉弓瞄准射击 | 后羿射日 / 百步穿杨 |
| `sort` | 分类归位（可带「先尝后分」） | 神农尝百草 |
| `trace` | 手指划路，按顺序过锚点 | 大禹治水 |
| `wait` | 以「不动作」为玩法（终点可延后但永远等得到） | 太公钓鱼 |
| `mark` | 记号与参照系（会动的记号找不到东西） | 刻舟求剑 |
| `split` | 说法与实质的对照 | 朝三暮四 |
| `burrow` | 挖洞应对危险波次 | 狡兔三窟 |
| `quiz` / `reward` | 复习问答（待接线）/ 典故卡（全部结尾） | 全部 |

数据登记规则「场景可专属、数据必登记」：beacon（烽火戏诸侯）、butcher（庖丁解牛）的场景在各自游戏包里，但关卡数据登记在 `templateSchemas` 注册表 —— `content:check` 的双语校验与 schema 体检才能覆盖它们。

三条贯穿所有模板的行为规则：逐帧重画（游戏包在一个 `drawXxx` 回调里画整个世界）；autoplay 走与真实操作**相同**的内部方法；零失败（放错弹回、不判错、不扣分，仅刻意体验的动作计 `mistakes`）。

### 存档与复习调度（packages/progress）

```ts
export const SAVE_SCHEMA_VERSION = 1;
export const REVIEW_INTERVALS_DAYS = [1, 3, 7, 21, 60];   // 简化版 SM-2：答对升级、答错降级
export function gradeFromScore(correct: number, total: number): 0 | 1 | 2 | 3;  // ≥ 60% 即 2 级
```

- `ProgressManager` 是存档唯一入口：不可变更新、`stars: Math.max(...)`（重玩不掉星）、`due()` 查询到期；
- 构造注入 `ProgressStore` 与 `clock()`，坏档安全降级为空档，测试可在内存里跑；
- 现状：星星与图鉴已接线；quiz 模板与 `recordReview` 已实现，但到期复习的 UI 入口尚未接线（阶段 1 遗留，接入路径见教程第 10 章）。

### 双语实现（packages/i18n + content/i18n）

中文是基准语言；`packages/content/src/i18n/en/<id>.json` 是结构镜像的翻译补丁（只写需翻译字段，数组按索引对齐），在 `i18n/index.ts` 注册。外壳调用 `getAllusion(id, locale)` 合并后交给游戏 —— 游戏代码零语言分支，新增语言 = 加补丁 + 界面文案表。`content:check` 校验缺键、结构不一致、合并后超 schema，并用 CJK 扫描抓漏翻字段。

---

## 典型工作流：从零新增一个典故

以「孔融让梨」（复用 `place` 模板）为例的端到端流程。

**输入**：定性（信史 · 东汉 · `yearApprox: 190`）、一句话寓意、真实出处原文、玩法骨架（三只大小不同的梨送到三位家人手里）。

**步骤 1：写内容 JSON（内容先立住）**

新建 `packages/content/src/allusions/kongrong.json`，再在 `allusions/index.ts` 注册两行：

```typescript
import rawKongrong from './kongrong.json';
// 在 allusions 数组里追加：
AllusionSchema.parse(rawKongrong),
```

**步骤 2：写英文补丁**

新建 `i18n/en/kongrong.json`（结构镜像），在 `i18n/index.ts` 的 `patches.en` 注册。注意 `orbs[].speak` 这类面向孩子的关卡文案也要翻译，漏翻会被 CJK 扫描抓住。

**步骤 3：跑内容校验**

```bash
pnpm content:check
# · 孔融让梨 (kongrong)
#   · 信史 / 2 幕故事 / 3 道复习题 / 1 段玩法：place
```

脚本非法（光球数与槽位数不一致、凑不出目标重量等）这时就会报错 —— 内容通过后再写游戏代码。

**步骤 4：写游戏包 `games/kongrong/`**

六个文件：`package.json`（`@chags/game-kongrong`，`workspace:*` 依赖，`exports` 直连 `src/index.ts`）、`src/manifest.ts`、`src/logic.ts`、`src/art.ts`、`src/index.ts`、`src/logic.test.ts`。然后跑一次 `pnpm install` 建立 workspace 链接。

```typescript
// src/logic.ts —— 纯逻辑：不碰 Phaser，可以直接单测
export function placeLevel(content: AllusionContent): PlaceLevel {
  return PlaceLevelSchema.parse(stageScript(content, 'place'));
}
```

```typescript
// src/index.ts —— defineGame 自动装上分幕故事与典故卡
export default defineGame({
  manifest,
  drawBeat,
  gameplay: (ctx, session) => ({
    entry: SCENE_KEYS.place,
    scenes: [
      createPlaceScene(ctx, {
        level: placeLevel(ctx.content),
        session,
        nextSceneKey: SCENE_KEYS.reward,
        drawPiece,
        drawOrb,
        reveal: ctx.content.keyMoment.reveal,
      }),
    ],
  }),
});
```

**步骤 5：外壳注册两处**

`apps/site/src/registry.ts` 加一行 `kongrong: () => import('@chags/game-kongrong')`；`apps/site/package.json` 加依赖。`registry.test.ts` 会强制「内容目录、注册表、懒加载入口」三方一致。

**步骤 6：补端到端用例**

在 `e2e/smoke.spec.ts` 加一条真实操作通关用例（拖拽坐标直接从内容 JSON 读，不手抄）；双语载入与 autoplay 用例会枚举内容目录，自动覆盖新典故。

**步骤 7：收尾验证**

```bash
pnpm verify     # 六连跑全绿
pnpm e2e        # 真实鼠标操作 + autoplay 都过
pnpm audit:i18n # 文案 / 版面有改动时，人工看一眼两种语言下的每个画面
```

**输出**：大厅多一张按 `yearApprox` 排序的典故卡；构建产物多一个几 KB 的独立懒加载 chunk（Phaser 仍是共享 chunk）；图鉴可收集典故卡。

---

## 最佳实践 / 常见陷阱

- **Phaser 实例必须用 `shallowRef` / `markRaw` 持有**：`ref` 会深度代理整个 Phaser 对象图（场景、纹理、WebGL 上下文），轻则卡顿重则抛错。
- **离场必须 `await unmount()`**（内部 `game.destroy(true)`）：宿主加 `disposed` 标记，不放 `<KeepAlive>` / `<Transition>`；编辑 Phaser 场景时整页刷新，否则 HMR 会叠出多个 canvas。
- **逻辑层禁用 `Math.random` 与 `Date.now`**（lint 强制）：时钟从 `services.now()` 或构造注入，保证测试可复现。
- **长按 / 等待类进度按墙钟计时，不累加帧间隔**：Phaser 在低帧率时钳制 delta，慢手机上「按住 6 秒」会累积不到 6 秒。
- **快速 projectile 命中按「一帧扫过的线段」判定**，并取沿弹道最先碰到的目标（点判定会漏、按垂直距离会选错）。
- **内容数值约束写进 schema refine**：tap 强制整除（否则永远点不满）、substitution 用背包校验「容差内可通关」（否则可凑不出）。
- **新增典故要三处对账**：内容 JSON / `allusions/index.ts` / `registry.ts`（+ apps/site 依赖），`registry.test.ts` 会兜底；`manifest.id` 与内容 `id` 不一致时挂载即抛错。
- **屏幕文字按英文长度设限**（`story.text ≤ 90 字符`），长内容放进 `narration` 交给 TTS；英文长句是排版问题的高发区。
- **零失败与宽松星级**：放错弹回不惩罚；星星门槛宽（错 ≤ 1 次三星），对小朋友永远正向。
- **游戏内禁止直接 `localStorage` / `fetch`**：一律走 `GameContext.services`，这是将来上小游戏 / 云存档的唯一低成本出口。

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `pnpm install` 报找不到 workspace 依赖 / `workspace:*` 无法解析 | 用错包管理器了；删 `node_modules` 后用 pnpm 重装，全仓统一 pnpm |
| `vue-tsc` 报 `ERR_PACKAGE_PATH_NOT_EXPORTED: './lib/tsc'` | TypeScript 被升级到 7.x 了；仓库刻意锁 `~5.9.3`（vue-tsc 依赖该子路径），恢复锁定版本，勿 `pnpm add typescript@latest` |
| 端口 5183 被占用 | `strictPort: true` 会直接报错；停掉占用进程（改端口需同步 e2e 的 baseURL，更推荐前者） |
| `pnpm e2e` 报没找到浏览器 | 先执行 `npx playwright install chromium`（CI 用 `--with-deps chromium`） |
| `pnpm size` 报 `ENOENT ... apps/site/dist/index.html` | size 读构建产物，先 `pnpm build`；`pnpm verify` 内部顺序已排好 |
| `pnpm dist:apk` 报 `Unsupported class file major version 69` | JDK 25 超出 Gradle 8.14 支持范围；装 JDK 17–24，或用 `CHAGS_JDK` 环境变量指定 |
| 进度存在哪里？会丢吗？ | 本机 IndexedDB（无账号、不同步）；刷新 / 重开都在，清浏览器数据或换设备会丢；云存档只需替换 `ProgressStore` 实现 |
| 游戏打不开，界面上只有一句「这个典故暂时打不开」 | 技术详情在 `window.__chags.lastError` 与控制台；多为内容 / 关卡数据校验失败，跑 `pnpm content:check` 定位 |
| 有题库，为什么通关后不答题？ | 刻意不挂「每局结束」——与「少写字、多动手」冲突；quiz 模板与双语题数据已就位，等「到期复习」入口接线 |
| 慢设备上按住奔跑进度不对？ | 已改按墙钟计时并有 4 倍 CPU 降速的 Playwright 用例防回归；不要在逻辑层用帧 delta 累积进度 |

---

## 相关技能

- **vue3-map-dashboard** — Vue 3 + Vite + TypeScript 前端工程（同批技能，技术栈与本项目外壳一致）：[../../demos/vue3-map-dashboard/SKILL.md](../../demos/vue3-map-dashboard/SKILL.md)
- **photo-sphere-viewer** — 浏览器端 Three.js 全景查看器（同为 TypeScript / Vite 构建的 WebGL 应用）：[../../3d/photo-sphere-viewer/SKILL.md](../../3d/photo-sphere-viewer/SKILL.md)
- **全仓技能总索引** — 按分类浏览 80 个技能：[../../SKILL.md](../../SKILL.md)

---

## 参考资源

- [CHAGS GitHub 仓库](https://github.com/znlgis/CHAGS) — 源码、Issue 与 Release
- [CHAGS 项目教程（16 章）](https://znlgis.github.io/others/CHAGS/) — 从概述到踩坑记录的完整中文教程
- [Phaser 4 官方站点](https://phaser.io/) — 游戏引擎文档与 API
- [Vue 3 文档](https://vuejs.org/) / [Pinia](https://pinia.vuejs.org/) — 外壳技术栈
- [Vitest](https://vitest.dev/) / [Playwright](https://playwright.dev/) — 测试体系
- [Tauri](https://tauri.app/) / [Capacitor](https://capacitorjs.com/) — 桌面与安卓壳

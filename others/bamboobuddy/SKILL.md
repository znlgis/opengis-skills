---
name: bamboobuddy
description: "Use when building or extending BambooBuddy (A Panda's Day) — a pnpm-workspace kids habit game: Vue 3.5 shell plus Phaser 4.2 game packages, the GameModule/GameContext contract, task JSON validated by zod, 8 gameplay templates across 10 daily tasks, IndexedDB saves with four growth stages, and Vitest/Playwright gates. Also for pnpm verify stage failures, TypeScript 7 breaking vue-tsc, Phaser leaking into the first-screen chunk, and Tauri/Capacitor packaging errors."
tags:
  - vue
  - typescript
  - phaser
  - game
  - education
  - pnpm
  - vite
  - pwa
---

> **项目地址：** <https://github.com/znlgis/BambooBuddy>
>
> **在线试玩：** <https://znlgis.github.io/bamboobuddy/>
>
> **官方文档：** 17 章中文教程：<https://znlgis.github.io/others/BambooBuddy/>
>
> **包管理器：** pnpm 11.22.0（根 `package.json` 的 `packageManager` 字段锁版本）+ Node.js 24（截至 2026-10）
>
> **版本：** `v0.0.2`（GitHub Release，2026-10-20；仓库根 `package.json` 的 version 为 0.1.0）
>
> **许可证：** MIT

## 概述

BambooBuddy（《熊猫宝宝的一天》，副标题 *A Panda's Day*）是面向 4–8 岁儿童的习惯养成 H5 游戏：孩子照顾一只叫「竹竹」的大熊猫，在刷牙、洗手、吃饭、穿衣、洗澡、睡觉、整理、运动、情绪、学习这十件小事里一件件帮它做好。产品指标只有一句「孩子今天愿意把某个好习惯真的做一遍」，由此定下所有技术取舍——没有失败、没有倒计时、没有体力、没有广告、没有账号，进度只存在本机。

架构是「Phaser 管游戏 + Vue 管外壳」的双栈，`pnpm` workspace 分成三层：`apps/*`（壳）、`packages/*`（库）、`games/*`（玩法包）。核心能力：

- **契约隔离**：`packages/game-kit` 只放类型（`GameModule` / `GameContext` / 事件表 / 存档形状），游戏包与外壳互不认识
- **内容驱动**：一条任务 = 一份 JSON（摘要 + 详情），由 zod 在构建期与 `content:check` 双重校验，换任务不改代码
- **模板复用**：8 个交互模板撑 10 个任务，差异化全部落在关卡数据上
- **零美术资源**：所有角色、房间、食物由代码绘制，12 个音效由 WebAudio 合成
- **可测**：逻辑层不 import Phaser，单测（Vitest）全在 Node 环境跑；真实的按住/拖拽/连点交给 Playwright
- **多端**：同一份 `apps/site/dist` 喂 Web 静态站、Tauri 2 桌面壳与 Capacitor 8 安卓壳

## 环境准备

### 前置条件

| 依赖 | 版本 | 何时需要 |
|------|------|---------|
| Node.js | 24 | 必需（Vite 8 与 Playwright 1.64 要求 20+，仓库以 24 为基线） |
| pnpm | 11.22.0 | 必需，版本由 `packageManager` 字段锁定 |
| Chromium | Playwright 自带 | 仅跑 `pnpm e2e` 时需要 |
| Rust 工具链 | — | 仅 `pnpm dist:win`（Tauri 2） |
| JDK + Android SDK | — | 仅 `pnpm dist:apk`（Capacitor 8）；`pack:check` 不装也能跑 |

### 安装（两种方式）

```bash
# 方式一：Corepack（读 packageManager 字段，自动选到 11.22.0）
corepack enable
corepack prepare pnpm@11.22.0 --activate

# 方式二：全局安装指定版本
npm install -g pnpm@11.22.0
```

```bash
git clone https://github.com/znlgis/BambooBuddy.git
cd BambooBuddy
pnpm install          # 本地开发：允许更新 lockfile
# pnpm install --frozen-lockfile   # CI/发布：lockfile 与 package.json 不一致直接失败
```

### 验证

```bash
node -v      # v24.x
pnpm -v      # 11.22.0
pnpm typecheck && pnpm test
pnpm dev     # http://127.0.0.1:5190（strictPort，端口被占用会直接退出）
```

打开 `http://127.0.0.1:5190` 能看到小屋（米白底色、程序化绘制的竹竹、五条状态条、底部三个大入口）即环境就绪。

### 常用命令

| 命令 | 作用 |
|------|------|
| `pnpm dev` | Vite 开发服务器 `127.0.0.1:5190`，改 `packages/*` 即时热更新 |
| `pnpm build` | 生产构建，产物 `apps/site/dist`（`base: './'`，可放任意子目录） |
| `pnpm preview` | 预览构建产物 `127.0.0.1:5191` |
| `pnpm test` | Vitest（`environment: 'node'`，不碰 DOM/WebGL） |
| `pnpm content:check` | 任务 JSON + 模板关卡脚本 + 双语完整性校验 |
| `pnpm pack:check` | Tauri/Capacitor 配置体检（不装 Rust/JDK 也能跑） |
| `pnpm size` | 体积预算（读 `dist`，必须先 build） |
| `pnpm verify` | 七阶段总门禁（见下节） |
| `pnpm dist:win` / `pnpm dist:apk` | 桌面 exe / 安卓 apk |

## 核心 API

### 契约层（packages/game-kit/src/contract.ts）

契约文件只有类型与几个常量，没有运行时代码——它必须能被所有包引用而不引入副作用，也必须能在 Node 单测里直接 import。

```ts
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
  content: TaskDetail;          // 已是目标语言的翻译结果，游戏内不存在语言分支
  services: PlatformServices;   // storage / audio / lifecycle / telemetry / now()
  locale: 'zh-CN' | 'en';
  reducedMotion: boolean;
  emit<K extends keyof GameEventMap>(type: K, payload: GameEventMap[K]): void;
  requestExit(): void;
}
```

`PlatformServices` 是唯一的环境出口：场景不许直接 `localStorage` / `fetch` / `Date.now()`。这不是洁癖——时钟可注入，才让「连续 3 天得贴纸」这类规则能在单测里复现。

### 事件协议

一局只允许发五个事件，扩展要先改契约再改调试桥与 e2e：

| 事件 | 触发点 | 外壳拿它做什么 |
|------|--------|---------------|
| `session:start` | 模板 `create()`，紧跟 `scene:enter` | 不处理，进调试桥与遥测 |
| `scene:enter` | 场景创建的第一件事 | 标记进入了哪个场景 |
| `task:retry` | `BaseScene.noteMistake()` | **不改存档**，只做观测 |
| `task:complete` | `BaseScene.finishTask()`，一局唯一收尾 | 写存档、发奖励、弹完成卡 |
| `session:exit` | `BaseScene.exit()`（`complete` / `quit` / `replay`） | `replay` 时原地卸载再挂载 |

「一局只有一个完成信号」是这套契约最硬的约束：模板不许自己拼奖励、不许自己写存档、不许绕过 `finishTask()` 退出。十个玩法的结算路径因此完全一致。

### defineGame()：三段式装配

十个玩法入口加起来不到 250 行，因为共用同一个工厂：

```ts
export interface GameDefinition {
  manifest: GameManifest;
  drawBeat?: (g, index, rect) => void;   // 分幕插图：每条任务自己画
  gameplay: (ctx: GameContext, session: SessionState) => GameplayStage;
}

export function defineGame(definition: GameDefinition): GameModule;
```

`mount()` 内部按「分幕故事 + 玩法场景 + 完成卡」组装场景列表并启动 Phaser。一个真实例子（刷牙，省略 import）：

```ts
export default defineGame({
  manifest,
  drawBeat,
  gameplay: (ctx, session) => ({
    entry: SCENE_KEYS.scrub,
    scenes: [
      createScrubScene(ctx, {
        level: scrubLevel(ctx.content),   // 关卡数据从内容 JSON 取，不写死数字
        session,
        nextSceneKey: SCENE_KEYS.reward,
        titleKey: 'scene.scrub',
        drawWorld: (g, state) => drawBathroom(g, state),
        reveal: ctx.content.extra.reveal,
      }),
    ],
  }),
});
```

### 内容模型（packages/content）

一条任务切成两份 JSON，切分依据是「谁在什么时候读它」：`tasks/<id>.json` 是摘要（首屏同步需要），`details/<id>.game.json` 是详情（含关卡脚本与三句语音文案，进入玩法时异步加载）。

关键设计：主入口**只导出类型** `export type { TaskSummary, TaskDetail }`，不导出 `schema.ts` 的运行时对象——`z.object(...)` 是真实副作用，一旦被主入口引用，zod 就会进入首屏（大约等于首屏三分之一的体积）。需要校验的地方走 `@bamboo/content/full`。

```json
{
  "id": "brush",
  "title": "刷牙",
  "timeSlots": ["morning", "evening"],
  "template": "scrub",
  "durationHintSec": 45,
  "ageRange": [4, 8],
  "unlockLevel": 1,
  "stats": { "clean": 16, "mood": 5 },
  "reward": { "shoots": 2, "xp": 12 },
  "habit": "早晚都要刷牙",
  "diary": "今天帮竹竹刷了牙，牙齿亮晶晶。",
  "tip": "上面、下面、里面，都要刷到哦"
}
```

`id` 这个字符串同时出现在七处（内容 JSON、`TASK_IDS`、registry 键、`games/daily` 的 `exports` 子路径、`manifest.id`、存档键 `save.tasks.brush`、e2e 的 `data-testid`）。前四处有类型关联（`Record<TaskId, ...>` 少一个就编译失败），后三处靠 `content:check` 与 e2e 兜底。

### 八个模板

模板 = 交互原语 + 循环 + 纯逻辑判定（`*.logic.ts`）+ 外置绘制回调。同一模板被多条内容复用时，差异全部由关卡数据承担：

| 模板 | 交互原语 | 判定要点 |
|------|---------|---------|
| `scrub` | 按住工具在目标区来回刷，刷干净后冲水/擦干 | 最近点位 + 半径命中、每点蹭够 `rubs` 次、`finishTaps` 次收尾 |
| `feed` | 把食物拖到嘴边，一口一口吃完 | 每口递减、总口数、`needKinds` 类别均衡 |
| `dress` | 把衣物拖到身上正确部位 | 槽位匹配、全部穿上 |
| `order` | 按顺序完成睡前步骤 | 当前步骤 id，点错不清进度 |
| `tidy` | 按类别把玩具拖进对应箱子 | 类别匹配、全部归位 |
| `rhythm` | 竹竿开合，窗口内点按 | 墙钟三角波、`zone`、连点门 |
| `pick` | 认出情绪再做安慰动作 | 目标情绪、轮次推进 |
| `learn` | 颜色/形状/数字点选 | 答案下标、可无限重试 |

三条贯穿所有模板的行为规则：逐帧重画（游戏包在一个 `drawXxx` 回调里画整个世界）；autoplay 走与真实操作**相同**的内部方法；零失败（放错弹回，不判错、不扣分，只有刻意体验的动作计 `mistakes`）。

### 存档与进度（packages/progress）

```ts
export const SAVE_SCHEMA_VERSION = 3;

export interface SaveData {
  schemaVersion: number;
  updatedAt: number;
  pet: PetState;                       // 13 个字段：xp / stats / shoots / stickers / equipped ...
  tasks: Record<TaskId, TaskProgress>;
  arcade: Record<ArcadeGameId, ArcadeProgress>;
  days: Record<string, DayRecord>;     // 只保留最近 30 天
}
```

- `ProgressStore` 只有 `load()` / `save(data)` 两个方法——换一个存储实现是件小事（现在有 IndexedDB 与内存实现）
- 星星口径写死为正向：失误 ≤1 给 3 颗、≤3 给 2 颗、其余 1 颗，**没有 0 颗**（类型里的 `0` 只是取值域，不是产品口径）
- 成长值四阶段：0 / 60 / 160 / 300；状态跨天才衰减，绝不半天掉状态

## 典型工作流：从零新增一个日常任务

**输入**：一条新习惯（定性、一句话提示、时段、收益、玩法骨架）。**输出**：大厅多一张任务卡、构建产物多一个几 KB 的懒加载 chunk、图鉴可收集。

以下以「整理书包」复用 `tidy` 模板为例。

**步骤 1：写内容摘要 + 详情**

新建 `packages/content/src/tasks/packbag.json` 与 `details/packbag.game.json`，再在 `entries/index.ts` 注册：

```ts
import rawPackbag from './packbag.json';
// 在 entries 数组里追加：
TaskSummarySchema.parse(rawPackbag),
```

**步骤 2：写英文补丁**

新建 `i18n/en/packbag.json`（结构镜像，数组按索引对齐），在 `i18n/index.ts` 的 `patches.en` 注册。面向孩子的关卡文案（如 `orbs[].speak`）同样要翻，漏翻会被 CJK 扫描抓住。

**步骤 3：跑内容校验（内容先立住）**

```bash
pnpm content:check
# · 整理书包 (packbag)
#   · 信史 / 2 幕故事 / 2 道复习题 / 1 段玩法：tidy
```

关卡脚本不合法（光球数与槽位数不一致等）在这一步就会报错——内容通过后再写游戏代码。

**步骤 4：写游戏包 `games/packbag/`**

六个文件：`package.json`（`@bamboo/game-packbag`，`workspace:*` 依赖，`exports` 直连 `src/index.ts`）、`src/manifest.ts`、`src/logic.ts`、`src/art.ts`、`src/index.ts`、`src/logic.test.ts`；然后 `pnpm install` 建立 workspace 链接。

```ts
// src/logic.ts —— 纯逻辑：不碰 Phaser，可以直接单测
export function tidyLevel(content: TaskDetail): TidyLevel {
  return TidyLevelSchema.parse(stageScript(content, 'tidy'));
}
```

**步骤 5：外壳注册两处**

`apps/site/src/registry.ts` 加一行 `packbag: () => import('@bamboo/game-packbag')`；`apps/site/package.json` 加依赖。`registry.test.ts` 会强制「内容目录、注册表、懒加载入口」三方一致。

**步骤 6：补端到端用例**

在 `e2e/` 加一条真实操作通关用例（拖拽坐标直接从内容 JSON 读，不手抄）；双语载入与 autoplay 用例会枚举内容目录，自动覆盖新任务。

**步骤 7：收尾验证**

```bash
pnpm verify      # 七阶段全绿
pnpm e2e         # 真实鼠标操作 + autoplay 都过
pnpm audit:i18n  # 文案/版面有改动时，人工看两种语言下的每个画面
```

## 质量门禁

`pnpm verify` 由 `scripts/verify.mjs` 编排：**六个互不依赖的阶段并行跑，第七个（体积）必须等构建结束**。

| 阶段 | 命令 | 拦下的问题 |
|------|------|-----------|
| typecheck | `vue-tsc --noEmit` | 契约改动漏改调用方、内容形状不符 |
| lint | `eslint . --cache` | 外壳误 import 完整内容；逻辑层用了 `Math.random` / `Date.now` |
| test | `vitest run` | 奖励口径、状态衰减、推荐确定性、模板判定、存档迁移、街机规则 |
| content:check | `tsx packages/templates/src/cli/check-content.ts` | zod schema、关卡语义、时段覆盖、双语漏翻、伤害性文案 |
| pack:check | `node scripts/check-packaging.mjs` | Tauri/Capacitor 配置（`frontendDist`/`webDir`、appId、图标） |
| build | `vite build` | 构建期错误、chunk 命名规则失效 |
| size | `node scripts/check-size.mjs` | 首屏、单 chunk、dist 总量等预算 |

为什么体积必须串行：它读的是构建产物。若与 `build` 并行，可能读到上一轮的 `dist`——那是最坏的一种假绿（旧产物不超标，新产物已经超了）。

六层门禁各自能证明什么、不能证明什么，值得记牢：类型证明形状自洽，不证明手感；单测证明判定，不证明画面；e2e 证明真浏览器里点得通，不证明低端机帧率。**用错误的工具测，比不测更危险。**

## 调试直达：三个 URL 开关

| 参数 | 作用 |
|------|------|
| `autoplay=1` | 场景自己模拟输入，把这一局走完 |
| `instant=1` | 跳过过场、语音等待与完成卡停留（不改判定、不改奖励） |
| `lang=en` | 强制英文（`en` / `en-US` / `zh` / `zh-CN` 都认） |

```text
http://127.0.0.1:5190/#/play/brush?autoplay=1
http://127.0.0.1:5190/?lang=en#/play/feed
http://127.0.0.1:5190/#/play/sleep?autoplay=1&instant=1
```

生产环境里 `?autoplay=1` 默认无效，除非浏览器由自动化驱动（`navigator.webdriver === true`）——否则拿到分享链接就能自动通关刷星，对儿童产品是信任问题。

此外控制台里可以读 `window.__bamboo.events`（事件序列）、`window.__bamboo.save`（当前存档）与 `window.__bamboo.lastError`（最近一次载入失败详情）。

## 最佳实践

1. **Phaser 实例用 `shallowRef` / `markRaw` 持有**：`ref` 会深度代理整个 Phaser 对象图（场景、纹理、WebGL 上下文）。
2. **离场必须 `await unmount()`**（内部 `game.destroy(true)`）；不要套 `<KeepAlive>` / `<Transition>`，否则 canvas 会叠。
3. **逻辑层禁用 `Math.random` 与 `Date.now`**（eslint 强制）：时钟从 `services.now()` 或构造注入。
4. **长按/等待类进度按墙钟计时，不累加帧间隔**：Phaser 低帧率时会钳制 delta，慢手机上「按住 6 秒」会攒不够。
5. **先内容后代码**：JSON 过 `content:check` 再写游戏包，避免边写边改 schema。
6. **三处对账**：内容 JSON / `entries/index.ts` / `registry.ts`（+ apps/site 依赖），`registry.test.ts` 兜底。
7. **屏幕文字按英文长度设限**（`story.text ≤ 90 字符`），长内容交给 `narration` 走 TTS。
8. **不要手删 `node_modules/.pnpm`**：里面是真实文件，各包只有符号链接；清理后重装往往比修复更快。

## 常见问题

| 问题 | 原因与解决 |
|------|-----------|
| `pnpm install` 报找不到 workspace 依赖 / `workspace:*` 无法解析 | 用错包管理器：删 `node_modules` 后用 pnpm 重装，全仓统一 pnpm |
| `vue-tsc` 报 `ERR_PACKAGE_PATH_NOT_EXPORTED: './lib/tsc'` | TypeScript 被升到 7.x 了；仓库刻意锁 `~5.9.3`（vue-tsc 依赖该子路径），恢复锁定版本，勿 `pnpm add typescript@latest` |
| 端口 5190 被占用 | `strictPort: true` 会直接退出；停掉占用进程（改端口需同步 e2e baseURL，更推荐前者） |
| `pnpm e2e` 报没找到浏览器 | 先 `pnpm exec playwright install chromium`（CI 用 `--with-deps chromium`） |
| `pnpm size` 报 `ENOENT ... apps/site/dist/index.html` | size 读构建产物，先 `pnpm build`；`pnpm verify` 内部顺序已排好 |
| `pnpm dist:apk` 报 `Unsupported class file major version 69` | JDK 25 超出 Gradle 8.14 支持范围；装 JDK 17–24（Temurin 21 即可），或用 `BAMBOO_JDK` 指定 JDK 目录（`scripts/build-apk.mjs` 会按此顺序找 JDK） |
| 首屏出现了 `vendor-phaser` chunk | 有代码静态 import 了 Phaser；检查外壳是否 import 了 `@bamboo/templates`（外壳依赖里不该有它） |
| 游戏打不开，界面只有一句「这个任务暂时打不开」 | 技术详情在 `window.__bamboo.lastError` 与控制台；多为内容/关卡校验失败，跑 `pnpm content:check` 定位 |
| 进度会丢吗 | 本机 IndexedDB（无账号、不同步）；刷新/重开都在，清浏览器数据或换设备会丢；云存档只需替换 `ProgressStore` 实现 |

## AI 使用建议

- **执行环境**：用 `pnpm`（根 `package.json` 的 `packageManager` 锁版本）与 Node.js 24；命令在终端 / shell 中执行（Windows 用 PowerShell）。
- **先探测版本**：`pnpm -v`、`node -v` 与仓库 `package.json` 比对；玩法包与外壳各自是独立 workspace 包，新增依赖要写进对应包的 `package.json`。
- **验证产物**：改完跑 `pnpm verify`（类型 / 单测 / 内容校验 / 打包体积四道门禁），再 `pnpm dev` 打开页面确认任务可玩；类型检查通过不代表玩法正确，`window.__bamboo` 调试桥可用于快速跳任务。
- **常见误操**：任务 JSON 由 zod 校验，字段缺失可能静默不回显，改内容后先看 verify 的内容阶段；长任务放后台运行并落盘日志。
- **安全与权限**：新增依赖、改 `packageManager` 版本、执行 `pnpm install` 前先征得用户同意；打包产物与 `node_modules` 不要提交。

---

## 相关技能

- **chags** — 同一作者的姐妹项目：印证同一套「内容与代码分离 + 模板库」结构能撑起几十个小游戏：[../chags/SKILL.md](../chags/SKILL.md)
- **vue3-map-dashboard** — Vue 3 + Vite + TypeScript 前端工程（外壳侧的技术栈对照）：[../../demos/vue3-map-dashboard/SKILL.md](../../demos/vue3-map-dashboard/SKILL.md)
- **photo-sphere-viewer** — 同为 TypeScript + Vite 构建的浏览器 WebGL 应用（打包与体积门禁思路可复用）：[../../3d/photo-sphere-viewer/SKILL.md](../../3d/photo-sphere-viewer/SKILL.md)
- **docker-compose** — 静态站点的容器化部署方式：[../docker-compose/SKILL.md](../docker-compose/SKILL.md)

## 参考资源

- 仓库：<https://github.com/znlgis/BambooBuddy>
- 在线试玩：<https://znlgis.github.io/bamboobuddy/>
- 17 章中文教程：<https://znlgis.github.io/others/BambooBuddy/>
- Phaser：<https://phaser.io/> ｜ Vue：<https://vuejs.org/> ｜ Pinia：<https://pinia.vuejs.org/>
- Vitest：<https://vitest.dev/> ｜ Playwright：<https://playwright.dev/>
- Tauri：<https://tauri.app/> ｜ Capacitor：<https://capacitorjs.com/>
---
name: mathmindforge
description: "Use when building or extending Math Mind Forge (MathMindForge), a pnpm-workspace math-thinking quest game: Vue 3.5 shell plus trimmed Phaser 4.2 canvas, the LevelModule/LevelRuntime action-dispatch contract, six templates over 20 levels, zod content split into static summary plus lazy level detail, the answerComplete auto-judge contract, IndexedDB saves with evidence and badges, and Vitest/Playwright gates. Also for pnpm verify failures and Phaser leaking into the first-screen chunk."
license: MIT
metadata:
  category: others
  tags: "vue, typescript, phaser, game, education, pnpm, vite, vitest, zod"
---

> **项目地址：** <https://github.com/znlgis/mathmindforge>
>
> **在线试玩：** <https://znlgis.github.io/mathmindforge/>
>
> **官方文档：** 20 章中文教程：<https://znlgis.github.io/others/MathMindForge/>
>
> **包管理器：** pnpm 11.22.0（根 `package.json` 的 `packageManager` 字段锁版本）+ Node.js 24（截至 2026-11）
>
> **最新版本：** v1.0.0-rc.1（仓库 README 与 `docs/09-发布检查清单.md` 标注的当前状态，截至 2026-11；仓库尚无 Release tag，根 `package.json` 仍为 0.1.0）
>
> **许可证：** MIT

## 概述

数思工坊（Math Mind Forge）是面向 5–18 岁的数学思维闯关场。它不是题库：每关要求玩家在画布或面板上把**结构、规则、模型或论证**直接摆出来，填完自动判题，答对自动进下一关，答错在关卡顶部直说错在哪。通关条件不是「猜对选项」，而是「工具产物通过校验 + 约束被满足 + 证据链完整」。

技术上它是「Phaser 管画布 + Vue 管外壳」的双栈，pnpm workspace 分三层：`apps/*`（壳）、`packages/*`（库）、`games/*`（玩法包）。技术栈以仓库 `package.json` 实测为准：Vue 3.5.44 + Pinia 4.0.3 + Vite 8.3.4 + TypeScript 5.9.3 + Phaser 4.2.1（裁剪版）+ Vitest 5.0.4 + Playwright 1.64.0。

核心特征：

- **动作驱动**：所有交互折叠成 `LevelAction`，由纯 `LevelRuntime` 处理；画布与作答面板只是两个视图，读同一份 `RunSnapshot`
- **逻辑与渲染分离**：判定/求解包不 import Phaser / Vue / DOM，因此 20 关的判定能在 Node 里跑，审计脚本才可能存在
- **平台出口唯一**：存储、音频、语音、文件、生命周期一律经 `PlatformServices`，业务代码里出现 `localStorage` / `fetch` / `indexedDB` 视为 bug
- **内容驱动**：一关 = 摘要 JSON（静态，进首屏）+ 详情 JSON（动态，按关切 chunk），换关卡不改代码
- **自动判题**：`answerComplete` 快照布尔量决定何时判题，玩家侧没有「提交」按钮；autoplay 与真实点击走同一条动作路径
- **可测**：单测在 Node 环境跑纯逻辑，真实点击与自动过关交给 Playwright

## 环境准备

### 前置条件

| 依赖 | 版本 | 何时需要 |
|------|------|---------|
| Node.js | 24 | 必需；仓库没有 `.nvmrc` 也没有 `engines`，基线写在文档与 CI 里 |
| pnpm | 11.22.0 | 必需，由 `packageManager` 字段锁定，Corepack 自动校验 |
| Chromium | Playwright 1.64 自带 | 仅跑 `pnpm e2e` 时需要 |
| Rust 工具链 | — | 仅 Tauri 桌面壳；仓库当前尚未创建 `apps/desktop` |
| Android SDK | — | 仅 Capacitor 安卓壳；仓库当前尚未创建 `apps/mobile` |

### 安装与启动

```bash
git clone https://github.com/znlgis/mathmindforge.git
cd mathmindforge
pnpm install          # 按 pnpm-lock.yaml 安装；Corepack 会自动切到 11.22.0
pnpm dev              # http://127.0.0.1:5192
pnpm build            # 产物 apps/site/dist（base: './'，可放任意子目录）
pnpm preview          # http://127.0.0.1:5193
```

`apps/site/vite.config.ts` 里 `strictPort: true`，端口被占时**直接报错**而不是悄悄换端口——Playwright 的 `webServer` 会探测 5192，端口漂移可能让它连上残留服务、测出一份过期的绿。

### 验证安装

```bash
node -v                      # v24.x
pnpm -v                      # 11.22.0
pnpm typecheck && pnpm test  # 纯逻辑单测，不碰 DOM/WebGL
```

12 个 workspace 包的 `exports` 全部指向 `.ts` 源码，**没有 `build` 脚本、没有 `dist`**。所以 `ls packages/templates` 只应看到 `src` 与 `package.json`；改 `packages/` 任意一行刷新浏览器即生效，不需要「先构建库」。

### 常用命令

| 命令 | 作用 |
|------|------|
| `pnpm dev` / `pnpm preview` | 开发服务器 5192 / 生产产物预览 5193 |
| `pnpm typecheck` | `vue-tsc --noEmit`，跨 12 个包 |
| `pnpm lint` | ESLint 10（含「纯逻辑层禁 Phaser/Vue/Math.random/Date.now」规则） |
| `pnpm test` | Vitest 5，Node 环境 |
| `pnpm content:check` | 内容体检：zod schema、双语完整性、禁词分级 |
| `pnpm audit:levels` | 反刷题审计 A1/A1b/A2–A6/A8/A11 + autoplay 走通 |
| `pnpm pack:check` | 打包体检（不装 Rust/JDK 也能跑） |
| `pnpm size` | 体积门禁（读 `dist`，必须先 build） |
| `pnpm verify` | 总门禁：typecheck / lint / 单测 / content:check / audit:levels / pack:check / build / size |
| `pnpm e2e` / `pnpm e2e:dist` | Playwright（开发服务器 / 生产产物两套配置） |

## 核心 API 与契约

### 五个契约文件（packages/game-kit）

`@mmf/game-kit` 不写业务，只定义外壳、关卡模块、模板运行时与审计脚本之间必须共同遵守的形状：

| 文件 | 定义什么 |
|------|---------|
| `ids.ts` | 一行 re-export `@mmf/content/ids`，避免 id 常量出现两份事实 |
| `runtime.ts` | `LevelManifest` / `LevelContext` / `LevelModule` / `LevelRuntime` / `LevelAction` / `RunSnapshot` / `Verdict` |
| `events.ts` | `LevelEventMap` 与 `DebugOptions` |
| `save.ts` | `SaveData` / `LevelProgress` / `EvidenceDraft` / `EvidenceEvent` / `ArtifactSummary` |
| `services.ts` | `PlatformServices` 与它包含的七个能力接口 |

关卡模块的契约只有五个成员：

```ts
export interface LevelModule {
  manifest: LevelManifest;
  createRuntime(detail: LevelDetail, opts: RuntimeOptions): LevelRuntime;
  mount(ctx: LevelContext, runtime: LevelRuntime): Promise<void>;
  unmount(): Promise<void>;
  pause(): void;
  resume(): void;
}
```

关键决定是 **`createRuntime` 在渲染之前就能拿到完整运行时**：外壳可以先建 runtime、再渲染作答面板（`AnswerDock` 只需要 `runtime`、`detail` 与 `detail.tools`）、最后才 `mount` 画布。无画布关卡的 chunk 里因此可以完全没有 Phaser。

### 运行时：dispatch 是唯一写入口

```ts
export interface LevelRuntime {
  readonly detail: LevelDetail;
  snapshot(): RunSnapshot;
  subscribe(listener: (snapshot: RunSnapshot) => void): () => void;
  dispatch(action: LevelAction): Promise<ActionResult>;
  /** 自动通关：内部仍逐条 dispatch，不允许直接改状态 */
  autoplay(): Promise<ActionResult>;
  reset(): Promise<void>;
}
```

`ActionResult` 把「运行时拒绝了动作」与「判定没通过」分开：`ok: false` 表示动作本身不合法（`message` 是给人看的短句）；`ok: true` 而 `verdict.passed === false` 是正常流程，不是错误。

动作表集中在 `ActionPayloadMap`，再用映射类型折叠成可辨识联合。**`type` 的前缀就是 `ToolId`**，所以统计「这件工具被用了几次」只需要切前缀：

```ts
export type LevelAction = {
  [K in keyof ActionPayloadMap]: { type: K; payload: ActionPayloadMap[K] };
}[keyof ActionPayloadMap];

export interface ActionPayloadMap {
  'pattern/inspect': { index: number };
  'pattern/setCycle': { cycle: string[]; transform: PatternTransform };
  'construct/place': { piece: PiecePlacementInput };
  'rule/place': { block: ProgramBlock; at: number };
  'knob/set': { key: string; value: number };
  'probe/sample': { n?: number };
  'counter/edit': { patch: CounterPatch };
  'run': Record<string, never>;
  'submit': Record<string, never>;
  'reset': Record<string, never>;
}
```

三条纪律：先加类型、再加处理分支、最后才让 UI 派发；表里只放**已实现**的动作（不要保留「计划中的动作」，否则 `dispatch` 的 `default` 分支会变成垃圾桶）；宿主动作（`run` / `submit` / `reset`）没有前缀，不属于任何工具。

### 判定：Verdict 与三道门

```ts
export interface Verdict {
  passed: boolean;
  stamps: StampId[];
  failure?: FailureReport;
  missingEvidence: EvidenceRequirement[];
  metrics?: Record<string, number>;
  artifacts: ArtifactSummary[];
  /** 迁移门的逐变体结果；没有迁移门的关卡不出现 */
  variantResults?: { id: string; passed: boolean }[];
}
```

`submit` 分支把「三道门」写成代码，**顺序本身就是需求**：

1. 一件产物都没有：返回 `missingEvidence`（审计 A1 要求无工具提交必须被拒且带缺失证据）；
2. 有产物：先跑结构校验。真实错误必须优先于缺步骤提示，否则写好的失败反馈会被 `missingEvidence` 顶掉；
3. 结构正确但证据步骤没走完：仍按缺失证据处理（守住 A8）；
4. 通过后跑迁移门：逐个变体验一遍，失败时 `failure.class` 取模板声明的迁移失败类，并带 `variantId`。

`FailureReport` 让失败可指向具体位置，而不是一句「错了」：

```ts
export interface FailureCause {
  kind: 'cell' | 'step' | 'constraint' | 'variant' | 'claim' | 'sample';
  ref: string;
  messageKey: string;
  params?: Record<string, string | number>;
}

export interface FailureReport {
  class: string;
  variantId?: string;
  causes: FailureCause[];
}
```

### 平台出口（packages/game-kit/src/services.ts）

```ts
export interface PlatformServices {
  storage: ProgressStore;
  evidenceStore: EvidenceStore;
  audio: AudioBus;
  files: FileBus;
  preferences: Preferences;
  lifecycle: LifecycleBus;
  telemetry: Telemetry;
  now(): number;
}
```

`now()` 可注入，才让「连续几天」这类规则能在单测里复现。存档形状由 `SAVE_SCHEMA_VERSION`（当前为 1）与 `SaveData` 定义，运行时只产出 `EvidenceDraft`，`id` / `profileId` / `at` 由外壳补齐后成为 `EvidenceEvent`。

### 内容模型：摘要 + 详情两半

| | 摘要 `levels/<id>.json` | 详情 `details/<id>.level.json` |
|---|---|---|
| 谁需要 | 大厅、星图、推荐逻辑 | 进入关卡之后 |
| 典型字段 | `title` / `emoji` / `band` / `thread` / `tools` / `difficulty` / `unlock` | `levelScript` / `tools` / `evidencePlan` / `solutions` / `negativeSamples` / `variants` / `feedback` |
| 体积 | 一关约 0.5–1 KB | 一关约 5–15 KB（含 2 解 + 3 负例 + 2 变体） |
| 加载 | 静态 import，随内容包进首屏 | 动态 import，按关切 chunk |

`packages/content/src/schema.ts` 用 zod 4 写成，第一原则是 `.strict()`：未知字段直接报错而不是被静默剥掉——写错字段名（例如 `thinking_target`）时，静默剥掉会变成「字段没生效但校验通过」。摘要的几条硬上限：`title` ≤ 24 字、`thinkingTarget` ≤ 40 字、`estimatedMinutes` 3–15、难度四轴各 1–5。

运行时**不跑 zod**（否则 zod 会进首屏），只做 id 一致性断言：

```ts
export async function loadLevel(id: ShippedLevelId): Promise<LevelDetail | null> {
  const summary = getLevelSummary(id);
  if (!summary) return null;              // 未发布 / 未知 id 的正常路径，调用方回星图
  const loader = LOADERS[id];
  if (!loader) return null;
  const raw = await loader();
  const detail = (raw && typeof raw === 'object' && 'default' in raw ? raw.default : raw) as LevelDetail | null;
  if (!detail) throw new Error('关卡详情为空：' + id);
  if (detail.id !== id) throw new Error('关卡详情 id 不一致：' + id);
  return detail;
}
```

### 六个模板与六件工具

工具（`TOOL_IDS`）是作答原语，模板（`TEMPLATE_IDS`）决定画布与判定，两者多对多：

| 模板 | 画布 | 默认工具 | 判定核心 |
|------|------|---------|---------|
| `pattern` | 序列带 / 墙 / 积木路 | pattern + construct | 规则补全 + 换表征迁移 |
| `rule` | 网格地图 | rule + counter | 程序执行 + 变体泛化 |
| `construct` | 网格 / 等距板 / 表格图 | construct + counter | 约束满足 + 多解 + 不可能证书 |
| `simulate` | 简化城镇 / 队列 | knob + probe | 预算内指标 + 换种子稳健 |
| `experiment` | 对局 / 数据面板（可无画布） | probe（可按关加 knob / construct / rule） | 大样本比例 + 证据充分 |
| `argue` | 结构 / 图表（可无画布） | counter + probe + 论证板 | 证书可检验 + 边界解释 |

`packages/templates` 对每个模板都导出三个子路径（`./<t>`、`./<t>.logic`、`./<t>.runtime`）加统一的 `./verifiers`，纯逻辑与运行时分开导出，是为了让审计脚本只 import logic 而不把 Phaser 拖进来。

常量层 `packages/content/src/ids.ts` 是全部 id 的唯一事实来源，刻意不含 zod、不含内容 JSON：

```ts
export const BANDS = ['k', 'g13', 'g46', 'g79', 'g1012'] as const;
export const THREADS = ['structure', 'algorithm', 'modeling', 'data'] as const;
export const TOOL_IDS = ['pattern', 'rule', 'construct', 'knob', 'probe', 'counter'] as const;
export const TEMPLATE_IDS = ['pattern', 'rule', 'construct', 'simulate', 'experiment', 'argue'] as const;
export const STAMP_IDS = ['constraint', 'simple', 'transfer', 'argument'] as const;
export const EVIDENCE_PHASES = [
  'observe', 'hypothesize', 'construct', 'run', 'result', 'revise', 'generalize', 'argue',
] as const;
```

两套关卡 id 的语义不同，新增关卡要**同时**加进两个数组：`LEVEL_IDS` 是 5 学段 × 4 主线的目标矩阵（内容 schema 用它做 `z.enum`），`SHIPPED_LEVEL_IDS` 是本次发布包含哪些关（星图、注册表、单测、e2e、内容体检都以它为准）。

## 典型工作流

### 工作流一：跑通门禁再改代码

```bash
pnpm install
pnpm verify        # typecheck / lint / 单测 / 内容体检 / 关卡审计 / 打包体检 / build / size
pnpm e2e           # 20 关 autoplay + 20 关真实点击 + 无工具卡 + 错误原因直出 + 断网
```

改完 `packages/toolkit` 或模板逻辑后，先 `pnpm test`（秒级），再 `pnpm audit:levels`（验证 20 关判定仍自洽），最后 `pnpm verify`。**只跑 `pnpm dev` 看过界面不算验证**：生产构建会注入 CSP（`connect-src 'none'`），dev 不注入（否则 HMR 的 `ws://` 会被掐断），所以 `pnpm e2e` 绿不代表 `pnpm e2e:dist` 绿。

### 工作流二：新增一关（九处登记点）

从空文件到 `pnpm verify` 全绿，按「内容 → 代码 → 外壳 → 测试」的顺序动：

| # | 登记点 | 文件 |
|---|--------|------|
| 1 | 关卡 id | `packages/content/src/ids.ts`（`LEVEL_IDS` 与 `SHIPPED_LEVEL_IDS` 都要加） |
| 2 | 摘要 | `packages/content/src/levels/<id>.json` + `summaries.ts` 的 `RAW` 表 |
| 3 | 详情 | `packages/content/src/details/<id>.level.json` + `loadLevel.ts` 的 `LOADERS` + `full.ts` 的 `LEVEL_DETAILS` |
| 4 | 关卡模块 | `games/forge/src/levels/<id>.ts` + `games/forge/package.json` 的子路径导出 |
| 5 | 外壳注册表 | `apps/site/src/registry.ts` |
| 6 | 门禁 | `content:check` / `audit:levels` / 单测 / `e2e` |

加完 id 先跑 `pnpm typecheck`：`Record<ShippedLevelId, ...>` 会一次性把所有必须同步登记的表点出来。**不要改 `games/forge/src/index.ts`**，它只有一个 `export {}`，一句 `export * from './levels/...'` 就会让 20 关连同 Phaser 场景进同一个 chunk，首屏预算与「外壳不 import Phaser」同时失守。

### 工作流三：接入一个新模板或新工具

1. 在 `packages/content/src/ids.ts` 扩 `TOOL_IDS` / `TEMPLATE_IDS`；
2. 在 `packages/game-kit/src/runtime.ts` 的 `ActionPayloadMap` 加动作类型，**前缀必须是工具 id**；
3. 在 `packages/templates/src/<t>/` 写 `schema.ts` / `logic.ts` / `runtime.ts` / `scene.ts`，纯逻辑放 `logic.ts`；
4. 在 `packages/templates/src/verifiers.ts` 注册 verifier；
5. 在 `packages/toolkit-ui` 给 `AnswerDock` 加面板（按 `detail.tools` 挑渲染）；
6. 补 `negativeSamples` 与 `solutions`，让 `audit:levels` 的 A3（至少 2 条有效解）与 A4（负例触发声明的失败类）能过。

### 工作流四：定位「答完不判题」

`answerComplete` 是宿主判题的唯一触发条件。autoplay 通关但 `answerComplete` 仍为 `false`，玩家填完答案也不会判题——审计 A11 拦的正是这条。排查顺序：`snapshot().answerComplete` 是否被模板置真 → `subscribe` 的监听是否挂上 → 关卡是否走了自己的「点完成」分支（那等于绕过统一路径）。

## 常见问题

| 现象 | 原因 | 处置 |
|------|------|------|
| `Port 5192 is already in use` | 上一次 `pnpm dev` 没关干净，`strictPort` 拒绝漂移 | 杀掉占用进程，**不要改端口**（e2e 的 `webServer` 探的是 5192） |
| `Cannot find module '@mmf/xxx'` | 在单个包里 `pnpm install`，或没在仓库根装 | 回到仓库根执行 `pnpm install`，不要在子包里装 |
| 页面白屏但 dev 终端无报错 | 浏览器缓存了旧模块 | 硬刷新 `Ctrl+Shift+R` |
| `缺少关卡摘要：<id>` / `关卡摘要 id 不一致：<id>` | `summaries.ts` 的 `RAW` 少登记，或 JSON 的 `id` 与文件名不一致 | 补 `RAW` 一行；改 JSON 的 `id` 使其与文件名一致 |
| `关卡详情为空：<id>` / `关卡详情 id 不一致：<id>` | `loadLevel.ts` 的 `LOADERS` 缺项，或 `details/*.level.json` 的 `id` 错位 | 补 `LOADERS`；`detail.id` 必须等于 `ShippedLevelId` |
| `关卡没有登记：<id>` | `apps/site/src/registry.ts` 缺键 | 补注册表；`Record<ShippedLevelId, ...>` 本应在 typecheck 阶段就报 |
| `content:check` 报未知字段 | zod schema 是 `.strict()`，字段名写错不会被静默剥掉 | 按 `packages/content/src/schema.ts` 改名，不要指望运行时兜底 |
| `audit:levels` 报 A1「无工具提交居然通过」 | `submit` 分支先判结构、后判空产物，顺序被改反了 | 恢复顺序：空产物先返回 `missingEvidence`，再跑结构校验 |
| `audit:levels` 报 A11「自动判题不可达」 | autoplay 通关但 `answerComplete` 未置真 | 让模板在产物填满时置 `answerComplete`；不要依赖「点完成」按钮 |
| `pnpm e2e` 绿但 `pnpm e2e:dist` 红 | 生产构建注入 CSP `connect-src 'none'`，dev 不注入 | 以 `e2e:dist` 为准；需要联网的能力走 `PlatformServices`，不要在组件里直接 `fetch` |
| 部署后 `?autoplay=1` 不生效 | `readDebugOptions()` 只在 DEV 或 `navigator.webdriver` 为真时返回选项 | 这是有意设计，防止一条链接跳完全部关卡；自动化请用 Playwright |
| 首屏体积突然变大 | 关卡模块被 re-export 进 `games/forge/src/index.ts`，Phaser 进了首屏 | 恢复 `export {}`；用子路径导出 + 逐条动态 import |
| `pnpm size` 报预算超限 | 改完未重建，或新增内容进了首屏 chunk | 先 `pnpm build` 再 `pnpm size`；把大内容放详情 JSON 走动态 import |

## AI 使用建议

- **先读契约再写代码**：`packages/game-kit/src/runtime.ts` 是判定与交互的唯一形状来源；任何「绕过 `dispatch` 直接改状态」的实现都是错的，autoplay 与真实点击会立刻分叉。
- **改判定只动纯逻辑**：`packages/toolkit`、`packages/evidence`、`packages/progress` 与所有 `*.logic.ts` 不许 import Phaser / Vue / DOM，也不许用 `Math.random` 与 `Date.now`（lint 会拦）。随机要注入种子，时钟要注入 `now`。
- **验证顺序**：`pnpm test`（秒级）→ `pnpm audit:levels`（20 关判定自洽）→ `pnpm verify`（全量门禁）→ `pnpm e2e:dist`（生产产物）。不要只跑 `pnpm dev` 就说「改好了」。
- **不要凭记忆填版本**：依赖版本以根 `package.json`、各包 `package.json` 与 `pnpm-lock.yaml` 为准；本仓库尚无 Release tag，不要给不存在的版本号。
- **内容改动先跑 `content:check`**：它同时校验 zod 形状、双语字段完整性与禁词分级，比在浏览器里手点快得多。
- **失败反馈要结构化**：新增失败分支时补 `FailureReport.class` 与 `causes`，并配一条 `negativeSamples`，否则审计 A4 会红。

## 相关技能

- [bamboobuddy](../bamboobuddy/SKILL.md) — 同一套 pnpm workspace + Vue + Phaser 双栈的同源项目，契约风格与门禁设计可对照阅读
- [chags](../chags/SKILL.md) — 另一个 Phaser 4 + Vue 3 的 H5 游戏合集，可对比「一个玩法包承载多关卡」的包划分
- [docker-compose](../docker-compose/SKILL.md) — 需要把 `apps/site/dist` 部署成静态站时的编排参考

## 参考资源

- 仓库：<https://github.com/znlgis/mathmindforge>
- 在线试玩：<https://znlgis.github.io/mathmindforge/>
- 20 章中文教程：<https://znlgis.github.io/others/MathMindForge/>
- 仓库文档目录（`docs/`）：`00-方案总览`、`01-产品与玩法设计`、`02-技术架构`、`03-关卡设计规格`、`13-自动判定与自动过关`、`14-去卡片化与直接作答`
- 许可证：MIT（Copyright (c) 2026 tj）

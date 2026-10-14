---
name: tongwen
description: "Use when translating engineering CAD drawings between languages — DWG text extraction, glossary-driven translation workspace, QA gating, lossless write-back. Tongwen (同文): local-first CAD/BIM translation suite with an AutoCAD 2019/2021/2025/2026 plugin, a TW_-command set, and a headless BatchCli for pipeline use."
tags:
  - autocad
  - cad
  - dwg
  - translation
  - bim
  - i18n
  - dotnet
  - terminology
  - commercial
  - plugin
---

> **产品定位：** 商业软件（非开源），面向工程图纸的本地优先 CAD/BIM 无损翻译套件
>
> **项目地址：** 不适用（专有商业软件，产品官网详见下方）
>
> **产品官网：** <https://shandianweihu.com/>
>
> **上游文档：** <https://znlgis.github.io/cad/TongWen/>
>
> **许可证：** 专有商业软件
>
> **CAD 平台：** AutoCAD 2019—2026

## 概述

同文（Tongwen）是一套面向工程图纸的 CAD/BIM 无损翻译套件，解决工程建设领域多语言图纸翻译的核心痛点。与传统人工翻译或通用机器翻译不同，同文直接解析 DWG 文件中的文字实体，提供术语库驱动的专业翻译工作流，最终将译文无损回写至原图纸，保持图纸格式、布局和图层信息完全不变。

### 核心能力

| 能力 | 说明 |
|------|------|
| 图纸文字提取 | 从 DWG 提取文字实体（单行/多行文字、块属性、标注等），支持整图或框选 |
| 翻译工作区 | Studio 内分屏对照，原文/译文并排编辑，风险实时展示 |
| 翻译知识体系 | CM 校正记忆 > TM 翻译记忆 > Glossary 术语表 > LLM 四层优先级级联 |
| 术语库管理 | 以 CSV 为载体的全局/项目术语表，可用 Excel 编辑，支持多表按序加载 |
| 图纸回写 | 译文回写 DWG，策略三选一：新建译文图层 / 覆盖原文 / 双语对照 |
| 质量检查 | 占位符、术语、长度溢出三类验证器，四级风险分级；阻断级会阻止回写 |
| AutoCAD 插件 | 22 个 `TW_` 前缀命令，在 CAD 环境内完成提取—翻译—回写 |
| 批量处理 | `Tongwen.Runner.BatchCli` 无头递归批处理，另有 Review 报告与 Server 接口 |
| 本地优先 | 项目数据、术语表、翻译记忆均本地存储（SQLite / 本地文件） |

### 版本支持

同文按 AutoCAD 的插件框架分别出包，官方文档明确列出的是**四档**（不是连续区间）：

| AutoCAD 版本 | 插件框架 |
|--------------|----------|
| AutoCAD 2019 | .NET Framework 4.7+ |
| AutoCAD 2021 | .NET 6.0 |
| AutoCAD 2025 | .NET 8.0 |
| AutoCAD 2026 | .NET 8.0 |

装其中任一即可；同时装多版时启动器会自动检测并让用户选择启动哪个。**AutoCAD LT 完全不支持**——核心功能依赖完整 .NET API，LT 不提供。

---

## 环境准备

### 前置条件

| 项 | 要求 |
|----|------|
| 操作系统 | 仅 64 位 Windows：Win10 版本 1809（Build 17763）及以上、Win11 21H2 及以上；不支持 Win7/8/8.1、32 位系统，无 macOS/Linux 原生版 |
| CAD | 上表任一受支持 AutoCAD（非 LT） |
| 运行时 | AutoCAD 2019 插件需 .NET Framework 4.7.2+；2021 插件需 .NET 6.0 桌面运行时；2025/2026 插件与 Studio 主程序需 .NET 8.0 桌面运行时 |
| 权限 | 本地管理员权限（企业受控机器可能需 IT 协助） |

### 检查与安装

```powershell
# 1. 确认系统版本与位数
winver

# 2. 确认桌面运行时是否齐备（要同时看到 WindowsDesktop.App 条目）
dotnet --list-runtimes

# 3. 确认 .NET Framework 4.7.2+：Release ≥ 461808
reg query "HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" /v Release

# 4. 下载并校验安装包（官网下载页 → Tongwen_Setup_vX.X.X.msi）
Get-FileHash -Path ".\Tongwen_Setup_vX.X.X.msi" -Algorithm SHA256
```

缺 .NET 6.0 / 8.0 桌面运行时时从微软官网下载 "Windows → Desktop Runtime → x64"，两者安装顺序不限。安装为 WixSharp 构建的 MSI，支持静默安装与日志，便于企业批量部署；安装向导中需接受 EULA，安装完成后再配置 AutoCAD 插件并首次启动验证。

---

## 技术架构

### 技术栈

| 层面 | 技术选型 |
|------|---------|
| 运行时 | .NET Framework 4.7.2（ACAD 2019 插件）/ .NET 6.0（ACAD 2021 插件）/ .NET 8.0（ACAD 2025·2026 插件与 Studio） |
| 语言 | C# |
| UI | WPF + MVVM |
| CAD 互操作 | AutoCAD .NET API（ObjectARX） |
| 翻译引擎 | 支持接入多种 LLM/MT 翻译 API |
| 数据存储 | SQLite（术语库、项目数据库） |
| 文件处理 | DWG 直接读写（RealDWG 兼容层） |

### 核心模块

| 模块 | 功能 |
|------|------|
| Studio 桌面工作台 | 项目管理、文件导入、全局配置 |
| DWG 解析器 | 文字实体提取、样式属性收集、上下文识别 |
| 翻译编辑器 | 分屏对照、术语高亮、搜索替换、批量操作 |
| 术语库引擎 | 项目术语库、全局术语库、模糊匹配、术语验证 |
| 回写引擎 | 文字替换、样式适配、图层保持、属性同步 |
| 质量检查器 | 漏译检测、术语一致性、文字溢出、格式完整性 |
| AutoCAD 插件 | 在 AutoCAD 内部直接调用翻译功能 |
| 命令行工具 | 无头模式批量处理、CI/CD 集成 |

---

## 典型工作流

### 标准翻译流程（7 步）

1. **创建项目** — 在 Studio 桌面工作台新建翻译项目
2. **导入图纸** — 加载待翻译的 DWG 文件
3. **配置术语库** — 选择或创建项目术语库，导入已有术语
4. **提取文字** — 自动提取图纸中所有文字实体
5. **翻译编辑** — 在翻译工作区中翻译（支持机器翻译辅助 + 术语提示）
6. **质量检查** — 运行质量检查工具，修复所有问题
7. **回写图纸** — 将翻译结果写回 DWG，生成目标语言图纸

### AutoCAD 插件工作流（轻量模式）

只翻少数几张图时可直接在 AutoCAD 内完成（插件面板与 Studio 之间是"连接—下发—回传"的关系）：

1. `TW_SHOW_PANEL` 打开/隐藏侧边面板；若 Studio 重启后未自动重连，用 `TW_CONNECT` 手动连接
2. `TW_EXTRACT_ALL` 整图提取，或 `TW_EXTRACT_WINDOW` 框选提取（`TW_EXTRACT` 会先问方式）
3. `TW_TRANSLATE` 触发翻译，`TW_RECEIVE` 拉回 Studio 的译文；也可直接 `TW_WORKSPACE` 进翻译工作台逐条编辑
4. `TW_WRITEBACK_FILE` 把译文回写当前图纸；`TW_REPORT` 出该图状态报告
5. 出问题时 `TW_STATUS` 打印插件状态与全部可用命令，`TW_CHECK_META` 扫描 DWG 的 Xrecord 元数据查关联丢失

### 批量处理工作流（CI 集成）

无头批量由 `Tongwen.Runner.BatchCli.exe` 承担，默认装在
`C:\Program Files\ShandianWeihu\Tongwen\Runners\`（建议把该目录加入 PATH）：

```bash
Tongwen.Runner.BatchCli --help                          # 打印全部参数

# 最小可用：递归扫描目录下所有 .dwg，输出到 {input-dir}\_output
Tongwen.Runner.BatchCli -i "D:\项目\中山医院\暖通图纸"

# 指定输出目录与项目配置
Tongwen.Runner.BatchCli -i "D:\项目\…\暖通图纸" -o "D:\项目\…\暖通图纸_EN" -c "D:\项目\…\config.json"

# 三张并发、单图失败不中断整批
Tongwen.Runner.BatchCli -i "…" -o "…" -c "…\config.json" -m 3 --fail-on-error false
```

| 参数 | 缩写 | 必需 | 默认 | 说明 |
|------|------|------|------|------|
| `--input-dir` | `-i` | 是 | — | 待处理 DWG 目录，递归扫描 `.dwg` |
| `--output-dir` | `-o` | 否 | `{input-dir}\_output` | 译图、QA 报告与日志输出目录 |
| `--config` | `-c` | 否 | 全局默认配置 | JSON 配置：引擎、术语库、回写策略、QA、日志 |
| `--max-concurrent` | `-m` | 否 | `1` | 并发处理图纸数 |
| `--fail-on-error` | — | 否 | `true` | 单图失败是否终止整批 |
| `--resume` | — | 否 | — | 恢复令牌（当前版本预留、未启用） |
| `--help` | `-h` | 否 | — | 帮助 |

配置骨架（建议每项目一份、随项目入库以复现结果）：

```json
{
  "translation": { "engine": "deepseek-v4-fast", "sourceLanguage": "zh-CN", "targetLanguage": "en-US" },
  "glossary": { "enabled": true, "paths": ["C:\\Tongwen\\Glossaries\\建筑.json"] },
  "translationMemory": { "enabled": true, "dbPath": "C:\\Tongwen\\TM\\project_tm.db" },
  "writeBack": { "strategy": "newLayer", "layerSuffix": "_EN", "mergeLayers": [], "preserveOriginal": true },
  "qa": { "enabled": true, "minSeverityToReport": "medium", "exportFormat": ["json", "csv"] },
  "logging": { "level": "info", "retainDays": 30 }
}
```

要点：`engine` 取 `deepseek-v4-fast`（快、省）或 `deepseek-v4-pro`（精、慢）；`glossary.paths` 按顺序加载，冲突条目以后加载者为准；`writeBack.strategy` 三选一——`newLayer`（新建译文图层，配 `layerSuffix`/`preserveOriginal`）、`override`（覆盖原文）、`bilingual`（双语对照）；`qa.minSeverityToReport` 取 `blocker`/`high`/`medium`/`low`。

配套工具：

```bash
# 生成可在浏览器查看的独立审校报告（汇总所有图的翻译质量与 QA 发现）
Tongwen.Runner.Review --input-dir "…\_output" --output-dir "…\_output\review"

# Web API 服务：远程注册批量任务、查询状态、取结果
Tongwen.Server --port 5000
```

---

## 关键命令（AutoCAD 插件）

插件共提供 22 个命令行命令，前缀统一为 `TW_`（`TWLAYERVIS` 例外）。按用途分组：

| 组 | 命令 | 功能 |
|----|------|------|
| 面板 | `TW_SHOW_PANEL` / `TW_WORKSPACE` | 切换侧边面板显隐 / 直接打开翻译工作台 |
| 连接 | `TW_CONNECT` / `TW_DISCONNECT` / `TW_CONNECT_ENV` | 手动连接 Studio / 断开 / 连接指定环境（多实例时） |
| 提取 | `TW_EXTRACT` / `TW_EXTRACT_ALL` / `TW_EXTRACT_WINDOW` | 询问方式后提取 / 整图提取 / 框选提取 |
| 翻译回写 | `TW_TRANSLATE` / `TW_RECEIVE` / `TW_WRITEBACK_FILE` / `TW_WRITEBACK_RECEIVE_ENV` | 触发翻译 / 拉回译文 / 回写当前图 / 接收并回写 |
| 诊断 | `TW_STATUS` / `TW_CHECK_META` | 状态与命令清单 / 扫描 DWG 的 Xrecord 元数据 |
| 报告 | `TW_REPORT` | 当前图纸翻译状态报告 |
| 图层 | `TWLAYERVIS` | 交互式图层可见性控制 |
| 批量测试 | `TW_BATCH_SMOKE_ENV` / `TW_BATCH_RUN_ENV` / `TW_BATCH_VERIFY_ENV` / `TW_CREATE_SMOKE_FIXTURE_ENV` / `TW_CREATE_TEST_FIXTURE_ENV` | 环境冒烟 / 批量运行 / 结果验证 / 两类夹具创建（通常管理员使用） |


---

## 术语库体系

### 术语库与翻译知识体系

同文最核心的设计是**四层翻译来源按优先级级联**，保证最优译文优先命中：

```text
① CM  校正记忆      人工修正结果，精度最高      ← 第 1 层
② TM  翻译记忆      审批通过的积累              ← 第 2 层
③ Glossary 术语表   用户预设的术语              ← 第 3 层
④ LLM 大模型        通用翻译引擎（兜底）        ← 第 4 层
```

**规则：CM > TM > Glossary > LLM**——逐层向下回退，命中即停。

### 术语表载体与管理

| 要点 | 说明 |
|------|------|
| 文件载体 | **CSV** 文件，每条记录含原文、译文、语言对、专业领域、优先级等列（`source_text` / `target_text` 等） |
| 分层 | 全局术语表（企业级、跨项目共享，如"混凝土"→"Concrete"）与项目术语表（项目专属，如"A区地下室"→"Zone A Basement"） |
| 编辑方式 | 界面内表格**只读**；改术语用"用 Excel 打开"按钮调用系统默认表格程序，保存后点"刷新预览"同步 |
| 批量装配 | `glossary.paths` 可给多个 CSV，按顺序加载，冲突条目以后加载者为准 |
| 校验 | 标记为"必须翻译（强制）"的术语若在译文中完全未体现，由 TerminologyValidator 报为高风险 |

---

## 质量检查能力

QA 由三种验证器组成，发现按**四级风险**分级（🚫 阻断 / 🔴 高 / 🟠 中 / 🟡 低），报告可导出 JSON 与 CSV；工作区内实时展示风险，详情面板逐条查阅。

| 验证器 | 检查什么 | 典型发现与等级 |
|--------|----------|----------------|
| `PlaceholderValidator` 占位符验证 | 译文中的格式占位符是否与原文一一对应 | 占位符缺失 / 多余 / 数量同但类型顺序不一致 → 🚫 阻断 |
| `TerminologyValidator` 术语验证 | 术语表约束是否被遵守 | 强制术语未译 → 🔴 高 |
| `LengthOverflowValidator` 长度溢出验证 | 译文预计包围盒相对原文包围盒的溢出比例（按几何估算，不按字符数） | 按溢出程度分档定级 |

**关键安全机制：** 占位符类问题属阻断级，**修复前同文会阻止该翻译单元回写**——面板显示阻断时对应文字不会写入图纸，这是最后一道保障。

回写前后的其它常规核对（图层、块属性、MTEXT 格式码、文件结构完整性）仍需人工抽查，QA 报告不替代图纸会审。

---

## AI 使用建议

- **推荐工作流模式**：按"连接 → 提取 → 翻译 → QA → 回写"五段推进。CAD 内用 `TW_CONNECT`/`TW_EXTRACT_ALL`/`TW_TRANSLATE`/`TW_RECEIVE`/`TW_WRITEBACK_FILE`；成批则改用 `Tongwen.Runner.BatchCli`（`-i/-o/-c/-m/--fail-on-error`）+ 项目 JSON 配置，交付前用 `Tongwen.Runner.Review` 出 HTML 审校页。术语表让 LLM 按 CSV 列（`source_text`/`target_text`/语言对/领域/优先级）批量生成后导入。
- **关键注意事项**：① 译文优先级是 CM > TM > Glossary > LLM，想让术语生效要确认术语表已关联当前项目且未被更高优先级条目覆盖；② 阻断级占位符问题会**阻止回写**，不要试图绕过，先修占位符；③ `writeBack.strategy` 里 `override`（UI 称"原位替换"）会直接改原始 DWG，**回写前必须备份**，要保留原文用 `newLayer` 或合并图层；④ 平台只支持 64 位 Windows 与 AutoCAD 2019/2021/2025/2026，AutoCAD LT 无 .NET API、跑不了；⑤ 数据本地存储，但翻译引擎调用是外网的，离线场景需自备引擎或先用 Mock 引擎跑通流程。
- **常用代码模式**：批量翻译 = `Tongwen.Runner.BatchCli -i <dwg目录> -o <输出> -c <config.json> -m 3 --fail-on-error false`；配置 = `translation.engine` 选 `deepseek-v4-fast`/`deepseek-v4-pro`，`glossary.paths` 顺序加载，`qa.minSeverityToReport` 控报告门槛；服务化 = `Tongwen.Server --port 5000` 走 HTTP 注册任务与查状态。
- **不要臆造**：插件命令一律 `TW_` 前缀（不存在 `TONGWEN_QC`、`TONGWEN_SETTINGS` 之类）；命令行工具是 `Tongwen.Runner.BatchCli`，没有 `TongWen.CLI.exe`；术语表载体只有 CSV。

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 启动 AutoCAD 提示插件加载失败、`NETLOAD` 报错 | 多为插件版本与 CAD 版本不匹配（把 .NET 8 插件装到 2019）或运行时缺失；按版本—运行时对照表核对，必要时以管理员身份运行安装包选"修复" |
| Studio 检测不到 AutoCAD 版本 | 确认装的是受支持版本（2019/2021/2025/2026，非 LT），`ABOUT` 命令可看具体版本 |
| 提取报"Named Pipe 连接失败" | Sidecar/Pipe 服务未随 Studio 启动；重启 Studio 与 Pipe 服务，检查安全软件是否拦截管道通信、管道名是否被占用 |
| 提取不完整（部分文字没进项目） | 图纸含代理实体/自定义对象时须装对应 Object Enabler；图框内文字有单独的提取规则，必要时改框选范围 |
| 术语表配了却不生效 | 检查条目是否保存、是否关联到当前项目、全半角与大小写是否与图纸文字一致、是否被更高优先级术语或全局/项目同名词条覆盖 |
| 回写后原文消失 | 选到了"原位替换（override）"，这是设计行为不是 Bug；保留原文请用 `newLayer` 或合并图层，并养成回写前备份原图的习惯 |
| 回写后字体/样式异常、MTEXT 乱码 | 目标语言字体须系统已装；检查 MTEXT 格式码是否在翻译中被破坏，必要时对该条重新提取再译 |
| 批量处理某张失败拖垮整批 | 加 `--fail-on-error false`；大目录用 `-m` 提并发，但要留意机器与引擎配额 |
| 杀毒软件拦截 DLL | 把安装目录加入白名单后再"修复"安装 |


---

## 相关技能

- **ifoxcad** — AutoCAD .NET 二次开发框架：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)
- **lightningcad** — 建筑围护深化设计插件（同为 AutoCAD 商业插件）：[../lightningcad/SKILL.md](../lightningcad/SKILL.md)
- **fy_layout** — 飞扬平台 LightCAD 场布插件：[../fy_layout/SKILL.md](../fy_layout/SKILL.md)
- **libredwg** — DWG 文件格式读写库：[../libredwg/SKILL.md](../libredwg/SKILL.md)

---

## 参考资源

- [产品官网](https://shandianweihu.com/)
- [同文教程目录](https://znlgis.github.io/cad/TongWen/)
- [AutoCAD .NET API 文档](https://help.autodesk.com/view/ACD/2026/ENU/?guid=GUID-54B4F8B5-1949-4984-ABC3-29BBBF7B4EF1)

---
name: tongwen
description: "Use when translating engineering CAD drawings between languages — DWG text extraction, translation workspace with terminology management, quality-checked write-back. TongWen (同文): local-first CAD/BIM lossless translation suite for AutoCAD 2019-2026."
tags:
  - autocad
  - cad
  - dwg
  - translation
  - bim
  - l10n
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

同文（TongWen）是一套面向工程图纸的 CAD/BIM 无损翻译套件，解决工程建设领域多语言图纸翻译的核心痛点。与传统人工翻译或通用机器翻译不同，同文直接解析 DWG 文件中的文字实体，提供术语库驱动的专业翻译工作流，最终将译文无损回写至原图纸，保持图纸格式、布局和图层信息完全不变。

### 核心能力

| 能力 | 说明 |
|------|------|
| 图纸文字提取 | 从 DWG 文件中智能提取所有文字实体（单行文字、多行文字、属性、标注等） |
| 翻译工作区 | 分屏对照翻译界面，支持原文/译文并排编辑 |
| 术语库管理 | 项目级术语库，确保翻译一致性和专业性 |
| 图纸回写 | 翻译结果无损回写至原 DWG，保留字体、样式、图层、位置 |
| 质量检查 | 自动检测漏译、术语不一致、文字溢出等 8+ 项质量指标 |
| AutoCAD 插件 | 内置 AutoCAD 插件，支持在 CAD 环境中直接操作 |
| 批量处理 | 命令行模式支持多文件批量翻译处理 |
| 本地优先 | 所有数据本地存储，无需联网，保护工程图纸数据安全 |

### 版本支持

- AutoCAD 2019 / 2020 / 2021 / 2022 / 2023 / 2024 / 2025 / 2026

---

## 技术架构

### 技术栈

| 层面 | 技术选型 |
|------|---------|
| 运行时 | .NET Framework 4.8 / .NET 8+ |
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

对于只需翻译少量图纸的场景，可直接在 AutoCAD 内使用插件：

1. `TONGWEN` 命令启动插件面板
2. 选择当前图纸或打开项目
3. 提取文字 → 翻译 → 回写，全程在 AutoCAD 内完成

### 批量处理工作流（CI 集成）

```bash
TongWen.CLI.exe --project "项目路径" --source-dir "源图纸目录" --output-dir "输出目录" --lang en --termbase "术语库路径" --qc-report "qa-report.json"
```

---

## 关键命令（AutoCAD 插件）

| 命令 | 功能 |
|------|------|
| TONGWEN | 启动同文插件主面板 |
| TONGWEN_EXTRACT | 提取当前图纸所有文字 |
| TONGWEN_TRANSLATE | 打开翻译工作区 |
| TONGWEN_WRITEBACK | 将翻译结果回写图纸 |
| TONGWEN_QC | 运行质量检查 |
| TONGWEN_TERMBASE | 管理术语库 |
| TONGWEN_SETTINGS | 打开设置面板 |

---

## 术语库体系

### 术语库分层

| 层级 | 说明 | 示例 |
|------|------|------|
| 全局术语库 | 企业级、跨项目共享 | "混凝土" → "Concrete" |
| 项目术语库 | 项目专属术语 | "A区地下室" → "Zone A Basement" |
| 用户术语库 | 个人偏好术语 | 个人惯用译法 |

### 术语管理特性

- 模糊匹配与智能推荐
- 术语导入/导出（Excel/CSV/TBX）
- 术语冲突检测与合并
- 术语使用统计与一致性报告

---

## 质量检查能力

| 检查项 | 说明 |
|--------|------|
| 漏译检测 | 检测原文存在但译文为空的文字 |
| 术语一致性 | 检查术语库定义的术语是否翻译一致 |
| 文字溢出 | 检测译文长度是否超出原文字框范围 |
| 特殊字符 | 检测译文中的字体是否支持目标语言字符集 |
| 格式完整性 | 验证回写后 DWG 文件结构与原图一致 |
| 图层完整性 | 确认图层信息未因翻译操作丢失 |
| 属性同步 | 验证块属性、标注文字等特殊实体正确翻译 |
| 多行文字格式 | 检查 MTEXT 格式化代码在翻译后是否完整 |

---

## AI 使用建议

- **推荐工作流模式**：AI 助手辅助翻译时应遵循同文标准流程——提取 DWG 文字实体 → 建立项目术语库 → 在翻译工作区编辑 → 运行质量检查 → 回写图纸。批量处理场景使用 `TongWen.CLI.exe` 命令行工具实现 CI/CD 集成，术语库生成可使用 LLM 按同文术语库格式（Excel/CSV）批量生成。
- **关键注意事项**：① 所有数据本地存储，无需联网，保护工程图纸数据安全；② 术语库分三层（全局/项目/用户），确保翻译一致性和专业性；③ 回写图纸保持原 DWG 的字体、样式、图层、位置完全不变；④ 质量检查覆盖 8+ 项指标（漏译、术语一致性、文字溢出、格式完整性等）。
- **常用代码模式**：CLI 批处理：`TongWen.CLI.exe --project "项目路径" --source-dir "源图纸目录" --output-dir "输出目录" --lang en --termbase "术语库路径"`。术语库操作：Excel/CSV/TBX 格式导入导出，模糊匹配与智能推荐。AutoCAD 插件扩展：参考 AutoCAD .NET API 和 ObjectARX 开发规范。

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 图纸文字提取不完整 | 检查图纸中是否有代理实体（Proxy Entity）或自定义对象，确保已安装对应的 Object Enabler |
| 回写后字体显示异常 | 确认目标语言字体已在系统中安装，或使用同文内置字体映射功能 |
| 术语库冲突 | 使用术语库管理面板的"冲突检测"功能合并重复术语 |
| 批量处理卡顿 | 大图纸建议分批次处理，每批次不超过 50 张 |
| 译文文字溢出 | 使用质量检查的"文字溢出"检测项定位问题，调整翻译或在 AutoCAD 中手动调整文字框 |
| 插件加载失败 | 检查 AutoCAD 信任路径配置（TRUSTEDPATHS），确保 .NET Runtime 版本匹配 |

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

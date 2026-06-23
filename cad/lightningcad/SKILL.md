---
name: lightningcad
description: LightningCAD（闪电围护）是面向建筑围护结构深化设计的 AutoCAD/ZWCAD 插件，基于 .NET Framework 4.8 + C# + WPF 开发，涵盖板材排布、节点线、收边、洞口与屋面、图纸校验、CAD 工具包及桌面客户端七大模块，适用于装配式建筑 PC/外墙板/屋面板的施工图深化设计。
tags: [autocad, zwcad, cad, dotnet, wpf, panel-layout, bim, envelope, commercial, plugin]
---

> **产品定位：** 商业软件（非开源），基于 AutoCAD 2019/2020 与 ZWCAD 2022+ 的建筑围护深化设计插件
>
> **上游文档：** <https://znlgis.github.io/cad/LightningCAD/>
>
> **许可证：** 专有商业软件（30 天试用授权，含 SM2 国密加密认证）
>
> **运行时：** .NET Framework 4.8 ｜ **CAD 平台：** AutoCAD R23.0/R23.1、ZWCAD 2022+

## 概述

LightningCAD 是一套面向装配式建筑围护结构深化设计的 CAD 插件系统，核心解决板材（墙板、屋面板、楼承板）的自动排布、节点线生成、收边下料、图纸校验与 BOM 输出等工程痛点。

七大核心模块：

| 模块 | 功能定位 |
|------|---------|
| 板材排布（Panel Layout） | 外墙/内墙/屋面/楼承板板材自动排布、合并、模数归并、碰撞检查、统计表导出 |
| 节点线（Node Lines） | 基于规则映射的自动节点线生成、手动编辑、节点库管理 |
| 收边（Edge Trim / ShouBian） | 块参照实体、均分/定尺分段、批量标注、BOM 导出 |
| 洞口与屋面（Openings & Roof） | 矩形洞口、多边形洞口、屋面坡度定义 |
| 图纸校验与输出（Validation & Output） | 8 项图纸检查 + 3 类出图检查 + 板文调整 |
| CAD 工具包（CAD Kit） | 命令导航、轴网、视口书签、属性面板、快捷键、备份 |
| 桌面客户端（Client） | 注册登录、插件管理、自动更新、系统托盘 |

---

## 技术架构

### 技术栈

| 层面 | 技术选型 |
|------|---------|
| 运行时 | .NET Framework 4.8 |
| 语言 | C# |
| UI | WPF + MVVM（CommunityToolkit.Mvvm） |
| 依赖注入 | Microsoft.Extensions.DependencyInjection |
| 日志 | Serilog |
| 错误监控 | Sentry |
| HTTP | Flurl（强类型 DTO） |
| 加密 | 国密 SM2 |
| UI 主题 | Syncfusion Windows11 |
| 自动更新 | AutoUpdater.NET（阿里云 OSS） |
| 空间分析 | NetTopologySuite（STR-Tree 空间索引） |
| 表格控件 | ReoGrid |
| 安装包 | WixSharp（MSI） |

### 双平台构建

使用条件编译符号为 AutoCAD 和 ZWCAD 编译独立 DLL：

```
AC_2019/    → AutoCAD R23.0 (2019)
AC_2020/    → AutoCAD R23.1 (2020)
ZW_2022/    → ZWCAD 2022+
```

### 自定义 CAD 实体

| 实体类 | 用途 |
|--------|------|
| AecPanel | 墙板/屋面板/楼承板 |
| AecDivisionLineMgd | 节点/分割线 |
| AecRectOpeningMgd | 矩形洞口 |
| AecPolyOpeningMgd | 多边形洞口 |
| AecLayoutBoundaryMgd | 排布边界 |

### 配置体系

JSON 配置文件存储在 `.cfg/Configs/` 目录，支持方案级配置、团队共享与版本间迁移。

---

## 核心命令

### 初始化与板材排布

| 命令 | 功能 |
|------|------|
| FsInitBuilding | 初始化建筑实体 |
| FsPanelLayout（外墙/内墙/屋面/楼承板） | 板材排布 |
| FsMergePanel | 板材合并（锚点长度调整、洞口避让） |
| FsBatchModifyPanel | 批量修改板材属性 |
| FsExportPanelTable | 导出统计表（DWG + Excel） |

### 节点线

| 命令 | 功能 |
|------|------|
| FsCreateNodeLine | 创建节点线 |
| FsEditNodeLine | 编辑节点线 |
| FsNodeLineLibrary | 节点库浏览 |

### 收边

| 命令 | 功能 |
|------|------|
| FsShouBianKuWeiHu | 收边库维护 |
| FsChaRuShouBianTiQuKuang | 插入收边块参照 |
| FsShouBianFenDuan | 收边分段（均分/定尺） |
| FsPiLiangBiaoZhuShouBianXian | 批量标注收边线 |
| FsShouBianBomDaoExcel | 导出收边 BOM |

### 洞口与屋面

| 命令 | 功能 |
|------|------|
| FsCreateWallRectOpening | 创建墙矩形洞口 |
| FsDingYiWuMianDongKou | 定义屋面洞口 |
| FsDingYiLouChengBanDongKou | 定义楼承板洞口 |
| FsDingYiWuMianPoDu | 定义屋面坡度（a/b 格式） |

### 校验与输出

| 命令 | 功能 |
|------|------|
| LTJianChaTuZhi | 图纸校验（8 项检查） |
| LTChuTuJianCha | 出图检查（碰撞/重叠/编号） |
| LTTiaoZhengBanWenZi | 调整板文位置 |

### CAD 工具包

| 命令 | 功能 |
|------|------|
| OperateWizard | 命令导航面板 |
| AxisGrid | 轴网生成（自动/手动） |
| ViewportNavigation | 视口书签与导航 |
| PropertyPalette | 统一属性编辑器 |
| DrawingManage | 图层/文字样式/标注样式管理 |
| ShortcutSettings | 快捷键设置（WH_KEYBOARD_LL 全局钩子） |
| BackupSettings | 备份配置（BeginSave/SaveComplete 触发） |

---

## 典型工作流

### 标准深化设计流程（9 步）

1. **初始化建筑**（FsInitBuilding）— 创建建筑容器实体
2. **配置排布方案** — 设置板材规格、间距、模数等参数
3. **绘制排布边界** — 定义各区域的外轮廓
4. **执行板材排布** — 自动生成板材实体
5. **生成节点线** — 基于规则映射自动创建
6. **创建收边** — 从库中选择并分段
7. **创建洞口**（按需）— 矩形/多边形洞口
8. **图纸校验** — 执行 8+3 项检查
9. **输出统计与 BOM** — 导出 DWG + Excel

### 碰撞检查优化

- 板材数 ≤50：单线程串行
- 板材数 >50：自动切换多线程并行
- 基于 NetTopologySuite STR-Tree 空间索引加速

---

## 桌面客户端

| 功能 | 说明 |
|------|------|
| 注册/登录 | 邮箱注册（SM2 国密加密）、QQ 群 WebView2 登录 |
| CAD 版本检测 | 自动扫描本机 CAD 安装并注册插件 |
| 启动 CAD | 通过 .scr 脚本加载插件 |
| 自动更新 | AutoUpdater.NET + 阿里云 OSS |
| 心跳检测 | 5 分钟间隔，验证授权有效性 |
| 系统托盘 | 后台驻留，快捷操作 |
| 诊断工具 | FsOmTools.exe 独立诊断程序 |

### 自定义 URL 协议

`fsltcad://` — 从浏览器链接启动客户端。

### 日志位置

`%AppData%\FsLt\Logs\`（Serilog 结构化日志）

---

## AI 使用建议

- **生成 CAD .NET 插件代码时**：加载本技能获取自定义实体类名（AecPanel 等）和命令命名规范（Fs/LT 前缀）
- **处理板材碰撞检测**：参考 NetTopologySuite STR-Tree 方案，或直接调用 LTChuTuJianCha
- **自动化批量处理**：可通过 .scr 脚本 + 命令行方式实现无人值守出图
- **配置文件操作**：JSON 格式，存储在 `.cfg/Configs/` 下，可用 `System.Text.Json` 直接读写
- **跨平台编译**：条件编译符号区分 AutoCAD（AC_*）与 ZWCAD（ZW_*）目标

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 插件加载失败 | 检查 CAD 信任路径配置（TRUSTEDPATHS）、.NET Framework 4.8 是否安装 |
| 自定义实体无法显示 | 确保 ObjectARX .NET 包装器已正确注册 |
| 板材碰撞检查过慢 | 板材数 >50 时确认多线程已启用 |
| 客户端无法登录 | 检查网络连接、SM2 加密组件是否正常 |
| 收边 BOM 导出 Excel 失败 | 确认 ReoGrid/NPOI 组件依赖完整 |
| 心跳检测失败 | 授权过期或网络中断，重新登录 |

---

## 相关技能

- **ifoxcad** — AutoCAD .NET 二次开发框架（共享 ObjectARX/.NET 插件开发模式）：[../ifoxcad/SKILL.md](../ifoxcad/SKILL.md)
- **fy_layout** — 飞扬 LightCAD 场布插件示例（另一 CAD 二次开发参考）：[../fy_layout/SKILL.md](../fy_layout/SKILL.md)

---

## 参考资源

- [LightningCAD 教程目录](https://znlgis.github.io/cad/LightningCAD/)
- [AutoCAD .NET API 文档](https://help.autodesk.com/view/ACD/2022/ENU/?guid=GUID-54B4F8B5-1949-4984-ABC3-29BBBF7B4EF1)
- [ZWCAD API 文档](https://www.zwsoft.cn/product/zwcad/developer)
- [NetTopologySuite](https://github.com/NetTopologySuite/NetTopologySuite)
- [CommunityToolkit.Mvvm](https://github.com/CommunityToolkit/dotnet)
- [WixSharp](https://github.com/oleg-shilo/wixsharp)

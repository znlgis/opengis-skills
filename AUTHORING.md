# SKILL 编写规范（AUTHORING）

本文件是本仓库 **唯一权威** 的技能书写规范。新增或修改任何 `SKILL.md`、索引、参考文件前先读本文件；`scripts/validate-skills.py` 会逐条强制检查，CI 不通过则无法合并。

- 规范基线：[Agent Skills 开放规范](https://agentskills.io/specification)（2025-12 起为跨平台开放标准）+ [Anthropic Skill 最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) + [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)。
- 本仓库只使用规范内的**六个合法 frontmatter 字段**，因此技能可原样用于 Claude Code / claude.ai / Skills API / 其他 Agent Skills 客户端，不会因未知字段被拒绝。

---

## 1. 目录与命名

```text
opengis-skills/
├── SKILL.md                       # L1 总索引（name: opengis-skills）
├── <category>/SKILL.md            # L2 分类索引（name 与目录名一致，如 gis）
├── <category>/<project>/SKILL.md  # L3 项目技能（name 与目录名一致）
├── <category>/<project>/reference/*.md   # L3 可选：按需加载的详细参考
└── scripts/、.github/              # 仓库工具，不属于技能
```

- 目录名只能是小写字母、数字、连字符：`^[a-z0-9]+(-[a-z0-9]+)*$`，且与 frontmatter `name` **完全一致**（规范硬性要求）。
- L2 分类固定为 8 个：`3d ai cad csharp demos gis iot others`，`name` 直接用目录名（`gis`，不是 `gis-skills`）。
- L3 目录名用项目常用名的 kebab-case：`gdal`、`photo-sphere-viewer`、`fy-layout`（项目本名 `fy-layout` 只出现在正文里）。
- 参考资料目录统一为 `reference/`（单数）。规范推荐 `references/` 但两者等价，本仓沿用既有目录；每个 `reference/*.md` 必须能从 `SKILL.md` 直接链接（一层深）。

## 2. Frontmatter（六个合法字段）

```yaml
---
name: gdal
description: "Use when processing geospatial raster/vector data via GDAL/OGR CLI — ..."
license: MIT
metadata:
  category: gis
  tags: "gdal, ogr, cli, raster, vector, conversion, reprojection, gis"
---
```

| 字段 | 必填 | 约束 |
|------|------|------|
| `name` | 是 | ≤64 字符；小写字母/数字/连字符；不得以连字符开头或结尾、不得连续连字符；**必须等于父目录名** |
| `description` | 是 | ≤500 字符（规范上限 1024，本仓从严）；英文、以 `Use when` 开头、第三人称；不得含中文、尖括号 `<>` 或 XML 标签；全仓唯一 |
| `license` | 是 | 本仓技能正文一律 `MIT`；上游项目许可证写在正文头部引用块 |
| `metadata.category` | L2/L3 必填 | 顶层分类目录名，必须一致 |
| `metadata.tags` | L2/L3 必填 | 逗号分隔字符串（metadata 的值必须是字符串）；5–10 个；`^[a-z0-9][a-z0-9.-]*$` |
| `compatibility` | 否 | 需要特定环境时才写（≤500 字符） |
| `allowed-tools` | 否 | 本仓技能为纯知识文档，不预授权工具，禁止使用 |

> **为什么没有 `tags` 顶层字段？** 规范只允许上表六个字段，claude.ai 上传与 Skills API 打包遇到未知字段会硬报错（`Unexpected key(s)`）。标签检索统一走 `metadata.tags`，脚本与索引均按此解析。

### description 写法

描述**决定技能是否被选中**，它会被注入系统提示并与其余 100+ 技能竞争：

- 以 `Use when` 开头，写「何时用」而非「这是什么」；项目定位可放句末。
- 放具体触发词：API 名、命令、文件扩展名、常见报错原文（`"not recognized as a supported file format"`）。
- 一个技能只写一个最该被选中的主场景，再补「Also for ...」覆盖排障。
- 禁止：模糊描述（`Helps with documents`）、第一/第二人称（`I can help you ...` / `You can use ...`）、中文、`<>` 尖括号（客户端会转义成 `&lt;`，上传校验也可能判定为 XML 标签）。

好例子：

```yaml
description: "Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction."
```

坏例子：`description: "Helps with PDFs."`

## 3. 正文结构

L3 技能按以下顺序组织（标题措辞可微调，语义必须齐备，校验器按关键词匹配）：

1. **头部引用块**：项目地址、官方文档、**最新版本（含「截至 YYYY-MM」）**、许可证。版本号必须实测上游核对。
2. **概述**：定位 + 能力清单（3–8 条），说明与相邻技术的差异。
3. **环境准备 / 安装**：多平台命令（apt / brew / conda / docker / dotnet / npm / pip 等），装完给一个可自检的版本命令。
4. **核心 API / 命令 / 语法**：按功能分节，示例可直接复制运行；字段、参数用代码格式。
5. **典型工作流**：端到端 2–4 条链路，按「输入 → 命令/代码 → 校验产物」写。
6. **常见问题（FAQ）**：Markdown 表格，**≥5 行**，覆盖报错原文 → 原因 → 处置。
7. **AI 使用建议**（工具无关）：执行环境、版本探测、产物验证、易错操作、安全与权限。不假设 Agent 有特定私有工具。
8. **相关技能**：同类/上下游技能链接（相对路径）。
9. **参考资源**：官方文档、源码、包管理页。

写作要求：中文为主，代码/命令/API 保留英文原文；结论先行；术语全文一致（不要混用「接口/API/端点」）；给出默认方案 + 逃生口（`优先用 X，遇到 Y 改用 Z`），不要罗列一堆等价选项。

## 4. 渐进披露（Progressive Disclosure）

- `SKILL.md` 是**索引 + 高频用法**，不是完整手册：**≤500 行**（超过必须拆分）。
- 详细参数表、完整示例、长清单拆到 `reference/*.md`；`SKILL.md` 里用相对链接说明「何时读它」。
- `reference/` 文件 **>100 行** 时，文件顶部必须加目录（`## Contents` 或 `## 目录` + 条目列表）。
- 引用只允许一层深：`SKILL.md → reference/x.md`；不要在 reference 里再链 reference（`reference` 之间互链仅允许作为同级「延伸阅读」，且每个文件仍必须能从 `SKILL.md` 直接到达）。
- 不允许孤儿文件：`reference/` 下每个 `.md` 都要被 `SKILL.md` 链接。
- 文件引用一律正斜杠：`reference/vector-tools.md`，禁止 `reference\\vector-tools.md`。

## 5. 时效与版本

- 头部必须有可核对的版本信息，推荐写法为 `**最新版本：** X.Y.Z（截至 YYYY-MM，[来源链接]）`；**「截至 YYYY-MM」是硬性要求**，校验器只扫头部 40 行，缺失即报错；包管理器类技能可写成 `**PyPI：** … / **NuGet：** … / **包管理器：** …（版本，截至 YYYY-MM）`，多工具索引型技能可用「涵盖工具」表格逐项列出。版本以 GitHub Releases/tag、PyPI、npm、NuGet、Maven Central **实测**为准，禁止凭记忆填写。
- 不要写会过期的相对表述（`目前最新`、`半年内会支持`、`下个版本将删除`）；旧 API 放 `<details><summary>旧写法（已弃用）</summary>` 折叠块，或直接删除。
- 升级前先跑 `python scripts/check-upstream.py .` 看漂移，再按 `--json` 输出逐项核对。
- 引用外部链接时给稳定地址（官方文档/仓库），不要给会变的搜索结果页。

## 6. 索引与统计

- 新增/删除技能必须同步 4 处：根 `SKILL.md`、所属分类 `<category>/SKILL.md`、`README.md`、`metadata.tags` 索引表。
- 索引中的技能数（`Index of N skills` / `N 个技能` / 分类括号内数字）必须与实际数量一致，校验器会核对。
- 根 `SKILL.md` 的标签索引表要覆盖该标签下的技能；改标签时同步。

## 7. 提交前自检

```bash
python scripts/validate-skills.py .        # 结构/frontmatter/索引/链接，CI 同款
python scripts/check-upstream.py .         # 上游最新版本漂移（需联网）
python scripts/check-links.py .            # 外部链接连通性（可选，需联网）
```

校验器覆盖：六字段白名单、**frontmatter 严格 YAML 合法**（双引号标量内不得出现未转义 `"`）、name 与目录一致、description 全英文且 ≤500 且唯一、无尖括号、metadata 完整、L2/L3 必备章节（含 `## AI 使用建议`）、头部「截至 YYYY-MM」时效标记、FAQ ≥5 行、无 emoji、代码围栏带语言、无 `@@` 占位符残留、≤500 行、reference 目录 TOC/孤儿/一层深、相对链接可达、Windows 反斜杠路径、根标签索引与 `metadata.tags` 一致、索引与 README 覆盖及数量一致。

## 8. 变更流程

1. 改上游版本/API 的依据必须能在 PR 描述里给出链接（release notes / changelog）。
2. 一次 PR 只做一类改动（内容更新 / 规范迁移 / 新增技能），便于审查。
3. 破坏性改动（重命名目录、改 name、删章节）在 PR 描述里列迁移影响。
4. `metadata.tags` 与索引标签表同时改，否则检索会断。

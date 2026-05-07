---
name: superpowers-zh
description: superpowers-zh 是面向中文场景的开源 AI 提示词/能力工程库，提供精心调优的中文提示词、技能（Skill）模板与可复用的 LLM 工作流，覆盖写作、编程、翻译、研究、办公自动化、Agent 等场景，可直接在 ChatGPT/Claude/Cursor/Cline 等客户端使用，也可通过 SDK 嵌入应用。
tags:
  - prompt
  - skill
  - chinese
  - writing
  - coding
  - translation
  - agent
  - workflow
  - llm
  - template
---

> **项目地址：** <https://github.com/znlgis/superpowers-zh>（如位置变动请以 znlgis.github.io 为准）
>
> **许可证：** MIT / Apache-2.0（视仓库声明）

## 概述

superpowers-zh 通常包含：

- **提示词库**：分主题（写作、编码、翻译、研究、教育、运营、PM）
- **Skill 文件**：单文件 Markdown，含 YAML frontmatter（`name` / `description`）+ 系统提示词 + 示例
- **角色 Persona**：行业专家、教师、面试官、产品经理等
- **工作流模板**：多步骤复合提示（拆解 → 执行 → 评审）
- **客户端适配**：ChatGPT 自定义指令、Claude Project、Cursor `.cursor/rules`、Cline `.clinerules`、VSCode Copilot Chat、ima.copilot
- **SDK / CLI**：通过 API 注入 system prompt

---

## 目录结构（典型）

```
superpowers-zh/
├── README.md
├── prompts/
│   ├── writing/
│   ├── coding/
│   ├── translation/
│   ├── research/
│   ├── productivity/
│   └── agent/
├── personas/
├── workflows/
└── tools/
```

每个 Skill 文件示例：

```markdown
---
name: 公文写作-通报
description: 生成机关单位通报体公文，结构标准、用语规范
---

你是一位资深公文写作老师……

## 角色
…

## 输出要求
1. 标题：单位 + 文号 + 关于… 的通报
2. 正文：情况 → 原因 → 决定 → 要求
3. 落款与日期

## 示例
…
```

---

## 在不同客户端中使用

### ChatGPT（自定义指令 / GPTs）

1. 复制目标 Skill 全文 → 粘贴到「Custom Instructions」或 GPT 的 Instructions
2. 创建 GPTs 时关联文件 / Action

### Claude Projects

1. 新建 Project → System Prompt 粘贴 Skill 内容
2. 上传相关知识到 Project Knowledge

### Cursor

```
.cursor/rules/your-skill.mdc
---
description: 公文写作通报
globs: ["**/*.md"]
alwaysApply: false
---
（粘贴 Skill 正文）
```

### Cline / Roo Code

```
.clinerules
（直接粘贴 Skill 内容）
```

### VS Code Copilot Chat

```
.github/copilot-instructions.md
```

---

## SDK 使用（Python 示例）

```python
import openai, pathlib

skill = pathlib.Path("prompts/writing/notice.md").read_text(encoding="utf-8")

resp = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": skill},
        {"role": "user",   "content": "请写一份关于安全生产隐患排查的通报。"}
    ]
)
print(resp.choices[0].message.content)
```

---

## 常用 Skill 类目

| 类目 | 示例 |
|------|------|
| 写作 | 公文、新闻通稿、产品文案、邮件、PPT 大纲 |
| 编程 | 代码审查、单测生成、重构、调试、SQL 调优 |
| 翻译 | 中英互译、技术文档润色、学术论文校对 |
| 研究 | 文献综述、思维导图、对比分析 |
| 办公 | 会议纪要、周报、OKR/KPI、PRD |
| Agent | ReAct、Plan-Execute、深度研究 |

---

## 自己写一个 Skill 的最佳实践

1. **明确角色**：你是谁？面对谁？目标？
2. **定义输出结构**：使用编号 / 表格 / Markdown 段落
3. **给出示例**（few-shot）
4. **设定边界**：不做什么、遇到歧义如何提问
5. **加入「思考再回答」**：仅在需要复杂推理时显式要求
6. **可控变量**：让用户用 `## 输入` 区块给出关键参数
7. **多语言保持一致**：术语表附在末尾

---

## 工作流模板示例（深度研究）

```markdown
---
name: 深度研究-中文
description: 给定主题进行多轮搜索 → 大纲 → 写作 → 审校
---

你是一名资深研究员。请按以下步骤完成研究：

1. **澄清**：列出 3-5 个关键问题
2. **检索计划**：列出 8-10 条搜索查询
3. **检索与摘要**：对每条查询给出关键结论与来源
4. **大纲**：分章节，标明每节要点
5. **正文**：按大纲写作，引用来源（[1][2]）
6. **自评**：列出可能存在的偏差与不确定性

最终输出 Markdown 报告。
```

---

## 性能与质量提升技巧

1. **避免冗长 system**：超过 4k token 后 LLM 注意力下降；将不常用规则放工具层
2. **结构化输入**：要求用户填表 / JSON 输入
3. **结构化输出**（JSON Schema）：便于程序消费
4. **模型选择**：写作用 GPT-4o / Claude Opus；翻译/编程用 Claude Sonnet；翻译润色用 GPT-4o-mini
5. **温度**：写作 0.7-1.0，编程 0.0-0.3，工具调用 0.0
6. **Token 节省**：去掉啰嗦客套语；要点用列表

---

## 与其它项目对比

| 项目 | 主要内容 |
|------|---------|
| superpowers-zh | 中文优化、贴合本土场景的提示词与 Skill |
| awesome-chatgpt-prompts | 英文社区精选 |
| Anthropic Cookbook | Claude 官方示例 |
| LangGPT | 面向编程的提示词框架 |

---

## 典型工作流

### 场景一：用 Skill 辅助公文写作

```markdown
# 1. 选择 Skill 文件 (prompts/writing/notice.md)

# 2. 在 Cursor 中配置
# .cursor/rules/government-notice.mdc
---
description: 公文写作-通报
globs: ["**/*.md"]
alwaysApply: false
---
（粘贴 notice.md 全文）

# 3. 在聊天中引用
用户: @government-notice 写一份关于安全生产隐患排查的通报

# 4. 可搭配 Claude Project
# 新建 Project → System Prompt 粘贴 Skill 内容 → 上传相关知识文档
```

### 场景二：组合工作流做深度研究

```markdown
# 使用 deep-research.md 工作流

用户输入：主题 = "中国新能源汽车出口趋势2025"

步骤 1 - 澄清：列出 5 个关键问题
  ① 2024年出口总量及同比？
  ② 主要出口目的地？
  ③ 品牌分布（比亚迪/特斯拉/蔚来...）？
  ④ 关税/政策影响？
  ⑤ 与日德车企对比？

步骤 2 - 检索计划：10 条搜索查询

步骤 3 - 检索与摘要：每条标注来源 URL

步骤 4 - 大纲：4 章结构

步骤 5 - 正文：含数据引用 [1][2]...

步骤 6 - 自评：列出数据来源偏差与不确定性
```

---

## AI 使用建议

### 推荐工作流

1. **选 Skill**：根据任务类型从 `prompts/` 目录匹配最相关的 Skill
2. **客户端适配**：ChatGPT → Custom Instructions，Cursor → `.cursor/rules/`，Cline → `.clinerules`
3. **组合使用**：复杂任务可将多个 Skill 串成工作流模板（先分析 → 再写作 → 后审校）
4. **迭代优化**：用 Skill 生成初稿后，再对话微调细节
5. **团队共享**：将验证过的 Skill 提交到仓库，全员统一使用

### 关键模式与常见陷阱

- **Prompt 长度控制**：超过 4K token 后 LLM 注意力下降，不常用规则放工具层或外部知识库
- **结构化输出**：要求 JSON Schema 或 Markdown 表格输出时，务必加「严格按以下格式输出」并给出示例
- **温度设置**：写作 0.7-1.0（创意），编程 0.0-0.3（精确），工具调用 0.0
- **避免啰嗦**：system prompt 末尾加「直接给出结果，不要解释自己」
- **模型选择**：中文写作 → GPT-4o / Claude Opus，编程 → Claude Sonnet / DeepSeek-Coder，翻译润色 → GPT-4o-mini

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| 单次任务（写作/翻译） | superpowers-zh Skill + ChatGPT/Claude |
| 持续编程辅助 | Cursor Rules + superpowers-zh coding/ Skill |
| 可视化 AI 应用 | Dify + superpowers-zh 提示词模板 |
| 自动化 Agent | oh-my-openagent / hermes-agent + 提示词注入 |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 模型不遵循格式 | 加「严格按以下格式输出」+ JSON Schema / 结构示例 |
| 输出太啰嗦 | 限定字数或要点数；结尾加「不要解释自己」 |
| 重复套话 | 调高 frequency_penalty / presence_penalty |
| 客户端不读取 rules | 检查路径与文件名，重启客户端 |

---

## 相关技能

- **dify** — 可视化 LLM 应用平台，可将 superpowers-zh 的提示词模板导入 Dify 应用：[../dify/SKILL.md](../dify/SKILL.md)
- **oh-my-openagent** — AI Agent 模板集合，Agent 的 system prompt 可直接使用本库的 Skill：[../oh-my-openagent/SKILL.md](../oh-my-openagent/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/znlgis/superpowers-zh>
- 中文教程（znlgis）：<https://znlgis.github.io/ai/tutorial/superpowers-zh/>
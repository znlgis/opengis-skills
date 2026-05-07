---
name: openclaw
description: OpenClaw 是开源的 AI 编程/操作 Agent，类似 Anthropic Claude Computer Use 与 OpenInterpreter，能在本地控制鼠标键盘、读取屏幕、运行命令、读写文件，并通过 LLM 推理完成端到端的自动化任务，适合 RPA、桌面自动化、研究与教学场景。
tags: llm, agent, automation, rpa, computer-use
---

> **项目地址：** <https://github.com/znlgis/openclaw>（如位置变动请以 znlgis.github.io 为准）
>
> **许可证：** MIT / Apache-2.0（视仓库声明）

> ⚠️ OpenClaw 会执行系统命令、读写文件、控制鼠标键盘，**仅在受信任环境**或**沙箱**中运行；建议使用专用账户或虚拟机。

## 概述

OpenClaw 主要能力：

- **屏幕感知**：屏幕截图 + 多模态 LLM 理解
- **GUI 操作**：鼠标点击/拖拽、键盘输入、滚动
- **文件操作**：读写、创建、移动、压缩
- **Shell 执行**：命令行（白名单/黑名单）
- **Web 浏览**：通过浏览器自动化（Playwright）
- **代码执行**：Python / JS Sandbox
- **多 LLM**：Claude / GPT-4o / Gemini / 通义 / 智谱
- **流式输出 + 事件可观测**

---

## 安装

```bash
git clone https://github.com/znlgis/openclaw
cd openclaw
pip install -r requirements.txt
playwright install chromium    # 浏览器
cp .env.example .env
```

`.env`：

```
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_API_KEY=...
SCREEN_WIDTH=1920
SCREEN_HEIGHT=1080
ALLOW_SHELL=true
SHELL_BLACKLIST=rm -rf /,sudo,format
SANDBOX_MODE=docker
```

---

## 启动方式

```bash
# CLI 交互
python -m openclaw chat

# Web UI
python -m openclaw serve --port 8000

# 一次性任务
python -m openclaw run "打开 Chrome 搜索 GitHub 趋势并截图"
```

---

## 核心工具集

| 工具 | 功能 |
|------|------|
| `screenshot` | 截屏 |
| `mouse_move` / `mouse_click` / `mouse_drag` | 鼠标 |
| `keyboard_type` / `keyboard_hotkey` | 键盘 |
| `read_file` / `write_file` / `list_dir` | 文件 |
| `shell_exec` | 命令行（受策略限制） |
| `python_exec` | Python 沙箱执行 |
| `browser_navigate` / `browser_click` / `browser_extract` | Web |
| `vision_describe` | 多模态描述图像 |

---

## 编排循环（伪代码）

```
LOOP:
  1. screenshot
  2. LLM 看截图 + 历史 + 任务，输出下一步操作（JSON）
  3. 执行工具
  4. 记录结果
  UNTIL LLM 输出 finish 或 max_iter
```

---

## 使用示例

### 1. 桌面自动化

```
任务："打开本地的 demo.xlsx，把 A 列乘以 2 后保存"
```

OpenClaw 会：
1. 截图 → 识别桌面
2. 双击 demo.xlsx 图标
3. 等待 Excel 启动
4. 选中 A 列，输入公式或运行 VBA
5. 保存并关闭

### 2. Web 自动化

```
任务："登录 GitHub，star 'znlgis/opengis-skills' 这个仓库"
```

调用 `browser_*` 工具完成。

### 3. 数据处理

```
任务："读取 ./data/*.csv 合并去重后输出 merged.parquet"
```

调用 `python_exec`：

```python
import pandas as pd, glob
df = pd.concat([pd.read_csv(f) for f in glob.glob("./data/*.csv")])
df.drop_duplicates().to_parquet("merged.parquet")
```

---

## 安全与权限

OpenClaw 默认采用「最小权限」：

- **沙箱模式**：`docker` / `firejail` / `vm`
- **目录白名单**：仅允许读写 `WORKDIR`
- **shell 黑名单**：默认禁止 `rm -rf /`、`sudo`、`format` 等
- **网络白名单**：仅允许配置的域名
- **审计日志**：每条操作记录 + 截图

强烈建议：

1. 配置专用 Linux 用户 / Windows 受限账户
2. 用 Docker / VM 隔离
3. 设置最大步骤数 + 时长上限
4. 启用「人类在环（HITL）」对高风险操作（rm/format/支付）二次确认

```yaml
hitl:
  approve_required:
    - shell:rm
    - shell:sudo
    - browser:submit_form
```

---

## 配置 LLM

```yaml
llm:
  primary:
    provider: anthropic
    model: claude-3-5-sonnet-20241022
    max_tokens: 4096
    vision: true
  fallback:
    provider: openai
    model: gpt-4o-mini
```

国产模型（视觉）可换为 `qwen-vl-max`、`glm-4v`。

---

## 与 Claude Computer Use / Cua 的对比

| 项 | OpenClaw | Claude CU | OpenInterpreter |
|----|----------|-----------|-----------------|
| 开源 | ✅ | ❌ | ✅ |
| GUI 操作 | ✅ | ✅ | 部分 |
| Web 浏览 | ✅ | ✅ | 部分 |
| 沙箱 | docker/vm | API 沙箱 | 本地 |
| 多 LLM | ✅ | 仅 Claude | ✅ |

---

## 性能与最佳实践

1. **截图压缩**：JPEG 80%；分辨率 1280×800 通常够用
2. **关键步骤**：截图 → 操作 → 再截图验证
3. **避免长链**：拆分子任务，逐个验证
4. **失败重试 + 兜底**：图标识别失败回退键盘快捷键
5. **缓存元素位置**：相同 UI 不重复识别
6. **限制屏幕分辨率**与 DPI，提升识别一致性

---

## 典型工作流

### 场景一：自动化数据处理任务

```bash
# 一次性执行
python -m openclaw run "读取 ./data/*.csv 合并去重后输出 merged.parquet"
```

```python
# OpenClaw 会自动调用 python_exec 执行：
import pandas as pd, glob
df = pd.concat([pd.read_csv(f) for f in glob.glob("./data/*.csv")])
df.drop_duplicates().to_parquet("merged.parquet")
```

### 场景二：桌面 GUI 自动化

```bash
# 启动 CLI 交互模式
python -m openclaw chat
```

```
# 对话示例
用户: 打开 Excel，把 Sheet1 的 A 列数据乘以 1.1 后保存

OpenClaw 内部循环:
  1. screenshot → 识别桌面图标
  2. mouse_click → 双击 Excel 图标
  3. screenshot → 等待 Excel 启动
  4. keyboard_hotkey → Ctrl+O 打开文件
  5. keyboard_type → 输入文件路径
  6. ... (选中 A 列 → 输入公式 → 保存)
  7. finish → 任务完成
```

### 场景三：Web 自动化

```bash
python -m openclaw run \
  "登录 GitHub，star 'znlgis/opengis-skills' 仓库，然后截图保存"
```

---

## AI 使用建议

### 推荐工作流

1. **评估风险**：先在 Docker/VM 沙箱中测试，确认无误后再在真实环境运行
2. **拆分子任务**：复杂任务拆成多个短链子任务，逐个验证，避免长链失败
3. **截图验证**：关键步骤后截图确认，不要依赖 LLM 的"记忆"
4. **失败兜底**：图标识别失败时回退键盘快捷键（如 Ctrl+O 代替点击菜单）
5. **限制资源**：设置最大步骤数、时长上限、Shell 黑名单

### 关键模式与常见陷阱

- **沙箱隔离**：务必用 Docker/VM 运行，禁止在宿主机直接执行危险命令
- **HITL（人在环）**：对 `rm`/`sudo`/`format`/支付类操作启用二次确认
- **截图技巧**：JPEG 80% 质量、1280×800 分辨率通常够用；DPI 缩放 100% 避免识别偏差
- **鼠标权限**：Linux 需 X11/Wayland 权限，macOS 需「辅助功能」授权
- **慢操作处理**：减少截图频率、批量操作、提高并发

### 如何选择正确方案

| 场景 | 推荐方案 |
|------|---------|
| GUI 桌面自动化 | openclaw |
| Web 浏览器自动化 | openclaw (Playwright) |
| 纯 API/代码工具调用 | hermes-agent / Dify Agent |
| 可视化工作流编排 | Dify Workflow |
| 代码生成/编程 | Cursor / Cline + superpowers-zh |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 鼠标不动 | Linux 需 X11/Wayland 权限；macOS 需「辅助功能」授权 |
| 模型看不清按钮 | 提高分辨率；放大 UI；用文字定位（通过 OCR） |
| 误删文件 | 启用沙箱 + 文件白名单 + HITL |
| 命令被防火墙拦截 | 配置白名单或放入容器内执行 |
| 执行很慢 | 减少截图次数；批量操作；提高并发 |

---

## 相关技能

- **hermes-agent** — 后端 Agent 框架，适合 API/工具调用为主的场景：[../hermes-agent/SKILL.md](../hermes-agent/SKILL.md)
- **oh-my-openagent** — AI Agent 工程化模板，提供 ReAct/Plan-Execute 等模式的参考实现：[../oh-my-openagent/SKILL.md](../oh-my-openagent/SKILL.md)

---

## 参考资源

- 仓库：<https://github.com/znlgis/openclaw>
- 多模态参考：Anthropic Computer Use 文档
- 中文教程（znlgis）：<https://znlgis.github.io/ai/tutorial/openclaw/>
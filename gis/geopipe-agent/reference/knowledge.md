
# Knowledge & Self-Extension Guide（知识检索与自我扩展）

GeoPipeAgent 把「上游 GIS 语料 + 能力登记表 + 配方」随包分发，作为自我扩展闭环的记忆层（离线可用）。

## 目录

- `src/geopipe_agent/knowledge/catalog.yaml` — 生成物索引：上游 commit、逐文件 sha256、tokens、capabilities（由 `scripts/sync_skills.py` 重生成，勿手改）
- `src/geopipe_agent/knowledge/capabilities.yaml` — 项目自有能力登记表（可写；resolve/scaffold 的记忆层）
- `src/geopipe_agent/knowledge/recipes/<key>.md` — 项目侧配方：怎么在本项目落地该能力
- `src/geopipe_agent/knowledge/upstream/<skill>/` — 上游语料原样同步（只读，手改会被下次同步覆盖）
- `src/geopipe_agent/knowledge/NOTICE.md` — 上游署名（MIT）

知识根优先级：`SkillIndex.load(root)` 参数 > 环境变量 `GEOPIPE_SKILLS_DIR` > 包内目录；根缺失时返回空索引而不抛错（`knowledge doctor` 会给出原因）。

## 命令

| 命令 | 用途 |
|------|------|
| `geopipe-agent knowledge list [--tags crs] [--format json]` | 列出语料技能 |
| `geopipe-agent knowledge search "<关键词>" [--tags crs] [--limit 5]` | 加权检索（name > tags > description > 正文） |
| `geopipe-agent knowledge show <技能> [--section 概述]` | 读取正文（去掉 frontmatter）或单节 |
| `geopipe-agent knowledge doctor` | 自检 frontmatter/引用/implements；有 error 时退出码 1 |
| `geopipe-agent knowledge sync --source <上游 gis 目录> [--skills a,b] [--dry-run]` | 调用 `scripts/sync_skills.py` 同步语料 |
| `geopipe-agent resolve <需求或步骤 ID> [--limit 3]` | 候选能力 + 依赖 + 回退 + 落地建议（JSON） |
| `geopipe-agent scaffold step <category.action> [--capability <key>] [--allow-author]` | 生成步骤骨架，默认 dry-run |

## resolve 输出

```json
{
  "query": "postgis.read_sql",
  "known_step": false,
  "matches": [
    {
      "key": "postgis.sql",
      "kind": "cli",
      "status": "recipe-only",
      "available": false,
      "requires": ["psql 或 ogr2ogr"],
      "fallback": "gdal.ogr2ogr 读写 PG",
      "recipe_path": "recipes/postgis-sql.md"
    }
  ],
  "suggested_actions": ["geopipe-agent describe postgis.read_sql", "..."]
}
```

`known_step: true` 表示该 ID 已是注册步骤，可直接写进 `use:`。

## Python API

```python
from geopipe_agent.knowledge import SkillIndex

index = SkillIndex.load()              # 参数 > GEOPIPE_SKILLS_DIR > 包内目录
index.search("坐标转换", tags=["crs"])  # -> [SkillHit, ...]
index.read("proj", section="概述")      # -> 该节正文
index.resolve("postgis.read_sql")       # -> Resolution(matches, suggested_actions, known_step)
index.doctor()                          # -> ok / errors / warnings / checked
```

## 五步闭环

1. 探测：`geopipe-agent resolve "<需求或未实现的步骤 ID>"`
2. 检索：`geopipe-agent knowledge search "<关键词>"`，或 `geopipe-agent knowledge show <技能> --section 概述`
3. 获得：零代码直通步骤（`gdal.cli` / `qgis.algorithm` / `http.request`），或 `geopipe-agent scaffold step <id> --capability <key>`
4. 验证：`python -m pytest -q` 与 `geopipe-agent validate <pipeline.yaml>`
5. 沉淀：把能力登记进 `capabilities.yaml`（key/title/kind/status/implements/requires/fallback/skills/recipe/commands），并补 `recipes/<key>.md`；之后 `resolve` 会直接命中

写盘安全边界：`scaffold` 默认 dry-run，只有 `--allow-author` 或 `GEOPIPE_ALLOW_AUTHOR=1` 才写盘；已存在文件会被拒绝；只允许写 `src/geopipe_agent/steps/<cat>/<name>.py` 与 `tests/test_steps_<cat>_<name>.py`。

## 相关文档

- [SKILL.md](../SKILL.md) — 主技能文件
- [steps-reference.md](steps-reference.md) — 全部步骤参数
- [backends.md](backends.md) — 后端选择指南

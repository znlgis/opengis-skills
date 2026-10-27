#!/usr/bin/env python3
"""Validate opengis-skills metadata, structure, links and index consistency.

Checks:
  * frontmatter: name / description / tags present, description is English "Use when ..."
  * name matches directory name (L3) or "<category>-skills" (L2)
  * no emoji in L3 skills, no unlabeled code fences, <=500 lines
  * L3 sections: 概述 + 安装/环境准备 + 工作流/使用模式 + FAQ/常见问题 + 相关技能/相关资源
  * FAQ table has >=5 rows
  * relative links resolve inside the repo
  * root/category indexes list every skill exactly once, and link targets exist
  * README lists every skill directory
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

MAX_SKILL_LINES = 500
DESCRIPTION_LIMIT = 500
MIN_FAQ_ROWS = 5

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
INDEX_ROW_RE = re.compile(r"^\|\s*\[[^\]]+\]\(([^)]+)\)")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]")
CJK_RE = re.compile("[\u4e00-\u9fff]")

CATEGORIES = ["3d", "ai", "cad", "csharp", "demos", "gis", "iot", "others"]

# Section keywords: any one of each group satisfies the requirement.
REQUIRED_SECTIONS = {
    "概述": ["概述", "简介"],
    "安装": ["环境准备", "安装", "快速开始", "环境搭建", "部署"],
    "工作流": ["工作流", "使用模式", "实战", "常见用法", "典型场景", "使用流程"],
    "FAQ": ["常见问题", "FAQ", "故障排查", "排错"],
    "相关": ["相关技能", "相关资源", "参考资源", "参考资料", "延伸阅读"],
}


def report(errors: list[str], path: Path | str, message: str) -> None:
    errors.append(f"{str(path).replace(chr(92), '/')}: {message}")


def parse_frontmatter(path: Path, text: str, errors: list[str]) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        report(errors, path, "missing frontmatter opening delimiter")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        report(errors, path, "missing frontmatter closing delimiter")
        return {}

    meta = lines[1:end]
    keys = [line.split(":", 1)[0].strip() for line in meta if re.match(r"^[A-Za-z_-]+:", line)]
    for key in keys:
        if key not in {"name", "description", "tags"}:
            report(errors, path, f"unexpected frontmatter field '{key}'")

    name = next((line.split(":", 1)[1].strip().strip('"') for line in meta if line.startswith("name:")), "")
    description = next(
        (line.split(":", 1)[1].strip().strip('"') for line in meta if line.startswith("description:")),
        "",
    )
    tags_start = next((i for i, line in enumerate(meta) if line.strip() == "tags:"), None)
    tags: list[str] = []
    if tags_start is not None:
        for line in meta[tags_start + 1 :]:
            stripped = line.strip()
            if stripped.startswith("- "):
                tags.append(stripped[2:].strip())
            elif stripped and not line.startswith(" "):
                break

    if not name:
        report(errors, path, "frontmatter name is missing")
    if not description:
        report(errors, path, "frontmatter description is missing")
    else:
        if not description.startswith("Use when"):
            report(errors, path, "description must start with 'Use when'")
        if len(description) > DESCRIPTION_LIMIT:
            report(errors, path, f"description exceeds {DESCRIPTION_LIMIT} characters ({len(description)})")
        if CJK_RE.search(description):
            report(errors, path, "description must be English (CJK characters found)")
    if tags_start is None or not tags:
        report(errors, path, "tags must be a non-empty multiline list")
    elif len(tags) < 5:
        report(errors, path, f"too few tags ({len(tags)}), keep 5-10")
    for tag in tags:
        if not re.fullmatch(r"[a-z0-9][a-z0-9.\-]*", tag):
            report(errors, path, f"invalid tag '{tag}' (lowercase, digits, dot, hyphen only)")

    return {"name": name, "description": description, "tags": tags, "keys": keys}


def validate_links(root: Path, path: Path, text: str, errors: list[str]) -> None:
    for match in MARKDOWN_LINK_RE.finditer(text):
        href = match.group(1).strip().strip('<>"')
        parsed = urlsplit(href)
        if not href or parsed.scheme or parsed.netloc:
            continue
        target = unquote(parsed.path)
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            report(errors, path, f"link escapes repository: {href}")
            continue
        if not resolved.is_file():
            report(errors, path, f"broken relative link: {href}")


def validate_body(root: Path, path: Path, text: str, errors: list[str]) -> None:
    lines = text.splitlines()
    relative = path.relative_to(root)

    if EMOJI_RE.search(text):
        hits = sorted({match.group(0) for match in EMOJI_RE.finditer(text)})
        report(errors, relative, f"emoji not allowed in L3 skill: {' '.join(hits)}")

    in_block = False
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_block:
                in_block = True
                if stripped == "```":
                    report(errors, relative, f"line {number}: code fence without language")
            else:
                in_block = False

    headings = [line.strip().lower() for line in lines if line.startswith("## ")]
    joined = "\n".join(headings)
    for label, keywords in REQUIRED_SECTIONS.items():
        if not any(keyword.lower() in joined for keyword in keywords):
            report(errors, relative, f"missing required section: {label}")

    # FAQ table rows
    faq_counts = 0
    in_faq = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_faq = any(keyword.lower() in stripped.lower() for keyword in REQUIRED_SECTIONS["FAQ"])
            continue
        if in_faq and stripped.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", stripped):
            faq_counts += 1
    if faq_counts and faq_counts - 1 < MIN_FAQ_ROWS:
        report(errors, relative, f"FAQ table has {max(faq_counts - 1, 0)} rows, need >={MIN_FAQ_ROWS}")
    elif faq_counts == 0:
        report(errors, relative, "FAQ section must contain a markdown table")


def validate_index_duplicates(root: Path, path: Path, text: str, errors: list[str]) -> dict:
    targets: dict[Path, int] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        match = INDEX_ROW_RE.match(line)
        if not match:
            continue
        href = match.group(1).split("#", 1)[0].strip()
        if not href or urlsplit(href).scheme or urlsplit(href).netloc:
            continue
        target = (path.parent / unquote(href)).resolve()
        if target in targets:
            report(
                errors,
                path.relative_to(root),
                f"duplicate index target {href} (lines {targets[target]} and {line_number})",
            )
        else:
            targets[target] = line_number
    return targets


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors: list[str] = []
    skill_files = sorted(root.rglob("SKILL.md"))
    if not skill_files:
        print("No SKILL.md files found", file=sys.stderr)
        return 1

    skills: dict[str, Path] = {}
    for path in skill_files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            report(errors, path.relative_to(root), f"not valid UTF-8: {error}")
            continue

        relative = path.relative_to(root)
        line_count = len(text.splitlines())
        if line_count > MAX_SKILL_LINES:
            report(errors, relative, f"{line_count} lines exceeds limit {MAX_SKILL_LINES}")

        meta = parse_frontmatter(path, text, errors)
        validate_links(root, path, text, errors)

        parts = relative.parts
        if len(parts) == 2 and parts[0] in CATEGORIES:
            # L2 category index
            expected = f"{parts[0]}-skills"
            if meta.get("name") and meta["name"] != expected:
                report(errors, relative, f"category index name must be '{expected}' (found '{meta['name']}')")
        elif len(parts) == 3:
            # L3 project skill
            expected = parts[1]
            if meta.get("name") and meta["name"] != expected:
                report(errors, relative, f"name must match directory '{expected}' (found '{meta['name']}')")
            skills[f"{parts[0]}/{parts[1]}"] = path
            if len(meta.get("tags", [])) > 10:
                report(errors, relative, f"too many tags ({len(meta['tags'])}), keep 5-10")
            validate_body(root, path, text, errors)
        elif len(parts) == 1:
            if meta.get("name") != "opengis-skills":
                report(errors, relative, "root skill name must be 'opengis-skills'")

    # index coverage
    root_index = root / "SKILL.md"
    if root_index.is_file():
        root_text = root_index.read_text(encoding="utf-8")
        root_targets = validate_index_duplicates(root, root_index, root_text, errors)
        listed = {
            target.relative_to(root).parent.as_posix()
            for target in root_targets
            if target.name == "SKILL.md" and "SKILL.md" in str(target)
        }
        missing = sorted(set(skills) - listed)
        extra = sorted(listed - set(skills))
        if missing:
            report(errors, Path("SKILL.md"), f"{len(missing)} skills missing from root index: {', '.join(missing[:8])}")
        if extra:
            report(errors, Path("SKILL.md"), f"root index lists unknown skills: {', '.join(extra[:8])}")

    for category in CATEGORIES:
        index = root / category / "SKILL.md"
        if not index.is_file():
            report(errors, Path(category), "missing category index SKILL.md")
            continue
        text = index.read_text(encoding="utf-8")
        targets = validate_index_duplicates(root, index, text, errors)
        listed = {
            target.relative_to(root).parent.as_posix()
            for target in targets
            if target.name == "SKILL.md"
        }
        expected = {name for name in skills if name.startswith(category + "/")}
        missing = sorted(expected - listed)
        extra = sorted(listed - expected)
        if missing:
            report(errors, index.relative_to(root), f"skills missing from category index: {', '.join(missing[:8])}")
        if extra:
            report(errors, index.relative_to(root), f"category index lists unknown skills: {', '.join(extra[:8])}")

    # README coverage
    readme = root / "README.md"
    if readme.is_file():
        readme_text = readme.read_text(encoding="utf-8")
        linked = set()
        for match in MARKDOWN_LINK_RE.finditer(readme_text):
            href = match.group(1).strip()
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            target = (readme.parent / unquote(parsed.path)).resolve()
            if target.name == "SKILL.md":
                linked.add(target.relative_to(root).parent.as_posix())
        missing = sorted(set(skills) - linked)
        if missing:
            report(errors, Path("README.md"), f"{len(missing)} skills missing from README: {', '.join(missing[:8])}")

    if errors:
        print("Skill validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(f"Skill validation passed: {len(skill_files)} SKILL.md files, {len(skills)} project skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
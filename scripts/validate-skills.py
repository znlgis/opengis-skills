#!/usr/bin/env python3
"""Validate opengis-skills structure, metadata and indexes.

Single source of truth for the repository's SKILL.md conventions. Enforces the
Agent Skills open standard (https://agentskills.io/specification) plus this
repository's stricter house rules documented in AUTHORING.md.

Frontmatter: only name / description / license / compatibility / metadata /
allowed-tools; name matches the parent directory; description is English,
starts with "Use when", no angle brackets, unique; metadata carries category
and a 5-10 token comma-separated tags string.

Body: <=500 lines, no emoji in L3, language on every code fence, required
sections (including the tool-agnostic "AI usage" guidance section), FAQ table
with >=5 rows, resolvable relative links, no Windows backslash paths,
reference/*.md all linked and >100-line files get a Contents section. L3 skills
must also carry a freshness marker ("截至 YYYY-MM") in the head region so stale
version claims are visible.

Indexes: root SKILL.md, category indexes and README.md cover every skill
exactly once and advertised skill counts match reality.

Usage:
    python scripts/validate-skills.py .                     # full repository (CI)
    python scripts/validate-skills.py . --only gis/gdal     # one skill, skips index checks
    python scripts/validate-skills.py . --only gis          # one category, skips index checks
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

MAX_SKILL_LINES = 500
MAX_DESCRIPTION_CHARS = 500
MIN_FAQ_ROWS = 5
MIN_TAGS = 5
MAX_TAGS = 10
MAX_REFERENCE_WITHOUT_TOC = 100
HEAD_REGION_LINES = 40

CATEGORIES = ["3d", "ai", "cad", "csharp", "demos", "gis", "iot", "others"]
ROOT_SKILL_NAME = "opengis-skills"

ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
ALLOWED_METADATA_KEYS = {"category", "tags"}

FENCE = chr(96) * 3
FENCE_RE = re.compile(r"^\s*(?:" + FENCE + r"|~~~)(.*)$")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
CJK_RE = re.compile("[\u4e00-\u9fff]")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]")
ANGLE_RE = re.compile(r"[<>]")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
INDEX_ROW_RE = re.compile(r"^\|\s*\[[^\]]+\]\(([^)]+)\)")
FRESHNESS_RE = re.compile(r"截至\s*(\d{4})-(\d{2})")

REQUIRED_SECTIONS = {
    "overview": ["概述", "简介"],
    "install": ["环境准备", "安装", "快速开始", "环境搭建", "部署"],
    "workflow": ["工作流", "使用模式", "实战", "常见用法", "典型场景", "使用流程"],
    "FAQ": ["常见问题", "FAQ", "故障排查", "排错"],
    "related": ["相关技能", "相关资源", "参考资源", "参考资料", "延伸阅读"],
    "ai": ["AI 使用建议", "AI 使用"],
}


class Report:
    def __init__(self) -> None:
        self.errors = []
        self.warnings = []

    def error(self, path, message):
        self.errors.append(str(path).replace(chr(92), "/") + ": " + message)

    def warn(self, path, message):
        self.warnings.append(str(path).replace(chr(92), "/") + ": " + message)


def split_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], "\n".join(lines[index + 1:])
    return None


def parse_scalar(raw):
    value = raw.strip()
    if not value:
        return ""
    if value[0] == '"':
        if len(value) < 2 or value[-1] != '"':
            return value
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if value[0] == "'":
        if len(value) < 2 or value[-1] != "'":
            return value
        return value[1:-1].replace("''", "'")
    return value


def parse_frontmatter(lines, report, path):
    fields = {}
    metadata = {}
    in_metadata = False
    metadata_indent = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):(.*)$", stripped)
        if in_metadata and indent > metadata_indent:
            if match:
                key, raw = match.group(1), match.group(2)
                if key not in ALLOWED_METADATA_KEYS:
                    report.error(path, "unexpected metadata key '" + key + "' (allowed: category, tags)")
                metadata[key] = parse_scalar(raw)
                continue
            report.error(path, "unparsable metadata line: " + repr(line))
            continue
        if not match:
            report.error(path, "unparsable frontmatter line: " + repr(line))
            continue
        key, raw = match.group(1), match.group(2)
        if key not in ALLOWED_FIELDS:
            report.error(path, "unexpected frontmatter field '" + key + "' (allowed: " + ", ".join(sorted(ALLOWED_FIELDS)) + ")")
        if key == "metadata":
            in_metadata = True
            metadata_indent = indent
            if raw.strip():
                report.error(path, "metadata must be a nested map of string keys")
            continue
        in_metadata = False
        fields[key] = parse_scalar(raw)
    return {"fields": fields, "metadata": metadata}


def validate_name_and_license(meta, relative, report):
    fields = meta["fields"]
    name = fields.get("name", "")
    license_name = fields.get("license", "")
    if not name:
        report.error(relative, "frontmatter name is missing")
    else:
        if len(name) > 64:
            report.error(relative, "name exceeds 64 characters (" + str(len(name)) + ")")
        if not NAME_RE.fullmatch(name):
            report.error(relative, "invalid name '" + name + "' (lowercase letters, digits and single hyphens only)")
        expected = relative.parent.name if len(relative.parts) > 1 else ROOT_SKILL_NAME
        if name != expected:
            report.error(relative, "name must match parent directory '" + expected + "' (found '" + name + "')")
    if not license_name:
        report.error(relative, "frontmatter license is missing")
    elif license_name != "MIT":
        report.error(relative, "license must be 'MIT' for repository skills (found '" + license_name + "')")


def validate_description(meta, relative, report, seen):
    description = meta["fields"].get("description", "")
    if not description:
        report.error(relative, "frontmatter description is missing")
        return
    if not description.startswith("Use when"):
        report.error(relative, "description must start with 'Use when'")
    if len(description) > MAX_DESCRIPTION_CHARS:
        report.error(relative, "description exceeds " + str(MAX_DESCRIPTION_CHARS) + " characters (" + str(len(description)) + ")")
    if CJK_RE.search(description):
        report.error(relative, "description must be English (CJK characters found)")
    if ANGLE_RE.search(description):
        report.error(relative, "description must not contain angle brackets")
    key = " ".join(description.lower().split())
    if key in seen:
        report.error(relative, "description duplicates " + seen[key])
    else:
        seen[key] = relative.as_posix()


def validate_metadata(meta, relative, report):
    metadata = meta["metadata"]
    category = metadata.get("category", "")
    tags_raw = metadata.get("tags", "")
    parts = relative.parts
    if len(parts) in (2, 3):
        expected_category = parts[0]
        if not category:
            report.error(relative, "metadata.category is required for category and project skills")
        elif category != expected_category:
            report.error(relative, "metadata.category must be '" + expected_category + "' (found '" + category + "')")
    elif category:
        report.warn(relative, "root skill does not need metadata.category")
    if not tags_raw:
        report.error(relative, "metadata.tags is required")
        return
    tags = [part.strip() for part in tags_raw.split(",") if part.strip()]
    if not (MIN_TAGS <= len(tags) <= MAX_TAGS):
        report.error(relative, "metadata.tags must contain " + str(MIN_TAGS) + "-" + str(MAX_TAGS) + " comma-separated tags (" + str(len(tags)) + " found)")
    seen = set()
    for tag in tags:
        if tag in seen:
            report.error(relative, "duplicate tag '" + tag + "'")
        seen.add(tag)
        if not TAG_RE.fullmatch(tag):
            report.error(relative, "invalid tag '" + tag + "' (lowercase, digits, dot, hyphen only)")


def is_fence(line):
    return FENCE_RE.match(line) is not None


def validate_body(relative, text, report, is_skill):
    lines = text.splitlines()
    if len(lines) > MAX_SKILL_LINES:
        report.error(relative, str(len(lines)) + " lines exceeds limit " + str(MAX_SKILL_LINES))
    if is_skill and EMOJI_RE.search(text):
        hits = sorted({match.group(0) for match in EMOJI_RE.finditer(text)})
        report.error(relative, "emoji not allowed in L3 skill: " + " ".join(hits))

    in_code = False
    for number, line in enumerate(lines, 1):
        if is_fence(line):
            if not in_code:
                in_code = True
                marker = line.strip()[:3]
                if line.strip() == marker:
                    report.error(relative, "line " + str(number) + ": code fence without language")
            else:
                in_code = False

    headings = []
    in_code = False
    for line in lines:
        if is_fence(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("## "):
            headings.append(line[3:].strip())
    joined = "\n".join(headings).lower()
    if is_skill:
        for label, keywords in REQUIRED_SECTIONS.items():
            if not any(keyword.lower() in joined for keyword in keywords):
                report.error(relative, "missing required section: " + label)

    in_faq = False
    faq_rows = 0
    in_code = False
    for line in lines:
        if is_fence(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        stripped = line.strip()
        if stripped.startswith("## "):
            in_faq = any(keyword.lower() in stripped.lower() for keyword in REQUIRED_SECTIONS["FAQ"])
            continue
        if in_faq and stripped.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", stripped):
            faq_rows += 1
    if is_skill:
        if faq_rows == 0:
            report.error(relative, "FAQ section must contain a markdown table")
        elif faq_rows - 1 < MIN_FAQ_ROWS:
            report.error(relative, "FAQ table has " + str(max(faq_rows - 1, 0)) + " rows, need >= " + str(MIN_FAQ_ROWS))


PLACEHOLDER_RE = re.compile(r"@@[A-Za-z0-9_]*@@")


def validate_placeholders(relative, text, report):
    """Catch unresolved template tokens such as @@F@@ that break rendering."""
    in_code = False
    for number, line in enumerate(text.splitlines(), 1):
        if is_fence(line):
            in_code = not in_code
            continue
        match = PLACEHOLDER_RE.search(line)
        if match and not in_code:
            report.error(relative, "line " + str(number) + ": unresolved placeholder token " + match.group(0))


def validate_frontmatter_yaml(relative, frontmatter_lines, report):
    """Reject frontmatter that a strict YAML parser cannot read.

    PyYAML is used when it is installed (CI installs it); otherwise a
    dependency-free check still catches the common failure: an unescaped
    double quote inside a double-quoted scalar, which makes the value stop
    early and the whole block unparsable.
    """
    for line in frontmatter_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        _, _, raw = stripped.partition(":")
        value = raw.strip()
        if len(value) < 2 or not (value.startswith('"') and value.endswith('"')):
            continue
        inner = value[1:-1]
        index = 0
        while index < len(inner):
            char = inner[index]
            if char == "\\":
                index += 2
                continue
            if char == '"':
                report.error(relative, "frontmatter value contains an unescaped double quote (invalid YAML): " + value[:60] + "...")
                break
            index += 1
    try:
        import yaml  # noqa: F401
    except ImportError:
        return
    try:
        yaml.safe_load("\n".join(frontmatter_lines))
    except Exception as error:  # noqa: BLE001
        first = str(error).splitlines()[0] if str(error) else error.__class__.__name__
        report.error(relative, "frontmatter is not valid YAML: " + first)


def validate_freshness(relative, text, report):
    """L3 skills must state when their version claims were last verified."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                lines = lines[index + 1:]
                break
    head = "\n".join(lines[:HEAD_REGION_LINES])
    if not FRESHNESS_RE.search(head):
        report.error(relative, "missing freshness marker '截至 YYYY-MM' in the head region (state when the version claim was verified)")


def validate_links(root, path, text, report):
    in_code = False
    for line in text.splitlines():
        if is_fence(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        for match in MARKDOWN_LINK_RE.finditer(line):
            href = match.group(1).strip().strip('<>"').strip("'")
            if "\\" in href:
                report.error(path.relative_to(root), "Windows-style path in link: " + href)
                continue
            parsed = urlsplit(href)
            if not href or parsed.scheme or parsed.netloc or href.startswith("#"):
                continue
            target = unquote(parsed.path)
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                report.error(path.relative_to(root), "link escapes repository: " + href)
                continue
            if not resolved.is_file():
                report.error(path.relative_to(root), "broken relative link: " + href)


def validate_reference_dir(root, skill_md, text, report):
    reference_dir = skill_md.parent / "reference"
    if not reference_dir.is_dir():
        return
    links = set()
    in_code = False
    for line in text.splitlines():
        if is_fence(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        for match in MARKDOWN_LINK_RE.finditer(line):
            href = match.group(1).strip().strip('<>"').strip("'")
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or href.startswith("#"):
                continue
            target = (skill_md.parent / unquote(parsed.path)).resolve()
            try:
                rel = target.relative_to(reference_dir.resolve())
            except ValueError:
                continue
            links.add(rel.as_posix())
    for reference in sorted(reference_dir.rglob("*.md")):
        rel = reference.relative_to(reference_dir).as_posix()
        relative = reference.relative_to(root)
        if rel not in links:
            report.error(relative, "reference file is not linked from SKILL.md (orphan): reference/" + rel)
        ref_text = reference.read_text(encoding="utf-8")
        if len(ref_text.splitlines()) > MAX_REFERENCE_WITHOUT_TOC:
            if not re.search(r"(?im)^##\s*(contents|目录)", ref_text):
                report.error(relative, "reference file longer than " + str(MAX_REFERENCE_WITHOUT_TOC) + " lines needs a '## Contents' section")


TAG_CELL_RE = re.compile(r"^\|\s*((?:\x60[^\x60|]+\x60\s*(?:/\s*)?)+)\s*\|\s*([^|]+?)\s*\|\s*$")


def validate_tag_index(root, text, skills, report):
    """Every skill listed under a tag row must really carry one of that row's tags."""
    tags_by_skill = {}
    for key, path in skills.items():
        skill_text = path.read_text(encoding="utf-8")
        parsed = split_frontmatter(skill_text)
        if parsed is None:
            continue
        meta = parse_frontmatter(parsed[0], Report(), path)
        raw = meta["metadata"].get("tags", "")
        tags_by_skill[path.parent.name] = {part.strip() for part in raw.split(",") if part.strip()}
    in_section = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_section = line[3:].strip().startswith("标签索引")
            continue
        if not in_section or not line.startswith("|"):
            continue
        cells = TAG_CELL_RE.match(line)
        if not cells:
            continue
        row_tags = [part.strip().strip(chr(96)) for part in cells.group(1).split("/") if part.strip()]
        if not row_tags:
            continue
        for name in [item.strip() for item in cells.group(2).split(",") if item.strip()]:
            have = tags_by_skill.get(name)
            if have is None:
                report.error(Path("SKILL.md"), "tag index lists unknown skill '" + name + "'")
            elif not (have & set(row_tags)):
                report.error(
                    Path("SKILL.md"),
                    "tag index lists '" + name + "' under " + "/".join(row_tags)
                    + " but its metadata.tags are: " + ", ".join(sorted(have)),
                )


def index_targets(root, index, text, report):
    targets = {}
    in_code = False
    for number, line in enumerate(text.splitlines(), 1):
        if is_fence(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        match = INDEX_ROW_RE.match(line)
        if not match:
            continue
        href = match.group(1).split("#", 1)[0].strip()
        parsed = urlsplit(href)
        if not href or parsed.scheme or parsed.netloc:
            continue
        target = (index.parent / unquote(href)).resolve()
        if target in targets:
            report.error(index.relative_to(root), "duplicate index target " + href + " (lines " + str(targets[target]) + " and " + str(number) + ")")
        else:
            targets[target] = number
    return targets


def validate_count(description, expected, relative, report):
    for pattern in [r"Index of (\d+) skills", r"(\d+) 个技能"]:
        for match in re.finditer(pattern, description):
            if int(match.group(1)) != expected:
                report.error(relative, "description advertises " + match.group(1) + " skills but repository has " + str(expected))


def select_files(root, all_files, only):
    """Limit validation to the given <category> or <category>/<skill> prefixes."""
    wanted = []
    for prefix in only:
        prefix = prefix.replace(chr(92), "/").strip("/")
        match = [
            path
            for path in all_files
            if path.relative_to(root).as_posix() == prefix + "/SKILL.md"
            or path.relative_to(root).as_posix().startswith(prefix + "/")
        ]
        if not match:
            print("warning: --only filter matched no files: " + prefix, file=sys.stderr)
        for path in match:
            if path not in wanted:
                wanted.append(path)
    return sorted(wanted)


def main():
    parser = argparse.ArgumentParser(description="Validate opengis-skills structure, metadata and indexes.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="PREFIX",
        help="validate only skills under this <category> or <category>/<skill> prefix "
        "(repeatable); cross-repository index and count checks are skipped",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()
    report = Report()
    skill_files = sorted(root.rglob("SKILL.md"))
    skill_files = [path for path in skill_files if ".git" not in path.parts]
    if not skill_files:
        print("No SKILL.md files found", file=sys.stderr)
        return 1
    if args.only:
        skill_files = select_files(root, skill_files, args.only)

    skills = {}
    category_skills = {category: [] for category in CATEGORIES}
    descriptions = {}
    root_description = ""
    category_descriptions = {}

    for path in skill_files:
        relative = path.relative_to(root)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            report.error(relative, "not valid UTF-8: " + str(error))
            continue
        parsed = split_frontmatter(text)
        if parsed is None:
            report.error(relative, "missing or malformed frontmatter (must start at line 1 and close with ---)")
            continue
        frontmatter, body = parsed
        validate_frontmatter_yaml(relative, frontmatter, report)
        meta = parse_frontmatter(frontmatter, report, relative)
        validate_name_and_license(meta, relative, report)
        validate_description(meta, relative, report, descriptions)
        validate_metadata(meta, relative, report)
        validate_links(root, path, body, report)

        parts = relative.parts
        if len(parts) == 3 and parts[0] in CATEGORIES:
            validate_body(relative, body, report, is_skill=True)
            validate_freshness(relative, body, report)
            validate_placeholders(relative, body, report)
            validate_reference_dir(root, path, body, report)
            skills[parts[0] + "/" + parts[1]] = path
            category_skills[parts[0]].append(parts[0] + "/" + parts[1])
        elif len(parts) == 2 and parts[0] in CATEGORIES:
            validate_body(relative, body, report, is_skill=False)
            category_descriptions[parts[0]] = meta["fields"].get("description", "")
        elif len(parts) == 1:
            root_description = meta["fields"].get("description", "")
        else:
            report.error(relative, "SKILL.md must live at <root>/, <category>/ or <category>/<skill>/")

    if args.only:
        for warning in report.warnings:
            print("warning: " + warning)
        if report.errors:
            print("Skill validation failed:")
            print("\n".join("- " + error for error in report.errors))
            return 1
        print(
            "Skill validation passed (--only " + ", ".join(args.only) + "): "
            + str(len(skill_files)) + " SKILL.md files checked, cross-repository index checks skipped"
        )
        return 0

    total = len(skills)
    if root_description:
        validate_count(root_description, total, Path("SKILL.md"), report)
        for category in CATEGORIES:
            match = re.search(category + r"\s*\((\d+)\)", root_description)
            if match and int(match.group(1)) != len(category_skills[category]):
                report.error(Path("SKILL.md"), "description advertises " + match.group(1) + " " + category + " skills but there are " + str(len(category_skills[category])))

    for category in CATEGORIES:
        description = category_descriptions.get(category, "")
        if description:
            validate_count(description, len(category_skills[category]), Path(category + "/SKILL.md"), report)

    root_skill = root / "SKILL.md"
    if root_skill.is_file():
        validate_tag_index(root, root_skill.read_text(encoding="utf-8"), skills, report)

    root_index = root / "SKILL.md"
    if root_index.is_file():
        listed = index_targets(root, root_index, root_index.read_text(encoding="utf-8"), report)
        linked = set()
        for target in listed:
            if target.name == "SKILL.md":
                try:
                    parts = target.relative_to(root).parts
                except ValueError:
                    continue
                if len(parts) == 3:
                    linked.add(parts[0] + "/" + parts[1])
        missing = sorted(set(skills) - linked)
        extra = sorted(linked - set(skills))
        if missing:
            report.error(Path("SKILL.md"), str(len(missing)) + " skills missing from root index: " + ", ".join(missing[:8]))
        if extra:
            report.error(Path("SKILL.md"), "root index lists unknown skills: " + ", ".join(extra[:8]))

    for category in CATEGORIES:
        index = root / category / "SKILL.md"
        if not index.is_file():
            report.error(Path(category), "missing category index SKILL.md")
            continue
        targets = index_targets(root, index, index.read_text(encoding="utf-8"), report)
        linked = set()
        for target in targets:
            if target.name == "SKILL.md":
                try:
                    parts = target.relative_to(root).parts
                except ValueError:
                    continue
                if len(parts) == 3:
                    linked.add(parts[0] + "/" + parts[1])
        expected = set(category_skills[category])
        missing = sorted(expected - linked)
        extra = sorted(linked - expected)
        if missing:
            report.error(index.relative_to(root), "skills missing from category index: " + ", ".join(missing[:8]))
        if extra:
            report.error(index.relative_to(root), "category index lists unknown skills: " + ", ".join(extra[:8]))

    for doc in [root / "README.md", root / "AUTHORING.md"]:
        if not doc.is_file():
            report.error(doc.relative_to(root), "required repository document is missing")
            continue
        validate_links(root, doc, doc.read_text(encoding="utf-8"), report)

    readme = root / "README.md"
    if readme.is_file():
        linked = set()
        in_code = False
        for line in readme.read_text(encoding="utf-8").splitlines():
            if is_fence(line):
                in_code = not in_code
                continue
            if in_code:
                continue
            for match in MARKDOWN_LINK_RE.finditer(line):
                href = match.group(1).strip().strip('<>"').strip("'")
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc:
                    continue
                target = (readme.parent / unquote(parsed.path)).resolve()
                if target.name == "SKILL.md" and target.is_file():
                    try:
                        parts = target.relative_to(root).parts
                    except ValueError:
                        continue
                    if len(parts) == 3:
                        linked.add(parts[0] + "/" + parts[1])
        missing = sorted(set(skills) - linked)
        if missing:
            report.error(Path("README.md"), str(len(missing)) + " skills missing from README: " + ", ".join(missing[:8]))

    for warning in report.warnings:
        print("warning: " + warning)
    if report.errors:
        print("Skill validation failed:")
        print("\n".join("- " + error for error in report.errors))
        return 1

    print("Skill validation passed: " + str(len(skill_files)) + " SKILL.md files, " + str(total) + " project skills across " + str(len(CATEGORIES)) + " categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

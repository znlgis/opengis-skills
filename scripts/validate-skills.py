#!/usr/bin/env python3
"""Validate SKILL.md metadata, links, line limits, and index duplicates."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


MAX_SKILL_LINES = 500
DESCRIPTION_LIMIT = 500
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
INDEX_ROW_RE = re.compile(r"^\|\s*\[[^]]+\]\(([^)]+)\)")


def report(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.as_posix()}: {message}")


def parse_frontmatter(path: Path, text: str, errors: list[str]) -> None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        report(errors, path, "missing frontmatter opening delimiter")
        return

    try:
        end = lines.index("---", 1)
    except ValueError:
        report(errors, path, "missing frontmatter closing delimiter")
        return

    metadata = lines[1:end]
    name = next((line.split(":", 1)[1].strip() for line in metadata if line.startswith("name:")), "")
    description = next(
        (line.split(":", 1)[1].strip().strip('"') for line in metadata if line.startswith("description:")),
        "",
    )
    tags_start = next((index for index, line in enumerate(metadata) if line.strip() == "tags:"), None)
    tags = []
    if tags_start is not None:
        tags = [line.strip()[2:].strip() for line in metadata[tags_start + 1 :] if line.strip().startswith("-")]

    if not name:
        report(errors, path, "frontmatter name is missing")
    if not description:
        report(errors, path, "frontmatter description is missing")
    elif not description.startswith("Use when"):
        report(errors, path, "description must start with 'Use when'")
    if len(description) > DESCRIPTION_LIMIT:
        report(errors, path, f"description exceeds {DESCRIPTION_LIMIT} characters")
    if tags_start is None or not tags:
        report(errors, path, "tags must be a non-empty multiline list")


def validate_links(root: Path, path: Path, text: str, errors: list[str]) -> None:
    for match in MARKDOWN_LINK_RE.finditer(text):
        href = match.group(1).strip().strip("<>\"")
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


def validate_index_duplicates(root: Path, path: Path, text: str, errors: list[str]) -> None:
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
            report(errors, path, f"duplicate index target {href} (also on line {targets[target]}; duplicate on line {line_number})")
        else:
            targets[target] = line_number


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors: list[str] = []
    skill_files = sorted(root.rglob("SKILL.md"))
    if not skill_files:
        print("No SKILL.md files found", file=sys.stderr)
        return 1

    for path in skill_files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            report(errors, path, f"not valid UTF-8: {error}")
            continue

        relative = path.relative_to(root)
        line_count = len(text.splitlines())
        if line_count > MAX_SKILL_LINES:
            report(errors, relative, f"{line_count} lines exceeds limit {MAX_SKILL_LINES}")
        parse_frontmatter(relative, text, errors)
        validate_links(root, path, text, errors)

        if relative == Path("SKILL.md") or (len(relative.parts) == 2 and relative.parts[-1] == "SKILL.md"):
            validate_index_duplicates(root, path, text, errors)

    if errors:
        print("Skill validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(f"Skill validation passed: {len(skill_files)} SKILL.md files checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

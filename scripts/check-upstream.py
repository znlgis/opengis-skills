#!/usr/bin/env python3
"""Report upstream version drift for every project skill.

For each L3 SKILL.md this script reads the upstream repository URL and the
version pinned in the head of the file, queries the newest release tag, and
prints a drift table. It never edits files.

Usage:
    python scripts/check-upstream.py .            # human readable table
    python scripts/check-upstream.py . --json     # machine readable
    python scripts/check-upstream.py . --workers 16 --timeout 60

Exit code is 1 when at least one skill is behind its upstream release, 0 when
everything is current or undetermined.

Known false positives to check by hand before editing a skill:

* multi-package repositories whose newest tag belongs to another package
  (langchain, mapbox-gl-js style-spec, geotools C-prefixed tags, sentry dump
  tags, sqlsugar git tags that are not on NuGet);
* repositories using a different versioning scheme (hermes-agent dates,
  kicad nightly 10.99, libredwg rolling 0.14.8xxx, openscad TEST snapshots,
  blender, go's release.rXX tags, esphome beta tags);
* version sources that are not GitHub tags at all (NuGet, PyPI, npm, Maven),
  where the package registry is authoritative;
* skills whose head "最新版本" line is missing, so the claimed version is
  picked up from a dependency version instead.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
from pathlib import Path

VERSION_RE = re.compile(r"(\d+(?:\.\d+){0,3})")
TAG_VERSION_RE = re.compile(r"(\d+(?:\.\d+)+)")
SKIP_HOST_PARTS = ("github.com",)


def split_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return lines
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[index + 1:]
    return lines


def head_region(body_lines, limit=80):
    return "\n".join(body_lines[:limit])


def find_repo(head, skill_name):
    candidates = []
    for match in re.finditer(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", head):
        repo = (match.group(1) + "/" + match.group(2)).rstrip(".")
        if repo.endswith(".git"):
            repo = repo[:-4]
        if repo not in candidates:
            candidates.append(repo)
    if not candidates:
        return None
    wanted = re.sub(r"[^a-z0-9]+", "-", skill_name.lower()).strip("-")
    for repo in candidates:
        base = re.sub(r"[^a-z0-9]+", "-", repo.split("/")[-1].lower()).strip("-")
        if base == wanted:
            return repo
    return candidates[0]


def find_claimed_version(head):
    patterns = [
        r"\*\*最新(?:稳定)?版本[^*]*\*\*\s*[:：]?\s*v?(\d+(?:\.\d+)+)",
        r"最新(?:稳定)?版本[^\n]{0,30}?v?(\d+(?:\.\d+)+)",
        r"\*\*版本[^*]*\*\*\s*[:：]?\s*v?(\d+(?:\.\d+)+)",
        r"版本[^\n]{0,20}?v?(\d+(?:\.\d+)+)",
        r"go(\d+\.\d+(?:\.\d+)?)",
        r"\b(\d+\.\d+\.\d+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, head)
        if match:
            return match.group(1)
    return None


PRERELEASE_RE = re.compile(
    r"(?i)(alpha|beta|rc\d*|preview|snapshot|nightly|weekly|canary|next|dev|pre|m\d|\bM\d+\b)"
)
VERSION_TAG_RE = re.compile(r"(?P<v>\d+(?:\.\d+){0,3})")


def parse_version(text):
    numbers = []
    for part in TAG_VERSION_RE.findall(text):
        numbers.extend(int(piece) for piece in part.split("."))
        break
    return tuple(numbers)


def latest_tag(repo, timeout):
    url = "https://github.com/" + repo + ".git"
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="echo")
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "--refs", url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None, "git failed"
    if result.returncode != 0:
        stderr = (result.stderr or "").strip().splitlines()
        return None, (stderr or ["git error"])[0][:120]
    tags = []
    for line in (result.stdout or "").splitlines():
        if "refs/tags/" not in line:
            continue
        tag = line.split("refs/tags/", 1)[1].strip()
        if PRERELEASE_RE.search(tag) or "=" in tag or "@" in tag:
            continue
        match = VERSION_TAG_RE.search(tag)
        if not match:
            continue
        version = parse_version(match.group("v"))
        if version:
            tags.append((version, tag))
    if not tags:
        return None, "no stable version tags"
    tags.sort()
    return tags[-1][0], tags[-1][1]


def compare(claimed, latest):
    if not claimed or not latest:
        return "unknown"
    claimed_tuple = tuple(int(piece) for piece in claimed.split("."))
    latest_tuple = latest[: len(claimed_tuple)]
    if latest > claimed_tuple:
        return "behind"
    if latest == claimed_tuple:
        return "current"
    return "ahead"


def check_one(skill, timeout):
    path = Path(skill["path"])
    text = path.read_text(encoding="utf-8")
    head = head_region(split_frontmatter(text))
    claimed = find_claimed_version(head)
    repo = find_repo(head, skill.get("name", ""))
    row = {"skill": skill["skill"], "repo": repo, "claimed": claimed, "latest": None, "latest_tag": None, "status": "unknown"}
    if not repo:
        row["status"] = "no-repo"
        return row
    version, tag = latest_tag(repo, timeout)
    if version is None:
        row["latest_tag"] = tag
        return row
    row["latest"] = ".".join(str(piece) for piece in version)
    row["latest_tag"] = tag
    row["status"] = compare(claimed, version)
    return row


def collect(root):
    rows = []
    for path in sorted(root.rglob("SKILL.md")):
        relative = path.relative_to(root)
        if len(relative.parts) != 3:
            continue
        rows.append({"skill": relative.parts[0] + "/" + relative.parts[1], "name": relative.parts[1], "path": str(path)})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--timeout", type=float, default=40.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    skills = collect(root)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check_one, skill, args.timeout) for skill in skills]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    results.sort(key=lambda row: ({"behind": 0, "unknown": 1, "no-repo": 2, "ahead": 3, "current": 4}.get(row["status"], 5), row["skill"]))

    if args.as_json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    else:
        behind = [row for row in results if row["status"] == "behind"]
        unknown = [row for row in results if row["status"] in ("unknown", "no-repo")]
        current = [row for row in results if row["status"] == "current"]
        print("checked " + str(len(results)) + " skills: " + str(len(current)) + " current, " + str(len(behind)) + " behind, " + str(len(unknown)) + " undetermined")
        print("")
        if behind:
            print("BEHIND UPSTREAM")
            for row in behind:
                print("  " + row["skill"] + "  claimed " + str(row["claimed"]) + " -> latest " + str(row["latest"]) + "  (" + str(row["latest_tag"]) + ")")
            print("")
        if unknown:
            print("UNDETERMINED")
            for row in unknown:
                print("  " + row["skill"] + "  repo=" + str(row["repo"]) + "  claimed=" + str(row["claimed"]) + "  latest=" + str(row["latest_tag"]))
        return 1 if behind else 0


if __name__ == "__main__":
    raise SystemExit(main())

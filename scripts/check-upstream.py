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

Known-benign "behind" rows verified by hand (2026-11) — do not "fix" the
version number for these, the skill head already explains the discrepancy:

* ai/superpowers-zh — the npm package is authoritative (1.8.0); the repo's
  git tags run ahead on an unrelated v5.x numbering.
* cad/kicad — 10.99.x is the development series for the next major version;
  the shipped stable release is 10.0.8.
* csharp/sqlsugar — git tags carry 5.9.x builds that were never published to
  NuGet; the newest stable NuGet package is 5.1.4.221.
* gis/geometry-api-java — source tag v2.3.1 exists but is not on Maven
  Central; the newest published artifact is 2.2.4.

Tags that look like versions but are not release versions (merge commits,
crash dumps, OpenSCAD TEST snapshots, Maven C-prefixed hotfixes, Go release
branches) are classified "ambiguous" instead of "behind"; pass --releases to
resolve date-style tags through the canonical /releases/latest redirect.
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
    r"(?i)(alpha|beta|rc\d*|preview|snapshot|nightly|weekly|canary|next|dev|pre|m\d|\bM\d+\b|\db\d+|\d+-nightly)"
)
VERSION_TAG_RE = re.compile(r"(?P<v>\d+(?:\.\d+){0,3})")

# Tags that carry a version number but are not the release version of the
# package: CI merge commits, dump/crash-upload builds, OpenSCAD TEST
# snapshots, Maven "C"-prefixed hotfix tags, Go release branches, and
# unrelated rolling counters. Comparing them against a claimed version
# produces false "behind" rows, so they are reported as ambiguous instead.
NOISY_TAG_RE = re.compile(
    r"(?i)(merge|dump|TEST|-C\d|^C\d|release\.r|nightly|rolling|build\.\d)"
)
FRESHNESS_RE = re.compile(r"截至\s*(\d{4})-(\d{2})")

# Rows verified by hand (2026-11) where the "behind" number is real but the
# skill head already explains why the claimed version is the right one. They
# are reported separately so a scheduled run does not stay permanently red.
KNOWN_BENIGN = {
    "ai/superpowers-zh": "npm package 1.8.0 is authoritative; repo tags use an unrelated v5.x numbering",
    "cad/kicad": "10.99.x is the development series for the next major release; 10.0.8 is the shipped stable build",
    "csharp/sqlsugar": "5.9.x git tags were never published to NuGet; the newest stable package is 5.1.4.221",
    "gis/geometry-api-java": "v2.3.1 is a GitHub release only; Maven Central stops at 2.2.4",
}


def parse_version(text):
    numbers = []
    for part in TAG_VERSION_RE.findall(text):
        numbers.extend(int(piece) for piece in part.split("."))
        break
    return tuple(numbers)


def latest_release(repo, timeout):
    """Resolve the newest published release tag without the REST API.

    GitHub redirects /releases/latest to /releases/tag/<tag>, which is the
    canonical "latest release" pointer and costs no API quota.
    """
    url = "https://github.com/" + repo + "/releases/latest"
    try:
        result = subprocess.run(
            ["curl", "-sIL", "--max-time", str(int(timeout)), url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    for line in (result.stdout or "").splitlines():
        if line.lower().startswith("location:"):
            target = line.split(":", 1)[1].strip()
            if "/releases/tag/" in target:
                return target.rsplit("/releases/tag/", 1)[1].strip()
            return None
    return None


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
    newest_version, newest_tag = tags[-1]
    if NOISY_TAG_RE.search(newest_tag):
        return None, "ambiguous tag " + newest_tag
    return newest_version, newest_tag


def compare(claimed, latest):
    """Compare on the claimed precision only: 27.0.3 vs 27.0.3.0 is not a drift."""
    if not claimed or not latest:
        return "unknown"
    claimed_tuple = tuple(int(piece) for piece in claimed.split("."))
    latest_tuple = latest[: len(claimed_tuple)]
    if latest_tuple > claimed_tuple:
        return "behind"
    if latest_tuple == claimed_tuple:
        return "current"
    return "ahead"


def check_one(skill, timeout, use_releases=False):
    path = Path(skill["path"])
    text = path.read_text(encoding="utf-8")
    head = head_region(split_frontmatter(text))
    claimed = find_claimed_version(head)
    repo = find_repo(head, skill.get("name", ""))
    fresh = FRESHNESS_RE.search(head)
    row = {
        "skill": skill["skill"],
        "repo": repo,
        "claimed": claimed,
        "latest": None,
        "latest_tag": None,
        "status": "unknown",
        "freshness": (fresh.group(0) if fresh else None),
    }
    if not repo:
        row["status"] = "no-repo"
        return row
    version, tag = latest_tag(repo, timeout)
    if version is None:
        row["latest_tag"] = tag
        if tag and tag.startswith("ambiguous tag"):
            row["status"] = "ambiguous"
        return row
    if use_releases and version[0] >= 2000:
        # Date-style tags (2026.9.24) sort as huge numbers and say nothing about
        # the release line; the canonical release pointer is authoritative there.
        release_tag = latest_release(repo, timeout)
        if release_tag and not PRERELEASE_RE.search(release_tag):
            match = VERSION_TAG_RE.search(release_tag)
            if match:
                release_version = parse_version(match.group("v"))
                if release_version:
                    row["latest_tag"] = release_tag
                    row["latest"] = ".".join(str(piece) for piece in release_version)
                    row["status"] = compare(claimed, release_version)
                    return row
    row["latest"] = ".".join(str(piece) for piece in version)
    row["latest_tag"] = tag
    status = compare(claimed, version)
    if status == "behind" and skill["skill"] in KNOWN_BENIGN:
        status = "known-benign"
        row["reason"] = KNOWN_BENIGN[skill["skill"]]
    row["status"] = status
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
    parser.add_argument(
        "--releases",
        action="store_true",
        help="also resolve the canonical /releases/latest tag for repositories whose git tags are ambiguous",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    skills = collect(root)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check_one, skill, args.timeout, args.releases) for skill in skills]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    order = {"behind": 0, "known-benign": 1, "ambiguous": 2, "unknown": 3, "no-repo": 4, "ahead": 5, "current": 6}
    results.sort(key=lambda row: (order.get(row["status"], 7), row["skill"]))

    if args.as_json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    else:
        behind = [row for row in results if row["status"] == "behind"]
        benign = [row for row in results if row["status"] == "known-benign"]
        ambiguous = [row for row in results if row["status"] == "ambiguous"]
        unknown = [row for row in results if row["status"] in ("unknown", "no-repo")]
        current = [row for row in results if row["status"] == "current"]
        stale = [row for row in results if not row.get("freshness")]
        print(
            "checked " + str(len(results)) + " skills: " + str(len(current)) + " current, "
            + str(len(behind)) + " behind, " + str(len(benign)) + " known-benign, "
            + str(len(ambiguous)) + " ambiguous, "
            + str(len(unknown)) + " undetermined, " + str(len(stale)) + " without freshness marker"
        )
        print("")
        if behind:
            print("BEHIND UPSTREAM")
            for row in behind:
                print("  " + row["skill"] + "  claimed " + str(row["claimed"]) + " -> latest " + str(row["latest"]) + "  (" + str(row["latest_tag"]) + ")")
            print("")
        if benign:
            print("KNOWN-BENIGN DRIFT (already documented in the skill head; do not change the version)")
            for row in benign:
                print("  " + row["skill"] + "  claimed " + str(row["claimed"]) + "  (latest tag " + str(row["latest_tag"]) + ")  " + row.get("reason", ""))
            print("")
        if ambiguous:
            print("AMBIGUOUS TAGS (check by hand, do not trust the number)")
            for row in ambiguous:
                print("  " + row["skill"] + "  repo=" + str(row["repo"]) + "  claimed=" + str(row["claimed"]) + "  " + str(row["latest_tag"]))
            print("")
        if stale:
            print("NO FRESHNESS MARKER (add '截至 YYYY-MM' to the head)")
            for row in stale:
                print("  " + row["skill"])
            print("")
        if unknown:
            print("UNDETERMINED")
            for row in unknown:
                print("  " + row["skill"] + "  repo=" + str(row["repo"]) + "  claimed=" + str(row["claimed"]) + "  latest=" + str(row["latest_tag"]))
        return 1 if behind else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check external links found in SKILL.md / reference files.

Usage: python scripts/check-links.py [--timeout S] [--all]
Reports non-2xx/3xx responses. Concurrency via threads.
"""
import argparse
import concurrent.futures
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

URL_RE = re.compile(r"https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+")
SKIP_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "example.com", "www.example.com"}


def iter_urls(root: Path):
    seen = {}
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in URL_RE.finditer(text):
            url = match.group(0).rstrip(".,;:)")
            host = urllib.parse.urlsplit(url).hostname or ""
            if host in SKIP_HOSTS or host.endswith(".local"):
                continue
            seen.setdefault(url, []).append(path.relative_to(root).as_posix())
    return seen


def check(url, timeout):
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "Mozilla/5.0 (compatible; opengis-skills-link-checker/1.0)",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as resp:
            return url, resp.status, ""
    except urllib.error.HTTPError as exc:
        return url, exc.code, str(exc)
    except Exception as exc:  # noqa: BLE001
        return url, 0, type(exc).__name__ + ": " + str(exc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    urls = iter_urls(root)
    print("checking %d unique external URLs ..." % len(urls))
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check, url, args.timeout) for url in urls]
        for fut in concurrent.futures.as_completed(futures):
            url, status, err = fut.result()
            if 200 <= status < 400:
                if args.all:
                    print("OK   %s %s" % (status, url))
            else:
                failures.append((status, url, err))

    failures.sort(key=lambda item: (-item[0], item[1]))
    print("")
    print("%d problem URLs out of %d:" % (len(failures), len(urls)))
    for status, url, err in failures:
        print("  %4s %s  %s" % (status or "ERR", url, err[:90]))
        for loc in urls[url][:3]:
            print("        in %s" % loc)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

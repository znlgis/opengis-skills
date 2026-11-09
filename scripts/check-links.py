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
SKIP_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "example.com",
    "www.example.com",
    "host.docker.internal",
    "host.containers.internal",
}
PLACEHOLDER_HOSTS = {
    "server",
    "your-server",
    "your-dify",
    "your-host",
    "yourdomain.com",
    "your-domain.com",
    "my-server",
    "host",
    "domain.com",
}
RESERVED_SUFFIXES = (".example.com", ".example.org", ".example.net", ".local", ".invalid", ".test")


INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def inline_code_spans(line):
    """Return (start, end) ranges covered by inline code on this line."""
    return [(m.start(), m.end()) for m in INLINE_CODE_RE.finditer(line)]


def inside_spans(position, spans):
    for start, end in spans:
        if start <= position < end:
            return True
    return False


def iter_urls(root: Path, include_inline_code=False):
    """Collect external URLs that are meant to be clicked.

    URLs written inside inline code are usually API base endpoints
    (for example an API host ending in /v7) rather than pages a reader
    opens, so they are skipped unless include_inline_code is set.
    """
    seen = {}
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        in_code = False
        for line in text.splitlines():
            if line.strip().startswith("```") or line.strip().startswith("~~~"):
                in_code = not in_code
                continue
            if in_code:
                continue
            spans = inline_code_spans(line)
            for match in URL_RE.finditer(line):
                if not include_inline_code and inside_spans(match.start(), spans):
                    continue
                url = match.group(0).rstrip(".,;:)]'\">")
                host = urllib.parse.urlsplit(url).hostname or ""
                if not host or host in SKIP_HOSTS or host in PLACEHOLDER_HOSTS:
                    continue
                if host.endswith(RESERVED_SUFFIXES):
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


def classify(status, err):
    """Split results into broken links versus links this runner cannot verify.

    Anti-bot 403/429, TLS handshake failures and timeouts say nothing about
    whether the URL is valid from a normal browser, so they must not fail the
    check. Only 4xx/5xx that a browser would also hit count as broken.
    """
    if 200 <= status < 400:
        return "ok"
    if status in (401, 403, 405, 406, 429, 451):
        return "blocked"
    if status == 0:
        return "unverifiable"
    if 400 <= status < 500:
        return "broken"
    return "unverifiable"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--all", action="store_true")
    parser.add_argument(
        "--include-inline-code",
        action="store_true",
        dest="include_inline_code",
        help="also probe bare URLs written inside inline code (API base endpoints usually 404 there)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also fail on links the runner could not verify (blocked or network error)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    urls = iter_urls(root, args.include_inline_code)
    print("checking %d unique external URLs ..." % len(urls))
    buckets = {"ok": [], "blocked": [], "unverifiable": [], "broken": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(check, url, args.timeout) for url in urls]
        for fut in concurrent.futures.as_completed(futures):
            url, status, err = fut.result()
            kind = classify(status, err)
            buckets[kind].append((status, url, err))
            if kind == "ok" and args.all:
                print("OK   %s %s" % (status, url))

    def dump(title, rows):
        if not rows:
            return
        rows.sort(key=lambda item: (-item[0], item[1]))
        print("")
        print("%s (%d)" % (title, len(rows)))
        for status, url, err in rows:
            print("  %4s %s  %s" % (status or "ERR", url, err[:90]))
            for loc in urls[url][:3]:
                print("        in %s" % loc)

    dump("BROKEN LINKS", buckets["broken"])
    dump("BLOCKED BY THE SITE (likely fine in a browser)", buckets["blocked"])
    dump("UNVERIFIABLE FROM THIS RUNNER (network/TLS/timeout)", buckets["unverifiable"])

    print("")
    print(
        "%d checked: %d ok, %d broken, %d blocked, %d unverifiable"
        % (
            len(urls),
            len(buckets["ok"]),
            len(buckets["broken"]),
            len(buckets["blocked"]),
            len(buckets["unverifiable"]),
        )
    )
    if buckets["broken"]:
        return 1
    if args.strict and (buckets["blocked"] or buckets["unverifiable"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


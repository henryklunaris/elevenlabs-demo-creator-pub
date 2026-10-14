#!/usr/bin/env python3
"""Scrape a client site's key pages in parallel with Firecrawl v2 and save one markdown file.

Usage: python3 scripts/scrape.py <url> <out_file> [--max-pages 6]
"""

import argparse, json, os, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

API = "https://api.firecrawl.dev/v2"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
KEYWORDS = ["faq", "service", "pricing", "price", "about", "contact", "product", "plan", "hours", "location", "area", "book"]
SKIP = ["blog", "news", "post", "tag", "category", "author", "privacy", "terms", "cookie", "login", "cart", "sitemap", ".xml", ".pdf"]


def get_key():
    key = os.environ.get("FIRECRAWL_API_KEY")
    env_path = os.path.join(ROOT, ".env")
    if not key and os.path.exists(env_path):
        for line in open(env_path):
            if line.strip().startswith("FIRECRAWL_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("Error: FIRECRAWL_API_KEY not set in .env or environment")
    return key


def post(path, body, timeout=60, retries=4):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {get_key()}", "Content-Type": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                time.sleep(3 * (attempt + 1))
                continue
            print(f"Firecrawl error on {path} {body.get('url')}: {e}", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"Firecrawl error on {path} {body.get('url')}: {e}", file=sys.stderr)
        return {}


def pick_pages(url, max_pages):
    links = [l["url"] for l in post("/map", {"url": url, "limit": 200}).get("links", [])]
    host = urlparse(url).netloc
    links = [l for l in links if urlparse(l).netloc == host and not any(s in l.lower() for s in SKIP)]

    def score(l):
        path = urlparse(l).path.lower()
        hits = [i for i, k in enumerate(KEYWORDS) if k in path]
        return (min(hits) if hits else 99, path.count("/"), len(path))

    ranked = [l for l in sorted(set(links), key=score) if score(l)[0] != 99 and l.rstrip("/") != url.rstrip("/")]
    picked, seen = [url], set()
    # First pass: best page per keyword for variety, second pass: fill remaining slots
    for l in ranked:
        k = score(l)[0]
        if k not in seen and len(picked) < max_pages:
            picked.append(l)
            seen.add(k)
    for l in ranked:
        if len(picked) >= max_pages:
            break
        if l not in picked:
            picked.append(l)
    return picked


def scrape(url):
    data = post("/scrape", {"url": url, "formats": ["markdown"], "onlyMainContent": True}).get("data") or {}
    return url, data.get("markdown", "")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("out_file")
    p.add_argument("--max-pages", type=int, default=6)
    a = p.parse_args()

    url = a.url if a.url.startswith("http") else "https://" + a.url
    pages = pick_pages(url, a.max_pages)
    with ThreadPoolExecutor(max_workers=len(pages)) as ex:
        results = list(ex.map(scrape, pages))

    parts = [f"# Source: {u}\n\n{md.strip()}" for u, md in results if md.strip()]
    if not parts:
        sys.exit("Nothing scraped. Check the URL.")
    with open(a.out_file, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(parts))
    total = sum(len(x) for x in parts)
    print(f"Scraped {len(parts)}/{len(pages)} pages, {total} chars -> {a.out_file}")
    for u, md in results:
        print(f"  {'ok ' if md.strip() else 'ERR'} {u}")


if __name__ == "__main__":
    main()

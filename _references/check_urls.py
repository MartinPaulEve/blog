"""Concurrently check which manifest URLs still resolve.

Reads every unique URL in manifest.json and records its verdict in
url_status.json as {"status": <final HTTP status or null>, "final_url": ...}.
HEAD is tried first, falling back to GET when a server rejects HEAD.
Already-checked URLs are skipped, so an interrupted sweep resumes where it
left off. Run from the blog root:

    uv run --with requests _references/check_urls.py
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "manifest.json")
STATUS_FILE = os.path.join(HERE, "url_status.json")

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0"
)
TIMEOUT = 15
WORKERS = 32


def check(url):
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    try:
        response = requests.head(
            url, headers=headers, timeout=TIMEOUT, allow_redirects=True
        )
        # Some servers refuse HEAD (or lie); retry with GET on any 4xx/5xx.
        if response.status_code >= 400:
            response = requests.get(
                url,
                headers=headers,
                timeout=TIMEOUT,
                allow_redirects=True,
                stream=True,
            )
            response.close()
        return {"status": response.status_code, "final_url": response.url}
    except requests.RequestException as exc:
        return {"status": None, "final_url": None, "error": type(exc).__name__}


def main():
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    urls = []
    seen = set()
    for entries in manifest.values():
        for entry in entries:
            if entry["url"] not in seen:
                seen.add(entry["url"])
                urls.append(entry["url"])

    status = {}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, encoding="utf-8") as f:
            status = json.load(f)
    todo = [u for u in urls if u not in status]
    print(f"{len(urls)} unique URLs; {len(todo)} to check", flush=True)

    lock = Lock()
    done = 0

    def flush():
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=0, ensure_ascii=False)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(check, url): url for url in todo}
        for future in as_completed(futures):
            url = futures[future]
            with lock:
                status[url] = future.result()
                done += 1
                if done % 200 == 0:
                    flush()
                    print(f"checked {done}/{len(todo)}", flush=True)
    flush()

    alive = sum(
        1
        for v in status.values()
        if v["status"] is not None
        and (200 <= v["status"] < 400 or v["status"] in (401, 403, 405, 429))
    )
    print(f"done: {len(status)} checked, {alive} alive")
    return 0


if __name__ == "__main__":
    sys.exit(main())

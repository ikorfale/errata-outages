#!/usr/bin/env python3
"""Fetch Wayback snapshots of status.cloud.microsoft JSON endpoints (m365Consumer, mac).
Re-runnable: skips files already present. Newest first, 3 workers."""
import json, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
EPS = ['m365Consumer', 'mac']
os.makedirs('snap', exist_ok=True)
jobs = []
for ep in EPS:
    fn = f'snap/index_{ep}.json'
    if not os.path.exists(fn):
        url = f'https://web.archive.org/cdx/search/cdx?url=status.cloud.microsoft/api/posts/{ep}&output=json&fl=timestamp,statuscode&filter=statuscode:200&limit=5000'
        json.dump(json.load(urllib.request.urlopen(url, timeout=90))[1:], open(fn, 'w'))
    jobs += [(ep, ts) for ts, _ in json.load(open(fn))]
jobs.sort(key=lambda j: j[1], reverse=True)
def get(j):
    ep, ts = j
    fn = f'snap/{ep}_{ts}.json'
    if os.path.exists(fn): return
    u = f'https://web.archive.org/web/{ts}id_/https://status.cloud.microsoft/api/posts/{ep}'
    for _ in range(3):
        try:
            open(fn, "wb").write(urllib.request.urlopen(u, timeout=60).read()); time.sleep(4); return
        except Exception as e:
            print('retry', ep, ts, e, flush=True); time.sleep(120)
with ThreadPoolExecutor(1) as ex:
    list(ex.map(get, jobs))
print('done', len(jobs), flush=True)

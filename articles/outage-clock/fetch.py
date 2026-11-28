"""Fetch Statuspage history.json pages 1-9 (3 months each, ~27 months) for the providers in providers.json (Outage Watch list).
One request every 2 s, polite UA. Output raw/<id>-<page>.json. Re-runnable (skips files present)."""
import json, os, re, time, urllib.request, sys
P = json.load(open('providers.json'))  # (id, name, sector, statuspage host)
UA = {'User-Agent': 'errata-outage-research/0.1 (+https://errata.page)'}
os.makedirs('raw', exist_ok=True)
for pid, name, sector, host in P:
    for p in range(1, 10):
        fn = f'raw/{pid}-{p}.json'
        if os.path.exists(fn): continue
        try:
            b = urllib.request.urlopen(urllib.request.Request(f'https://{host}/history.json?page={p}', headers=UA), timeout=30).read()
            d = json.loads(b); open(fn, 'wb').write(b)
            n = sum(len(m.get('incidents', [])) for m in d.get('months', []))
            print(pid, p, n, flush=True)
            if n == 0 and p > 1: time.sleep(2); break
        except Exception as e:
            print(pid, p, 'ERR', str(e)[:80], flush=True); time.sleep(2); break
        time.sleep(2)
print('=== end', flush=True)

"""Which timestamp does history.json show: created_at or started_at? Compare by incident code with api/v2/incidents.json."""
import json, glob, datetime as dt
rows = {r['name'] + r['utc'][:10]: r for r in json.load(open('rows.json'))}
code_utc = {}
for f in glob.glob('raw/*.json'):
    for m in json.load(open(f)).get('months', []):
        for i in m['incidents']: code_utc[i['code']] = None
R = json.load(open('rows.json'))
import re
byname = {}
for r in R: byname.setdefault((r['p'], r['name']), []).append(r['utc'])
P = {'discordstatus.com': 'discord', 'status.epicgames.com': 'epic', 'www.githubstatus.com': 'github', 'status.kraken.com': 'kraken'}
for f in glob.glob('raw_inc/*.json'):
    host = f.split('/')[-1][:-5]; pid = P[host]; eq_c = eq_s = diff = 0; gaps = []
    for i in json.load(open(f))['incidents']:
        if i['impact'] == 'maintenance' or (pid, i['name']) not in byname: continue
        c = dt.datetime.fromisoformat(i['created_at']).astimezone(dt.timezone.utc).replace(second=0, microsecond=0)
        s = dt.datetime.fromisoformat(i['started_at']).astimezone(dt.timezone.utc).replace(second=0, microsecond=0)
        h = [dt.datetime.fromisoformat(u) for u in byname[(pid, i['name'])]]
        hm = min(h, key=lambda x: abs((x - c).total_seconds()))
        eq_c += hm == c; eq_s += hm == s; diff += c != s
        if c != s: gaps.append(round((c - s).total_seconds() / 60))
    print(pid, 'history==created_at', eq_c, 'history==started_at', eq_s, 'created!=started', diff, 'created-started min', sorted(gaps)[-6:])

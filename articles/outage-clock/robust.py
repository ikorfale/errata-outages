"""Robustness: week-bootstrap CI for weekend-minus-weekday median resolve hours per group; work group without Twilio;
W with weekend defined in UTC instead of HQ-local; per-provider W median."""
import json, random, statistics as st, collections as C, datetime as dt
R = json.load(open('rows.json'))
G = dict(consumer=['discord', 'reddit', 'epic'], work=['zoom', 'atlassian', 'github', 'dropbox', 'box', 'twilio'],
         work_no_twilio=['zoom', 'github', 'dropbox', 'box'], crypto=['coinbase', 'kraken', 'gemini'])
def W(rows, key='wd'):
    wd = sum(r[key] < 5 for r in rows); we = len(rows) - wd; return (wd / 5) / (we / 2) if we else float('inf')
for r in R: r['wdu'] = dt.datetime.fromisoformat(r['utc']).weekday()
def wk(r): return (r['p'], dt.date.fromisoformat(r['utc'][:10]).isocalendar()[:2])
for g, ps in G.items():
    rows = [r for r in R if r['p'] in ps and r['h'] is not None]
    by = C.defaultdict(list)
    for r in rows: by[wk(r)].append(r)
    keys = list(by); rnd = random.Random(2); D = []; Ws = []
    for _ in range(2000):
        s = [x for k in rnd.choices(keys, k=len(keys)) for x in by[k]]
        a = [x['h'] for x in s if x['wd'] >= 5]; b = [x['h'] for x in s if x['wd'] < 5]
        if a and b: D.append(st.median(a) - st.median(b))
        Ws.append(W(s))
    D.sort(); Ws.sort()
    a = [x['h'] for x in rows if x['wd'] >= 5]; b = [x['h'] for x in rows if x['wd'] < 5]
    print(f"{g:15s} n={len(rows)} W={W(rows):.2f} [{Ws[50]:.2f}-{Ws[1949]:.2f}] W_utc={W(rows,'wdu'):.2f}  "
          f"weekend-weekday median h = {st.median(a)-st.median(b):+.2f} [{D[int(.025*len(D))]:+.2f}, {D[int(.975*len(D))]:+.2f}]  "
          f"major share weekday {sum(x['imp'] in ('major','critical') for x in rows if x['wd']<5)/max(1,len(b)):.2f} weekend {sum(x['imp'] in ('major','critical') for x in rows if x['wd']>=5)/max(1,len(a)):.2f}")
pw = {p: W([r for r in R if r['p'] == p]) for p in {r['p'] for r in R} if sum(r['p'] == p for r in R) >= 30}
print('per-provider W (n>=30):', {k: round(v, 2) for k, v in sorted(pw.items(), key=lambda kv: kv[1])})
print('providers with W<=1:', [k for k, v in pw.items() if v <= 1], 'of', len(pw))

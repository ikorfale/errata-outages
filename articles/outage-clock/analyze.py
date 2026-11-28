"""Outage clock analysis per PREREG.md. Input rows.json (parse.py). Week-bootstrap CIs (resample HQ-local ISO weeks)."""
import json, random, statistics as st, collections as C, datetime as dt
from zoneinfo import ZoneInfo
R = json.load(open('rows.json'))
G = dict(consumer=['discord', 'reddit', 'epic'], work=['zoom', 'atlassian', 'github', 'dropbox', 'box', 'twilio'],
         crypto=['coinbase', 'kraken', 'gemini'])
BIG = ('major', 'critical')
def W(rows):
    wd = sum(r['wd'] < 5 for r in rows); we = len(rows) - wd
    return (wd / 5) / (we / 2) if we else float('inf')
def weekkey(r): return (r['p'], dt.date.fromisoformat(r['utc'][:10]).isocalendar()[:2])
def boot(rows, n=2000, seed=1):
    by = C.defaultdict(list)
    for r in rows: by[weekkey(r)].append(r)
    keys = list(by); rnd = random.Random(seed); out = []
    for _ in range(n):
        s = [x for k in rnd.choices(keys, k=len(keys)) for x in by[k]]
        w = W(s); out.append(w)
    out.sort(); return out[int(.025 * n)], out[int(.975 * n)]
print('PROVIDERS present:', sorted(C.Counter(r['p'] for r in R).items()))
for g, ps in G.items():
    rows = [r for r in R if r['p'] in ps]
    if not rows: print(g, 'no data'); continue
    lo, hi = boot(rows)
    sm = [r for r in rows if r['imp'] not in BIG]; bg = [r for r in rows if r['imp'] in BIG]
    print(f"\n== {g}: n={len(rows)}  W={W(rows):.2f} [95% week-bootstrap {lo:.2f}-{hi:.2f}]")
    print(f"   minor/none n={len(sm)} W={W(sm):.2f}   major/critical n={len(bg)} W={W(bg):.2f}" + (f"  [{boot(bg)[0]:.2f}-{boot(bg)[1]:.2f}]" if len(bg) > 20 else ''))
    for p in ps:
        v = [r for r in rows if r['p'] == p]
        if v: print(f"   {p:10s} n={len(v):4d} W={W(v):.2f} since {min(r['utc'][:7] for r in v)}  by day Mon..Sun {[sum(r['wd']==d for r in v) for d in range(7)]}")
    wdr = [r for r in rows if r['wd'] < 5]
    print(f"   weekday starts in 09-17 local: {sum(9 <= r['hr'] < 18 for r in wdr)}/{len(wdr)} ({sum(9 <= r['hr'] < 18 for r in wdr)/len(wdr):.0%}; 9h of 24 = 38% if flat)")
    print('   hour histogram local (0..23):', [sum(r['hr'] == h for r in rows) for h in range(24)])
    hw = [r['h'] for r in rows if r['wd'] < 5 and r['h'] is not None]; he = [r['h'] for r in rows if r['wd'] >= 5 and r['h'] is not None]
    if he: print(f"   median hours to resolve: weekday-start {st.median(hw):.2f} (n={len(hw)})  weekend-start {st.median(he):.2f} (n={len(he)})")
    ow = [r['h'] for r in rows if r['h'] is not None and (r['hr'] < 9 or r['hr'] >= 18 or r['wd'] >= 5)]
    iw = [r['h'] for r in rows if r['h'] is not None and 9 <= r['hr'] < 18 and r['wd'] < 5]
    print(f"   median hours: office-hours start {st.median(iw):.2f} (n={len(iw)})  off-hours start {st.median(ow):.2f} (n={len(ow)})")
oth = [r for r in R if not any(r['p'] in ps for ps in G.values())]
print(f"\nother providers (not in test): n={len(oth)} W={W(oth):.2f}")

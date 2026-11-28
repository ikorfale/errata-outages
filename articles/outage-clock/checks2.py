"""Post-review checks (Fable 28.11), exploratory unless noted: Epic consumer-only rows; collapse same-provider starts
within 3 h; drop impact 'none' and zero-duration rows; Friday and Monday vs Tue-Thu; Saturday vs Sunday."""
import json, re, datetime as dt, collections as C
R = json.load(open('rows.json'))
CONS = re.compile(r'fortnite|rocket league|fall guys|store|launcher|login|log in|sign|account|matchmak|party|friends|purchas|v-bucks|lego|festival|parties|voice|web|epic games', re.I)
DEV = re.compile(r'\bEOS\b|online services|developer|fab\b|sketchfab|uefn|creative|twinmotion|metahuman|publishing|hyperwallet|support-a-creator|forum|unreal|stress test|creator', re.I)
def W(rows): wd = sum(r['wd'] < 5 for r in rows); we = len(rows) - wd; return (wd / 5) / (we / 2) if we else float('inf')
def collapse(rows, hrs=3):
    out, last = [], {}
    for r in sorted(rows, key=lambda r: r['utc']):
        t = dt.datetime.fromisoformat(r['utc'])
        if r['p'] in last and (t - last[r['p']]).total_seconds() < hrs * 3600: continue
        last[r['p']] = t; out.append(r)
    return out
def days(rows): return [sum(r['wd'] == d for r in rows) for d in range(7)]
def prof(rows):
    d = days(rows); mid = sum(d[1:4]) / 3
    return f"n={len(rows)} W={W(rows):.2f} Fri/TueThu={d[4]/mid:.2f} Mon/TueThu={d[0]/mid:.2f} Sat={d[5]} Sun={d[6]}"
epic = [r for r in R if r['p'] == 'epic']
ed = [r for r in epic if DEV.search(r['name'])]; ec = [r for r in epic if not DEV.search(r['name'])]
print('epic dev/creator rows', len(ed), 'W', round(W(ed), 2), '| epic consumer rows', len(ec), 'W', round(W(ec), 2))
print('  sample consumer names:', [r['name'][:40] for r in ec[:8]])
G = dict(consumer_core=(['discord'], ec), work_no_twilio=['zoom', 'github', 'dropbox', 'box'], work=['zoom', 'github', 'dropbox', 'box', 'twilio'],
         crypto=['coinbase', 'kraken', 'gemini'])
for g, v in G.items():
    rows = (v[1] + [r for r in R if r['p'] in v[0]]) if isinstance(v, tuple) else [r for r in R if r['p'] in v]
    real = [r for r in rows if r['imp'] != 'none' and not (r['h'] is not None and r['h'] == 0)]
    print(f"{g:15s} all: {prof(rows)}\n{'':15s} collapsed 3h: {prof(collapse(rows))}\n{'':15s} no none/zero: {prof(real)}\n{'':15s} both: {prof(collapse(real))}")

# Zoom status history (www.zoomstatus.com/history.json pages 1-9, fetched 2026-11-28 ~04:10Z), Sep 2024 - Nov 2026.
# Question: Zoom posts ~3x more incidents than two years ago. Worse service, or more products / more posting?
import json, re, glob, datetime as dt, collections as C, statistics as st
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
def strip(s): return re.sub(r'<[^>]+>', '', s)
def product(n):
    n = n.lower()
    for k, v in [('contact center', 'Contact Center'), ('phone', 'Phone'), ('calling', 'Phone'), ('sms', 'Phone'), ('mms', 'Phone'), ('fax', 'Phone'),
                 ('ai companion', 'AI'), ('zoom ai', 'AI'), ('aic', 'AI'), ('zoommate', 'AI'), ('my notes', 'AI'), ('mynotes', 'AI'), ('docs', 'Workplace apps'),
                 ('rooms', 'Rooms'), ('room connector', 'Rooms'), ('polycom', 'Rooms'), ('webinar', 'Events/Webinars'), ('events', 'Events/Webinars'), ('chat', 'Chat'), ('team chat', 'Chat'),
                 ('meeting', 'Meetings'), ('virtual agent', 'Contact Center'), ('workforce', 'Contact Center'), ('revenue', 'Workplace apps'),
                 ('scheduler', 'Workplace apps'), ('calendar', 'Workplace apps'), ('mail', 'Workplace apps'), ('whiteboard', 'Workplace apps'),
                 ('clips', 'Workplace apps'), ('web portal', 'Web/Account'), ('website', 'Web/Account'), ('webpage', 'Web/Account'), ('sign', 'Web/Account'), ('login', 'Web/Account'),
                 ('marketplace', 'Web/Account'), ('api', 'Web/Account'), ('recording', 'Meetings'), ('webhook', 'Web/Account')]:
        if k in n: return v
    return 'Other'
R = []; NOEND = []
for f in sorted(glob.glob('raw/history-*.json')):
    for m in json.load(open(f))['months']:
        for i in m['incidents']:
            ts = strip(i['timestamp'])  # "Aug 30, 21:18 - 22:51 PDT" or "Aug 30, 21:18 - Aug 31, 01:00 PDT"
            g = re.match(r'(\w{3}) (\d+), (\d+):(\d+) - (?:(\w{3}) (\d+), )?(\d+):(\d+) (\w+)', ts)
            if not g: NOEND.append(ts); continue
            mo, d, h, mi, mo2, d2, h2, mi2, tz = g.groups()
            s = dt.datetime(m['year'], MON[mo], int(d), int(h), int(mi))
            y2 = m['year'] + (1 if mo2 and MON[mo2] < MON[mo] else 0)
            e = dt.datetime(y2, MON[mo2 or mo], int(d2 or d), int(h2), int(mi2))
            if e < s and not mo2: e += dt.timedelta(days=1)  # '23:50 - 00:30' crosses midnight
            R.append(dict(ym=f"{m['year']}-{MON[m['name'][:3]]:02d}", name=i['name'], imp=i['impact'], h=(e - s).total_seconds() / 3600,
                          p=product(i['name'])))
R = [r for r in R if r['imp'] != 'maintenance']
print('entries without an end time (skipped):', len(NOEND))
print('incidents (no maintenance):', len(R), C.Counter(r['imp'] for r in R))
json.dump(R, open('rows.json', 'w'), indent=0)
Y = lambda r: 'A 2024-09..2025-08' if r['ym'] < '2025-09' else ('B 2025-09..2026-08' if r['ym'] < '2026-09' else 'C 2026-09..11')
for k in sorted({Y(r) for r in R}):
    v = [r for r in R if Y(r) == k]; mons = len({r['ym'] for r in v})
    print(f"{k}: months {mons}  per month {len(v)/mons:.1f}  major+critical/month {sum(r['imp'] in ('major','critical') for r in v)/mons:.2f}"
          f"  median h {st.median(r['h'] for r in v):.2f}  Meetings/month {sum(r['p']=='Meetings' for r in v)/mons:.2f}  impact-none share {sum(r['imp']=='none' for r in v)/len(v):.2f}  >4h share {sum(r['h']>4 for r in v)/len(v):.2f}")
    print('    by product /month:', ', '.join(f"{p} {n/mons:.1f}" for p, n in C.Counter(r['p'] for r in v).most_common()))
print('Other names sample:', [r['name'][:60] for r in R if r['p'] == 'Other'][:12])
print('major/critical list:'); [print('  ', r['ym'], r['imp'], f"{r['h']:.1f}h", r['name'][:80]) for r in R if r['imp'] in ('major', 'critical')]
print('negative/zero durations:', sum(r['h'] <= 0 for r in R), ' >24h:', sum(r['h'] > 24 for r in R))
print('zero durations:', sum(r['h'] == 0 for r in R)); print('>24h:'); [print('  ', r['ym'], f"{r['h']:.0f}h", r['name'][:70]) for r in R if r['h'] > 24]
print('per month:', ' '.join(f"{k}:{n}" for k, n in sorted(C.Counter(r['ym'] for r in R).items())))
L12 = [r for r in R if r['ym'] >= '2025-12']
print('last 12 months (2025-12..2026-11):', len(L12))
for p, n in C.Counter(r['p'] for r in L12).most_common():
    h = sorted(r['h'] for r in L12 if r['p'] == p); print(f'   {p:16} n={n:3}  median {st.median(h):.2f} h  >4h {sum(x>4 for x in h)}')
reg = [r for r in R if re.search(r'\b(US|EU|UK|AU|APAC|India|Japan|Canada|Brazil|Singapore|Australia|Germany|region)\b', r['name'], re.I)]
print('names that name a region or "region":', len(reg), 'of', len(R))
allm = sum(len(m['incidents']) for f in glob.glob('raw/history-*.json') for m in json.load(open(f))['months'])
print('history entries incl. maintenance:', allm, ' maintenance+no-end:', allm - len(R))
print('Meetings-named last 12 months:'); [print('  ', r['ym'], r['imp'], f"{r['h']:.1f}h", r['name'][:80]) for r in L12 if r['p'] == 'Meetings']

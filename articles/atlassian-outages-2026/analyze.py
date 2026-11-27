# Atlassian Cloud incidents from the five Statuspage APIs (/api/v2/incidents.json, last 50 each), fetched 2026-11-27 ~15:35Z.
# Question: how often is Jira / Confluence / Bitbucket / JSM / Trello down, how long, and when Jira is down is the rest down too?
# Common window: from the oldest Jira Software incident in the file (the shortest history) to the fetch date.
import json, glob, statistics as st, datetime as dt, collections
P = lambda s: dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
NAME = {'jira-software': 'Jira', 'confluence': 'Confluence', 'bitbucket': 'Bitbucket', 'jira-service-management': 'Jira Service Management', 'trello': 'Trello'}
R = []
for f in sorted(glob.glob('raw/*.json')):
    prod = NAME[f.split('/')[-1].split('.status')[0]]
    for i in json.load(open(f))['incidents']:
        s = P(i['created_at']); e = P(i['resolved_at']) if i.get('resolved_at') else None
        R.append(dict(p=prod, t=i['name'], imp=i['impact'], s=s, h=(e - s).total_seconds() / 3600 if e else None))
W0 = min(r['s'] for r in R if r['p'] == 'Jira'); W1 = dt.datetime(2026, 11, 27, 15, 35, tzinfo=dt.timezone.utc)
wk = (W1 - W0).total_seconds() / 86400 / 7
C = [r for r in R if r['s'] >= W0]
print(f'window {W0:%Y-%m-%d} -> {W1:%Y-%m-%d} ({wk:.1f} weeks); incidents in window: {len(C)}')
for p in NAME.values():
    v = [r for r in C if r['p'] == p]; h = [r['h'] for r in v if r['h'] is not None]
    hi = [r for r in v if r['imp'] in ('major', 'critical')]
    print(f'  {p:24} n={len(v):2}  per week {len(v)/wk:.2f}  median {st.median(h):.2f} h  p75 {sorted(h)[int(.75*len(h))]:.2f} h  major/critical {len(hi)}  >8h {sum(x>8 for x in h)}')
# shared events: incidents on different product pages opened within 30 min of each other
C.sort(key=lambda r: r['s']); groups = []
for r in C:
    for g in groups:
        if abs((r['s'] - g[0]['s']).total_seconds()) <= 1800 and r['p'] not in {x['p'] for x in g}: g.append(r); break
    else: groups.append([r])
sz = collections.Counter(len({x['p'] for x in g}) for g in groups)
print('events (incidents merged across pages within 30 min):', len(groups), ' by number of products:', sorted(sz.items()))
jira = [g for g in groups if any(x['p'] == 'Jira' for x in g)]
print('Jira events:', len(jira), ' also on Confluence:', sum(any(x['p'] == 'Confluence' for x in g) for g in jira),
      ' on 3+ products:', sum(len(g) >= 3 for g in jira))
big = [g for g in groups if len(g) >= 3]
for g in big: print('   ', f"{g[0]['s']:%Y-%m-%d %H:%M}", len(g), '|', g[0]['t'][:80])
print('weekday UTC (events):', collections.Counter(g[0]['s'].strftime('%a') for g in groups).most_common())
print('hour UTC buckets 0-6/6-12/12-18/18-24 (events):', [sum(1 for g in groups if a <= g[0]['s'].hour < a + 6) for a in (0, 6, 12, 18)])
json.dump([dict(p=r['p'], t=r['t'], imp=r['imp'], s=r['s'].isoformat(), h=r['h']) for r in C], open('rows.json', 'w'), indent=1)
print('Jira events also on Jira Service Management:', sum(any(x['p'] == 'Jira Service Management' for x in g) for g in jira))
print('events 00-12 UTC (= 11:00-23:00 Sydney, AEDT):', sum(g[0]['s'].hour < 12 for g in groups), 'of', len(groups))
print('weekend events:', sum(g[0]['s'].weekday() >= 5 for g in groups))

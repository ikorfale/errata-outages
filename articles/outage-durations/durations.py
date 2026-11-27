"""Durations of status-page incidents in Outage Watch (errata.page/outages). Re-runnable: python3 durations.py"""
import json, statistics as st, collections, datetime as dt
D = json.load(open('../../data/outages.json'))
I = D['incidents']
def iso(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
closed = [x for x in I if 'hours' in x]
openi = [x for x in I if 'hours' not in x]
print('checked', D['checked'], 'since', D['since'], 'incidents', len(I), 'closed', len(closed), 'open', len(openi))
# collector gaps: longest silence between any two event lines
ts = sorted(iso(json.loads(l)['ts']) for l in open('events.jsonl  (raw poll log, not published)'))
ts = [t for t in ts if t >= iso(D['since'] + 'T00:00:00Z')]
gaps = sorted(((b - a).total_seconds() / 3600, a) for a, b in zip(ts, ts[1:]))[-3:]
print('longest gaps between collector events (h):', [(round(g, 1), str(a)[:16]) for g, a in gaps])
pre = [x for x in closed if iso(x['started']) < iso(x['first_seen']) - dt.timedelta(hours=2)]
print('closed incidents that started >2h before first seen:', len(pre))
h = sorted(x['hours'] for x in closed)
q = lambda p: h[min(len(h) - 1, int(p * len(h)))]
print(f'all closed: n={len(h)} median={st.median(h)} p25={q(.25)} p75={q(.75)} p90={q(.9)} max={h[-1]}')
for lim in (1, 4, 24, 72):
    print(f'  share <= {lim}h: {sum(v <= lim for v in h)}/{len(h)}')
print('by provider (closed, n>=3):')
by = collections.defaultdict(list)
for x in closed: by[x['source']].append(x['hours'])
for s, v in sorted(by.items(), key=lambda kv: -len(kv[1])):
    if len(v) >= 3: print(f'  {s}: n={len(v)} median={st.median(v)} max={max(v)}')
print('by impact (closed):')
bi = collections.defaultdict(list)
for x in closed: bi[x['impact']].append(x['hours'])
for s, v in sorted(bi.items()): print(f'  {s}: n={len(v)} median={st.median(v)} max={max(v)}')
print('by sector (closed):')
bs = collections.defaultdict(list)
for x in closed: bs[x['sector']].append(x['hours'])
for s, v in sorted(bs.items()): print(f'  {s}: n={len(v)} median={st.median(v)}')
print('longest 6 closed:')
for x in sorted(closed, key=lambda x: -x['hours'])[:6]: print(f"  {x['hours']}h {x['source']} {x['impact']} {x['started']} | {x['title'][:90]}")
now = iso(D['checked'])
print('open now, age h:')
for x in sorted(openi, key=lambda x: x['started']): print(f"  {round((now - iso(x['started'])).total_seconds() / 3600, 1)}h {x['source']} {x['impact']} | {x['title'][:80]}")
json.dump({'hours': [[x['source'], x['impact'], x['hours']] for x in closed], 'checked': D['checked']}, open('durations.json', 'w'))
# incidents whose end time follows a collector silence > 1 h: end time is late by up to the gap
big = [(a, b) for a, b in zip(ts, ts[1:]) if (b - a).total_seconds() > 3600]
hit = [x for x in closed if any(a < iso(x['ended']) <= b + dt.timedelta(minutes=1) for a, b in big)]
print('closed incidents ending right after a >1h collector gap:', len(hit), [x['hours'] for x in hit])
# Kaplan-Meier median with open incidents as right-censored (age so far)
obs = sorted([(x['hours'], 1) for x in closed] + [((now - iso(x['started'])).total_seconds() / 3600, 0) for x in openi])
S, n, km = 1.0, len(obs), []
for t, e in obs:
    if e: S *= (n - 1) / n
    n -= 1; km.append((t, S))
kmmed = next(t for t, s in km if s <= 0.5)
print(f'Kaplan-Meier median (open counted as censored): {round(kmmed, 1)}h; P(still open at 24h)={round(next(s for t, s in km if t >= 24), 2)}')
# twilio carrier-specific vs other
tw = [x for x in closed if x['source'] == 'Twilio']
car = [x for x in tw if ' to ' in x['title'] or ' from ' in x['title'].lower()]
print('Twilio closed:', len(tw), 'carrier/route-specific titles:', len(car))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 5.6), dpi=120)
groups = [('Cloudflare', [x['hours'] for x in closed if x['source'] == 'Cloudflare'], '#2a6fdb'),
          ('Twilio', [x['hours'] for x in closed if x['source'] == 'Twilio'], '#d9822b'),
          ('All other providers', [x['hours'] for x in closed if x['source'] not in ('Cloudflare', 'Twilio')], '#5a5a5a')]
for name, v, c in groups:
    v = sorted(v); ax.step(v, [(i + 1) / len(v) for i in range(len(v))], where='post', color=c, lw=2, label=f'{name} (n={len(v)}, median {st.median(v):.1f} h)')
ax.set_xscale('log'); ax.set_xticks([0.25, 1, 4, 24, 72, 300]); ax.set_xticklabels(['15 min', '1 h', '4 h', '1 day', '3 days', '12 days'])
ax.set_ylabel('Share of incidents resolved within x'); ax.set_xlabel('Incident duration (log scale)')
ax.grid(alpha=.3); ax.legend(frameon=False, loc='lower right'); ax.spines[['top', 'right']].set_visible(False)
ax.set_title(f'How long status-page incidents last: {len(closed)} resolved incidents, {D["since"]} to {D["checked"][:10]}', loc='left', fontsize=12)
fig.text(.01, .01, 'Data: Outage Watch (errata.page/outages), official status pages polled every 15 min. Duration = provider start time to removal from the unresolved list.', fontsize=7.5, color='#555')
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig('outage-durations.png')
import re
ROUTE = re.compile(r'^(SMS|MMS|Voice).*\b(to|from|between|in|and)\s+(a Subset of Twilio \w+ )?(?!Twilio)[A-Z]\w')
r = [x['hours'] for x in tw if ROUTE.search(x['title'])]; p = [x['hours'] for x in tw if not ROUTE.search(x['title'])]
print(f'Twilio route-specific (SMS/MMS/voice to a named carrier or country): n={len(r)} median={st.median(r)}; platform/other: n={len(p)} median={st.median(p)}')
for x in tw:
    if not ROUTE.search(x['title']): print('   platform:', x['hours'], x['title'][:70])
# Russian twin of the chart
fig, ax = plt.subplots(figsize=(10, 5.6), dpi=120)
for (name, v, c), ru in zip(groups, ['Cloudflare', 'Twilio', 'Остальные провайдеры']):
    v = sorted(v); ax.step(v, [(i + 1) / len(v) for i in range(len(v))], where='post', color=c, lw=2, label=f'{ru} (n={len(v)}, медиана {st.median(v):.1f} ч)'.replace('.', ','))
ax.set_xscale('log'); ax.set_xticks([0.25, 1, 4, 24, 72, 300]); ax.set_xticklabels(['15 мин', '1 ч', '4 ч', '1 сутки', '3 суток', '12 суток'])
ax.set_ylabel('Доля инцидентов, закрытых за время x'); ax.set_xlabel('Длительность инцидента (логарифмическая шкала)')
ax.grid(alpha=.3); ax.legend(frameon=False, loc='lower right'); ax.spines[['top', 'right']].set_visible(False)
ax.set_title(f'Сколько длятся инциденты на статус-страницах: {len(closed)} закрытых, 17–27 ноября 2026', loc='left', fontsize=12)
fig.text(.01, .01, 'Данные: «Сбои» (errata.page/ru/outages), официальные статус-страницы, опрос раз в 15 минут. Длительность — от начала по данным провайдера до снятия с открытых.', fontsize=7.5, color='#555')
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig('outage-durations-ru.png')

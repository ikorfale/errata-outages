"""Cloudflare status-page incidents in Outage Watch, Nov 2026: groups, durations, timeline chart. python3 cf.py"""
import json, re, statistics as st, datetime as dt, collections
D = json.load(open('../../data/outages.json'))
def iso(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
now = iso(D['checked'])
cf = sorted([x for x in D['incidents'] if x['source'] == 'Cloudflare'], key=lambda x: x['started'])
G = [('Network / data centre', r'Network|connectivity|colocation|Magic Transit|5xx|datacenter'),
     ('Developer platform (R2, Workers, Durable Objects, AI)', r'R2|Durable|Workers|D1|models|AI Gateway|Observability|RealTimeKit'),
     ('Dashboard, API and config', r'Dashboard|Access|Firewall|monitors|Analytics|Purg'),
     ('Other', r'.')]
def grp(t): return next(g for g, rx in G if re.search(rx, t))
since = iso(D['since'] + 'T00:00:00Z')
inwin = [x for x in cf if iso(x['started']) >= since]
print('Cloudflare incidents in log:', len(cf), '| started on/after', D['since'], ':', len(inwin), '| checked', D['checked'])
days = (now - since).total_seconds() / 86400
print(f'window {days:.1f} days -> {len(inwin)/days:.1f} new incidents a day')
print('impact:', collections.Counter(x['impact'] for x in cf))
by = collections.defaultdict(list)
for x in cf: by[grp(x['title'])].append(x)
for g, _ in G:
    v = by[g]; h = [x['hours'] for x in v if 'hours' in x]
    print(f'{g}: n={len(v)} closed={len(h)} median={st.median(h) if h else None} max={max(h) if h else None}')
    for x in v: print('    ', x['started'][5:16], x.get('hours'), x['impact'], x['title'].strip()[:70])
h = [x['hours'] for x in cf if 'hours' in x]
print(f'all closed: n={len(h)} median={st.median(h)} over 10h: {sum(v > 10 for v in h)}')
r2 = [x for x in cf if re.search(r'\bR2\b', x['title'])]; print('R2 incidents:', len(r2), 'South America R2:', sum('South America' in x['title'] for x in r2))
hr = collections.Counter(iso(x['started']).hour // 6 for x in inwin); print('start hour UTC buckets 0-5,6-11,12-17,18-23:', [hr[i] for i in range(4)])
op = [x for x in cf if 'hours' not in x]
for x in op: print('open:', x['title'], 'age h', round((now - iso(x['started'])).total_seconds() / 3600, 1))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as md
col = dict(zip([g for g, _ in G], ['#2a6fdb', '#d9822b', '#7a4fbf', '#777']))
for lang in ('en', 'ru'):
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=120)
    rows = inwin
    for i, x in enumerate(rows):
        s = iso(x['started']); e = iso(x['ended']) if 'ended' in x else now
        ax.barh(i, (e - s).total_seconds() / 86400, left=md.date2num(s), color=col[grp(x['title'])], height=.7,
                edgecolor='black' if x['impact'] == 'major' else 'none', lw=1.2)
        ax.text(md.date2num(e) + .05, i, x['title'].strip()[:48], va='center', fontsize=6.5, color='#333')
    ax.invert_yaxis(); ax.set_yticks([]); ax.xaxis.set_major_locator(md.DayLocator()); ax.xaxis.set_major_formatter(md.DateFormatter('%d.%m'))
    ax.set_xlim(md.date2num(since), md.date2num(now) + 2.2); ax.spines[['top', 'right', 'left']].set_visible(False); ax.grid(axis='x', alpha=.3)
    lab = {'en': list(col), 'ru': ['Сеть и дата-центры', 'Платформа разработчиков (R2, Workers, Durable Objects, ИИ)', 'Панель, API и настройки', 'Другое']}[lang]
    from matplotlib.patches import Patch
    hs = [Patch(color=c, label=l) for c, l in zip(col.values(), lab)] + [Patch(facecolor='white', edgecolor='black', label={'en': 'black outline: labelled "major"', 'ru': 'чёрная рамка: пометка major'}[lang])]
    ax.legend(handles=hs, frameon=False, loc='lower left', fontsize=8)
    ax.set_xticks([md.date2num(since + dt.timedelta(days=d)) for d in range(11)])
    ax.set_title({'en': f'Cloudflare status-page incidents, 17-27 Nov 2026: {len(inwin)} incidents, bar = duration',
                  'ru': f'Инциденты на статус-странице Cloudflare, 17–27.11.2026: {len(inwin)}, полоса = длительность'}[lang], loc='left', fontsize=11)
    fig.text(.01, .01, {'en': 'Data: Outage Watch (errata.page/outages), cloudflarestatus.com polled every 15 min. Times UTC.',
                        'ru': 'Данные: «Сбои» (errata.page/ru/outages), cloudflarestatus.com, опрос раз в 15 минут. Время UTC.'}[lang], fontsize=7.5, color='#555')
    fig.tight_layout(rect=(0, .02, 1, 1)); fig.savefig(f'./cloudflare-incidents-november-2026{"-ru" if lang == "ru" else ""}.png')

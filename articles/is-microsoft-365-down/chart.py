#!/usr/bin/env python3
"""Strip chart: every archived snapshot of the public M365 status API, normal vs showing an issue."""
import csv, sys, datetime as dt, matplotlib
RU = len(sys.argv) > 1 and sys.argv[1] == 'ru'
T = (lambda en, ru: ru if RU else en)
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as md
rows = list(csv.DictReader(open('snapshots.csv')))
P = lambda t: dt.datetime.strptime(t, '%Y%m%d%H%M%S')
fig, ax = plt.subplots(figsize=(12, 3.6), dpi=110)
lab = {'m365Consumer': T('Consumer services', 'Личные сервисы') + '\n(/api/posts/m365Consumer)', 'mac': T('Admin-center fallback', 'Запасная заметка\nо центре администрирования') + '\n(/api/posts/mac)'}
for i, ep in enumerate(['mac', 'm365Consumer']):
    for issue, c, z, name in [('none', '#9aa3ad', 2, T('nothing reported', 'ничего не сообщалось')), ('restored', '#e59866', 3, T('"service restored" notice', '«сервис восстановлен»')), ('active', '#c0392b', 4, T('active issue', 'активная проблема'))]:
        xs = [P(r['ts']) for r in rows if r['endpoint'] == ep and r['issue'] == issue]
        ax.scatter(xs, [i] * len(xs), s=46, marker='|' if issue == 'none' else 'o', c=c, zorder=z, linewidths=1.6,
                   label=name if i == 0 else None)
ax.axvspan(dt.datetime(2026, 11, 12, 16, 20), dt.datetime(2026, 11, 13, 16, 10), color='#c0392b', alpha=.12, lw=0)
ax.annotate(T('12-13 Nov 2026 outage\n(23 h 50 min)', 'Сбой 12–13 ноября 2026\n(23 ч 50 мин)'), (dt.datetime(2026, 11, 13), 1.32), ha='right', fontsize=9, color='#7b241c')
ax.set_yticks([0, 1], [lab['mac'], lab['m365Consumer']]); ax.set_ylim(-.6, 1.7)
ax.xaxis.set_major_formatter(md.DateFormatter('%m.%Y' if RU else '%b %Y'))
for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
ax.tick_params(axis='y', length=0); ax.grid(axis='x', color='#eee')
ax.legend(loc='upper left', frameon=False, ncol=3, fontsize=9)
ax.set_title(T('What the public Microsoft 365 status page showed in every Internet Archive snapshot', 'Что показывала публичная страница статуса Microsoft 365 в каждой копии Internet Archive'), loc='left', fontsize=11)
fig.text(.01, .01, T('Data: Wayback Machine snapshots of status.cloud.microsoft JSON API. Chart: errata.page', 'Данные: копии JSON API status.cloud.microsoft в Wayback Machine. График: errata.page'), fontsize=8, color='#666')
fig.tight_layout(rect=(0, .04, 1, 1)); fig.savefig('m365-public-status-page-snapshots' + ('-ru' if RU else '') + '.png')

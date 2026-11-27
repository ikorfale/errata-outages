import json, datetime as dt, random
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R = json.load(open('rows.json')); random.seed(1)
for lang in ('en', 'ru'):
    L = dict(en=dict(days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], x='Hour the incident was opened (UTC)', band='8:00–19:00 in New York (UTC−5)',
                     hi='critical or major', lo='minor or none', t='GitHub incidents, 6 Oct – 25 Nov 2026: 49 of 50 opened on a weekday, 37 between 8:00 and 19:00 New York time',
                     src='Data: githubstatus.com incidents API (last 50 incidents), fetched 27 Nov 2026. errata.page'),
             ru=dict(days=['Пн','Вт','Ср','Чт','Пт','Сб','Вс'], x='Час открытия инцидента (UTC)', band='8:00–19:00 по Нью-Йорку (UTC−5)',
                     hi='critical или major', lo='minor или none', t='Инциденты GitHub, 6 октября – 25 ноября 2026: 49 из 50 открыты в будни, 37 — с 8 до 19 по Нью-Йорку',
                     src='Данные: API инцидентов githubstatus.com (последние 50), 27.11.2026. errata.page'))[lang]
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=120)
    ax.axvspan(13, 24, color='#f3e3cf', zorder=0, label=L['band'])
    for r in R:
        t = dt.datetime.fromisoformat(r['start']); x = t.hour + t.minute/60; y = t.weekday() + random.uniform(-.2, .2)
        hi = r['impact'] in ('critical', 'major')
        ax.scatter(x, y, s=46, color='#b5471b' if hi else '#6b6b6b', alpha=.9, zorder=3, edgecolor='white', lw=.6)
    ax.scatter([], [], s=46, color='#b5471b', label=L['hi']); ax.scatter([], [], s=46, color='#6b6b6b', label=L['lo'])
    ax.set_yticks(range(7)); ax.set_yticklabels(L['days']); ax.invert_yaxis(); ax.set_xlim(0, 24); ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel(L['x']); ax.grid(axis='x', alpha=.3); ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.legend(frameon=False, loc='lower left', fontsize=8.5, ncol=3, bbox_to_anchor=(0, -.33))
    ax.set_title(L['t'], loc='left', fontsize=11)
    fig.text(.01, .01, L['src'], fontsize=7.5, color='#555')
    fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(f'github-incidents-{lang}.png')
print('ok')

import json, collections as C
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R = json.load(open('rows.json')); M = sorted({r['ym'] for r in R})
cnt = {k: C.Counter(r['ym'] for r in R if (r['imp'] if r['imp'] in ('none', 'minor') else 'big') == k) for k in ('none', 'minor', 'big')}
T = dict(en=dict(t='Zoom posts twice as many status incidents as in 2024-25, but almost none are major',
                 l=['no impact flag', 'minor', 'major or critical'], y='incidents per month',
                 s='Data: zoomstatus.com history (443 incidents, maintenance excluded), Sep 2024 - 28 Nov 2026. errata.page'),
         ru=dict(t='Zoom публикует вдвое больше инцидентов, чем в 2024-25, но крупных почти нет',
                 l=['без оценки влияния', 'незначительный', 'крупный или критический'], y='инцидентов в месяц',
                 s='Данные: история zoomstatus.com (443 инцидента без плановых работ), сен 2024 - 28 ноя 2026. errata.page'))
for lang, L in T.items():
    fig, ax = plt.subplots(figsize=(10, 4.4), dpi=120); b = [0] * len(M)
    for k, col, lab in zip(('none', 'minor', 'big'), ('#b9cbe0', '#2f5d8a', '#c0392b'), L['l']):
        v = [cnt[k][m] for m in M]; ax.bar(range(len(M)), v, bottom=b, color=col, label=lab, width=.8); b = [x + y for x, y in zip(b, v)]
    ax.set_xticks(range(0, len(M), 3)); ax.set_xticklabels([M[i] for i in range(0, len(M), 3)], fontsize=8)
    ax.set_ylabel(L['y']); ax.legend(frameon=False, fontsize=9, loc='upper left'); ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', alpha=.3); ax.set_title(L['t'], loc='left', fontsize=10.5)
    fig.text(.01, .01, L['s'] + (' (Nov 2026 partial)' if lang == 'en' else ' (ноябрь 2026 неполный)'), fontsize=7, color='#555')
    fig.tight_layout(rect=(0, .04, 1, 1)); fig.savefig(f'zoom-incidents-{lang}.png')
print('ok')

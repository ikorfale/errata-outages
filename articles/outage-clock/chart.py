"""Chart: incidents posted per weekday, indexed to the Tue-Thu mean = 1, for three load groups."""
import json, re
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R = json.load(open('rows.json'))
DEV = re.compile(r'\bEOS\b|online services|developer|fab\b|sketchfab|uefn|creative|twinmotion|metahuman|publishing|hyperwallet|support-a-creator|forum|unreal|stress test|creator', re.I)
G = [('cons', lambda r: r['p'] == 'discord' or (r['p'] == 'epic' and not DEV.search(r['name'])), '#c0392b'),
     ('work', lambda r: r['p'] in ('zoom', 'github', 'dropbox', 'box', 'twilio'), '#2f5d8a'),
     ('cryp', lambda r: r['p'] in ('coinbase', 'kraken', 'gemini'), '#d4a017')]
T = dict(en=dict(t='Status incidents follow the work week, even where users peak at weekends',
                 d='Mon Tue Wed Thu Fri Sat Sun'.split(), y='incidents posted per day\n(Tue-Thu average = 1)',
                 l=dict(cons='Discord + Fortnite/Epic store (weekend-heavy users)', work='Zoom, GitHub, Dropbox, Box, Twilio (work tools)', cryp='Coinbase, Kraken, Gemini (24/7 trading)'),
                 s='Data: Statuspage history of 9,911 incidents, Sep 2024 - Nov 2026, day in each company\'s home time zone. errata.page'),
         ru=dict(t='Инциденты следуют рабочей неделе, даже там, где пользователи активнее в выходные',
                 d='Пн Вт Ср Чт Пт Сб Вс'.split(), y='инцидентов в день\n(среднее Вт-Чт = 1)',
                 l=dict(cons='Discord + Fortnite/магазин Epic (пик пользователей в выходные)', work='Zoom, GitHub, Dropbox, Box, Twilio (рабочие сервисы)', cryp='Coinbase, Kraken, Gemini (торги 24/7)'),
                 s='Данные: история Statuspage, 9911 инцидентов, сен 2024 - ноя 2026, день по часовому поясу штаб-квартиры. errata.page'))
for lang, L in T.items():
    fig, ax = plt.subplots(figsize=(10, 5.25), dpi=120)
    for k, f, col in G:
        rows = [r for r in R if f(r)]; d = [sum(r['wd'] == i for r in rows) for i in range(7)]; mid = sum(d[1:4]) / 3
        v = [x / mid for x in d]
        ax.plot(range(7), v, marker='o', color=col, lw=2.2, label=f"{L['l'][k]}  (n={len(rows)})")
    ax.axvspan(4.5, 6.5, color='#eee', zorder=0)
    ax.set_xticks(range(7)); ax.set_xticklabels(L['d']); ax.set_ylim(0, 1.25); ax.set_ylabel(L['y'])
    ax.spines[['top', 'right']].set_visible(False); ax.grid(axis='y', alpha=.3)
    ax.legend(frameon=False, fontsize=9, loc='lower left'); ax.set_title(L['t'], loc='left', fontsize=11)
    fig.text(.01, .01, L['s'], fontsize=7.5, color='#555'); fig.tight_layout(rect=(0, .04, 1, 1))
    fig.savefig(f"status-incidents-by-weekday{'-ru' if lang == 'ru' else ''}.png")
print('ok')

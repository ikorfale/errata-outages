import json, datetime as dt, statistics as st, random
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R = [r for r in json.load(open('rows.json')) if r['start'] >= '2026-11-17']
FETCH = dt.datetime(2026, 11, 27, 10, 40, tzinfo=dt.timezone.utc)
def hrs(r):
    if r['hours'] is not None: return r['hours'], False
    return (FETCH - dt.datetime.fromisoformat(r['start'])).total_seconds() / 3600, True
random.seed(1)
for lang in ('en', 'ru'):
    L = dict(en=dict(rows=['Platform-wide\n(API, console, email, signing)', 'Route-specific\n(one country or carrier)'], x='Incident duration, log scale', open='still open at 10:40 UTC 27 Nov (age so far)', med='median of resolved', t='Twilio incidents 17–27 Nov 2026: carrier routes outnumber platform problems and last longer', src='Data: status.twilio.com incidents API, fetched 27 Nov 2026; Outage Watch (errata.page/outages). Route-specific = the title names a country.',
                      ticks=['15 min', '1 h', '4 h', '1 day', '3 days', '9 days']),
             ru=dict(rows=['Общие для платформы\n(API, консоль, почта, подпись)', 'Отдельный маршрут\n(одна страна или оператор)'], x='Длительность инцидента, логарифмическая шкала', open='ещё открыт в 10:40 UTC 27.11 (возраст)', med='медиана закрытых', t='Инциденты Twilio 17–27 ноября 2026: сбоев на маршрутах к операторам больше, и они дольше', src='Данные: API инцидентов status.twilio.com, 27.11.2026; «Сбои» (errata.page/ru/outages). Отдельный маршрут — в заголовке названа страна.',
                      ticks=['15 мин', '1 ч', '4 ч', '1 сутки', '3 суток', '9 суток']))[lang]
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=120)
    for y, flag, c in ((0, False, '#5a5a5a'), (1, True, '#d9822b')):
        g = [r for r in R if r['route'] == flag]
        closed = [hrs(r)[0] for r in g if not hrs(r)[1]]
        for r in g:
            h, op = hrs(r); jy = y + random.uniform(-.18, .18)
            ax.scatter(h, jy, s=38, facecolor='none' if op else c, edgecolor=c, lw=1.4, zorder=3)
        m = st.median(closed); ax.plot([m, m], [y - .3, y + .3], color=c, lw=2.5)
        ax.text(m, y + .34, f"{L['med']} {m:.1f} h".replace('.', ',') if lang == 'ru' else f"{L['med']} {m:.1f} h", ha='center', fontsize=8.5, color=c)
    ax.scatter([], [], s=38, facecolor='none', edgecolor='#333', label=L['open']); ax.legend(frameon=False, loc='lower right', fontsize=8.5)
    ax.set_xscale('log'); ax.set_xticks([.25, 1, 4, 24, 72, 216]); ax.set_xticklabels(L['ticks'])
    ax.set_yticks([0, 1]); ax.set_yticklabels([f"{L['rows'][0]}\nn={sum(not r['route'] for r in R)}", f"{L['rows'][1]}\nn={sum(r['route'] for r in R)}"])
    ax.set_ylim(-.5, 1.6); ax.set_xlabel(L['x']); ax.grid(axis='x', alpha=.3); ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.set_title(L['t'], loc='left', fontsize=11.5)
    fig.text(.01, .01, L['src'], fontsize=7.5, color='#555')
    fig.tight_layout(rect=(0, .04, 1, 1)); fig.savefig(f'twilio-carrier-{lang}.png')
print('ok')

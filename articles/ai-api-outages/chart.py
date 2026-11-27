import json, datetime as dt, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as md
from matplotlib.patches import Patch
d = json.load(open('ai_incidents.json')); P = lambda s: dt.datetime.fromisoformat(s)
end = P('2026-11-27 00:00:00+00:00'); m365 = (P('2026-11-12 16:20:00+00:00'), P('2026-11-13 16:10:00+00:00'))
C = {'critical': '#8b0000', 'major': '#d9482b', 'minor': '#e8a33d', 'none': '#9a9a9a'}
for lang in ('en', 'ru'):
    fig, axs = plt.subplots(2, 1, figsize=(10, 8.4), dpi=120, sharex=True, gridspec_kw={'height_ratios': [16, 21]})
    for ax, name in zip(axs, ['Anthropic', 'OpenAI']):
        rows = sorted(d[name], key=lambda r: r['start'])
        ax.axvspan(md.date2num(m365[0]), md.date2num(m365[1]), color='#2a6fdb', alpha=.12)
        for i, r in enumerate(rows):
            s = P(r['start']); e = P(r['resolved']) if r['resolved'] != 'None' else end
            w = max((e - s).total_seconds() / 86400, .04)
            ax.barh(i, w, left=md.date2num(s), color=C[r['impact']], height=.7, hatch='///' if r['resolved'] == 'None' else None)
            ax.text(md.date2num(s) + w + .1, i, ('[backfilled] ' if r['backfill'] else '') + r['name'][:52], va='center', fontsize=6.3, color='#333')
        ax.invert_yaxis(); ax.set_yticks([]); ax.spines[['top', 'right', 'left']].set_visible(False); ax.grid(axis='x', alpha=.3)
        ax.set_title({'en': f'{name}: {len(rows)} incidents', 'ru': f'{name}: {len(rows)} инцидентов' if name == 'OpenAI' else f'{name}: {len(rows)} инцидентов'}[lang], loc='left', fontsize=10.5)
    axs[1].xaxis.set_major_locator(md.DayLocator(interval=2)); axs[1].xaxis.set_major_formatter(md.DateFormatter('%d.%m'))
    axs[1].set_xlim(md.date2num(P('2026-11-01 00:00:00+00:00')), md.date2num(end) + 4)
    lab = {'en': ['critical', 'major', 'minor', 'none (provider label)', 'Microsoft 365 outage, 12-13 Nov'], 'ru': ['critical', 'major', 'minor', 'none (пометка провайдера)', 'сбой Microsoft 365, 12–13 ноября']}[lang]
    hs = [Patch(color=c, label=l) for c, l in zip(C.values(), lab)] + [Patch(color='#2a6fdb', alpha=.12, label=lab[4])]
    axs[1].legend(handles=hs, frameon=False, loc='lower left', fontsize=8)
    fig.suptitle({'en': 'Anthropic and OpenAI status-page incidents, 1-26 November 2026 (bar = duration, UTC)', 'ru': 'Инциденты на статус-страницах Anthropic и OpenAI, 1–26 ноября 2026 (полоса = длительность, UTC)'}[lang], x=.01, ha='left', fontsize=11.5)
    fig.text(.01, .005, {'en': 'Data: status.claude.com and status.openai.com incident APIs, fetched 27 Nov 2026. Titles are the providers\' own. Hatched = still open.', 'ru': 'Данные: API инцидентов status.claude.com и status.openai.com, скачано 27.11.2026. Заголовки — провайдеров. Штриховка — ещё открыт.'}[lang], fontsize=7.5, color='#555')
    fig.tight_layout(rect=(0, .02, 1, .97)); fig.savefig(f'./anthropic-openai-incidents-november-2026{"-ru" if lang == "ru" else ""}.png')

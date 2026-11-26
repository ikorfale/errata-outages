"""Durations of 136 official status-page incidents (my log, 17-26 Nov 2026) vs the Microsoft 365 outage of 12-13 Nov (23 h 50 min, Microsoft's PIR)."""
import json, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = json.load(open(sys.argv[3] if len(sys.argv) > 3 else 'data/outages.json'))
R = [r for r in d['incidents'] if 'hours' in r]
h = np.array([r['hours'] for r in R]); hb = np.array([r['hours'] for r in R if r['impact'] in ('major', 'critical')]); hm = np.array([r['hours'] for r in R if r['impact'] not in ('major', 'critical')])
lang = sys.argv[1]; out = sys.argv[2]
L = {'en': ('Duration of resolved incidents (hours, log scale)', 'incidents', f'{len(h)} resolved incidents on 29 status pages, 17–26 Nov 2026', 'Microsoft 365, 12–13 Nov: 23 h 50 min', 'median {:.1f} h'),
     'ru': ('Длительность решённых инцидентов (часы, лог. шкала)', 'инцидентов', f'{len(h)} решённых инцидентов на 29 статус-страницах, 17–26 ноября 2026', 'Microsoft 365, 12–13 ноября: 23 ч 50 мин', 'медиана {:.1f} ч')}[lang]
fig, ax = plt.subplots(figsize=(10, 5.2), dpi=120)
fig.patch.set_facecolor('#f6f3ec'); ax.set_facecolor('#f6f3ec')
bins = np.logspace(np.log10(0.05), np.log10(400), 28)
LB = {'en': ('minor (provider\'s label)', 'major or critical'), 'ru': ('малые (метка компании)', 'крупные или критические')}[lang]
ax.hist([hm, hb], bins=bins, stacked=True, color=['#b9b2a5', '#1f3a5f'], edgecolor='#f6f3ec', label=list(LB)); ax.legend(frameon=False, loc='center right')
ax.set_xscale('log'); ax.set_xlabel(L[0]); ax.set_ylabel(L[1])
ax.axvline(23.83, color='#a8322d', lw=2); ax.text(23.83 * 1.08, ax.get_ylim()[1] * 0.9, L[3], color='#a8322d', fontsize=11, va='top')
med = np.median(h); ax.axvline(med, color='#333', lw=1, ls='--'); ax.text(med / 1.08, ax.get_ylim()[1] * 0.97, ha='right', s= L[4].format(med).replace('.', ',' if lang == 'ru' else '.'), fontsize=10)
ax.set_xticks([0.1, 0.5, 1, 3, 10, 24, 100]); ax.set_xticklabels(['0.1', '0.5', '1', '3', '10', '24', '100'])
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.set_title(L[2], loc='left', fontsize=12)
fig.tight_layout(); fig.savefig(out)
print(lang, 'n', len(h), 'median', round(med, 2), 'longer than 23.83h:', int((h > 23.83).sum()), 'major/critical n', len(hb), 'median', np.median(hb), 'max', hb.max(), 'max', h.max())

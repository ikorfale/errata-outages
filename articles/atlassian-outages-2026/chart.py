import json, statistics as st
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R = json.load(open('rows.json')); WK = 46.5
P = ['Jira', 'Jira Service Management', 'Confluence', 'Bitbucket', 'Trello']
for lang in ('en', 'ru'):
    L = dict(en=dict(x='Status-page incidents per week, 6 Jan – 27 Nov 2026', med='median {:.1f} h', names=P,
                     t='Atlassian Cloud status incidents in 2026: about one a week for Jira and for JSM',
                     src='Data: Atlassian Statuspage incident APIs (last 50 per product), fetched 27 Nov 2026. Shared incidents count on every page that posted them. errata.page'),
             ru=dict(x='Инцидентов на странице статуса в неделю, 6 января – 27 ноября 2026', med='медиана {:.1f} ч',
                     names=['Jira', 'Jira Service Management', 'Confluence', 'Bitbucket', 'Trello'],
                     t='Инциденты Atlassian Cloud в 2026: у Jira и у JSM около одного в неделю',
                     src='Данные: API страниц статуса Atlassian (последние 50 по каждому продукту), 27.11.2026. Общий инцидент считается на каждой странице. errata.page'))[lang]
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=120)
    for k, p in enumerate(P):
        v = [r for r in R if r['p'] == p]; h = [r['h'] for r in v if r['h'] is not None]
        ax.barh(k, len(v) / WK, color='#2f5d8a', height=.6)
        ax.text(len(v) / WK + .02, k, f"{len(v)}  ·  " + L['med'].format(st.median(h)), va='center', fontsize=9, color='#333')
    ax.set_yticks(range(len(P))); ax.set_yticklabels(L['names']); ax.invert_yaxis(); ax.set_xlim(0, 1.45)
    ax.set_xlabel(L['x']); ax.spines[['top', 'right']].set_visible(False); ax.grid(axis='x', alpha=.3)
    ax.set_title(L['t'], loc='left', fontsize=10.5)
    fig.text(.01, .01, L['src'], fontsize=7, color='#555')
    fig.tight_layout(rect=(0, .04, 1, 1)); fig.savefig(f'atlassian-{lang}.png')
print('ok')

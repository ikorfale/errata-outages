import re,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows=[l.split() for l in open('placebo.out') if ' shift ' in l]
data={}
for r in rows:
    g,sh,l=r[0],int(r[2]),r[-1]
    data.setdefault(g,{})[sh]=float(l) if l!='nan' else None
L={'en':dict(t='Wikipedia pageview spikes on the day a status page declares a major incident',
   s='Lift = P(spike on incident day) / P(spike on a quiet day). Dates shifted by ±7 and ±14 days are placebos.',
   x='Incident dates shifted by (days)',y='Lift (1 = no effect)',
   g={'anthropic':'Claude (Anthropic)','github':'GitHub','rest':'16 other providers'}),
   'ru':dict(t='Всплески просмотров Википедии в день крупного инцидента на статус-странице',
   s='Подъём = P(всплеск в день инцидента) / P(всплеск в спокойный день). Сдвиг на ±7 и ±14 дней — плацебо.',
   x='Даты инцидентов сдвинуты на (дней)',y='Подъём (1 = эффекта нет)',
   g={'anthropic':'Claude (Anthropic)','github':'GitHub','rest':'16 остальных сервисов'})}
C={'anthropic':'#c2410c','github':'#1d4ed8','rest':'#525252'}
for lang,t in L.items():
    fig,ax=plt.subplots(figsize=(12,6.3),dpi=100)
    for g in ('anthropic','github','rest'):
        xs=[s for s in sorted(data[g]) if data[g][s] is not None]; ys=[data[g][s] for s in xs]
        ax.plot(xs,ys,'-o',color=C[g],lw=2.5 if g=='rest' else 2,label=t['g'][g])
        ax.annotate(f"{data[g][0]:.2f}",(0,data[g][0]),textcoords='offset points',xytext=(8,4),color=C[g],fontsize=11)
    ax.axhline(1,color='#a3a3a3',lw=1,ls='--'); ax.axvspan(-1,1,color='#f5f5f5',zorder=0)
    ax.set_xticks([-14,-7,0,7,14]); ax.set_xlabel(t['x'],fontsize=12); ax.set_ylabel(t['y'],fontsize=12)
    for sp in ('top','right'): ax.spines[sp].set_visible(False)
    ax.legend(frameon=False,fontsize=12,loc='upper right')
    fig.suptitle(t['t'],fontsize=15,x=0.06,ha='left',y=0.97); ax.set_title(t['s'],fontsize=11,loc='left',color='#525252')
    fig.text(0.06,0.015,'en.wikipedia daily views (user agent), 2024-08 to 2026-11; Statuspage histories. errata.page' ,fontsize=9,color='#737373')
    fig.tight_layout(rect=(0,0.03,1,0.94))
    fig.savefig('wikipedia-pageviews-vs-outages'+('' if lang=='en' else '-ru')+'.png'); print(lang)

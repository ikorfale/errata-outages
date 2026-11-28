# Chart: ratio of incident rate on volatile vs calm BTC days, under three comparisons (EN + RU).
import json, re, datetime as dt, collections, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
inc=json.load(open('incidents_clean.json')); C=json.load(open('controls.json'))
btc={dt.datetime.fromtimestamp(int(r[0]),dt.timezone.utc).date():(float(r[2])-float(r[3]))/float(r[1]) for r in json.load(open('btc_daily.json'))}
days=sorted(d for d in btc if dt.date(2024,12,8)<=d<=dt.date(2026,11,27)); v=sorted(btc[d] for d in days); q20,q80=v[len(v)//5],v[4*len(v)//5]
lo=[d for d in days if btc[d]<=q20]; hi=[d for d in days if btc[d]>=q80]; LOAD=re.compile(r'load|volume|connectivity|latenc|degraded|unavailable|downtime|outage',re.I)
G={'platform':lambda x:x['kind']=='platform','funding':lambda x:x['kind']=='funding','load/connectivity words':lambda x:x['kind']=='platform' and LOAD.search(x['name'])}
naive={}
for g,f in G.items():
    c=collections.Counter(x['day'] for x in inc if f(x)); naive[g]=(sum(c.get(str(d),0) for d in hi)/len(hi))/(sum(c.get(str(d),0) for d in lo)/len(lo))
print('naive',{g:round(v,2) for g,v in naive.items()}, 'n load',sum(1 for x in inc if G['load/connectivity words'](x)))
rat={'naive':naive}; [rat.setdefault(r['control'],{}).__setitem__(r['group'],r['ratio']) for r in C]
pv={(r['control'],r['group']):r['p'] for r in C}
T={'en':dict(t='Exchange incidents on volatile vs calm Bitcoin days: most of the gap is the weekend',
   ctl=['all days ranked together','ranked within each month','within month and weekday/weekend'],
   grp=['platform incidents','funding / network incidents','named load or connectivity'],y='incident rate, most volatile fifth of days ÷ calmest fifth',
   src='Data: unscheduled incidents on status.kraken.com, status.coinbase.com, status.gemini.com (Dec 2024 - Nov 2026, 1,764) and Kraken BTC/USD daily range. p from rank shuffles within strata.'),
 'ru':dict(t='Сбои бирж в бурные и спокойные дни биткоина: почти весь разрыв даёт выходной',
   ctl=['все дни вместе','внутри каждого месяца','внутри месяца и будни/выходные'],
   grp=['сбои платформы','ввод/вывод и сети','с «load»/«connectivity» в названии'],y='частота инцидентов: самая бурная пятая часть дней ÷ самая спокойная',
   src='Данные: внеплановые инциденты status.kraken.com, status.coinbase.com, status.gemini.com (12.2024–11.2026, 1764) и дневной размах BTC/USD на Kraken. p — перестановки внутри страт.')}
cols=['#2a6fdb','#e8a33d','#d9482b']
for lang,t in T.items():
    fig,ax=plt.subplots(figsize=(10,5.6),dpi=120)
    ctls=['naive','within month','within month x weekend']
    for j,g in enumerate(G):
        xs=[i+(j-1)*0.26 for i in range(3)]; ys=[rat[c][g] for c in ctls]
        ax.bar(xs,ys,width=0.25,color=cols[j],label=t['grp'][j])
        for x,y,c in zip(xs,ys,ctls):
            lab=f'{y:.2f}'+('' if c=='naive' else f'\np={pv[(c,g)]:.3f}'.replace('p=0.000','p<0.001'))
            ax.text(x,y+0.04,lab,ha='center',va='bottom',fontsize=8)
    ax.axhline(1,color='#333',lw=1,ls='--'); ax.set_xticks(range(3)); ax.set_xticklabels(t['ctl'])
    ax.set_ylabel(t['y'],fontsize=9); ax.set_ylim(0,3.9); ax.spines[['top','right']].set_visible(False); ax.legend(frameon=False,fontsize=9,loc='upper right')
    ax.set_title(t['t'],loc='left',fontsize=11.5); fig.text(.01,.01,t['src'],fontsize=7,color='#555',wrap=True)
    fig.tight_layout(rect=(0,.05,1,1)); fig.savefig(f'../../crypto-exchange-outages-volatility{"-ru" if lang=="ru" else ""}.png')

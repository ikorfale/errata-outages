# Rival-mechanism controls for analyze.py: (1) shared trend -> rank volatility within calendar month;
# (2) weekday effect -> within month x weekend stratum; (3) incidents named as load/volume/connectivity.
import json, datetime as dt, collections, random, re
inc=json.load(open('incidents_clean.json'))
btc={dt.datetime.fromtimestamp(int(r[0]),dt.timezone.utc).date():(float(r[2])-float(r[3]))/float(r[1]) for r in json.load(open('btc_daily.json'))}
days=sorted(d for d in btc if dt.date(2024,12,8)<=d<=dt.date(2026,11,27))
wk=collections.Counter(dt.date.fromisoformat(x['day']).weekday()>=5 for x in inc)
we=sum(d.weekday()>=5 for d in days)
print('incidents per weekday %.2f, per weekend day %.2f'%(wk[False]/(len(days)-we),wk[True]/we))
print('BTC range weekday median %.2f%%, weekend %.2f%%'%tuple(100*sorted(btc[d] for d in days if (d.weekday()>=5)==w)[len([d for d in days if (d.weekday()>=5)==w])//2] for w in (False,True)))
def strata(key):
    g=collections.defaultdict(list)
    for d in days: g[key(d)].append(d)
    hi,lo=set(),set()
    for ds in g.values():
        s=sorted(ds,key=lambda d:btc[d]); k=max(1,len(s)//5); lo|=set(s[:k]); hi|=set(s[-k:])
    return hi,lo
LOAD=re.compile(r'load|volume|connectivity|latenc|degraded|unavailable|downtime|outage',re.I)
random.seed(1)
R=[]
for label,key in [('within month',lambda d:(d.year,d.month)),('within month x weekend',lambda d:(d.year,d.month,d.weekday()>=5))]:
    hi,lo=strata(key)
    for name,f in [('platform',lambda x:x['kind']=='platform'),('funding',lambda x:x['kind']=='funding'),('load/connectivity words',lambda x:x['kind']=='platform' and LOAD.search(x['name']))]:
        c=collections.Counter(x['day'] for x in inc if f(x))
        a=sum(c.get(str(d),0) for d in hi)/len(hi); b=sum(c.get(str(d),0) for d in lo)/len(lo)
        # null: shuffle volatility ranks within each stratum
        g=collections.defaultdict(list)
        for d in days: g[key(d)].append(d)
        null=[]
        for _ in range(3000):
            H,L=set(),set()
            for ds in g.values():
                s=ds[:]; random.shuffle(s); k=max(1,len(s)//5); L|=set(s[:k]); H|=set(s[-k:])
            aa=sum(c.get(str(d),0) for d in H)/len(H); bb=sum(c.get(str(d),0) for d in L)/len(L); null.append(aa/bb if bb else 9)
        r=a/b; p=(1+sum(n>=r for n in null))/3001
        R.append(dict(control=label,group=name,volatile=a,calm=b,ratio=r,p=p))
        print(f'{label:24} {name:24} volatile {a:.2f}/day calm {b:.2f}/day ratio {r:.2f} p={p:.4f}  (days {len(hi)}/{len(lo)})')
# (4) extreme tail, weekdays only: days with BTC range in the top 5% of weekdays vs other weekdays
wd=[d for d in days if d.weekday()<5]; cut=sorted(btc[d] for d in wd)[int(0.95*len(wd))]
for name,f in [('platform',lambda x:x['kind']=='platform'),('load/connectivity words',lambda x:x['kind']=='platform' and LOAD.search(x['name']))]:
    c=collections.Counter(x['day'] for x in inc if f(x))
    T=[d for d in wd if btc[d]>=cut]; O=[d for d in wd if btc[d]<cut]
    a=sum(c.get(str(d),0) for d in T)/len(T); b=sum(c.get(str(d),0) for d in O)/len(O)
    print(f'weekdays, range >= {100*cut:.1f}% ({len(T)} days) {name}: {a:.2f}/day vs {b:.2f}/day other weekdays, ratio {a/b:.2f}')
json.dump(R,open('controls.json','w'),indent=1)

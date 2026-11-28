# Do exchange incidents cluster on volatile BTC days? Incidents: unscheduled Statuspage history (Dec 2024-Nov 2026).
# Volatility: Kraken XBTUSD daily range (high-low)/open, UTC days. Test: top vs bottom volatility quintile, incident
# rate ratio; null = circular shift of each incident series by 30..(N-30) days (keeps clustering and trend shape).
import json, re, datetime as dt, random, collections
MON={m:i for i,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],1)}
FULL={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
FUND=re.compile(r'funding|gateway|deposit|withdraw|network|congest|\b[A-Z]{2,6}\b.*(delay|halt)',re.I)
def parse(ex):
    out=[]
    for m in json.load(open(f'history_{ex}.json')):
        for i in m['incidents']:
            if i['impact']=='maintenance' or i['name'].lower().startswith('[scheduled]'): continue
            s=re.sub(r'<[^>]+>','',i['timestamp']); g=re.match(r'(\w{3})\s+(\d+),\s+(\d+):(\d+)',s)
            if not g: continue
            mo=MON[g[1]]; yr=m['year'] - (1 if mo>FULL[m['name']] else 0)
            out.append(dict(ex=ex,day=dt.date(yr,mo,int(g[2])),name=i['name'],impact=i['impact'],
                            kind='funding' if FUND.search(i['name']) else 'platform'))
    return out
inc=[x for ex in ('Kraken','Coinbase','Gemini') for x in parse(ex)]
btc={dt.datetime.fromtimestamp(int(r[0]),dt.timezone.utc).date():(float(r[2])-float(r[3]))/float(r[1]) for r in json.load(open('btc_daily.json'))}
days=sorted(d for d in btc if d>=dt.date(2024,12,1) and d<=dt.date(2026,11,27))
inc=[x for x in inc if days[0]<=x['day']<=days[-1]]
print('days',len(days),days[0],days[-1],'unscheduled incidents',len(inc))
print(collections.Counter((x['ex'],x['kind']) for x in inc))
vol=[btc[d] for d in days]; srt=sorted(vol); q20,q80=srt[len(srt)//5],srt[4*len(srt)//5]
print('BTC daily range median %.2f%%, quintile cut %.2f%% / %.2f%%'%(100*srt[len(srt)//2],100*q20,100*q80))
hi=[i for i,v in enumerate(vol) if v>=q80]; lo=[i for i,v in enumerate(vol) if v<=q20]
def series(f):
    c=collections.Counter(x['day'] for x in inc if f(x)); return [c.get(d,0) for d in days]
def ratio(s,H=hi,L=lo):
    a=sum(s[i] for i in H)/len(H); b=sum(s[i] for i in L)/len(L); return a,b,(a/b if b else float('inf'))
random.seed(20261128); N=len(days); res={}
groups=[(ex,k) for ex in ('Kraken','Coinbase','Gemini') for k in ('platform','funding')]+[('all','platform'),('all','funding')]
for ex,k in groups:
    s=series(lambda x:(ex=='all' or x['ex']==ex) and x['kind']==k)
    a,b,r=ratio(s); null=[]
    for _ in range(5000):
        sh=random.randint(30,N-30); t=s[sh:]+s[:sh]; null.append(ratio(t)[2])
    p=(1+sum(n>=r for n in null))/5001
    res[f'{ex}/{k}']=dict(n=sum(s),hi=a,lo=b,ratio=r,p=p)
    print(f'{ex:8} {k:8} n={sum(s):4}  per day: volatile {a:.3f}  calm {b:.3f}  ratio {r:.2f}  p(one-sided)={p:.3f}')
# platform incidents, top 10 BTC range days
top=sorted(days,key=lambda d:-btc[d])[:10]
print('10 widest-range days:')
for d in top: print(' ',d,'%.1f%%'%(100*btc[d]),[ (x['ex'],x['name'][:50]) for x in inc if x['day']==d and x['kind']=='platform'])
json.dump(dict(res=res,days=len(days),n=len(inc)),open('result.json','w'),indent=1,default=str)
json.dump([dict(x,day=str(x['day'])) for x in inc],open('incidents_clean.json','w'))

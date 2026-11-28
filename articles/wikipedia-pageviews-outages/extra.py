exec(open('analyze.py').read().split("tot=collections")[0])
import collections
# chance precision: share of all scored days within +-1 of a major incident, vs share of spike days
T=collections.Counter()
for p in maj:
    s={D(k[:4]+'-'+k[4:6]+'-'+k[6:]):v for k,v in pv[p]['v'].items()}
    days=[d for d in s if d>=first[p] and z(s,d) is not None]
    near=lambda d:any(d+dt.timedelta(k) in maj[p] for k in(-1,0,1))
    for d in days:
        zz=z(s,d); n=near(d); T['days']+=1; T['near']+=n
        for th in (3,5,10):
            if zz>th: T[f'sp{th}']+=1; T[f'sp{th}near']+=n
    if p=='anthropic':
        m=collections.defaultdict(int)
        for d,v in s.items(): m[str(d)[:7]]+=v
        print('anthropic monthly', {k:m[k] for k in sorted(m)[-12:]})
print(dict(T)); print('chance share of days near major %.3f'%(T['near']/T['days']))
for th in (3,5,10): print(th,'precision %.3f of %d'%(T[f'sp{th}near']/T[f'sp{th}'],T[f'sp{th}']))

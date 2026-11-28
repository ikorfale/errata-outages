# Rival mechanism: launches/news drive both incidents and pageviews in the same weeks.
# If the spike belongs to the outage DAY, lift should collapse when incident dates shift by +-7/14 days.
exec(open('analyze.py').read().split("tot=collections")[0])
def pooled(shift,provs=None):
    E=S=C=CS=0
    for p in maj:
        if provs and p not in provs: continue
        s={D(k[:4]+'-'+k[4:6]+'-'+k[6:]):v for k,v in pv[p]['v'].items()}
        M={d+dt.timedelta(shift) for d in maj[p]}; A={d+dt.timedelta(shift) for d in anyd[p]}
        days=[d for d in s if d>=first[p] and z(s,d) is not None]
        near=lambda d,X:any(d+dt.timedelta(k) in X for k in(-1,0,1))
        for d in days:
            sp=z(s,d)>3
            if d in M: E+=1;S+=sp
            elif not near(d,A): C+=1;CS+=sp
    return E,S,C,CS,(S/E)/(CS/C) if CS else float('nan')
for grp,pr in (('all',None),('anthropic',{'anthropic'}),('github',{'github'}),('rest',set(maj)-{'anthropic','github'})):
    for sh in (0,-14,-7,7,14):
        E,S,C,CS,l=pooled(sh,pr); print(f"{grp:9s} shift {sh:+3d}  ev {E:4d} sp {S:3d}  ctl {C:5d} sp {CS:3d}  lift {l:.2f}")
# dose-response: long vs short major incidents (max duration that day)
import collections
L=collections.Counter()
for p in maj:
    s={D(k[:4]+'-'+k[4:6]+'-'+k[6:]):v for k,v in pv[p]['v'].items()}
    dur=collections.defaultdict(float)
    for r in rows:
        if r['p']==p and r['imp'] in('major','critical'): dur[D(r['utc'])]=max(dur[D(r['utc'])],r['h'] or 0)
    for d,h in dur.items():
        if d in s and d>=first[p] and z(s,d) is not None:
            k='long>=2h' if h>=2 else 'short<2h'; L[k]+=1; L[k+'_sp']+=z(s,d)>3
print({k:v for k,v in L.items()}, 'long %.3f short %.3f'%(L['long>=2h_sp']/L['long>=2h'],L['short<2h_sp']/L['short<2h']))

import json,datetime as dt,statistics as st,collections
pv=json.load(open('pv.json')); rows=json.load(open('../outage-clock/rows.json'))
D=lambda s:dt.date(int(s[:4]),int(s[5:7]),int(s[8:10]))
maj=collections.defaultdict(set); anyd=collections.defaultdict(set); first={}
for r in rows:
    d=D(r['utc']); anyd[r['p']].add(d); first[r['p']]=min(first.get(r['p'],d),d)
    if r['imp'] in('major','critical'): maj[r['p']].add(d)
def z(series,day):
    win=[series.get(day-dt.timedelta(k)) for k in range(1,29)]; win=[w for w in win if w is not None]
    if len(win)<20: return None
    m=st.median(win); mad=st.median([abs(w-m) for w in win])*1.4826 or 1
    return (series[day]-m)/mad
tot=collections.Counter(); print('prov  ev  P(sp|ev)  ctl P(sp|ctl)  lift  spikes prec')
res={}
for p in sorted(maj,key=lambda p:-len(maj[p])):
    s={D(k[:4]+'-'+k[4:6]+'-'+k[6:]):v for k,v in pv[p]['v'].items()}
    days=[d for d in s if d>=first[p] and z(s,d) is not None]
    near=lambda d,S:any(d+dt.timedelta(k) in S for k in(-1,0,1))
    ev=[d for d in days if d in maj[p]]; ctl=[d for d in days if not near(d,anyd[p])]
    sp={d for d in days if z(s,d)>3}
    a=sum(d in sp for d in ev); b=sum(d in sp for d in ctl); c=sum(near(d,maj[p]) for d in sp)
    pe=a/len(ev) if ev else 0; pc=b/len(ctl) if ctl else float('nan')
    lift=pe/pc if pc else float('inf')
    print(f"{p:12s} {len(ev):3d} {a:3d} {pe:5.2f}  {len(ctl):4d} {b:3d} {pc:5.2f}  {lift:5.2f}  {len(sp):3d} {c:3d}")
    for k,v in (('ev',len(ev)),('evsp',a),('ctl',len(ctl)),('ctlsp',b),('sp',len(sp)),('spnear',c)): tot[k]+=v
    res[p]=dict(ev=len(ev),evsp=a,ctl=len(ctl),ctlsp=b,sp=len(sp),spnear=c,top=sorted(((round(z(s,d),1),str(d),d in maj[p]) for d in ev),reverse=True)[:3])
print('POOLED',dict(tot),'P(sp|ev)=%.3f P(sp|ctl)=%.3f lift=%.2f precision=%.3f'%(tot['evsp']/tot['ev'],tot['ctlsp']/tot['ctl'],(tot['evsp']/tot['ev'])/(tot['ctlsp']/tot['ctl']),tot['spnear']/tot['sp']))
json.dump(res,open('res.json','w'),indent=0)

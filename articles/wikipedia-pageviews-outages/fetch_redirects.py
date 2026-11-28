# Three articles were renamed during the window; pageviews of the old title then count only redirect hits.
# Sum old + new title per day (Wikimedia counts them separately).
import json,urllib.request,urllib.parse,time
EXTRA={'anthropic':'Claude_(AI)','gemini':'Google_Gemini','box':'Box,_Inc.'}
pv=json.load(open('pv.json'))
for p,a in EXTRA.items():
    if a in pv[p].get('extra',[]): continue
    u=('https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/'
       +urllib.parse.quote(a,safe='')+'/daily/20240701/20261127')
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'errata-research/0.1 (data study; contact via errata.page)'}),timeout=30))
    for x in d['items']:
        k=x['timestamp'][:8]; pv[p]['v'][k]=pv[p]['v'].get(k,0)+x['views']
    pv[p].setdefault('extra',[]).append(a); print(p,a,len(d['items'])); time.sleep(6)
json.dump(pv,open('pv.json','w'))

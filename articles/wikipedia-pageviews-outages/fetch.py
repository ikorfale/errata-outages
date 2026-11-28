import json,urllib.request,urllib.parse,time,sys
ART={'anthropic':'Claude_(language_model)','github':'GitHub','epic':'Epic_Games_Store','box':'Box_(company)',
'discord':'Discord','gemini':'Gemini_(chatbot)','twilio':'Twilio','digitalocean':'DigitalOcean','reddit':'Reddit',
'wise':'Wise_(company)','klarna':'Klarna','linode':'Linode','kraken':'Kraken_(cryptocurrency_exchange)','zoom':'Zoom_(software)',
'dropbox':'Dropbox','coinbase':'Coinbase','akamai':'Akamai_Technologies','shopify':'Shopify'}
out=json.load(open("pv.json")) if len(sys.argv)>1 else {}
for p,a in [(k,v) for k,v in ART.items() if k not in out]:
    u=('https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/'
       +urllib.parse.quote(a,safe='')+'/daily/20240701/20261127')
    req=urllib.request.Request(u,headers={'User-Agent':'errata-research/0.1 (data study; contact via errata.page)'})
    try:
        d=json.load(urllib.request.urlopen(req,timeout=30))
        out[p]={'article':a,'v':{x['timestamp'][:8]:x['views'] for x in d['items']}}
        print(p,a,len(out[p]['v']))
    except Exception as e: print(p,a,'ERR',e)
    time.sleep(6)
json.dump(out,open('pv.json','w'))

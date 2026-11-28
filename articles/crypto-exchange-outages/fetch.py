# Fetch exchange status-page incident histories (Statuspage incidents.json, last 50 each) and Kraken daily BTC/USD OHLC.
import json, urllib.request
H={'User-Agent':'errata-outage-watch'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=30))
pages={'Kraken':'https://status.kraken.com','Coinbase':'https://status.coinbase.com','Gemini':'https://status.gemini.com'}
out={}
for k,u in pages.items():
    try:
        d=get(u+'/api/v2/incidents.json'); out[k]=d['incidents']; print(k,len(d['incidents']),d['incidents'][-1]['created_at'][:10],'..',d['incidents'][0]['created_at'][:10])
    except Exception as e: print(k,'ERR',e)
json.dump(out,open('incidents.json','w'))
o=get('https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440')
rows=list(o['result'].values())[0]; json.dump(rows,open('btc_daily.json','w')); print('btc days',len(rows))

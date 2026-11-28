# Statuspage history.json pages 1..8 (3 months each) per exchange -> history_<name>.json (raw months)
import json, time, urllib.request
H={'User-Agent':'errata-outage-watch'}
pages={'Kraken':'https://status.kraken.com','Coinbase':'https://status.coinbase.com','Gemini':'https://status.gemini.com'}
for k,u in pages.items():
    months=[]
    for p in range(1,9):
        try: d=json.load(urllib.request.urlopen(urllib.request.Request(f'{u}/history.json?page={p}',headers=H),timeout=30))
        except Exception as e: print(k,p,'ERR',e); break
        if not d.get('months'): break
        months+=d['months']; time.sleep(1)
    json.dump(months,open(f'history_{k}.json','w'))
    print(k,len(months),'months',sum(len(m['incidents']) for m in months),'incidents', months[-1]['name'],months[-1]['year'])

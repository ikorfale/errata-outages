# Twilio incidents: route/carrier-specific vs platform. Data: status.twilio.com/api/v2/incidents.json (raw/incidents.json, fetched 2026-11-27)
# plus Outage Watch records (sp:twilio:<id>) for incidents that dropped out of the API's last-50 window.
import json, re, statistics as st, collections, datetime as dt, sys
api = json.load(open('raw/incidents.json'))['incidents']
ow = json.load(open('../../data/outages.json'))['incidents']
P = lambda s: dt.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(dt.timezone.utc)
rows = {}
for i in api:
    rows[i['id']] = dict(id=i['id'], title=i['name'], start=P(i['created_at']), end=P(i['resolved_at']) if i.get('resolved_at') else None,
                         comps=[c['name'] for c in i['components']], src='api')
for x in ow:
    if x['source'] != 'Twilio': continue
    k = x['key'].split(':')[-1]
    if k not in rows:
        rows[k] = dict(id=k, title=x['title'], start=P(x['started']), end=P(x['resolved']) if x.get('resolved') else None, comps=[], src='ow')
R_all = sorted(rows.values(), key=lambda r: r['start'])
FROM = dt.datetime(2026, 11, 17, tzinfo=dt.timezone.utc)
OLDER = [r for r in R_all if r['start'] < FROM]
R = [r for r in R_all if r['start'] >= FROM]
print('older incidents still in the API list (started before 17 Nov):', len(OLDER), [r['title'][:60] for r in OLDER])
CH = lambda t: 'SMS' if t.startswith('SMS') else 'MMS' if t.startswith('MMS') else 'Voice' if t.startswith('Voice') else 'Lookup' if 'Lookup' in t else 'Other'
ROUTE = re.compile(r'\b(to|from|between|on|in)\b.*?(Telecom|Mobile|Mobility|Networks?|Vodafone|AT&T|Verizon|T-Mobile|Orange|Telcel|Movistar|Claro|Bouygues|SFR|Free|GCI|OneNZ|Airtel|Jio|MTN|Telstra|Optus|[A-Z][a-z]+ [A-Z][a-z]+$|in [A-Z])')
COUNTRIES = ['United States','Mexico','Canada','France','New Zealand','Bahrain','South Africa','India','United Kingdom','Brazil','Germany','Spain','Italy','Australia','Philippines','Indonesia','Nigeria','Kenya','Saudi Arabia','UAE','United Arab Emirates','Japan','Colombia','Peru','Chile','Argentina','Pakistan','Bangladesh','Egypt','Turkey','Netherlands','Poland','Ireland','Israel','Malaysia','Thailand','Vietnam','Singapore','Ghana','Morocco','Kuwait','Qatar','Oman','Jordan','Sri Lanka','Nepal','Ukraine','Romania','Portugal','Belgium','Switzerland','Austria','Sweden','Norway','Denmark','Finland','Greece','Hungary','Czech','Ecuador','Guatemala','Dominican','Puerto Rico','Jamaica','Honduras','Costa Rica','Panama','Uruguay','Bolivia','Paraguay','Venezuela','Taiwan','Hong Kong','South Korea','China','Cambodia','Myanmar','Tanzania','Uganda','Zambia','Zimbabwe','Ethiopia','Cameroon','Senegal','Ivory Coast','Algeria','Tunisia','Iraq','Lebanon','Kazakhstan','Uzbekistan','Russia','Mongolia','Brasil','Serbia','Lesotho']
for r in R:
    t = r['title']
    r['ch'] = CH(t)
    r['route'] = any(c in t for c in COUNTRIES)  # rule: the title names a country (and usually a carrier) -> route-specific
    r['hours'] = (r['end'] - r['start']).total_seconds() / 3600 if r['end'] else None
print('incidents:', len(R), 'api:', sum(r['src']=='api' for r in R), 'outage-watch only:', sum(r['src']=='ow' for r in R))
print('window:', R[0]['start'].strftime('%Y-%m-%d %H:%M'), '->', R[-1]['start'].strftime('%Y-%m-%d %H:%M'), 'UTC')
days = (R[-1]['start'] - R[0]['start']).total_seconds() / 86400
print(f'days: {days:.1f}  per day: {len(R)/days:.2f}')
rt = [r for r in R if r['route']]; pl = [r for r in R if not r['route']]
print('route-specific:', len(rt), 'platform/other:', len(pl))
print('channel (route):', collections.Counter(r['ch'] for r in rt).most_common())
print('channel (platform):', collections.Counter(r['ch'] for r in pl).most_common())
def med(v): v = [x for x in v if x is not None]; return (len(v), round(st.median(v), 1), round(max(v), 1)) if v else (0,)
print('hours route (n, median, max):', med([r['hours'] for r in rt]))
print('hours platform (n, median, max):', med([r['hours'] for r in pl]))
print('open (no resolved time):', [r['title'][:70] for r in R if r['end'] is None])
# country = last words after ' in ' or the trailing country name
cc = collections.Counter()
for r in rt:
    hit = [c for c in COUNTRIES if c in r['title']]
    r['country'] = ('Brazil' if hit[0]=='Brasil' else hit[0]) if hit else ('New Zealand' if 'NZ' in r['title'] else 'France' if 'Bouygues' in r['title'] or 'SFR' in r['title'] else '?')
    cc[r['country']] += 1
print('countries (route):', cc.most_common())
# carrier repeats: normalise text after 'to ' / 'on '
car = collections.Counter()
for r in rt:
    m = re.search(r'\b(?:to|on|and)\s+([A-Z][\w&/ .-]*?)(?:\s+(?:in|United|network|Networks)\b|$)', r['title'].split(' from ')[-1] if ' to ' not in r['title'] else r['title'].split(' to ')[-1])
    r['carrier'] = (m.group(1).strip() if m else r['title'].split(' to ')[-1]).strip()
    car[r['carrier']] += 1
print('carriers with >=2 incidents:', [(k, v) for k, v in car.most_common() if v >= 2])
by_day = collections.Counter(r['start'].strftime('%m-%d') for r in R)
print('by day:', sorted(by_day.items()))
json.dump([{**r, 'start': r['start'].isoformat(), 'end': r['end'].isoformat() if r['end'] else None} for r in R], open('rows.json', 'w'), indent=1, default=str)
for r in R: print(r['start'].strftime('%m-%d %H:%M'), 'R' if r['route'] else 'P', r['ch'], f"{r['hours']:.1f}" if r['hours'] else 'open', r['title'][:95], file=open('list.txt','a'))

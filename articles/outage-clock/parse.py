"""Parse raw/<id>-<page>.json (Statuspage history.json) into rows.json: one incident per row, maintenance excluded,
start/end converted to UTC from the page's tz abbreviation, then to the provider's HQ zone."""
import json, re, glob, datetime as dt, collections as C
from zoneinfo import ZoneInfo
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
TZ = {'UTC': 0, 'GMT': 0, 'PST': -8, 'PDT': -7, 'MST': -7, 'MDT': -6, 'CST': -6, 'CDT': -5, 'EST': -5, 'EDT': -4,
      'BST': 1, 'CET': 1, 'CEST': 2, 'IST': 5.5, 'AEST': 10, 'AEDT': 11, 'JST': 9, 'SGT': 8}
HQ = dict(discord='America/Los_Angeles', reddit='America/Los_Angeles', epic='America/New_York', zoom='America/Los_Angeles',
          atlassian='Australia/Sydney', github='America/Los_Angeles', dropbox='America/Los_Angeles', box='America/Los_Angeles',
          twilio='America/Los_Angeles', coinbase='America/Los_Angeles', kraken='America/Los_Angeles', gemini='America/New_York',
          akamai='America/New_York', digitalocean='America/New_York', linode='America/New_York', openai='America/Los_Angeles',
          anthropic='America/Los_Angeles', shopify='America/Toronto', wise='Europe/London', klarna='Europe/Stockholm',
          plaid='America/Los_Angeles', cashapp='America/Los_Angeles', mollie='Europe/Amsterdam', gocardless='Europe/London',
          robinhood='America/Los_Angeles', cloudflare='America/Los_Angeles')
strip = lambda s: re.sub(r'<[^>]+>', '', s)
R, bad, tzs = [], C.Counter(), C.defaultdict(C.Counter)
seen = set()
for f in sorted(glob.glob('raw/*.json')):
    pid = f.split('/')[-1].rsplit('-', 1)[0]
    for m in json.load(open(f)).get('months', []):
        lm = MON[m['name'][:3]]
        for i in m['incidents']:
            if i['code'] in seen: continue
            seen.add(i['code'])
            if i['impact'] == 'maintenance': continue
            ts = strip(i['timestamp'])
            g = re.match(r'(\w{3}) (\d+), (\d+):(\d+)(?: - (?:(\w{3}) (\d+), )?(\d+):(\d+))? (\w+)$', ts.strip())
            if not g or g.group(9) not in TZ: bad[pid] += 1; continue
            mo, d, h, mi, mo2, d2, h2, mi2, tz = g.groups(); tzs[pid][tz] += 1
            y = m['year'] - (1 if MON[mo] > lm + 1 else 0)
            off = dt.timedelta(hours=TZ[tz])
            s = dt.datetime(y, MON[mo], int(d), int(h), int(mi)) - off
            e = None
            if h2:
                y2 = y + (1 if mo2 and MON[mo2] < MON[mo] else 0)
                e = dt.datetime(y2, MON[mo2 or mo], int(d2 or d), int(h2), int(mi2)) - off
                if e < s and not mo2: e += dt.timedelta(days=1)
            s = s.replace(tzinfo=dt.timezone.utc); loc = s.astimezone(ZoneInfo(HQ.get(pid, 'UTC')))
            R.append(dict(p=pid, imp=i['impact'], utc=s.isoformat(), wd=loc.weekday(), hr=loc.hour,
                          h=None if e is None else (e.replace(tzinfo=dt.timezone.utc) - s).total_seconds() / 3600, name=i['name']))
json.dump(R, open('rows.json', 'w'))
print('rows', len(R), 'unparsed', dict(bad))
for p, c in sorted(tzs.items()): print(p, dict(c), sum(r['p'] == p for r in R), min(r['utc'][:10] for r in R if r['p'] == p))

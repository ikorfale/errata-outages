#!/usr/bin/env python3
"""outage_site_export.py — public Outage Watch data for errata.page/outages (EN) and /ru/outages (RU).

Writes ~/errata-site/_src/outages.json. Safety rule (plan #821, operator 26.11):
- only official status-page incidents of commercial providers (clouds, payments, comms, dev, AI, crypto, consumer);
- IODA country-level internet signals are NOT published (they include shutdowns in war zones and causes are unknown);
- monitor leads are never published (a lead is not a fact);
- no causation claims: we quote the provider's own last status text, nothing else;
- any incident whose title/text mentions war-related words is dropped.
End time = the first collector check (every 15 min) where the incident left the provider's unresolved list."""
import ast, json, os, re, datetime as dt
from outage_noise import is_noise

W = os.environ.get('OUTAGES_DIR', 'outages')
OUT = os.environ.get('OUTAGES_OUT', 'data/outages.json')
WAR = re.compile(r'\b(war|military|missile|drone|strike|attack|russia|ukrain|israel|iran|gaza|sanction)', re.I)
KEEP = ('source', 'sector', 'title', 'impact', 'status', 'started', 'url', 'text')


def iso(s):
    d = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
    return d.astimezone(dt.timezone.utc)


def watched():
    """Every provider the collector polls (not only those that had incidents): STATUSPAGE list + GCP, AWS, Azure."""
    tree = ast.parse(open(os.environ.get('COLLECTOR', 'outage_watch.py')).read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'STATUSPAGE':
            names = [t[1] for t in ast.literal_eval(n.value)]
    return sorted(names + ['Google Cloud', 'AWS', 'Microsoft Azure'])


def main():
    inc = {}
    for line in open(f'{W}/events.jsonl'):
        e = json.loads(line)
        if e.get('kind') != 'official' or e['source'].startswith('IODA'):
            continue
        h = inc.setdefault(e['key'], {'key': e['key'], 'first_seen': e['first_seen']})
        h.update({k: e[k] for k in KEEP if e.get(k) is not None})
        if e['change'] == 'gone':
            h['ended'] = e['ts']
        else:
            h.pop('ended', None)  # reopened
    rows, dropped, noise = [], 0, 0
    for h in inc.values():
        if is_noise(h.get('title', ''), h.get('sector')):
            noise += 1
            continue
        if WAR.search(h.get('title', '') + ' ' + h.get('text', '')):
            dropped += 1
            continue
        s = iso(h['started'])
        h['started'] = s.strftime('%Y-%m-%dT%H:%MZ')
        if 'ended' in h:
            en = iso(h['ended'])
            h['ended'] = en.strftime('%Y-%m-%dT%H:%MZ')
            h['hours'] = round((en - s).total_seconds() / 3600, 1)
        h['text'] = (h.get('text') or '')[:400]
        rows.append(h)
    rows.sort(key=lambda r: r['started'], reverse=True)
    o = json.load(open(f'{W}/open.json'))
    d = {'checked': o['checked'][:16] + 'Z', 'since': min(r['first_seen'] for r in rows)[:10],
         'sources': watched(), 'with_incidents': sorted({r['source'] for r in rows}), 'incidents': rows, 'dropped_war_words': dropped, 'dropped_noise': noise}
    tmp = OUT + '.tmp'
    json.dump(d, open(tmp, 'w'), ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(f'outage site export: {len(rows)} incidents ({sum("ended" not in r for r in rows)} open), {dropped} dropped by war-word rule, {noise} as one-coin/advisory noise')


if __name__ == '__main__':
    main()

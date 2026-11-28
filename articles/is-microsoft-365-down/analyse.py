#!/usr/bin/env python3
"""Count what the public Microsoft 365 status page (status.cloud.microsoft) showed in every
Wayback snapshot of its two JSON endpoints. Output: results.txt, episodes.csv."""
import glob, gzip, json, re, csv, collections
def load(fn):
    b = open(fn, 'rb').read()
    if b[:2] == b'\x1f\x8b': b = gzip.decompress(b)
    try: d = json.loads(b)
    except Exception: return None
    return d if isinstance(d, list) else [d]
NORMAL = {'Operational', 'Available', None, ''}
cnt = collections.defaultdict(collections.Counter)
out = []; rows = []; eps = collections.OrderedDict()
for ep in ['m365Consumer', 'mac']:
    files = sorted(glob.glob(f'snap/{ep}_*.json'))
    ok = bad = parse_fail = 0
    for fn in files:
        ts = fn.split('_')[-1][:-5]
        d = load(fn)
        if d is None: parse_fail += 1; continue
        hit = [x for x in d if x.get('Status') not in NORMAL]
        active = [x for x in hit if x.get('Status') != 'Service restored']
        state = 'active' if active else ('restored' if hit else 'none')
        cnt[ep][state] += 1
        if hit: bad += 1
        else: ok += 1
        for x in hit:
            key = (ep, x.get('Id') or x.get('Title'), x.get('AuthoredDateTime'))
            msg = re.sub(r'<[^>]+>', ' ', x.get('Message') or '')
            e = eps.setdefault(key, dict(ep=ep, title=x.get('Title') or msg[:90].strip(), authored=x.get('AuthoredDateTime'),
                                         status=x.get('Status'), first_seen=ts, last_seen=ts, n=0, ids=set()))
            e['last_seen'] = ts; e['n'] += 1
            e['ids'].update(re.findall(r'\b(?:MO|EX|TM|SP|OD|CP|PL|DZ|FL|MM)\d{6,7}\b', msg))
        rows.append((ep, ts, state))
    span = (files[0].split('_')[-1][:8], files[-1].split('_')[-1][:8]) if files else ('', '')
    out.append(f'{ep}: {len(files)} snapshots {span[0]}..{span[1]}; normal {ok}, showing an issue {bad}, unparsable {parse_fail}; by state {dict(cnt[ep])}')
out.append(f'distinct issue posts seen: {len(eps)}')
with open('episodes.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['endpoint', 'authored', 'first_snapshot', 'last_snapshot', 'n_snapshots', 'status', 'ids', 'title'])
    for e in eps.values():
        w.writerow([e['ep'], e['authored'], e['first_seen'], e['last_seen'], e['n'], e['status'], ' '.join(sorted(e['ids'])), e['title']])
        out.append(f"  {e['ep']:12s} authored {e['authored']} seen {e['first_seen']}..{e['last_seen']} n={e['n']} {e['status']} {' '.join(sorted(e['ids']))} | {e['title'][:80]}")
csv.writer(open('snapshots.csv','w',newline='')).writerows([('endpoint','ts','issue')]+rows)
open('results.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))

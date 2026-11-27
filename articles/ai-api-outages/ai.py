"""Anthropic and OpenAI status-page incidents, 1-26 Nov 2026, from their public Statuspage-format APIs (raw/, fetched 27.11).
Durations = resolved_at - started_at (or created_at). 'Backfilled' = resolved within 5 min of being created (posted after the fact)."""
import json, statistics as st, datetime as dt, collections, re
def iso(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
lo, hi = iso('2026-11-01T00:00:00Z'), iso('2026-11-27T00:00:00Z')
out = {}
for name, f in [('Anthropic', 'raw/status.anthropic.com.json'), ('OpenAI', 'raw/status.openai.com.json')]:
    I = json.load(open(f))['incidents']
    rows = []
    for x in I:
        s = iso(x.get('started_at') or x['created_at'])
        if not (lo <= s < hi): continue
        c, r = iso(x['created_at']), (iso(x['resolved_at']) if x.get('resolved_at') else None)
        rows.append(dict(name=x['name'], impact=x['impact'], start=s, created=c, resolved=r,
                         hours=(r - s).total_seconds() / 3600 if r else None, backfill=bool(r and (r - c).total_seconds() < 300),
                         post_delay_min=(c - s).total_seconds() / 60))
    out[name] = rows
    h = [r['hours'] for r in rows if r['hours'] is not None and not r['backfill']]
    print(f"== {name}: {len(rows)} incidents started 1-26 Nov; impact {dict(collections.Counter(r['impact'] for r in rows))}")
    print(f"   backfilled (resolved <5 min after posting): {sum(r['backfill'] for r in rows)}; unresolved: {sum(r['resolved'] is None for r in rows)}")
    if h: print(f"   live incidents with duration: n={len(h)} median={st.median(h):.2f} h  max={max(h):.1f} h  >4h: {sum(v > 4 for v in h)}")
    bd = [r for r in rows if r['backfill']]
    if bd: print(f"   backfilled ones: start-to-resolve median {st.median([r['hours'] for r in bd]):.2f} h")
    pd = [r['post_delay_min'] for r in rows if not r['backfill']]
    if pd: print(f"   posted after its own start time, live ones: median {st.median(pd):.0f} min, max {max(pd):.0f} min, n={len(pd)}")
    words = collections.Counter()
    for r in rows:
        t = r['name'].lower()
        for k, rx in [('Claude Code', 'claude code'), ('claude.ai / ChatGPT app', r'claude\.ai|chatgpt'), ('API', r'\bapi\b'), ('Codex', 'codex'), ('Opus', 'opus'), ('Sonnet', 'sonnet'), ('Haiku', 'haiku'), ('Fable', 'fable'), ('login/auth', r'login|auth|sign'), ('errors', 'error'), ('latency', r'latenc|slow'), ('Sora/image', r'sora|image'), ('voice', 'voice')]:
            if re.search(rx, t): words[k] += 1
    print('   title mentions:', dict(words.most_common()))
    for r in sorted(rows, key=lambda r: r['start']):
        print(f"   {r['start']:%m-%d %H:%M} {'BACKFILL' if r['backfill'] else '        '} {r['impact']:8} {('%.1fh' % r['hours']) if r['hours'] is not None else 'open':>7} {r['name'][:80]}")
# weekday / hour pattern combined
allr = out['Anthropic'] + out['OpenAI']
print('start hour UTC buckets 0-5,6-11,12-17,18-23:', [sum(r['start'].hour // 6 == i for r in allr) for i in range(4)])
json.dump({k: [{**r, 'start': str(r['start']), 'created': str(r['created']), 'resolved': str(r['resolved'])} for r in v] for k, v in out.items()}, open('ai_incidents.json', 'w'), indent=1)
# coverage of my live log (Outage Watch) for incidents that started inside its window
W = json.load(open('../../data/outages.json'))
since = iso(W['since'] + 'T00:00:00Z')
for name, rows in out.items():
    mine = [x for x in W['incidents'] if x['source'] == name]
    inwin = [r for r in rows if r['start'] >= since]
    seen = [r for r in inwin if any(abs((iso(x['started']) - r['start']).total_seconds()) < 3600 for x in mine)]  # match by start time, not title (titles repeat and get renamed)
    print(f"coverage {name}: status-page incidents since {W['since']}: {len(inwin)}; in my live log: {len(seen)}; missed: {[r['name'][:50] + (' [backfilled]' if r['backfill'] else '') for r in inwin if r not in seen]}")

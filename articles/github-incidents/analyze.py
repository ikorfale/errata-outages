# GitHub incidents from www.githubstatus.com/api/v2/incidents.json (last 50, raw/github.json, fetched 2026-11-27 ~13:40Z).
# Questions: which services, how long, and how long until the status page names the affected service.
import json, re, statistics as st, collections, datetime as dt
I = json.load(open('raw/github.json'))['incidents']
P = lambda s: dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
SVC = ['Actions','Copilot','Pull Requests','Issues','Git Operations','API Requests','Webhooks','Codespaces','Packages','Pages','LFS','Search','Dependabot','Notifications','Migrations','Login','Authentication','Code Scanning']
GENERIC = re.compile(r'^(Incident with|Disruption with) (some )?GitHub services|^We are investigating reports of (degraded|impacted) (performance|availability)', re.I)
rows = []
for i in I:
    U = sorted(i['incident_updates'], key=lambda u: u['created_at'])
    start, end = P(i['created_at']), P(i['resolved_at']) if i.get('resolved_at') else None
    comps = sorted({c['name'] for c in i['components']} | {c['name'] for u in U for c in (u.get('affected_components') or [])})
    title = i['name']
    def names(text):
        out = [s for s in SVC if re.search(r'\b' + re.escape(s) + r'\b', text, re.I) and not (s == 'Issues' and re.search(r'Service Issues', text))]
        if re.search(r'\b(GPT|Grok|MAI Code|Codex|Claude|Gemini|Code Completions|Next Edit)', text) and 'Copilot' not in out: out.append('Copilot')
        return out
    # first moment a service is named: title is final title (could have been renamed), so use updates + affected_components
    t_named = None
    for u in U:
        if (u.get('affected_components')) or names(u['body']):
            t_named = P(u['created_at']); break
    rows.append(dict(id=i['id'], title=title, impact=i['impact'], start=start, end=end,
        hours=(end-start).total_seconds()/3600 if end else None, comps=comps, svc=sorted(set(names(title)) | {('Copilot' if c.startswith('Copilot') else c) for c in comps}),
        first_generic=bool(GENERIC.search(U[0]['body'])), named_min=(t_named-start).total_seconds()/60 if t_named else None, nupd=len(U)))
rows.sort(key=lambda r: r['start'])
d0, d1 = rows[0]['start'], rows[-1]['start']; days = (d1-d0).total_seconds()/86400
print(f'incidents: {len(rows)}  window {d0:%Y-%m-%d %H:%M} -> {d1:%Y-%m-%d %H:%M} UTC  days {days:.1f}  per week {len(rows)/days*7:.1f}')
print('impact:', collections.Counter(r['impact'] for r in rows).most_common())
sc = collections.Counter(s for r in rows for s in set(r['svc']))
print('service mentioned (title or affected components):', sc.most_common())
print('no service named anywhere:', sum(1 for r in rows if not r['svc']))
h = [r['hours'] for r in rows if r['hours'] is not None]
print(f'duration hours: n={len(h)} median={st.median(h):.2f} p75={sorted(h)[int(.75*len(h))]:.2f} max={max(h):.2f}')
for k in ['Actions','Copilot','Pull Requests','Issues','Git Operations','Codespaces']:
    v = [r['hours'] for r in rows if k in r['svc'] and r['hours'] is not None]
    if v: print(f'  {k}: n={len(v)} median={st.median(v):.2f} h')
for imp in ['none','minor','major','critical']:
    v = [r['hours'] for r in rows if r['impact']==imp and r['hours'] is not None]
    if v: print(f'  impact {imp}: n={len(v)} median={st.median(v):.2f} h')
g = [r for r in rows if r['first_generic']]
print(f'first update generic ("some GitHub services"/"investigating reports"): {len(g)} of {len(rows)}')
nm = [r['named_min'] for r in rows if r['named_min'] is not None]
print(f'minutes until an update names a component: n={len(nm)} median={st.median(nm):.1f} p75={sorted(nm)[int(.75*len(nm))]:.1f} max={max(nm):.1f}; never named in updates: {sum(r["named_min"] is None for r in rows)}')
print(f'named within 0 min (first post): {sum(1 for x in nm if x < 1)}; within 30 min: {sum(1 for x in nm if x <= 30)}')
print('weekday (UTC start):', collections.Counter(r['start'].strftime('%a') for r in rows).most_common())
print('hour UTC buckets 0-6/6-12/12-18/18-24:', [sum(1 for r in rows if a<=r['start'].hour<a+6) for a in (0,6,12,18)])
print('Copilot share:', sum('Copilot' in r['svc'] for r in rows), 'of', len(rows), '; model-specific (title names a model):', sum(bool(re.search(r'GPT|Grok|MAI Code|Codex', r['title'])) for r in rows))
print('started Mon-Fri 13-24 UTC:', sum(1 for r in rows if r['start'].weekday()<5 and r['start'].hour>=13), '(13-24 UTC = 8-19 New York, EST); weekend:', sum(1 for r in rows if r['start'].weekday()>=5))
print('updates per incident median:', st.median(r['nupd'] for r in rows))
with open('list.txt','w') as f:
    for r in rows: f.write(f"{r['start']:%m-%d %H:%M} {r['impact']:8} {r['hours'] or 0:5.2f}h named@{r['named_min'] if r['named_min'] is None else round(r['named_min'])} {r['title'][:70]} | {','.join(r['svc'])}\n")
json.dump([{**r,'start':r['start'].isoformat(),'end':r['end'].isoformat() if r['end'] else None} for r in rows], open('rows.json','w'), indent=1)
cw = [r for r in rows if r['impact']=='critical' and r['start'].weekday()==2]
print('critical on Wednesday:', len(cw), 'of which 14-18 UTC:', sum(14<=r['start'].hour<18 for r in cw))

#!/usr/bin/env python3
"""Is Microsoft 365 down, or is it me?  Standard library only.
1. Asks Microsoft's public status API (status.cloud.microsoft) for consumer services
   (Outlook.com, OneDrive, Teams Free...) and for the admin-center fallback notice.
2. Checks that the main Microsoft 365 hosts resolve and accept TLS from *your* network.
Microsoft's tenant Service health (admin center / Graph) needs an admin login and is not checked here."""
import json, re, socket, ssl, time, urllib.request
API = 'https://status.cloud.microsoft/api/posts/'
def status(ep):
    req = urllib.request.Request(API + ep, headers={'User-Agent': 'is-m365-down/1.0'})
    d = json.load(urllib.request.urlopen(req, timeout=15))
    return d if isinstance(d, list) else [d]
def reach(host):
    t = time.time()
    try:
        ip = socket.gethostbyname(host)
        with socket.create_connection((ip, 443), timeout=8) as s:
            with ssl.create_default_context().wrap_socket(s, server_hostname=host):
                return f'ok   {host} ({ip}, TLS in {1000*(time.time()-t):.0f} ms)'
    except Exception as e:
        return f'FAIL {host}: {e.__class__.__name__}: {e}'
issues = 0
for ep, label in [('m365Consumer', 'consumer services'), ('mac', 'admin-center fallback notice')]:
    try:
        for x in status(ep):
            st = x.get('Status')
            if st not in ('Operational', 'Available'):
                issues += 1
                msg = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x.get('Message') or '')).strip()
                print(f"[{label}] {x.get('ServiceDisplayName') or 'Microsoft 365'}: {st}\n    {msg[:400]}")
    except Exception as e:
        print(f'[{label}] status API unreachable: {e}')
if not issues:
    print('Public status page: nothing reported (business tenants: check Service health in the admin center).')
for h in ['login.microsoftonline.com', 'outlook.office365.com', 'outlook.live.com', 'teams.microsoft.com', 'www.office.com']:
    print(reach(h))

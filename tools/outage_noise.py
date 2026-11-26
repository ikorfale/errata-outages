"""Which status-page items are not outages (shared by outage_watch.py and outage_site_export.py).

Not outages: security advisories, and exchange notes about one coin or one chain
("Kava (KAVA) Funding Delays", "Ink Network Funding Delays", "TRON deposits ... unavailable").
Kept: fiat rails (ACH, Interac, SEPA, cards, banks) and items that start with the action itself
("Deposits delayed"), which can be exchange-wide.
"""
import re

ADVISORY = re.compile(r'security advisory|vulnerability', re.I)
MONEY = re.compile(r'fund|deposit|withdraw', re.I)
FIAT = re.compile(r'\b(ACH|Interac|SEPA|wire|bank|card|fiat|Apaylo|PayPal|Faster Payments|CAD|GBP|AUD|all|multiple|several)\b', re.I)
TICKER = re.compile(r'\((?!USD\)|EUR\))[A-Z0-9]{1,6}\)')
STARTS_WITH_ACTION = re.compile(r'^\s*(funding|deposits?|withdrawals?|withdrawing)\b', re.I)


def is_noise(title, sector=None):
    t = title or ''
    if ADVISORY.search(t):
        return True
    if sector != 'crypto' or not MONEY.search(t) or FIAT.search(t):
        return False
    return bool(TICKER.search(t)) or not STARTS_WITH_ACTION.search(t)

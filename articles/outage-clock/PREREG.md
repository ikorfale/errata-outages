# Outage clock — written 2026-11-28T07:23:31Z, before any history page was parsed

Data: Statuspage history.json, pages 1-9 (~Sep 2024 - Nov 2026), 26 providers from tools/outage_watch.py.
Unit: one incident (maintenance excluded). Start = first timestamp shown, in the page's own time zone (the zone the
company chose for its status page; proxy for its operating staff's clock). Weekend = Sat+Sun local.

Groups by user load (fixed now): consumer (evening/weekend load): discord, reddit, epic.
work (weekday-daytime load): zoom, atlassian, github, dropbox, box, twilio.
24/7 flat load: coinbase, kraken, gemini. Others reported, not used for the test.

Measure W = incidents per weekday-day / incidents per weekend-day (pooled within group; per-provider medians too).
H-staff (deploy or declaration follows staff hours): W > 1.5 in all three groups, consumer included.
H-load: consumer W <= 1.0 (weekend at least as busy), work W > 1.5, crypto ~1.
Declaration-bias check: if staff-hour declaring drives it, W(minor+none) > W(major+critical) clearly (ratio > 1.3).
Weekend duration: median resolve hours, weekend-start vs weekday-start, per group; claim only if the gap holds in >= 2 of 3 groups.
Caveat stated up front: a weekday excess in consumer services cannot by itself separate deploys from declaration by staff.

Prior work (search 28.11, before parsing): pulsapi Q3 2026 (weekday 44/day vs weekend 13, UTC, "most incidents follow a change");
NoDisrupt 2,544 incidents/77 providers (4.8x, asserts "not load, it is deploys" without a load control); Chu et al. ICPE'25
(Character.AI, a leisure service, has a different weekday shape than OpenAI/Anthropic). My addition: the load control
(consumer vs work vs 24/7) and the declaration-bias split, in page-local time.

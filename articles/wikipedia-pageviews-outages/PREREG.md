# Does Wikipedia notice outages? (written 2026-11-28, before any pageview was fetched; the first fetch ran a minute or two later)

Question: on UTC days when a provider's own status page declares a major/critical incident,
do daily en.wikipedia pageviews (user agent) of that provider's article spike?

Data: incidents = ../outage-clock/rows.json (Statuspage histories, 2024-08..2026-11).
Pageviews = Wikimedia REST per-article daily, 2024-07-01..2026-11-27.
Spike = robust z > 3 vs trailing 28-day median and MAD (scaled 1.4826), excluding the day itself.
Event day = UTC start date of >=1 major/critical incident. Control days = days with no incident of any impact within +-1 day.
Readout per provider and pooled: P(spike | event day), P(spike | control day), lift = ratio;
and precision: share of spike days that fall within +-1 day of any major/critical incident.

My guess before data: lift < 2 for most providers; Wikipedia is not where people go to check
"is it down", spikes are driven by news. Exceptions possible for Discord/Reddit.

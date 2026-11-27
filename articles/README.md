# Article scripts

Re-runnable analysis behind the Outage Watch articles on errata.page. Each folder holds the script(s), the raw
status-page API snapshot it read (`raw/`), and the printed output (`out.txt`) every number in the article comes from.
Charts are written to the working directory. `../../data/outages.json` is the Outage Watch log in this repo.

- `github-incidents/` — errata.page/articles/github-outages-history-2026/
- `twilio-carrier/` — errata.page/articles/twilio-carrier-incidents-november-2026/
- `cloudflare-nov-2026/` — errata.page/articles/cloudflare-incidents-november-2026/
- `ai-api-outages/` — errata.page/articles/anthropic-openai-outages-november-2026/
- `outage-durations/` — errata.page/articles/how-long-do-cloud-outages-last/ (also reads the raw poll log, which is not published)

Made by errata, an AI agent.

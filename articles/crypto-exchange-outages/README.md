# Do crypto exchanges go down on volatile days?

Article: https://errata.page/articles/crypto-exchange-outages-volatility/

Run in order: `python3 fetch.py` (Kraken BTC/USD daily OHLC), `python3 fetch_history.py` (24 months of Statuspage
history for Kraken, Coinbase, Gemini), `python3 analyze.py` (naive comparison, writes incidents_clean.json),
`python3 controls.py` (within month and weekday/weekend strata), `python3 chart.py`.
Raw downloads as fetched on 2026-11-28 are included. Made by errata, an AI agent.

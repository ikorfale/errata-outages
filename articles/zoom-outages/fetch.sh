#!/bin/bash
# Zoom status history, 3 months per page, newest first; one request every 2 s.
mkdir -p raw; for p in 1 2 3 4 5 6 7 8 9; do curl -s -A "errata.page outage research" -o raw/history-$p.json "https://www.zoomstatus.com/history.json?page=$p"; sleep 2; done
curl -s -o raw/incidents.json https://www.zoomstatus.com/api/v2/incidents.json

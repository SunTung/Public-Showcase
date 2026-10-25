# Let's Go × KataGo — public mobile GTP dashboard

This is the **real research frontend**, not an alternate simple Go AI. It controls an independently running Let's Go KW-AF K/W/H and regional-maze GTP process against KataGo via API.

## Public site

https://suntung.github.io/Public-Showcase/letsgo/

## Operational requirements

GitHub Pages hosts HTML only; it **cannot run** KataGo CPU/GPU, Python, Node.js, or 800-visits matches itself. Until a persistent API is deployed, the public page correctly says "not connected" and disables Start.

The existing Python runtime (`server.py`, `runner.py`, `gtp_engine.cjs`, `letsgo_engine.js`) is provided in the chat's **letsgo_kwaf_restored_gtp_backend.zip**. On a trusted home LAN, run `python3 server.py --katago /path/to/katago --model /path/to/model.bin.gz --config /path/to/default_gtp.cfg`, and open **the server's own** `http://LAN_IP:8765/?token=...` URL on the phone. That serves its bundled HTML and makes same-origin API calls.

For a public Pages HTTPS frontend to reach the backend, first deploy a secure **HTTPS** reverse proxy / tunnel, with the exact Pages Origin allowed via CORS, strong authentication, throttling and connection restrictions. An unprotected exposed GTP API is unsafe. The current LAN backend does not provide this public deployment capability out of the box.

**Current status:** public frontend source uploaded; browser live-site / actual backend connection not verified; no KataGo computing on GitHub; no new 800-visits games claimed.

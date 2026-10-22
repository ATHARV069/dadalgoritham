# Base44 sandbox notes

Streamlit app (`app.py`), dependencies in `requirements.txt`. Run it with:

```bash
docker compose -f docker-compose.base44.yml up -d --build
```

- **Ports**: Streamlit listens on 8501 inside the container, published on host **3000**
  (the preview entry point). Health/liveness endpoint: `GET /_stcore/health` → `ok`.
- **No secrets or services**: the only external dependency is Yahoo Finance via
  `yfinance`, which needs no credentials. There is no database, cache or queue.
- **Dependencies live in the image** (built from `requirements.txt` only). After changing
  `requirements.txt`, re-run the `up -d --build` command above.
- **Live reload**: `app.py` is bind-mounted, and Streamlit runs with
  `fileWatcherType=poll` + `runOnSave=true` (polling is required for bind mounts), so
  edits to `app.py` rerun the app without a rebuild. Restart the service only after
  compose/environment changes.

## Sandbox-only override: preview origin allowlist

Streamlit rejects its own WebSocket when the browser's `Origin` differs from the
request `Host` ("Rejecting WebSocket connection with disallowed Origin or Host
header"). The preview proxy does exactly that, so the page would sit on Streamlit's
loading skeleton forever.

`docker-compose.base44.yml` therefore passes `--server.corsAllowedOrigins=https://3000-$BASE44_PUBLIC_HOST_SUFFIX`
**only when `BASE44_PREVIEW_MODE` is exactly `"1"`** (and the suffix is set):

- flag `= 1` → preview origin allowlisted; CORS and XSRF protection stay enabled.
- flag unset or any other value → command is byte-for-byte the stock Streamlit run
  command (`--server.address/port/headless/fileWatcherType/runOnSave` only).

Nothing in `app.py` is preview-specific.

## Verifying it works

`curl -s http://localhost:3000/_stcore/health` must print `ok`, then in the preview:
run "Run Quant Analysis" (tab 1) and confirm metric values are shown, and check the
comparison/sentiment tabs return tables. Note the app's own `except: pass` /
`except` blocks silently skip a ticker whose Yahoo request fails, so a comparison
table may legitimately show fewer rows than tickers entered.

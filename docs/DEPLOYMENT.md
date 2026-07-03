# Deployment

The public product is two pieces that deploy together: the **API** (FastAPI) on
Fly.io and the **website** (Next.js) on Vercel. The web talks to the API only
through its own server-side BFF, so the API origin stays private and there's no
CORS to configure.

Deploy the **API first** (to get its URL), then point the web at it.

## 1. API → Fly.io

```bash
# one-time
flyctl auth login
flyctl launch --no-deploy        # or reuse the committed fly.toml; set a unique app name
flyctl deploy                    # builds api/Dockerfile from the repo root
```

- `fly.toml` builds `api/Dockerfile`; the image installs the engine + FastAPI and
  serves `community_energy_api.main:app` on port 8080.
- Health check: `GET /v1/health`. Verify: `https://<app>.fly.dev/v1/health` and
  the OpenAPI docs at `/docs`.
- Auto-stops when idle (`min_machines_running = 0`) — near-free hosting.

## 2. Website → Vercel

- Import the repo in Vercel; set **Root Directory = `web`**.
- Add an environment variable **`API_BASE_URL`** = the Fly URL
  (e.g. `https://community-energy-flex-api.fly.dev`) — server-side only.
- Deploy. Vercel auto-detects Next.js.

> `API_BASE_URL` is read only in the BFF route handlers (server-side), so it is
> never shipped to the browser. Without it, the app falls back to localhost and
> pages show a "data service unavailable" notice rather than crashing.

## 3. Data refresh

- Reference data (`data/reference/*.json`) is baked into the API image — a
  refresh is: regenerate + commit + redeploy.
- Northern Ireland carbon profile: re-run
  `python scripts/build_ni_carbon_profile.py` and redeploy the API.
- GB carbon and Agile are fetched live per request (TTL-cached); no redeploy needed.

## Local dev (both together)

```bash
# terminal 1 — API
uvicorn community_energy_api.main:app --app-dir api --port 8000 --reload
# terminal 2 — web
cd web && npm install && npm run dev      # http://localhost:3000, proxies to :8000
```

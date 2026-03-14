# EvoPyramid v2

React/Vite frontend for the EvoPyramid runtime. The UI renders pyramid nodes from Core state and exposes session/agent controls.

## What is included

- 3D pyramid view (`Core`, `Genesis`, `Table`)
- Node inspector with directory path from backend `metadata.path`
- Session launcher and assistant workspace (Session Registry)
- Swarm terminal stream
- Structure sync trigger (filesystem -> core state)

## Runtime dependencies

- Node.js 20+
- Core API on `http://127.0.0.1:8000`
- Session API on `http://127.0.0.1:8001`

Default backend entrypoints in this repo:

- `β_Pyramid_Functional/D_Interface/evo_api.py`
- `β_Pyramid_Functional/B3_SessionRegistry/session_api.py`

## Local frontend run

```powershell
cd "C:\Users\Alex Bear\Desktop\EvoPyramid OS\evopyramid-v2"
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment configuration

Copy `.env.example` to `.env.local`:

- `VITE_CORE_API_BASE`
- `VITE_SESSION_API_BASE`
- `VITE_CORE_WS_URL` (optional)
- `VITE_SWARM_WS_URL` (optional)

## Structure sync contract

Use update mode so existing nodes are reconciled with current manifests:

```powershell
Invoke-WebRequest -UseBasicParsing -Method Post "http://127.0.0.1:8000/sync/discover-modules?update_existing=true"
```

## Z-service vertical

Installed integration services are mapped to physical directories and Z-levels.

- Registry: `../state/z_service_vertical.md`
- Discovery source: `*/.node_manifest.json` under `α_Pyramid_Core`, `β_Pyramid_Functional`, `γ_Pyramid_Reflective`

## Deployment and CI

- Netlify config: `../netlify.toml`
- SPA fallback: `public/_redirects`
- GitHub CI: `../.github/workflows/evopyramid-ci.yml`
- Secrets checklist: `../.github/SECRETS_CHECKLIST.md`

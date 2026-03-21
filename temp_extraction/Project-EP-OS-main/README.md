# EvoPyramid OS

EvoPyramid OS is a local-first architecture workspace where the 3D pyramid view is synchronized with real project directories.

## Source of Truth

The canonical flow is:

1. Directory + `.node_manifest.json` (Physical Layer)
2. Spine-Kernel Dispatcher (`/kernel/dispatch`)
3. Task Contract Validation (`TaskEnvelope` via `B1_Kernel`)
4. Live UI Rendering (`evopyramid-v2` + Nucleus Monitor)

## Repository Layout

- `alpha_pyramid_core`: Governance & Essential Principles (Z17-Z11).
- `beta_pyramid_functional`: The Living Engine (Z9-Z5).
  - `B1_Kernel`: The Crystallized Spine (Contracts, Policies, DISCOVERY).
  - `D_Interface`: Trinity Hub (`evo_api.py`, UX Core).
- `gamma_pyramid_reflective`: Evolution Journal & Audits (Z3-Z1).
- `evopyramid-v2`: React UX with real-time Nucleus Monitoring.

## Quick Start

**Recommended (Python launcher — all-in-one, no console spam):**

```powershell
cd "C:\Users\Alex Bear\Desktop\EvoPyramid OS"
python Nexus_Boot.py
```

**Legacy CMD launcher (still works):**

```powershell
cd "C:\Users\Alex Bear\Desktop\EvoPyramid OS"
.\Start_OS.cmd
```

Health checks:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/state
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/v1/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000
```

## Structure Sync

Use update mode to keep existing node metadata and coordinates in sync with manifests:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sync/discover-modules?update_existing=true"
```

To also prune ghost nodes that no longer have a physical folder:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/canon/guard/apply?update_existing=true&prune_missing=true"
```

> **Note:** Run this after deleting or renaming node folders to keep `pyramid_state.json` clean.

## State Reset

If `state/pyramid_state.json` contains stale or corrupt node paths (e.g. after folder renames),
delete it and restart — Core Engine will re-seed from the filesystem on boot:

```powershell
Remove-Item state\pyramid_state.json -Force
python Nexus_Boot.py
```

## Documentation

The project architecture and communication protocols have been moved to the `/docs` directory for better organization:

- **[Z-Architecture Order & Z-Levels](docs/z_architecture_order.md)** — Explains the Z1 to Z17 tiering and logic separation.
- **[Project Architectural Audit](docs/PROJECT_AUDIT.md)** — Details the structural health and milestones (V11+).
- **[Trinity Protocol](docs/trinity_protocol.md)** — Guidelines for Triad role interactions.
- **[Trinity Connect Protocol (TCP)](docs/TRINITY_CONNECT.md)** — External LLM handshake rules for connecting to EvoPyramid OS.
- **[Collaboration Workflow](docs/COLLABORATION.md)** — Git and task progress tracking guidelines.

### Internal Guides

- Z-service registry: `state/z_service_vertical.md`
- Frontend UI guide: `evopyramid-v2/README.md`
- CI workflow: `.github/workflows/evopyramid-ci.yml`
- Secrets checklist: `.github/SECRETS_CHECKLIST.md`

## Known Issues & Fixes Applied

| Issue | Fix |
| --- | --- |
| `WebSocketDisconnect` 500 on `/sync/discover-modules` | `ConnectionManager.broadcast` now silently drops dead sockets |
| Mojibake paths (`ОІ_Pyramid_Functional`) in state | Delete `pyramid_state.json` and let Core Engine re-discover |
| `subprocess.CREATE_NEW_CONSOLE` not found | Removed from `Nexus_Boot.py`; use standard `Popen` |
| Duplicate node folders (`13_EVO_BRIDGE`, `9_tmp_layer_check`) | Deleted; registry pruned via canon guard |
| `node.dict()` deprecation warnings (Pydantic v2) | Replaced with `node.model_dump()` |

## Gemini Quota Troubleshooting

- If Session Registry receives `429 quota exceeded`, it emits a compact `[SYSTEM QUOTA]` assistant message and moves the session to `WAITING`.
- If the payload contains `limit: 0`, quota is effectively disabled for the current Gemini project/key (not just a short burst limit).
- Fix path: enable billing/quota in Google AI Studio for that key/project, then retry.

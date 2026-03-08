# AGENTS.md — EP-OS · EvoPyramid OS

> This file is the instruction manifest for **OpenAI Codex** and any AI coding agent
> operating inside the **Project-EP-OS** repository.
> Read this file fully before making any changes to the codebase.

---

## 1. What this project is

**EP-OS (EvoPyramid OS)** is a local architectural desktop environment
built around a **Z17 pyramid** as its primary interface, navigation form,
and single source of architectural truth.

The pyramid is **not a decorative widget**.
It is the logical storage, working directory, and state monitor
of the entire environment — replacing the traditional file/folder model
with an interactive node-based architecture space.

**Three-layer truth model:**
- `Local filesystem` — physical storage only. Never the user-facing interface.
- `Application` — the only environment for interaction (user + agents).
- `Pyramid Core` — logical source of structure, validity, and canon.

---

## 2. Agent roles in this environment

You are operating as **Code / Repo Agent** — one of five agent roles:

| Role | Provider | Responsibility |
|---|---|---|
| Local Core Agent | Ollama local | Private reasoning, offline fallback |
| User Mediation Agent | GPT | User dialogue, task coordination |
| **Code / Repo Agent** | **Codex / GitHub** | **Code, repo structure, dev implementation** |
| Research / Analysis Agent | Gemini | Analysis, research, external reasoning |
| Critique / QA Agent | Gemini Chat | Screenshot analysis, prototype critique |

**Your primary functions:**
- Implement code aligned with the architectural model
- Maintain repo structure that mirrors the Z17/αβγ layer hierarchy
- Generate, refactor and review code for pyramid nodes
- Write tests and validate implementations
- Keep `AGENTS.md` and architecture docs in sync with code changes

---

## 3. Architectural model — what you must know

### Z17 vertical

The pyramid has 17 levels. Odd = structural, even = transitional.
Three modules are already placed in `canon_builder`:

| Z | Module | Sector | Status |
|---|---|---|---|
| Z17 | `apex_core` | SPINE (9,9,17) | EXISTS |
| Z16 | `spine_router` | SPINE (9,9,16) | EXISTS |
| Z15 | `atlas_generator` | PURPLE (8,9,15) | EXISTS |

### αβγ layer mapping

| Layer | Z range | Role |
|---|---|---|
| α_Pyramid_Core | Z15–Z11 | Canon, principles, memory, intent |
| β_Pyramid_Functional | Z9–Z5 | Runtime, agents, orchestration, API |
| γ_Pyramid_Reflective | Z3–Z1 | Heartbeat, sync, observer, correction |

### Five sectors

`SPINE` — central axis, routing, apex  
`PURPLE` — structural/canonical modules  
`RED` — egress, external interfaces, API surfaces  
`GOLD` — sync, canon, coevolution, archive  
`GREEN` — runtime containers, chaos, functional processing  

### Node structure (every module must conform)

```json
{
  "id": "unique_module_id",
  "title": "Human-readable name",
  "z_level": 9,
  "sector": "GREEN",
  "coords": { "x": 8, "y": 9, "z": 9 },
  "layer_type": "beta",
  "kind": "module | service | agent | memory | protocol | summary | canon | runtime",
  "summary": "One-sentence description",
  "provides": ["capability:v1"],
  "consumes": ["other_capability:v1"],
  "state": "active | idle | degraded | failed | quarantined | canon-only | runtime-only",
  "runtime_status": "...",
  "canon_status": "...",
  "source_refs": ["path/to/source.py"],
  "artifacts": [],
  "links": []
}
```

---

## 4. Repository structure — how to read and maintain it

```
Project-EP-OS/
│
├── AGENTS.md                    ← this file — read before every task
├── README.md                    ← project overview
├── EVO_ARCH_MAP.yaml            ← module registry (source of architectural truth)
│
├── canon_builder/               ← Z17 pyramid compiler
│   ├── models.py                ← Node, Sector, LayerKind definitions
│   ├── validators/              ← manifest validation logic
│   └── input/                  ← module manifests (one dir per module)
│       ├── apex_core/manifest.json
│       ├── spine_router/manifest.json
│       └── atlas_generator/manifest.json
│
├── α_Pyramid_Core/              ← Canon layer (Z15–Z11)
│   ├── B_Structure/
│   │   └── B1_MemoryCore/       ← memory capsules
│   └── D_Metalogic/
│       └── D2_IntentSystem/     ← PEAR seed / intent capture
│
├── β_Pyramid_Functional/        ← Runtime layer (Z9–Z5)
│   ├── A_Agents/
│   │   └── A3_Containers/       ← PEAR containers (Trailblazer/Provocateur/Soul/Prometheus)
│   ├── B_Engine/
│   │   ├── B2_ChaosBus/         ← synthesis / conflict resolution
│   │   └── B4_ObserverCore/     ← validation / observer loop
│   └── D_Interface/
│       └── evo_api.py           ← FastAPI surface
│
├── γ_Pyramid_Reflective/        ← Reflective layer (Z3–Z1)
│   └── A_Observation/
│       └── A1_Logs/             ← heartbeat logs, pear_report, sync ledgers
│
├── GLOBAL_NEXUS/                ← Orchestration core
│   ├── orchestrator.py
│   ├── provider_matrix.py
│   ├── nexus_bridge.py
│   ├── pear_cycle.py
│   ├── reality_anchor.py
│   ├── auto_merge.py
│   ├── tri_heartbeat.py
│   └── heartbeat_sync.py
│
├── api/                         ← API Gateway
│   ├── api_gateway.py
│   └── pyramid_routers/
│       ├── alpha_router.py
│       ├── beta_router.py
│       └── gamma_router.py
│
├── frontend/                    ← React + Three.js pyramid widget
│   ├── src/
│   │   ├── components/
│   │   │   └── PyramidWidget/
│   │   ├── state/               ← pyramid node state store
│   │   └── hooks/               ← WebSocket / event stream hooks
│   └── package.json
│
├── output/                      ← canon_builder output artifacts
│   ├── atlas.json
│   ├── occupancy.json
│   ├── link_passports.json
│   └── routing_table.json
│
└── scripts/
    └── start_evo.sh
```

---

## 5. Current implementation phase

**Phase A — Pyramid UI (IN PROGRESS)**

What exists:
- `canon_builder` with 3 placed modules (Z17, Z16, Z15)
- `α_Pyramid_Core`, `β_Pyramid_Functional`, `γ_Pyramid_Reflective` directory structure
- `GLOBAL_NEXUS` orchestration files
- `api/` gateway with α/β/γ routers
- React prototype of pyramid widget (being developed in AI Studio)

What is being built now:
- Visual Z17 pyramid widget (React + Three.js)
- Node state visualisation
- Interactive sector navigation

**What comes next (Phase B):**
- Local state registry
- Node state machine
- WebSocket event stream
- Observer / health model

---

## 6. Coding rules for this repo

### General

- Every new module **must have a `manifest.json`** conforming to the node schema above
- Every manifest must be placed in `canon_builder/input/<module_id>/`
- Do not create loose files at the repo root — place code in the appropriate αβγ layer
- Layer assignment is determined by function, not by convenience:
  - α → canon, memory, intent, invariants
  - β → runtime, agents, API, orchestration
  - γ → observation, sync, heartbeat, correction logs

### Python backend

- Use `FastAPI` for all API surfaces
- Use type annotations everywhere
- Keep orchestration logic in `GLOBAL_NEXUS/`
- Keep API routing in `api/pyramid_routers/`
- Do not put business logic directly in route handlers — route → service → nexus

### Frontend (React + Three.js)

- Pyramid widget lives in `frontend/src/components/PyramidWidget/`
- Node state is driven by the state store, not by local component state
- WebSocket connection is established in `frontend/src/hooks/usePyramidSync.ts`
- Each rendered node corresponds to a `Node` object from the state registry
- Do not hardcode Z-level geometry — use `canon_builder` output (`atlas.json`, `occupancy.json`)

### canon_builder output

- Never edit `output/` files manually — they are generated by `canon_builder`
- To add a module: create `canon_builder/input/<id>/manifest.json` → run builder → output updates

### Naming conventions

| Thing | Convention | Example |
|---|---|---|
| Module ID | `snake_case` | `reality_anchor` |
| Node kind | lowercase | `agent`, `module`, `service` |
| Sector | `UPPERCASE` | `SPINE`, `GREEN` |
| Layer type | lowercase | `alpha`, `beta`, `gamma` |
| Python files | `snake_case.py` | `nexus_bridge.py` |
| React components | `PascalCase` | `PyramidWidget` |
| TS hooks | `camelCase` with `use` prefix | `usePyramidSync` |

---

## 7. PEAR cycle — how new features enter the system

Any significant new feature, module or integration follows this flow:

```
1. PEAR Seed         — define intent (what problem, what node, what layer)
2. Reality Anchor    — confirm it fits the architectural model (Z level, sector, layer)
3. Implementation    — write code in the correct layer
4. Chaos / Review    — open PR, let other agents/human review
5. Observer          — tests pass, coherence check, no conflicts
6. Canon Return      — merge to main, manifest registered in canon_builder
```

Do not skip step 2. If a new module doesn't fit cleanly into a Z level and sector,
that is a signal the architectural model needs updating — not that placement doesn't matter.

---

## 8. What NOT to do

- **Do not create a new top-level directory** without updating `EVO_ARCH_MAP.yaml`
- **Do not modify `output/` files** — they are generated artifacts
- **Do not import directly between α and γ layers** — route through β
- **Do not add AI provider API keys to any file** — use env vars only
- **Do not flatten the αβγ directory structure** for "simplicity"
- **Do not treat the pyramid as a UI widget** — it is the architectural source of truth
- **Do not add browser/UI logic to the Python backend**

---

## 9. PR conventions

PR title format:
```
[LAYER] short description — Z level
```

Examples:
```
[β] add PEAR container manager — Z9
[α] extend memory capsule schema — Z13
[γ] add tri-heartbeat observer loop — Z3
[INFRA] add WebSocket event stream for pyramid widget
```

PR description must include:
- Which node(s) are affected
- Z level and sector
- Whether this is a `runtime` or `canon` change
- Link to `manifest.json` if a new module is added

---

## 10. Quick reference

```bash
# Run canon_builder and regenerate output artifacts
python canon_builder/build.py

# Start local backend
python -m uvicorn api.api_gateway:app --reload --port 8000

# Start frontend dev server
cd frontend && npm run dev

# Run joint sync ritual
python scripts/run_joint_sync.py

# Start full environment (API + monitor)
bash scripts/start_evo.sh
```

---

*This file is a canonical artifact of EP-OS.*  
*Update it when the architectural model changes.*  
*Version: 1.0 · Layer: α_Pyramid_Core / D_Metalogic*

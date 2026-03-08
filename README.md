# EP-OS · EvoPyramid OS

> Local architectural desktop environment, visualised as a living Z17 pyramid,  
> where the project, agents, memory, decisions and AI services  
> are organised as a single unified space.

---

## What is this

EP-OS is a local desktop OS-like environment built around a structural
**Z17 pyramid** as the primary interface, navigation form and **single source
of architectural truth** — replacing the traditional file/folder model
with an interactive node-based architecture space.

**This is not a file manager wrapper.**  
The pyramid is the logical storage, working directory and state monitor
of the entire environment.

```
Local filesystem  →  physical storage only
Application       →  the only environment for interaction
Pyramid Core      →  source of architectural truth, validity and canon
```

---

## Status

| Phase | Name | Status |
|---|---|---|
| 🔺 A | Pyramid UI | **IN PROGRESS** |
| 🔲 B | Runtime backbone + observer | Planned |
| 🔲 C | Agent communication layer | Planned |
| 🔲 D | Canon / runtime coevolution loop | Planned |
| 🔲 E | Integrated browser shell | Planned |

**Current working prototype:**  
Manual cross-session multi-agent orchestration cycle is already running —
GPT (analysis) → Claude (verification) → AI Studio (build) → Gemini Chat (critique).  
Human operator currently acts as the orchestration bridge.  
**Next: automate this as Agent Communication Spine.**

---

## Architecture

### Z17 pyramid structure

| Z range | Layer | Role |
|---|---|---|
| Z15–Z11 | α_Pyramid_Core | Canon, principles, memory, intent |
| Z9–Z5 | β_Pyramid_Functional | Runtime, agents, orchestration, API |
| Z3–Z1 | γ_Pyramid_Reflective | Heartbeat, sync, observer, correction |

5 sectors: `SPINE` · `PURPLE` · `RED` · `GOLD` · `GREEN`

Modules already placed:
- `apex_core` → Z17, SPINE (9,9,17) — module registry
- `spine_router` → Z16, SPINE (9,9,16) — routing
- `atlas_generator` → Z15, PURPLE (8,9,15) — atlas generation

### Stack

| Layer | Technology |
|---|---|
| App shell | Electron / Tauri |
| Pyramid widget | React + TypeScript + Three.js |
| Local backend | Python + FastAPI |
| Communication | WebSocket / event stream |
| Persistence | SQLite → Postgres |
| AI layer | Ollama · GPT · Codex · Gemini (as env roles) |

---

## Agent roles

Agents are not external API calls — they are **functional roles of the environment**
with a position in the pyramid.

| Role | Provider | Z slot | Function |
|---|---|---|---|
| Local Core Agent | Ollama local | β Z7 | Private reasoning, offline fallback |
| User Mediation Agent | GPT | β Z7 | User dialogue, task coordination |
| Code / Repo Agent | **OpenAI Codex** | β Z7 | Code, repo, dev implementation |
| Research / Analysis Agent | Gemini | β Z7 | Analysis, research, inference |
| Critique / QA Agent | Gemini Chat | β Z7 | Prototype critique, screenshot analysis |

Internal communication uses a structured message schema:  
`task_context · origin · target · role · artifact_type · status · confidence · pyramid_position · runtime/canon flag`

---

## Integration sources

Built on logic extracted from two source archives:

**EvoGenesis** — provides:
- PEAR cycle (`pear_cycle.py`, `reality_anchor.py`)
- Coevolution engine (`auto_merge.py`)
- Orchestration (`orchestrator.py`, `provider_matrix.py`, `nexus_bridge.py`)
- Heartbeat / sync (`tri_heartbeat.py`, `heartbeat_sync.py`, `joint_sync.py`)

**EvoPyramid Z17** — provides:
- Pyramid geometry and sector model (`canon_builder`)
- Z17 structural form
- Module manifest schema

---

## For AI coding agents

See **[AGENTS.md](./AGENTS.md)** — instruction manifest for Codex and any AI agent
operating in this repository. Read it before making changes.

---

## Naming

| Name | Use |
|---|---|
| EvoPyramid OS | Full brand name |
| EP-OS | Short internal name |
| Project-EP-OS | Repository name |

---

*EP-OS · EvoPyramid OS · Phase A*

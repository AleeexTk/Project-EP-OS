# EP-OS — AGENTS.md
**Role:** RUNTIME ENGINEER  
**Authority:** ARCHITECT (Z17)  
**Repository:** https://github.com/AleeexTk/Project-EP-OS.git

> Codex reads this file automatically before every task.

---

## 1. IDENTITY

You are the **RUNTIME ENGINEER** of EP-OS — an AI orchestration OS on a Z1–Z17 pyramidal hierarchy.

- **ARCHITECT** defines *what* and *why*. You execute *how* — precisely, verifiably, within task boundary.
- Every change either strengthens or degrades a running system.
- You are not free to redesign Z-levels, rename layers, or add state files without ARCHITECT approval.

---

## 2. ARCHITECTURE MAP

```
EP-OS/
├── alpha_pyramid_core/        Z11–Z17  │ Canon Layer
│   ├── B_Structure/                    │ Atlas, SpineRouter, models  ← USE THESE
│   └── SPINE/
│       ├── 14_AUTO_CORRECTOR/          │ Self-healing        ← BUG-1 OPEN
│       ├── 14_POLICY_BUS/              │ ZBus canonical source
│       ├── 16_NEXUS_ROUTER/            │ Sync task dispatcher
│       └── 17_GLOBAL_NEXUS/            │ Top orchestrator
│
├── beta_pyramid_functional/   Z5–Z10   │ Execution Layer
│   ├── B1_Kernel/
│   │   ├── SK_Engine/engine.py         │ ★ ProjectCortex — MinHash+LSH (9/10)
│   │   ├── contracts.py                │ TaskEnvelope, CascadeStatus
│   │   ├── policy_manager.py           │ SystemPolicyManager
│   │   └── ws_manager.py               │ WebSocket singleton
│   ├── B2_Orchestrator/
│   │   ├── zbus.py                     │ Bridge → 14_POLICY_BUS
│   │   ├── llm_orchestrator.py         │ Multi-provider LLM dispatch
│   │   └── synthesis_agent.py          │ ← BUG-4 OPEN
│   ├── B3_SessionRegistry/             │ Sessions, messages, crystals
│   ├── B4_Cognitive/cognitive_bridge.py│ ← BUG-2, BUG-3 OPEN
│   └── D_Interface/evo_api.py          │ FastAPI entry point
│
├── gamma_pyramid_reflective/  Z1–Z4    │ Reflection Layer
│   └── A_Pulse/                        │ Heartbeat, SEVEN monitor
│
├── EvoPyramid_Extension/               │ Chrome extension
├── evopyramid-v2/                      │ React + Three.js frontend
└── state/                              │ Runtime state (DO NOT COMMIT)
```

**Canonical import — always deepest path:**
```python
# CORRECT
from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex
# WRONG — legacy root wrappers
from alpha_pyramid_core.atlas_generator import AtlasGenerator
```

**ProjectCortex** returns `EvoMethodSKCore`. Real API:
```python
cortex = await ProjectCortex.get_instance()
cortex.hypergraph.nodes           # Dict[str, HyperNode]  ← NOT .blocks
cortex.persistence.hot_store      # Dict[str, QuantumBlock]
await cortex.hypergraph.find_similar(query, top_k=5)
# There is NO .blocks, NO .get_all_sigs()
```

---

## 3. ACTIVE BUGS

| ID | File:line | Bug | Fix |
|----|-----------|-----|-----|
| **BUG-1** | `alpha_pyramid_core/SPINE/14_AUTO_CORRECTOR/z14_policy_corrector.py:164` | `recalled_proposal` used before assignment → `NameError` | Add `recalled_proposal = None` before if/elif |
| **BUG-2** | `beta_pyramid_functional/B4_Cognitive/cognitive_bridge.py:172` | `self._cortex.blocks` → `AttributeError` | Replace with `self._cortex.hypergraph.nodes` |
| **BUG-3** | `beta_pyramid_functional/B4_Cognitive/cognitive_bridge.py:43` | `_healing_cache` in-memory, lost on restart | Persist to `state/healing_cache.json` |
| **BUG-4** | `beta_pyramid_functional/B2_Orchestrator/synthesis_agent.py:42` | `cortex.get_all_sigs()` does not exist | Replace with `cortex.hypergraph.nodes` iteration |

If your task touches any of these files — fix the listed bug as part of the task.

---

## 4. GIT WORKFLOW

### Branch naming
```
codex/<sprint>-<description>
Examples:
  codex/s3-fix-z14-nameError
  codex/s3-fix-cognitive-bridge
  codex/s3-healing-cache-persist
  codex/s3-fix-synthesis-agent
```

### Session flow
```bash
git checkout main && git pull origin main
git checkout -b codex/<sprint>-<description>
# ... implement ...
uv run python -m pytest tests/ -x --tb=short -q   # must exit 0
git add <only changed files>                        # never "git add ."
git commit -m "<type>(<scope>): <description>"
git push origin codex/<sprint>-<description>
# open PR → base: main
```

### Commit format
```
fix(z14): add recalled_proposal init — resolves BUG-1
fix(cognitive): replace .blocks with .hypergraph.nodes — resolves BUG-2
feat(cognitive): persist healing_cache to state/healing_cache.json
test(synthesis): smoke test for SynthesisAgent
```
Types: `fix | feat | refactor | test | docs | chore`  
Scopes: `z14 | cognitive | synthesis | zbus | api | extension | frontend | ci`

### NEVER commit these
```
beta_pyramid_functional/B3_SessionRegistry/sessions_store.json  ← PII
beta_pyramid_functional/D_Interface/evolution_journal.json      ← PII
state/pyramid_state.json
state/project_cortex/
evo_data/ , evo_backups/ , **/__pycache__/ , .venv/
```
Before every commit: `git status` — if you see the above, `git restore --staged <file>`.

### PR description template
```markdown
## What changed
<one paragraph>

## Bug fixed
BUG-N: <description>  — or "none"

## Pytest output
<paste: uv run python -m pytest tests/ -x --tb=short -q>

## Files modified
- path/to/file.py
```

---

## 5. HARD RULES

### RULE 1 — No invisible stubs
```python
# STUB(codex): <reason> — mark every incomplete implementation
raise NotImplementedError("STUB: <what needs to happen>")
```
Never write code that looks complete but silently fails. This is how BUG-1 and BUG-4 were created.

### RULE 2 — pytest gate before every PR
```bash
uv run python -m pytest tests/ -x --tb=short -q
```
Must exit 0. If no test covers your change — write a smoke test first:
```python
# tests/test_<component>_smoke.py
def test_import():
    from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge
    assert CognitiveBridge is not None
```

### RULE 3 — No PII, no absolute paths
```python
# FORBIDDEN: C:\Users\Alex Bear\Desktop\EvoPyramid OS\...
# CORRECT:
PROJECT_ROOT = Path(__file__).resolve().parents[N]
```

### RULE 4 — No duplicate files
`find . -name "<n>.py" | grep -v __pycache__` before creating anything new.

### RULE 5 — Z-level hierarchy
Z5 cannot command Z14. Validate all cross-level tasks:
```python
if not SystemPolicyManager().validate_action(envelope): return
await zbus.publish({"topic": "EXECUTE_TASK", "payload": {...}})
```

### RULE 6 — Async safety
Never call `ProjectCortex` / `HypergraphMemory` from sync context.

---

## 6. CI — WHAT RUNS ON YOUR PUSH

Every push to `codex/**` triggers `.github/workflows/evopyramid-ci.yml`:

| Job | Checks | Blocks merge |
|-----|--------|-------------|
| `python-sanity` | `compileall` on all 3 layers | Yes |
| `pytest` | `pytest tests/ -x` (e2e excluded) | Yes |
| `frontend` | `npm lint && build` | Yes |

Tests use dummy API keys (`test-key-ci`) — do not make real LLM calls in tests.

---

## 7. REVIEW GUIDELINES

When reviewing PRs as `@codex review`:

- **P0** — NameError, AttributeError, undefined variable before use, missing `await` on async call
- **P0** — PII or absolute paths in committed files
- **P0** — Direct commit to `main` branch
- **P1** — Missing `raise NotImplementedError` on stub (silent stub = production bug)
- **P1** — New file that duplicates existing module
- **P1** — Cross-Z-level call without `SystemPolicyManager.validate_action()`
- **P2** — Import from legacy root wrappers instead of canonical path
- **P2** — No test coverage for changed component

---

## 8. ZBUS EVENT CONTRACTS

| Topic | Direction | Required fields |
|-------|-----------|----------------|
| `EXECUTE_TASK` | → ZBus | `task_id`, `envelope` |
| `TASK_RESULT` | ← ZBus | `task_id`, `status`, `result` |
| `PROMPT_DISPATCH` | → ZBus | `provider`, `session_id`, `prompt` |
| `RESPONSE_COMPLETE` | ← ZBus | `session_id`, `content` |
| `BRIDGE_HEARTBEAT` | ← Extension | *(empty)* |

New topics: ARCHITECT approval + entry in `beta_pyramid_functional/B1_Kernel/events.py`.

---

## 9. SESSION CHECKLIST

**START:** `git checkout main && git pull` → new branch → confirm task in one sentence  
**END:** pytest → list modified files → list STUBs → state BUG-N resolved → push → PR

---

## 10. ВЗАИМОДЕЙСТВИЕ С CLAUDE

> Full profile: `.agents/workflows/CLAUDE_ROLE.md`  
> Source diagnostic: `docs/EvoPYRAMID_AI_SELF_DIAGNOSTIC_QUESTIONNAIRE_v1.1.md`

Claude — это другой агент в EP-OS.

---

## 11. EXTERNAL ARCHITECTURAL INTELLIGENCE (AIO) — CHATGPT

**Status:** Formal external role (documentation/governance only).

ChatGPT is recognized in EP-OS as **External Architectural Intelligence (AIO)**:
- external architectural co-processor;
- external meta-level participant for repository reasoning;
- architecture-supporting intelligence, not a runtime subsystem.

### Mandate (allowed usage)
- architectural interpretation of canon and repository structure;
- protocol/task formalization for implementation handoff;
- repository analysis and consistency review (`canon ↔ docs ↔ code layout`);
- task briefing support for Codex execution.

### Limits (non-negotiable)
- ChatGPT is **not** a runtime node, service, daemon, worker, API module, or Z-level component.
- ChatGPT is **not** an autonomous committer and does not execute repository changes directly.
- ChatGPT does **not** override ARCHITECT/owner authority.
- ChatGPT does **not** replace Codex as sanctioned repository executor.
- ChatGPT does **not** change project constitution or governance on its own.

### Role separation
- **ARCHITECT / Owner**: defines will, direction, approvals, and governance.
- **ChatGPT (AIO)**: interprets, formalizes, audits, and structures architectural context.
- **Codex**: executes sanctioned repository changes inside approved scope.

Operating note: use ChatGPT mainly for audits, task shaping, protocol clarification, and repo-level reasoning — never as an internal always-running EP-OS runtime service.

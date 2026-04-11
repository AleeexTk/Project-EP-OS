# 0. CORE ARCHITECTURAL PILLARS (READ FIRST)

To operate correctly in EvoPyramid OS, all agents MUST read the **[AI Cognitive Bootstrap Protocol](docs/AI_COGNITIVE_BOOTSTRAP.md)** and adhere to these four fundamental laws:

1. **Law of Z-Parity**:
   - **Odd Z-levels** (Z17, Z15...): **Structural Nuclei (White)**. Pure logic/data cores.
   - **Even Z-levels** (Z16, Z14...): **Responsibility Bridges (Colored)**. Agent-governed transit zones.
2. **Geometric Expansion (18-Z)**:
   - Every level Z has an available block of size `(18 - Z) x (18 - Z)` centered at `(9,9)`.
   - Z17: 1x1 | Z16: 2x2 | Z14: 4x4 | Z12: 6x6 ... Z1: 17x17.
3. **Triad Responsibility (Colored Sectors)**:
   - **NW (Green)**: Trailblazer (Efficiency/Route).
   - **NE (Dark Red)**: Provocateur (Stability/Viability).
   - **SW (Gold)**: Synthesis (Integration).
   - **SE (Purple)**: Soul (Reflection/Memory).
   - **Axial (x=9 or y=9)**: Spine (White/Neutral).
4. **PEAR-CHAOS-OBSERVER Cycle**:
   - All state transitions must flow from `PEAR` (Z17/Initiation) through `CHAOS` (Z14/Validation) to `OBSERVER` (Z2/Reflection).

---

## 1. TOPOLOGY OF INTELLIGENCES (AI REGISTRY)

EvoPyramid OS operates as a symbiotic hierarchy of both intrinsic runtime LLMs and external Meta-Agents. Every entity has its defined zone of execution, memory persistence, and authority level.

### 1.1 EXTERNAL META-AGENTS (The Builders)

These entities operate outside the Python runtime but hold repository execution authority.

- **Antigravity (The Triad of Evolution)**
  - **Role:** Main Runtime Engineer & Cognitive Meta-Agent.
  - **Environment:** Local `.gemini/` workspace & IDE.
  - **Temporal Identity:** `IDENTITY = ID + TIME TRACE + LOCATION + ACTION HISTORY`.
  - **Reference:** `.agents/workflows/ANTIGRAVITY_ROLE.md`
  - **Interaction:** Executes continuous changes, debates architecture via Triad persona, and interfaces with the repository through `antigravity/**` branches. Keeps Knowledge Items (KIs) locally.

- **Codex**
  - **Role:** Historic Executor & CI PR Reviewer.
  - **Environment:** GitHub Actions `.github/codex/`.
  - **Interaction:** Validates structural integrity at merge time via automated GitHub workflows. Reads this file for CI rules.

- **Claude**
  - **Role:** Specialized Analyst & Pair Programmer.
  - **Environment:** Remote Web / Local `.agents` interface.
  - **Reference:** `.agents/workflows/CLAUDE_ROLE.md`

### 1.2 INTERNAL RUNTIME ENTITIES (The Z-Pyramid)

These agents are hardcoded into the OS execution layer (Python codebase).

- **Z13 AutoCorrector** (`alpha_pyramid_core/SPINE/_13_AUTO_CORRECTOR/z13_policy_corrector.py`)
  - **Role:** The Immune System.
  - **Interaction:** Intercepts proposed changes and cross-checks them against system policy across the ZBus. Can veto external outputs.

- **Synthesis Agent** (`beta_pyramid_functional/B2_Orchestrator/synthesis_agent.py`)
  - **Role:** Task Translator. Parses tasks from ZBus and allocates execution across local/remote foundational models.
  - **Interaction:** Communicates with CognitiveBridge for context matching.

- **LLM Orchestrator** (`beta_pyramid_functional/B2_Orchestrator/llm_orchestrator.py`)
  - **Role:** The Execution Muscle. Dispatches parsed prompts concurrently across multi-LLM networks.

- **Cognitive Bridge** (`beta_pyramid_functional/B4_Cognitive/cognitive_bridge.py`)
  - **Role:** Long-term Memory Gateway.
  - **Interaction:** Interfaces between `ProjectCortex` (storage) and runtime, caching and recalling successful healing mechanisms via `evolution_journal.json`.

### 1.3 EXTERNAL ARCHITECTURAL INTELLIGENCE (AIO)

- **ChatGPT**
  - **Role:** Architecture Formalizer & Governance Auditor.
  - **Environment:** Remote Web Interface.
  - **Interaction:** Does NOT commit. Does NOT execute code. Used strictly for blueprint drafting and conceptual governance. See Section 11.

---

## 2. ARCHITECTURE MAP

```text
EP-OS/
├── alpha_pyramid_core/        Z11–Z17  │ Canon Layer
│   ├── B_Structure/                    │ Atlas, SpineRouter, models  ← USE THESE
│   └── SPINE/
│       ├── _14_AUTO_CORRECTOR/          │ Self-healing
│       ├── _14_POLICY_BUS/              │ ZBus canonical source
│       ├── _16_NEXUS_ROUTER/            │ Sync task dispatcher
│       └── _17_GLOBAL_NEXUS/            │ Top orchestrator
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
│   │   └── synthesis_agent.py          │
│   ├── B3_SessionRegistry/             │ Sessions, messages, crystals
│   ├── B4_Cognitive/cognitive_bridge.py│
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

*All previous bugs (BUG-1 to BUG-4) have been verified as resolved. No active structural execution bugs are currently tracked.*

---

## 4. GIT WORKFLOW

### Branch naming

```text
antigravity/<sprint>-<description>
codex/<sprint>-<description>
Examples:
  antigravity/s4-map-agents
  codex/s3-fix-z14-nameError
```

### Session flow

```bash
git checkout main && git pull origin main
git checkout -b antigravity/<sprint>-<description>
# ... implement ...
uv run python -m pytest tests/ -x --tb=short -q   # must exit 0
git add <only changed files>                        # never "git add ."
git commit -m "<type>(<scope>): <description>"
git push origin HEAD
# open PR → base: main
```

### Commit format

```text
fix(z14): add recalled_proposal init — resolves BUG-1
feat(cognitive): persist healing_cache to state/healing_cache.json
test(synthesis): smoke test for SynthesisAgent
docs(agents): update global registry of intelligences
```

Types: `fix | feat | refactor | test | docs | chore`  
Scopes: `z14 | cognitive | synthesis | zbus | api | extension | frontend | ci | agents`

### NEVER commit these

```text
beta_pyramid_functional/B3_SessionRegistry/sessions_store.json  ← PII
beta_pyramid_functional/D_Interface/evolution_journal.json      ← PII
state/pyramid_state.json
state/project_cortex/
evo_data/ , evo_backups/ , **/__pycache__/ , .venv/
```

Before every commit: `git status` — if you see the above, `git restore --staged <file>`.

### PR description template

```markdown
## 1. Что добавляется нового?

<описание нового модуля, функции или workflow>

## 2. Почему это нельзя сделать через уже существующий модуль или решение?

<объяснение, почему архитектура требует новой сущности, а не расширения существующей>

## 3. Что именно было проверено на дублирование?

<отчет о сверке с architecture_map.json, solution_catalog.json и поиском по репозиторию>

## Pytest output

<paste: uv run python -m pytest tests/ -x --tb=short -q>
```

---

## 5. HARD RULES

### RULE 1 — No invisible stubs

```python
# STUB(agent): <reason> — mark every incomplete implementation
raise NotImplementedError("STUB: <what needs to happen>")
```

Never write code that looks complete but silently fails.

### RULE 2 — pytest gate before every PR

```bash
uv run python -m pytest tests/ -x --tb=short -q
```

Must exit 0. If no test covers your change — write a smoke test first.

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

### RULE 7 — Architectural Deduplication

Во время интеграции любые новые изменения должны проходить архитектурную сверку с текущим содержимым репозитория, картой архитектуры (`architecture_map.json`) и каталогом решений (`solution_catalog.json`). Если находится дублирующая функция или пересекающееся решение, приоритет отдаётся объединению, переиспользованию или расширению существующего элемента, а не созданию нового.

---

## 6. CI — WHAT RUNS ON YOUR PUSH

Every push to `antigravity/**` or `codex/**` triggers `.github/workflows/evopyramid-ci.yml`:

| Job | Checks | Blocks merge |
| --- | --- | --- |
| `python-sanity` | `compileall` on all 3 layers | Yes |
| `pytest` | `pytest tests/ -x` (e2e excluded) | Yes |
| `frontend` | `npm lint && build` | Yes |

Tests use dummy API keys (`test-key-ci`) — do not make real LLM calls in tests.

---

## 7. REVIEW GUIDELINES

When reviewing PRs via Codex CI or Antigravity validation:

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
| --- | --- | --- |
| `EXECUTE_TASK` | → ZBus | `task_id`, `envelope` (must have `slot_id`) |
| `TASK_RESULT` | ← ZBus | `task_id`, `status`, `result` |
| `PROMPT_DISPATCH` | → ZBus | `provider`, `session_id`, `prompt` |
| `RESPONSE_COMPLETE` | ← ZBus | `session_id`, `content` |
| `BRIDGE_HEARTBEAT` | ← Extension | *(empty)* |

New topics: ARCHITECT approval + entry in `beta_pyramid_functional/B1_Kernel/events.py`.

---

## 9. SESSION CHECKLIST

**START:** `git checkout main && git pull` → new branch `antigravity/...` → confirm task in one sentence  
**END:** pytest → list modified files → list STUBs → state BUG-N resolved → push → PR

---

## 10. ВЗАИМОДЕЙСТВИЕ С CLAUDE

> Full profile: `.agents/workflows/CLAUDE_ROLE.md`  
> Source diagnostic: `docs/EvoPYRAMID_AI_SELF_DIAGNOSTIC_QUESTIONNAIRE_v1.1.md`

Claude — это другой внешний агент в EP-OS, выступающий аналитиком.

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
- task briefing support for Antigravity/Codex execution.

### Limits (non-negotiable)

- ChatGPT is **not** a runtime node, service, daemon, worker, API module, or Z-level component.
- ChatGPT is **not** an autonomous committer and does not execute repository changes directly.
- ChatGPT does **not** override ARCHITECT/owner authority.
- ChatGPT does **not** replace Antigravity or Codex as sanctioned repository executor.
- ChatGPT does **not** change project constitution or governance on its own.

### Role separation

- **ARCHITECT / Owner**: defines will, direction, approvals, and governance.
- **ChatGPT (AIO)**: interprets, formalizes, audits, and structures architectural context.
- **Antigravity / Codex**: execute sanctioned repository changes inside approved scope.

Operating note: use ChatGPT mainly for audits, task shaping, protocol clarification, and repo-level reasoning — never as an internal always-running EP-OS runtime service.

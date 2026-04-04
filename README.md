# EvoPyramid OS: The Hybrid Architectural System

EP-OS is an operating architectural system where projects execute in **Runtime Nodes**, are governed by a shared **Pyramid Canon**, and are managed via a visual **Web Control Plane**.

## The Hybrid Model

- **Local Runtime Node**: Stateful project execution (files, memory, local agents).
- **Shared Canon**: The Z-Architecture rules, contracts, and semantic logic.
- **Web Control Plane**: Remote orchestration, 3D visualization, and audit console.

## Canonical Flow (V7 — Trinity Resonance)

The system enforces a strictly regulated task lifecycle:

1. **Z17 Global Nexus** (`nexus_core.py`): Intent capture + PEAR pulse + Trinity **Coherence Audit** (must be ≥ 0.7).
2. **Z16 Nexus Router** (`nexus_router.py`): Dispatches tasks across Z-Bus to target layers.
3. **Z12 Security Audit** (`sec_guardian.py`): Rate-limiting and anti-spoofing check.
4. **Z-Cascade Monument**: Semantic integrity validation (intent must survive descent).
5. **Z13 Auto-Corrector** (`z13_policy_corrector.py`): LLM-powered repair + Trinity coherence elevation.
6. **B1 Kernel Dispatch**: Execution via `SystemPolicyManager`.

## Repository Layout (Sprint 9 — Canonical)

```text
├── alpha_pyramid_core/       Z11–Z17  │ Canon Layer
│   ├── SPINE/
│   │   ├── 17_GLOBAL_NEXUS/ nexus_core.py    ← Z17 apex + ApexCore registry + PEAR pulse
│   │   │   └── trinity_resonance/             ← Formal Resonance Engine v3.0
│   │   ├── 15_ARCHITECT_CORE/ evo_meta.py     ← Metadata reflection
│   │   ├── 13_AUTO_CORRECTOR/ z13_policy_corrector.py ← Immune System
│   │   └── 14_POLICY_BUS/                     ← ZBus canonical source
│   └── B_Structure/                            ← AtlasGenerator, SpineRouter, Models
│
├── beta_pyramid_functional/  Z5–Z10   │ Execution Layer
│   ├── B1_Kernel/            contracts.py, policy_manager.py, z_cascade.py
│   ├── B2_Orchestrator/      zbus.py, llm_orchestrator.py, synthesis_agent.py
│   ├── B4_Cognitive/         cognitive_bridge.py
│   └── D_Interface/          evo_api.py  ← FastAPI entry point
│
├── gamma_pyramid_reflective/ Z1–Z4    │ Reflection Layer
│   ├── A_Pulse/              Heartbeat, SEVEN monitor
│   └── D_Audit/              evolution_proposals.md  ← Master intent ledger
│
├── evopyramid-v2/                      │ React + Three.js 3D frontend
└── architecture/                       │ architecture_map.json ← Source of Truth
```

## Resilience & Self-Healing

As of Phase 7, the OS is equipped with:

- **Circuit Breaker**: Automatic LLM provider fallback (e.g., Gemini -> Claude) on API failures.
- **Monument Block**: Prevents "hallucinating" agents from executing distorted instructions.
- **Active Repair**: Z14 interceptor that re-writes failing proposals to align with Original Intent.

## Quick Start

**Recommended (Python launcher — all-in-one):**

```powershell
cd "C:\Users\Alex Bear\Desktop\EvoPyramid OS"

python Nexus_Boot.py
```

**Testing the Integrity Chain:**

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

## Documentation

- **[EP-OS Canonical Execution Model](docs/ep_os_canonical_execution_model.md)** — The Hybrid Truth and layer separation.
- **[Z-Architecture Order & Z-Levels](docs/z_architecture_order.md)** — Z1 to Z17 tiering.
- **[Project Architectural Audit](docs/PROJECT_AUDIT.md)** — Structural health and milestones.
- **[Trinity Protocol](docs/trinity_protocol.md)** — Triad role interactions.
- **[Reference Operating Model](docs/reference_operating_model.md)** — Restaurant analogy for role/flow alignment and the shift to 4D Architecture (Timeline + Temporal Routing).

## Known Issues & Fixes Applied

| Issue | Fix |
| --- | --- |
| `ImportError` on relative kernel imports | Migrated to Absolute Imports with `sys.path.insert(0)` |
| Module name collision (`auto_corrector`) | Prioritized Z14 SPINE path in Kernel dispatcher |
| Z-Level Spoofing | Z12 SEC_GUARDIAN now verifies `origin_z` legitimacy |
| Semantic Drift in descent | Z-Cascade Monument + Z14 Auto-Corrector repair loop |
| `node.dict()` deprecation (Pydantic v2) | Replaced with `node.model_dump()` |

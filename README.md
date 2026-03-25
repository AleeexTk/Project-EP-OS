# EvoPyramid OS

EvoPyramid OS is a local-first architecture workspace where a 3D pyramid view is synchronized with real project directories. It features a self-healing kernel with semantic integrity protection.

## Canonical Flow (V6)

The system enforces a strictly regulated task lifecycle:

1. **Z12 Security Audit** (`sec_guardian.py`): Rate-limiting and anti-spoofing check.
2. **Z5 Quarantine Check**: Blocking actions from rogue/locked nodes.
3. **Z-Cascade Monument**: Semantic integrity validation (ensures intent isn't lost during descent).
4. **Z14 Auto-Correction**: Autonomous repair of tasks blocked by semantic drift.
5. **B1 Kernel Dispatch**: Execution via `SystemPolicyManager`.

## Repository Layout

- `alpha_pyramid_core`: Governance & Spine Nodes (Z17-Z11).
  - `SPINE/12_SEC_GUARDIAN`: Security Proxy Gateway.
  - `SPINE/14_AUTO_CORRECTOR`: Semantic Repair Advocate.
- `beta_pyramid_functional`: The Living Engine (Z9-Z5).
  - `B1_Kernel`: The Crystallized Spine (Contracts, Policies, DISCOVERY).
  - `D_Interface`: Trinity Hub (`evo_api.py`, UX Core).
- `gamma_pyramid_reflective`: Evolution Journal & Audits (Z3-Z1).
- `evopyramid-v2`: React UX with real-time Nucleus Monitoring.

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

- **[Z-Architecture Order & Z-Levels](docs/z_architecture_order.md)** — Z1 to Z17 tiering.
- **[Project Architectural Audit](docs/PROJECT_AUDIT.md)** — Structural health and milestones.
- **[Trinity Protocol](docs/trinity_protocol.md)** — Triad role interactions.

## Known Issues & Fixes Applied

| Issue | Fix |
| --- | --- |
| `ImportError` on relative kernel imports | Migrated to Absolute Imports with `sys.path.insert(0)` |
| Module name collision (`auto_corrector`) | Prioritized Z14 SPINE path in Kernel dispatcher |
| Z-Level Spoofing | Z12 SEC_GUARDIAN now verifies `origin_z` legitimacy |
| Semantic Drift in descent | Z-Cascade Monument + Z14 Auto-Corrector repair loop |
| `node.dict()` deprecation (Pydantic v2) | Replaced with `node.model_dump()` |

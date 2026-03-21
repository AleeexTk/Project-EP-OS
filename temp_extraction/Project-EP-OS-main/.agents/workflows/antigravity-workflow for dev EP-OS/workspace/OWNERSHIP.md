# File Ownership Rules per Workspace

## The golden rule

> **No two agents write to the same path simultaneously.**  
> Violations cause context collapse and broken state.

---

## Ownership map

| Path | Owner workspace | Other workspaces |
|---|---|---|
| `canon_builder/` | `ws-canon` | READ ONLY |
| `canon_builder/input/*/manifest.json` | `ws-canon` | READ ONLY |
| `canon_builder/output/` | generated — never edit manually | — |
| `EVO_ARCH_MAP.yaml` | `ws-canon` | READ ONLY |
| `AGENTS.md` | `ws-canon` | READ ONLY |
| `README.md` | `ws-canon` | READ ONLY |
| `α_Pyramid_Core/` | `ws-canon` | READ ONLY |
| `environment/` | `ws-runtime` | READ ONLY |
| `GLOBAL_NEXUS/` | `ws-runtime` | READ ONLY |
| `api/` | `ws-runtime` | READ ONLY |
| `β_Pyramid_Functional/` | `ws-runtime` | READ ONLY |
| `evopyramid-v2/src/` | `ws-ui` | READ ONLY |
| `evopyramid-v2/src/lib/evo.ts` | `ws-ui` | READ ONLY |
| `γ_Pyramid_Reflective/A_Observation/A1_Logs/` | `ws-runtime` writes, `ws-canon` reads | others READ ONLY |

---

## Conflict resolution

If two agents need to change the same file:

1. Stop both
2. Assign task to the **owner workspace**
3. The non-owner workspace gets the result via artifact
4. Non-owner reads the updated file, does not write

---

## The one file no agent touches alone

`canon_builder/input/` + `canon_builder/output/`

Changes to manifests **must** go through:
1. Plan Artifact from `ws-canon`
2. Human approval (you)
3. Only then: `ws-canon` executes

This protects the single source of architectural truth.

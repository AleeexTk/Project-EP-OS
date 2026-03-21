# EP-OS Antigravity Quick Reference

## 5 workspaces

| ws | Agent | Model | Owns |
|---|---|---|---|
| ws-canon | Architect | Opus 4.6 | manifests, canon_builder, AGENTS.md |
| ws-runtime | Runtime | Sonnet 4.6 | environment/, GLOBAL_NEXUS/, api/ |
| ws-ui | UI | Gemini 2.5 Pro | evopyramid-v2/src/ |
| ws-qa | QA Browser | Gemini 2.5 Pro | read-only, browser testing |
| ws-research | Research | Sonnet / GPT | read-only, external research |

## 3 immediate next tasks (as of 2026-03-15)

**ws-runtime / Plan mode:**
```
Implement PATCH /nodes/{node_id}/status endpoint.
Allows UI to set node status to quarantined/active/degraded.
Add runtime_canon_flag field to PyramidNode in models.py.
```

**ws-ui / Fast mode:**
```
Add Confirm Route + Quarantine Z7 buttons to Observer banner in App.tsx.
Confirm → banner closes (anomaly resolved).
Quarantine → PATCH chaos_engine status = quarantined.
```

**ws-ui / Fast mode:**
```
Add Canon vs Runtime visual badge to each node cube in EvoPyramid.tsx:
CANON = dark/solid, RUNTIME = outlined, DEGRADED = amber, QUARANTINED = purple.
Read runtime_canon_flag from node data.
```

## PR title format

```
[β] fix WebSocket connection — Z7
[UI] add Observer banner actions — Phase A close
[α] register mvp_browser modules — Z8
```

## Canon protection — never skip

```bash
# After any manifest change:
python -m canon_builder.pipeline --modules input --output output

# Verify no errors, check atlas.json updated
```

## Daily cycle in 60 seconds

```
Morning  → check ws-research findings + GitHub issues
Task     → write task_brief → assign → get Plan → approve → build
After    → ws-qa verifies → Verifier checks → PR → merge
Evening  → no uncommitted canon changes left open
```

## Signs something is wrong

🔴 Two agents editing same file  
🔴 output/ files edited manually  
🔴 Merge without Verification Artifact  
🔴 Core Link Lost after runtime change  
🔴 Frontend nodes don't match atlas.json  

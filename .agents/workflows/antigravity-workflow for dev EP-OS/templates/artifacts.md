# Implementation Plan Template

> Agents in Plan mode must produce this before any code changes.

```
IMPLEMENTATION PLAN
──────────────────────────────────────
Agent:          [role]
Workspace:      [ws-name]
Task:           [task title from brief]
Date:           [timestamp]

AFFECTED NODES / FILES:
- [file path] → [what changes]
- [file path] → [what changes]

Z-LEVEL / LAYER:
- Z: [number]
- Layer: [alpha / beta / gamma]
- Sector: [SPINE / PURPLE / RED / GOLD / GREEN]
- Canon or Runtime change: [canon / runtime]

APPROACH:
[2-5 sentences describing how the task will be done]

STEP BY STEP:
1. [first action]
2. [second action]
3. [...]

RISKS / QUESTIONS:
- [anything that might go wrong]
- [anything that needs human decision before proceeding]

ESTIMATED OUTPUT:
[What will exist after this is done]

READY TO PROCEED: YES / WAITING FOR [...]
──────────────────────────────────────
```

---
---

# Verification Artifact Template

> QA Browser Agent produces this after every test run.

```
VERIFICATION ARTIFACT
──────────────────────────────────────
Tested by:      QA Browser Agent (ws-qa)
Date:           [timestamp]
Build:          [branch / last commit message]
Test URL:       http://localhost:3000

TEST RESULTS:

[ ] Pyramid renders at correct Z-levels (Z1–Z17 visible)
[ ] Named nodes visible with correct sector colors
[ ] Node click → inspector opens
[ ] Inspector shows: COORD / STATUS / SECTOR correctly
[ ] Z-LVL slider filters layers correctly
[ ] PAN slider moves view
[ ] Observer banner visible
[ ] Observer banner actions work (if implemented)
[ ] Core Link indicator: GREEN (WebSocket connected)
[ ] SWARM TERMINAL: opens, shows agent log entries
[ ] No console errors in browser devtools

BUGS FOUND:
[describe each bug, which file/component, assign to correct agent]

SCREENSHOTS:
[attach or reference screenshot files]

VERDICT: PASS / FAIL / NEEDS_REVIEW
Blocking issues (if FAIL): [list]
──────────────────────────────────────
```

---
---

# Observer Event Template

> Use this when logging a system event to γ_Pyramid_Reflective

```
OBSERVER EVENT
──────────────────────────────────────
Event ID:       OBS-[timestamp]-[sequence]
Detected by:    Observer Core (Z5)
Severity:       INFO / WARNING / ANOMALY / CRITICAL
Affected node:  [node_id] at Z[level] / [sector]
State change:   [previous state] → [new state]

DESCRIPTION:
[What happened. One paragraph.]

CAUSE (if known):
[Root cause or hypothesis]

ACTION TAKEN:
[ ] Routed to Runtime Agent
[ ] Routed to Architect Agent
[ ] Quarantine applied
[ ] Manual routing confirmation requested
[ ] Auto-resolved by coevolution loop
[ ] Escalated to human

RESOLUTION:
[How it was resolved, or PENDING]

CANON IMPACT: YES / NO
If YES — trigger Architect Agent review
──────────────────────────────────────
```

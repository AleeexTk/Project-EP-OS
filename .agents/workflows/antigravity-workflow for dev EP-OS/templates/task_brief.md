# Task Brief Template

> Copy this template. Fill it in. Paste it to the correct workspace in Antigravity.

---

```
TASK BRIEF
──────────────────────────────────────
Workspace:        [ws-canon / ws-runtime / ws-ui / ws-qa / ws-research]
Agent role:       [Architect / Runtime / UI / QA / Research]
Mode:             [Plan / Fast]
Priority:         [High / Normal / Low]

TASK TITLE:
[One line — what needs to happen]

CONTEXT:
[Why this is needed. 2-4 sentences max. Reference relevant files if known.]

SCOPE:
[What files / modules / layers are affected]

WHAT DONE LOOKS LIKE:
[Describe the concrete outcome — what will be visible, testable, or verifiable]

NOT IN SCOPE:
[What the agent should NOT touch or change]

ARTIFACTS REQUIRED:
[ ] Implementation Plan (before starting)
[ ] Walkthrough / Change Summary (after)
[ ] Screenshot (for UI tasks)
[ ] Verification artifact (for QA tasks)

REFERENCES:
- AGENTS.md
- [any relevant manifest path]
- [any relevant component]
──────────────────────────────────────
```

---

## Example filled brief

```
TASK BRIEF
──────────────────────────────────────
Workspace:        ws-ui
Agent role:       UI
Mode:             Fast
Priority:         High

TASK TITLE:
Add Confirm Route and Quarantine buttons to Observer OS banner

CONTEXT:
The Observer banner shows "Architectural anomaly detected in Z7. 
Awaiting manual routing confirmation." but has no action buttons.
This is the last item to close Phase A. The chaos_engine node at Z7 
is currently in 'warning' state.

SCOPE:
evopyramid-v2/src/App.tsx — Observer banner section (lines ~89-115)
evopyramid-v2/src/lib/usePyramidState.ts — may need state handler

WHAT DONE LOOKS LIKE:
- Banner has two buttons: "Confirm Route" and "Quarantine Z7"
- Confirm Route → banner closes, anomaly resolved
- Quarantine Z7 → chaos_engine node status changes to 'quarantined' 
  (visible in node inspector if you click the node)

NOT IN SCOPE:
- Do not modify backend files
- Do not change manifest files
- Do not change the banner text

ARTIFACTS REQUIRED:
[x] Walkthrough showing which lines changed
[x] Screenshot showing the two buttons visible in the banner

REFERENCES:
- AGENTS.md
- evopyramid-v2/src/lib/evo.ts → NodeStatus type (quarantined is valid)
──────────────────────────────────────
```

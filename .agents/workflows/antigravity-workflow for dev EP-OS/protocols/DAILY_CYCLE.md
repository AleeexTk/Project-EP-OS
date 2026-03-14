# Daily Development Cycle — EP-OS in Antigravity

---

## Morning start (5 min)

1. Open Agent Manager
2. Check `ws-research` — any overnight findings or issues?
3. Check GitHub — any open issues on `Project-EP-OS`?
4. Decide: what is today's one main goal?

---

## Standard feature cycle

```
1. BRIEF        You write task_brief.md → assign to correct workspace
       ↓
2. PLAN         Agent produces Implementation Plan Artifact
       ↓
3. APPROVE      You read the plan. If OK → say "proceed". If not → revise.
       ↓
4. BUILD        Agent implements in Fast mode
       ↓
5. WALKTHROUGH  Agent produces Walkthrough Artifact (what changed, terminal output)
       ↓
6. QA           ws-qa opens localhost, runs verification, produces Verification Artifact
       ↓
7. VERIFY       ws-canon or you run Verifier checklist
       ↓
8. MERGE        PR with correct title format → main branch
```

---

## Parallel mode (Agent Manager)

Run these simultaneously when building a feature that spans layers:

```
ws-runtime  →  fix WebSocket connection
ws-ui       →  add Observer banner action buttons
ws-qa       →  verify previous build in background
ws-research →  research Antigravity browser automation for future QA
```

You watch artifacts appearing in Manager. Review, comment, unblock.

---

## When to stop and call Architect Agent

Stop and go to `ws-canon` when:
- A new module needs to be placed in the pyramid
- Something breaks geometry validation
- A capability conflict appears in routing_table
- The αβγ layer mapping of a new feature is unclear
- Someone wants to change a manifest that already exists in `output/`

Do not try to resolve these in `ws-runtime` or `ws-ui`.

---

## End of day (3 min)

1. Confirm all open agent tasks are paused or complete
2. Check that no agent has uncommitted changes in `canon_builder/`
3. If any work is in progress — leave a brief note in the relevant workspace
4. Close Agent Manager

---

## Signs the workflow is breaking down

🔴 Two agents are modifying the same file  
🔴 An agent is writing to a path it doesn't own  
🔴 A change was merged without a Verification Artifact  
🔴 A manifest was created without running `canon_builder` pipeline  
🔴 The Frontend shows nodes that don't exist in `atlas.json`  
🔴 `Core Link Lost` after a runtime change with no investigation  

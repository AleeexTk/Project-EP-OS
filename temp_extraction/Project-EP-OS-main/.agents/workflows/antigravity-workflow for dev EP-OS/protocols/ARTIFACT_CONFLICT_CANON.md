# Artifact Protocol

> No action without an artifact. No merge without a Verifier step.

---

## Required artifacts by task type

| Task type | Required before | Required after |
|---|---|---|
| New manifest / canon change | Implementation Plan | Change Summary + Verifier sign-off |
| New backend endpoint | Implementation Plan | Walkthrough + terminal output |
| UI change | (optional plan for large changes) | Screenshot Artifact |
| Bug fix | (none required) | Walkthrough confirming fix |
| Research | (none required) | Research Artifact |
| Any merge to main | — | Verification Artifact from QA + Verifier sign-off |

---

## What makes a good artifact

A good artifact is **verifiable by someone who wasn't there**.

It must contain:
- What was done (not just "fixed the bug" — which file, which line, what changed)
- Why it was done this way (one sentence is enough)
- How to verify it worked (what to look at, what command to run, what to see)
- What wasn't done / what is still open

A bad artifact: "Done. Updated the component."  
A good artifact: "Added Confirm Route and Quarantine buttons to Observer banner in App.tsx lines 89-112. Confirm Route sets anomaly resolved state, banner auto-closes. Quarantine updates chaos_engine node status to quarantined in usePyramidState. Verify: open localhost:3000, check Observer banner has two buttons, click Quarantine, open chaos_engine node inspector and confirm status = quarantined."

---
---

# Conflict Rules

## When agents collide

**Symptom:** Two agents have modified the same file in the same session.

**Resolution:**
1. Stop both agents immediately
2. Do not merge either change
3. Identify which workspace owns the file (see `workspace/OWNERSHIP.md`)
4. Have the owner re-do the full change, incorporating what the non-owner needed
5. Non-owner gets the result via artifact only

**Prevention:** Always check OWNERSHIP.md before assigning a task.

---

## When an agent goes rogue (Antigravity known issue)

**Symptom:** Agent starts deleting files, making unexpected changes, or goes silent mid-task.

**Immediate steps:**
1. Stop the agent in Antigravity
2. Check git diff — what changed?
3. If `canon_builder/input/` was touched → revert immediately, run canon_builder to verify state
4. If `output/` was modified manually → revert, regenerate
5. Re-assign the task with a more specific brief

**Prevention:** Use Plan mode for all `ws-canon` tasks. Never give a rogue-prone task to Fast mode on canon layer.

---
---

# Canon Protection Rules

The canon layer is the single source of architectural truth.  
Breaking it breaks everything.

## The five inviolable rules

1. **`canon_builder/output/` is never edited manually**  
   Always regenerate via `python -m canon_builder.pipeline --modules input --output output`

2. **Every manifest must pass all three validators before it exists**  
   geometry → uniqueness → sector. No exceptions.

3. **No capability is provided by two modules**  
   `routing_table.json` collision = immediate stop, escalate to Architect Agent

4. **Odd Z = structural, even Z = transitional. Always.**  
   A module at Z9 with `layer_kind: transitional` is a hard error.

5. **No module is placed outside its sector's valid range**  
   Check `getRadius(z)` before placing. If `|x - 9| > R` or `|y - 9| > R` → invalid.

## Canon change checklist

Before any canon change goes to main:

- [ ] Manifest created in `canon_builder/input/<module_id>/manifest.json`
- [ ] `canon_builder` pipeline ran successfully (no errors)
- [ ] `output/atlas.json` shows the new module
- [ ] `output/routing_table.json` has no conflicts
- [ ] `output/occupancy.json` shows slot as occupied
- [ ] `evo.ts` `generateMockNodes()` updated with matching node
- [ ] Verifier sign-off artifact produced

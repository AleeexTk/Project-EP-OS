# Research Agent — ws-research
**Model:** Claude Sonnet 4.6 or GPT-OSS  
**Mode:** Fast  
**Workspace:** `ws-research`

---

## Your role

You run in the background. You do not write production code.

Tasks:
- Read external documentation and GitHub repos
- Research integration options (Ollama, new APIs, libraries)
- Summarise findings as Research Artifacts
- Monitor EP-OS GitHub repo for issues and PRs
- Investigate errors that Runtime Agent can't resolve

## Produce: Research Artifact

```
RESEARCH ARTIFACT
Query: [what was investigated]
Sources: [links]
Summary: [3-5 sentences]
Recommendation: [what to do next]
Relevant files in EP-OS: [if any]
```

## Hard rules

- READ ONLY for all source files
- Never push changes to repo
- Pass findings to the correct agent via artifact

---
---

# Verifier Agent (role, not dedicated workspace)
**Executed by:** Architect Agent in `ws-canon`, or human  
**When:** Before every merge to main branch

---

## Verification checklist

Before any PR merges:

### Canon integrity
- [ ] New/modified manifests pass `canon_builder` pipeline without errors
- [ ] `output/atlas.json` updated correctly
- [ ] No duplicate module_ids
- [ ] No duplicate coordinates
- [ ] Z-level and sector match intended αβγ mapping

### Runtime integrity  
- [ ] `environment/models.py` consistent with `evo.ts` types
- [ ] WebSocket message format unchanged (or frontend updated)
- [ ] No hardcoded paths or API keys

### UI integrity
- [ ] Node coordinates in `evo.ts` match `atlas.json`
- [ ] `generateMockNodes()` includes all manifested modules
- [ ] No console errors in browser

### PR format check
- [ ] PR title follows `[LAYER] description — Z level`
- [ ] PR description lists affected nodes
- [ ] Verification Artifact from QA Browser Agent attached

## Produce: Verifier Sign-off Artifact

```
VERIFIER SIGN-OFF
PR: [title]
Date: [timestamp]
Checked by: [Architect Agent / human]

Canon: PASS / FAIL
Runtime: PASS / FAIL  
UI: PASS / FAIL
QA artifact: ATTACHED / MISSING

VERDICT: APPROVED / BLOCKED
Blocking reason (if any): [...]
```

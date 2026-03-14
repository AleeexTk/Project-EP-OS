# EP-OS · EvoPyramid OS
# Antigravity Development Workflow

> Operating protocol for developing EP-OS inside **Google Antigravity IDE**  
> Using Agent Manager + Editor View as the dev-orchestration layer

---

## Core principle

```
Antigravity  =  dev-orchestration layer      (HOW you build)
EP-OS        =  system-orchestration layer   (WHAT you build)
```

Two rules that prevent everything from falling apart:

1. **One agent = one workspace = one layer of responsibility**
2. **No action without an artifact. No merge without a Verifier step.**

---

## Files in this package

```
README.md                        ← this file
agents/
  ARCHITECT.md                   ← Architect Agent instructions
  RUNTIME.md                     ← Runtime Agent instructions
  UI.md                          ← UI Agent instructions
  QA_BROWSER.md                  ← Browser QA Agent instructions
  RESEARCH.md                    ← Research Agent instructions
  VERIFIER.md                    ← Verifier Agent instructions
workspace/
  SETUP.md                       ← How to configure workspaces in Antigravity
  OWNERSHIP.md                   ← File ownership rules per workspace
protocols/
  DAILY_CYCLE.md                 ← Daily development cycle
  ARTIFACT_PROTOCOL.md           ← Artifact requirements per task type
  CONFLICT_RULES.md              ← What to do when agents collide
  CANON_PROTECTION.md            ← Rules for protecting canon layer
templates/
  task_brief.md                  ← Template: how to assign a task to an agent
  implementation_plan.md         ← Template: agent implementation plan artifact
  verification_artifact.md       ← Template: verifier sign-off artifact
  observer_event.md              ← Template: Observer OS event log entry
```

---

## Quick start

1. Open Antigravity → create 5 workspaces (see `workspace/SETUP.md`)
2. Assign one agent per workspace using agent instruction files in `agents/`
3. Use `templates/task_brief.md` to assign every task
4. Follow `protocols/DAILY_CYCLE.md` for the daily loop
5. Never touch `canon_builder/` without going through `ws-canon` + Verifier

---

## Model assignments

| Workspace | Agent Role | Recommended Model | Mode |
|---|---|---|---|
| `ws-canon` | Architect Agent | Claude Opus 4.6 | Plan only |
| `ws-runtime` | Runtime Agent | Claude Sonnet 4.6 | Plan → Fast |
| `ws-ui` | UI Agent | Gemini 2.5 Pro | Fast |
| `ws-qa` | Browser QA Agent | Gemini 2.5 Pro | Fast + browser |
| `ws-research` | Research Agent | GPT-OSS or Sonnet | Fast |

Verifier role = you, or a dedicated Verifier pass in `ws-canon`.

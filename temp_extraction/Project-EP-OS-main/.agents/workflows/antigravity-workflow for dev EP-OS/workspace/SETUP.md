# Workspace Setup in Antigravity

## Create these 5 workspaces in Agent Manager

| # | Workspace name | Agent file | Model | Mode |
|---|---|---|---|---|
| 1 | `ws-canon` | `agents/ARCHITECT.md` | Claude Opus 4.6 | Plan only |
| 2 | `ws-runtime` | `agents/RUNTIME.md` | Claude Sonnet 4.6 | Plan → Fast |
| 3 | `ws-ui` | `agents/UI.md` | Gemini 2.5 Pro | Fast |
| 4 | `ws-qa` | `agents/QA_BROWSER.md` | Gemini 2.5 Pro | Fast + browser |
| 5 | `ws-research` | `agents/RESEARCH_VERIFIER.md` | Sonnet / GPT-OSS | Fast |

## How to initialise each workspace

1. Open Agent Manager in Antigravity
2. Create new workspace with the name above
3. Open the corresponding agent `.md` file
4. Paste its full contents as the system prompt / agent instructions
5. Set the model and mode as listed
6. Point the workspace to the `Project-EP-OS` repo root

## Editor View vs Agent Manager — when to use which

**Use Editor View (single agent in sidebar) for:**
- Fixing one bug in one file
- Small refactor under 50 lines
- Quick manifest tweak
- Reading and explaining a file
- Testing a single hypothesis in terminal

**Use Agent Manager (parallel workspaces) for:**
- Building a new feature (UI + runtime simultaneously)
- Research running in background while UI work continues
- QA running while next feature is being built
- Canon validation while runtime agent fixes a bug
- Any task longer than ~20 minutes

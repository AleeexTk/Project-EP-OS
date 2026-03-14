# GitHub + Netlify Secrets Checklist

Deployment and integration checklist aligned with the Z-service vertical.

## Scope

- CI workflow: `.github/workflows/evopyramid-ci.yml`
- Netlify build config: `netlify.toml`
- Frontend runtime env: `evopyramid-v2/.env.example`
- Service mapping: `state/z_service_vertical.md`

## Z-vertical mapping

- Z15 `openai_docs_hub`: documentation source-of-truth
- Z11 `gh_ci_guardian`: CI quality gate
- Z9 `gh_pr_resolver`: review resolution loop
- Z7 `chatgpt_apps_bridge`: app bridge runtime
- Z3 `netlify_deploy_beacon`: deploy checkpoint
- Z1 `deploy_audit_ledger`: release continuity record

## GitHub repository secrets

### Required when Netlify deploy automation is enabled
- [ ] `NETLIFY_AUTH_TOKEN`
- [ ] `NETLIFY_SITE_ID`

### Required when provider-backed automations are enabled
- [ ] `OPENAI_API_KEY`
- [ ] `GEMINI_API_KEY` (valid key + enabled billing/quota in Google AI Studio project)

### Optional
- [ ] `GH_TOKEN` (only if workflow/scripts explicitly require custom token)

## GitHub repository variables (non-secret)

- [ ] `VITE_CORE_API_BASE`
- [ ] `VITE_SESSION_API_BASE`
- [ ] `VITE_CORE_WS_URL` (optional)
- [ ] `VITE_SWARM_WS_URL` (optional)

## Netlify environment variables

Set in Site settings -> Environment variables:

- [ ] `VITE_CORE_API_BASE`
- [ ] `VITE_SESSION_API_BASE`
- [ ] `VITE_CORE_WS_URL` (optional)
- [ ] `VITE_SWARM_WS_URL` (optional)

## Quota notes

- If Gemini returns `429 quota exceeded`, Session Registry places the session into `WAITING` and emits a short `[SYSTEM QUOTA]` message with retry cooldown.
- If the error includes `limit: 0`, your Gemini key/project has no usable quota until billing/quota is enabled in Google AI Studio.
- Use the `Open` button to continue externally while quota is cooling down.

## Post-configuration verification

1. Run `EvoPyramid CI` and confirm green status.
2. Confirm Netlify build uses `base = "evopyramid-v2"` and publishes `dist`.
3. Check `http://127.0.0.1:8000/state` contains all Z-service nodes.
4. In UI, verify node path equals backend `metadata.path`.
5. Trigger structure sync with `update_existing=true` after manifest edits.


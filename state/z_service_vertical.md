# Z-Service Vertical Mapping

This registry binds installed integration services to physical EvoPyramid directories.

## Node Registry

| Service | Node ID | Z | Layer | Directory |
| --- | --- | --- | --- | --- |
| openai-docs | openai_docs_hub | Z15 | Alpha | α_Pyramid_Core/PURPLE/15_OPENAI_DOCS_HUB |
| gh-fix-ci | gh_ci_guardian | Z11 | Alpha | α_Pyramid_Core/RED/11_GH_CI_GUARDIAN |
| gh-address-comments | gh_pr_resolver | Z9 | Beta | β_Pyramid_Functional/GREEN/9_GH_PR_RESOLVER |
| chatgpt-apps | chatgpt_apps_bridge | Z7 | Beta | β_Pyramid_Functional/SPINE/7_CHATGPT_APPS_BRIDGE |
| netlify-deploy | netlify_deploy_beacon | Z3 | Gamma | γ_Pyramid_Reflective/GOLD/3_NETLIFY_DEPLOY_BEACON |
| deploy-audit | deploy_audit_ledger | Z1 | Gamma | γ_Pyramid_Reflective/SPINE/1_DEPLOY_AUDIT_LEDGER |

## Vertical Flow

`openai_docs_hub -> gh_ci_guardian -> gh_pr_resolver -> chatgpt_apps_bridge -> netlify_deploy_beacon -> deploy_audit_ledger`

## Sync Contract

After any manifest or directory update, run:

```powershell
Invoke-WebRequest -UseBasicParsing -Method Post "http://127.0.0.1:8000/sync/discover-modules?update_existing=true"
```

## Live Validation

- `http://127.0.0.1:8000/state` includes all six node IDs
- UI node path uses backend `metadata.path`
- Coordinates/kind/links in state match each `.node_manifest.json`

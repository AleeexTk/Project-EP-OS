# Z-Service Vertical Mapping

> Updated: 2026-03-15 | Full Z1–Z17 spine complete

## Structural Nodes (odd Z — bones)

| Service | Node ID | Z | Layer | Sector | Directory |
| --- | --- | --- | --- | --- | --- |
| Global Nexus | gen-nexus | Z17 | Alpha | SPINE | α_Pyramid_Core/SPINE/17_GLOBAL_NEXUS |
| Evo Meta | gen-meta | Z15 | Alpha | PURPLE | α_Pyramid_Core/PURPLE/15_EVO_META |
| OpenAI Docs Hub | openai_docs_hub | Z15 | Alpha | PURPLE | α_Pyramid_Core/PURPLE/15_OPENAI_DOCS_HUB |
| Evo Bridge | gen-bridge | Z13 | Alpha | RED | α_Pyramid_Core/RED/13_EVO_BRIDGE |
| PEAR Loop | gen-pear | Z11 | Alpha | GOLD | α_Pyramid_Core/GOLD/11_PEAR_LOOP |
| GH CI Guardian | gh_ci_guardian | Z11 | Alpha | RED | α_Pyramid_Core/RED/11_GH_CI_GUARDIAN |
| Async Job Runner | gen-async-jobs | Z9 | Beta | GREEN | β_Pyramid_Functional/GREEN/9_ASYNC_JOB_RUNNER |
| GH PR Resolver | gh_pr_resolver | Z9 | Beta | GREEN | β_Pyramid_Functional/GREEN/9_GH_PR_RESOLVER |
| Web MCP Core | gen-webmcp | Z7 | Beta | GREEN | β_Pyramid_Functional/GREEN/7_WEB_MCP_CORE |
| Chaos Engine | chaos_engine | Z7 | Beta | SPINE | β_Pyramid_Functional/SPINE/7_CHAOS_ENGINE |
| Trinity Agent Bridge | trinity_agent_bridge | Z7 | Beta | SPINE | β_Pyramid_Functional/SPINE/7_TRINITY_AGENT_BRIDGE |
| Evo Dashboard | gen-dashboard | Z5 | Beta | SPINE | β_Pyramid_Functional/SPINE/5_EVO_DASHBOARD |
| Netlify Deploy Beacon | netlify_deploy_beacon | Z3 | Gamma | GOLD | γ_Pyramid_Reflective/GOLD/3_NETLIFY_DEPLOY_BEACON |
| Deploy Audit Ledger | deploy_audit_ledger | Z1 | Gamma | SPINE | γ_Pyramid_Reflective/SPINE/1_DEPLOY_AUDIT_LEDGER |

## Infrastructure Nodes (even Z — blood/transit)

| Node ID | Z | Layer | Sector | Directory | Connects |
| --- | --- | --- | --- | --- | --- |
| nexus_router_z16 | Z16 | Alpha | SPINE | α_Pyramid_Core/SPINE/16_NEXUS_ROUTER | Z17 → Z15 |
| policy_bus_z14 | Z14 | Alpha | SPINE | α_Pyramid_Core/SPINE/14_POLICY_BUS | Z15 → Z13 |
| provider_router_z12 | Z12 | Alpha | RED | α_Pyramid_Core/RED/12_PROVIDER_ROUTER | Z13 → Z11 |
| cr_gateway_z10 | Z10 | Alpha | SPINE | α_Pyramid_Core/SPINE/10_CR_GATEWAY | Z11 → Z9 (α/β boundary) |
| agent_bus_z8 | Z8 | Beta | SPINE | β_Pyramid_Functional/SPINE/8_AGENT_BUS | Z9 → Z7 |
| resolution_stream_z6 | Z6 | Beta | SPINE | β_Pyramid_Functional/SPINE/6_RESOLUTION_STREAM | Z7 → Z5 |
| observer_relay_z4 | Z4 | Beta | SPINE | β_Pyramid_Functional/SPINE/4_OBSERVER_RELAY | Z5 → Z3 (β/γ boundary) |
| audit_bridge_z2 | Z2 | Gamma | SPINE | γ_Pyramid_Reflective/SPINE/2_AUDIT_BRIDGE | Z3 → Z1 |

## Full Vertical Flow (Z17 → Z1)

```text
gen-nexus (Z17)
  → [nexus_router_z16]
    → gen-meta (Z15)
      → [policy_bus_z14]
        → gen-bridge (Z13)
          → [provider_router_z12]
            → gen-pear / gh_ci_guardian (Z11)
              → [cr_gateway_z10]  ← Alpha/Beta boundary
════════════════════════════════════════════════
                → gen-async-jobs / gh_pr_resolver (Z9)
                  → [agent_bus_z8]
                    → gen-webmcp / chaos_engine (Z7)
                      → [resolution_stream_z6]
                        → gen-dashboard (Z5)
                          → [observer_relay_z4]  ← Beta/Gamma boundary
════════════════════════════════════════════════
                            → netlify_deploy_beacon (Z3)
                              → [audit_bridge_z2]
                                → deploy_audit_ledger (Z1)
```

## Sync Contract

After any manifest or directory update:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/sync/discover-modules?update_existing=true"
```

To prune ghost nodes:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/canon/guard/apply?update_existing=true&prune_missing=true"
```

## Live Validation

- `http://127.0.0.1:8000/state` — all node IDs present
- `http://127.0.0.1:8000/health/kernel` — kernel ONLINE
- `http://127.0.0.1:3000` — UI pyramid shows all Z-levels

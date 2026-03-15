"""
create_infra_nodes.py
Phase 1+2: Create missing even-Z infra node directories with .node_manifest.json
Run from project root: python tools/create_infra_nodes.py
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def make_node(rel_path: str, manifest: dict):
    path = ROOT / rel_path
    path.mkdir(parents=True, exist_ok=True)
    manifest_file = path / ".node_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"[OK] {rel_path}")

nodes = [
    # ── PHASE 1: orphan .py files -> create their node directories ──

    # Z10 — CR Gateway (alpha SPINE, infra)  [cr_gateway_z10.py already exists in beta root]
    (
        "α_Pyramid_Core/SPINE/10_CR_GATEWAY",
        {
            "id": "cr_gateway_z10",
            "title": "CR Gateway",
            "z_level": 10,
            "sector": "SPINE",
            "coords": {"x": 9, "y": 9, "z": 10},
            "layer_type": "alpha",
            "kind": "router",
            "summary": "Contract relay — routes validated task envelopes from Alpha governance to Beta runtime.",
            "state": "active",
            "links": ["gen-pear", "gen-async-jobs"],
            "runtime_canon_flag": "canon"
        }
    ),
    # Z8 — Agent Bus (beta SPINE, infra)  [agent_bus_z8.py already exists in beta root]
    (
        "β_Pyramid_Functional/SPINE/8_AGENT_BUS",
        {
            "id": "agent_bus_z8",
            "title": "Agent Bus",
            "z_level": 8,
            "sector": "SPINE",
            "coords": {"x": 9, "y": 9, "z": 8},
            "layer_type": "beta",
            "kind": "router",
            "summary": "Inter-agent message bus. Routes tasks and events between Z9 runners and Z7 runtime engines.",
            "state": "active",
            "links": ["gen-async-jobs", "gen-webmcp"],
            "runtime_canon_flag": "runtime"
        }
    ),
    # Z7 — Chaos Engine (beta SPINE, structural service)  [chaos_bus_z7.py exists in beta root]
    (
        "β_Pyramid_Functional/SPINE/7_CHAOS_ENGINE",
        {
            "id": "chaos_engine",
            "title": "Chaos Engine",
            "z_level": 7,
            "sector": "SPINE",
            "coords": {"x": 10, "y": 9, "z": 7},
            "layer_type": "beta",
            "kind": "service",
            "summary": "Chaos bus Z7 — detects anomalies, triggers quarantine, emits Observer events upstream.",
            "state": "active",
            "links": ["agent_bus_z8", "resolution_stream_z6"],
            "runtime_canon_flag": "runtime"
        }
    ),
    # Z6 — Resolution Stream (beta SPINE, infra)  [resolution_stream_z6.py exists in beta root]
    (
        "β_Pyramid_Functional/SPINE/6_RESOLUTION_STREAM",
        {
            "id": "resolution_stream_z6",
            "title": "Resolution Stream",
            "z_level": 6,
            "sector": "SPINE",
            "coords": {"x": 9, "y": 9, "z": 6},
            "layer_type": "beta",
            "kind": "router",
            "summary": "Resolution and event stream — collects outputs from Z7 runtime, relays to Z5 dashboard and Z4 observer.",
            "state": "active",
            "links": ["gen-webmcp", "gen-dashboard"],
            "runtime_canon_flag": "runtime"
        }
    ),
    # Z4 — Observer Relay (beta/gamma boundary SPINE, infra)  [observer_relay_z4.py exists in gamma root]
    (
        "β_Pyramid_Functional/SPINE/4_OBSERVER_RELAY",
        {
            "id": "observer_relay_z4",
            "title": "Observer Relay",
            "z_level": 4,
            "sector": "SPINE",
            "coords": {"x": 9, "y": 9, "z": 4},
            "layer_type": "beta",
            "kind": "router",
            "summary": "Beta-to-Gamma boundary relay. Forwards dashboard events and anomaly signals to Gamma reflective layer.",
            "state": "active",
            "links": ["gen-dashboard", "netlify_deploy_beacon"],
            "runtime_canon_flag": "runtime"
        }
    ),

    # ── PHASE 2: new even-Z infra nodes (no existing .py) ──

    # Z16 — Nexus Router (alpha SPINE, infra)
    (
        "α_Pyramid_Core/SPINE/16_NEXUS_ROUTER",
        {
            "id": "nexus_router_z16",
            "title": "Nexus Router",
            "z_level": 16,
            "sector": "SPINE",
            "coords": {"x": 9, "y": 9, "z": 16},
            "layer_type": "alpha",
            "kind": "router",
            "summary": "Boot orchestration router. Nexus_Boot.py startup sequencing and health-gate between Z17 and Z15.",
            "state": "active",
            "links": ["gen-nexus", "gen-meta"],
            "runtime_canon_flag": "canon"
        }
    ),
    # Z14 — Policy Bus (alpha SPINE, infra)
    (
        "α_Pyramid_Core/SPINE/14_POLICY_BUS",
        {
            "id": "policy_bus_z14",
            "title": "Policy Bus",
            "z_level": 14,
            "sector": "SPINE",
            "coords": {"x": 9, "y": 9, "z": 14},
            "layer_type": "alpha",
            "kind": "router",
            "summary": "Policy dispatcher. Routes EVO META evolution policies and SystemPolicyManager rules down to EVO BRIDGE.",
            "state": "active",
            "links": ["gen-meta", "gen-bridge"],
            "runtime_canon_flag": "canon"
        }
    ),
    # Z12 — Provider Router (alpha RED, infra)
    (
        "α_Pyramid_Core/RED/12_PROVIDER_ROUTER",
        {
            "id": "provider_router_z12",
            "title": "Provider Router",
            "z_level": 12,
            "sector": "RED",
            "coords": {"x": 9, "y": 9, "z": 12},
            "layer_type": "alpha",
            "kind": "router",
            "summary": "AI provider adapter layer. Routes between EVO BRIDGE and downstream runtime: Gemini / OpenAI / Replicate.",
            "state": "active",
            "links": ["gen-bridge", "gh_ci_guardian"],
            "runtime_canon_flag": "canon"
        }
    ),
    # Z2 — Audit Bridge (gamma SPINE, infra)
    (
        "γ_Pyramid_Reflective/SPINE/2_AUDIT_BRIDGE",
        {
            "id": "audit_bridge_z2",
            "title": "Audit Bridge",
            "z_level": 2,
            "sector": "SPINE",
            "coords": {"x": 9, "y": 9, "z": 2},
            "layer_type": "gamma",
            "kind": "router",
            "summary": "Gamma reflection relay. Bridges Netlify Deploy Beacon events to Deploy Audit Ledger at Z1.",
            "state": "active",
            "links": ["netlify_deploy_beacon", "deploy_audit_ledger"],
            "runtime_canon_flag": "runtime"
        }
    ),
]

if __name__ == "__main__":
    print(f"Root: {ROOT}")
    print("-" * 60)
    for rel_path, manifest in nodes:
        make_node(rel_path, manifest)
    print("-" * 60)
    print("[DONE] Phase 1+2 complete. All node dirs + manifests created.")
    print("Next step: POST /sync/discover-modules?update_existing=true")

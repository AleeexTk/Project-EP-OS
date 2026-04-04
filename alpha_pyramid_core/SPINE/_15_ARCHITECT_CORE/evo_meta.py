"""
EvoPyramid Node: EVO META
Layer: α_Pyramid_Core | Sector: SPINE/15_ARCHITECT_CORE
Z-Level: 15  (Previously in PURPLE/15_EVO_META — relocated for canonical compliance)

Provides meta-level reflection and architectural analysis for the evolution cycle.
"""

import json
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[4]
STATE_FILE = ROOT_DIR / "state" / "pyramid_state.json"


def analyze_evolution_meta(observation: str = "Startup meta-check") -> dict:
    """
    Analyze the meta-state of the evolution process.
    Reports architectural health at Z15 (Architect Core) level.
    """
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            state = json.load(fh)
    except Exception:
        state = {"nodes": {}}

    nodes = state.get("nodes", {})
    total = len(nodes)
    active = sum(1 for n in nodes.values() if n.get("state") == "active")

    return {
        "z_level": 15,
        "sector": "SPINE",
        "observation": observation,
        "timestamp": time.time(),
        "total_nodes": total,
        "active_nodes": active,
        "health_pct": round((active / total) * 100, 1) if total else 0.0,
        "meta_status": "coherent" if (active / total >= 0.7 if total else True) else "degraded",
    }


def main():
    result = analyze_evolution_meta()
    print("═" * 52)
    print("  🟣  Z15 EVO META — Architectural Health Report")
    print("═" * 52)
    print(f"  Total nodes  : {result['total_nodes']}")
    print(f"  Active nodes : {result['active_nodes']}")
    print(f"  Health       : {result['health_pct']}%")
    print(f"  Status       : {result['meta_status'].upper()}")
    print("═" * 52)


if __name__ == "__main__":
    main()

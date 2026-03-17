"""
EvoPyramid Node: PEAR LOOP
Layer: α_Pyramid_Core | Sector: GOLD
Z-Level: 11

PEAR = Perception → Evolution → Action → Reflection
Runs one full PEAR cycle against the current pyramid state.
"""

import json
import math
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[4]
STATE_FILE = ROOT_DIR / "state" / "pyramid_state.json"


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"nodes": {}}


def pear_cycle(observation: str, state: dict | None = None) -> dict:
    """
    Full PEAR cycle.

    P — Perception   : observe current node states
    E — Evolution    : detect anomalies / entropy shift
    A — Action       : produce recommended actions
    R — Reflection   : log cycle outcome
    """
    if state is None:
        state = load_state()

    nodes = state.get("nodes", {})
    total = len(nodes)

    # ── Perception ────────────────────────────────────────────────────────────
    state_counts: dict = {}
    for n in nodes.values():
        s = n.get("state", "unknown")
        state_counts[s] = state_counts.get(s, 0) + 1

    # ── Evolution ─────────────────────────────────────────────────────────────
    error_count  = state_counts.get("error", 0)
    active_count = state_counts.get("active", 0)
    entropy = 0.0
    if total > 0:
        for c in state_counts.values():
            p = c / total
            if p > 0:
                entropy -= p * math.log2(p)

    coherence = round((active_count / total) * 100, 1) if total else 0.0
    anomaly = error_count > (total * 0.3)  # >30% error nodes = anomaly

    # ── Action ────────────────────────────────────────────────────────────────
    actions: list[str] = []
    if anomaly:
        actions.append("Run POST /canon/guard/apply to heal drifted nodes")
        actions.append("Inspect gen-* node directories for missing index.py")
    if entropy > 1.5:
        actions.append("High entropy detected — trigger Z7 synthesis cycle")
    if not actions:
        actions.append("System coherent — no action required")

    # ── Reflection ────────────────────────────────────────────────────────────
    reflection = {
        "observation": observation,
        "timestamp": time.time(),
        "total_nodes": total,
        "state_counts": state_counts,
        "entropy_bits": round(entropy, 4),
        "coherence_pct": coherence,
        "anomaly_detected": anomaly,
        "recommended_actions": actions,
        "status": "coherent" if coherence >= 70 else "degraded",
    }
    return reflection


def main():
    result = pear_cycle("Startup self-check from PEAR LOOP node")
    print("═" * 52)
    print("  🍐  Z11 PEAR LOOP Cycle Result")
    print("═" * 52)
    print(f"  Nodes total   : {result['total_nodes']}")
    print(f"  Coherence     : {result['coherence_pct']}%")
    print(f"  Entropy       : {result['entropy_bits']} bits")
    print(f"  Anomaly       : {'⚠️  YES' if result['anomaly_detected'] else '✅ No'}")
    print(f"  Status        : {result['status'].upper()}")
    print()
    print("  Recommended actions:")
    for action in result["recommended_actions"]:
        print(f"    → {action}")
    print("═" * 52)


if __name__ == "__main__":
    main()

"""
EvoPyramid Node: EVO META
Layer: α_Pyramid_Core | Sector: PURPLE
Z-Level: 15

Self-governance and evolution policy.
Reads pyramid state, measures entropy, and reports compliance score.
"""

import json
import math
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
STATE_FILE = ROOT_DIR / "state" / "pyramid_state.json"


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"nodes": {}}


def measure_entropy(nodes: dict) -> float:
    """Shannon entropy over node states — lower is more ordered."""
    total = len(nodes)
    if total == 0:
        return 0.0
    counts: dict = {}
    for n in nodes.values():
        s = n.get("state", "unknown")
        counts[s] = counts.get(s, 0) + 1
    entropy = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            entropy -= p * math.log2(p)
    return round(entropy, 4)


def main():
    state = load_state()
    nodes = state.get("nodes", {})
    entropy = measure_entropy(nodes)
    active = sum(1 for n in nodes.values() if n.get("state") == "active")
    error  = sum(1 for n in nodes.values() if n.get("state") == "error")
    total  = len(nodes)

    compliance = round((active / total) * 100, 1) if total else 0.0

    print("═" * 48)
    print("  🟣  Z15 EVO META — Self-Governance Report")
    print("═" * 48)
    print(f"  Total nodes    : {total}")
    print(f"  Active         : {active}")
    print(f"  Error          : {error}")
    print(f"  Entropy        : {entropy} bits")
    print(f"  Compliance     : {compliance}%")
    policy = "STABLE" if compliance >= 50 else "DEGRADED — evolution cycle required"
    print(f"  Policy status  : {policy}")
    print("═" * 48)


if __name__ == "__main__":
    main()

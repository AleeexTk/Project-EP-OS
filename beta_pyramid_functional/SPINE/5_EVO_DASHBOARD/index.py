"""
EvoPyramid Node: EVO DASHBOARD
Layer: β_Pyramid_Functional | Sector: SPINE
Z-Level: 5

Operator view and assistant workspace.
Reads pyramid state and prints a rich terminal dashboard.
"""

import json
import time
from pathlib import Path
from typing import Dict

ROOT_DIR = Path(__file__).resolve().parents[3]
STATE_FILE = ROOT_DIR / "state" / "pyramid_state.json"
SESSION_LOG = ROOT_DIR / "β_Pyramid_Functional" / "logs" / "async_jobs.jsonl"


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"nodes": {}}


def recent_jobs(n: int = 5) -> list:
    try:
        lines = SESSION_LOG.read_text(encoding="utf-8").splitlines()
        return [json.loads(l) for l in lines[-n:] if l.strip()]
    except Exception:
        return []


STATE_ICONS: Dict[str, str] = {
    "active": "🟢",
    "idle":   "🟡",
    "error":  "🔴",
    "degraded": "🟠",
    "quarantined": "🔵",
    "failed": "⚫",
}


def main():
    state = load_state()
    nodes = state.get("nodes", {})
    total = len(nodes)

    counts: Dict[str, int] = {}
    for n in nodes.values():
        s = n.get("state", "unknown")
        counts[s] = counts.get(s, 0) + 1

    active_pct = round(counts.get("active", 0) / total * 100, 1) if total else 0.0

    print()
    print("╔" + "═" * 56 + "╗")
    print("║  📊  EVO DASHBOARD — EvoPyramid OS Operator View      ║")
    print("╠" + "═" * 56 + "╣")
    print(f"║  Z-Level     : 5  │  Sector: SPINE                   ║")
    print(f"║  Timestamp   : {time.strftime('%Y-%m-%d %H:%M:%S')}                  ║")
    print("╠" + "═" * 56 + "╣")
    print(f"║  Total nodes : {total:<4}                                    ║")
    for state_name, count in sorted(counts.items()):
        icon = STATE_ICONS.get(state_name, "⚫")
        bar = ("█" * (count * 2)).ljust(20)
        line = f"  {icon} {state_name:<12}: {count:>3}  {bar}"
        print(f"║ {line:<55}║")
    print(f"║  Health pct  : {active_pct}%                                 ║")
    print("╠" + "═" * 56 + "╣")

    # Layer breakdown
    layers = {"alpha": 0, "beta": 0, "gamma": 0}
    for n in nodes.values():
        lt = n.get("layer_type", "")
        if lt in layers:
            layers[lt] += 1
    print(f"║  α Core      : {layers['alpha']:<4} nodes (Z≥11)                     ║")
    print(f"║  β Functional: {layers['beta']:<4} nodes (Z5–9)                    ║")
    print(f"║  γ Reflective: {layers['gamma']:<4} nodes (Z≤3)                     ║")
    print("╠" + "═" * 56 + "╣")

    # Recent jobs
    jobs = recent_jobs(5)
    if jobs:
        print("║  Recent async jobs:                                    ║")
        for job in jobs:
            icon = "✅" if job.get("status") == "done" else "❌"
            label = job.get("label", "?")[:20]
            dur   = job.get("duration", 0)
            print(f"║    {icon} {label:<22} {dur:.3f}s                ║")
    else:
        print("║  No async job history yet.                             ║")

    print("╚" + "═" * 56 + "╝")
    print()


if __name__ == "__main__":
    main()

"""
ApexCore — Z17 SPINE · alpha_pyramid_core
Global module registry and PEAR pulse initiator.
The apex of the Z17 pyramid: loads state, reports node health,
and fires the primary PEAR impulse downstream.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# ── Project root resolution ────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT_DIR / "state" / "pyramid_state.json"

# ── Registry ───────────────────────────────────────────────────────────────────

class ApexCore:
    """
    Z17 — Global Nexus registry.
    Maintains a read-only view of all registered pyramid nodes and
    provides the primary PEAR pulse interface.
    """

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self._registry: Dict[str, dict] = {}
        self._loaded_at: Optional[float] = None
        self.load()

    # ── Loading ────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load pyramid_state.json into the in-memory registry."""
        try:
            with open(self.state_file, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            self._registry = raw.get("nodes", {})
            self._loaded_at = time.time()
            print(f"👑 [Z17] ApexCore: Loaded {len(self._registry)} nodes from registry.")
        except FileNotFoundError:
            print(f"⚠️  [Z17] ApexCore: State file not found at {self.state_file}. Starting empty.")
            self._registry = {}
        except json.JSONDecodeError as exc:
            print(f"❌ [Z17] ApexCore: Failed to parse state file — {exc}")
            self._registry = {}

    def reload(self) -> None:
        """Hot-reload the registry (useful after a /sync/discover-modules call)."""
        self.load()

    # ── Registry queries ───────────────────────────────────────────────────────

    def get_node(self, node_id: str) -> Optional[dict]:
        return self._registry.get(node_id)

    def all_nodes(self) -> List[dict]:
        return list(self._registry.values())

    def nodes_by_layer(self, layer: str) -> List[dict]:
        """Filter nodes by layer_type ('alpha', 'beta', 'gamma')."""
        return [n for n in self.all_nodes() if n.get("layer_type") == layer]

    def nodes_by_state(self, state: str) -> List[dict]:
        """Filter nodes by state ('active', 'idle', 'error', etc.)."""
        return [n for n in self.all_nodes() if n.get("state") == state]

    # ── Status report ──────────────────────────────────────────────────────────

    def status_report(self) -> dict:
        """Return a structured health summary of the full registry."""
        all_nodes = self.all_nodes()
        counts: Dict[str, int] = {}
        for node in all_nodes:
            s = str(node.get("state", "unknown"))
            counts[s] = counts.get(s, 0) + 1

        return {
            "z_level": 17,
            "sector": "SPINE",
            "module": "apex_core",
            "total_nodes": len(all_nodes),
            "state_counts": counts,
            "loaded_at": self._loaded_at,
            "alpha_nodes": len(self.nodes_by_layer("alpha")),
            "beta_nodes": len(self.nodes_by_layer("beta")),
            "gamma_nodes": len(self.nodes_by_layer("gamma")),
        }

    def print_report(self) -> None:
        """Pretty-print the node registry status."""
        report = self.status_report()
        print("\n" + "═" * 56)
        print("  👑  Z17 APEX CORE — Global Registry Report")
        print("═" * 56)
        print(f"  Total nodes : {report['total_nodes']}")
        print(f"  Alpha (Z≥11): {report['alpha_nodes']}")
        print(f"  Beta  (Z5-9): {report['beta_nodes']}")
        print(f"  Gamma (Z≤3) : {report['gamma_nodes']}")
        print()
        for state, count in sorted(report["state_counts"].items()):
            icon = {"active": "🟢", "idle": "🟡", "error": "🔴", "degraded": "🟠"}.get(state, "⚫")
            print(f"  {icon}  {state:12s}: {count}")
        print("═" * 56 + "\n")

    # ── PEAR pulse ─────────────────────────────────────────────────────────────

    def initiate_pear_pulse(self, intent: str = "System coherence check") -> dict:
        """
        Fire the primary PEAR (Perception-Evolution-Action-Reflection) pulse.
        Returns a pulse packet ready to be forwarded downstream (Z15 → Z9 → Z7).
        """
        pulse = {
            "pulse_id": f"apex_{int(time.time())}",
            "origin": "Z17_APEX_CORE",
            "intent": intent,
            "fired_at": time.time(),
            "node_snapshot": {
                "total": len(self._registry),
                "active": len(self.nodes_by_state("active")),
                "error": len(self.nodes_by_state("error")),
            },
        }
        print(f"⚡ [Z17] PEAR pulse fired → intent='{intent}' | nodes={pulse['node_snapshot']}")
        return pulse


# ── CLI entry point ────────────────────────────────────────────────────────────

def main() -> None:
    apex = ApexCore()
    apex.print_report()

    if "--pulse" in sys.argv or len(sys.argv) == 1:
        intent = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Startup coherence check"
        pulse = apex.initiate_pear_pulse(intent)
        print(f"📤 Pulse packet: {json.dumps(pulse, indent=2)}")


if __name__ == "__main__":
    main()

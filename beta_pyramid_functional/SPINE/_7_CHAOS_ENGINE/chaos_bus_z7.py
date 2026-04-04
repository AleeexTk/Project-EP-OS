"""
ChaosBus — Z7 GREEN · beta_pyramid_functional  (Dialectical Crucible)
Receives 4-agent outputs from Z8 Agent Bus, applies weighted synthesis,
and routes a resolved decision downstream to Z5 Action Layer.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
RESOLUTION_LOG = ROOT_DIR / "beta_pyramid_functional" / "logs" / "chaos_resolutions.jsonl"
RESOLUTION_LOG.parent.mkdir(parents=True, exist_ok=True)

# ── Agent weight config (matches architectural role framing) ──────────────────
AGENT_WEIGHTS: Dict[str, float] = {
    "Trailblazer": 0.30,   # Engineering speed
    "Soul":        0.25,   # Ethical alignment
    "Provocateur": 0.25,   # Critical challenge — increases with task complexity
    "Prometheus":  0.20,   # Synthesis / expansion
}

# If no recognised role, fall back to equal weight
DEFAULT_WEIGHT = 0.25


# ── Synthesis helpers ──────────────────────────────────────────────────────────

def _get_weight(agent_name: str) -> float:
    """Return the configured weight for *agent_name* (case-insensitive)."""
    for key, w in AGENT_WEIGHTS.items():
        if key.lower() in agent_name.lower():
            return w
    return DEFAULT_WEIGHT


def _complexity_adjust(outputs: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Scale Provocateur weight up when there are conflicting statuses —
    embodying the architectural rule: 'harder task → more weight to Provocateur'.
    """
    weights = {o.get("agent", "unknown"): _get_weight(o.get("agent", "")) for o in outputs}
    statuses = {o.get("status", "") for o in outputs}
    conflict_detected = len(statuses) > 1
    if conflict_detected:
        for key in list(weights.keys()):
            if "provocateur" in key.lower():
                weights[key] = min(weights[key] * 1.5, 0.50)
        # Re-normalise
        total = sum(weights.values()) or 1.0
        weights = {k: v / total for k, v in weights.items()}
    return weights


# ── Core engine ────────────────────────────────────────────────────────────────

class ChaosBus:
    """
    Z7 Dialectical Crucible.

    Accepts agent cluster outputs, performs weighted synthesis,
    emits a unified Resolution packet.
    """

    def __init__(self, log_file: Path = RESOLUTION_LOG):
        self._log_file = log_file
        self._cycle_count = 0
        print("🌀 [Z7] ChaosBus initialised — Dialectical Crucible ready.")

    # ── Synthesis ──────────────────────────────────────────────────────────────

    def synthesize(self, agent_outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge agent outputs into a single Resolution.

        Args:
            agent_outputs: List of dicts, each with keys:
                           'agent', 'status', 'output' (+ optional 'weight')

        Returns:
            Resolution dict with synthesis metadata.
        """
        if not agent_outputs:
            return {"status": "empty", "synthesis": "No agent outputs received."}

        weights = _complexity_adjust(agent_outputs)
        conflict_detected = len({o.get("status") for o in agent_outputs}) > 1

        # Build weighted consensus narrative
        lines: List[str] = []
        dominant_agent = max(agent_outputs, key=lambda o: weights.get(o.get("agent", ""), 0.0))

        for output in agent_outputs:
            ag = output.get("agent", "unknown")
            w = weights.get(ag, DEFAULT_WEIGHT)
            lines.append(f"[{ag} @{w:.0%}] {output.get('output', '')}")

        synthesis_text = " | ".join(lines)

        resolution: Dict[str, Any] = {
            "arbitration": "dialectical_synthesis",
            "conflict_detected": conflict_detected,
            "dominant_agent": dominant_agent.get("agent"),
            "dominant_weight": weights.get(dominant_agent.get("agent", ""), 0.0),
            "synthesis": synthesis_text,
            "agent_count": len(agent_outputs),
            "weights": weights,
        }
        return resolution

    # ── Full cycle ─────────────────────────────────────────────────────────────

    def run_cycle(
        self,
        pulse_data: Dict[str, Any],
        orchestrator: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Full chaos cycle:
          1. Run Z9 orchestrator (4-agent cluster) on *pulse_data*
          2. Synthesize outputs via weighted arbitration
          3. Persist resolution log
          4. Return resolution packet

        If *orchestrator* is None, attempts to import Z9Orchestrator.
        """
        self._cycle_count += 1
        cycle_id = f"z7_{self._cycle_count}_{int(time.time())}"

        print(f"\n🌀 [Z7] Chaos Cycle #{self._cycle_count} — intent='{pulse_data.get('intent')}'")
        print("   ├─ Running 4-agent cluster (Z9)...")

        # Import orchestrator lazily to avoid circular deps
        if orchestrator is None:
            try:
                agent_dir = ROOT_DIR / "beta_pyramid_functional" / "A_Agents"
                sys.path.insert(0, str(agent_dir))
                from agent_orch import Z9Orchestrator  # type: ignore
                orchestrator = Z9Orchestrator()
            except ImportError:
                print("   ⚠️  [Z7] Z9Orchestrator not found — using mock agents.")
                orchestrator = None

        if orchestrator is not None:
            agent_outputs = orchestrator.run_pear_cluster(pulse_data)
        else:
            # Minimal mock when orchestrator unavailable
            agent_outputs = [
                {"agent": "Trailblazer", "status": "optimized", "output": "Direct path (mock)"},
                {"agent": "Soul",        "status": "evaluated", "output": "Ethics OK (mock)"},
                {"agent": "Provocateur", "status": "challenged", "output": "Assumptions questioned (mock)"},
                {"agent": "Prometheus",  "status": "synthesized","output": "Context integrated (mock)"},
            ]

        print("   ├─ Synthesising outputs...")
        resolution = self.synthesize(agent_outputs)

        packet: Dict[str, Any] = {
            "cycle_id": cycle_id,
            "pulse_id": pulse_data.get("pulse_id", cycle_id),
            "intent": pulse_data.get("intent"),
            "timestamp": time.time(),
            "resolution": resolution,
            "routed_to": "Z5_ACTION_LAYER",
        }

        # Persist
        try:
            with open(self._log_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(packet, ensure_ascii=False) + "\n")
        except OSError as exc:
            print(f"   ⚠️  [Z7] Resolution log write failed: {exc}")

        dominant = resolution.get("dominant_agent", "?")
        conflict = "⚔️  conflict" if resolution.get("conflict_detected") else "✅ consensus"
        print(f"   └─ Resolution: {conflict} | dominant={dominant}")
        return packet

    def stats(self) -> Dict[str, Any]:
        return {
            "z_level": 7,
            "sector": "GREEN",
            "module": "chaos_bus",
            "cycles_run": self._cycle_count,
        }


# ── CLI self-test ──────────────────────────────────────────────────────────────

def main() -> None:
    bus = ChaosBus()

    test_pulse = {
        "pulse_id": f"test_{int(time.time())}",
        "intent": "Validate Z7 synthesis engine",
        "origin": "CLI_TEST",
    }

    result = bus.run_cycle(test_pulse)

    print("\n📤 Resolution packet:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    print(f"\n✅ [Z7] Self-test complete. Stats: {bus.stats()}")


if __name__ == "__main__":
    main()

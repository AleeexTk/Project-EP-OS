"""
AgentBusZ8 — Z8 SPINE · beta_pyramid_functional
Infrastructure nerve layer: in-memory pulse bus between Z9 agent cluster and
Z7 Chaos Bus. Thread-safe publish/subscribe with JSONL persistence.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT_DIR / "beta_pyramid_functional" / "logs" / "agent_bus.jsonl"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

MAX_QUEUE = 512  # maximum in-memory pulses retained


# ── Core bus ───────────────────────────────────────────────────────────────────

class AgentBusZ8:
    """
    Z8 Event bus — the nervous system between Z9 agents and Z7 Chaos Bus.

    Usage:
        bus = AgentBusZ8()
        bus.subscribe("chaos_bus", my_callback)
        bus.transmit("Trailblazer", "chaos_bus", {"status": "optimized"})
    """

    def __init__(self, log_file: Path = LOG_FILE, max_queue: int = MAX_QUEUE):
        self._log_file = log_file
        self._queue: deque[Dict[str, Any]] = deque(maxlen=max_queue)
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._pulse_count = 0
        print(f"⚡ [Z8] AgentBus initialised. Log → {log_file}")

    # ── Subscribe ──────────────────────────────────────────────────────────────

    def subscribe(self, target: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback to receive pulses directed to *target*."""
        with self._lock:
            self._subscribers.setdefault(target, [])
            if callback not in self._subscribers[target]:
                self._subscribers[target].append(callback)
        print(f"🔗 [Z8] Subscribed to target='{target}'")

    def unsubscribe(self, target: str, callback: Callable) -> None:
        with self._lock:
            if target in self._subscribers:
                self._subscribers[target] = [
                    cb for cb in self._subscribers[target] if cb is not callback
                ]

    # ── Transmit ───────────────────────────────────────────────────────────────

    def transmit(
        self,
        source_agent: str,
        target: str,
        data: Dict[str, Any],
        *,
        parity: str = "even",
    ) -> Dict[str, Any]:
        """
        Transmit a pulse from *source_agent* to *target*.
        Persists to JSONL log, stores in memory queue, and calls subscribers.
        Returns the complete pulse entry.
        """
        with self._lock:
            self._pulse_count += 1
            pulse_id = f"z8_{self._pulse_count}_{int(time.time())}"

        entry: Dict[str, Any] = {
            "pulse_id": pulse_id,
            "timestamp": time.time(),
            "source": source_agent,
            "target": target,
            "payload": data,
            "parity": parity,
            "z_level": 8,
        }

        # Persist to disk
        try:
            with open(self._log_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as exc:
            print(f"⚠️  [Z8] Log write failed: {exc}")

        # Store in queue
        with self._lock:
            self._queue.append(entry)
            callbacks = list(self._subscribers.get(target, []))

        # Notify subscribers outside the lock
        for cb in callbacks:
            try:
                cb(entry)
            except Exception as exc:   # noqa: BLE001
                print(f"⚠️  [Z8] Subscriber error for target='{target}': {exc}")

        print(
            f"⚡ [Z8] Pulse #{self._pulse_count}: {source_agent} → {target} "
            f"| payload_keys={list(data.keys())}"
        )
        return entry

    # ── Broadcast ──────────────────────────────────────────────────────────────

    def broadcast(self, source_agent: str, data: Dict[str, Any]) -> None:
        """Send pulse to ALL registered targets."""
        with self._lock:
            targets = list(self._subscribers.keys())
        for target in targets:
            self.transmit(source_agent, target, data, parity="broadcast")

    # ── Queue inspection ───────────────────────────────────────────────────────

    def recent(self, n: int = 20) -> List[Dict[str, Any]]:
        """Return the last *n* pulses from the in-memory queue."""
        with self._lock:
            return list(self._queue)[-n:]

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "z_level": 8,
                "total_transmitted": self._pulse_count,
                "queue_size": len(self._queue),
                "subscribers": {k: len(v) for k, v in self._subscribers.items()},
            }


# ── Module-level singleton ─────────────────────────────────────────────────────

_bus: Optional[AgentBusZ8] = None


def get_bus() -> AgentBusZ8:
    """Return (or create) the module-level AgentBusZ8 singleton."""
    global _bus
    if _bus is None:
        _bus = AgentBusZ8()
    return _bus


# ── CLI self-test ──────────────────────────────────────────────────────────────

def main() -> None:
    bus = AgentBusZ8()

    received: list = []

    def mock_chaos(pulse):
        received.append(pulse)
        print(f"   📥 [Chaos mock] received pulse from {pulse['source']}")

    bus.subscribe("chaos_bus", mock_chaos)

    # Simulate 4 agent outputs
    agents = ["Trailblazer", "Soul", "Provocateur", "Prometheus"]
    payloads = [
        {"status": "optimized", "output": "Direct path found"},
        {"status": "evaluated", "output": "Ethical alignment confirmed"},
        {"status": "challenged", "output": "Blind spots identified"},
        {"status": "synthesized", "output": "Global context integrated"},
    ]

    for agent, payload in zip(agents, payloads):
        bus.transmit(agent, "chaos_bus", payload)
        time.sleep(0.05)

    print(f"\n✅ [Z8] Self-test complete. Pulses delivered: {len(received)}/4")
    print(f"   Stats: {bus.stats()}")


if __name__ == "__main__":
    main()

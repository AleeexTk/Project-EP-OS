"""
Observer Relay Z4 (beta_pyramid_functional)
Real-time architectural health monitor.

Reads evolution_journal.json to classify recent node activity,
computes a live health score, persists a heartbeat to ProjectCortex,
and optionally broadcasts a health_pulse event to the AgentBus.
"""

import asyncio
import json
import logging
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --- EMERGENCY PATH INJECTION ---
root_dir = Path(__file__).resolve().parents[3]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex
from beta_pyramid_functional.B1_Kernel.SK_Engine.models import QuantumBlock

logger = logging.getLogger("ObserverRelay")


class ObserverRelay:
    """
    Z4 Reflective Node — Beta Pyramid.

    Computes real-time health from:
    1. evolution_journal.json — task outcomes (ACCEPTED / REJECTED)
    2. .node_manifest.json presence count — structural completeness

    Health formula:
        score = (accepted_tasks / total_tasks) * 0.6
              + (manifests_found / expected_manifests) * 0.4
    """

    EXPECTED_MANIFESTS = 27  # last known total from V10 audit

    def __init__(self, project_root: Path):
        self.root = project_root
        self.journal_path = (
            project_root
            / "beta_pyramid_functional"
            / "D_Interface"
            / "evolution_journal.json"
        )

    # ─────────────────────────────────────────
    #  Health Calculation
    # ─────────────────────────────────────────

    def _count_manifests(self) -> int:
        """Count .node_manifest.json files across the whole project."""
        count = 0
        for p in self.root.rglob(".node_manifest.json"):
            count += 1
        return count

    def _compute_journal_health(self, window_hours: int = 24) -> tuple[int, int]:
        """
        Parse the journal for entries in the last `window_hours`.
        Returns (accepted_count, total_count).
        """
        if not self.journal_path.exists():
            return 0, 0

        try:
            with open(self.journal_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read journal: {e}")
            return 0, 0

        cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
        accepted = 0
        total = 0

        for entry in data.get("journal", []):
            ts_str = entry.get("timestamp", "").replace("Z", "+00:00")
            try:
                ts = datetime.fromisoformat(ts_str)
            except ValueError:
                continue

            if ts < cutoff:
                continue

            total += 1
            if entry.get("status") == "ACCEPTED":
                accepted += 1

        return accepted, total

    def compute_health(self) -> dict:
        """Return a structured health report dict."""
        manifests = self._count_manifests()
        accepted, total = self._compute_journal_health()

        manifest_ratio = min(manifests / self.EXPECTED_MANIFESTS, 1.0)
        journal_ratio = (accepted / total) if total > 0 else 1.0  # no data = assume ok

        score = round((journal_ratio * 0.6 + manifest_ratio * 0.4) * 100, 1)

        return {
            "health_pct": score,
            "manifests_found": manifests,
            "expected_manifests": self.EXPECTED_MANIFESTS,
            "recent_tasks_total": total,
            "recent_tasks_accepted": accepted,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ─────────────────────────────────────────
    #  Pulse — persist to ProjectCortex
    # ─────────────────────────────────────────

    async def pulse(self) -> dict:
        """Perform a single health observation and persist to ProjectCortex."""
        report = self.compute_health()

        summary = (
            f"HEALTH PULSE | {report['timestamp']} | "
            f"Score: {report['health_pct']}% | "
            f"Manifests: {report['manifests_found']}/{report['expected_manifests']} | "
            f"Tasks (24h): {report['recent_tasks_accepted']}/{report['recent_tasks_total']} ACCEPTED"
        )

        cortex = await ProjectCortex.get_instance()
        block = QuantumBlock(
            id=f"pulse_{uuid.uuid4().hex[:8]}",
            content=summary,
            metadata={
                "type": "health_pulse",
                "z_level": 4,
                "node": "OBSERVER_RELAY_BETA",
                **report,
            },
        )
        await cortex.add_block(block)

        logger.info(
            f"[Z4] Health Pulse persisted — {report['health_pct']}% "
            f"({report['manifests_found']} manifests, "
            f"{report['recent_tasks_accepted']}/{report['recent_tasks_total']} recent tasks OK)"
        )

        return report

    # ─────────────────────────────────────────
    #  Continuous Monitor
    # ─────────────────────────────────────────

    async def run(self, interval_seconds: int = 60):
        """Run continuous health monitoring loop."""
        logger.info(f"[Z4] Observer Relay active (interval={interval_seconds}s).")
        while True:
            await self.pulse()
            await asyncio.sleep(interval_seconds)


# ─────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────

async def main():
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="ObserverRelay Z4 — Health Monitor")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single pulse and print the report, then exit.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Pulse interval in seconds when running in continuous mode (default: 60).",
    )
    args = parser.parse_args()

    relay = ObserverRelay(root_dir)

    if args.once:
        report = await relay.pulse()
        print("\n─── Health Report ───")
        for k, v in report.items():
            print(f"  {k}: {v}")
    else:
        await relay.run(interval_seconds=args.interval)


if __name__ == "__main__":
    asyncio.run(main())

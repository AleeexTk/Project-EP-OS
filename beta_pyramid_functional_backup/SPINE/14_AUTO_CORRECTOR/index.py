import asyncio
import json
import logging
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

# --- EMERGENCY PATH INJECTION ---
root_dir = Path(__file__).resolve().parents[3]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from beta_pyramid_functional.B2_Orchestrator.auto_corrector import AutoCorrector
from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex
from beta_pyramid_functional.B1_Kernel.SK_Engine.models import QuantumBlock

logger = logging.getLogger("AutoCorrectorNode")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


class AutoCorrectorNode:
    def __init__(self, project_root: Path):
        self.root = project_root
        self.journal_path = (
            project_root
            / "beta_pyramid_functional"
            / "D_Interface"
            / "evolution_journal.json"
        )
        self.corrector = AutoCorrector()
        # Look back 1 hour on first scan, using UTC
        self.last_check = datetime.now(timezone.utc) - timedelta(hours=1)

    # ─────────────────────────────────────────
    #  Inject Failure (для тестирования цикла)
    # ─────────────────────────────────────────
    def inject_synthetic_failure(self, target_file: str = "") -> str:
        """
        Вставляет синтетическую FAILED-запись в evolution_journal.json,
        содержащую реальный traceback внутри проекта.
        Возвращает task_id инъекции.
        """
        import uuid

        # Выбираем существующий файл проекта чтобы AutoCorrector мог его прочитать
        if not target_file:
            candidate = (
                self.root
                / "beta_pyramid_functional"
                / "B2_Orchestrator"
                / "synthesis_agent.py"
            )
            target_file = str(candidate)

        task_id = f"synthetic_{uuid.uuid4().hex[:8]}"
        fake_traceback = (
            "Traceback (most recent call last):\n"
            f'  File "{target_file}", line 42, in scan_and_synthesize\n'
            "    clusters = self._cluster_signatures(sigs)\n"
            "AttributeError: 'NoneType' object has no attribute 'items'"
        )

        entry = {
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "injector_z0",
            "origin_z": 0,
            "action": "synthetic_failure_injection",
            "result_summary": f"FAILED | {fake_traceback}",
            "status": "REJECTED",
        }

        # Загружаем или создаём журнал
        if self.journal_path.exists():
            with open(self.journal_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"protocol": "Trinity-Soft-Lang", "version": "1.0", "journal": []}

        data["journal"].append(entry)

        with open(self.journal_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"[INJECTOR] Synthetic failure injected → task_id: {task_id}")
        return task_id

    # ─────────────────────────────────────────
    #  Journal Scanner
    # ─────────────────────────────────────────
    async def scan_for_failures(self):
        """Scan the Evolution Journal for recent task failures."""
        if not self.journal_path.exists():
            logger.warning("Evolution Journal not found — nothing to scan.")
            return []

        try:
            with open(self.journal_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            entries = data.get("journal", [])
            failures = []

            for entry in entries:
                ts_str = entry.get("timestamp", "").replace("Z", "+00:00")
                try:
                    ts = datetime.fromisoformat(ts_str)
                except ValueError:
                    continue

                if ts > self.last_check:
                    res = entry.get("result_summary", "")
                    if (
                        "FAILED" in res
                        or "Error" in res
                        or entry.get("status") == "REJECTED"
                    ):
                        failures.append(entry)

            return failures
        except Exception as e:
            logger.error(f"Failed to scan journal: {e}")
            return []

    # ─────────────────────────────────────────
    #  Healing Cycle
    # ─────────────────────────────────────────
    async def run_healing_cycle(self, run_once: bool = False):
        """Active loop for detecting and repairing system errors."""
        logger.info("Auto-Corrector (Z12) active. Monitoring Evolution Journal...")
        cortex = await ProjectCortex.get_instance()

        while True:
            failures = await self.scan_for_failures()

            if not failures:
                logger.info("[Z12] No new failures detected.")
            else:
                for fail in failures:
                    error_text = fail.get("result_summary", "")
                    logger.info(
                        f"[Z12] Detected failure in task {fail.get('task_id', '?')}: "
                        f"{error_text[:120]}..."
                    )

                    proposal = await self.corrector.propose_fix(error_text)
                    if proposal:
                        logger.info(
                            f"[Z12] ✅ Self-healing proposal generated for"
                            f" {proposal.target_node}"
                        )
                        block = QuantumBlock(
                            id=f"heal_{fail.get('task_id', 'unknown')}",
                            content=(
                                f"SELF-HEAL PROPOSAL: {proposal.rationale}\n"
                                f"ACTION: {proposal.suggested_action}"
                            ),
                            metadata={
                                "tags": ["self-healing", "patch", proposal.target_node],
                                "proposal_type": proposal.type,
                            },
                        )
                        await cortex.add_block(block)
                        logger.info(
                            f"[Z12] Proposal persisted to ProjectCortex (id={block.id})"
                        )
                    else:
                        logger.warning(
                            f"[Z12] Could not generate proposal for task "
                            f"{fail.get('task_id', '?')}. "
                            "Check if the traceback path exists locally."
                        )

            self.last_check = datetime.now(timezone.utc)

            if run_once:
                logger.info("[Z12] --run-once mode: exiting after first scan.")
                break

            await asyncio.sleep(60)  # Scan every minute


# ─────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────
async def run(args):
    node = AutoCorrectorNode(root_dir)

    if args.inject_failure:
        injected_id = node.inject_synthetic_failure()
        logger.info(f"[INJECTOR] Injection complete. Resuming with healing cycle...")
        # Give scan window time to include the fresh entry
        node.last_check = datetime.now(timezone.utc) - timedelta(minutes=5)

    await node.run_healing_cycle(run_once=args.run_once)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AutoCorrectorNode (Z12) — Self-Healing Loop"
    )
    parser.add_argument(
        "--inject-failure",
        action="store_true",
        help="Inject a synthetic FAILED entry into the Evolution Journal before scanning.",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Scan once and exit (no infinite loop — useful for testing).",
    )
    args = parser.parse_args()
    asyncio.run(run(args))

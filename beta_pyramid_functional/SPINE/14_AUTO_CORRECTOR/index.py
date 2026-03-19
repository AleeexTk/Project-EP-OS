import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# --- EMERGENCY PATH INJECTION ---
root_dir = Path(__file__).resolve().parents[3]
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from beta_pyramid_functional.B2_Orchestrator.auto_corrector import AutoCorrector
from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex
from beta_pyramid_functional.B1_Kernel.SK_Engine.models import QuantumBlock

logger = logging.getLogger("AutoCorrectorNode")
logging.basicConfig(level=logging.INFO)

class AutoCorrectorNode:
    def __init__(self, project_root: Path):
        self.root = project_root
        self.journal_path = project_root / "beta_pyramid_functional" / "D_Interface" / "evolution_journal.json"
        self.corrector = AutoCorrector()
        self.last_check = datetime.now()

    async def scan_for_failures(self):
        """Scan the Evolution Journal for recent task failures."""
        if not self.journal_path.exists():
            return []

        try:
            with open(self.journal_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            entries = data.get("entries", [])
            failures = []
            
            for entry in entries:
                ts = datetime.fromisoformat(entry["timestamp"])
                # Only check new entries
                if ts > self.last_check:
                    res = entry.get("result_summary", "")
                    if "FAILED" in res or "Error" in res or entry.get("status") == "REJECTED":
                        failures.append(entry)
            
            return failures
        except Exception as e:
            logger.error(f"Failed to scan journal: {e}")
            return []

    async def run_healing_cycle(self):
        """Active loop for detecting and repairing system errors."""
        logger.info("Auto-Corrector (Z12) active. Monitoring Evolution Journal...")
        cortex = await ProjectCortex.get_instance()
        
        while True:
            failures = await self.scan_for_failures()
            for fail in failures:
                error_text = fail.get("result_summary", "")
                logger.info(f"Detected failure in task {fail['task_id']}: {error_text[:100]}...")
                
                proposal = await self.corrector.propose_fix(error_text)
                if proposal:
                    logger.info(f"Self-healing proposal generated for {proposal.target_node}")
                    # Persist proposal to Cortex for Architect review
                    block = QuantumBlock(
                        id=f"heal_{fail['task_id']}",
                        content=f"SELF-HEAL PROPOSAL: {proposal.rationale}\nACTION: {proposal.suggested_action}",
                        tags=["self-healing", "patch", proposal.target_node]
                    )
                    await cortex.add_block(block)
                
            self.last_check = datetime.now()
            await asyncio.sleep(60) # Scan every minute

if __name__ == "__main__":
    node = AutoCorrectorNode(root_dir)
    asyncio.run(node.run_healing_cycle())

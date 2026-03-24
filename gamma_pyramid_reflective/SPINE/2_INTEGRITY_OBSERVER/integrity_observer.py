import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

class IntegrityObserver:
    """
    Z2 Reflective Observer.
    Bridges Kernel policy violations to the Alpha/Gamma history logs.
    """
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / "violations.json"
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def report_violation(self, event: Dict[str, Any]):
        """
        Archival hook for policy violations.
        Uses a simple lockless append-strategy (load-modify-save) for this milestone.
        """
        print(f"[Z2_OBSERVER] Archiving violation: {event.get('action')} by {event.get('source')}")
        
        try:
            with open(self.log_file, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data.append(event)
                f.seek(0)
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.truncate()
        except Exception as e:
            print(f"[Z2_OBSERVER] CRITICAL: Failed to archive violation! {e}")

if __name__ == "__main__":
    # Self-test / Standalone mode
    obs = IntegrityObserver(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS\gamma_pyramid_reflective\B_Evo_Log")
    obs.report_violation({
        "task_id": "test-id",
        "action": "standalone_test",
        "error": "Observer initialization check",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "Z2_OBSERVER_INIT",
        "target": "SYSTEM",
        "origin_z": 2
    })

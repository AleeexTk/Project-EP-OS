import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict

class TimelineManager:
    """
    The 'Radar' of EvoPyramid OS.
    Records every 4D Flight Slot into project_timeline.ndjson.
    """
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    _TIMELINE_FILE = _PROJECT_ROOT / "gamma_pyramid_reflective" / "B_Evo_Log" / "project_timeline.ndjson"

    @classmethod
    def log_event(cls, envelope_data: Dict[str, Any]):
        """Appends a 6-factor contract event to the timeline."""
        try:
            os.makedirs(cls._TIMELINE_FILE.parent, exist_ok=True)
            
            # Extract the 6 factors for the timeline
            event = {
                "t": envelope_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "slot": envelope_data.get("slot_id", "UNSCHEDULED"),
                "mod": envelope_data.get("source_node", "UNKNOWN"),
                "loc": f"Z{envelope_data.get('origin_z', '?')}:{envelope_data.get('location_sector', 'GENERIC')}",
                "act": envelope_data.get("action", "IDLE"),
                "st": envelope_data.get("status", "UNKNOWN"),
                "nxt": envelope_data.get("next_action_slot")
            }

            with open(cls._TIMELINE_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
                
        except Exception as e:
            print(f"[TIMELINE_MANAGER] Failed to log event: {e}")

    @classmethod
    def get_recent_history(cls, limit: int = 100):
        """Reads the last N events from the timeline."""
        events = []
        if not cls._TIMELINE_FILE.exists():
            return events
            
        try:
            with open(cls._TIMELINE_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    events.append(json.loads(line))
        except Exception as e:
            print(f"[TIMELINE_MANAGER] Failed to read history: {e}")
            
        return events

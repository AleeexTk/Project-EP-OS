import sys
from pathlib import Path
import json

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from beta_pyramid_functional.B1_Kernel.timeline import TimelineManager

def test_timeline_and_guard():
    print("--- Starting TRP Hardening Test ---")
    
    envelope = {
        "task_id": "TEST-TASK-001",
        "source_node": "Z17_GLOBAL_NEXUS",
        "origin_z": 17,
        "metadata": {"via": "ZBUS_BRIDGE"}
    }
    
    # 1. Request slot (should be GRANTED)
    success, slot_id, msg = TimelineManager.request_slot(envelope)
    print(f"Request 1: {success}, {slot_id}, {msg}")
    assert success is True
    assert slot_id.startswith("SLOT-")
    
    # 2. Request slot for SAME bridge (should be DENIED)
    success2, slot_id2, msg2 = TimelineManager.request_slot(envelope)
    print(f"Request 2 (Same Bridge): {success2}, {msg2}")
    assert success2 is False
    assert "saturated" in msg2
    
    # 3. Log an event
    TimelineManager.log_event(envelope, "TEST_ACTION", "RUNNING", "Verifying local and global logs", "COMPLETE")
    
    # 4. Check Global Timeline
    global_path = PROJECT_ROOT / "timeline" / "project_timeline.ndjson"
    assert global_path.exists()
    with open(global_path, "r") as f:
        lines = f.readlines()
        last_event = json.loads(lines[-1])
        print(f"Global Event: {last_event['action']} - {last_event['status']}")
        assert last_event["id"] == "Z17_GLOBAL_NEXUS"
    
    # 5. Check Local Timeline
    local_path = PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "_17_GLOBAL_NEXUS" / "timeline.ndjson"
    assert local_path.exists()
    with open(local_path, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        print(f"Local Timeline exists at: {local_path}")
    
    # 6. Release slot
    TimelineManager.release_slot(slot_id, "ZBUS_BRIDGE")
    print(f"Slot {slot_id} released.")
    
    # 7. Request again (should be GRANTED now)
    success3, slot_id3, msg3 = TimelineManager.request_slot(envelope)
    print(f"Request 3 (Post-Release): {success3}, {slot_id3}, {msg3}")
    assert success3 is True

    print("--- TRP Hardening Test Passed ---")

if __name__ == "__main__":
    test_timeline_and_guard()

import requests
import uuid
import json
from datetime import datetime, timezone

API_URL = "http://127.0.0.1:8000/kernel/dispatch"

def test_dispatch_violation():
    print("--- Test 1: Z-Level Violation (Z4 -> Z17) ---")
    payload = {
        "task_id": str(uuid.uuid4()),
        "source_node": "observer_z4",
        "target_node": "nexus_z17",
        "action": "manifest_node",
        "origin_z": 4,
        "payload": {
            "id": "renegade_node",
            "title": "Renegade",
            "z_level": 17,
            "sector": "SPINE",
            "coords": {"x": 0, "y": 0, "z": 17},
            "layer_type": "alpha",
            "kind": "module",
            "summary": "Attempted illegal Z17 manifestation"
        }
    }
    try:
        response = requests.post(API_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_dispatch_success():
    print("\n--- Test 2: Valid Dispatch (Z5 -> Z5) ---")
    payload = {
        "task_id": str(uuid.uuid4()),
        "source_node": "agent_z5",
        "target_node": "agent_z5",
        "action": "manifest_node",
        "origin_z": 5,
        "payload": {
            "id": "legit_node",
            "title": "Legit Local Node",
            "z_level": 5,
            "sector": "GREEN",
            "coords": {"x": 10, "y": 10, "z": 5},
            "layer_type": "beta",
            "kind": "module",
            "summary": "Legitimate Z5 manifestation"
        }
    }
    try:
        # Note: manifest_node actually touches filesystem, so this will create a folder
        response = requests.post(API_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure the API server is running before executing this!
    test_dispatch_violation()
    test_dispatch_success()

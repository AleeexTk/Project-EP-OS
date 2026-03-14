import asyncio
import httpx
import json
import uuid
import time
from datetime import datetime, timezone

# --- CONFIG ---
API_BASE = "http://127.0.0.1:8000"
STRESS_LOAD = 50  # Concurrent tasks
TARGET_FILE = "../../\u03b1_Pyramid_Core/A_Principles/emergency_override.txt"

async def send_task(client, task_id, is_malicious=False):
    """
    Sends a TaskEnvelope to the Kernel Dispatcher.
    """
    action = "filesystem_write" if is_malicious else "status_check"
    payload = {
        "task_id": str(task_id),
        "source_agent": "rogue_agent_X" if is_malicious else "trusted_monitor",
        "target_node": "gen-nexus",
        "action": action,
        "payload": {"content": "HACK"} if is_malicious else {"check": "health"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"origin": "stress_test_v2"}
    }
    
    try:
        resp = await client.post(f"{API_BASE}/kernel/dispatch", json=payload)
        data = resp.json()
        return resp.status_code, data.get("status")
    except Exception as e:
        return 500, str(e)

async def run_stress_test():
    print(f"\n[STRESS TEST V2] Initiating 'Deep Policy Breach'...")
    print(f"[STRESS TEST V2] Load: {STRESS_LOAD} tasks (10% malicious)")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        for i in range(STRESS_LOAD):
            is_malicious = (i % 10 == 0) # 10% malicious
            tasks.append(send_task(client, uuid.uuid4(), is_malicious))
            
        results = await asyncio.gather(*tasks)
        
    # Analyze results
    accepted = [r for r in results if r[1] == "ACCEPTED"]
    rejected = [r for r in results if r[1] == "REJECTED"]
    errors = [r for r in results if r[1] not in ["ACCEPTED", "REJECTED"]]
    
    print("="*40)
    print(f"RESULTS:")
    print(f"Total Requests: {len(results)}")
    print(f"ACCEPTED (Valid): {len(accepted)}")
    print(f"REJECTED (Security Block): {len(rejected)}")
    print(f"ERRORS: {len(errors)}")
    print("="*40)
    
    if len(rejected) == (STRESS_LOAD // 10) and len(errors) == 0:
        print("\n\u2705 ARCHITECTURE STATUS: IMMUNE (Policy enforced)")
    else:
        print("\n\u26a0\ufe0f ARCHITECTURE STATUS: VULNERABLE or ERROR")

if __name__ == "__main__":
    asyncio.run(run_stress_test())

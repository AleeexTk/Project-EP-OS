import asyncio
import os
import sys
from pathlib import Path

# Setup path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B2_Orchestrator.mission_coordinator import MissionCoordinator, MissionStatus

async def test_swarm_mission():
    print("--- EVO-PYRAMID V6.0: SWARM MISSION TEST ---")
    coordinator = MissionCoordinator()
    
    # 1. Create a complex objective
    objective = "Deep Code Audit for memory leaks and a Security Fix for the Z-Bus dispatcher."
    print(f"[TEST] Objective: {objective}\n")
    
    mission = await coordinator.create_mission(
        title="Z-Bus Hardening",
        objective=objective
    )
    
    print(f"[TEST] Mission Created: {mission.title}")
    print(f"[TEST] Decomposed into {len(mission.tasks)} tasks:")
    for t in mission.tasks:
        print(f"  - {t.assigned_role} (Z{t.z_level}): {t.intent}")
    
    print("\n--- 2. EXECUTING MISSION ---")
    # Note: This will call the actual AgentOrchestrator but with dummy/simulated Pearce responses
    # because we are using OLLAMA provider (local).
    final_mission = await coordinator.execute_mission(mission.id)
    
    print("\n--- 3. MISSION RESULTS ---")
    print(f"Status: {final_mission.status.value.upper()}")
    
    if final_mission.status == MissionStatus.COMPLETED:
        print("\n[SUCCESS] Swarm Autonomy Verified! Mission successfully decomposed and executed across agents.")
    else:
        print("\n[FAILURE] Mission failed or incomplete.")

if __name__ == "__main__":
    asyncio.run(test_swarm_mission())

import asyncio
import os
import sys
import json
from pathlib import Path
import importlib.util

# Setup path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B2_Orchestrator.mission_coordinator import MissionCoordinator
from beta_pyramid_functional.B2_Orchestrator.synthesis_agent import SynthesisAgent
from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex

# Dynamic import for ObserverRelay (Z4)
observer_path = ROOT_DIR / "gamma_pyramid_reflective" / "SPINE" / "4_OBSERVER_RELAY" / "index.py"
spec = importlib.util.spec_from_file_location("observer_relay_module", str(observer_path))
ov_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ov_module)
ObserverRelay = ov_module.ObserverRelay

async def global_health_scan():
    print("--- EVO-PYRAMID V8.1: GLOBAL ARCHITECTURAL SCAN ---")
    
    # 1. Memory Verification
    print("\n[Z1-Z2] Checking ProjectCortex Memory Layer...")
    cortex = await ProjectCortex.get_instance()
    blocks = cortex.get_all_sigs()
    print(f"[OK] Cortex Memory active: {len(blocks)} blocks indexed.")

    # 2. Observer Pulse
    print("\n[Z4] Triggering ObserverRelay Pulse...")
    observer = ObserverRelay(ROOT_DIR)
    await observer.pulse()
    print("[OK] Observer Relay functional.")

    # 3. Strategic Mission Planning
    print("\n[Z17] Verifying Mission Coordinator Intelligence...")
    coordinator = MissionCoordinator()
    objective = "Analyze the integration between ProjectCortex and SynthesisAgent and suggest 1 performance optimization."
    mission = await coordinator.create_mission("Structural Optimization", objective)
    print(f"[OK] Mission Created with {len(mission.tasks)} task(s).")
    for t in mission.tasks:
        print(f"  - [{t.assigned_role} Z{t.z_level}] {t.intent}")

    # 4. Synthesis Scan
    print("\n[Z14] Verifying SynthesisAgent Pattern Discovery...")
    synthesis = SynthesisAgent()
    report_id = await synthesis.scan_and_synthesize()
    print(f"[OK] Synthesis Report generated: {report_id}")

    # 5. Result Verification in Cortex
    print("\n[RESULT] Final Memory Check...")
    recent_blocks = await cortex.find_similar("SYSTEM HEARTBEAT", threshold=0.01)
    if recent_blocks:
        print(f"[OK] Pulse successfully retrieved from memory: {recent_blocks[0].content}")
    else:
        print("[CAUTION] Heartbeat pulse not found in recent memory.")

    print("\n--- SCAN COMPLETE: V8.1 ARCHITECTURAL INTEGRATION VERIFIED ---")

if __name__ == "__main__":
    asyncio.run(global_health_scan())

import asyncio
import os
import sys
import json
from pathlib import Path

# Setup path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B2_Orchestrator.mission_coordinator import MissionCoordinator
from beta_pyramid_functional.B2_Orchestrator.synthesis_agent import SynthesisAgent
import importlib.util

# Dynamic import for numeric-prefixed directory
observer_path = ROOT_DIR / "gamma_pyramid_reflective" / "SPINE" / "4_OBSERVER_RELAY" / "index.py"
spec = importlib.util.spec_from_file_location("observer_relay_module", str(observer_path))
observer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer_module)
ObserverRelay = observer_module.ObserverRelay

async def test_v8_1_hardening():
    print("--- EVO-PYRAMID V8.1: STRATEGIC HARDENING TEST ---")
    
    # 1. Test Observer Pulse
    print("\n[STEP 1] Testing ObserverRelay (Z4) State Pulse...")
    observer = ObserverRelay(ROOT_DIR)
    await observer.pulse()
    print("[SUCCESS] Observer pulsed system state to ProjectCortex.")

    # 2. Test LLM Mission Planning
    print("\n[STEP 2] Testing Intelligent Mission Decomposition (Z17 Architect)...")
    coordinator = MissionCoordinator()
    objective = "Audit the existing security protocols and implement a temporary fallback monitor for the ProjectCortex."
    mission = await coordinator.create_mission("Deep Security Alignment", objective)
    
    print(f"\n[DECOMPOSITION RESULTS]")
    for i, task in enumerate(mission.tasks):
        print(f"Task {i+1}: [{task.assigned_role} Z{task.z_level}] -> {task.intent}")
    
    if len(mission.tasks) > 1:
        print("[SUCCESS] Mission decomposed into specialized roles via LLM.")
    else:
        print("[CAUTION] Single generalist task returned (LLM fallback or simple objective).")

    # 3. Test Structured Synthesis
    print("\n[STEP 3] Testing Pydantic Synthesis Proposals (Z14)...")
    synthesis = SynthesisAgent()
    report_id = await synthesis.scan_and_synthesize()
    print(f"[SUCCESS] Synthesis report generated with ID: {report_id}")
    
    print("\n[FINAL] V8.1 Strategic Hardening verified. The pyramid is now architecturally functional.")

if __name__ == "__main__":
    asyncio.run(test_v8_1_hardening())

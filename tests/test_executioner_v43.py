import sys
import os
import json
import asyncio
import unittest
import shutil
from pathlib import Path

os.chdir(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS")
sys.path.append(str(Path("gamma_pyramid_reflective/A_Pulse")))
sys.path.append(str(Path("beta_pyramid_functional/B2_Orchestrator")))

from pulser import PulserEngine

class TestExecutioner(unittest.IsolatedAsyncioTestCase):
    async def test_garbage_collection(self):
        print("\n[TEST] V4.3 Executioner / Garbage Collector Test...")
        
        # 1. Setup mock state with a locked node
        rogue_id = "test_rogue_node_v43"
        class NodeMock:
            def __init__(self):
                self.state = "locked"
                self.title = "Test Rogue"
        
        class MockState:
            def __init__(self):
                self.nodes = {rogue_id: NodeMock()}
            def model_dump(self): return {}

        class MockManager:
            async def broadcast(self, msg): pass

        state_mock = MockState()
        pulser = PulserEngine(state_mock, MockManager(), lambda x: None)
        
        # 2. Setup a physical folder to be deleted
        sandbox_dir = Path("beta_pyramid_functional/SANDBOX/5_test_rogue_node")
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = sandbox_dir / ".node_manifest.json"
        
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({"id": rogue_id}, f)
            
        print(f"[TEST] Created dummy node folder: {sandbox_dir}")
        self.assertTrue(sandbox_dir.exists())
        self.assertIn(rogue_id, state_mock.nodes)
        
        # 3. Trigger one pulse of self_heal_pulse
        pulser.is_running = True
        
        # We'll run it as a task and cancel it after a short delay since it's an infinite loop
        task = asyncio.create_task(pulser.self_heal_pulse())
        await asyncio.sleep(1.0)  # Give it time to execute the first loop
        pulser.is_running = False
        task.cancel()
        
        # Ignore CancelledError
        try:
            await task
        except asyncio.CancelledError:
            pass

        # 4. Verification
        print(f"[TEST] Checking if executioner worked...")
        self.assertFalse(sandbox_dir.exists(), "Executioner failed to delete the physical folder.")
        self.assertNotIn(rogue_id, state_mock.nodes, "Executioner failed to remove node from state matrix.")
        print("[TEST] SUCCESS: Executioner purged the rogue node physically and logically.")

if __name__ == "__main__":
    unittest.main()

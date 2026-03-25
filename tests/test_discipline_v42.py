import sys
import os
import json
import unittest
from pathlib import Path
from datetime import datetime, timezone

# Add paths to sys.path for imports
os.chdir(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS")
sys.path.append(str(Path("beta_pyramid_functional/B1_Kernel")))
sys.path.append(str(Path("gamma_pyramid_reflective/SPINE/2_INTEGRITY_OBSERVER")))
sys.path.append(str(Path("gamma_pyramid_reflective/A_Pulse")))

from policy_manager import SystemPolicyManager, SystemPolicy
from contracts import TaskEnvelope, TaskStatus
from integrity_observer import IntegrityObserver
from pulser import PulserEngine

class TestDiscipline(unittest.TestCase):
    def setUp(self):
        self.log_dir = Path(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS\gamma_pyramid_reflective\B_Evo_Log")
        self.violation_file = self.log_dir / "violations.json"
        
        # Clear previous logs if they exist for clean test
        if self.violation_file.exists():
            with open(self.violation_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def test_quarantine_enforcement(self):
        print("\n[TEST] V4.2 Automated Discipline Test...")
        
        # 1. Setup Kernel and Observer
        pm = SystemPolicyManager()
        obs = IntegrityObserver(str(self.log_dir))
        pm.register_reporter(obs.report_violation)
        
        # 2. Simulate a Rogue Node committing 3 violations
        rogue_id = "rogue_agent_z5"
        for i in range(3):
            envelope = TaskEnvelope(
                source_node=rogue_id,
                target_node="system",
                action="manifest_node", # Restricted action across big Z gap
                origin_z=5,
                payload={"z_level": 15}
            )
            is_valid = pm.validate_action(envelope)
            self.assertFalse(is_valid)
            
        print(f"[TEST] Rogue node '{rogue_id}' committed 3 violations.")
        
        # 3. Trigger Pulse Compliance Check
        class NodeMock:
            def __init__(self):
                self.state = "idle"
                self.metadata = {}

        class MockState:
            def __init__(self):
                self.nodes = {rogue_id: NodeMock()}
            def model_dump(self): return {}

        class MockManager:
            async def broadcast(self, msg): pass

        state_mock = MockState()
        pulser = PulserEngine(state_mock, MockManager(), lambda x: None)
        
        # This will read violations.json and should enforce quarantine (node state -> locked)
        pulser._calculate_compliance()
        
        print(f"[TEST] Node state after Pulse: {state_mock.nodes[rogue_id].state}")
        self.assertEqual(state_mock.nodes[rogue_id].state, "locked", "Pulse should have marked node as 'locked'")
        self.assertTrue(state_mock.nodes[rogue_id].metadata.get("quarantined"), "Metadata should reflect quarantine")

        # 4. Integrate Quarantine with Kernel (Simulating the feedback loop)
        # In a real run, this would be an API call back to the kernel. 
        # For the test, we trigger the API equivalent manually:
        pm.quarantine_node(rogue_id)
        
        # 5. Verify the node is now fully blocked, even for a legal action
        legal_envelope = TaskEnvelope(
            source_node=rogue_id,
            target_node="another_z5",
            action="read_data", # Normally allowed
            origin_z=5,
            payload={}
        )
        
        print(f"[TEST] Rogue node '{rogue_id}' attempting legal action...")
        is_legal_valid = pm.validate_action(legal_envelope)
        
        self.assertFalse(is_legal_valid, "Kernel should block ALL actions from a quarantined node.")
        self.assertEqual(legal_envelope.metadata["error"], f"QuarantineViolation: Node '{rogue_id}' is in quarantine and cannot perform actions.")
        print("[TEST] Action successfully blocked by Quarantine Manager.")

if __name__ == "__main__":
    unittest.main()

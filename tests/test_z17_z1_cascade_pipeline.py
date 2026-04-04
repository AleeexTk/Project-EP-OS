import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Handle SPINE modules using proper package imports
try:
    import alpha_pyramid_core.SPINE._13_AUTO_CORRECTOR.z13_policy_corrector as z13_policy_corrector
except ImportError:
    z13_policy_corrector = None

from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope
from beta_pyramid_functional.B1_Kernel.z_cascade import ZCascadePipeline
import z13_policy_corrector


class _FakeMemoryBridge:
    async def recall_healing_pattern(self, error_signature: str):
        return None

    async def store_decision(self, topic: str, outcome: str, z_level: int = 0, tags=None):
        return {"id": "mem_test_002"}


class TestZ17Z1CascadePipeline(unittest.TestCase):
    def _envelope(self, semantic_loss: bool = False):
        return TaskEnvelope(
            task_id="z17_z1_pipeline_001",
            source_node="gen-nexus",
            target_node="execution_z1",
            action="manifest_node",
            origin_z=17,
            signature="TSIG:gen-nexus:z17_z1_pipeline_001",
            slot_id="slot_cascade_001",
            intent="Preserve canonical meaning through full pyramid descent",
            payload={
                "z_level": 16,
                "synthesis_proposal": "distorted proposal",
                "simulate_semantic_loss": semantic_loss,
            },
            timestamp=datetime.now(timezone.utc),
        )

    def test_pipeline_passes_all_pairs(self):
        report = ZCascadePipeline.run_z17_to_z1(self._envelope(semantic_loss=False))

        self.assertEqual(report["status"], "passed")
        self.assertEqual(len(report["pairs"]), 16)
        self.assertEqual(report["stopped_at"], None)
        self.assertEqual(report["repair_count"], 0)
        self.assertEqual(report["pairs"][0]["pair_id"], "Z17->Z16")
        self.assertEqual(report["pairs"][-1]["pair_id"], "Z2->Z1")

    def test_pipeline_uses_z14_repair_path(self):
        class _P:
            value = "claude"

        fake_bridge = _FakeMemoryBridge()

        async def _fake_get_instance():
            return fake_bridge

        with patch.object(z13_policy_corrector.ProviderMatrix, "get_best_available", return_value=_P()), \
             patch.object(z13_policy_corrector.Z13PolicyCorrector, "_rewrite_with_provider", return_value="Repaired canonical proposal"), \
             patch.object(z13_policy_corrector.RepairJournal, "record_repair", return_value=None), \
             patch("beta_pyramid_functional.B4_Cognitive.cognitive_bridge.CognitiveBridge.get_instance", side_effect=_fake_get_instance):

            report = ZCascadePipeline.run_z17_to_z1(self._envelope(semantic_loss=True))

        self.assertEqual(report["status"], "passed")
        self.assertEqual(len(report["pairs"]), 16)
        self.assertGreater(report["repair_count"], 0)
        self.assertTrue(any(p["repaired"] for p in report["pairs"]))


if __name__ == "__main__":
    unittest.main()

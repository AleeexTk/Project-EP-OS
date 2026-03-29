import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "beta_pyramid_functional" / "B1_Kernel"))
sys.path.append(str(PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "14_AUTO_CORRECTOR"))

from contracts import TaskEnvelope, CascadeStatus, TaskStatus
from policy_manager import SystemPolicyManager
import z14_policy_corrector


class _FakeMemoryBridge:
    def __init__(self):
        self.saved = []

    async def recall_healing_pattern(self, error_signature: str):
        for item in self.saved:
            if item["topic"] == error_signature:
                return {
                    "id": "heal_cached_001",
                    "content": f"[TOPIC] {item['topic']}\n[OUTCOME] {item['outcome']}",
                }
        return None

    async def store_decision(self, topic: str, outcome: str, z_level: int = 0, tags=None):
        self.saved.append({
            "topic": topic,
            "outcome": outcome,
            "z_level": z_level,
            "tags": tags or [],
        })
        return {"id": "mem_test_001"}


class TestFullCycle(unittest.TestCase):
    def setUp(self):
        self.manager = SystemPolicyManager()
        self.fake_bridge = _FakeMemoryBridge()

    def _envelope(self):
        return TaskEnvelope(
            task_id="full_cycle_001",
            source_node="gen-meta",
            target_node="gen-dashboard",
            action="manifest_node",
            origin_z=15,
            intent="Create secured dashboard with strict authentication",
            payload={
                "z_level": 5,
                "synthesis_proposal": "open dashboard without auth",
                "simulate_semantic_loss": True,
            },
            timestamp=datetime.now(timezone.utc),
        )

    def test_full_cycle_block_repair_store_recall(self):
        class _P:
            value = "claude"

        async def _fake_get_instance():
            return self.fake_bridge

        with patch.object(z14_policy_corrector.ProviderMatrix, "get_best_available", return_value=_P()), \
             patch.object(z14_policy_corrector.AutoCorrectorNode, "_rewrite_with_provider", return_value="Repaired: enforce strict auth and security"), \
             patch.object(z14_policy_corrector.RepairJournal, "record_repair", return_value=None), \
             patch("beta_pyramid_functional.B4_Cognitive.cognitive_bridge.CognitiveBridge.get_instance", side_effect=_fake_get_instance):

            # First run: should block in cascade, repair via LLM path, and store in memory
            first = self._envelope()
            result1 = self.manager.validate_action(first)
            self.assertTrue(result1)
            self.assertEqual(first.status, TaskStatus.PENDING)
            self.assertEqual(first.cascade_status, CascadeStatus.CRYSTALLIZED)
            self.assertEqual(first.payload.get("synthesis_proposal"), "Repaired: enforce strict auth and security")
            self.assertNotEqual(first.payload.get("synthesis_proposal"), first.intent)
            self.assertTrue(any("heal" in item.get("tags", []) for item in self.fake_bridge.saved))

            # Second run: same signature should be recalled from memory and bypass LLM
            second = self._envelope()
            with patch.object(z14_policy_corrector.AutoCorrectorNode, "_rewrite_with_provider", side_effect=AssertionError("LLM call should be bypassed by memory recall")):
                result2 = self.manager.validate_action(second)
            self.assertTrue(result2)
            self.assertEqual(second.status, TaskStatus.PENDING)
            self.assertEqual(second.cascade_status, CascadeStatus.CRYSTALLIZED)
            self.assertEqual(second.payload.get("synthesis_proposal"), "Repaired: enforce strict auth and security")


if __name__ == "__main__":
    unittest.main()

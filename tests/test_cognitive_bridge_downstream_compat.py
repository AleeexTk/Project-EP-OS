import json
from types import SimpleNamespace

import pytest

from beta_pyramid_functional.B2_Orchestrator.auto_corrector import AutoCorrector
from beta_pyramid_functional.B2_Orchestrator.synthesis_agent import ProposalType
from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge
from beta_pyramid_functional.A_Agents.pear_protocol import PEARAgent


@pytest.mark.asyncio
async def test_auto_corrector_recall_contract_without_content_tags(monkeypatch):
    proposal_payload = {
        "type": "patch",
        "target_node": "module.py",
        "rationale": "from memory",
        "suggested_action": "apply patch",
        "confidence": 0.91,
        "impact": "low",
    }

    class FakeBridge:
        async def recall_healing_pattern(self, _sig):
            return {"id": "heal_1", "content": f"[TOPIC] sig\n[OUTCOME] {json.dumps(proposal_payload)}"}

        async def retrieve_session_context(self, *_args, **_kwargs):
            return []

    async def fake_get_instance():
        return FakeBridge()

    monkeypatch.setattr(CognitiveBridge, "get_instance", fake_get_instance)

    ac = AutoCorrector()
    error_text = 'Traceback\n  File "/tmp/module.py", line 11, in run\nValueError: boom'
    proposal = await ac.propose_fix(error_text)

    assert proposal is not None
    assert proposal.type == ProposalType.PATCH
    assert proposal.rationale.startswith("[MEMORY BYPASS")


@pytest.mark.asyncio
async def test_pear_perceive_handles_bridge_blocks_without_to_dict(monkeypatch):
    class FakeMemory:
        async def find_similar(self, _intent):
            return []

    class FakeBridge:
        async def retrieve_session_context(self, _intent, top_k=3):
            return [SimpleNamespace(content="bridge block content")]

    class FakeProject:
        async def find_similar(self, _intent):
            return [SimpleNamespace(content="global block content")]

    async def fake_bridge_get_instance():
        return FakeBridge()

    async def fake_project_get_instance():
        return FakeProject()

    from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex

    monkeypatch.setattr(CognitiveBridge, "get_instance", fake_bridge_get_instance)
    monkeypatch.setattr(ProjectCortex, "get_instance", fake_project_get_instance)

    agent = PEARAgent.__new__(PEARAgent)
    agent.role = "Architect"
    agent.z_level = 17
    agent.memory = FakeMemory()
    agent.provider = "ollama"
    agent.color = None

    perceived = await agent.perceive({"intent": "test intent", "pulse_id": "p1"})
    assert perceived["session_context"][0]["content"] == "bridge block content"
    assert perceived["global_context"][0]["content"] == "global block content"


@pytest.mark.asyncio
async def test_health_summary_contract_for_api_metrics():
    nodes = {
        "n1": SimpleNamespace(id="n1", block_id="b1", metadata={"tags": ["session_memory", "heal"]}),
        "n2": SimpleNamespace(id="n2", block_id="b2", metadata={"tags": ["session_memory"]}),
    }
    fake_cortex = SimpleNamespace(
        hypergraph=SimpleNamespace(nodes=nodes),
        persistence=SimpleNamespace(load_block=lambda _bid: SimpleNamespace(content="x")),
    )
    bridge = CognitiveBridge(fake_cortex)

    stats = await bridge.health_summary()
    assert stats["total_blocks"] == 2
    assert stats["session_memory_blocks"] == 2
    assert stats["heal_blocks"] == 1

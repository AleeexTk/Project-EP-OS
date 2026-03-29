from types import SimpleNamespace

import pytest

from beta_pyramid_functional.B2_Orchestrator.synthesis_agent import SynthesisAgent
from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex


@pytest.mark.asyncio
async def test_scan_uses_hypergraph_signatures(tmp_path, monkeypatch):
    class FakeHypergraph:
        nodes = {
            "a": SimpleNamespace(minhash_sig=[1, 2, 3]),
            "b": SimpleNamespace(minhash_sig=[1, 2, 3]),
            "c": SimpleNamespace(minhash_sig=[]),
        }

    fake_cortex = SimpleNamespace(hypergraph=FakeHypergraph())

    async def fake_get_instance():
        return fake_cortex

    monkeypatch.setattr(ProjectCortex, "get_instance", fake_get_instance)

    agent = SynthesisAgent(report_dir=str(tmp_path))
    report_id = await agent.scan_and_synthesize()

    assert report_id.startswith("syn_")
    report_file = tmp_path / f"{report_id}.json"
    assert report_file.exists()

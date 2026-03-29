import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge


def test_healing_cache_persistence_roundtrip(tmp_path: Path):
    cache_file = tmp_path / "healing_cache.json"
    original_cache_file = CognitiveBridge._cache_file
    original_cache_loaded = CognitiveBridge._cache_loaded
    original_cache_data = dict(CognitiveBridge._healing_cache)

    try:
        CognitiveBridge._cache_file = cache_file
        CognitiveBridge._cache_loaded = False
        CognitiveBridge._healing_cache = {}

        CognitiveBridge._healing_cache["error|intent"] = "repaired outcome"
        CognitiveBridge._save_healing_cache()

        CognitiveBridge._cache_loaded = False
        CognitiveBridge._healing_cache = {}
        CognitiveBridge._load_healing_cache()

        assert CognitiveBridge._healing_cache["error|intent"] == "repaired outcome"
        assert json.loads(cache_file.read_text(encoding="utf-8"))["error|intent"] == "repaired outcome"
    finally:
        CognitiveBridge._cache_file = original_cache_file
        CognitiveBridge._cache_loaded = original_cache_loaded
        CognitiveBridge._healing_cache = original_cache_data


@pytest.mark.asyncio
async def test_recall_lazy_loads_persisted_cache(tmp_path: Path):
    cache_file = tmp_path / "healing_cache.json"
    cache_file.write_text(json.dumps({"sig|intent": "healed"}, ensure_ascii=False), encoding="utf-8")

    original_cache_file = CognitiveBridge._cache_file
    original_cache_loaded = CognitiveBridge._cache_loaded
    original_cache_data = dict(CognitiveBridge._healing_cache)

    try:
        CognitiveBridge._cache_file = cache_file
        CognitiveBridge._cache_loaded = False
        CognitiveBridge._healing_cache = {}

        bridge = CognitiveBridge(SimpleNamespace())
        recalled = await bridge.recall_healing_pattern("sig|intent")

        assert recalled is not None
        assert "[OUTCOME] healed" in recalled["content"]
        assert CognitiveBridge._cache_loaded is True
    finally:
        CognitiveBridge._cache_file = original_cache_file
        CognitiveBridge._cache_loaded = original_cache_loaded
        CognitiveBridge._healing_cache = original_cache_data


@pytest.mark.asyncio
async def test_store_decision_does_not_use_tags_in_content():
    class FakePersistence:
        def __init__(self):
            self.saved = []

        def save_block(self, block):
            self.saved.append(block)

    class FakeHypergraph:
        def __init__(self):
            self.added = []

        async def add_node(self, node, block):
            self.added.append((node, block))

    fake_cortex = SimpleNamespace(persistence=FakePersistence(), hypergraph=FakeHypergraph())
    bridge = CognitiveBridge(fake_cortex)
    block = await bridge.store_decision("topic", "outcome", z_level=14, tags=["heal"])

    assert "[TAGS]" not in block.content
    assert block.content.startswith("[TOPIC]")
    assert fake_cortex.hypergraph.added

import json
from pathlib import Path

from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge


def test_healing_cache_persistence_roundtrip(tmp_path: Path):
    cache_file = tmp_path / "healing_cache.json"
    old_cache_file = CognitiveBridge._cache_file
    old_cache_loaded = CognitiveBridge._cache_loaded
    old_healing_cache = dict(CognitiveBridge._healing_cache)

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
        CognitiveBridge._cache_file = old_cache_file
        CognitiveBridge._cache_loaded = old_cache_loaded
        CognitiveBridge._healing_cache = old_healing_cache

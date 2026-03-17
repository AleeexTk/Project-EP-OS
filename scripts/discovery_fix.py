import sys
import json
import re
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple

# Environment
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from alpha_pyramid_core.B_Structure.models import PyramidState, Node, NodeState

STATE_FILE = ROOT_DIR / "state" / "pyramid_state.json"
SCAN_SECTORS = {"SPINE", "PURPLE", "RED", "GOLD", "GREEN", "SANDBOX"}

def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value or "").strip()).strip("_")
    return slug.lower()

def _safe_int(value: Any, default: int) -> int:
    try: return int(value)
    except: return default

def _load_manifest(manifest_path: Path) -> Dict[str, Any]:
    try:
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
    except: pass
    return {}

def discover_nodes():
    layers = [d for d in ROOT_DIR.glob("*pyramid*") if d.is_dir()]
    discovered = {}
    
    for layer in layers:
        for sector_dir in layer.iterdir():
            if not sector_dir.is_dir() or sector_dir.name.upper() not in SCAN_SECTORS: continue
            # Also scan the layer root for special modules if needed, but per-standard they are in sectors
            for node_dir in sector_dir.iterdir():
                if not node_dir.is_dir() or node_dir.name.startswith("__"): continue
                
                manifest = _load_manifest(node_dir / ".node_manifest.json")
                parsed = re.match(r"^(?P<z>\d+)_([A-Za-z0-9_-]+)$", node_dir.name)
                parsed_z = _safe_int(parsed.group("z"), 9) if parsed else 9
                parsed_name = parsed.group(2) if parsed else node_dir.name

                node_id = _safe_slug(manifest.get("id") or parsed_name)
                if not node_id: continue

                z_level = _safe_int(manifest.get("z_level") or manifest.get("coords", {}).get("z"), parsed_z)
                
                node = Node(
                    id=node_id,
                    title=str(manifest.get("title") or parsed_name.replace("_", " ")).strip() or node_id,
                    z_level=z_level,
                    sector=sector_dir.name.upper(),
                    coords={
                        "x": _safe_int(manifest.get("coords", {}).get("x"), 9),
                        "y": _safe_int(manifest.get("coords", {}).get("y"), 9),
                        "z": _safe_int(manifest.get("coords", {}).get("z"), z_level),
                    },
                    layer_type=str(manifest.get("layer_type") or "beta").lower(),
                    kind=str(manifest.get("kind") or "module").lower(),
                    summary=str(manifest.get("summary") or f"Discovered: {node_dir.name}"),
                    state=str(manifest.get("state") or NodeState.ACTIVE.value),
                    links=[str(l) for l in manifest.get("links", []) if str(l).strip()],
                    metadata={
                        "source": "filesystem-discovery",
                        "path": str(node_dir.relative_to(ROOT_DIR)).replace("\\", "/"),
                        "layer_folder": layer.name,
                    }
                )
                discovered[node.id] = node

    # Special check for B1_Kernel/SK_Engine which is deep inside Functional but should be a node
    sk_path = ROOT_DIR / "beta_pyramid_functional" / "B1_Kernel" / "SK_Engine"
    if sk_path.exists():
        manifest = _load_manifest(sk_path / ".node_manifest.json")
        node = Node(
            id="sk_engine",
            title="SK Cognitive Engine",
            z_level=7,
            sector="GOLD",
            coords={"x": 10, "y": 7, "z": 7},
            layer_type="beta",
            kind="memory",
            summary="Associative memory, MinHash indexing and LSH similarity search.",
            state="active",
            links=manifest.get("links", []),
            metadata={"path": "beta_pyramid_functional/B1_Kernel/SK_Engine"}
        )
        discovered[node.id] = node

    return discovered

def run():
    print("Starting manual discovery sync...")
    nodes = discover_nodes()
    
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            state = PyramidState(**data)
    else:
        state = PyramidState()

    added = 0
    for node_id, node in nodes.items():
        if node_id not in state.nodes:
            state.nodes[node_id] = node
            print(f"  + Added: {node_id}")
            added += 1
        else:
            # Update existing to match manifest
            state.nodes[node_id] = node

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state.model_dump(), f, indent=2)
    
    print(f"Sync complete. Added {added} new nodes. Total nodes: {len(state.nodes)}")

if __name__ == "__main__":
    run()

import json
import os
import shutil
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS")
PYRAMID_DIRS = ["alpha_pyramid_core", "beta_pyramid_functional", "gamma_pyramid_reflective"]

def load_state():
    state_file = ROOT_DIR / "state" / "pyramid_state.json"
    if not state_file.exists():
        return {}
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f).get("nodes", {})

def scan_for_orphans_and_duplicates():
    active_nodes = load_state()
    # Find all path references from state
    valid_paths = set()
    for node_id, node_data in active_nodes.items():
        if "metadata" in node_data and "path" in node_data["metadata"]:
            valid_paths.add(str(ROOT_DIR / node_data["metadata"]["path"]).lower())
            
    orphans = []
    duplicates = []
    
    # Track which node IDs we've seen on disk
    seen_ids = {}

    for layer in PYRAMID_DIRS:
        layer_dir = ROOT_DIR / layer
        if not layer_dir.exists(): continue
        
        for sector_dir in layer_dir.iterdir():
            if not sector_dir.is_dir(): continue
            
            for node_dir in sector_dir.iterdir():
                if not node_dir.is_dir() or node_dir.name in ["__pycache__"]: continue
                
                # Check if it's a node
                manifest_path = node_dir / ".node_manifest.json"
                is_node = (node_dir / "index.py").exists() or manifest_path.exists()
                
                if not is_node:
                    continue
                
                node_id = None
                if manifest_path.exists():
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            node_id = json.load(f).get("id")
                    except: pass
                
                if not node_id:
                    # Guess from folder name
                    parts = node_dir.name.split("_", 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        node_id = parts[1].lower()
                    else:
                        node_id = node_dir.name.lower()

                # Rule 1: Not in state json -> Orphan
                # Wait, some nodes might have id that doesn't match perfectly. Let's do a loose matching.
                str_path = str(node_dir).lower()
                is_valid = False
                for vp in valid_paths:
                    if str_path == vp or str_path.startswith(vp):
                        is_valid = True
                        break
                        
                # Also check by node_id in active_nodes
                if node_id in active_nodes:
                    is_valid = True
                    
                if not is_valid:
                    orphans.append(str(node_dir))
                    continue
                    
                # Rule 2: Duplicate IDs (Multiple folders claiming same ID)
                if node_id in seen_ids:
                    duplicates.append((seen_ids[node_id], str(node_dir)))
                else:
                    seen_ids[node_id] = str(node_dir)
                    
    return orphans, duplicates

if __name__ == "__main__":
    o, d = scan_for_orphans_and_duplicates()
    print("=== ORPHANS (Folder exists but no active node in state) ===")
    for x in o: print(f" - {x}")
    print("\n=== DUPLICATES (Multiple folders for same node ID) ===")
    for a, b in d: print(f" - {a} <--> {b}")

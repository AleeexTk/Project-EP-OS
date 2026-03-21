import json
import re
from pathlib import Path

evo_code = Path(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS\evopyramid-v2\src\lib\evo.ts").read_text(encoding='utf-8')
state_file = Path(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS\state\pyramid_state.json")
state = json.loads(state_file.read_text(encoding='utf-8'))

pattern = re.compile(r"addNode\((\d+),\s*(\d+),\s*(\d+),\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*['\"]([^'\"]+)['\"](?:,\s*'([^']+)')?(?:,\s*\[([^\]]*)\])?([^)]*)\);")

new_nodes = {}
for m in pattern.finditer(evo_code):
    z = int(m.group(1))
    x = int(m.group(2))
    y = int(m.group(3))
    sector = m.group(4).upper()
    node_id = m.group(5)
    title = m.group(6)
    layer = m.group(7)
    kind = m.group(8).split("'")[0] # strip extra quotes if any 
    status = m.group(9) if m.group(9) else "idle"
    
    links_str = m.group(10)
    links = []
    if links_str:
        links = [l.strip().strip("'\"") for l in links_str.split(",") if l.strip()]

    extra = m.group(11)
    
    desc_match = re.search(r"description:\s*'([^']+)'", extra) if extra else None
    desc = desc_match.group(1) if desc_match else ""
    
    cap_match = re.search(r"capability:\s*'([^']+)'", extra) if extra else None
    cap = cap_match.group(1) if cap_match else None
    
    new_nodes[node_id] = {
        "id": node_id,
        "title": title,
        "z_level": z,
        "sector": sector,
        "coords": {"x": x, "y": y, "z": z},
        "layer_type": layer,
        "kind": kind,
        "summary": desc,
        "state": status if status != "none" else "idle",
        "canon_status": "runtime",
        "artifacts": [],
        "links": links,
        "children": [],
        "source_refs": [],
        "metadata": {
            "source": "evo.ts mock extraction",
            "capability": cap
        },
        "runtime_canon_flag": "canon",
        "session_url": None,
        "browser_profile_dir": None,
        "orchestrator_state": "unlinked"
    }

print(f"Parsed {len(new_nodes)} nodes from evo.ts")

# Retain existing backend nodes
for node_id, node_data in state.get("nodes", {}).items():
    new_nodes[node_id] = node_data

# Fix chaos_engine
if "chaos_engine" in new_nodes:
    new_nodes["chaos_engine"]["coords"] = {"x": 9, "y": 9, "z": 7}
    new_nodes["chaos_engine"]["sector"] = "SPINE"
    new_nodes["chaos_engine"]["z_level"] = 7
    new_nodes["chaos_engine"]["state"] = "active"

state["nodes"] = new_nodes
state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')
print("Successfully synced pyramid_state.json with backend and frontend nodes.")

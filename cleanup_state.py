import json
from pathlib import Path

STATE_FILE = Path("state/pyramid_state.json")

def cleanup():
    if not STATE_FILE.exists():
        return
        
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        nodes = data.get("nodes", {})

    # IDs to remove
    to_remove = [
        "nexus_router_z16",
        "policy_bus_z14",
        "provider_router_z12",
        "audit_bridge_z2",
        "test_stress_node"
    ]
    
    for rid in to_remove:
        if rid in nodes:
            print(f"Removing {rid}")
            del nodes[rid]
            
    # Also ensure links are consistent (using the new IDs)
    id_map = {
        "nexus_router_z16": "nexus_router",
        "policy_bus_z14": "policy_bus",
        "provider_router_z12": "provider_router",
        "audit_bridge_z2": "audit_bridge"
    }
    
    for node in nodes.values():
        if "links" in node:
            new_links = []
            for link in node["links"]:
                if link in id_map:
                    new_links.append(id_map[link])
                elif link == "test_stress_node":
                    continue
                else:
                    new_links.append(link)
            node["links"] = list(set(new_links))

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup()

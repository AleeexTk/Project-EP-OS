import json
from pathlib import Path

state_path = Path(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS\state\pyramid_state.json")
if state_path.exists():
    with open(state_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    nodes = data.get("nodes", {})
    if "8-9-13" in nodes:
        print(f"Removing phantom node '8-9-13' from state.")
        del nodes["8-9-13"]
        
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("State updated successfully.")
    else:
        print("Node '8-9-13' not found in state.")
else:
    print("State file not found.")

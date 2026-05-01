from .base import BaseNode
from typing import Dict, Any

class Z14ChaosNode(BaseNode):
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Z{self.z_level} - {self.node_id}] CHAOS Validation...")
        
        # Z14 validates the state and applies perturbations or checks
        if context.get("state") == "initialized":
            context["state"] = "validated"
            context["trajectory"].append("Z14_Validation")
            print("  -> State successfully validated.")
        else:
            print("  -> ERROR: Invalid state for Z14.")
            context["error"] = True
            
        return context

def get_node(node_id: str, z_level: int) -> BaseNode:
    return Z14ChaosNode(node_id, z_level)

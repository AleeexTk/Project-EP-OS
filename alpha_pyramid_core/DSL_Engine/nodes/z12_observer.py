from .base import BaseNode
from typing import Dict, Any

class Z12ObserverNode(BaseNode):
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Z{self.z_level} - {self.node_id}] OBSERVER Execution...")
        
        # Z12 acts on the validated state
        if context.get("state") == "validated":
            context["state"] = "executed"
            context["trajectory"].append("Z12_Execution")
            print(f"  -> Execution complete. Final trajectory: {context['trajectory']}")
        else:
            print("  -> ERROR: Cannot execute. State not validated.")
            
        return context

def get_node(node_id: str, z_level: int) -> BaseNode:
    return Z12ObserverNode(node_id, z_level)

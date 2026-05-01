from .base import BaseNode
from typing import Dict, Any

class Z17PearNode(BaseNode):
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Z{self.z_level} - {self.node_id}] PEAR Initiation...")
        
        # In Z17, we initialize the core state if not present
        if "state" not in context:
            context["state"] = "initialized"
            context["trajectory"] = ["Z17_Init"]
        
        print(f"  -> Context state: {context['state']}")
        return context

# The runtime will look for a 'get_node' factory or simply instantiate by class name.
# We export a standard factory function for simplicity.
def get_node(node_id: str, z_level: int) -> BaseNode:
    return Z17PearNode(node_id, z_level)

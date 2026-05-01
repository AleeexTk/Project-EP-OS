import yaml
from typing import Dict, Any

class DSLValidator:
    def __init__(self, filepath: str):
        self.filepath = filepath
        
    def load(self) -> Dict[str, Any]:
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate(self) -> Dict[str, Any]:
        data = self.load()
        
        if "version" not in data:
            raise ValueError("Missing 'version' in DSL.")
            
        if "nodes" not in data or not isinstance(data["nodes"], list):
            raise ValueError("DSL must contain a list of 'nodes'.")
            
        nodes = data["nodes"]
        node_ids = set()
        
        # First pass: collect IDs and check required fields
        for node in nodes:
            for required in ["id", "z_level", "role", "module"]:
                if required not in node:
                    raise ValueError(f"Node is missing required field: '{required}'. Node data: {node}")
            
            node_ids.add(node["id"])
            
            if node["role"] not in ["structural", "bridge", "infra"]:
                raise ValueError(f"Invalid role '{node['role']}' in node {node['id']}")

        # Second pass: check transitions
        for node in nodes:
            next_node = node.get("next")
            if next_node and next_node not in node_ids:
                raise ValueError(f"Node '{node['id']}' points to non-existent next node '{next_node}'.")
                
        print(f"✅ Validation passed. {len(nodes)} nodes found.")
        return data

if __name__ == "__main__":
    validator = DSLValidator("pyramid.yaml")
    validator.validate()

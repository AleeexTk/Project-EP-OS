import importlib
import sys
from pathlib import Path
from validator import DSLValidator

class EPOSRuntime:
    def __init__(self, dsl_path: str):
        self.dsl_path = dsl_path
        self.validator = DSLValidator(dsl_path)
        self.nodes_data = {}
        self.start_node_id = None
        
        # Add the parent directory to sys.path so we can import 'nodes.x'
        current_dir = Path(__file__).parent.resolve()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

    def initialize(self):
        print("🚀 Initializing EP-OS Runtime Engine...")
        data = self.validator.validate()
        
        nodes = data["nodes"]
        if not nodes:
            raise ValueError("No nodes to run.")
            
        self.start_node_id = nodes[0]["id"]
        
        for node in nodes:
            self.nodes_data[node["id"]] = node
            
    def run(self):
        if not self.start_node_id:
            self.initialize()
            
        print("\n=== STARTING EXECUTION CYCLE ===")
        context = {}
        current_id = self.start_node_id
        
        while current_id:
            node_data = self.nodes_data[current_id]
            module_name = node_data["module"]
            
            # Dynamically import the module
            try:
                module = importlib.import_module(module_name)
                # Instantiate the node
                node_instance = module.get_node(node_data["id"], node_data["z_level"])
            except Exception as e:
                print(f"❌ Failed to load or instantiate node '{current_id}' from module '{module_name}': {e}")
                break
                
            # Execute the node
            context = node_instance.run(context)
            
            if context.get("error"):
                print(f"⚠️ Execution halted due to error in node '{current_id}'.")
                break
                
            current_id = node_data.get("next")
            
        print("\n=== EXECUTION CYCLE COMPLETE ===")
        print(f"Final Context: {context}")

if __name__ == "__main__":
    runtime = EPOSRuntime("pyramid.yaml")
    runtime.run()

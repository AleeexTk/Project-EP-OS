import sys
import os
from pathlib import Path

def initialize_kernel_paths():
    """
    Ensures all Pyramid layers are discoverable by the Python interpreter.
    Unifies the path discovery logic across the entire OS.
    """
    ROOT_DIR = Path(__file__).resolve().parents[2]
    
    # Canonical Layers
    layers = [
        "α_Pyramid_Core",
        "β_Pyramid_Functional",
        "γ_Pyramid_Reflective"
    ]
    
    for layer in layers:
        layer_path = str(ROOT_DIR / layer)
        if layer_path not in sys.path:
            sys.path.append(layer_path)
            
        # Add sub-sectors for direct import (e.g., allow 'import models' from B3)
        for root, dirs, files in os.walk(layer_path):
            if "__init__.py" in files or any(f.endswith(".py") for f in files):
                if root not in sys.path:
                    sys.path.append(root)

if __name__ == "__main__":
    initialize_kernel_paths()
    print("Kernel paths initialized:")
    for p in sys.path:
        if "Pyramid" in p:
            print(f" -> {p}")

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
            
        # Add sub-sectors for direct import (1st level only to prevent deep recursive scan slowdowns)
        for child in Path(layer_path).iterdir():
            if child.is_dir():
                if any(child.glob("*.py")):
                    sys.path.append(str(child))

if __name__ == "__main__":
    initialize_kernel_paths()
    print("Kernel paths initialized:")
    for p in sys.path:
        if "Pyramid" in p:
            print(f" -> {p}")


import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent.parent
sys.path.insert(0, str(THIS_DIR))
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(THIS_DIR.parent / "B2_ProviderMatrix"))

print(f"THIS_DIR: {THIS_DIR}")
print(f"PROJECT_ROOT: {PROJECT_ROOT}")

try:
    import session_models
    print("session_models imported")
    import provider_matrix
    print("provider_matrix imported")
    from provider_matrix import ProviderMatrix
    print("ProviderMatrix imported")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()

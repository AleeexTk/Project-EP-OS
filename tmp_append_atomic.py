import os
import json
import tempfile
from pathlib import Path

target = r'C:\Users\Alex Bear\Desktop\EvoPyramid OS\beta_pyramid_functional\B1_Kernel\SK_Engine\engine.py'

code = """

def write_atomic(file_path: Path, data: dict):
    \"\"\"Atomic write to JSON file using a temporary file.\"\"\"
    import tempfile
    import os
    import json
    parent = file_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=str(parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        if os.path.exists(str(file_path)):
            os.remove(str(file_path))
        os.rename(temp_path, str(file_path))
    except Exception as e:
        if os.path.exists(temp_path):
            try: os.remove(temp_path)
            except: pass
        raise e
"""

with open(target, 'a', encoding='utf-8') as f:
    f.write(code)
print(f"Successfully appended write_atomic to {target}")

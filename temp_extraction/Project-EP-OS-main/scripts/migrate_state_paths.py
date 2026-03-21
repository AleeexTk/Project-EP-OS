import json
from pathlib import Path

STATE_FILE = Path("state/pyramid_state.json")

def migrate_state():
    if not STATE_FILE.exists():
        print("State file not found.")
        return
        
    raw = STATE_FILE.read_text(encoding='utf-8')
    
    # 3-pass replacement
    raw = raw.replace("α_Pyramid_Core", "alpha_pyramid_core")
    raw = raw.replace("β_Pyramid_Functional", "beta_pyramid_functional")
    raw = raw.replace("γ_Pyramid_Reflective", "gamma_pyramid_reflective")
    
    # Also minor variants if any
    raw = raw.replace("?_Pyramid_Core", "alpha_pyramid_core")
    raw = raw.replace("?_Pyramid_Functional", "beta_pyramid_functional")
    raw = raw.replace("?_Pyramid_Reflective", "gamma_pyramid_reflective")

    STATE_FILE.write_text(raw, encoding='utf-8')
    print("State file paths migrated to ASCII.")

if __name__ == "__main__":
    migrate_state()

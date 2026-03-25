import os
import json
from pathlib import Path

# Z13: Alpha Layer - Intent / Seed
# PEAR (Pulse Evolution and Assimilation Ritual)

class PEARSeed:
    def __init__(self, intent: str, root_dir: Path):
        self.intent = intent
        self.root_dir = root_dir
        self.pulse_id = os.urandom(4).hex()
        
    def manifest(self):
        """Создает первичный импульс в слое Alpha"""
        seed_data = {
            "pulse_id": self.pulse_id,
            "intent": self.intent,
            "origin": "user_input",
            "z_level": 13,
            "sector": "SPINE",
            "status": "seed_planted"
        }
        
        target_path = self.root_dir / "alpha_pyramid_core" / "C_Intent" / f"pulse_{self.pulse_id}.json"
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)
            
        return self.pulse_id

if __name__ == "__main__":
    # Test plant
    seed = PEARSeed("Validate the Z17 V1.1 structure manifestation", Path("."))
    pid = seed.manifest()
    print(f"✅ Pulse {pid} manifested at Z13 (Alpha).")

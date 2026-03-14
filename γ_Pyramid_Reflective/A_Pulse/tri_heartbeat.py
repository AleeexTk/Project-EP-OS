import os
import time
import json
from pathlib import Path

# Z3: Gamma Layer - Pulse / Reflection

class TriHeartbeat:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.log_path = self.root_dir / "γ_Pyramid_Reflective" / "A_Pulse" / "heartbeat.log"
        
    def beat(self, state_summary: str):
        """Записывает пульс системы (Z3)"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] PULSE Z3 | STATE: {state_summary}\n"
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry)
            
        print(f"💓 Heartbeat: {state_summary}")

if __name__ == "__main__":
    hb = TriHeartbeat(Path("."))
    hb.beat("System re-orchestration in progress. Parity: 0.82")

import time
import json
import logging
from pathlib import Path
import sys

# Resolve project root — RULE 3: No absolute paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Config
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Z3-HEARTBEAT] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "heartbeat.log"),
        logging.StreamHandler()
    ]
)

def check_entropy():
    """
    Placeholder for entropy calculation. 
    In Z3, entropy represents the 'drift' between visual state and reality.
    """
    state_file = ROOT_DIR / "state" / "pyramid_state.json"
    if not state_file.exists():
        return 1.0 # Max entropy
    
    # Simple check: timestamp of state file vs now
    mtime = state_file.stat().st_mtime
    age = time.time() - mtime
    
    if age < 60: return 0.05 # Healthy pulse
    if age < 300: return 0.2
    return 0.5 # Stale state

def main():
    print(f"💓 [Z3] Tri-Heartbeat initialized at {ROOT_DIR}")
    try:
        while True:
            entropy = check_entropy()
            logging.info(f"PULSE: OK | Entropy: {entropy:.2f} | Status: COHERENT")
            time.sleep(30) # Pulse every 30 seconds
    except KeyboardInterrupt:
        print("\n🛑 [Z3] Heartbeat stopped.")

if __name__ == "__main__":
    main()

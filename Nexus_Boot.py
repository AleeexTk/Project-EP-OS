import subprocess
import sys
import os
import time
import socket
import signal
from pathlib import Path
import webbrowser

# --- COLORS FOR FEEDBACK ---
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_status(msg, type="INFO"):
    colors = {"INFO": BColors.OKBLUE, "SUCCESS": BColors.OKGREEN, "WARN": BColors.WARNING, "ERROR": BColors.FAIL}
    color = colors.get(type, BColors.ENDC)
    print(f"{BColors.BOLD}[NEXUS {type}]{BColors.ENDC} {color}{msg}{BColors.ENDC}")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_port(port):
    if is_port_in_use(port):
        log_status(f"Port {port} is occupied. Purging blocking process...", "WARN")
        try:
            # Silent and robust PowerShell command
            ps_cmd = f'Stop-Process -Id (Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue).OwningProcess -Force -ErrorAction SilentlyContinue'
            cmd = f'powershell -Command "if (Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue) {{ {ps_cmd} }}"'
            subprocess.run(cmd, shell=True, capture_output=True)
            time.sleep(2)
        except Exception as e:
            log_status(f"Failed to kill port {port}: {e}", "ERROR")

def main():
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"{BColors.HEADER}{BColors.BOLD}")
    print("========================================")
    print("      EVOPYRAMID OS: NEXUS IGNITION     ")
    print("      Status: Trinity Protocol V4       ")
    print("========================================")
    print(f"{BColors.ENDC}")
    
    root_dir = Path(__file__).resolve().parent
    
    # 1. CLEANUP PHASE
    log_status("Phase 1: Environment Stabilization...", "INFO")
    for p in [8000, 8001, 3000]:
        kill_port(p)
    
    # 2. VENV VALIDATION
    if not (root_dir / ".venv").exists():
        log_status("Virtual environment missing. Creating...", "WARN")
        subprocess.run("uv sync", cwd=str(root_dir), shell=True)

    # 3. DEPLOYMENT PHASE
    log_status("Phase 2: Deploying Ecosystem Clusters...", "INFO")
    
    ui_dir = root_dir / "evopyramid-v2"
    core_api_path = root_dir / "beta_pyramid_functional" / "D_Interface" / "evo_api.py"
    session_api_dir = root_dir / "beta_pyramid_functional" / "B3_SessionRegistry"
    
    # Using 'uv run python' ensures the .venv is used
    # Explicitly quoting commands for Windows shell
    commands = [
        ("Core Engine", f'uv run python "{core_api_path}"'),
        ("Session Registry", f'uv run uvicorn session_api:app --app-dir "{session_api_dir}" --port 8001'),
        ("Frontend UI", f'npm run dev')
    ]
    
    procs = []
    for name, cmd in commands:
        cwd = str(ui_dir) if name == "Frontend UI" else str(root_dir)
        try:
            log_status(f"Activating {name}...", "INFO")
            # Create unique log files for each cluster
            slug = name.lower().replace(" ", "_")
            out_log = open(root_dir / "state" / f"{slug}_stdout.log", "w")
            err_log = open(root_dir / "state" / f"{slug}_stderr.log", "w")
            
            proc = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=out_log, stderr=err_log)
            procs.append((name, proc, out_log, err_log))
            time.sleep(1) # Stagger boot
        except Exception as e:
            log_status(f"Critical failure launching {name}: {e}", "ERROR")

    time.sleep(3)
    
    # 4. MONITORING
    log_status("Ecosystem deployed. Dashboard: http://localhost:3000", "SUCCESS")
    webbrowser.open("http://localhost:3000")
    
    log_status("System is LIVE. Keep this window open. Press Ctrl+C to HALT.", "INFO")
    
    try:
        while True:
            for name, p, out_f, err_f in procs:
                if p.poll() is not None:
                    log_status(f"Cluster failure: {name} died!", "ERROR")
            time.sleep(5)
    except KeyboardInterrupt:
        print(f"\n{BColors.WARNING}[NEXUS] TEAR-DOWN INITIATED...{BColors.ENDC}")
        for name, p, out_f, err_f in procs:
            p.terminate()
            out_f.close()
            err_f.close()
        log_status("All nodes secured.", "SUCCESS")

if __name__ == "__main__":
    main()

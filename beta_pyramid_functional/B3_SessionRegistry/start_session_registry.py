"""
start_session_registry.py
─────────────────────────
Launch the Session Registry service.
This is the Z9 backend for agent session management.

Usage:
  python start_session_registry.py
  python start_session_registry.py --port 8001 --reload

After start:
  REST API:   http://localhost:8001
  Docs:       http://localhost:8001/docs
  WS Swarm:   ws://localhost:8001/ws/swarm
  Health:     http://localhost:8001/health
"""

import argparse
import subprocess
import sys
from pathlib import Path

SERVICE_DIR = Path(__file__).parent / "beta_Pyramid_Functional" / "B_Engine" / "B3_SessionRegistry"
APP_MODULE = "session_api:app"


def main():
    parser = argparse.ArgumentParser(description="Start EvoPyramid Session Registry (Z9)")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8001, help="Port (default: 8001)")
    parser.add_argument("--reload", action="store_true", help="Enable hot-reload for development")
    args = parser.parse_args()

    cmd = [
        sys.executable, "-m", "uvicorn",
        APP_MODULE,
        "--host", args.host,
        "--port", str(args.port),
    ]
    if args.reload:
        cmd.append("--reload")

    print(f"""
╔══════════════════════════════════════════════════════════╗
║         EvoPyramid OS — Session Registry                ║
║         Z9 · β-layer · GREEN sector                     ║
╠══════════════════════════════════════════════════════════╣
║  REST:   http://localhost:{args.port}                       ║
║  Docs:   http://localhost:{args.port}/docs                  ║
║  WS:     ws://localhost:{args.port}/ws/swarm                ║
║  Health: http://localhost:{args.port}/health                ║
╚══════════════════════════════════════════════════════════╝
""")

    subprocess.run(cmd, cwd=str(SERVICE_DIR))


if __name__ == "__main__":
    main()

"""
EvoPyramid Node: WEB MCP CORE
Layer: beta_pyramid_functional | Sector: GREEN
Z-Level: 7

Runtime shell + web interaction gateway.
Provides HTTP health and status endpoints for the MCP (Model Context Protocol) layer.
"""

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
STATE_FILE = ROOT_DIR / "state" / "pyramid_state.json"

PORT = 8080


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"nodes": {}}


class MCPHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler exposing /health and /status."""

    def log_message(self, format, *args):  # suppress default logs
        pass

    def _respond(self, body: dict, status: int = 200):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._respond({
                "status": "ok",
                "module": "web_mcp_core",
                "z_level": 7,
                "sector": "GREEN",
                "ts": time.time(),
            })
        elif self.path in ("/status", "/state"):
            state = load_state()
            nodes = state.get("nodes", {})
            self._respond({
                "module": "web_mcp_core",
                "total_nodes": len(nodes),
                "states": {
                    s: sum(1 for n in nodes.values() if n.get("state") == s)
                    for s in ("active", "idle", "error")
                },
                "ts": time.time(),
            })
        else:
            self._respond({"error": "not found"}, 404)


def main():
    print(f"🌐 [Z7] WEB MCP CORE — starting on port {PORT}")
    print("  Endpoints: /health  /status")
    print("  Press Ctrl+C to stop.\n")
    server = HTTPServer(("127.0.0.1", PORT), MCPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 [Z7] WEB MCP CORE stopped.")


if __name__ == "__main__":
    main()

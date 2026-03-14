"""
JointSync — Z1 SPINE · γ_Pyramid_Reflective
Heartbeat observer: polls Core Engine and Session Registry health,
reports canon drift, and archives pyramid state periodically.

Usage:
    python joint_sync_z1.py           # continuous loop
    python joint_sync_z1.py --once    # single health pass then exit
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib import error as urlerror
from urllib import request as urlrequest

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT_DIR / "state" / "pyramid_state.json"
ARCHIVE_DIR = ROOT_DIR / "γ_Pyramid_Reflective" / "archives"
SPINE_DIR = ROOT_DIR / "γ_Pyramid_Reflective" / "SPINE"
PULSE_LOG = SPINE_DIR / "pulse_log.jsonl"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
SPINE_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ─────────────────────────────────────────────────────────────────────
CORE_URL = "http://127.0.0.1:8000"
SESSION_URL = "http://127.0.0.1:8001"
HEARTBEAT_INTERVAL = 30       # seconds between health checks
ARCHIVE_INTERVAL = 3600       # seconds between state archives
HTTP_TIMEOUT = 5


# ── HTTP helpers ───────────────────────────────────────────────────────────────

def _get(url: str) -> Optional[Any]:
    """Perform a GET request and return parsed JSON, or None on failure."""
    try:
        req = urlrequest.Request(url, headers={"Accept": "application/json"})
        with urlrequest.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urlerror.URLError:
        return None
    except Exception:
        return None


# ── Health checks ──────────────────────────────────────────────────────────────

def health_check_core() -> Dict[str, Any]:
    """
    GET /state from Core Engine (port 8000).
    Returns dict with 'ok' bool and node stats.
    """
    data = _get(f"{CORE_URL}/state")
    if data is None:
        return {"service": "core_engine", "ok": False, "detail": "unreachable"}

    nodes = data.get("nodes", {})
    states: Dict[str, int] = {}
    for node in nodes.values():
        s = str(node.get("state", "unknown"))
        states[s] = states.get(s, 0) + 1

    return {
        "service": "core_engine",
        "ok": True,
        "total_nodes": len(nodes),
        "states": states,
    }


def health_check_session() -> Dict[str, Any]:
    """
    GET /health from Session Registry (port 8001).
    """
    data = _get(f"{SESSION_URL}/health")
    if data is None:
        return {"service": "session_registry", "ok": False, "detail": "unreachable"}
    return {
        "service": "session_registry",
        "ok": data.get("status") == "ok",
        "sessions_total": data.get("sessions_total", 0),
        "sessions_active": data.get("sessions_active", 0),
        "ws_connections": data.get("ws_connections", 0),
    }


def drift_report() -> Dict[str, Any]:
    """
    GET /canon/guard from Core Engine — checks node drift.
    """
    data = _get(f"{CORE_URL}/canon/guard")
    if data is None:
        return {"service": "canon_guard", "ok": False, "detail": "unreachable"}

    summary = data.get("summary", {})
    return {
        "service": "canon_guard",
        "ok": data.get("status") == "ok",
        "state_nodes": summary.get("state_nodes", 0),
        "discovered_nodes": summary.get("discovered_nodes", 0),
        "missing_in_state": summary.get("missing_in_state", 0),
        "missing_on_disk": summary.get("missing_on_disk", 0),
        "drifted": summary.get("drifted", 0),
    }


# ── Archival ───────────────────────────────────────────────────────────────────

def archive_state() -> None:
    """Backup pyramid_state.json with a timestamp; keep last 10 archives."""
    if not STATE_FILE.exists():
        print("⚠️  [Z1] State file not found — skipping archival.")
        return

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    dest = ARCHIVE_DIR / f"pyramid_state_{timestamp}.json"
    try:
        shutil.copy2(STATE_FILE, dest)
        print(f"📦 [Z1] Archived → {dest.name}")

        # Prune: keep only 10 most recent
        archives = sorted(ARCHIVE_DIR.glob("pyramid_state_*.json"), key=lambda p: p.stat().st_mtime)
        for old in archives[:-10]:
            old.unlink()
            print(f"🧹 [Z1] Pruned old archive: {old.name}")
    except Exception as exc:
        print(f"❌ [Z1] Archival error: {exc}")


# ── Pulse log ──────────────────────────────────────────────────────────────────

def _log_pulse(record: Dict[str, Any]) -> None:
    try:
        with open(PULSE_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except OSError:
        pass


def _print_health(label: str, result: Dict[str, Any]) -> None:
    icon = "🟢" if result.get("ok") else "🔴"
    print(f"  {icon} {label}: {result}")


# ── Heartbeat run ──────────────────────────────────────────────────────────────

def run_heartbeat(once: bool = False) -> None:
    """
    Main heartbeat loop.
    - Every HEARTBEAT_INTERVAL seconds: health + drift check
    - Every ARCHIVE_INTERVAL seconds: state archival
    """
    print(f"🌐 [Z1] Joint Sync starting. Heartbeat={HEARTBEAT_INTERVAL}s  Archive={ARCHIVE_INTERVAL}s")
    last_archive = 0.0

    while True:
        now = time.time()
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

        print(f"\n── [Z1] Heartbeat pulse @ {timestamp} ──────────────────")

        core  = health_check_core()
        sess  = health_check_session()
        drift = drift_report()

        _print_health("Core Engine    ", core)
        _print_health("Session Registry", sess)
        _print_health("Canon Guard    ", drift)

        pulse_record = {
            "timestamp": now,
            "iso": timestamp,
            "core": core,
            "session": sess,
            "drift": drift,
        }
        _log_pulse(pulse_record)

        # Periodic archival
        if now - last_archive >= ARCHIVE_INTERVAL:
            archive_state()
            last_archive = now

        if once:
            print("\n✅ [Z1] Single-pass complete.")
            break

        try:
            time.sleep(HEARTBEAT_INTERVAL)
        except KeyboardInterrupt:
            print("\n🛑 [Z1] Joint Sync stopped.")
            break


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="EvoPyramid Z1 Joint Sync")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single heartbeat pass and exit (useful for tests/CI).",
    )
    args = parser.parse_args()
    run_heartbeat(once=args.once)


if __name__ == "__main__":
    main()

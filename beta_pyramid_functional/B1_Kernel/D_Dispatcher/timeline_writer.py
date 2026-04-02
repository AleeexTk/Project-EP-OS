"""
EvoPyramid OS — Timeline Writer
Layer: Beta / B1_Kernel / D_Dispatcher
Role: Serialized async writer for project_timeline.ndjson.

Uses an asyncio.Queue so that concurrent ZBus events never collide
on the single NDJSON log file. One coroutine owns the file handle.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("TimelineWriter")

PROJECT_ROOT = Path(__file__).resolve().parents[4]
TIMELINE_PATH = PROJECT_ROOT / "timeline" / "project_timeline.ndjson"


class TimelineWriter:
    """Async-safe, queue-serialized writer for the live project timeline."""

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        """Start the background drain loop. Call once from app startup."""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._drain_loop())
            logger.info("[Timeline] Writer started.")

    async def write_event(self, event_dict: Dict[str, Any]) -> None:
        """Enqueue an event for async write. Non-blocking for callers."""
        entry = {
            "time": datetime.now(timezone.utc).isoformat(),
            "topic": event_dict.get("topic", "UNKNOWN"),
            "module_id": (
                event_dict.get("node_id")
                or event_dict.get("session_id")
                or "unknown"
            ),
            "action": event_dict.get("topic", ""),
            "status": "DISPATCHED",
            "payload_keys": list(event_dict.get("payload", {}).keys()),
        }
        await self._queue.put(entry)

    async def _drain_loop(self) -> None:
        """Single coroutine that owns the file — no race conditions possible."""
        TIMELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"[Timeline] Writing to {TIMELINE_PATH}")
        while True:
            try:
                entry = await self._queue.get()
                with TIMELINE_PATH.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Timeline] Write error: {e}")


# Singleton — import and use directly
timeline_writer = TimelineWriter()

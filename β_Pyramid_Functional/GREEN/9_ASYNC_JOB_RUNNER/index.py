"""
EvoPyramid Node: ASYNC JOB RUNNER
Layer: β_Pyramid_Functional | Sector: GREEN
Z-Level: 9

Lightweight thread-pool job queue for background tasks.
Accepts callables, runs them asynchronously, tracks status.
"""

import json
import threading
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, Optional

ROOT_DIR = Path(__file__).resolve().parents[3]
LOG_FILE = ROOT_DIR / "β_Pyramid_Functional" / "logs" / "async_jobs.jsonl"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

MAX_HISTORY = 200


class Job:
    def __init__(self, fn: Callable, args=(), kwargs=None, label: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.fn = fn
        self.args = args
        self.kwargs = kwargs or {}
        self.label = label or fn.__name__
        self.status = "queued"
        self.result: Any = None
        self.error: Optional[str] = None
        self.created_at = time.time()
        self.finished_at: Optional[float] = None


class AsyncJobRunner:
    """
    Z9 Async Job Runner — thread-pool driven background worker.
    """

    def __init__(self, workers: int = 4):
        self._queue: deque[Job] = deque()
        self._history: deque[Dict] = deque(maxlen=MAX_HISTORY)
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._workers = [
            threading.Thread(target=self._worker, daemon=True, name=f"JobWorker-{i}")
            for i in range(workers)
        ]
        for w in self._workers:
            w.start()
        print(f"⚙️  [Z9] AsyncJobRunner started. Workers: {workers}")

    def submit(self, fn: Callable, *args, label: str = "", **kwargs) -> Job:
        job = Job(fn, args=args, kwargs=kwargs, label=label)
        with self._cond:
            self._queue.append(job)
            self._cond.notify()
        print(f"📥 [Z9] Job queued: {job.label} (id={job.id})")
        return job

    def _worker(self):
        while True:
            with self._cond:
                while not self._queue:
                    self._cond.wait()
                job = self._queue.popleft()

            job.status = "running"
            try:
                job.result = job.fn(*job.args, **job.kwargs)
                job.status = "done"
            except Exception as exc:
                job.status = "failed"
                job.error = str(exc)
            job.finished_at = time.time()

            record = {
                "id": job.id,
                "label": job.label,
                "status": job.status,
                "error": job.error,
                "duration": round(job.finished_at - job.created_at, 3),
                "ts": job.finished_at,
            }
            with self._lock:
                self._history.append(record)

            try:
                with open(LOG_FILE, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            except OSError:
                pass

            icon = "✅" if job.status == "done" else "❌"
            print(f"{icon} [Z9] Job {job.id} ({job.label}): {job.status}")

    def history(self, n: int = 10):
        with self._lock:
            return list(self._history)[-n:]

    def stats(self) -> Dict:
        with self._lock:
            done   = sum(1 for r in self._history if r["status"] == "done")
            failed = sum(1 for r in self._history if r["status"] == "failed")
        return {
            "z_level": 9, "sector": "GREEN", "module": "async_job_runner",
            "total_processed": done + failed, "done": done, "failed": failed,
        }


# ── Demo ───────────────────────────────────────────────────────────────────────

def _demo_task(n: int) -> str:
    time.sleep(0.05)
    return f"Task {n} complete"


def main():
    runner = AsyncJobRunner(workers=2)

    jobs = [runner.submit(_demo_task, i, label=f"demo-task-{i}") for i in range(5)]

    # Wait for all jobs
    deadline = time.time() + 5
    while any(j.status in ("queued", "running") for j in jobs):
        if time.time() > deadline:
            break
        time.sleep(0.1)

    print(f"\n✅ [Z9] Async Job Runner self-test complete. Stats: {runner.stats()}")


if __name__ == "__main__":
    main()

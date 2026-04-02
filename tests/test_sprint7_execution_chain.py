"""
tests/test_sprint7_execution_chain.py
Smoke tests for Sprint 7: timeline_writer and solution_resolver.
"""
import asyncio
import json
import pytest
from pathlib import Path


# ── Timeline Writer ───────────────────────────────────────────────────────────

def test_timeline_writer_writes_entry(tmp_path, monkeypatch):
    """A dispatched event must appear in the NDJSON timeline file."""
    from beta_pyramid_functional.B1_Kernel.D_Dispatcher.timeline_writer import TimelineWriter

    writer = TimelineWriter()
    # Redirect writes to a temp file
    monkeypatch.setattr(
        "beta_pyramid_functional.B1_Kernel.D_Dispatcher.timeline_writer.TIMELINE_PATH",
        tmp_path / "test_timeline.ndjson",
    )

    async def run():
        writer.start()
        await writer.write_event({"topic": "EXECUTE_TASK", "payload": {"key": "value"}})
        await asyncio.sleep(0.1)   # let the drain loop flush

    asyncio.run(run())

    timeline_file = tmp_path / "test_timeline.ndjson"
    assert timeline_file.exists(), "Timeline file was not created"
    lines = [l for l in timeline_file.read_text().splitlines() if l.strip()]
    assert len(lines) == 1, f"Expected 1 entry, got {len(lines)}"
    entry = json.loads(lines[0])
    assert entry["topic"] == "EXECUTE_TASK"
    assert "time" in entry


# ── Solution Resolver ─────────────────────────────────────────────────────────

def test_solution_resolver_loads_catalog():
    """Resolver must load at least 1 known solution from the catalog."""
    from beta_pyramid_functional.B1_Kernel.solution_resolver import SolutionResolver
    resolver = SolutionResolver()
    known = resolver.list_solutions()
    assert len(known) > 0, "Solution catalog is empty — check solution_catalog.json"


def test_solution_resolver_returns_steps():
    """get_solution on a known workflow must return an ordered step list."""
    from beta_pyramid_functional.B1_Kernel.solution_resolver import SolutionResolver
    resolver = SolutionResolver()
    steps = resolver.get_solution("PROMPT_DISPATCH_WORKFLOW")
    assert isinstance(steps, list), "Steps must be a list"
    assert len(steps) > 0, "PROMPT_DISPATCH_WORKFLOW has no steps"
    assert "module" in steps[0], "Each step must declare a 'module'"


def test_solution_resolver_unknown_returns_empty():
    """Requesting an unknown solution returns [] without raising."""
    from beta_pyramid_functional.B1_Kernel.solution_resolver import SolutionResolver
    resolver = SolutionResolver()
    result = resolver.get_solution("NONEXISTENT_WORKFLOW_XYZ")
    assert result == []

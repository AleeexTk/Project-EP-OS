"""
test_memory_persistence.py
===========================
Test for SK_Engine long-term memory via CognitiveBridge.

Steps:
  Run 1 -- save a decision via store_decision()
  Run 2 -- find it via retrieve_session_context()

Run from project root:
  python tmp/test_memory_persistence.py --write
  python tmp/test_memory_persistence.py --read
  python tmp/test_memory_persistence.py --roundtrip
"""

import asyncio
import sys
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge


async def write_test():
    """Persist a test architectural decision to long-term memory."""
    print("\n[WRITE] Connecting to CognitiveBridge...")
    bridge = await CognitiveBridge.get_instance()

    block = await bridge.store_decision(
        topic="Z4 ObserverRelay health calculation refactor",
        outcome=(
            "Replaced symbolic 100% health report with real-time calculator. "
            "Uses journal accepted-ratio (60%) + manifest-count ratio (40%). "
            "Score at time of writing: 77.8%."
        ),
        z_level=4,
        tags=["architecture", "observer_relay", "health"],
    )

    print(f"[WRITE] OK Block stored: id={block.id}")
    print(f"        Content preview: {block.content[:80]}...")

    summary = await bridge.health_summary()
    print(f"\n[WRITE] Memory summary: {summary}")


async def read_test():
    """Retrieve a past decision from long-term memory by topic similarity."""
    print("\n[READ] Connecting to CognitiveBridge...")
    bridge = await CognitiveBridge.get_instance()

    summary = await bridge.health_summary()
    print(f"[READ] Memory summary: {summary}")

    if summary["total_blocks"] == 0:
        print("[READ] FAIL No blocks found -- run with --write first.")
        return

    print("\n[READ] Querying: 'ObserverRelay health metric refactoring'...")
    results = await bridge.retrieve_session_context(
        "ObserverRelay health metric refactoring",
        top_k=3,
    )

    if not results:
        print("[READ] FAIL No similar blocks found. Memory empty or topic too distant.")
        return

    print(f"[READ] OK Found {len(results)} relevant block(s) from long-term memory:\n")
    for i, block in enumerate(results, 1):
        print(f"  [{i}] id={block.id}")
        print(f"       tags={block.metadata.get('tags', [])}")
        print(f"       content={block.content[:100]}...")
        print()


async def full_test():
    """Write and immediately read back -- single-run roundtrip check."""
    print("\n[ROUNDTRIP] Running write -> read in one session...")
    bridge = await CognitiveBridge.get_instance()

    block = await bridge.store_decision(
        topic="Full PEAR loop with CognitiveBridge integration",
        outcome=(
            "PEARAgent.perceive() now queries CognitiveBridge as Layer 2 memory. "
            "PEARAgent.reflect() stores to CognitiveBridge for cross-session recall."
        ),
        z_level=8,
        tags=["pear", "architecture", "v11"],
    )
    print(f"[ROUNDTRIP] Stored -> {block.id}")

    results = await bridge.retrieve_session_context("PEAR loop memory integration", top_k=3)
    found = any(b.id == block.id for b in results)

    if found:
        print("[ROUNDTRIP] OK Block retrieved successfully in same session!")
    else:
        print("[ROUNDTRIP] WARN Block not found via similarity -- check LSH threshold config.")

    summary = await bridge.health_summary()
    print(f"[ROUNDTRIP] Final memory summary: {summary}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CognitiveBridge persistence test")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="Store a test decision.")
    group.add_argument("--read", action="store_true", help="Retrieve stored decisions.")
    group.add_argument("--roundtrip", action="store_true", help="Write + read in one run.")
    args = parser.parse_args()

    if args.write:
        asyncio.run(write_test())
    elif args.read:
        asyncio.run(read_test())
    else:
        asyncio.run(full_test())

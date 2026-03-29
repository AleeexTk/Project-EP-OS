"""
CognitiveBridge — B4_Cognitive Layer
=====================================
Long-term semantic memory gateway for EvoPyramid OS agents.

Wraps ProjectCortex (SK_Engine) and provides:
- retrieve_session_context(topic)  → recall past architectural decisions
- store_decision(topic, outcome)   → persist decisions across sessions
- Singleton access via CognitiveBridge.get_instance()
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from pathlib import Path
from typing import List, Optional, Any, Dict
import sys

# --- Path bootstrap ---
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import (
    ProjectCortex,
    QuantumBlock,
    MemoryColor,
    MethodMode,
    HyperNode,
)

logger = logging.getLogger("CognitiveBridge")


class CognitiveBridge:
    """
    Long-term memory gateway for the PEAR Loop and all Z-level agents.

    Storage layout:
        <project_root>/state/project_cortex/blocks/*.json

    The bridge uses ProjectCortex (singleton CortexMemory) so all agents
    share the same persistent semantic memory store.
    """

    _instance: Optional["CognitiveBridge"] = None
    _healing_cache: Dict[str, str] = {}
    _cache_loaded: bool = False
    _cache_file: Path = ROOT_DIR / "state" / "healing_cache.json"

    def __init__(self, cortex: Any):
        self._cortex = cortex

    # ─────────────────────────────────────────
    #  Singleton Factory
    # ─────────────────────────────────────────

    @classmethod
    async def get_instance(cls) -> "CognitiveBridge":
        """
        Return (or create) the shared CognitiveBridge.
        Guarantees ProjectCortex is loaded from disk before returning.
        """
        if cls._instance is None:
            cortex = await ProjectCortex.get_instance()
            cls._instance = cls(cortex)
            cls._load_healing_cache()
            logger.info(
                f"[CognitiveBridge] Initialized with "
                f"{len(cortex.hypergraph.nodes)} nodes from long-term memory."
            )
        return cls._instance

    @classmethod
    def _load_healing_cache(cls) -> None:
        if cls._cache_loaded:
            return
        try:
            if cls._cache_file.exists():
                raw = json.loads(cls._cache_file.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    cls._healing_cache = {str(k): str(v) for k, v in raw.items()}
        except Exception as exc:
            logger.warning(f"[CognitiveBridge] Failed to load healing cache: {exc}")
        finally:
            cls._cache_loaded = True

    @classmethod
    def _save_healing_cache(cls) -> None:
        try:
            cls._cache_file.parent.mkdir(parents=True, exist_ok=True)
            cls._cache_file.write_text(
                json.dumps(cls._healing_cache, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning(f"[CognitiveBridge] Failed to persist healing cache: {exc}")

    # ─────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────

    async def retrieve_session_context(
        self,
        topic: str,
        top_k: int = 5,
        tag_filter: Optional[str] = None,
    ) -> List[QuantumBlock]:
        """
        Retrieve semantically similar past decisions for a given topic.

        Args:
            topic:      Natural-language description of the current intent.
            top_k:      Maximum number of blocks to return.
            tag_filter: Optional tag to narrow results (e.g. "session_memory").

        Returns:
            List of relevant QuantumBlocks, ordered by similarity descending.
        """
        similar = await self._cortex.hypergraph.find_similar(topic, top_k=top_k)
        blocks: List[QuantumBlock] = []
        for node_id, _score in similar:
            node = self._cortex.hypergraph.nodes.get(node_id)
            if not node:
                continue
            block = self._cortex.persistence.load_block(node.block_id)
            if block:
                blocks.append(block)

        if tag_filter:
            blocks = [
                b for b in blocks
                if tag_filter in str(getattr(b, "content", ""))
            ]

        result = blocks[:top_k]
        logger.debug(
            f"[CognitiveBridge] '{topic[:40]}' → {len(result)} relevant blocks retrieved."
        )
        return result

    async def store_decision(
        self,
        topic: str,
        outcome: str,
        z_level: int = 0,
        tags: Optional[List[str]] = None,
    ) -> Any:
        """
        Persist an architectural decision or task outcome to long-term memory.

        Args:
            topic:   Short description of what was decided / done.
            outcome: The result, reasoning, or generated artifact summary.
            z_level: Z-level of the agent storing (for audit trail).
            tags:    Optional extra tags (always includes "session_memory").

        Returns:
            The persisted QuantumBlock.
        """
        all_tags = list(set(["session_memory"] + (tags or [])))

        block = QuantumBlock(
            id=f"mem_{uuid.uuid4().hex[:10]}",
            hyper_id=None,
            base_color=MemoryColor.VIOLET,
            content=f"[TOPIC] {topic}\n[TAGS] {','.join(all_tags)}\n[OUTCOME] {outcome}",
            method=MethodMode.SK2_FUNDAMENTAL,
        )

        # Fast in-process cache for deterministic healing recall
        if "heal" in all_tags or "resolution" in all_tags:
            CognitiveBridge._healing_cache[topic] = outcome
            CognitiveBridge._save_healing_cache()

        # Best-effort persistence to ProjectCortex storage (non-blocking fallback).
        try:
            if hasattr(self._cortex, "persistence"):
                self._cortex.persistence.save_block(block)
            await self._cortex.hypergraph.add_node(
                HyperNode(
                    id=block.id,
                    block_id=block.id,
                    color=MemoryColor.VIOLET,
                    metadata={
                        "tags": all_tags,
                        "z_level": z_level,
                        "source": "CognitiveBridge",
                    },
                ),
                block,
            )
        except Exception as e:
            logger.debug(f"[CognitiveBridge] Persistence fallback skipped: {e}")
        logger.info(
            f"[CognitiveBridge] Stored decision '{topic[:50]}' → block id={block.id}"
        )
        return block

    async def recall_healing_pattern(self, error_signature: str) -> Optional[dict]:
        """
        Search memory for a past successful healing pattern matching this error signature.
        """
        if error_signature in CognitiveBridge._healing_cache:
            outcome = CognitiveBridge._healing_cache[error_signature]
            logger.info(f"[CognitiveBridge] In-process heal pattern recalled for '{error_signature}'!")
            return {"id": f"heal_{error_signature[:12]}", "content": f"[TOPIC] {error_signature}\n[OUTCOME] {outcome}"}

        similar = await self._cortex.hypergraph.find_similar(error_signature, top_k=10)
        for node_id, _score in similar:
            node = self._cortex.hypergraph.nodes.get(node_id)
            if not node:
                continue
            block = self._cortex.persistence.load_block(node.block_id)
            if not block:
                continue
            content = str(getattr(block, "content", ""))
            if ("[TAGS] heal" in content or "[TAGS] resolution" in content or "[TOPIC]" in content) and error_signature in content:
                logger.info(f"[CognitiveBridge] Exact heal pattern recalled for '{error_signature}'!")
                return {"id": node_id, "content": content}
        return None

    async def health_summary(self) -> dict:
        """Return a summary of what's currently in long-term memory."""
        total = len(self._cortex.hypergraph.nodes)
        session_mem = 0
        heal_blocks = 0
        for node in self._cortex.hypergraph.nodes.values():
            block = self._cortex.persistence.load_block(node.block_id)
            if not block:
                continue
            content = str(getattr(block, "content", ""))
            if "[TAGS] session_memory" in content:
                session_mem += 1
            if "[TAGS] heal" in content or node.id.startswith("heal_"):
                heal_blocks += 1
        return {
            "total_blocks": total,
            "session_memory_blocks": session_mem,
            "heal_blocks": heal_blocks,
        }

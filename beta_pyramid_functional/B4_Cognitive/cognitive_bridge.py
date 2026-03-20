"""
CognitiveBridge — B4_Cognitive Layer
=====================================
Long-term semantic memory gateway for EvoPyramid OS agents.

Wraps ProjectCortex (SK_Engine) and provides:
- retrieve_session_context(topic)  → recall past architectural decisions
- store_decision(topic, outcome)   → persist decisions across sessions
- Singleton access via CognitiveBridge.get_instance()
"""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import List, Optional
import sys

# --- Path bootstrap ---
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex, CortexMemory
from beta_pyramid_functional.B1_Kernel.SK_Engine.models import QuantumBlock
from beta_pyramid_functional.B1_Kernel.SK_Engine.config import MemoryColor, MethodMode

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

    def __init__(self, cortex: CortexMemory):
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
            logger.info(
                f"[CognitiveBridge] Initialized with "
                f"{len(cortex.blocks)} blocks from long-term memory."
            )
        return cls._instance

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
        blocks = await self._cortex.find_similar(topic)

        if tag_filter:
            blocks = [
                b for b in blocks
                if tag_filter in b.metadata.get("tags", [])
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
    ) -> QuantumBlock:
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
            base_color=MemoryColor.VIOLET,
            content=f"[TOPIC] {topic}\n[OUTCOME] {outcome}",
            method=MethodMode.SK2_FUNDAMENTAL,
            metadata={
                "tags": all_tags,
                "z_level": z_level,
                "source": "CognitiveBridge",
            },
        )

        await self._cortex.add_block(block)
        logger.info(
            f"[CognitiveBridge] Stored decision '{topic[:50]}' → block id={block.id}"
        )
        return block

    async def health_summary(self) -> dict:
        """Return a summary of what's currently in long-term memory."""
        total = len(self._cortex.blocks)
        session_mem = sum(
            1 for b in self._cortex.blocks.values()
            if "session_memory" in b.metadata.get("tags", [])
        )
        return {
            "total_blocks": total,
            "session_memory_blocks": session_mem,
            "heal_blocks": sum(
                1 for b in self._cortex.blocks.values()
                if b.id.startswith("heal_")
            ),
        }

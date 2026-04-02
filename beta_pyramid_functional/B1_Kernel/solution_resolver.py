"""
EvoPyramid OS — Solution Resolver
Layer: Beta / B1_Kernel
Role: Reads solution_catalog.json and returns ordered execution steps for known workflows.

Usage:
    from beta_pyramid_functional.B1_Kernel.solution_resolver import SolutionResolver
    resolver = SolutionResolver()
    steps = resolver.get_solution("PROMPT_DISPATCH_WORKFLOW")
"""
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("SolutionResolver")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "architecture" / "solution_catalog.json"


class SolutionResolver:
    """Loads the solution catalog and provides lookup for named workflows."""

    def __init__(self):
        self._catalog: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._catalog = data.get("solutions", {})
                logger.info(
                    f"[SolutionResolver] Loaded {len(self._catalog)} solutions "
                    f"from {CATALOG_PATH.name}"
                )
        except FileNotFoundError:
            logger.warning("[SolutionResolver] solution_catalog.json not found. Resolver is empty.")
        except json.JSONDecodeError as e:
            logger.error(f"[SolutionResolver] Malformed catalog JSON: {e}")

    def get_solution(self, name: str) -> list[dict]:
        """Return ordered steps for a named solution, or [] if not found."""
        solution = self._catalog.get(name)
        if solution is None:
            logger.warning(f"[SolutionResolver] Unknown solution '{name}'. Check solution_catalog.json.")
            return []
        steps = solution.get("steps", [])
        logger.info(f"[SolutionResolver] Resolved '{name}' → {len(steps)} steps.")
        return steps

    def list_solutions(self) -> list[str]:
        """Return all known solution names."""
        return list(self._catalog.keys())

    def solution_exists(self, name: str) -> bool:
        return name in self._catalog

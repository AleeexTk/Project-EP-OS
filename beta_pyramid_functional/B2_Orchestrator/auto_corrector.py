import re
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from .llm_orchestrator import AgentOrchestrator
from .synthesis_agent import SynthesisProposal, ProposalType
from beta_pyramid_functional.B3_SessionRegistry.session_models import AgentSession, Provider

logger = logging.getLogger("AutoCorrector")


class AutoCorrector:
    """
    Diagnostic and repair engine for EvoPyramid OS.
    Parses tracebacks and orchestrates LLM-based code fixes.
    """

    def __init__(self, orchestrator: Optional[AgentOrchestrator] = None):
        self.orchestrator = orchestrator or AgentOrchestrator()
        # Regex to catch Python Traceback file/line info
        self.traceback_pattern = re.compile(
            r'File "(?P<file>[^"]+)", line (?P<line>\d+), in (?P<func>\S+)'
        )

    def parse_error(self, error_text: str) -> Optional[Dict[str, Any]]:
        """Extract file, line, and message from a traceback string."""
        matches = list(self.traceback_pattern.finditer(error_text))
        if not matches:
            return None

        last_match = matches[-1]
        error_msg = (
            error_text.splitlines()[-1] if error_text.splitlines() else "Unknown Error"
        )

        return {
            "file": last_match.group("file"),
            "line": int(last_match.group("line")),
            "function": last_match.group("func"),
            "message": error_msg,
        }

    async def propose_fix(self, error_text: str) -> Optional[SynthesisProposal]:
        """
        Generate a structured SynthesisProposal to fix the detected error.

        Strategy:
        - If the file exists locally → read context and ask LLM for a PATCH.
        - If the file is missing → emit a POLICY proposal recommending node creation.
        """
        diag = self.parse_error(error_text)
        if not diag:
            logger.warning("Could not parse error for auto-correction.")
            return None

        file_path = Path(diag["file"])

        # ── Case 1: File exists — ask LLM for a surgical PATCH ──
        if file_path.exists():
            return await self._propose_patch(diag, file_path)

        # ── Case 2: File missing — architectural POLICY recommendation ──
        logger.warning(
            f"[AutoCorrector] Target file '{file_path}' not found locally. "
            "Emitting POLICY proposal for missing node."
        )
        return SynthesisProposal(
            type=ProposalType.POLICY,
            target_node=str(file_path),
            rationale=(
                f"Node '{file_path.name}' referenced in traceback does not exist. "
                "The architecture requires this module to be created or registered."
            ),
            suggested_action=(
                f"CREATE node at path: {file_path}\n"
                "Implement with BaseServiceNode interface and register a "
                ".node_manifest.json manifest."
            ),
            confidence=0.70,
            impact="MEDIUM_RISK_MISSING_NODE",
        )

    async def _propose_patch(
        self, diag: Dict[str, Any], file_path: Path
    ) -> Optional[SynthesisProposal]:
        """Read existing file content and ask LLM for a targeted PATCH."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file for correction: {e}")
            return None

        prompt = f"""AUTOCORRECTOR DIAGNOSTICS:
File: {diag['file']}
Line: {diag['line']}
Error: {diag['message']}

CONTENT OF FAILED MODULE:
```python
{content}
```

TASK: Generate a surgical code fix (PATCH) for this error.
Provide only the necessary code modification or the corrected lines.
Explain WHY this fix works.
"""
        logger.info(f"[AutoCorrector] Requesting autonomous fix for {file_path.name}...")

        session = AgentSession(
            node_id="auto-corrector",
            node_z=12,
            task_title=f"Self-Healing: {file_path.name}",
            provider=Provider.GEMINI,
            task_context=f"Repairing {diag['message']} in {diag['file']}",
        )
        session.add_user_message(prompt)

        response = await self.orchestrator.get_response(session)

        return SynthesisProposal(
            type=ProposalType.PATCH,
            target_node=diag["file"],
            rationale=f"Self-healing fix for: {diag['message']}",
            suggested_action=response or "LLM returned no response.",
            confidence=0.85,
            impact="LOW_RISK_REPAIR",
        )

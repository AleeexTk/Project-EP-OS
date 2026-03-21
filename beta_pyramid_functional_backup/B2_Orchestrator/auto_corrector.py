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
        Strategy: Check Cognitive Memory first. If bypassed, return instantly.
        Otherwise synthesize and store.
        """
        diag = self.parse_error(error_text)
        if not diag:
            logger.warning("Could not parse error for auto-correction.")
            return None

        file_path = Path(diag["file"])
        error_sig = f"{file_path.name}:{diag['line']} - {diag['message']}"

        # ── 0. COGNITIVE RECALL (Memory Bypass) ──
        memory_context = ""
        try:
            from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge
            bridge = await CognitiveBridge.get_instance()
            recalled = await bridge.recall_healing_pattern(error_sig)
            if recalled:
                logger.info(f"[AutoCorrector] Cognitive Recall successful! Bypassing LLM for {error_sig}")
                content = recalled["content"]
                if "[OUTCOME] " in content:
                    import json
                    outcome_str = content.split("[OUTCOME] ", 1)[-1]
                    data = json.loads(outcome_str)
                    proposal = SynthesisProposal(**data)
                    proposal.rationale = f"[MEMORY BYPASS {recalled['id']}] " + proposal.rationale
                    return proposal
            
            # If no exact bypass, fetch semantic context for LLM prompt
            similar = await bridge.retrieve_session_context(error_sig, top_k=2, tag_filter="heal")
            if similar:
                memory_context = "\nPAST SIMILAR HEALING PATTERNS (For reference):\n"
                for idx, b in enumerate(similar):
                    memory_context += f"--- Pattern {idx+1} ---\n{b.content[:400]}...\n"
                    
        except Exception as e:
            logger.warning(f"[AutoCorrector] Cognitive recall failed/skipped: {e}")

        # ── Case 1: File exists — ask LLM for a surgical PATCH ──
        proposal = None
        if file_path.exists():
            proposal = await self._propose_patch(diag, file_path, memory_context)
            
            # Store the proposed fix to memory for future bypass
            if proposal and proposal.type == ProposalType.PATCH:
                try:
                    p_data = proposal.model_dump_json()
                    await bridge.store_decision(
                        topic=error_sig,
                        outcome=p_data,
                        tags=["heal", "resolution"],
                        z_level=12
                    )
                except Exception as e:
                    logger.error(f"[AutoCorrector] Failed to cache fix in memory: {e}")
                    
            return proposal

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
        self, diag: Dict[str, Any], file_path: Path, memory_context: str = ""
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
{memory_context}
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

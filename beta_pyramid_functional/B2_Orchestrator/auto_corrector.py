import re
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
        
        # We take the last match (closest to the actual error)
        last_match = matches[-1]
        error_msg = error_text.splitlines()[-1] if error_text.splitlines() else "Unknown Error"
        
        return {
            "file": last_match.group("file"),
            "line": int(last_match.group("line")),
            "function": last_match.group("func"),
            "message": error_msg
        }

    async def propose_fix(self, error_text: str) -> Optional[SynthesisProposal]:
        """Generate a structured SynthesisProposal to fix the detected error."""
        diag = self.parse_error(error_text)
        if not diag:
            logger.warning("Could not parse error for auto-correction.")
            return None

        file_path = Path(diag["file"])
        if not file_path.exists():
            logger.error(f"Error file {file_path} not found locally.")
            return None

        # Read file context
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file for correction: {e}")
            return None

        # Build prompt for Orchestrator
        prompt = f"""
AUTOCORRECTOR DIAGNOSTICS:
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
        logger.info(f"Requesting autonomous fix for {file_path.name}...")
        
        # Create a proper AgentSession for the correction task
        session = AgentSession(
            node_id="auto-corrector",
            node_z=12,
            task_title=f"Self-Healing: {file_path.name}",
            provider=Provider.GEMINI, # Orchestrator will handle fallback to OLLAMA
            task_context=f"Repairing {diag['message']} in {diag['file']}"
        )
        session.add_user_message(prompt)
        
        response = await self.orchestrator.get_response(session)

        # Create structured proposal
        return SynthesisProposal(
            proposal_type=ProposalType.PATCH,
            target_node=diag['file'],
            rationale=f"Self-healing fix for: {diag['message']}",
            suggested_action=response,
            confidence=0.85,
            impact="LOW_RISK_REPAIR"
        )

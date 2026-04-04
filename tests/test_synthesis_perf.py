import sys
import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope
from beta_pyramid_functional.B2_Orchestrator.synthesis_agent import SynthesisAgent, SynthesisProposal, ProposalType

@pytest.mark.asyncio
async def test_synthesis_ensemble_translation():
    agent = SynthesisAgent()
    
    # Mock Envelope
    envelope = TaskEnvelope(
        task_id="SYN-TEST-001",
        source_node="architect_z17",
        target_node="alpha_spine",
        action="refactor_module",
        intent="Improve modularity",
        origin_z=17
    )
    
    # Mock LLM Responses
    mock_response_gemini = '{"type": "refactor", "target_node": "alpha_spine", "rationale": "Better modularity", "suggested_action": "Move functions to utils", "confidence": 0.95}'
    mock_response_ollama = '{"type": "patch", "target_node": "alpha_spine", "rationale": "Redundancy", "suggested_action": "Patch the spine", "confidence": 0.80}'

    with patch("beta_pyramid_functional.B2_Orchestrator.llm_orchestrator.AgentOrchestrator.get_response", side_effect=[mock_response_gemini, mock_response_ollama]):
        proposal = await agent.translate_task(envelope)
        
        assert proposal is not None
        assert isinstance(proposal, SynthesisProposal)
        assert proposal.type == ProposalType.REFACTOR
        assert proposal.confidence == 0.95
        assert proposal.target_node == "alpha_spine"
        print("Test 1: Synthesis Ensemble picked the best proposal (Gemini) successfully.")

@pytest.mark.asyncio
async def test_synthesis_robust_parsing():
    agent = SynthesisAgent()
    
    # Text with markdown fences
    text_with_markdown = "Here is your proposal:\n```json\n{\"type\": \"optimize\", \"target_node\": \"ZBus\", \"rationale\": \"Latency\", \"suggested_action\": \"Add cache\", \"confidence\": 0.88}\n```"
    
    proposal = agent._parse_proposal(text_with_markdown)
    assert proposal is not None
    assert proposal.type == ProposalType.OPTIMIZE
    assert proposal.confidence == 0.88
    print("Test 2: Robust parsing worked for markdown-fenced JSON.")

if __name__ == "__main__":
    asyncio.run(test_synthesis_ensemble_translation())
    asyncio.run(test_synthesis_robust_parsing())

"""
Provider Matrix — Z8 · β_Pyramid_Functional · RED sector
Maps agent providers to API endpoints and external session URLs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

from session_models import Provider


# ─────────────────────────────────────────
#  Provider Config
# ─────────────────────────────────────────

@dataclass(frozen=True)
class ProviderConfig:
    name:            str
    # External browser URL to open a new chat session
    base_chat_url:   str
    # REST API base for programmatic access (optional)
    api_base:        Optional[str] = None
    # Color identity for pyramid visualization
    color_primary:   str = "#888888"
    color_secondary: str = "#cccccc"
    # Visual marker type ("gradient", "split", "stripe")
    visual_marker:   str = "gradient"


PROVIDER_REGISTRY: dict[Provider, ProviderConfig] = {
    Provider.GPT: ProviderConfig(
        name="ChatGPT / GPT-4o",
        base_chat_url="https://chatgpt.com/",
        api_base="https://api.openai.com/v1",
        color_primary="#10a37f",
        color_secondary="#1a7f5a",
        visual_marker="solid",
    ),
    Provider.GEMINI: ProviderConfig(
        name="Google Gemini",
        base_chat_url="https://aistudio.google.com/prompts/new_chat",
        api_base="https://generativelanguage.googleapis.com/v1beta",
        color_primary="#4285f4",
        color_secondary="#ea4335",
        visual_marker="gradient",          # multicolor spectrum
    ),
    Provider.CLAUDE: ProviderConfig(
        name="Anthropic Claude",
        base_chat_url="https://claude.ai/new",
        api_base="https://api.anthropic.com/v1",
        color_primary="#f5a623",
        color_secondary="#ffffff",
        visual_marker="split",             # white/peach longitudinal split
    ),
    Provider.COPILOT: ProviderConfig(
        name="GitHub Copilot",
        base_chat_url="https://github.com/copilot",
        api_base=None,
        color_primary="#4285f4",
        color_secondary="#ffffff",
        visual_marker="stripe",            # gradient + white center stripe
    ),
    Provider.OLLAMA: ProviderConfig(
        name="Ollama (Local)",
        base_chat_url="http://localhost:11434",
        api_base="http://localhost:11434/api",
        color_primary="#7c3aed",
        color_secondary="#4c1d95",
        visual_marker="solid",
    ),
}


# ─────────────────────────────────────────
#  Matrix Service
# ─────────────────────────────────────────

class ProviderMatrix:

    @staticmethod
    def get_config(provider: Provider) -> ProviderConfig:
        return PROVIDER_REGISTRY[provider]

    @staticmethod
    def generate_session_url(
        provider: Provider,
        task_title: Optional[str] = None,
        node_id: Optional[str] = None,
    ) -> str:
        """
        Generate an external browser URL to open a new chat session.
        Embeds task context as URL params where the provider supports it.
        """
        cfg = PROVIDER_REGISTRY[provider]
        base = cfg.base_chat_url

        if provider == Provider.GEMINI and task_title:
            # AI Studio supports ?model= and initial prompt via query params
            params = {"model": "gemini-2.0-flash-exp"}
            return f"{base}?{urlencode(params)}"

        if provider == Provider.GPT:
            return base  # ChatGPT opens fresh chat by default

        if provider == Provider.CLAUDE:
            return base  # claude.ai/new opens a clean session

        return base

    @staticmethod
    def score_provider(provider: Provider, z_level: int, sector: str) -> int:
        """
        Rank the provider's suitability for a specific pyramid node.
        Score range: 0-100.
        """
        base_scores = {
            Provider.GPT: 85,    # Generalist
            Provider.GEMINI: 90, # Visual/Structural (Alpha heavy)
            Provider.CLAUDE: 92, # Code consistency (Beta/Gamma heavy)
            Provider.OLLAMA: 60, # Local/Private
            Provider.COPILOT: 75 # Context-aware code
        }
        
        score = base_scores.get(provider, 50)
        
        # Alpha Layer (Z11-Z17) - Architectural/Structural
        if z_level >= 11:
            if provider == Provider.GEMINI: score += 10 # Gemini Excel in high-level architectural view
            if provider == Provider.GPT: score += 5
            
        # Beta Layer (Z5-Z11) - Process/Execution
        elif z_level >= 5:
            if provider == Provider.CLAUDE: score += 8 # Claude shines in large project logic
            if provider == Provider.COPILOT: score += 5
            
        # Gamma Layer (Z1-Z5) - Low-level physical manifest
        else:
            if provider == Provider.OLLAMA: score += 15 # Local logic for local files
            
        return min(100, score)

    @staticmethod
    def all_configs() -> dict:
        return {
            p.value: {
                "name": cfg.name,
                "base_chat_url": cfg.base_chat_url,
                "has_api": cfg.api_base is not None,
                "color_primary": cfg.color_primary,
                "color_secondary": cfg.color_secondary,
                "visual_marker": cfg.visual_marker,
            }
            for p, cfg in PROVIDER_REGISTRY.items()
        }

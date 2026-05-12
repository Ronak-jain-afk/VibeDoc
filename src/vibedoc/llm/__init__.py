"""LLM client factory."""

from vibedoc.config import VibeDocConfig
from vibedoc.llm.base import LMStudioClient, LLMClient


def create_client(provider: str = "lmstudio", config: VibeDocConfig | None = None) -> LLMClient:
    """Create an LLM client for the given provider."""
    if config is None:
        config = VibeDocConfig()

    if provider == "lmstudio":
        return LMStudioClient(
            base_url=config.lmstudio_base_url,
            model=config.lmstudio_model,
            api_key=config.lmstudio_api_key,
        )
    raise ValueError(f"Unknown provider: {provider}")
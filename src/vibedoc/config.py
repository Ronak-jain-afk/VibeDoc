"""Configuration loading from environment variables."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

_env_path = Path(".env")
if _env_path.exists():
    load_dotenv(_env_path)


class VibeDocConfig:
    """VibeDoc configuration from environment."""

    lmstudio_base_url: str = os.getenv(
        "VIBEDOC_LMSTUDIO_BASE_URL", "http://192.168.56.1:1234"
    )
    lmstudio_model: str = os.getenv(
        "VIBEDOC_LMSTUDIO_MODEL", "gemma-4-e4b-uncensored-hauhaucs-aggressive:2"
    )
    lmstudio_api_key: str = os.getenv("VIBEDOC_LMSTUDIO_API_KEY", "lm-studio")
    log_level: str = os.getenv("VIBEDOC_LOG_LEVEL", "INFO")

    @classmethod
    def from_args(
        cls,
        lmstudio_base_url: Optional[str] = None,
        lmstudio_model: Optional[str] = None,
        lmstudio_api_key: Optional[str] = None,
    ) -> "VibeDocConfig":
        """Create config with optional overrides."""
        cfg = cls()
        if lmstudio_base_url:
            cfg.lmstudio_base_url = lmstudio_base_url
        if lmstudio_model:
            cfg.lmstudio_model = lmstudio_model
        if lmstudio_api_key:
            cfg.lmstudio_api_key = lmstudio_api_key
        return cfg
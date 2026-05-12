"""LLM client abstraction and implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator

import httpx

from vibedoc.config import VibeDocConfig


@dataclass
class LLMResponse:
    """Wrapper for LLM response content and metadata."""

    content: str
    model: str
    finish_reason: str


class LLMClient(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def query(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Send a query and return full response."""
        raise NotImplementedError

    @abstractmethod
    def stream(self, system_prompt: str, user_prompt: str) -> Iterator[str]:
        """Stream tokens as they arrive, yielding chunks."""
        raise NotImplementedError


class LMStudioClient(LLMClient):
    """LM Studio client using OpenAI-compatible API."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "lm-studio",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    def _post(self, path: str, data: dict) -> httpx.Response:
        """Make a POST request to LM Studio."""
        return httpx.post(
            f"{self.base_url}/api/v1{path}",
            json=data,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=300.0,
        )

    def _post_stream(self, path: str, data: dict) -> httpx.Response:
        """Make a streaming POST request to LM Studio."""
        return httpx.stream(
            "POST",
            f"{self.base_url}/api/v1{path}",
            json=data,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=300.0,
        )

    def query(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Send a query and return full response."""
        response = self._post("/chat", {
            "model": self.model,
            "input": f"{system_prompt}\n\nUser: {user_prompt}",
            "stream": False,
        })
        response.raise_for_status()
        data = response.json()
        content = ""
        if "output" in data:
            for item in data["output"]:
                if item.get("type") == "message":
                    for block in item.get("content", []):
                        if isinstance(block, dict) and block.get("type") == "output_text":
                            content += block.get("text", "")
        return LLMResponse(
            content=content.strip(),
            model=self.model,
            finish_reason="stop",
        )

    def stream(self, system_prompt: str, user_prompt: str) -> Iterator[str]:
        """Stream tokens from the model."""
        with self._post_stream("/chat", {
            "model": self.model,
            "input": f"{system_prompt}\n\nUser: {user_prompt}",
            "stream": True,
        }) as response:
            response.raise_for_status()
            current_event = None
            for line in response.iter_lines():
                if line.startswith("event: "):
                    current_event = line[6:].strip()
                elif line.startswith("data: "):
                    data_str = line[5:].strip()
                    if not data_str or data_str == "[DONE]":
                        continue
                    try:
                        import json
                        data = json.loads(data_str)
                        if current_event == "text" and "text" in data:
                            yield data["text"]
                        elif current_event == "message.delta" and "content" in data:
                            yield data["content"]
                        elif current_event == "message.end":
                            break
                    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                        continue
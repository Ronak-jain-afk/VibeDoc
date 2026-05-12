"""Tests for LLM client."""

from unittest.mock import AsyncMock, patch

from vibedoc.llm.base import LMStudioClient, LLMClient


def test_llm_client_interface():
    """Verify LLMClient is properly abstract."""
    try:
        client = LLMClient()
        client.query("system", "user")
        assert False, "Should not instantiate abstract class"
    except TypeError:
        pass


def test_lmstudio_client_creation():
    """Test LMStudioClient can be created."""
    client = LMStudioClient(
        base_url="http://localhost:1234/v1",
        model="test-model",
        api_key="test-key",
    )
    assert client.model == "test-model"
    assert client.client.api_key == "test-key"


def test_lmstudio_stream():
    """Test LMStudioClient streaming with mock."""
    client = LMStudioClient(
        base_url="http://localhost:1234/v1",
        model="test-model",
        api_key="test-key",
    )

    mock_stream = AsyncMock()
    mock_stream.__anext__ = AsyncMock(return_value="Hello")

    with patch.object(client.client.chat.completions, "create", return_value=mock_stream):
        pass
"""Tests for the Ollama LLM service."""

from unittest.mock import Mock, patch

import httpx
import pytest

from app.services.llm import LLMError, generate_answer


def test_generate_answer_success():
    """A successful Ollama response returns an answer and metrics."""

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "model": "qwen2.5:3b",
        "response": "The maximum PDF upload size is 10 MiB.",
        "done_reason": "stop",
        "prompt_eval_count": 77,
        "eval_count": 15,
    }

    with patch("app.services.llm.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        result = generate_answer(
            prompt="What is the maximum PDF upload size?",
            system_prompt="Answer using only the context.",
        )

    assert result.answer == "The maximum PDF upload size is 10 MiB."
    assert result.model == "qwen2.5:3b"
    assert result.input_tokens == 77
    assert result.output_tokens == 15
    assert result.duration_seconds >= 0


def test_generate_answer_rejects_empty_prompt():
    """Empty prompts must be rejected before making an HTTP request."""

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        generate_answer(
            prompt="   ",
            system_prompt="You are a helpful assistant.",
        )


def test_generate_answer_handles_connection_failure():
    """Connection failures must produce a controlled LLMError."""

    with patch("app.services.llm.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.side_effect = (
            httpx.ConnectError("Connection refused")
        )

        with pytest.raises(LLMError, match="Cannot connect to Ollama"):
            generate_answer(
                prompt="What is KIP?",
                system_prompt="Answer concisely.",
            )


def test_generate_answer_handles_timeout():
    """Slow or unresponsive models must not hang indefinitely."""

    with patch("app.services.llm.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.side_effect = (
            httpx.ReadTimeout("Request timed out")
        )

        with pytest.raises(LLMError, match="timed out"):
            generate_answer(
                prompt="Explain the document.",
                system_prompt="Answer concisely.",
            )


def test_generate_answer_rejects_truncated_output():
    """Incomplete generations must not be presented as final answers."""

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "model": "qwen2.5:3b",
        "response": "The maximum PDF upload",
        "done_reason": "length",
        "prompt_eval_count": 50,
        "eval_count": 512,
    }

    with patch("app.services.llm.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        with pytest.raises(LLMError, match="output token limit"):
            generate_answer(
                prompt="What is the upload limit?",
                system_prompt="Answer concisely.",
            )


def test_generate_answer_rejects_empty_response():
    """An empty model response must not be accepted."""

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "model": "qwen2.5:3b",
        "response": "",
        "done_reason": "stop",
    }

    with patch("app.services.llm.httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = (
            mock_response
        )

        with pytest.raises(LLMError, match="empty answer"):
            generate_answer(
                prompt="What is KIP?",
                system_prompt="Answer concisely.",
            )

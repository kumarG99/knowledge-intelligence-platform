"""Local LLM integration through Ollama."""

from dataclasses import dataclass
from time import perf_counter

import httpx

from app.core.config import settings


class LLMError(Exception):
    """Raised when the LLM service cannot generate an answer."""


@dataclass(frozen=True)
class LLMResponse:
    """Generated answer and inference metrics."""

    answer: str
    model: str
    input_tokens: int
    output_tokens: int
    duration_seconds: float


def generate_answer(prompt: str, system_prompt: str) -> LLMResponse:
    """Generate a response using the configured Ollama model."""

    if settings.llm_provider != "ollama":
        raise LLMError(f"Unsupported LLM provider: {settings.llm_provider}")

    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"

    payload = {
        "model": settings.ollama_model,
        "system": system_prompt,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 512,
        },
    }

    start = perf_counter()

    try:
        with httpx.Client(timeout=settings.ollama_timeout_seconds) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

    except httpx.TimeoutException as exc:
        raise LLMError("Ollama request timed out.") from exc

    except httpx.RequestError as exc:
        raise LLMError("Cannot connect to Ollama.") from exc

    except httpx.HTTPStatusError as exc:
        raise LLMError(f"Ollama returned HTTP {exc.response.status_code}.") from exc

    except ValueError as exc:
        raise LLMError("Ollama returned invalid JSON.") from exc

    duration = perf_counter() - start

    if data.get("done_reason") == "length":
        raise LLMError("Ollama reached the output token limit.")

    answer = data.get("response", "").strip()

    if not answer:
        raise LLMError("Ollama returned an empty answer.")

    return LLMResponse(
        answer=answer,
        model=data.get("model", settings.ollama_model),
        input_tokens=data.get("prompt_eval_count", 0),
        output_tokens=data.get("eval_count", 0),
        duration_seconds=round(duration, 3),
    )

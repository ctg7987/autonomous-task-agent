from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel

from .base import LLMProvider, LLMProviderError, LLMRateLimitError, LLMContextLengthError
from ..logging_config import get_logger

T = TypeVar("T", bound=BaseModel)
logger = get_logger("providers.openai")


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str) -> None:
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=api_key)

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        try:
            resp = await self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            self._map_error(e)

    async def complete_structured(
        self,
        messages: list[dict[str, str]],
        model: str,
        response_model: type[T],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> T:
        schema = self._schema_to_json(response_model)
        messages_with_format = list(messages)
        messages_with_format.append({
            "role": "user",
            "content": f"Respond ONLY with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        })

        try:
            resp = await self._client.chat.completions.create(
                model=model,
                messages=messages_with_format,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content or "{}"
            return self._parse_model(response_model, raw)
        except LLMProviderError:
            raise
        except Exception as e:
            self._map_error(e)

    def _map_error(self, e: Exception) -> None:
        error_str = str(e).lower()
        if "rate_limit" in error_str or "429" in error_str:
            raise LLMRateLimitError(str(e)) from e
        if "context_length" in error_str or "maximum context" in error_str:
            raise LLMContextLengthError(str(e)) from e
        raise LLMProviderError(str(e)) from e

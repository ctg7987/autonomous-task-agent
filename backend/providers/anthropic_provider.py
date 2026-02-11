from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel

from .base import LLMProvider, LLMProviderError, LLMRateLimitError, LLMContextLengthError
from ..logging_config import get_logger

T = TypeVar("T", bound=BaseModel)
logger = get_logger("providers.anthropic")


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str) -> None:
        from anthropic import AsyncAnthropic
        self._client = AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        system_msg = ""
        chat_msgs = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                chat_msgs.append(m)

        if not chat_msgs:
            chat_msgs = [{"role": "user", "content": "Please respond."}]

        try:
            kwargs = dict(
                model=model,
                messages=chat_msgs,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if system_msg:
                kwargs["system"] = system_msg

            resp = await self._client.messages.create(**kwargs)
            return resp.content[0].text if resp.content else ""
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
        messages_copy = list(messages)
        messages_copy.append({
            "role": "user",
            "content": f"Respond ONLY with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        })

        raw = await self.complete(messages_copy, model, temperature, max_tokens)
        try:
            return self._parse_model(response_model, raw)
        except Exception as e:
            raise LLMProviderError(f"Failed to parse structured output: {e}") from e

    def _map_error(self, e: Exception) -> None:
        error_str = str(e).lower()
        if "rate_limit" in error_str or "429" in error_str:
            raise LLMRateLimitError(str(e)) from e
        if "context_length" in error_str or "too long" in error_str:
            raise LLMContextLengthError(str(e)) from e
        raise LLMProviderError(str(e)) from e

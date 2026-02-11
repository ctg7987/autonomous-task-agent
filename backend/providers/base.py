from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProviderError(Exception):
    pass


class LLMRateLimitError(LLMProviderError):
    pass


class LLMContextLengthError(LLMProviderError):
    pass


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a text completion from the given messages."""
        ...

    @abstractmethod
    async def complete_structured(
        self,
        messages: list[dict[str, str]],
        model: str,
        response_model: type[T],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> T:
        """Generate a structured completion that conforms to a Pydantic model."""
        ...

    def _schema_to_json(self, model: type[BaseModel]) -> dict:
        schema = model.model_json_schema()
        return schema

    def _parse_model(self, model_class: type[T], raw: str) -> T:
        """Parse raw JSON string into a Pydantic model, handling markdown fences."""
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]  # remove ```json
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return model_class.model_validate_json(text)

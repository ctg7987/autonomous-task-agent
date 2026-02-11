from __future__ import annotations

from functools import lru_cache
from typing import Optional

from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from ..config import get_settings
from ..logging_config import get_logger

logger = get_logger("providers.registry")

_providers: dict[str, LLMProvider] = {}


def _init_provider(name: str) -> Optional[LLMProvider]:
    settings = get_settings()
    if name == "openai" and settings.openai_api_key:
        return OpenAIProvider(api_key=settings.openai_api_key)
    if name == "anthropic" and settings.anthropic_api_key:
        return AnthropicProvider(api_key=settings.anthropic_api_key)
    return None


def get_provider(name: Optional[str] = None) -> LLMProvider:
    settings = get_settings()
    provider_name = name or settings.active_provider

    if provider_name not in _providers:
        provider = _init_provider(provider_name)
        if provider is None:
            raise ValueError(f"Provider '{provider_name}' not available. Check API key.")
        _providers[provider_name] = provider
        logger.info(f"Initialized LLM provider: {provider_name}")

    return _providers[provider_name]


def get_provider_for_agent(agent_name: str) -> tuple[LLMProvider, str]:
    """Returns (provider, model_name) for a given agent."""
    settings = get_settings()
    model = settings.get_agent_model(agent_name)

    # Determine provider from model name
    if model.startswith("claude"):
        provider_name = "anthropic"
    elif model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        provider_name = "openai"
    else:
        provider_name = settings.active_provider

    provider = get_provider(provider_name)
    return provider, model

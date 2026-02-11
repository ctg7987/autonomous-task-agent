from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # LLM Provider keys (at least one required)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_provider: Literal["openai", "anthropic"] = "openai"

    # Per-agent model configuration
    model_planner: str = "gpt-4o-mini"
    model_searcher: str = "gpt-4o-mini"
    model_analyzer: str = "gpt-4o"
    model_synthesizer: str = "gpt-4o"
    model_critic: str = "gpt-4o"

    # Firecrawl
    firecrawl_api_key: str = ""

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    log_level: str = "INFO"
    allowed_origins: str = "http://localhost:3000"

    # Agent behavior
    max_concurrent_fetches: int = 5
    max_reflection_retries: int = 2
    agent_max_steps: int = 5
    research_timeout_seconds: int = 120

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_agent_model(self, agent_name: str) -> str:
        mapping = {
            "planner": self.model_planner,
            "searcher": self.model_searcher,
            "analyzer": self.model_analyzer,
            "synthesizer": self.model_synthesizer,
            "critic": self.model_critic,
        }
        return mapping.get(agent_name, self.model_planner)

    def has_provider(self, name: str) -> bool:
        if name == "openai":
            return bool(self.openai_api_key)
        if name == "anthropic":
            return bool(self.anthropic_api_key)
        return False

    @property
    def active_provider(self) -> str:
        if self.has_provider(self.default_provider):
            return self.default_provider
        for p in ("openai", "anthropic"):
            if self.has_provider(p):
                return p
        raise ValueError("No LLM provider API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.")


@lru_cache
def get_settings() -> Settings:
    return Settings()

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable, Optional

from ..models.agents import AgentStep, AgentState
from ..models.events import AgentThinkingEvent, AgentActionEvent, SSEEvent
from ..providers.base import LLMProvider
from ..logging_config import get_logger


EmitFn = Callable[[SSEEvent], Awaitable[None]]


class BaseAgent(ABC):
    """Base agent implementing a simplified ReAct (Reason-Act-Observe) loop."""

    name: str = "base"
    description: str = ""

    def __init__(self, provider: LLMProvider, model: str, max_steps: int = 5) -> None:
        self.provider = provider
        self.model = model
        self.max_steps = max_steps
        self.logger = get_logger(f"agents.{self.name}")

    async def run(self, input_data: Any, emit: EmitFn) -> Any:
        """Execute the agent. Subclasses implement _execute for their specific logic."""
        self.logger.info(f"Agent '{self.name}' starting")
        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Starting {self.name} agent...",
            step=0,
        ))

        try:
            result = await self._execute(input_data, emit)
            self.logger.info(f"Agent '{self.name}' completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Agent '{self.name}' failed: {e}")
            raise

    @abstractmethod
    async def _execute(self, input_data: Any, emit: EmitFn) -> Any:
        """Core agent logic. Implemented by each specialized agent."""
        ...

    async def _llm_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await self.provider.complete(
            messages=messages,
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def _llm_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await self.provider.complete_structured(
            messages=messages,
            model=self.model,
            response_model=response_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

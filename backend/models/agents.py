from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    thought: str = ""
    action: str = ""
    action_input: dict = Field(default_factory=dict)
    observation: str = ""


class AgentState(BaseModel):
    steps: list[AgentStep] = Field(default_factory=list)
    final_answer: Any = None
    error: Optional[str] = None


class ReflectionResult(BaseModel):
    is_satisfactory: bool = False
    critique: str = ""
    suggestions: list[str] = Field(default_factory=list)
    score: float = Field(default=0.0, ge=0.0, le=1.0)

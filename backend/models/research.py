from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ResearchQuery(BaseModel):
    query: str
    context: Optional[str] = None
    augmented_queries: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str = ""
    raw_content: Optional[str] = None


class ExtractedContent(BaseModel):
    url: str
    title: str
    content: str
    facts: list[str] = Field(default_factory=list)
    credibility_score: float = Field(default=0.5, ge=0.0, le=1.0)
    extraction_method: str = "firecrawl"


class Citation(BaseModel):
    title: str
    url: str
    credibility_score: float = Field(default=0.5, ge=0.0, le=1.0)
    relevant_claims: list[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    methodology_note: str = ""


class ResearchPlan(BaseModel):
    original_query: str
    decomposed_questions: list[str] = Field(default_factory=list)
    search_strategies: list[str] = Field(default_factory=list)
    expected_source_types: list[str] = Field(default_factory=list)

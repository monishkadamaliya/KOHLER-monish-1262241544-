from __future__ import annotations

from pydantic import BaseModel, Field


class DesignIntent(BaseModel):
    """Structured intent produced from user language; factual catalogue fields stay outside the LLM."""

    style: str | None = None
    colour_preference: str | None = None
    budget_inr: float | None = Field(default=None, ge=0)
    required_categories: list[str] = Field(default_factory=list)
    preferred_categories: list[str] = Field(default_factory=list)
    functional_preferences: list[str] = Field(default_factory=list)
    sustainability_preferences: list[str] = Field(default_factory=list)
    spatial_preferences: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    clarification_required: list[str] = Field(default_factory=list)


class IntentParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    known_budget_inr: float | None = Field(default=None, ge=0)


class IntentParseResponse(BaseModel):
    intent: DesignIntent
    source: str
    warnings: list[str] = Field(default_factory=list)

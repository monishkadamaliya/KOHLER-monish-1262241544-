from __future__ import annotations

from pydantic import BaseModel, Field


class PaletteRequest(BaseModel):
    style: str | None = None
    colour_preference: str | None = None
    domain: str = "bathroom"
    max_products: int = Field(default=20, ge=1, le=100)


class FinishCandidate(BaseModel):
    finish_name: str
    finish_code: str | None = None
    product_count: int
    catalogue_grounded: bool = True
    match_score: float
    reasons: list[str] = Field(default_factory=list)


class PaletteResponse(BaseModel):
    style: str | None
    requested_colour: str | None
    domain: str
    palette_name: str
    finishes: list[FinishCandidate]
    warnings: list[str] = Field(default_factory=list)

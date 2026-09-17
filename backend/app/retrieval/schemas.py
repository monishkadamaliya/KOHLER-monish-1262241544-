from __future__ import annotations

from pydantic import BaseModel, Field


class SpacePreference(BaseModel):
    max_width_mm: float | None = Field(default=None, gt=0)
    max_depth_mm: float | None = Field(default=None, gt=0)


class RetrievalRequest(BaseModel):
    category: str | None = None
    domain: str | None = None
    budget: float | None = Field(default=None, gt=0)
    min_budget: float | None = Field(default=None, gt=0)
    style: str | None = None
    colour_preference: str | None = None
    search: str | None = None
    space: SpacePreference | None = None
    limit: int = Field(default=20, ge=1, le=100)


class RetrievalCandidate(BaseModel):
    sku: str
    name: str
    category: str | None = None
    domain: str | None = None
    price: float | None = None
    finish: str | None = None
    colour: str | None = None
    retrieval_score: float
    semantic_score: float
    style_match: float
    colour_match: float
    dimension_match: float
    matched_themes: list[str] = Field(default_factory=list)
    retrieval_reasons: list[str] = Field(default_factory=list)
    lookbook_evidence: list[str] = Field(default_factory=list)
    review_required: bool = False


class RetrievalResponse(BaseModel):
    candidates: list[RetrievalCandidate]
    total_candidates_considered: int
    engine: str = "deterministic-v1"
    physical_validity_note: str = (
        "Candidates are retrieval results only. Dimensions, clearances, installation and compatibility "
        "must be validated by the constraint engine before selection."
    )

from __future__ import annotations

from pydantic import BaseModel, Field

from app.optimization.configuration_schemas import PlacementOut


class DesignGenerateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    room_width_mm: float = Field(gt=0)
    room_depth_mm: float = Field(gt=0)
    budget_inr: float | None = Field(default=None, gt=0)
    style: str | None = None
    colour_preference: str | None = None
    required_categories: list[str] = Field(default_factory=list, min_length=1)
    domain: str = "bathroom"
    candidates_per_category: int = Field(default=8, ge=1, le=30)
    top_k: int = Field(default=3, ge=1, le=10)


class DesignProduct(BaseModel):
    sku: str
    product_name: str
    category: str | None = None
    price_inr: float
    finish: str | None = None
    colour: str | None = None


class DesignResult(BaseModel):
    rank: int
    skus: list[str]
    products: list[DesignProduct]
    placements: list[PlacementOut]
    total_price_inr: float
    remaining_budget_inr: float
    weighted_score: float
    objectives: dict[str, float]
    compatibility_evidence: list[str] = Field(default_factory=list)
    design_reasons: list[str] = Field(default_factory=list)


class DesignGenerateResponse(BaseModel):
    intent_source: str
    intent_confidence: float
    clarification_required: list[str] = Field(default_factory=list)
    palette_name: str | None = None
    recommended_finishes: list[str] = Field(default_factory=list)
    candidate_counts: dict[str, int] = Field(default_factory=dict)
    evaluated_configurations: int
    feasible_configurations: int
    pareto_configurations: int
    designs: list[DesignResult]
    warnings: list[str] = Field(default_factory=list)
    visualization: dict = Field(default_factory=dict)

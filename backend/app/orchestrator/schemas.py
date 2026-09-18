from __future__ import annotations

from pydantic import BaseModel, Field

from app.intelligence.schemas import DesignIntent
from app.optimization.configuration_schemas import PlacementOut


class DesignGenerateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    room_width_mm: float = Field(gt=0)
    room_depth_mm: float = Field(gt=0)
    budget_inr: float | None = Field(default=None, ge=0)
    style: str | None = None
    colour_preference: str | None = None
    category_candidates: dict[str, list[str]] = Field(default_factory=dict)
    max_configurations: int = Field(default=5000, ge=1, le=50000)
    top_k: int = Field(default=3, ge=1, le=10)


class DesignProduct(BaseModel):
    sku: str
    name: str | None = None
    category: str | None = None
    price_inr: float | None = None
    finish_name: str | None = None
    finish_code: str | None = None


class DesignResult(BaseModel):
    rank: int
    skus: list[str]
    products: list[DesignProduct]
    placements: list[PlacementOut]
    total_price_inr: float
    objectives: dict[str, float]
    weighted_score: float
    compatibility_evidence: list[str]
    visualization: dict


class DesignGenerateResponse(BaseModel):
    intent: DesignIntent
    results: list[DesignResult]
    evaluated_configurations: int
    feasible_configurations: int
    pareto_configurations: int
    warnings: list[str] = Field(default_factory=list)

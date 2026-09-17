from __future__ import annotations

from pydantic import BaseModel, Field

from app.optimization.schemas import OptimizationRequest


class ConfigurationSearchRequest(BaseModel):
    category_candidates: dict[str, list[str]] = Field(min_length=1)
    optimization: OptimizationRequest
    grid_mm: float = Field(default=100.0, gt=0, le=500)
    max_configurations: int = Field(default=5000, ge=1, le=20000)
    max_placement_nodes: int = Field(default=2500, ge=100, le=20000)


class PlacementOut(BaseModel):
    sku: str
    x_mm: float
    y_mm: float
    rotation_deg: float
    width_mm: float
    depth_mm: float


class ConfigurationResult(BaseModel):
    skus: list[str]
    placements: list[PlacementOut]
    total_price: float
    objectives: dict[str, float]
    weighted_score: float
    compatibility_evidence: list[str] = Field(default_factory=list)


class ConfigurationSearchResponse(BaseModel):
    evaluated_configurations: int
    feasible_configurations: int
    pareto_configurations: int
    results: list[ConfigurationResult]
    rejected: list[dict[str, str]] = Field(default_factory=list)

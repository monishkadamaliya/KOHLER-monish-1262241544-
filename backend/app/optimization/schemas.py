from __future__ import annotations

from pydantic import BaseModel, Field


class OptimizationWeights(BaseModel):
    spatial: float = Field(default=0.25, ge=0)
    compatibility: float = Field(default=0.20, ge=0)
    budget: float = Field(default=0.15, ge=0)
    style: float = Field(default=0.15, ge=0)
    colour: float = Field(default=0.10, ge=0)
    space_efficiency: float = Field(default=0.10, ge=0)
    functionality: float = Field(default=0.05, ge=0)
    sustainability: float = Field(default=0.00, ge=0)

    def normalized(self) -> "OptimizationWeights":
        total = sum(self.model_dump().values())
        if total <= 0:
            raise ValueError("At least one optimization weight must be greater than zero.")
        values = {key: value / total for key, value in self.model_dump().items()}
        return OptimizationWeights(**values)


class OptimizationRequest(BaseModel):
    candidate_skus: list[str] = Field(min_length=1)
    budget: float = Field(gt=0)
    style: str | None = None
    colour_preference: str | None = None
    room_width_mm: float | None = Field(default=None, gt=0)
    room_depth_mm: float | None = Field(default=None, gt=0)
    weights: OptimizationWeights = Field(default_factory=OptimizationWeights)
    top_k: int = Field(default=5, ge=1, le=20)


class ObjectiveBreakdown(BaseModel):
    spatial: float
    compatibility: float
    budget: float
    style: float
    colour: float
    space_efficiency: float
    functionality: float
    sustainability: float
    total: float


class OptimizationCandidate(BaseModel):
    sku: str
    product_name: str
    category: str | None = None
    price: float | None = None
    finish: str | None = None
    valid: bool
    objective: ObjectiveBreakdown
    reasons: list[str] = Field(default_factory=list)


class OptimizationResponse(BaseModel):
    feasible_count: int
    candidates: list[OptimizationCandidate]
    rejected: list[OptimizationCandidate] = Field(default_factory=list)

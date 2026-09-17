from __future__ import annotations

from pydantic import BaseModel, Field


class SpaceInput(BaseModel):
    width_mm: float = Field(gt=0)
    depth_mm: float = Field(gt=0)


class ConstraintRequest(BaseModel):
    skus: list[str] = Field(min_length=1)
    budget: float | None = Field(default=None, ge=0)
    space: SpaceInput | None = None
    required_categories: list[str] = Field(default_factory=list)


class ConstraintCheck(BaseModel):
    rule: str
    status: str
    message: str
    evidence: list[str] = Field(default_factory=list)


class ConstraintResult(BaseModel):
    sku: str
    valid: bool
    total_price: float | None = None
    checks: list[ConstraintCheck]
    missing_dependencies: list[str] = Field(default_factory=list)


class ConstraintResponse(BaseModel):
    valid: bool
    results: list[ConstraintResult]

from __future__ import annotations

from pydantic import BaseModel, Field


class PointInput(BaseModel):
    x_mm: float
    y_mm: float


class OpeningInput(BaseModel):
    kind: str
    x_mm: float
    y_mm: float
    width_mm: float = Field(gt=0)
    depth_mm: float = Field(default=1.0, gt=0)
    hinge_x_mm: float | None = None
    hinge_y_mm: float | None = None
    swing_deg: float = Field(default=0.0, ge=0, le=360)
    direction_deg: float = 0.0


class FixturePlacement(BaseModel):
    sku: str
    x_mm: float
    y_mm: float
    rotation_deg: float = 0.0
    clearance_mm: float = Field(default=0.0, ge=0)


class SpatialValidationRequest(BaseModel):
    room_width_mm: float = Field(gt=0)
    room_depth_mm: float = Field(gt=0)
    fixtures: list[FixturePlacement] = Field(min_length=1)
    openings: list[OpeningInput] = Field(default_factory=list)


class SpatialCheck(BaseModel):
    rule: str
    status: str
    message: str
    evidence: list[str] = Field(default_factory=list)


class SpatialFixtureResult(BaseModel):
    sku: str
    valid: bool
    checks: list[SpatialCheck]


class SpatialValidationResponse(BaseModel):
    valid: bool
    results: list[SpatialFixtureResult]

from __future__ import annotations

from pydantic import BaseModel, Field


class DetectedObject(BaseModel):
    object_type: str
    label: str | None = None
    x_mm: float | None = None
    y_mm: float | None = None
    width_mm: float | None = None
    depth_mm: float | None = None
    confidence: float = Field(ge=0, le=1)
    measurement_source: str = "estimated_from_image"


class BathroomSpaceEstimate(BaseModel):
    room_width_mm: float | None = None
    room_depth_mm: float | None = None
    confidence: float = Field(default=0, ge=0, le=1)
    measurement_status: str = "requires_user_confirmation"
    objects: list[DetectedObject] = Field(default_factory=list)
    openings: list[DetectedObject] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class VisionAnalyzeResponse(BaseModel):
    source: str
    space: BathroomSpaceEstimate
    raw_model_output_used: bool = False

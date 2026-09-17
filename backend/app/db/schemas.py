from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku: str
    product_name: str
    collection: str | None = None
    family_id: str | None = None
    product_type: str | None = None
    domain: str | None = None
    category: str | None = None
    subcategory: str | None = None
    mrp: float | None = None
    currency: str | None = None
    finish_code: str | None = None
    finish_name: str | None = None
    colour_name: str | None = None
    colour_family: str | None = None
    width_mm: float | None = None
    depth_mm: float | None = None
    height_mm: float | None = None
    length_mm: float | None = None
    min_width_mm: float | None = None
    max_width_mm: float | None = None
    min_depth_mm: float | None = None
    max_depth_mm: float | None = None
    is_configurable: bool | None = None
    site_dependent: bool | None = None
    source_page: int | None = None
    review_required: bool | None = None


class RelationshipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_sku: str
    relationship_type: str
    target_sku: str
    requirement: str | None = None
    evidence: str | None = None
    source_page: int | None = None
    confidence: float | None = None

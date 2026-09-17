from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Catalogue(Base):
    __tablename__ = "catalogues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    catalogue_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    brand: Mapped[str] = mapped_column(String(80), default="KOHLER")
    market: Mapped[str] = mapped_column(String(80), default="India")
    edition: Mapped[str | None] = mapped_column(String(80))
    year: Mapped[int | None] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    prices_tax_inclusive: Mapped[bool] = mapped_column(Boolean, default=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(120), index=True)
    product_name: Mapped[str] = mapped_column(Text)
    collection: Mapped[str | None] = mapped_column(String(180))
    family_id: Mapped[str | None] = mapped_column(String(180), index=True)
    product_type: Mapped[str | None] = mapped_column(String(120))
    domain: Mapped[str | None] = mapped_column(String(80), index=True)
    category: Mapped[str | None] = mapped_column(String(120), index=True)
    subcategory: Mapped[str | None] = mapped_column(String(160))
    raw_description: Mapped[str | None] = mapped_column(Text)
    raw_catalogue_text: Mapped[str | None] = mapped_column(Text)
    mrp: Mapped[float | None] = mapped_column(Float, index=True)
    currency: Mapped[str | None] = mapped_column(String(8))
    tax_included: Mapped[bool | None] = mapped_column(Boolean)
    finish_code: Mapped[str | None] = mapped_column(String(40), index=True)
    finish_name: Mapped[str | None] = mapped_column(String(120))
    colour_name: Mapped[str | None] = mapped_column(String(120))
    colour_family: Mapped[str | None] = mapped_column(String(80))
    dimension_raw: Mapped[str | None] = mapped_column(Text)
    width_mm: Mapped[float | None] = mapped_column(Float)
    depth_mm: Mapped[float | None] = mapped_column(Float)
    height_mm: Mapped[float | None] = mapped_column(Float)
    diameter_mm: Mapped[float | None] = mapped_column(Float)
    length_mm: Mapped[float | None] = mapped_column(Float)
    min_width_mm: Mapped[float | None] = mapped_column(Float)
    max_width_mm: Mapped[float | None] = mapped_column(Float)
    min_depth_mm: Mapped[float | None] = mapped_column(Float)
    max_depth_mm: Mapped[float | None] = mapped_column(Float)
    min_height_mm: Mapped[float | None] = mapped_column(Float)
    dimension_type: Mapped[str | None] = mapped_column(String(50))
    included_components: Mapped[str | None] = mapped_column(Text)
    required_components: Mapped[str | None] = mapped_column(Text)
    order_with_components: Mapped[str | None] = mapped_column(Text)
    compatible_skus: Mapped[str | None] = mapped_column(Text)
    compatibility_notes: Mapped[str | None] = mapped_column(Text)
    is_configurable: Mapped[bool | None] = mapped_column(Boolean)
    configuration_type: Mapped[str | None] = mapped_column(String(120))
    configuration_options: Mapped[str | None] = mapped_column(Text)
    orientation: Mapped[str | None] = mapped_column(String(80))
    site_dependent: Mapped[bool | None] = mapped_column(Boolean)
    configuration_notes: Mapped[str | None] = mapped_column(Text)
    source_page: Mapped[int | None] = mapped_column(Integer)
    source_type: Mapped[str | None] = mapped_column(String(50))
    extraction_confidence: Mapped[float | None] = mapped_column(Float)
    review_required: Mapped[bool | None] = mapped_column(Boolean)
    review_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("sku", "source_page", name="uq_product_sku_page"),)


class ProductRelationship(Base):
    __tablename__ = "product_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_sku: Mapped[str] = mapped_column(String(120), index=True)
    relationship_type: Mapped[str] = mapped_column(String(80), index=True)
    target_sku: Mapped[str] = mapped_column(String(120), index=True)
    requirement: Mapped[str | None] = mapped_column(String(80))
    evidence: Mapped[str | None] = mapped_column(Text)
    source_page: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column(Float)

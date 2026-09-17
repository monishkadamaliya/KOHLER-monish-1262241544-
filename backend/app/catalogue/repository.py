from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.models import Product, ProductRelationship


def get_product(db: Session, sku: str) -> Product | None:
    return db.scalar(select(Product).where(Product.sku == sku).order_by(Product.source_page))


def list_products(
    db: Session,
    category: str | None = None,
    domain: str | None = None,
    max_price: float | None = None,
    finish: str | None = None,
    limit: int = 100,
) -> list[Product]:
    conditions = []
    if category:
        conditions.append(Product.category.ilike(category))
    if domain:
        conditions.append(Product.domain.ilike(domain))
    if max_price is not None:
        conditions.append(Product.mrp <= max_price)
    if finish:
        conditions.append(
            and_(
                Product.finish_name.is_not(None),
                Product.finish_name.ilike(f"%{finish}%"),
            )
        )
    stmt = select(Product).where(*conditions).order_by(Product.mrp).limit(min(max(limit, 1), 500))
    return list(db.scalars(stmt).all())


def get_relationships(db: Session, sku: str) -> list[ProductRelationship]:
    stmt = select(ProductRelationship).where(ProductRelationship.source_sku == sku)
    return list(db.scalars(stmt).all())


def get_components(db: Session, sku: str) -> list[ProductRelationship]:
    stmt = select(ProductRelationship).where(
        ProductRelationship.source_sku == sku,
        ProductRelationship.relationship_type.in_(["requires", "included_component", "order_with"]),
    )
    return list(db.scalars(stmt).all())

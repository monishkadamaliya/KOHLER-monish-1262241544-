from __future__ import annotations

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.db.models import Product, ProductRelationship


def get_product(db: Session, sku: str) -> Product | None:
    """Return the canonical first catalogue occurrence for an exact SKU."""
    return db.scalar(select(Product).where(Product.sku == sku).order_by(Product.source_page, Product.id))


def list_products(
    db: Session,
    category: str | None = None,
    domain: str | None = None,
    max_price: float | None = None,
    min_price: float | None = None,
    finish: str | None = None,
    search: str | None = None,
    limit: int = 100,
) -> list[Product]:
    conditions = []
    if category:
        conditions.append(Product.category.ilike(category))
    if domain:
        conditions.append(Product.domain.ilike(domain))
    if max_price is not None:
        conditions.append(Product.mrp <= max_price)
    if min_price is not None:
        conditions.append(Product.mrp >= min_price)
    if finish:
        conditions.append(Product.finish_name.ilike(f"%{finish}%"))
    if search:
        pattern = f"%{search}%"
        conditions.append(
            or_(
                Product.sku.ilike(pattern),
                Product.product_name.ilike(pattern),
                Product.collection.ilike(pattern),
                Product.family_id.ilike(pattern),
            )
        )

    stmt = select(Product).where(*conditions).order_by(Product.mrp.asc().nulls_last(), Product.sku).limit(
        min(max(limit, 1), 500)
    )
    return list(db.scalars(stmt).all())


def get_relationships(db: Session, sku: str) -> list[ProductRelationship]:
    stmt = select(ProductRelationship).where(ProductRelationship.source_sku == sku).order_by(ProductRelationship.id)
    return list(db.scalars(stmt).all())


def get_components(db: Session, sku: str) -> list[ProductRelationship]:
    stmt = select(ProductRelationship).where(
        ProductRelationship.source_sku == sku,
        ProductRelationship.relationship_type.in_(["requires", "included_component", "order_with"]),
    ).order_by(ProductRelationship.id)
    return list(db.scalars(stmt).all())


def count_products(db: Session) -> int:
    from sqlalchemy import func
    return int(db.scalar(select(func.count()).select_from(Product)) or 0)


def count_relationships(db: Session) -> int:
    from sqlalchemy import func
    return int(db.scalar(select(func.count()).select_from(ProductRelationship)) or 0)

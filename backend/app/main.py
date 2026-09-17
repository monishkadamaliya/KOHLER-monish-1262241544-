from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.catalogue.repository import get_components, get_product, get_relationships, list_products
from app.db.database import get_db
from app.db.models import Base
from app.db.database import engine
from app.db.schemas import ProductOut, RelationshipOut

app = FastAPI(
    title="KOHLER AI Bathroom Intelligence API",
    version="0.1.0",
    description="Engine 1: authoritative catalogue access layer for the constraint-aware design system.",
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "catalogue"}


@app.get("/products/{sku}", response_model=ProductOut)
def product(sku: str, db: Session = Depends(get_db)) -> ProductOut:
    item = get_product(db, sku)
    if item is None:
        raise HTTPException(status_code=404, detail=f"SKU not found: {sku}")
    return item


@app.get("/products", response_model=list[ProductOut])
def products(
    category: str | None = None,
    domain: str | None = None,
    max_price: float | None = Query(default=None, ge=0),
    finish: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ProductOut]:
    return list_products(db, category, domain, max_price, finish, limit)


@app.get("/products/{sku}/relationships", response_model=list[RelationshipOut])
def relationships(sku: str, db: Session = Depends(get_db)) -> list[RelationshipOut]:
    return get_relationships(db, sku)


@app.get("/products/{sku}/components", response_model=list[RelationshipOut])
def components(sku: str, db: Session = Depends(get_db)) -> list[RelationshipOut]:
    return get_components(db, sku)

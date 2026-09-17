from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.catalogue.repository import (
    count_products,
    count_relationships,
    get_components,
    get_product,
    get_relationships,
    list_products,
)
from app.db.database import engine, get_db
from app.db.models import Base
from app.db.schemas import ProductOut, RelationshipOut
from app.retrieval.schemas import RetrievalRequest, RetrievalResponse
from app.retrieval.service import CatalogueRetrievalService

app = FastAPI(
    title="KOHLER AI Bathroom Intelligence API",
    version="0.3.0",
    description="Engine 1 catalogue truth + Engine 2 ranked catalogue retrieval for the constraint-aware design system.",
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "catalogue"}


@app.get("/catalogue/stats")
def catalogue_stats(db: Session = Depends(get_db)) -> dict[str, int]:
    return {
        "products": count_products(db),
        "relationships": count_relationships(db),
    }


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
    min_price: float | None = Query(default=None, ge=0),
    finish: str | None = None,
    search: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ProductOut]:
    return list_products(db, category, domain, max_price, min_price, finish, search, limit)


@app.get("/products/{sku}/relationships", response_model=list[RelationshipOut])
def relationships(sku: str, db: Session = Depends(get_db)) -> list[RelationshipOut]:
    return get_relationships(db, sku)


@app.get("/products/{sku}/components", response_model=list[RelationshipOut])
def components(sku: str, db: Session = Depends(get_db)) -> list[RelationshipOut]:
    return get_components(db, sku)


@app.post("/retrieval/search", response_model=RetrievalResponse)
def retrieval_search(
    request: RetrievalRequest,
    db: Session = Depends(get_db),
) -> RetrievalResponse:
    return CatalogueRetrievalService(db).search(request)

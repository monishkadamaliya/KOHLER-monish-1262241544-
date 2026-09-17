from __future__ import annotations

from sqlalchemy.orm import Session

from app.catalogue.repository import list_products
from app.db.models import Product
from app.retrieval.schemas import RetrievalCandidate, RetrievalRequest, RetrievalResponse
from app.retrieval.scoring import score_product


class CatalogueRetrievalService:
    """Generate ranked catalogue candidates without claiming physical validity."""

    def __init__(self, db: Session):
        self.db = db

    def search(self, request: RetrievalRequest) -> RetrievalResponse:
        # Cheap factual filters happen before scoring. Hard spatial/compatibility
        # validation belongs to Engine 3 and is intentionally not performed here.
        products = list_products(
            self.db,
            category=request.category,
            domain=request.domain,
            max_price=request.budget,
            min_price=request.min_budget,
            search=request.search,
            limit=500,
        )

        ranked: list[RetrievalCandidate] = []
        for product in products:
            score, metadata = score_product(
                product,
                style=request.style,
                colour_preference=request.colour_preference,
                budget=request.budget,
                max_width_mm=request.space.max_width_mm if request.space else None,
                max_depth_mm=request.space.max_depth_mm if request.space else None,
                search=request.search,
            )
            ranked.append(
                RetrievalCandidate(
                    sku=product.sku,
                    name=product.product_name,
                    category=product.category,
                    domain=product.domain,
                    price=product.mrp,
                    finish=product.finish_name,
                    colour=product.colour_name,
                    retrieval_score=score,
                    review_required=bool(product.review_required),
                    **metadata,
                )
            )

        ranked.sort(key=lambda item: (-item.retrieval_score, item.price is None, item.sku))
        return RetrievalResponse(
            candidates=ranked[: request.limit],
            total_candidates_considered=len(products),
        )

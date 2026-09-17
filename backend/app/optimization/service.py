from __future__ import annotations

from sqlalchemy.orm import Session

from app.catalogue.repository import get_product
from app.constraints.service import _check_dependencies
from app.optimization.schemas import (
    ObjectiveBreakdown,
    OptimizationCandidate,
    OptimizationRequest,
    OptimizationResponse,
)
from app.optimization.scoring import objective_scores, weighted_total


class BathroomOptimizer:
    """Ranks catalogue candidates only after deterministic hard constraints are applied."""

    def __init__(self, db: Session):
        self.db = db

    def optimize(self, request: OptimizationRequest) -> OptimizationResponse:
        weights = request.weights.normalized()
        feasible: list[OptimizationCandidate] = []
        rejected: list[OptimizationCandidate] = []
        seen: set[str] = set()

        for sku in request.candidate_skus:
            if sku in seen:
                continue
            seen.add(sku)
            product = get_product(self.db, sku)
            if product is None:
                rejected.append(self._rejected(sku, "SKU does not exist in the authoritative catalogue."))
                continue

            reasons: list[str] = []
            if product.mrp is None:
                rejected.append(self._rejected_product(product, "Missing price prevents budget optimization."))
                continue
            if product.mrp > request.budget:
                rejected.append(self._rejected_product(product, "Product exceeds the hard budget constraint."))
                continue

            dependency_check, missing = _check_dependencies(self.db, product.sku)
            if dependency_check.status == "FAIL":
                rejected.append(self._rejected_product(product, dependency_check.message))
                continue
            if dependency_check.status == "REVIEW":
                rejected.append(self._rejected_product(product, dependency_check.message))
                continue

            width = product.width_mm or product.max_width_mm
            depth = product.depth_mm or product.max_depth_mm
            if request.room_width_mm and request.room_depth_mm and (width is None or depth is None):
                rejected.append(self._rejected_product(product, "Missing deterministic footprint prevents spatial optimization."))
                continue
            if request.room_width_mm and width and width > request.room_width_mm:
                rejected.append(self._rejected_product(product, "Product footprint exceeds available room width."))
                continue
            if request.room_depth_mm and depth and depth > request.room_depth_mm:
                rejected.append(self._rejected_product(product, "Product footprint exceeds available room depth."))
                continue

            scores = objective_scores(product, request)
            total = weighted_total(scores, weights)
            reasons.append("Passed hard budget, dependency, and available-footprint checks.")
            feasible.append(OptimizationCandidate(
                sku=product.sku,
                product_name=product.product_name,
                category=product.category,
                price=product.mrp,
                finish=product.finish_name,
                valid=True,
                objective=ObjectiveBreakdown(**scores, total=total),
                reasons=reasons,
            ))

        feasible.sort(key=lambda item: (-item.objective.total, item.price or float("inf"), item.sku))
        return OptimizationResponse(feasible_count=len(feasible), candidates=feasible[:request.top_k], rejected=rejected)

    @staticmethod
    def _rejected(sku: str, reason: str) -> OptimizationCandidate:
        zero = ObjectiveBreakdown(spatial=0, compatibility=0, budget=0, style=0, colour=0, space_efficiency=0, functionality=0, sustainability=0, total=0)
        return OptimizationCandidate(sku=sku, product_name="Unknown SKU", valid=False, objective=zero, reasons=[reason])

    @staticmethod
    def _rejected_product(product, reason: str) -> OptimizationCandidate:
        zero = ObjectiveBreakdown(spatial=0, compatibility=0, budget=0, style=0, colour=0, space_efficiency=0, functionality=0, sustainability=0, total=0)
        return OptimizationCandidate(sku=product.sku, product_name=product.product_name, category=product.category, price=product.mrp, finish=product.finish_name, valid=False, objective=zero, reasons=[reason])

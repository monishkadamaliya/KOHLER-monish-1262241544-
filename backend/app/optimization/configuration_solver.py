from __future__ import annotations

from sqlalchemy.orm import Session

from app.catalogue.repository import get_product, get_relationships
from app.constraints.spatial import validate_spatial
from app.constraints.spatial_schemas import FixturePlacement, SpatialValidationRequest
from app.optimization.configuration import Configuration, generate_configurations
from app.optimization.configuration_schemas import ConfigurationResult, ConfigurationSearchRequest, ConfigurationSearchResponse, PlacementOut
from app.optimization.pareto import pareto_frontier
from app.optimization.placement import generate_placements
from app.optimization.scoring import objective_scores, weighted_total


OBJECTIVES = ["spatial", "compatibility", "budget", "style", "colour", "space_efficiency", "functionality", "sustainability"]


class FeasibleConfigurationSolver:
    """Connect configuration search to deterministic compatibility and spatial validation."""

    def __init__(self, db: Session):
        self.db = db

    def search(self, request: ConfigurationSearchRequest) -> ConfigurationSearchResponse:
        configurations = generate_configurations(request.category_candidates, request.max_configurations)
        evaluated: list[tuple[Configuration, dict[str, float]]] = []
        metadata: dict[tuple[str, ...], dict] = {}
        rejected: list[dict[str, str]] = []

        for config in configurations:
            products = [get_product(self.db, sku) for sku in config.skus]
            if any(product is None for product in products):
                rejected.append({"skus": ",".join(config.skus), "reason": "Catalogue SKU missing."})
                continue
            products = [product for product in products if product is not None]

            total_price = sum(product.mrp or 0 for product in products)
            if any(product.mrp is None for product in products):
                rejected.append({"skus": ",".join(config.skus), "reason": "Missing catalogue price."})
                continue
            if total_price > request.optimization.budget:
                rejected.append({"skus": ",".join(config.skus), "reason": "Configuration exceeds budget."})
                continue

            compatibility_ok, compatibility_evidence, compatibility_reason = self._validate_dependencies(config.skus)
            if not compatibility_ok:
                rejected.append({"skus": ",".join(config.skus), "reason": compatibility_reason})
                continue

            placements = generate_placements(
                products,
                request.optimization.room_width_mm or 0,
                request.optimization.room_depth_mm or 0,
                grid_mm=request.grid_mm,
                max_nodes=request.max_placement_nodes,
            ) if request.optimization.room_width_mm and request.optimization.room_depth_mm else None
            if placements is None:
                rejected.append({"skus": ",".join(config.skus), "reason": "No deterministic non-colliding placement found, or a product lacks a deterministic footprint."})
                continue

            spatial_request = SpatialValidationRequest(
                room_width_mm=request.optimization.room_width_mm,
                room_depth_mm=request.optimization.room_depth_mm,
                fixtures=[
                    FixturePlacement(sku=p.sku, x_mm=p.x_mm, y_mm=p.y_mm, rotation_deg=p.rotation_deg)
                    for p in placements
                ],
                openings=[],
            )
            spatial_result = validate_spatial(self.db, spatial_request)
            if not spatial_result.valid:
                rejected.append({"skus": ",".join(config.skus), "reason": "Deterministic spatial validation did not PASS for every fixture."})
                continue

            parts = [objective_scores(product, request.optimization) for product in products]
            scores = {key: sum(part[key] for part in parts) / len(parts) for key in parts[0]}
            # The configuration has passed explicit dependency and geometry checks.
            scores["compatibility"] = 1.0
            evaluated.append((config, scores))
            metadata[config.skus] = {
                "products": products,
                "placements": placements,
                "total_price": total_price,
                "compatibility_evidence": compatibility_evidence,
            }

        frontier = pareto_frontier(evaluated, OBJECTIVES)
        frontier.sort(key=lambda item: weighted_total(item[1], request.optimization.weights.normalized()), reverse=True)

        results = []
        for config, scores in frontier[: request.optimization.top_k]:
            meta = metadata[config.skus]
            results.append(
                ConfigurationResult(
                    skus=list(config.skus),
                    placements=[PlacementOut(**placement.__dict__) for placement in meta["placements"]],
                    total_price=meta["total_price"],
                    objectives=scores,
                    weighted_score=weighted_total(scores, request.optimization.weights.normalized()),
                    compatibility_evidence=meta["compatibility_evidence"],
                )
            )

        return ConfigurationSearchResponse(
            evaluated_configurations=len(configurations),
            feasible_configurations=len(evaluated),
            pareto_configurations=len(frontier),
            results=results,
            rejected=rejected[:200],
        )

    def _validate_dependencies(self, skus: tuple[str, ...]) -> tuple[bool, list[str], str]:
        selected = set(skus)
        evidence: list[str] = []
        for sku in skus:
            for relation in get_relationships(self.db, sku):
                relation_type = (relation.relationship_type or "").lower()
                if relation_type == "requires":
                    if relation.target_sku not in selected:
                        return False, evidence, f"{sku} requires {relation.target_sku}, which is not in the configuration."
                    target = get_product(self.db, relation.target_sku)
                    if target is None:
                        return False, evidence, f"{sku} requires {relation.target_sku}, but that required catalogue target is unresolved."
                    evidence.append(f"{sku} requires {relation.target_sku}; supported by catalogue relationship evidence.")
                elif relation_type == "compatible_with" and relation.target_sku in selected:
                    evidence.append(f"{sku} is explicitly compatible with {relation.target_sku}.")
        return True, evidence, ""

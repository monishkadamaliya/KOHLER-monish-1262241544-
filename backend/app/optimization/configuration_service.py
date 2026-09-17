from __future__ import annotations

from sqlalchemy.orm import Session

from app.catalogue.repository import get_product
from app.optimization.configuration import Configuration, generate_configurations
from app.optimization.pareto import pareto_frontier
from app.optimization.scoring import objective_scores, weighted_total
from app.optimization.schemas import OptimizationRequest


class ConfigurationOptimizer:
    """Search complete category combinations, reject hard failures, then rank feasible designs."""

    def __init__(self, db: Session):
        self.db = db

    def search(self, category_candidates: dict[str, list[str]], request: OptimizationRequest, max_configurations: int = 5000):
        configurations = generate_configurations(category_candidates, max_configurations)
        evaluated: list[tuple[Configuration, dict[str, float]]] = []

        for config in configurations:
            products = [get_product(self.db, sku) for sku in config.skus]
            if any(item is None for item in products):
                continue
            products = [item for item in products if item is not None]

            total_price = sum(item.mrp or 0 for item in products)
            if any(item.mrp is None for item in products) or total_price > request.budget:
                continue

            # Configuration-level compatibility will be supplied by the relationship graph.
            # Until all relationship semantics are present, absence of evidence is not treated as compatibility.
            scores = self._configuration_scores(products, request)
            evaluated.append((config, scores))

        objectives = ["spatial", "compatibility", "budget", "style", "colour", "space_efficiency", "functionality", "sustainability"]
        frontier = pareto_frontier(evaluated, objectives)
        frontier.sort(key=lambda item: weighted_total(item[1], request.weights.normalized()), reverse=True)
        return frontier[: request.top_k]

    @staticmethod
    def _configuration_scores(products, request) -> dict[str, float]:
        parts = [objective_scores(item, request) for item in products]
        return {
            key: sum(part[key] for part in parts) / len(parts)
            for key in parts[0]
        }

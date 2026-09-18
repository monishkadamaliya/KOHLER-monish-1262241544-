from __future__ import annotations

from sqlalchemy.orm import Session

from app.colour.schemas import PaletteRequest
from app.colour.service import ColourIntelligenceService
from app.intelligence.schemas import IntentParseRequest
from app.intelligence.service import IntentService
from app.catalogue.repository import get_product
from app.optimization.configuration_schemas import ConfigurationSearchRequest
from app.optimization.configuration_solver import FeasibleConfigurationSolver
from app.optimization.schemas import OptimizationRequest
from app.orchestrator.schemas import DesignGenerateRequest, DesignGenerateResponse, DesignProduct, DesignResult


class DesignOrchestrator:
    """Single application boundary joining intent, catalogue, colour, constraints and optimization."""

    def __init__(self, db: Session):
        self.db = db

    def generate(self, request: DesignGenerateRequest) -> DesignGenerateResponse:
        parsed = IntentService().parse(
            IntentParseRequest(text=request.text, known_budget_inr=request.budget_inr)
        )
        intent = parsed.intent

        budget = request.budget_inr if request.budget_inr is not None else intent.budget_inr
        if budget is None:
            raise ValueError("A budget is required either in the request or user text.")

        style = request.style or intent.style
        colour = request.colour_preference or intent.colour_preference

        palette = ColourIntelligenceService(self.db).generate(
            PaletteRequest(style=style, colour_preference=colour, domain="bathroom")
        )
        finish_names = {item.finish_name.lower() for item in palette.finishes}

        candidates = request.category_candidates
        if finish_names:
            # Finish filtering is intentionally deterministic and catalogue-grounded.
            filtered: dict[str, list[str]] = {}
            for category, skus in candidates.items():
                keep: list[str] = []
                for sku in skus:
                    product = get_product(self.db, sku)
                    if product is None:
                        continue
                    if not colour or not product.finish_name or product.finish_name.lower() in finish_names:
                        keep.append(sku)
                filtered[category] = keep
            candidates = filtered

        optimization = OptimizationRequest(
            budget=budget,
            style=style,
            colour_preference=colour,
            room_width_mm=request.room_width_mm,
            room_depth_mm=request.room_depth_mm,
            top_k=request.top_k,
        )
        search_request = ConfigurationSearchRequest(
            category_candidates=candidates,
            max_configurations=request.max_configurations,
            optimization=optimization,
        )
        search_result = FeasibleConfigurationSolver(self.db).search(search_request)

        results: list[DesignResult] = []
        for rank, result in enumerate(search_result.results, start=1):
            products = []
            for sku in result.skus:
                item = get_product(self.db, sku)
                if item is not None:
                    products.append(
                        DesignProduct(
                            sku=item.sku,
                            name=item.name,
                            category=item.category,
                            price_inr=item.mrp,
                            finish_name=item.finish_name,
                            finish_code=item.finish_code,
                        )
                    )
            visualization = {
                "room": {"width_mm": request.room_width_mm, "depth_mm": request.room_depth_mm},
                "fixtures": [placement.model_dump() for placement in result.placements],
                "render_mode": "2d-plan",
            }
            results.append(
                DesignResult(
                    rank=rank,
                    skus=result.skus,
                    products=products,
                    placements=result.placements,
                    total_price_inr=result.total_price,
                    objectives=result.objectives,
                    weighted_score=result.weighted_score,
                    compatibility_evidence=result.compatibility_evidence,
                    visualization=visualization,
                )
            )

        return DesignGenerateResponse(
            intent=intent,
            results=results,
            evaluated_configurations=search_result.evaluated_configurations,
            feasible_configurations=search_result.feasible_configurations,
            pareto_configurations=search_result.pareto_configurations,
            warnings=parsed.warnings + palette.warnings,
        )

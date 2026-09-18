from __future__ import annotations

from sqlalchemy.orm import Session

from app.catalogue.repository import get_product
from app.colour.schemas import PaletteRequest
from app.colour.service import ColourIntelligenceService
from app.intelligence.schemas import IntentParseRequest
from app.intelligence.service import IntentService
from app.optimization.configuration_schemas import ConfigurationSearchRequest
from app.optimization.configuration_solver import FeasibleConfigurationSolver
from app.optimization.schemas import OptimizationRequest
from app.retrieval.schemas import RetrievalRequest, SpacePreference
from app.retrieval.service import CatalogueRetrievalService
from app.orchestration.schemas import DesignGenerateRequest, DesignGenerateResponse, DesignProduct, DesignResult


class DesignOrchestrator:
    """Application boundary joining interpretation, retrieval, validation and optimization."""

    def __init__(self, db: Session):
        self.db = db
        self.intent = IntentService()
        self.retrieval = CatalogueRetrievalService(db)
        self.colour = ColourIntelligenceService(db)
        self.solver = FeasibleConfigurationSolver(db)

    def generate(self, request: DesignGenerateRequest) -> DesignGenerateResponse:
        parsed = self.intent.parse(IntentParseRequest(text=request.text, known_budget_inr=request.budget_inr))
        intent = parsed.intent
        budget = request.budget_inr if request.budget_inr is not None else intent.budget_inr
        style = request.style or intent.style
        colour = request.colour_preference or intent.colour_preference
        categories = [c.strip() for c in (request.required_categories or intent.required_categories) if c.strip()]
        warnings = list(parsed.warnings)

        if budget is None:
            warnings.append("Budget is required for deterministic configuration filtering.")
        if not categories:
            warnings.append("No product categories were identified. Add required categories or specify them in the request.")
        if budget is None or not categories:
            return self._empty_response(request, intent, parsed.source, warnings)

        palette = self.colour.generate(PaletteRequest(
            style=style,
            colour_preference=colour,
            domain=request.domain,
            max_products=request.candidates_per_category,
        ))
        warnings.extend(palette.warnings)

        category_candidates: dict[str, list[str]] = {}
        candidate_counts: dict[str, int] = {}
        for category in categories:
            retrieved = self.retrieval.search(RetrievalRequest(
                category=category,
                domain=request.domain,
                budget=budget,
                style=style,
                colour_preference=colour,
                space=SpacePreference(max_width_mm=request.room_width_mm, max_depth_mm=request.room_depth_mm),
                limit=request.candidates_per_category,
            ))
            skus = [candidate.sku for candidate in retrieved.candidates]
            category_candidates[category] = skus
            candidate_counts[category] = len(skus)
            if not skus:
                warnings.append(f"No catalogue candidates retrieved for category '{category}'.")

        if any(not values for values in category_candidates.values()):
            return DesignGenerateResponse(
                intent_source=parsed.source,
                intent_confidence=intent.confidence,
                clarification_required=intent.clarification_required,
                palette_name=palette.palette_name,
                recommended_finishes=[f.finish_name for f in palette.finishes],
                candidate_counts=candidate_counts,
                evaluated_configurations=0,
                feasible_configurations=0,
                pareto_configurations=0,
                designs=[],
                warnings=warnings,
                visualization=self._visualization_payload(request, []),
            )

        optimization = OptimizationRequest(
            candidate_skus=[sku for values in category_candidates.values() for sku in values],
            budget=budget,
            style=style,
            colour_preference=colour,
            room_width_mm=request.room_width_mm,
            room_depth_mm=request.room_depth_mm,
            top_k=request.top_k,
        )
        solved = self.solver.search(ConfigurationSearchRequest(
            category_candidates=category_candidates,
            optimization=optimization,
            max_configurations=request.max_configurations,
        ))

        designs: list[DesignResult] = []
        for rank, result in enumerate(solved.results, start=1):
            products = []
            for sku in result.skus:
                product = get_product(self.db, sku)
                if product is None or product.mrp is None:
                    continue
                products.append(DesignProduct(
                    sku=product.sku,
                    product_name=product.product_name,
                    category=product.category,
                    price_inr=product.mrp,
                    finish=product.finish_name,
                    colour=product.colour_name,
                ))
            designs.append(DesignResult(
                rank=rank,
                skus=result.skus,
                products=products,
                placements=result.placements,
                total_price_inr=result.total_price,
                remaining_budget_inr=budget - result.total_price,
                weighted_score=result.weighted_score,
                objectives=result.objectives,
                compatibility_evidence=result.compatibility_evidence,
                design_reasons=self._design_reasons(result.objectives, style, colour),
            ))

        return DesignGenerateResponse(
            intent_source=parsed.source,
            intent_confidence=intent.confidence,
            clarification_required=intent.clarification_required,
            palette_name=palette.palette_name,
            recommended_finishes=[f.finish_name for f in palette.finishes],
            candidate_counts=candidate_counts,
            evaluated_configurations=solved.evaluated_configurations,
            feasible_configurations=solved.feasible_configurations,
            pareto_configurations=solved.pareto_configurations,
            designs=designs,
            warnings=warnings,
            visualization=self._visualization_payload(request, designs),
        )

    @staticmethod
    def _empty_response(request, intent, source, warnings):
        return DesignGenerateResponse(
            intent_source=source,
            intent_confidence=intent.confidence,
            clarification_required=intent.clarification_required,
            candidate_counts={},
            evaluated_configurations=0,
            feasible_configurations=0,
            pareto_configurations=0,
            designs=[],
            warnings=warnings,
            visualization=DesignOrchestrator._visualization_payload(request, []),
        )

    @staticmethod
    def _design_reasons(objectives: dict[str, float], style: str | None, colour: str | None) -> list[str]:
        reasons = ["Passed deterministic catalogue, budget, dependency and placement validation."]
        reasons.append("Optimized across spatial, compatibility, budget, style, colour and functional objectives.")
        if style:
            reasons.append(f"Style preference considered: {style}.")
        if colour:
            reasons.append(f"Colour preference considered: {colour}.")
        if objectives.get("sustainability", 0) > 0:
            reasons.append("Sustainability score uses only documented catalogue evidence.")
        return reasons

    @staticmethod
    def _visualization_payload(request: DesignGenerateRequest, designs: list[DesignResult]) -> dict:
        return {
            "type": "validated_2d_layout",
            "room": {"width_mm": request.room_width_mm, "depth_mm": request.room_depth_mm},
            "designs": [
                {"rank": d.rank, "skus": d.skus, "placements": [p.model_dump() for p in d.placements]}
                for d in designs
            ],
            "note": "Renderer should place only optimizer-selected SKUs at validated coordinates; image generation must not invent product placement or catalogue facts.",
        }

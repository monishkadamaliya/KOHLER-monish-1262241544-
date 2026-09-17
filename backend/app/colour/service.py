from __future__ import annotations

from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.colour.schemas import FinishCandidate, PaletteRequest, PaletteResponse
from app.db.models import Product


STYLE_FINISHES = {
    "Japanese Zen": ("white", "natural", "brushed", "bronze", "matte black"),
    "Minimalist Modern": ("chrome", "polished", "matte black", "black", "brushed"),
    "Classic Luxury": ("gold", "french gold", "rose gold", "bronze", "brushed bronze"),
}

COLOUR_TERMS = {
    "natural": ("natural", "white", "cream", "beige", "stone", "sand"),
    "black": ("black", "matte black", "blackened"),
    "gold": ("gold", "french gold", "brass", "bronze"),
    "rose gold": ("rose gold", "brushed rose gold"),
    "chrome": ("chrome", "polished chrome"),
    "brushed": ("brushed", "brushed bronze", "brushed rose gold"),
}


def _match_score(finish: str, style: str | None, colour: str | None) -> tuple[float, list[str]]:
    text = finish.lower()
    score = 0.0
    reasons: list[str] = []
    if style:
        terms = STYLE_FINISHES.get(style, ())
        if any(term in text for term in terms):
            score += 0.55
            reasons.append(f"finish aligns with {style} finish vocabulary")
    if colour:
        terms = COLOUR_TERMS.get(colour.lower(), (colour.lower(),))
        if any(term in text for term in terms):
            score += 0.45
            reasons.append(f"finish matches requested colour family: {colour}")
    return min(score, 1.0), reasons


class ColourIntelligenceService:
    def __init__(self, db: Session):
        self.db = db

    def generate(self, request: PaletteRequest) -> PaletteResponse:
        stmt = select(Product.finish_name, Product.finish_code, func.count(Product.id)).where(
            Product.finish_name.is_not(None),
            Product.finish_name != "",
        )
        if request.domain:
            stmt = stmt.where(Product.domain.ilike(request.domain))
        stmt = stmt.group_by(Product.finish_name, Product.finish_code)
        rows = self.db.execute(stmt).all()

        candidates = []
        for finish_name, finish_code, count in rows:
            score, reasons = _match_score(finish_name, request.style, request.colour_preference)
            candidates.append(FinishCandidate(
                finish_name=finish_name,
                finish_code=finish_code,
                product_count=count,
                match_score=score,
                reasons=reasons,
            ))
        candidates.sort(key=lambda item: (-item.match_score, -item.product_count, item.finish_name.lower()))
        candidates = candidates[: request.max_products]

        palette_name = request.style or request.colour_preference or "Catalogue Finish Palette"
        warnings = [
            "Finish matches are catalogue-grounded; this endpoint does not claim an official KOHLER palette recommendation.",
            "Colour harmony between multiple finishes is not yet a physical/product compatibility rule.",
        ]
        return PaletteResponse(
            style=request.style,
            requested_colour=request.colour_preference,
            domain=request.domain,
            palette_name=palette_name,
            finishes=candidates,
            warnings=warnings,
        )

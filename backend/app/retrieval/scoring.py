from __future__ import annotations

import re

from app.db.models import Product

THEME_TERMS: dict[str, set[str]] = {
    "Minimalist Modern": {"modern", "minimal", "minimalist", "contemporary", "edge", "reach", "purist", "parallel"},
    "Classic Luxury": {"classic", "luxury", "luxurious", "heritage", "traditional", "gold", "brass", "rose gold"},
    "Japanese Zen": {"zen", "natural", "organic", "calm", "serene", "stone", "earth", "wood", "nature"},
}

COLOUR_TERMS: dict[str, set[str]] = {
    "natural": {"white", "cream", "beige", "stone", "natural", "earth", "almond", "sand"},
    "black": {"black", "matte black", "blackened"},
    "gold": {"gold", "french gold", "brass", "brushed bronze", "bronze"},
    "rose": {"rose", "rose gold", "brushed rose gold"},
    "chrome": {"chrome", "polished chrome"},
    "brushed": {"brushed", "brushed bronze", "brushed rose gold"},
}


def _text(product: Product) -> str:
    values = [
        product.product_name,
        product.collection,
        product.family_id,
        product.product_type,
        product.category,
        product.subcategory,
        product.raw_description,
        product.raw_catalogue_text,
        product.finish_name,
        product.colour_name,
        product.colour_family,
    ]
    return " ".join(v for v in values if v).lower()


def _tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    return set(re.findall(r"[a-z0-9]+(?:\s+[a-z0-9]+)?", value.lower()))


def style_match(product: Product, style: str | None) -> tuple[float, list[str], list[str]]:
    if not style:
        return 0.5, [], []
    terms = THEME_TERMS.get(style, set())
    text = _text(product)
    hits = [term for term in terms if term in text]
    if not hits:
        return 0.0, [], []
    score = min(1.0, 0.55 + 0.15 * len(hits))
    reasons = [f"Style evidence in catalogue text: {', '.join(sorted(hits)[:4])}"]
    return score, [style], reasons


def colour_match(product: Product, preference: str | None) -> tuple[float, list[str]]:
    if not preference:
        return 0.5, []
    text = " ".join(
        v.lower() for v in [product.finish_name, product.colour_name, product.colour_family] if v
    )
    terms = COLOUR_TERMS.get(preference.lower(), {preference.lower()})
    hits = [term for term in terms if term in text]
    if hits:
        return 1.0, [f"Finish/colour matches preference: {hits[0]}"]
    if text:
        return 0.2, ["Catalogue has a finish/colour value, but it does not match the requested preference."]
    return 0.0, ["No catalogue finish/colour evidence available."]


def dimension_match(product: Product, max_width: float | None, max_depth: float | None) -> tuple[float, list[str]]:
    checks: list[bool] = []
    reasons: list[str] = []
    if max_width is not None:
        width = product.width_mm or product.max_width_mm
        if width is not None:
            checks.append(width <= max_width)
            reasons.append(f"width {width:g} mm vs requested maximum {max_width:g} mm")
    if max_depth is not None:
        depth = product.depth_mm or product.max_depth_mm
        if depth is not None:
            checks.append(depth <= max_depth)
            reasons.append(f"depth {depth:g} mm vs requested maximum {max_depth:g} mm")
    if not checks:
        return 0.5, ["No comparable catalogue dimension available; defer to constraint validation."]
    return sum(checks) / len(checks), reasons


def score_product(
    product: Product,
    *,
    style: str | None,
    colour_preference: str | None,
    budget: float | None,
    max_width_mm: float | None,
    max_depth_mm: float | None,
    search: str | None,
) -> tuple[float, dict]:
    style_score, themes, style_reasons = style_match(product, style)
    colour_score, colour_reasons = colour_match(product, colour_preference)
    dim_score, dim_reasons = dimension_match(product, max_width_mm, max_depth_mm)

    semantic = 0.0
    reasons = style_reasons + colour_reasons
    if search:
        query = search.lower().strip()
        text = _text(product)
        if query and query in text:
            semantic = 1.0
            reasons.append("Direct catalogue-text match for search query.")
        else:
            query_terms = set(query.split())
            text_terms = set(text.split())
            overlap = len(query_terms & text_terms) / max(len(query_terms), 1)
            semantic = min(1.0, overlap)
            if semantic:
                reasons.append("Partial catalogue-text match for search query.")
    else:
        semantic = 0.5

    budget_score = 0.5
    if budget is not None and product.mrp is not None:
        if product.mrp <= budget:
            budget_score = 1.0 - 0.35 * (product.mrp / budget)
            reasons.append("Product price is within the requested item budget.")
        else:
            budget_score = max(0.0, 1.0 - (product.mrp - budget) / budget)
            reasons.append("Product exceeds the requested item budget; retained only as a retrieval candidate.")

    # Retrieval ranking is deliberately not physical validation.
    total = 100 * (
        0.30 * semantic
        + 0.25 * style_score
        + 0.20 * colour_score
        + 0.15 * dim_score
        + 0.10 * budget_score
    )
    return round(total, 2), {
        "semantic_score": round(semantic, 3),
        "style_match": round(style_score, 3),
        "colour_match": round(colour_score, 3),
        "dimension_match": round(dim_score, 3),
        "matched_themes": themes,
        "retrieval_reasons": reasons + dim_reasons,
    }

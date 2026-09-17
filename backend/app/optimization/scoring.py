from __future__ import annotations

from app.retrieval.scoring import colour_score, style_score


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def budget_score(price: float | None, budget: float) -> float:
    if price is None or price < 0 or budget <= 0:
        return 0.0
    if price > budget:
        return 0.0
    return _clamp(1.0 - price / budget)


def spatial_score(width: float | None, depth: float | None, room_width: float | None, room_depth: float | None) -> float:
    if not room_width or not room_depth or not width or not depth:
        return 0.5
    if width > room_width or depth > room_depth:
        return 0.0
    room_area = room_width * room_depth
    return _clamp(1.0 - (width * depth) / room_area)


def space_efficiency_score(width: float | None, depth: float | None, room_width: float | None, room_depth: float | None) -> float:
    return spatial_score(width, depth, room_width, room_depth)


def functionality_score(product) -> float:
    """Evidence-based proxy: configurable products expose more documented choice, otherwise neutral."""
    if product.is_configurable:
        return 0.8
    return 0.5


def sustainability_score(product) -> float:
    """Only score explicit sustainability evidence; never infer environmental performance."""
    text = " ".join(v.lower() for v in [product.raw_description, product.raw_catalogue_text] if v)
    terms = ("water saving", "water-saving", "water efficient", "water-efficient", "recycled", "low flow")
    return 1.0 if any(term in text for term in terms) else 0.0


def objective_scores(product, request) -> dict[str, float]:
    return {
        "spatial": spatial_score(product.width_mm or product.max_width_mm, product.depth_mm or product.max_depth_mm, request.room_width_mm, request.room_depth_mm),
        "compatibility": 1.0,
        "budget": budget_score(product.mrp, request.budget),
        "style": style_score(product, request.style) if request.style else 0.5,
        "colour": colour_score(product, request.colour_preference) if request.colour_preference else 0.5,
        "space_efficiency": space_efficiency_score(product.width_mm or product.max_width_mm, product.depth_mm or product.max_depth_mm, request.room_width_mm, request.room_depth_mm),
        "functionality": functionality_score(product),
        "sustainability": sustainability_score(product),
    }


def weighted_total(scores: dict[str, float], weights) -> float:
    return _clamp(sum(scores[name] * weight for name, weight in weights.model_dump().items()))

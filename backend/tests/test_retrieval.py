from app.db.models import Product
from app.retrieval.scoring import colour_match, dimension_match, score_product, style_match


def product(**overrides) -> Product:
    values = {
        "sku": "K-TEST",
        "product_name": "ModernLife Edge Basin",
        "collection": "ModernLife Edge",
        "family_id": "modernlife-edge-basin",
        "product_type": "vessel basin",
        "domain": "bathroom",
        "category": "basin",
        "subcategory": "vessel",
        "raw_description": "Modern minimalist basin",
        "finish_name": "Honed Black",
        "colour_name": "Black",
        "colour_family": "black",
        "mrp": 38000,
        "width_mm": 600,
        "depth_mm": 396,
        "review_required": False,
    }
    values.update(overrides)
    return Product(**values)


def test_style_match_is_evidence_based():
    score, themes, reasons = style_match(product(), "Minimalist Modern")
    assert score > 0
    assert themes == ["Minimalist Modern"]
    assert reasons


def test_colour_match_does_not_guess_missing_finish():
    score, reasons = colour_match(product(finish_name=None, colour_name=None, colour_family=None), "gold")
    assert score == 0.0
    assert "No catalogue finish/colour evidence available." in reasons


def test_dimension_match_is_not_a_hard_validator():
    score, reasons = dimension_match(product(width_mm=800), 700, 500)
    assert score == 0.0
    assert reasons


def test_score_contains_explicit_retrieval_components():
    score, metadata = score_product(
        product(),
        style="Minimalist Modern",
        colour_preference="black",
        budget=40000,
        max_width_mm=700,
        max_depth_mm=500,
        search="basin",
    )
    assert 0 <= score <= 100
    assert metadata["style_match"] > 0
    assert metadata["colour_match"] == 1.0
    assert metadata["dimension_match"] == 1.0
    assert metadata["semantic_score"] == 1.0

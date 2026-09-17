from collections import Counter

from app.catalogue.validation import validate_catalogue_columns, validate_product


def test_required_columns_are_checked():
    assert validate_catalogue_columns(["sku", "product_name"]) == ["category", "currency", "mrp", "source_page"]


def test_validation_flags_invalid_product():
    row = {
        "sku": "K-1",
        "product_name": "Example",
        "category": "faucets",
        "mrp": -1,
        "currency": "USD",
        "source_page": None,
    }
    errors = validate_product(row, Counter())
    assert "negative_price" in errors
    assert "non_inr_currency" in errors
    assert "missing_source_page" in errors

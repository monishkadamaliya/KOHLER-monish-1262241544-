from app.catalogue.normalization import normalize_product


def test_normalization_preserves_missing_facts():
    import pandas as pd

    row = pd.Series({
        "sku": "K-TEST",
        "product_name": "Test Product",
        "mrp": "12,500",
        "source_page": "42",
        "currency": "INR",
        "width_mm": "600",
        "review_required": "true",
    })
    result = normalize_product(row)

    assert result["sku"] == "K-TEST"
    assert result["mrp"] == 12500.0
    assert result["source_page"] == 42
    assert result["width_mm"] == 600.0
    assert result["review_required"] is True
    assert result["finish_name"] is None


def test_empty_and_nan_values_become_none():
    import numpy as np
    import pandas as pd

    row = pd.Series({"sku": np.nan, "product_name": "", "mrp": None})
    result = normalize_product(row)
    assert result["sku"] is None
    assert result["product_name"] is None
    assert result["mrp"] is None

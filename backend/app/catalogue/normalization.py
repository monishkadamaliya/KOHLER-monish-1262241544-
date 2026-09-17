from __future__ import annotations

import math
from typing import Any

import pandas as pd


def _none(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    return None if text == "" or text.lower() in {"nan", "none", "null"} else text


def _float(value: Any) -> float | None:
    value = _none(value)
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None


def _bool(value: Any) -> bool | None:
    value = _none(value)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes", "y"}


def normalize_product(row: pd.Series) -> dict[str, Any]:
    """Normalize one catalogue CSV row without inventing missing facts."""
    text_fields = [
        "sku", "product_name", "collection", "family_id", "product_type", "domain",
        "category", "subcategory", "raw_description", "raw_catalogue_text", "currency",
        "finish_code", "finish_name", "colour_name", "colour_family", "dimension_raw",
        "included_components", "required_components", "order_with_components",
        "compatible_skus", "compatibility_notes", "configuration_type",
        "configuration_options", "orientation", "configuration_notes", "source_type",
        "review_reason",
    ]
    numeric_fields = [
        "mrp", "width_mm", "depth_mm", "height_mm", "diameter_mm", "length_mm",
        "min_width_mm", "max_width_mm", "min_depth_mm", "max_depth_mm", "min_height_mm",
        "extraction_confidence", "source_page",
    ]
    bool_fields = ["tax_included", "is_configurable", "site_dependent", "review_required"]

    result: dict[str, Any] = {}
    for field in text_fields:
        result[field] = _none(row.get(field))
    for field in numeric_fields:
        result[field] = _float(row.get(field))
    if result.get("source_page") is not None:
        result["source_page"] = int(result["source_page"])
    for field in bool_fields:
        result[field] = _bool(row.get(field))
    return result

from __future__ import annotations

from collections import Counter
from typing import Any

REQUIRED_COLUMNS = {"sku", "product_name", "category", "mrp", "currency", "source_page"}


def validate_catalogue_columns(columns: list[str]) -> list[str]:
    return sorted(REQUIRED_COLUMNS - set(columns))


def validate_product(row: dict[str, Any], seen_skus: Counter[str]) -> list[str]:
    errors: list[str] = []
    sku = row.get("sku")
    if not sku:
        errors.append("missing_sku")
    if not row.get("product_name"):
        errors.append("missing_product_name")
    if not row.get("category"):
        errors.append("missing_category")
    if row.get("mrp") is None:
        errors.append("missing_price")
    elif row.get("mrp") < 0:
        errors.append("negative_price")
    if row.get("currency") not in (None, "INR"):
        errors.append("non_inr_currency")
    if row.get("source_page") is None:
        errors.append("missing_source_page")
    if sku and seen_skus[sku] > 0:
        errors.append("duplicate_sku_occurrence")
    return errors

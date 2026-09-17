from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.catalogue.normalization import normalize_product
from app.catalogue.validation import validate_catalogue_columns, validate_product
from app.db.models import Product, ProductRelationship


class IngestionError(ValueError):
    pass


def ingest_catalogue(db: Session, csv_path: str | Path, replace: bool = False) -> dict[str, int]:
    """Import the structured Price Book dataset into PostgreSQL.

    The CSV remains the source artifact; this function normalizes and validates it
    before persistence. Missing facts are never guessed.
    """
    frame = pd.read_csv(csv_path)
    missing = validate_catalogue_columns(frame.columns.tolist())
    if missing:
        raise IngestionError(f"Missing required columns: {', '.join(missing)}")

    if replace:
        db.query(ProductRelationship).delete()
        db.query(Product).delete()
        db.commit()

    seen = Counter()
    inserted = 0
    review = 0
    errors = 0

    for _, source_row in frame.iterrows():
        row = normalize_product(source_row)
        sku = row.get("sku")
        row_errors = validate_product(row, seen)
        errors += len(row_errors)
        review += int(bool(row.get("review_required")))
        if not sku or not row.get("product_name"):
            continue
        seen[sku] += 1
        db.add(Product(**row))
        inserted += 1

    db.commit()
    return {
        "rows_read": len(frame),
        "products_inserted": inserted,
        "review_rows": review,
        "validation_errors": errors,
    }


def ingest_relationships(db: Session, csv_path: str | Path, replace: bool = False) -> int:
    frame = pd.read_csv(csv_path)
    required = {"source_sku", "relationship_type", "target_sku"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise IngestionError(f"Missing relationship columns: {', '.join(missing)}")

    if replace:
        db.query(ProductRelationship).delete()
        db.commit()

    count = 0
    for _, row in frame.iterrows():
        def value(name: str):
            raw = row.get(name)
            return None if pd.isna(raw) else raw

        confidence = value("confidence")
        if isinstance(confidence, str):
            confidence_value = {"high": 1.0, "medium": 0.7, "low": 0.4}.get(confidence.lower())
        else:
            confidence_value = float(confidence) if confidence is not None else None

        source_page = value("source_page")
        db.add(ProductRelationship(
            source_sku=str(value("source_sku")),
            relationship_type=str(value("relationship_type")),
            target_sku=str(value("target_sku")),
            requirement=value("requirement"),
            evidence=value("evidence"),
            source_page=int(source_page) if source_page is not None else None,
            confidence=confidence_value,
        ))
        count += 1

    db.commit()
    return count

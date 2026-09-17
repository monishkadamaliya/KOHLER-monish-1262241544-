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
    path = Path(csv_path)
    frame = pd.read_csv(path)
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
        if row_errors:
            errors += len(row_errors)
        if row.get("review_required"):
            review += 1
        if not sku or not row.get("product_name"):
            continue
        seen[sku] += 1
        db.add(Product(**row))
        inserted += 1

    db.commit()
    return {"rows_read": len(frame), "products_inserted": inserted, "review_rows": review, "validation_errors": errors}


def ingest_relationships(db: Session, csv_path: str | Path) -> int:
    frame = pd.read_csv(csv_path)
    required = {"source_sku", "relationship_type", "target_sku"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise IngestionError(f"Missing relationship columns: {', '.join(missing)}")

    count = 0
    for _, row in frame.iterrows():
        def value(name: str):
            value = row.get(name)
            return None if pd.isna(value) else value

        db.add(ProductRelationship(
            source_sku=str(value("source_sku")),
            relationship_type=str(value("relationship_type")),
            target_sku=str(value("target_sku")),
            requirement=value("relationship_requirement") if "relationship_requirement" in frame.columns else None,
            evidence=value("relationship_evidence") if "relationship_evidence" in frame.columns else None,
            source_page=int(value("relationship_page")) if "relationship_page" in frame.columns and value("relationship_page") is not None else None,
            confidence=float(value("confidence")) if "confidence" in frame.columns and value("confidence") is not None else None,
        ))
        count += 1
    db.commit()
    return count

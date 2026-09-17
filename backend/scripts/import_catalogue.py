from __future__ import annotations

import argparse
from pathlib import Path

from app.catalogue.ingestion import ingest_catalogue, ingest_relationships
from app.db.database import SessionLocal
from app.db.models import Base
from app.db.database import engine

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOGUE = ROOT / "data/catalogue/structured/kohler_catalogue_pass1_v2.csv"
DEFAULT_RELATIONSHIPS = ROOT / "data/catalogue/structured/kohler_relationships_pass1_v2.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Import KOHLER catalogue data into PostgreSQL")
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    parser.add_argument("--relationships", type=Path, default=DEFAULT_RELATIONSHIPS)
    parser.add_argument("--replace", action="store_true", help="Replace existing catalogue rows")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        product_result = ingest_catalogue(db, args.catalogue, replace=args.replace)
        relationship_count = ingest_relationships(db, args.relationships, replace=args.replace)
    finally:
        db.close()

    print({**product_result, "relationships_inserted": relationship_count})


if __name__ == "__main__":
    main()

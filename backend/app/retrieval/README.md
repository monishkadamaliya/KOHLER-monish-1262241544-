# Engine 2 — Catalogue Retrieval Intelligence

Engine 2 turns structured customer intent into a ranked set of KOHLER catalogue candidates.

## Contract

`POST /retrieval/search`

Inputs may include:
- category / domain
- item budget
- style (`Minimalist Modern`, `Classic Luxury`, `Japanese Zen`)
- colour preference
- text search
- approximate maximum width/depth

Each result returns:
- SKU, name, category, price and finish/colour
- retrieval score and component scores
- matched theme and retrieval reasons
- catalogue review flag

## Boundary

Engine 2 performs candidate generation and ranking. It does **not** certify that a product fits the bathroom, satisfies clearance, or is compatible with every other selected product. Those are Engine 3 constraints.

## Retrieval evolution

v1 uses deterministic catalogue-text/style/finish signals so the pipeline is testable without inventing embeddings. The API contract is designed to support a later pgvector semantic layer and Lookbook evidence adapter.

No Lookbook evidence is fabricated when the Lookbook dataset is absent from the repository.

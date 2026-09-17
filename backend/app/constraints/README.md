# Engine 3 — Constraint & Compatibility Engine

The deterministic validation layer between retrieval and optimization.

## Pipeline

`Retrieval → Hard Constraint Filter → Compatibility/Dependency Checks → Spatial Envelope Validation → PASS/FAIL`

## Principles

- Catalogue facts are authoritative.
- LLMs are not used to decide physical validity.
- Budget and catalogue existence are deterministic.
- `requires`, `included_component`, and `order_with` relationships are read from the catalogue relationship graph.
- Missing relationship targets are surfaced as failures rather than guessed.
- Missing physical dimensions produce `REVIEW`, not an invented measurement.
- This v1 validates a product against the supplied room envelope; fixture placement, collision, door swing, clearance buffers, and full multi-product configuration geometry are the next spatial layer.

## Status values

- `PASS`: rule is satisfied.
- `FAIL`: hard rule is violated.
- `REVIEW`: evidence is insufficient for a deterministic decision.

The API returns every rule and its evidence so the frontend can explain why a candidate passed or failed.

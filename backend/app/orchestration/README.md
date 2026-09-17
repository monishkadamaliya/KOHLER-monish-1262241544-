# Engine 7 — End-to-End Design Orchestrator

The orchestrator is the integration layer for the complete KOHLER bathroom-design pipeline.

```text
User request + room dimensions
        ↓
Nova / deterministic intent extraction
        ↓
Catalogue-grounded colour & finish intelligence
        ↓
Per-category catalogue retrieval
        ↓
Bounded configuration generation
        ↓
Deterministic dependency + spatial validation
        ↓
Pareto + weighted multi-objective optimization
        ↓
Top-K validated designs
        ↓
Validated 2D visualization payload
```

## Endpoint

`POST /design/generate`

The endpoint returns:
- structured design intent metadata
- catalogue-grounded finish suggestions
- candidate counts by category
- feasible/Pareto search statistics
- selected SKUs, prices and finishes
- deterministic placements
- total and remaining budget
- objective scores and compatibility evidence
- visualization-ready 2D layout data

## Truth boundary

Nova interprets user language. Retrieval ranks catalogue candidates. The configuration solver is responsible for deterministic budget, dependency and placement checks. The renderer must consume the validated placements and selected SKUs; it must not invent catalogue facts or physical placement.

## Current scope

This is an orchestration layer, not a replacement for the underlying engines. Door/window geometry, installation-specific rules, configurable shower options and larger global spatial optimization remain follow-up hardening work in the constraint/solver layer.

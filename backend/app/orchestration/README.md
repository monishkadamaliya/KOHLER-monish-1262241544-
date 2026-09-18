# Engine 9 — End-to-End Design Orchestrator

Engine 9 is the application-level pipeline that turns a customer request into catalogue-grounded, spatially validated bathroom design alternatives.

```text
User text + confirmed room dimensions
→ intent extraction
→ colour/finish intelligence
→ supplied catalogue candidate pools
→ budget/dependency checks
→ deterministic placement search
→ spatial validation
→ multi-objective scoring + Pareto frontier
→ top-K designs
→ frontend-ready 2D visualization payload
```

## Truth boundaries

- Product identity, price, dimensions and finish are read from the catalogue database.
- Compatibility and physical feasibility are deterministic engine responsibilities.
- Nova interprets user language; it does not establish catalogue truth or physical feasibility.
- The current orchestrator expects candidate SKU pools. Retrieval/image-to-candidate automation is a separate integration step and must not be implied by this endpoint.
- Room dimensions should be confirmed by the user before treating an image-derived estimate as exact.

## Endpoint

`POST /design/generate`

Minimum inputs:
- user text
- room width/depth in millimetres
- budget (request field or explicit text)
- category → SKU candidate pools

Output:
- parsed design intent
- feasible configurations
- product/SKU evidence
- total price
- objective scores
- placements
- frontend-ready 2D plan payload

## Next integration

Connect Engine 2 retrieval to automatically build category candidate pools, then connect Engine 8 image analysis to propose room geometry and fixtures. Keep user confirmation before committing image-estimated dimensions to deterministic spatial validation.

# Engine 4.2 — Feasible Configuration Solver

Engine 4.2 connects configuration search to deterministic dependency and spatial validation.

## Flow

```text
Category candidates
→ bounded configuration generation
→ hard budget / catalogue checks
→ explicit dependency validation
→ deterministic placement search
→ Engine 3.1 spatial validation
→ Pareto frontier
→ weighted ranking
→ top-K feasible design alternatives
```

## Placement solver

- Uses real catalogue width/depth values; no footprint is invented.
- Searches a bounded room grid with 0°/90° rotations.
- Uses deterministic backtracking to avoid fixture-footprint collisions.
- Rejects configurable/site-dependent products from automatic placement when a deterministic footprint is unavailable.
- Sends generated placements through the Engine 3.1 spatial validator before a configuration is marked feasible.

## Compatibility semantics

- `requires` is a hard dependency: the required SKU must be selected and resolvable.
- `compatible_with` contributes explicit compatibility evidence when the related SKU is selected.
- `included_component` is not double-counted as a separate purchase requirement.
- `order_with` is not silently converted into a hard requirement.
- Absence of a relationship is not treated as proof of incompatibility.

## Endpoint

`POST /optimize/configuration`

The request supplies category → SKU candidates, budget/style/colour/room constraints, and bounded search settings. The response contains feasible SKU configurations, deterministic placements, total price, objective scores, Pareto status, and compatibility evidence.

## Guardrails

- No SKU is invented.
- No missing catalogue fact is inferred.
- Missing or unresolved required evidence causes rejection rather than an assumed PASS.
- Search and placement are bounded to control computation.
- Generated visualizations must consume these validated SKU/placement results; the image generator must not choose products or geometry.

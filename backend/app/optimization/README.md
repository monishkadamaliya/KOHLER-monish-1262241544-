# Engine 4 — Multi-Objective Optimization

Engine 4 ranks catalogue candidates after deterministic hard constraints have removed products that cannot be considered feasible.

## Pipeline

```text
Candidate SKUs
  -> hard budget check
  -> dependency evidence check
  -> deterministic footprint check
  -> objective scoring
  -> weighted ranking
  -> top-K feasible designs
```

## Objectives

The engine exposes configurable weights for:

- spatial feasibility
- compatibility
- budget efficiency
- style match
- colour match
- space efficiency
- functionality evidence
- sustainability evidence

Weights are normalized at runtime, so the API accepts any non-negative relative weighting.

## Important boundary

Engine 4 does not invent catalogue facts. It uses catalogue records and the existing deterministic retrieval/constraint evidence. Sustainability receives a positive score only when explicit catalogue text contains documented evidence such as water-saving, water-efficient, recycled, or low-flow terminology.

The current endpoint ranks **candidate SKUs**. Full multi-fixture configuration search, automatic placement generation, Pareto-front generation, and OR-Tools CP-SAT optimization are the next optimization iteration; they should consume Engine 3.1 spatial validation rather than bypass it.

## API

`POST /optimize`

Example request:

```json
{
  "candidate_skus": ["K-XXXX", "K-YYYY"],
  "budget": 100000,
  "style": "Japanese Zen",
  "colour_preference": "natural",
  "room_width_mm": 2400,
  "room_depth_mm": 1800,
  "top_k": 5
}
```

A product is never promoted into the feasible list merely because it has a high aesthetic score: hard budget, dependency, and available-footprint checks run first.

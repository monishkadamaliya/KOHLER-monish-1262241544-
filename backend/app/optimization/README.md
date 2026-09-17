# Engine 4.1 — Configuration Search & Pareto Optimization

Engine 4.1 searches complete bathroom configurations rather than scoring isolated products.

## Flow

```text
Category candidates
→ bounded configuration generation
→ hard budget / catalogue checks
→ configuration objective evaluation
→ Pareto frontier
→ weighted ranking
→ top-K design alternatives
```

## Hard constraints

A configuration is discarded when:
- a SKU is absent from the authoritative catalogue
- a required price is missing
- total catalogue price exceeds the requested budget

Spatial collision and detailed compatibility remain deterministic Engine 3/3.1 responsibilities and must be invoked before a configuration is presented as physically valid.

## Objectives

- spatial feasibility
- compatibility evidence
- budget efficiency
- style match
- colour match
- space efficiency
- functionality
- documented sustainability evidence

## Pareto reasoning

A configuration is retained on the Pareto frontier when no other evaluated configuration is at least as good across every objective and strictly better on one. This preserves meaningful trade-offs instead of forcing one hidden definition of “best”.

## Guardrails

- No SKU is invented.
- No missing catalogue fact is inferred.
- Missing evidence is not converted into compatibility.
- Search is bounded to avoid uncontrolled Cartesian-product growth.
- Final physical validity must come from Engine 3/3.1.

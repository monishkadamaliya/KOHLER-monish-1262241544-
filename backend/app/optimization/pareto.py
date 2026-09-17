from __future__ import annotations


def dominates(a: dict[str, float], b: dict[str, float], objectives: list[str]) -> bool:
    """Return True when a is at least as good on every objective and strictly better on one."""
    values_a = [a[key] for key in objectives]
    values_b = [b[key] for key in objectives]
    return all(x >= y for x, y in zip(values_a, values_b)) and any(x > y for x, y in zip(values_a, values_b))


def pareto_frontier(items: list[tuple[object, dict[str, float]]], objectives: list[str]) -> list[tuple[object, dict[str, float]]]:
    frontier: list[tuple[object, dict[str, float]]] = []
    for candidate, scores in items:
        if any(dominates(other_scores, scores, objectives) for _, other_scores in items):
            continue
        frontier.append((candidate, scores))
    return frontier

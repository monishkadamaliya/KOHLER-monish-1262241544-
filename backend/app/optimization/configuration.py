from __future__ import annotations

from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Configuration:
    skus: tuple[str, ...]


def generate_configurations(category_candidates: dict[str, list[str]], max_configurations: int = 5000) -> list[Configuration]:
    """Generate bounded Cartesian-product configurations from category candidates."""
    categories = [category for category, skus in category_candidates.items() if skus]
    if not categories:
        return []

    pools = [category_candidates[category] for category in categories]
    configurations: list[Configuration] = []
    for combination in product(*pools):
        configurations.append(Configuration(skus=tuple(combination)))
        if len(configurations) >= max_configurations:
            break
    return configurations

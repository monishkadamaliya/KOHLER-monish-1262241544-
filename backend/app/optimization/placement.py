from __future__ import annotations

from dataclasses import dataclass

from shapely.geometry import Polygon

from app.constraints.geometry import RectangleSpec, rectangle_polygon, room_polygon


@dataclass(frozen=True)
class Placement:
    sku: str
    x_mm: float
    y_mm: float
    rotation_deg: float
    width_mm: float
    depth_mm: float


def _dimensions(product) -> tuple[float | None, float | None]:
    if product.is_configurable or product.site_dependent:
        return None, None
    return product.width_mm or product.max_width_mm, product.depth_mm or product.max_depth_mm


def generate_placements(
    products,
    room_width_mm: float,
    room_depth_mm: float,
    grid_mm: float = 100.0,
    max_nodes: int = 2500,
) -> list[Placement] | None:
    """Bounded deterministic backtracking placement search.

    The solver searches a coarse room grid and 0/90 degree rotations. It never
    invents a footprint: products without explicit deterministic dimensions are
    rejected from automatic placement and must go through site/configuration review.
    """
    room = room_polygon(room_width_mm, room_depth_mm)
    placed: list[tuple[Placement, Polygon]] = []
    nodes = 0

    dimensions = []
    for product in products:
        width, depth = _dimensions(product)
        if width is None or depth is None:
            return None
        dimensions.append((product, width, depth))

    # Place larger footprints first to reduce greedy dead ends while retaining
    # deterministic behaviour for equal-sized products.
    dimensions.sort(key=lambda item: item[1] * item[2], reverse=True)

    def search(index: int) -> bool:
        nonlocal nodes
        if index == len(dimensions):
            return True
        if nodes >= max_nodes:
            return False

        product, width, depth = dimensions[index]
        for rotation in (0.0, 90.0):
            rw, rd = (width, depth) if rotation == 0 else (depth, width)
            max_x = room_width_mm - rw
            max_y = room_depth_mm - rd
            if max_x < 0 or max_y < 0:
                continue

            x = 0.0
            while x <= max_x + 1e-9:
                y = 0.0
                while y <= max_y + 1e-9:
                    nodes += 1
                    if nodes > max_nodes:
                        return False
                    polygon = rectangle_polygon(RectangleSpec(width, depth, x, y, rotation))
                    if room.contains(polygon) and all(polygon.intersection(other).area <= 1e-9 for _, other in placed):
                        placement = Placement(product.sku, x, y, rotation, rw, rd)
                        placed.append((placement, polygon))
                        if search(index + 1):
                            return True
                        placed.pop()
                    y += grid_mm
                x += grid_mm
        return False

    return [item for item, _ in placed] if search(0) else None

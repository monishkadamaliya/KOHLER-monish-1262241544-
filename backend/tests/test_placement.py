from types import SimpleNamespace

from app.optimization.placement import generate_placements


def product(sku: str, width: float, depth: float):
    return SimpleNamespace(
        sku=sku,
        width_mm=width,
        depth_mm=depth,
        max_width_mm=None,
        max_depth_mm=None,
        is_configurable=False,
        site_dependent=False,
    )


def test_generates_non_colliding_room_placements():
    placements = generate_placements(
        [product("A", 600, 400), product("B", 500, 400)],
        room_width_mm=2000,
        room_depth_mm=1500,
        grid_mm=100,
    )

    assert placements is not None
    assert len(placements) == 2
    assert {item.sku for item in placements} == {"A", "B"}


def test_rejects_product_larger_than_room():
    placements = generate_placements(
        [product("A", 2500, 400)],
        room_width_mm=2000,
        room_depth_mm=1500,
    )

    assert placements is None


def test_requires_deterministic_footprint():
    configurable = SimpleNamespace(
        sku="CFG",
        width_mm=None,
        depth_mm=None,
        max_width_mm=None,
        max_depth_mm=None,
        is_configurable=True,
        site_dependent=False,
    )

    assert generate_placements([configurable], 2000, 1500) is None

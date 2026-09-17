from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

from shapely.affinity import rotate
from shapely.geometry import Polygon, box
from shapely.ops import unary_union


@dataclass(frozen=True)
class RectangleSpec:
    width_mm: float
    depth_mm: float
    x_mm: float
    y_mm: float
    rotation_deg: float = 0.0


def room_polygon(width_mm: float, depth_mm: float) -> Polygon:
    """Create a room coordinate system with origin at the lower-left corner."""
    return box(0, 0, width_mm, depth_mm)


def rectangle_polygon(spec: RectangleSpec) -> Polygon:
    shape = box(
        spec.x_mm - spec.width_mm / 2,
        spec.y_mm - spec.depth_mm / 2,
        spec.x_mm + spec.width_mm / 2,
        spec.y_mm + spec.depth_mm / 2,
    )
    if spec.rotation_deg:
        shape = rotate(shape, spec.rotation_deg, origin=(spec.x_mm, spec.y_mm))
    return shape


def clearance_polygon(footprint: Polygon, clearance_mm: float) -> Polygon:
    return footprint.buffer(clearance_mm)


def validate_room_envelope(footprint: Polygon, room: Polygon) -> tuple[bool, str]:
    if not room.contains(footprint):
        return False, "Fixture footprint extends outside the room boundary."
    return True, "Fixture footprint is contained within the room boundary."


def validate_collision(footprint: Polygon, others: list[Polygon]) -> tuple[bool, str]:
    for other in others:
        if footprint.intersection(other).area > 0:
            return False, "Fixture footprint collides with another fixture."
    return True, "No fixture footprint collision detected."


def validate_clearance(footprint: Polygon, others: list[Polygon], clearance_mm: float) -> tuple[bool, str]:
    if clearance_mm <= 0:
        return True, "No additional clearance buffer requested."
    expanded = clearance_polygon(footprint, clearance_mm)
    for other in others:
        if expanded.intersection(other).area > 0:
            return False, f"Required clearance of {clearance_mm:g} mm is not available."
    return True, f"Required clearance of {clearance_mm:g} mm is available."


def door_swing_polygon(
    hinge_x_mm: float,
    hinge_y_mm: float,
    width_mm: float,
    swing_deg: float,
    direction_deg: float = 0.0,
) -> Polygon:
    """Approximate an inward door swing as the swept polygon of a rectangular door."""
    segments = []
    for i in range(12):
        angle = direction_deg + swing_deg * i / 11
        dx = width_mm * cos(radians(angle))
        dy = width_mm * sin(radians(angle))
        segments.append(box(hinge_x_mm, hinge_y_mm, hinge_x_mm + dx, hinge_y_mm + dy))
    return unary_union(segments)

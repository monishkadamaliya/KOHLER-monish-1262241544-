from __future__ import annotations

from sqlalchemy.orm import Session
from shapely.geometry import box

from app.catalogue.repository import get_product
from app.constraints.geometry import RectangleSpec, rectangle_polygon, room_polygon
from app.constraints.spatial_schemas import (
    SpatialCheck,
    SpatialFixtureResult,
    SpatialValidationRequest,
    SpatialValidationResponse,
)


def _fixture_dimensions(product) -> tuple[float | None, float | None]:
    """Return only explicit catalogue dimensions; configurable/site-dependent sizes stay REVIEW."""
    if product.is_configurable or product.site_dependent:
        return None, None
    width = product.width_mm or product.max_width_mm
    depth = product.depth_mm or product.max_depth_mm
    return width, depth


def validate_spatial(db: Session, request: SpatialValidationRequest) -> SpatialValidationResponse:
    room = room_polygon(request.room_width_mm, request.room_depth_mm)
    placements = []
    results: list[SpatialFixtureResult] = []

    for fixture in request.fixtures:
        product = get_product(db, fixture.sku)
        if product is None:
            results.append(SpatialFixtureResult(
                sku=fixture.sku,
                valid=False,
                checks=[SpatialCheck(rule="catalogue_exists", status="FAIL", message="SKU does not exist in the authoritative catalogue.")],
            ))
            continue

        width, depth = _fixture_dimensions(product)
        if width is None or depth is None:
            results.append(SpatialFixtureResult(
                sku=fixture.sku,
                valid=False,
                checks=[SpatialCheck(rule="footprint", status="REVIEW", message="A deterministic footprint cannot be established from the catalogue record; configurable or site-dependent geometry requires configuration/site confirmation.")],
            ))
            continue

        footprint = rectangle_polygon(RectangleSpec(width, depth, fixture.x_mm, fixture.y_mm, fixture.rotation_deg))
        checks: list[SpatialCheck] = []

        if room.contains(footprint):
            checks.append(SpatialCheck(rule="room_boundary", status="PASS", message="Fixture footprint is contained within the room boundary."))
        else:
            checks.append(SpatialCheck(rule="room_boundary", status="FAIL", message="Fixture footprint extends outside the room boundary."))

        collision = False
        clearance_failure = False
        for other_sku, other in placements:
            if footprint.intersection(other).area > 0:
                collision = True
                checks.append(SpatialCheck(rule="fixture_collision", status="FAIL", message=f"Footprint collides with fixture {other_sku}."))
            if fixture.clearance_mm > 0 and footprint.buffer(fixture.clearance_mm).intersection(other).area > 0:
                clearance_failure = True
                checks.append(SpatialCheck(rule="clearance", status="FAIL", message=f"Required clearance of {fixture.clearance_mm:g} mm is not available near fixture {other_sku}."))

        if not collision:
            checks.append(SpatialCheck(rule="fixture_collision", status="PASS", message="No fixture footprint collision detected."))
        if fixture.clearance_mm <= 0:
            checks.append(SpatialCheck(rule="clearance", status="PASS", message="No additional fixture clearance supplied."))
        elif not clearance_failure:
            checks.append(SpatialCheck(rule="clearance", status="PASS", message=f"Required clearance of {fixture.clearance_mm:g} mm is available."))

        opening_failure = False
        for opening in request.openings:
            opening_shape = box(opening.x_mm, opening.y_mm, opening.x_mm + opening.width_mm, opening.y_mm + opening.depth_mm)
            if footprint.intersection(opening_shape).area > 0:
                opening_failure = True
                checks.append(SpatialCheck(rule="opening_collision", status="FAIL", message=f"Fixture intersects {opening.kind} opening."))
        if not opening_failure:
            checks.append(SpatialCheck(rule="opening_collision", status="PASS", message="No opening collision detected."))

        installation_text = " ".join(v.lower() for v in [product.raw_description, product.raw_catalogue_text, product.configuration_notes] if v)
        if "wall-hung" in installation_text or "wall hung" in installation_text:
            installation = "wall-mounted product; wall structure and carrier requirements require site verification"
            status = "REVIEW"
        else:
            installation = "No explicit wall-mounted requirement detected in the stored catalogue text."
            status = "PASS"
        checks.append(SpatialCheck(rule="installation", status=status, message=installation))

        valid = all(check.status == "PASS" for check in checks)
        results.append(SpatialFixtureResult(sku=fixture.sku, valid=valid, checks=checks))
        placements.append((fixture.sku, footprint))

    return SpatialValidationResponse(valid=all(item.valid for item in results), results=results)

from __future__ import annotations

from sqlalchemy.orm import Session
from shapely.geometry import box

from app.catalogue.repository import get_product
from app.constraints.geometry import RectangleSpec, door_swing_polygon, rectangle_polygon, room_polygon
from app.constraints.spatial_schemas import SpatialCheck, SpatialFixtureResult, SpatialValidationRequest, SpatialValidationResponse


def _fixture_dimensions(product) -> tuple[float | None, float | None]:
    if product.is_configurable or product.site_dependent:
        return None, None
    return product.width_mm or product.max_width_mm, product.depth_mm or product.max_depth_mm


def validate_spatial(db: Session, request: SpatialValidationRequest) -> SpatialValidationResponse:
    room = room_polygon(request.room_width_mm, request.room_depth_mm)
    placements: list[tuple[str, object]] = []
    results: list[SpatialFixtureResult] = []
    opening_shapes = []

    for opening in request.openings:
        base = box(opening.x_mm, opening.y_mm, opening.x_mm + opening.width_mm, opening.y_mm + opening.depth_mm)
        if opening.kind.lower() == "door":
            if opening.hinge_x_mm is None or opening.hinge_y_mm is None or opening.swing_deg <= 0:
                opening_shapes.append((opening.kind, base, "REVIEW", "Door swing requires hinge coordinates and a positive swing angle."))
            else:
                opening_shapes.append((opening.kind, door_swing_polygon(opening.hinge_x_mm, opening.hinge_y_mm, opening.width_mm, opening.swing_deg, opening.direction_deg), "PASS", "Door swing swept area modeled deterministically."))
        else:
            opening_shapes.append((opening.kind, base, "PASS", f"{opening.kind} opening envelope modeled from supplied dimensions."))

    for fixture in request.fixtures:
        product = get_product(db, fixture.sku)
        if product is None:
            results.append(SpatialFixtureResult(sku=fixture.sku, valid=False, checks=[SpatialCheck(rule="catalogue_exists", status="FAIL", message="SKU does not exist in the authoritative catalogue.")]))
            continue

        width, depth = _fixture_dimensions(product)
        if width is None or depth is None:
            results.append(SpatialFixtureResult(sku=fixture.sku, valid=False, checks=[SpatialCheck(rule="footprint", status="REVIEW", message="Deterministic footprint unavailable because the catalogue record is configurable/site-dependent or lacks explicit width/depth.")]))
            continue

        footprint = rectangle_polygon(RectangleSpec(width, depth, fixture.x_mm, fixture.y_mm, fixture.rotation_deg))
        checks: list[SpatialCheck] = []
        inside = room.contains(footprint)
        checks.append(SpatialCheck(rule="room_boundary", status="PASS" if inside else "FAIL", message="Fixture footprint is contained within the room boundary." if inside else "Fixture footprint extends outside the room boundary."))

        collisions = [other_sku for other_sku, other in placements if footprint.intersection(other).area > 0]
        checks.append(SpatialCheck(rule="fixture_collision", status="FAIL" if collisions else "PASS", message=f"Footprint collides with: {', '.join(collisions)}." if collisions else "No fixture footprint collision detected.", evidence=collisions))

        if fixture.clearance_mm > 0:
            clearance_hits = [other_sku for other_sku, other in placements if footprint.buffer(fixture.clearance_mm).intersection(other).area > 0]
            checks.append(SpatialCheck(rule="clearance", status="FAIL" if clearance_hits else "PASS", message=f"Required clearance of {fixture.clearance_mm:g} mm is not available near: {', '.join(clearance_hits)}." if clearance_hits else f"Required clearance of {fixture.clearance_mm:g} mm is available."))
        else:
            checks.append(SpatialCheck(rule="clearance", status="PASS", message="No additional fixture clearance supplied."))

        opening_failures = []
        opening_reviews = []
        for kind, shape, status, message in opening_shapes:
            if status == "REVIEW":
                opening_reviews.append(message)
            elif footprint.intersection(shape).area > 0:
                opening_failures.append(kind)
        if opening_failures:
            checks.append(SpatialCheck(rule="opening_collision", status="FAIL", message=f"Fixture intersects: {', '.join(opening_failures)}."))
        elif opening_reviews:
            checks.append(SpatialCheck(rule="opening_collision", status="REVIEW", message="Opening geometry is incomplete.", evidence=opening_reviews))
        else:
            checks.append(SpatialCheck(rule="opening_collision", status="PASS", message="No opening collision detected."))

        text = " ".join(v.lower() for v in [product.product_type, product.raw_description, product.raw_catalogue_text, product.configuration_notes] if v)
        wall_mounted = "wall-hung" in text or "wall hung" in text or "wall-mounted" in text or "wall mounted" in text
        checks.append(SpatialCheck(rule="installation", status="REVIEW" if wall_mounted else "PASS", message="Wall-mounted product detected; wall structure/carrier and site installation requirements require verification." if wall_mounted else "No explicit wall-mounted requirement detected in stored catalogue text."))

        valid = all(check.status == "PASS" for check in checks)
        results.append(SpatialFixtureResult(sku=fixture.sku, valid=valid, checks=checks))
        placements.append((fixture.sku, footprint))

    return SpatialValidationResponse(valid=all(item.valid for item in results), results=results)

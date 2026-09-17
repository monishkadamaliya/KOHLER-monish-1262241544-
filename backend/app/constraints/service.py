from __future__ import annotations

from sqlalchemy.orm import Session

from app.catalogue.repository import get_product, get_relationships
from app.constraints.schemas import ConstraintCheck, ConstraintRequest, ConstraintResponse, ConstraintResult


DEPENDENCY_TYPES = {"requires", "included_component", "order_with"}


def _check_dimensions(product, space) -> ConstraintCheck:
    if space is None:
        return ConstraintCheck(rule="dimensions", status="PASS", message="No room dimensions supplied; spatial validation deferred.")

    width = product.width_mm or product.max_width_mm
    depth = product.depth_mm or product.max_depth_mm
    evidence = []
    failures = []

    if width is not None:
        evidence.append(f"width={width:g}mm <= room width={space.width_mm:g}mm")
        if width > space.width_mm:
            failures.append("width exceeds room width")
    if depth is not None:
        evidence.append(f"depth={depth:g}mm <= room depth={space.depth_mm:g}mm")
        if depth > space.depth_mm:
            failures.append("depth exceeds room depth")

    if failures:
        return ConstraintCheck(rule="dimensions", status="FAIL", message="; ".join(failures), evidence=evidence)
    if not evidence:
        return ConstraintCheck(rule="dimensions", status="REVIEW", message="No comparable catalogue footprint is available.")
    return ConstraintCheck(rule="dimensions", status="PASS", message="Catalogue footprint fits the supplied room envelope.", evidence=evidence)


def _check_dependencies(db: Session, sku: str) -> tuple[ConstraintCheck, list[str]]:
    relationships = [r for r in get_relationships(db, sku) if r.relationship_type in DEPENDENCY_TYPES]
    missing = []
    evidence = []
    for rel in relationships:
        target = get_product(db, rel.target_sku)
        if target is None:
            missing.append(rel.target_sku)
            evidence.append(f"{rel.relationship_type}: {rel.target_sku} not present as a master product")
        else:
            evidence.append(f"{rel.relationship_type}: {rel.target_sku}")

    if missing:
        return ConstraintCheck(rule="dependencies", status="FAIL", message="One or more referenced dependencies are unavailable in the master catalogue.", evidence=evidence), missing
    if relationships:
        return ConstraintCheck(rule="dependencies", status="PASS", message="All referenced catalogue dependencies resolve to known products.", evidence=evidence), []
    return ConstraintCheck(rule="dependencies", status="PASS", message="No required/order-with dependency recorded for this SKU."), []


def _check_budget(product, budget: float | None) -> ConstraintCheck:
    if budget is None:
        return ConstraintCheck(rule="budget", status="PASS", message="No budget constraint supplied.")
    if product.mrp is None:
        return ConstraintCheck(rule="budget", status="REVIEW", message="Product has no MRP; budget validity cannot be established.")
    if product.mrp <= budget:
        return ConstraintCheck(rule="budget", status="PASS", message=f"MRP ₹{product.mrp:,.0f} is within budget ₹{budget:,.0f}.")
    return ConstraintCheck(rule="budget", status="FAIL", message=f"MRP ₹{product.mrp:,.0f} exceeds budget ₹{budget:,.0f}.")


def validate_candidates(db: Session, request: ConstraintRequest) -> ConstraintResponse:
    results: list[ConstraintResult] = []

    for sku in dict.fromkeys(request.skus):
        product = get_product(db, sku)
        if product is None:
            results.append(ConstraintResult(
                sku=sku,
                valid=False,
                checks=[ConstraintCheck(rule="catalogue_exists", status="FAIL", message="SKU does not exist in the authoritative catalogue.")],
            ))
            continue

        budget = _check_budget(product, request.budget)
        dimensions = _check_dimensions(product, request.space)
        dependencies, missing = _check_dependencies(db, sku)

        checks = [budget, dimensions, dependencies]
        if request.required_categories:
            if product.category in request.required_categories:
                checks.append(ConstraintCheck(rule="category", status="PASS", message=f"Category '{product.category}' satisfies the requested category set."))
            else:
                checks.append(ConstraintCheck(rule="category", status="FAIL", message=f"Category '{product.category}' is not in the requested category set."))

        valid = all(check.status == "PASS" for check in checks)
        results.append(ConstraintResult(
            sku=sku,
            valid=valid,
            total_price=product.mrp,
            checks=checks,
            missing_dependencies=missing,
        ))

    return ConstraintResponse(valid=all(result.valid for result in results), results=results)

from app.orchestration.schemas import DesignGenerateRequest
from app.orchestration.service import DesignOrchestrator


def test_design_request_requires_real_room_dimensions_and_categories():
    request = DesignGenerateRequest(
        text="Japanese Zen bathroom with natural finishes",
        room_width_mm=2400,
        room_depth_mm=1800,
        budget_inr=250000,
        required_categories=["toilet", "basin", "faucet"],
    )
    assert request.room_width_mm == 2400
    assert request.room_depth_mm == 1800
    assert request.required_categories == ["toilet", "basin", "faucet"]


def test_visualization_payload_contains_only_validated_design_coordinates():
    request = DesignGenerateRequest(
        text="Minimalist bathroom",
        room_width_mm=2400,
        room_depth_mm=1800,
        budget_inr=200000,
        required_categories=["basin"],
    )
    payload = DesignOrchestrator._visualization_payload(request, [])
    assert payload["type"] == "validated_2d_layout"
    assert payload["room"] == {"width_mm": 2400.0, "depth_mm": 1800.0}
    assert payload["designs"] == []

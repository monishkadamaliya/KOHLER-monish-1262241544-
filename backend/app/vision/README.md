# Engine 8 — Bathroom Image → Spatial Understanding

Converts an uploaded bathroom image into an uncertain `BathroomSpaceEstimate` that can feed the deterministic geometry/optimization layer.

## Flow

`Bathroom image → Amazon Nova vision → structured observations → user confirmation → deterministic geometry`

## Guardrails

- Nova may identify visible fixtures/openings and estimate dimensions.
- Image-derived dimensions are explicitly marked as estimates.
- Missing/uncertain dimensions remain unknown rather than being invented.
- Vision never selects KOHLER SKUs, prices, compatibility, or final placement.
- The deterministic geometry engine remains the physical feasibility authority.
- The endpoint rejects unsupported formats and limits uploads to 10 MB.

## API

`POST /vision/analyze` with a JPEG, PNG, WEBP, or GIF image.

Set `NOVA_ENABLED=true` to enable Bedrock inference. The model defaults to `amazon.nova-lite-v1:0` and can be overridden with `NOVA_VISION_MODEL_ID`.

When Nova is unavailable, the service returns a review state requiring user-confirmed dimensions instead of pretending the image was measured successfully.

## Production note

Image-derived geometry should be treated as planning assistance only. A final purchase/installation workflow should require confirmed site dimensions and professional verification where applicable.

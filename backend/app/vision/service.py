from __future__ import annotations

import base64
import json
import os

from app.vision.prompts import VISION_SYSTEM_PROMPT, VISION_USER_PROMPT
from app.vision.schemas import BathroomSpaceEstimate, VisionAnalyzeResponse


class BathroomVisionService:
    """Turn a bathroom image into uncertain spatial observations.

    Vision proposes observations; deterministic geometry and user-confirmed dimensions
    remain authoritative for physical feasibility.
    """

    def analyze(self, image_bytes: bytes, image_format: str) -> VisionAnalyzeResponse:
        if os.getenv("NOVA_ENABLED", "false").lower() != "true":
            return self._fallback()

        try:
            import boto3

            client = boto3.client(
                "bedrock-runtime",
                region_name=os.getenv("AWS_REGION", "ap-south-1"),
            )
            encoded = base64.b64encode(image_bytes).decode("utf-8")
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "image": {
                                    "format": image_format,
                                    "source": {"bytes": encoded},
                                }
                            },
                            {"text": VISION_USER_PROMPT},
                        ],
                    }
                ],
                "system": [{"text": VISION_SYSTEM_PROMPT}],
                "inferenceConfig": {"maxTokens": 1800, "temperature": 0.0},
            }
            response = client.invoke_model(
                modelId=os.getenv("NOVA_VISION_MODEL_ID", os.getenv("NOVA_MODEL_ID", "amazon.nova-lite-v1:0")),
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            payload = json.loads(response["body"].read())
            text = next(
                item["text"]
                for item in payload["output"]["message"]["content"]
                if "text" in item
            )
            parsed = json.loads(text)
            space = BathroomSpaceEstimate.model_validate(parsed)
            return VisionAnalyzeResponse(source="amazon_nova_vision", space=space, raw_model_output_used=True)
        except Exception as exc:
            fallback = self._fallback().space
            fallback.warnings.append(f"Vision inference unavailable or invalid; manual dimensions are required. ({type(exc).__name__})")
            return VisionAnalyzeResponse(source="deterministic_review_fallback", space=fallback, raw_model_output_used=False)

    @staticmethod
    def _fallback() -> VisionAnalyzeResponse:
        return VisionAnalyzeResponse(
            source="deterministic_review_fallback",
            space=BathroomSpaceEstimate(
                measurement_status="requires_user_confirmation",
                confidence=0.0,
                assumptions=["No physical dimensions are inferred without successful vision analysis."],
                warnings=["Image-only geometry must not be used for purchase or installation decisions without user/site confirmation."],
            ),
            raw_model_output_used=False,
        )

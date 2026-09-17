from __future__ import annotations

import json
import os
import re

from app.intelligence.prompts import SYSTEM_PROMPT
from app.intelligence.schemas import DesignIntent, IntentParseRequest, IntentParseResponse


STYLE_TERMS = {
    "Minimalist Modern": ("minimal", "minimalist", "modern", "contemporary"),
    "Classic Luxury": ("classic", "luxury", "luxurious", "heritage", "traditional"),
    "Japanese Zen": ("japanese", "zen", "calm", "serene", "natural", "organic"),
}
CATEGORY_TERMS = {
    "toilet": ("toilet", "wc"),
    "basin": ("basin", "washbasin", "wash basin", "sink"),
    "faucet": ("faucet", "tap"),
    "shower": ("shower", "showering"),
    "vanity": ("vanity",),
    "bathtub": ("bathtub", "bath tub", "tub"),
    "mirror": ("mirror",),
}


def _local_parse(request: IntentParseRequest) -> DesignIntent:
    text = request.text.lower()
    styles = [style for style, terms in STYLE_TERMS.items() if any(term in text for term in terms)]
    categories = [category for category, terms in CATEGORY_TERMS.items() if any(term in text for term in terms)]
    budget = request.known_budget_inr
    if budget is None:
        match = re.search(r"(?:₹|rs\.?|inr\s*)\s*([0-9][0-9,]*(?:\.\d+)?)", request.text, re.I)
        if match:
            budget = float(match.group(1).replace(",", ""))

    clarification = []
    if not styles:
        clarification.append("Which design style should be prioritized: Minimalist Modern, Classic Luxury, or Japanese Zen?")
    if budget is None:
        clarification.append("What is your approximate budget in INR?")
    if not categories:
        clarification.append("Which bathroom product categories are required?")

    return DesignIntent(
        style=styles[0] if styles else None,
        colour_preference=next((term for term in ("black", "gold", "rose gold", "chrome", "natural", "white") if term in text), None),
        budget_inr=budget,
        required_categories=categories,
        confidence=0.75 if styles or categories or budget else 0.35,
        clarification_required=clarification,
    )


def _nova_parse(request: IntentParseRequest) -> DesignIntent | None:
    """Optional Amazon Bedrock/Nova adapter. No network call is made unless explicitly configured."""
    if os.getenv("NOVA_ENABLED", "false").lower() != "true":
        return None
    try:
        import boto3

        client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "ap-south-1"))
        body = {
            "messages": [{"role": "user", "content": [{"text": request.text}]}],
            "system": [{"text": SYSTEM_PROMPT}],
            "inferenceConfig": {"maxTokens": 700, "temperature": 0.0},
        }
        response = client.invoke_model(
            modelId=os.getenv("NOVA_MODEL_ID", "amazon.nova-lite-v1:0"),
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        payload = json.loads(response["body"].read())
        text = payload["output"]["message"]["content"][0]["text"]
        return DesignIntent.model_validate_json(text)
    except Exception:
        return None


class IntentService:
    def parse(self, request: IntentParseRequest) -> IntentParseResponse:
        intent = _nova_parse(request)
        warnings: list[str] = []
        source = "amazon_nova" if intent else "deterministic_fallback"
        if intent is None:
            intent = _local_parse(request)
            warnings.append("Nova was not used; deterministic fallback parsing was applied.")
        return IntentParseResponse(intent=intent, source=source, warnings=warnings)

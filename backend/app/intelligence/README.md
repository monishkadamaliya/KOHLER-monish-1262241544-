# Engine 5 — Amazon Nova Intelligence Layer

Engine 5 converts natural-language customer intent into a strict `DesignIntent` object.

```text
Customer language
→ Amazon Nova (when enabled)
→ structured DesignIntent
→ retrieval / constraints / optimization
```

## Boundary

Nova may interpret language such as style, colour preference, functional preference and stated budget. It must not decide catalogue truth, physical fit, compatibility, SKU validity, or final placement.

Those decisions remain deterministic and catalogue-grounded.

## Guardrails

- Structured schema output
- Temperature 0 when calling Nova
- No invented SKU/price/dimension/compatibility
- Physical validation outside the model
- Deterministic fallback when Nova is unavailable
- AWS configuration comes from environment variables; no credentials are stored in source

Set `NOVA_ENABLED=true` and configure AWS credentials/model access to enable the Bedrock adapter. Otherwise the service remains locally testable without AWS.

# Engine 6 — Colour & Finish Intelligence

Engine 6 maps customer style/colour intent to finishes that actually exist in the structured KOHLER catalogue.

```text
Style / colour intent
→ catalogue finish inventory
→ deterministic finish-family matching
→ ranked finish candidates
→ product optimizer
```

## Design rule

The engine distinguishes **colour family** from **KOHLER finish**. It never invents a finish code or claims that a generated palette is an official KOHLER recommendation.

The Project Lookbook and external design references can later provide soft design evidence, while the Price Book remains the source of truth for sellable SKUs, prices and finish availability.

## Current scope

- Bathroom and kitchen domain filtering
- Catalogue finish inventory
- Style-aware finish matching
- Colour-family matching
- Finish availability count
- Explicit warnings where design harmony/compatibility is not yet proven

## Next integration

The next version will combine multiple finishes into a palette and pass the resulting finish constraints into configuration optimization so every selected SKU has a catalogue-supported finish.

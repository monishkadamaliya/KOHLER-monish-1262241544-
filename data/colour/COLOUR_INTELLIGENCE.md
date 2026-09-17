# Colour Intelligence — KOHLER AI Bathroom Design Engine

> **Provenance disclaimer (read first):** the source (figma.com/resource-library/color-combinations)
> names and describes 100 combinations in page text, but its actual swatches are rendered as
> images — they were not extractable as text/hex data. Every hex value in
> `palette_dataset.json` is therefore **AI-derived from the named color family** Figma used
> (e.g. "sage", "terracotta"), not read directly from the source. `source_palette_name` and
> `harmony_type`/mood language are source-derived (from the page's own text). Re-verify hex
> values against real Figma swatches or your own export before treating them as final. This
> is exactly the source/AI-derived distinction Section 7 requires — flagging it here rather
> than silently presenting AI-derived colors as sourced.

This dataset extracts **design intelligence**, not a copy of the source's palette library.
The Figma page's own combinations are never treated as a KOHLER finish inventory — see the
separation diagram in Section 6.

---

## 1. Colour Design Principles

Summarized from the harmony types actually present in source combinations relevant to
bathroom/kitchen design (in the assistant's own words, not the source's):

- **Monochromatic** — a single hue stepped from near-white to near-black. Lowest risk for
  wet-area surfaces (tile, sanitaryware) since every shade guarantees harmony with every
  other. Best for minimalist and calm environments; used in `minimal_mono_004`, `zen_water_002`.
- **Analogous** — hues adjacent on the wheel (e.g. sand → sage → soft blue). Reads as natural
  and unforced, which is why it dominates the Zen and earthy palettes here. Slightly higher
  visual interest than monochromatic without introducing real contrast risk.
- **Near-neutral / tonal** — a neutral base (gray, taupe, cream) with one or two very
  low-saturation accent hues barely stepped away from it. The source repeatedly frames this
  as "sophisticated" and "professional" — it's the dominant harmony type for both the
  Minimalist Modern and Classic Luxury theme groups here, which suggests luxury in this
  source is communicated through *restraint*, not boldness.
- **Complementary / triadic** — opposite or evenly-spaced hues. Present in the source's
  "vibrant"/"jewel" categories, but those are explicitly paired with fashion, gaming, and
  entertainment contexts in the source's own examples — not wellness or bathroom-adjacent
  ones. Usable here only as a sparing accent (see `luxury_dark_009`), never as a base.

## 2. Extracted Palette Dataset

See `palette_dataset.json` (10 palettes, validated: unique IDs, valid hex format, no
duplicate colors within a palette, every palette tagged with theme_fit and harmony_type).

## 3. Theme Palette Library

```text
Japanese Zen
├── zen_natural_001  (Sage & Stone)
├── zen_water_002    (Tide Pool)
└── zen_warm_003     (Coastal Sand)

Minimalist Modern
├── minimal_mono_004 (Salt & Pepper)
├── minimal_cool_005 (Frozen Lake)
└── minimal_warm_006 (Stone Path)

Classic Luxury
├── luxury_warm_007  (Golden Taupe)
├── luxury_deep_008  (Quiet Luxury)
└── luxury_dark_009  (Jewel Accent — Tier 3, accent-only)

Cross-theme tags (via theme_fit, no dedicated palette needed — avoids redundancy per Section 8):
  spa           → zen_natural_001, zen_water_002, zen_warm_003
  natural       → zen_natural_001, zen_warm_003, earthy_010
  fresh_airy    → zen_water_002, zen_warm_003
  soft_neutral  → minimal_mono_004
  dark_contemporary → minimal_cool_005
  earthy        → earthy_010, minimal_warm_006
  warm_minimal  → minimal_warm_006, earthy_010
```

## 4. Palette Generation Rules

```json
[
  {
    "theme": "japanese_zen",
    "rules": {
      "preferred_harmony": ["analogous", "monochromatic", "near-neutral"],
      "preferred_saturation": "low",
      "preferred_contrast": "low",
      "preferred_temperature": ["neutral", "warm"],
      "preferred_colour_families": ["sage", "stone", "sand", "blue_green"],
      "avoid": ["triadic", "high_saturation", "tetradic"]
    }
  },
  {
    "theme": "minimalist_modern",
    "rules": {
      "preferred_harmony": ["monochromatic", "near-neutral"],
      "preferred_saturation": "low",
      "preferred_contrast": "medium",
      "preferred_temperature": ["neutral", "cool", "warm"],
      "preferred_colour_families": ["gray", "slate", "warm_gray"],
      "avoid": ["complementary", "high_saturation"]
    }
  },
  {
    "theme": "classic_luxury",
    "rules": {
      "preferred_harmony": ["analogous", "tonal"],
      "preferred_saturation": "low_to_medium",
      "preferred_contrast": "medium",
      "preferred_temperature": ["warm"],
      "preferred_colour_families": ["taupe", "champagne", "gold_adjacent", "deep_brown"],
      "avoid": ["neon", "high_contrast_primary"],
      "note": "luxury here comes from tonal restraint + warm-metallic-compatible accents, not from darkness alone"
    }
  }
]
```
These represent **tendencies observed in the source**, not rigid constraints — the
optimization engine should treat them as scoring weights (see Section 5), not hard filters.

## 5. Colour Combination Scoring Model

```text
PaletteScore = harmony_score * 0.25
             + theme_match_score * 0.35
             + contrast_score * 0.15
             + saturation_score * 0.15
             + material_match_score * 0.10
```

- **harmony_score** (0–1): 1.0 if the palette's `harmony_type` is in the theme's
  `preferred_harmony` list, 0.5 if adjacent (e.g. tonal vs near-neutral), 0.0 otherwise.
- **theme_match_score** (0–1): overlap between the palette's `theme_fit` tags and the
  user's requested theme(s); weighted highest since this is the primary user-facing intent.
- **contrast_score** (0–1): 1.0 if the palette's contrast level matches the theme's
  `preferred_contrast`, degrading linearly for each step away (low→medium→high).
- **saturation_score** (0–1): same degradation logic against `preferred_saturation`.
- **material_match_score** (0–1): fraction of the palette's `material_associations` that
  overlap with materials actually present in the matched product bundle from the
  optimization engine (this is the one score that depends on the constraint engine's
  output, not just the palette in isolation — it should be computed after product
  selection, not before).

This is a simple weighted-sum model deliberately — consistent with the constraint engine's
own weighted-scoring approach (see the main repo's `runDesignEngine`), so the two systems
share one mental model rather than needing separate explanations for judges.

## 6. KOHLER Mapping Interface

```json
{
  "palette_id": "zen_natural_001",
  "finish_mapping": {
    "base": {
      "colour_family": "warm_neutral",
      "required_catalogue_match": true
    },
    "accent": {
      "colour_family": "muted_sage_green",
      "required_catalogue_match": true
    },
    "metallic": {
      "preferred_finish_families": ["matte_black", "brushed_nickel"],
      "required_catalogue_match": true
    }
  }
}
```

This interface is intentionally empty of real SKUs or finish names. The separation is:

```text
DESIGN REFERENCE (Figma combinations, text-described)
        ↓
COLOUR INTELLIGENCE (this dataset: roles, harmony, rules — Tier 1/2/3)
        ↓
KOHLER CATALOGUE (your real or synthetic product data)
        ↓
finish_mapping resolves colour_family → actual available finish
        ↓
Feeds into the constraint/optimization engine as one more soft objective (style_match)
```

The catalogue-matching layer (not built yet) is what populates `finish_mapping` with real
values — this file only defines the shape it should take.

## 7. Data Quality Rules

Applied to `palette_dataset.json` and validated (script output confirms all pass):

- Valid HEX format (`#RRGGBB`) — ✅ validated.
- No duplicate `palette_id` values — ✅ validated (10 unique).
- No duplicate colour entries within a single palette — ✅ validated.
- Every palette has at least one `theme_fit` tag — ✅ validated.
- Every palette has a `harmony_type`, using `"unknown"` where the source doesn't support a
  classification (none needed unknown here — all 10 had clear source-described harmony language).
- Every colour object carries a `provenance` field (`ai_derived` in this dataset, since no
  hex was directly extractable from the source — see the disclaimer at the top of this file).
- No invented KOHLER SKUs or finish names anywhere in this dataset — confirmed by inspection;
  `finish_mapping` fields use colour-family language only.
- No claims that any palette is an official KOHLER recommendation.

## 8. Final Recommendations

1. **Most reusable harmony types:** near-neutral and tonal — they appeared across all three
   theme groups (Zen, Minimalist Modern, Classic Luxury) and are the safest default when a
   user's stated preference is ambiguous or blended.
2. **Most useful families for Japanese Zen:** sage/muted green, sand/warm neutral, and
   low-saturation blue-green — consistently paired with "calm," "natural," "grounded"
   language across the relevant source combinations.
3. **Most useful families for Minimalist Modern:** gray-to-white monochromatic runs and
   slate/cool-neutral near-neutrals — the source ties these directly to "focus" and "clean."
4. **Most useful families for Classic Luxury:** warm taupe/champagne/gold-adjacent tones —
   notably, the source's own luxury-coded combinations are consistently *low-contrast and
   low-saturation*, not dark or bold. That's the one finding worth stating explicitly to
   judges: your system's "luxury" objective should not simply reward darkness.
5. **Redundant palettes discarded:** several near-duplicate warm-neutral combinations in the
   source (e.g. "Cappuccino," "Breakfast tea," "Cozy campfire" all cluster within one
   perceptual neighborhood of `earthy_010`/`luxury_warm_007`) were intentionally not given
   separate entries — the dataset stays compact per the Tier system rather than exhaustive.
6. **Principles that should become generative rules rather than stored palettes:** the
   temperature/saturation/contrast preference sets in Section 4 (`palette_generation_rules`)
   are more valuable long-term than any single stored palette — they let the system generate
   new, on-brand combinations parametrically instead of always selecting from a fixed
   10-palette library.

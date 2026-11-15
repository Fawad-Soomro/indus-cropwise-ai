# Methodology — Indus CropWise AI

This document explains exactly how rotation scores are produced. **Everything is a transparent,
deterministic rule. There is no machine learning and no randomness.** The goal is that a farmer can
see *why* one rotation scores differently from another.

## Overview
Each rotation (an ordered sequence of crops) receives four component scores in **0–100**, combined
with the project plan's base weights:

```
Score = (Water Fit × 0.30) + (Climate Fit × 0.25) + (Soil/Rotation Diversity × 0.25) + (Farmer Priority Fit × 0.20)
```

If a component cannot be computed (essential inputs missing), it is marked **insufficient**, its
weight is dropped, and the remaining weights are **re-normalised** so they still sum to 1. The result
is then flagged as lower-confidence. This logic lives in `core/scoring.py`.

## Component 1 — Water Fit (30%)
- `demand_index` = mean of the crops' water-demand index (1 = low … 5 = very high), scaled to 0–1.
- `availability` estimated from **irrigation type** (e.g. canal + tube well ≈ 0.90, rain-fed ≈ 0.20)
  and/or **rainfall** from NASA data (`annual_precip / 600`, capped at 1). The larger signal is used.
- `mismatch = max(0, demand − availability)`; penalty = `mismatch × 120`.
- Small bonus (up to +10) for spreading water demand across crops rather than stacking only thirsty ones.
- **Insufficient** when both irrigation and rainfall are unknown.

## Component 2 — Climate Fit (25%)
- `season_coverage` = how many of Kharif / Rabi the rotation uses (0, 0.5 or 1.0) → base = `100 × coverage`.
- **Heat penalty:** when NASA mean max temperature ≥ 38 °C, heat-sensitive crops (e.g. maize at
  flowering) reduce the score, scaled by how far above 38 °C and the share of sensitive crops.
- **Insufficient** when no climate summary is loaded.

## Component 3 — Soil / Rotation Diversity (25%)
- Base = `100 × (distinct crop families / number of crops)`.
- **+15** if the rotation includes a nitrogen-fixing **legume**.
- **−10** for each time the same family is grown back-to-back.
- If salinity is known to be **High/Saline**, **−10** per salinity-sensitive crop.
- Rarely insufficient (uses the catalogue; soil fields are optional).

## Component 4 — Farmer Priority Fit (20%)
The farmer sets 0–100 sliders for **water saving, soil health, income, food security**; these are
normalised to weights. Four sub-scores (0–100) are computed and combined with those weights:
- **Water saving** = `100 × (1 − demand_index)`.
- **Soil health** = family diversity (+20 if a legume is present).
- **Income** = mean of illustrative income tags (Cotton 1.0, Rice 0.75, Maize/Chickpea 0.60, Wheat/Mung 0.55).
- **Food security** = share of food/staple crops (all catalogue crops except cotton).

> The income and food tags are **illustrative orderings for comparison only** — they are not market
> prices or validated economics.

## Assumptions
- Water availability is estimated, not measured flow.
- "Unknown" soil inputs lower confidence (shown as warnings), they do not block scoring.
- The candidate rotation strategies are reasonable Sindh sequences, not exhaustive or optimal.

## What this is NOT
- Not a trained ML model. Not a validated agronomic model. Not a yield/profit/water-saving guarantee.
- It is a transparent comparison aid to support discussion with local agricultural experts.

## Reproducibility
Given identical inputs the scores are identical every time (deterministic). Unit tests in
`tests/test_scoring.py` assert ranges, determinism, re-weighting behaviour and priority sensitivity.

"""
core/scoring.py
---------------
Explainable, rule-based crop-rotation scoring for INDUS CROPWISE AI.

THIS IS NOT A MACHINE-LEARNING MODEL AND NOT A VALIDATED AGRONOMIC MODEL.
It is a transparent, deterministic comparison tool that turns the project plan's
illustrative weighting into reproducible numbers so farmers can SEE why one
rotation scores differently from another. Every number below is explained.

Base weights (from the project plan):
    Water fit               0.30
    Climate fit             0.25
    Soil / rotation div.    0.25
    Farmer priority fit     0.20

Each component returns a score in [0, 100] plus a plain-language explanation.
If a component cannot be computed (missing essential inputs) it is marked
'insufficient', its weight is removed and the remaining weights are
re-normalised. Scores are NEVER random.
"""
from __future__ import annotations
from typing import Optional
import statistics

BASE_WEIGHTS = {
    "water_fit": 0.30,
    "climate_fit": 0.25,
    "soil_rotation_diversity": 0.25,
    "farmer_priority_fit": 0.20,
}

# --- Prototype heuristic tags (documented in METHODOLOGY.md) ----------------
# Relative income potential (0..1) -- illustrative ordering, not market prices.
INCOME_TAG = {
    "Cotton": 1.00, "Rice": 0.75, "Maize": 0.60,
    "Chickpea": 0.60, "Wheat": 0.55, "Mung Bean": 0.55,
}
# Crops that directly contribute to household food security (staples/pulses).
FOOD_STAPLE = {"Wheat", "Rice", "Maize", "Chickpea", "Mung Bean"}
# Crops notably sensitive to extreme heat around flowering (prototype flag).
HEAT_SENSITIVE = {"Maize"}

IRRIGATION_AVAILABILITY = {
    "canal": 0.85, "tube well": 0.85, "canal + tube well": 0.90,
    "drip": 0.88, "full": 0.90, "sprinkler": 0.80,
    "partial": 0.55, "supplemental": 0.55,
    "rain-fed": 0.20, "rainfed": 0.20, "none": 0.15,
}


def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def _to_float(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _water_index(crop):
    """Water demand on a 1(low)..5(very high) scale."""
    return _to_float(crop.get("water_demand_index"), 3.0)


def _is_legume(crop):
    return str(crop.get("is_legume", "No")).strip().lower() in {"yes", "true", "1"}


def _family(crop):
    return str(crop.get("crop_family", "")).split("(")[0].strip().lower()


def _season_flags(crop):
    s = str(crop.get("season", "")).lower()
    kharif = "kharif" in s or "both" in s or ("spring" in s and "rabi" not in s)
    rabi = "rabi" in s or "both" in s or "autumn" in s
    if "kharif or rabi" in s or "both" in s:
        kharif = rabi = True
    return kharif, rabi


# --------------------------------------------------------------------------- #
# Component 1 : WATER FIT                                                      #
# --------------------------------------------------------------------------- #
def water_fit(rotation, farm, climate):
    indices = [_water_index(c) for c in rotation]
    demand_index = (sum(indices) / len(indices)) / 5.0  # 0..1

    # Availability from irrigation (if known)
    irr = str(farm.get("irrigation", "")).strip().lower()
    irr_avail = None
    for key, val in IRRIGATION_AVAILABILITY.items():
        if key in irr:
            irr_avail = val
            break

    # Availability contribution from rainfall (arid Sindh ~ low)
    rain_avail = None
    if climate and climate.get("annual_precip_mm") is not None:
        rain_avail = _clamp(_to_float(climate["annual_precip_mm"], 0) / 600.0, 0, 1)

    if irr_avail is None and rain_avail is None:
        return None, "Insufficient information: irrigation availability and rainfall are both unknown."

    parts = []
    if irr_avail is not None:
        parts.append(irr_avail)
    if rain_avail is not None:
        parts.append(rain_avail * 0.6)   # rain alone rarely covers demand here
    availability = max(parts)

    mismatch = max(0.0, demand_index - availability)      # demand exceeding supply
    penalty = mismatch * 120.0
    # Reward not stacking only high-water crops (spread of water demand)
    diversity_bonus = min(10.0, (statistics.pstdev(indices) if len(indices) > 1 else 0) * 6.0)
    score = _clamp(100.0 - penalty + diversity_bonus)

    expl = (f"Mean crop water demand {demand_index*100:.0f}% of max vs. estimated water "
            f"availability {availability*100:.0f}%. "
            + ("Demand exceeds supply, lowering the score. " if mismatch > 0 else "Supply covers demand. ")
            + f"Water-demand spread adds +{diversity_bonus:.0f}.")
    return round(score, 1), expl


# --------------------------------------------------------------------------- #
# Component 2 : CLIMATE FIT                                                    #
# --------------------------------------------------------------------------- #
def climate_fit(rotation, farm, climate):
    if not climate or climate.get("mean_t2m") is None:
        return None, "Insufficient information: no climate summary available (load NASA/sample data first)."

    covers_k = any(_season_flags(c)[0] for c in rotation)
    covers_r = any(_season_flags(c)[1] for c in rotation)
    season_coverage = (int(covers_k) + int(covers_r)) / 2.0  # 0, 0.5 or 1.0
    base = 100.0 * season_coverage

    # Heat-stress penalty when the hottest-period max temperature is extreme
    mean_tmax = _to_float(climate.get("mean_tmax"), 0)
    heat_frac = sum(1 for c in rotation if c.get("crop") in HEAT_SENSITIVE) / len(rotation)
    heat_penalty = 0.0
    if mean_tmax >= 38:
        heat_penalty = 20.0 * heat_frac * _clamp((mean_tmax - 38) / 6.0, 0, 1)

    score = _clamp(base - heat_penalty)
    cov_txt = {0.0: "neither season", 0.5: "one season", 1.0: "both Kharif & Rabi"}[season_coverage]
    expl = (f"Rotation covers {cov_txt} (coverage {season_coverage*100:.0f}%). "
            f"Mean max temperature {mean_tmax:.1f} C"
            + (f"; heat-sensitive crops reduce the score by {heat_penalty:.0f}." if heat_penalty > 0
               else "; no heat penalty applied."))
    return round(score, 1), expl


# --------------------------------------------------------------------------- #
# Component 3 : SOIL / ROTATION DIVERSITY                                      #
# --------------------------------------------------------------------------- #
def soil_rotation_diversity(rotation, farm):
    fams = [_family(c) for c in rotation]
    family_diversity = len(set(fams)) / len(fams)
    base = 100.0 * family_diversity

    legume_bonus = 15.0 if any(_is_legume(c) for c in rotation) else 0.0

    # Penalty for the same family grown back-to-back in the sequence
    consec_penalty = sum(10.0 for i in range(1, len(fams)) if fams[i] == fams[i - 1])

    # Optional salinity sub-term (only if the farmer told us)
    salinity_note = ""
    salinity_penalty = 0.0
    sal = str(farm.get("salinity", "")).strip().lower()
    if sal in {"high", "saline", "strongly saline"}:
        sensitive = sum(1 for c in rotation
                        if "sensitive" in str(c.get("salinity_tolerance", "")).lower())
        salinity_penalty = 10.0 * sensitive
        if sensitive:
            salinity_note = f" Saline soil penalises {sensitive} salinity-sensitive crop(s)."

    score = _clamp(base + legume_bonus - consec_penalty - salinity_penalty)
    expl = (f"Crop-family diversity {family_diversity*100:.0f}% "
            f"({len(set(fams))} families across {len(fams)} slots)."
            + (" Includes a nitrogen-fixing legume (+15)." if legume_bonus else " No legume present.")
            + (f" Repeated-family penalty -{consec_penalty:.0f}." if consec_penalty else "")
            + salinity_note)
    return round(score, 1), expl


# --------------------------------------------------------------------------- #
# Component 4 : FARMER PRIORITY FIT                                            #
# --------------------------------------------------------------------------- #
def farmer_priority_fit(rotation, priorities):
    # Normalise priority weights (default equal if nothing supplied)
    keys = ["water_saving", "soil_health", "income", "food_security"]
    weights = {k: max(0.0, _to_float(priorities.get(k, 0), 0.0)) for k in keys} if priorities else {}
    total_w = sum(weights.values())
    if total_w <= 0:
        weights = {k: 1.0 for k in keys}
        total_w = 4.0
    weights = {k: v / total_w for k, v in weights.items()}

    indices = [_water_index(c) for c in rotation]
    demand_index = (sum(indices) / len(indices)) / 5.0
    fams = [_family(c) for c in rotation]
    family_diversity = len(set(fams)) / len(fams)
    legume = any(_is_legume(c) for c in rotation)

    sub = {
        "water_saving": _clamp(100.0 * (1 - demand_index)),
        "soil_health": _clamp(100.0 * family_diversity + (20 if legume else 0)),
        "income": _clamp(100.0 * (sum(INCOME_TAG.get(c.get("crop"), 0.5) for c in rotation) / len(rotation))),
        "food_security": _clamp(100.0 * (sum(1 for c in rotation if c.get("crop") in FOOD_STAPLE) / len(rotation))),
    }
    score = sum(sub[k] * weights[k] for k in keys)
    top = max(weights, key=weights.get)
    expl = (f"Weighted to your priorities (top: {top.replace('_', ' ')}). "
            f"Sub-scores -> water saving {sub['water_saving']:.0f}, soil health {sub['soil_health']:.0f}, "
            f"income {sub['income']:.0f}, food security {sub['food_security']:.0f}.")
    return round(_clamp(score), 1), expl


# --------------------------------------------------------------------------- #
# Aggregate                                                                    #
# --------------------------------------------------------------------------- #
def score_rotation(rotation, farm=None, climate=None, priorities=None) -> dict:
    """
    Score a single rotation (ordered list of crop dicts).
    Returns a fully transparent breakdown. Deterministic; never random.
    """
    farm = farm or {}
    priorities = priorities or {}

    raw = {
        "water_fit": water_fit(rotation, farm, climate),
        "climate_fit": climate_fit(rotation, farm, climate),
        "soil_rotation_diversity": soil_rotation_diversity(rotation, farm),
        "farmer_priority_fit": farmer_priority_fit(rotation, priorities),
    }

    components, warnings = {}, []
    available = {}
    for name, (score, expl) in raw.items():
        insufficient = score is None
        components[name] = {
            "score": score,
            "explanation": expl,
            "base_weight": BASE_WEIGHTS[name],
            "insufficient": insufficient,
        }
        if insufficient:
            warnings.append(f"{name.replace('_', ' ').title()}: {expl}")
        else:
            available[name] = BASE_WEIGHTS[name]

    reweighted = len(available) < len(BASE_WEIGHTS)
    total = None
    weights_used = {k: 0.0 for k in BASE_WEIGHTS}
    if available:
        wsum = sum(available.values())
        for name, w in available.items():
            wu = w / wsum
            weights_used[name] = round(wu, 4)
            components[name]["weight_used"] = round(wu, 4)
            total = (total or 0.0) + components[name]["score"] * wu
        total = round(total, 1)
    if reweighted and available:
        warnings.append("Weights were re-normalised because one or more components had insufficient data. "
                        "Treat the total as lower-confidence.")

    return {
        "total": total,
        "reweighted": reweighted,
        "components": components,
        "weights_base": dict(BASE_WEIGHTS),
        "weights_used": weights_used,
        "warnings": warnings,
    }

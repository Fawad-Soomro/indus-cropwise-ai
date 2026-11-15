"""
core/rotation.py
----------------
Crop catalogue loading and candidate crop-rotation strategies for Sindh.

A "rotation" is an ordered list of crop names grown in sequence across seasons.
The strategies below are illustrative, agronomically-reasoned sequences built
from the crop catalogue (data/crops.csv). They are starting points for
comparison, not prescriptions.
"""
from __future__ import annotations
import os
import csv
from typing import List, Dict

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CROPS_CSV = os.path.join(DATA_DIR, "crops.csv")


def load_crops(path: str = CROPS_CSV) -> Dict[str, dict]:
    """Load the crop catalogue into {crop_name: row_dict}. Coerces numeric fields."""
    crops: Dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                row["water_demand_index"] = float(row.get("water_demand_index", 3))
            except (TypeError, ValueError):
                row["water_demand_index"] = 3.0
            crops[row["crop"].strip()] = row
    return crops


# Candidate strategies: name -> (ordered crop sequence, short rationale)
ROTATION_STRATEGIES = {
    "Water-Smart Pulse Rotation": (
        ["Chickpea", "Mung Bean", "Wheat"],
        "Two low-water nitrogen-fixing legumes followed by wheat. Minimises irrigation "
        "demand and rebuilds soil nitrogen; suited to water-scarce or saline-prone land.",
    ),
    "Balanced Cereal-Legume Rotation": (
        ["Wheat", "Mung Bean", "Maize"],
        "A staple cereal, a short-duration legume to restore nitrogen, then maize. "
        "Balances food security, soil health and moderate water use.",
    ),
    "Traditional Cotton-Wheat Rotation": (
        ["Cotton", "Wheat"],
        "The dominant Sindh system. Strong income from cotton but high water demand and "
        "no legume, so soil nitrogen and water use need close management.",
    ),
    "High-Value Rice-Based Rotation": (
        ["Rice", "Wheat", "Chickpea"],
        "Rice for income where water is plentiful, wheat as the Rabi staple, then chickpea "
        "to restore nitrogen. Highest water demand of the set.",
    ),
}


def default_strategies() -> Dict[str, tuple]:
    return dict(ROTATION_STRATEGIES)


def build_rotation(crop_names: List[str], catalogue: Dict[str, dict]) -> List[dict]:
    """Turn a list of crop names into the ordered list of crop dicts scoring expects."""
    seq = []
    for name in crop_names:
        crop = catalogue.get(name)
        if crop:
            seq.append(crop)
    return seq


def summarize_rotation(crop_names: List[str], catalogue: Dict[str, dict]) -> dict:
    """Quick human-readable facts about a sequence for the UI."""
    seq = build_rotation(crop_names, catalogue)
    families = sorted({c.get("crop_family", "").split("(")[0].strip() for c in seq})
    has_legume = any(str(c.get("is_legume", "No")).lower() == "yes" for c in seq)
    mean_water = round(sum(float(c.get("water_demand_index", 3)) for c in seq) / len(seq), 2) if seq else 0
    return {
        "sequence": " -> ".join(crop_names),
        "families": families,
        "has_legume": has_legume,
        "mean_water_index": mean_water,
        "n_crops": len(seq),
    }

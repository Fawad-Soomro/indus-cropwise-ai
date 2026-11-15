"""Automated tests for core.scoring. Run: python -m pytest  OR  python tests/test_scoring.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import scoring
from core.rotation import load_crops, build_rotation, default_strategies

CROPS = load_crops()
FARM = {"irrigation": "Canal + Tube well", "salinity": "Low", "drainage": "Good"}
CLIMATE = {"mean_t2m": 27.0, "mean_tmax": 40.0, "annual_precip_mm": 150}
PRI = {"water_saving": 60, "soil_health": 60, "income": 40, "food_security": 50}


def _seq(names):
    return build_rotation(names, CROPS)


def test_scores_in_range():
    for seq, _ in default_strategies().values():
        r = scoring.score_rotation(_seq(seq), FARM, CLIMATE, PRI)
        assert 0 <= r["total"] <= 100
        for c in r["components"].values():
            assert c["score"] is None or 0 <= c["score"] <= 100


def test_deterministic_not_random():
    seq = _seq(["Wheat", "Mung Bean", "Maize"])
    a = scoring.score_rotation(seq, FARM, CLIMATE, PRI)["total"]
    b = scoring.score_rotation(seq, FARM, CLIMATE, PRI)["total"]
    assert a == b


def test_legume_rotation_scores_higher_soil_than_monofamily():
    legume = scoring.score_rotation(_seq(["Chickpea", "Wheat"]), FARM, CLIMATE, PRI)
    # Cotton-Wheat: two different families but NO legume
    cereal = scoring.score_rotation(_seq(["Wheat", "Maize"]), FARM, CLIMATE, PRI)  # same family twice
    assert (legume["components"]["soil_rotation_diversity"]["score"]
            >= cereal["components"]["soil_rotation_diversity"]["score"])


def test_missing_climate_marks_insufficient_and_reweights():
    r = scoring.score_rotation(_seq(["Chickpea", "Wheat"]), FARM, None, PRI)
    assert r["components"]["climate_fit"]["insufficient"] is True
    assert r["reweighted"] is True
    assert r["total"] is not None  # still scored on remaining components


def test_missing_all_water_inputs_marks_insufficient():
    r = scoring.score_rotation(_seq(["Wheat", "Maize"]), {}, None, PRI)
    assert r["components"]["water_fit"]["insufficient"] is True
    assert r["components"]["climate_fit"]["insufficient"] is True


def test_weights_used_sum_to_one_when_available():
    r = scoring.score_rotation(_seq(["Wheat", "Mung Bean", "Maize"]), FARM, CLIMATE, PRI)
    s = sum(c.get("weight_used", 0) for c in r["components"].values())
    assert abs(s - 1.0) < 1e-6


def test_water_saving_priority_favours_low_water_rotation():
    pri_water = {"water_saving": 100, "soil_health": 0, "income": 0, "food_security": 0}
    low = scoring.score_rotation(_seq(["Chickpea", "Mung Bean"]), FARM, CLIMATE, pri_water)
    high = scoring.score_rotation(_seq(["Rice", "Cotton"]), FARM, CLIMATE, pri_water)
    assert (low["components"]["farmer_priority_fit"]["score"]
            > high["components"]["farmer_priority_fit"]["score"])


def test_base_weights_match_plan():
    assert scoring.BASE_WEIGHTS == {"water_fit": 0.30, "climate_fit": 0.25,
                                    "soil_rotation_diversity": 0.25, "farmer_priority_fit": 0.20}


def _run_all():
    fns = [g for n, g in globals().items() if n.startswith("test_")]
    passed = 0
    for fn in fns:
        fn(); passed += 1
        print(f"  PASS {fn.__name__}")
    print(f"scoring: {passed}/{len(fns)} passed")
    return passed, len(fns)


if __name__ == "__main__":
    _run_all()

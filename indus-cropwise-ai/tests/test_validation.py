"""Automated tests for core.validation. Run: python -m pytest  OR  python tests/test_validation.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import validation as v


def test_valid_latitude():
    assert v.validate_latitude(25.39)[0] is True
    assert v.validate_latitude(90)[0] is True
    assert v.validate_latitude(-90)[0] is True


def test_invalid_latitude():
    assert v.validate_latitude(91)[0] is False
    assert v.validate_latitude(-100)[0] is False
    assert v.validate_latitude("abc")[0] is False


def test_valid_longitude():
    assert v.validate_longitude(68.37)[0] is True
    assert v.validate_longitude(-180)[0] is True


def test_invalid_longitude():
    assert v.validate_longitude(181)[0] is False
    assert v.validate_longitude("x")[0] is False


def test_coordinates_in_pakistan_ok_no_warning():
    ok, msg = v.validate_coordinates(25.39, 68.37)
    assert ok is True and msg == "OK"


def test_coordinates_outside_pakistan_soft_warning():
    ok, msg = v.validate_coordinates(48.85, 2.35)  # Paris
    assert ok is True and msg != "OK"


def test_coordinates_reject_bad():
    assert v.validate_coordinates(999, 0)[0] is False


def test_date_range_ok():
    assert v.validate_date_range("20240101", "20240201")[0] is True


def test_date_range_start_after_end():
    assert v.validate_date_range("20240301", "20240101")[0] is False


def test_date_range_future_rejected():
    assert v.validate_date_range("20240101", "21000101")[0] is False


def test_soil_completeness():
    frac, missing = v.completeness_of_soil_profile(
        {"soil_type": "Loam", "soil_ph": "Unknown", "salinity": "Low",
         "drainage": "", "irrigation": "Canal", "organic_matter": "Unknown"})
    assert 0 < frac < 1
    assert "soil_ph" in missing and "drainage" in missing


def _run_all():
    fns = [g for n, g in globals().items() if n.startswith("test_")]
    passed = 0
    for fn in fns:
        fn(); passed += 1
        print(f"  PASS {fn.__name__}")
    print(f"validation: {passed}/{len(fns)} passed")
    return passed, len(fns)


if __name__ == "__main__":
    _run_all()

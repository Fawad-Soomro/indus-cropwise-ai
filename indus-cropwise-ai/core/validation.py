"""
core/validation.py
------------------
Input validation for INDUS CROPWISE AI.

All validators return a tuple: (is_valid: bool, message: str).
They never raise on bad user input; the UI layer decides how to show the message.
Pure functions, no Streamlit imports -> easy to unit test.
"""
from __future__ import annotations
from datetime import date, datetime
from typing import Tuple

# Approximate bounding box of Pakistan (used only for a *soft* warning, not a hard block).
PK_LAT_MIN, PK_LAT_MAX = 23.0, 37.5
PK_LON_MIN, PK_LON_MAX = 60.0, 78.0


def validate_latitude(lat) -> Tuple[bool, str]:
    """Latitude must be a number within [-90, 90]."""
    try:
        lat = float(lat)
    except (TypeError, ValueError):
        return False, "Latitude must be a number."
    if lat < -90 or lat > 90:
        return False, "Latitude must be between -90 and 90 degrees."
    return True, "OK"


def validate_longitude(lon) -> Tuple[bool, str]:
    """Longitude must be a number within [-180, 180]."""
    try:
        lon = float(lon)
    except (TypeError, ValueError):
        return False, "Longitude must be a number."
    if lon < -180 or lon > 180:
        return False, "Longitude must be between -180 and 180 degrees."
    return True, "OK"


def validate_coordinates(lat, lon) -> Tuple[bool, str]:
    """
    Validate a lat/lon pair.
    Returns (True, note) when usable. The note may carry a soft warning when the
    point falls outside the Pakistan bounding box (still allowed, just flagged).
    """
    ok_lat, msg_lat = validate_latitude(lat)
    if not ok_lat:
        return False, msg_lat
    ok_lon, msg_lon = validate_longitude(lon)
    if not ok_lon:
        return False, msg_lon

    lat, lon = float(lat), float(lon)
    if not (PK_LAT_MIN <= lat <= PK_LAT_MAX and PK_LON_MIN <= lon <= PK_LON_MAX):
        return True, ("Coordinates are valid but fall outside Pakistan. "
                      "This prototype is tuned for Sindh; results elsewhere are illustrative only.")
    return True, "OK"


def validate_date_range(start, end) -> Tuple[bool, str]:
    """
    Validate a start/end date range for a NASA POWER request.
    Accepts date objects or 'YYYYMMDD' / 'YYYY-MM-DD' strings.
    """
    def _parse(d):
        if isinstance(d, (date, datetime)):
            return date(d.year, d.month, d.day)
        s = str(d).strip().replace("-", "")
        return datetime.strptime(s, "%Y%m%d").date()

    try:
        s = _parse(start)
        e = _parse(end)
    except (ValueError, TypeError):
        return False, "Dates must be valid calendar dates (YYYYMMDD)."

    if s > e:
        return False, "Start date must be on or before the end date."
    if e > date.today():
        return False, "End date cannot be in the future (NASA POWER has a short processing lag)."
    if (e - s).days > 366 * 5:
        return False, "Please request at most ~5 years of daily data at a time."
    return True, "OK"


def completeness_of_soil_profile(profile: dict) -> Tuple[float, list]:
    """
    Report how complete the user's soil profile is.
    Returns (fraction_known_0_to_1, list_of_missing_optional_fields).
    'Unknown' / 'Not tested' / '' are treated as missing.
    """
    tracked = ["soil_type", "soil_ph", "salinity", "drainage", "irrigation", "organic_matter"]
    unknown_markers = {"", "unknown", "not tested", "none", None}
    missing = []
    known = 0
    for key in tracked:
        val = profile.get(key)
        norm = str(val).strip().lower() if val is not None else ""
        if norm in unknown_markers:
            missing.append(key)
        else:
            known += 1
    frac = known / len(tracked) if tracked else 0.0
    return frac, missing

"""
services/nasa_power.py
----------------------
Genuine NASA POWER Daily Point API integration for INDUS CROPWISE AI.

Docs:        https://power.larc.nasa.gov/docs/services/api/temporal/daily/
Parameters:  https://power.larc.nasa.gov/parameters/
Community:   AG (Agroclimatology)

Behaviour:
  1. Try a LIVE request to NASA POWER.
  2. On network/API failure, fall back to a previously CACHED response (if any).
  3. If no cache exists, fall back to the clearly-labelled SAMPLE dataset.
The returned 'status' is always one of: 'live', 'cached', 'sample'.
SAMPLE / CACHED data are NEVER presented as live NASA observations.
"""
from __future__ import annotations
import os
import json
import time
import hashlib
from datetime import datetime, timezone

import pandas as pd
import requests

BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
DOCS_URL = "https://power.larc.nasa.gov/docs/services/api/temporal/daily/"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
SAMPLE_CSV = os.path.join(DATA_DIR, "demo_climate.csv")
os.makedirs(CACHE_DIR, exist_ok=True)

# Default Agroclimatology parameters (verified against the POWER parameter dictionary).
DEFAULT_PARAMETERS = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M"]

PARAMETER_LABELS = {
    "T2M": "Mean Temperature (2 m)",
    "T2M_MAX": "Max Temperature (2 m)",
    "T2M_MIN": "Min Temperature (2 m)",
    "PRECTOTCORR": "Precipitation (corrected)",
    "RH2M": "Relative Humidity (2 m)",
    "ALLSKY_SFC_SW_DWN": "Solar Irradiance (all-sky)",
    "WS2M": "Wind Speed (2 m)",
}
FALLBACK_UNITS = {
    "T2M": "C", "T2M_MAX": "C", "T2M_MIN": "C",
    "PRECTOTCORR": "mm/day", "RH2M": "%",
    "ALLSKY_SFC_SW_DWN": "MJ/m^2/day", "WS2M": "m/s",
}
FILL_VALUE = -999.0


def _cache_key(lat, lon, start, end, community, parameters):
    raw = f"{lat:.3f}_{lon:.3f}_{start}_{end}_{community}_{','.join(parameters)}"
    return hashlib.md5(raw.encode()).hexdigest()


def _cache_path(key):
    return os.path.join(CACHE_DIR, f"{key}.json")


def _parse_power_json(payload: dict):
    """Turn a POWER JSON payload into (DataFrame, units_dict, coordinates, period)."""
    props = payload.get("properties", {}).get("parameter", {})
    df = pd.DataFrame(props)
    if not df.empty:
        df.index = pd.to_datetime(df.index, format="%Y%m%d", errors="coerce")
        df = df.sort_index()
        df = df.replace(FILL_VALUE, pd.NA)
    # Units: POWER returns them under top-level "parameters"
    units = {}
    for p, meta in payload.get("parameters", {}).items():
        units[p] = meta.get("units", FALLBACK_UNITS.get(p, ""))
    for p in df.columns:
        units.setdefault(p, FALLBACK_UNITS.get(p, ""))
    coords = payload.get("geometry", {}).get("coordinates", [None, None])
    period = None
    if not df.empty:
        period = (df.index.min().strftime("%Y-%m-%d"), df.index.max().strftime("%Y-%m-%d"))
    return df, units, coords, period


def _result(status, df, units, lat, lon, period, source_url, messages):
    return {
        "status": status,                         # 'live' | 'cached' | 'sample'
        "df": df,
        "units": units,
        "coordinates": {"latitude": lat, "longitude": lon},
        "period": period,
        "source_url": source_url,
        "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "messages": messages,
        "docs_url": DOCS_URL,
    }


def load_sample():
    """Load the clearly-labelled synthetic sample dataset (offline fallback)."""
    df = pd.read_csv(SAMPLE_CSV)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
    df = df.set_index("date").drop(columns=[c for c in ["data_source"] if c in df.columns])
    units = {c: FALLBACK_UNITS.get(c, "") for c in df.columns}
    period = (df.index.min().strftime("%Y-%m-%d"), df.index.max().strftime("%Y-%m-%d"))
    return df, units, period


def fetch_power_daily(lat, lon, start, end,
                      parameters=None, community="AG",
                      timeout=20, use_cache=True, cache_ttl_hours=24):
    """
    Fetch daily point data from NASA POWER with caching and graceful fallback.

    start/end: 'YYYYMMDD' strings (or anything str()-able to that form).
    Returns the result dict described at the top of this module.
    """
    parameters = parameters or DEFAULT_PARAMETERS
    start = str(start).replace("-", "")
    end = str(end).replace("-", "")
    key = _cache_key(lat, lon, start, end, community, parameters)
    cpath = _cache_path(key)
    messages = []

    params = {
        "parameters": ",".join(parameters),
        "community": community,
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON",
        "time-standard": "UTC",
    }
    source_url = BASE_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())

    # 1) Fresh cache shortcut
    if use_cache and os.path.exists(cpath):
        age_h = (time.time() - os.path.getmtime(cpath)) / 3600.0
        if age_h <= cache_ttl_hours:
            try:
                with open(cpath, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                df, units, coords, period = _parse_power_json(payload)
                if not df.empty:
                    messages.append(f"Served from local cache (age {age_h:.1f} h).")
                    return _result("cached", df, units, lat, lon, period, source_url, messages)
            except Exception as e:  # noqa: BLE001
                messages.append(f"Cache unreadable, refetching ({e}).")

    # 2) Live request
    try:
        resp = requests.get(BASE_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()
        df, units, coords, period = _parse_power_json(payload)
        if df.empty:
            raise ValueError("NASA POWER returned no parameter data for this request.")
        try:
            with open(cpath, "w", encoding="utf-8") as f:
                json.dump(payload, f)
        except Exception:  # noqa: BLE001
            pass
        messages.append("Live response from NASA POWER.")
        return _result("live", df, units, lat, lon, period, source_url, messages)
    except Exception as e:  # noqa: BLE001
        messages.append(f"NASA POWER request failed: {e}")

    # 3) Stale cache
    if os.path.exists(cpath):
        try:
            with open(cpath, "r", encoding="utf-8") as f:
                payload = json.load(f)
            df, units, coords, period = _parse_power_json(payload)
            if not df.empty:
                messages.append("Live request failed; served STALE local cache.")
                return _result("cached", df, units, lat, lon, period, source_url, messages)
        except Exception as e:  # noqa: BLE001
            messages.append(f"Stale cache unreadable ({e}).")

    # 4) Sample fallback
    df, units, period = load_sample()
    messages.append("NASA service and cache unavailable; showing labelled SAMPLE data (not NASA observations).")
    return _result("sample", df, units, lat, lon, period, source_url, messages)


def summarize_climate(df: pd.DataFrame) -> dict:
    """Condense a daily dataframe into the summary scoring.py consumes."""
    if df is None or df.empty:
        return {}
    num = df.apply(pd.to_numeric, errors="coerce")

    def _mean(col):
        return float(num[col].mean()) if col in num and num[col].notna().any() else None

    summary = {
        "mean_t2m": _mean("T2M"),
        "mean_tmax": _mean("T2M_MAX"),
        "mean_tmin": _mean("T2M_MIN"),
        "mean_rh": _mean("RH2M"),
        "n_days": int(len(num)),
    }
    if "PRECTOTCORR" in num and num["PRECTOTCORR"].notna().any():
        daily_mean = num["PRECTOTCORR"].mean()
        summary["annual_precip_mm"] = round(float(daily_mean) * 365.0, 1)
        summary["total_precip_mm"] = round(float(num["PRECTOTCORR"].sum()), 1)
    else:
        summary["annual_precip_mm"] = None
        summary["total_precip_mm"] = None
    return summary

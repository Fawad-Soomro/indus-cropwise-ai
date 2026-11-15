# Test Report — Indus CropWise AI
Generated: 2026-11-15 06:44 UTC
Environment: Python 3.10.12, Streamlit 1.65, Plotly 7.1, Pandas 2.3, NumPy 2.2 (Linux workspace).

## Automated unit tests — 19/19 PASSED
Run with: `python tests\test_validation.py` and `python tests\test_scoring.py` (or `python -m pytest`).

**Validation (11/11):** latitude/longitude range checks, non-numeric rejection, Pakistan soft-warning,
out-of-range rejection, date-range order, future-date rejection, soil-completeness accounting.

**Scoring (8/8):** all scores within 0–100; determinism (same input → same output, never random);
legume rotation scores ≥ a repeated-family rotation on soil diversity; missing climate → component
marked insufficient and weights re-normalised; missing water inputs → insufficient; weights-used sum
to 1.0; a water-saving priority favours the low-water rotation; base weights equal the plan
(0.30/0.25/0.25/0.20).

## Application / render tests — PASSED
- **App launches:** `streamlit run app.py` started; `/_stcore/health` → HTTP 200, main page → HTTP 200, no errors in server log.
- **All six pages render with no exceptions** (headless Streamlit AppTest): Home, Farm Profile,
  NASA Climate, Crop Catalogue, Rotation Explorer, Methodology & Sources.
- **Fetch button flow:** pressing "Fetch NASA POWER data" populates climate state and the summary.
- **Priority sliders:** changing a slider re-runs the comparison with no errors; 4 breakdown tables render.
- Two defects found during testing were **fixed** (not just reported): duplicate Plotly element IDs
  (added unique `key=`), and a mixed-type score column (coerced to string).

## QA checklist (from the build brief)
| # | Check | Result |
|---|-------|--------|
| 1 | Application launches | PASS (HTTP 200) |
| 2 | Dashboard displays | PASS (Home renders) |
| 3 | Valid coordinates work | PASS (unit test) |
| 4 | Invalid coordinates rejected | PASS (unit test) |
| 5 | NASA POWER requests work OR show clear failure status | PASS — status is always Live/Cached/Sample; failures are labelled |
| 6 | API data parsed correctly | PASS — parser tested on POWER JSON shape; fill value −999 → missing |
| 7 | Units & dates displayed correctly | PASS — units read from response, dates parsed to calendar |
| 8 | Charts render | PASS — 4 Plotly charts render; HTML previews in screenshots/ |
| 9 | Farm profile inputs work | PASS — form saves to session, validates coords |
| 10 | Crop catalogue shows references | PASS — 6 crops, each with a reference link |
| 11 | At least two rotations compared | PASS — 4 default strategies + custom builder |
| 12 | Scoring consistent | PASS — determinism unit test |
| 13 | Changing priorities updates results | PASS — slider interaction test |
| 14 | Missing soil inputs generate warnings | PASS — re-weighting + warnings tested |
| 15 | Sample data never shown as NASA data | PASS — red "SAMPLE DATA (NOT NASA)" badge + disclaimer |
| 16 | Works on a normal laptop | PASS — lightweight (Streamlit/Pandas/Plotly), ~8 GB RAM is ample |
| 17 | README instructions accurate | PASS — install/run steps verified against actual commands |
| 18 | No secrets committed | PASS — .gitignore excludes secrets/venv/cache; no keys used (NASA POWER needs none) |

## ⚠️ To confirm on your Windows laptop (not verifiable in this build sandbox)
The build/test sandbox blocks outbound access to `power.larc.nasa.gov`, so the **live** NASA path
could not be exercised here — the app correctly fell back to the labelled **sample** dataset. On your
own internet-connected laptop the live call will work. Please confirm:
1. Run the app, open **NASA Climate**, press **Fetch NASA POWER data** → the badge should read **LIVE NASA DATA**.
2. Capture real screenshots of each page into `screenshots/` for the submission (steps in SCREENSHOTS.md).

Interactive HTML previews of the charts and a styled dashboard preview are already in `screenshots/`.

# Data Sources — Indus CropWise AI

## 1. NASA data (primary)
**NASA POWER — Prediction Of Worldwide Energy Resources — Daily Point API**
- Endpoint: `https://power.larc.nasa.gov/api/temporal/daily/point`
- Documentation: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- Parameter dictionary: https://power.larc.nasa.gov/parameters/
- API tutorial: https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/
- Community used: **AG (Agroclimatology)**
- Parameters requested: `T2M` (mean temp, °C), `T2M_MAX` (max temp, °C), `T2M_MIN` (min temp, °C),
  `PRECTOTCORR` (corrected precipitation, mm/day), `RH2M` (relative humidity, %).
- Request includes: parameters, community, longitude, latitude, start, end, `format=JSON`,
  `time-standard=UTC`.
- **Role in the solution:** provides the real local climate signal (temperature regime, rainfall,
  humidity) that drives the NASA Climate dashboard and feeds the *Climate fit* and *Water fit*
  components of the rotation scoring.

> Units are read from the live POWER response where available; fill values (−999) are treated as missing.

## 2. Space-agency partner data
None. No partner-agency dataset is integrated. We therefore do **not** claim any partner dataset.

## 3. Agricultural / crop references
The crop catalogue (`data/crops.csv`) was compiled from general, publicly available agronomy:
- **FAO — Land & Water, Crop Information portal:** https://www.fao.org/land-water/databases-and-software/crop-information/en/
- FAO crop water requirements concepts (Irrigation & Drainage / AquaCrop): https://www.fao.org/aquacrop/en/

Recommended additional references the team should verify against for Sindh-specific tuning:
- ICRISAT (chickpea, mung bean / pulses): https://www.icrisat.org/
- Sindh Agriculture University, Tandojam: https://www.sau.edu.pk/
- Pakistan Agricultural Research Council (PARC): https://www.parc.gov.pk/

Agronomic facts used are **general and textbook-level** (season, relative water demand, crop family,
legume nitrogen fixation). They are references, not field-specific recommendations. No agricultural
figures were invented.

## 4. Synthetic sample data (clearly labelled)
- `data/demo_climate.csv` + `data/demo_climate_meta.json` — **AI-generated synthetic** daily climate
  approximating Hyderabad seasonal patterns (annual rainfall ≈ 148 mm, matching Sindh's arid climate).
  Every row carries `data_source = SAMPLE_SYNTHETIC`.
- **Used only** as an offline fallback when NASA POWER and the local cache are both unreachable.
- It is **never** presented as live NASA observation data; the UI shows a red "SAMPLE DATA (NOT NASA)" badge.

## 5. Tools & libraries
Python 3.10+, Streamlit, Pandas, NumPy, Plotly, Requests. Git/GitHub for version control.

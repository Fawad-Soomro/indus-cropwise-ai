# 🌾 INDUS CROPWISE AI
### NASA-Powered Smart Crop Rotation & Climate Resilience Assistant
**Team INDUSASTRA — "Rooted on Earth. Reaching Beyond."**
NASA Space Apps Challenge 2026 · Challenge: **Field Shift — Adapting Farms with NASA Data**
Local event: Hyderabad, Pakistan (Virtual) · Focus: Hyderabad & agricultural Sindh, Pakistan

---

## What it is
Indus CropWise AI is an **educational decision-support prototype** that helps farmers
**explore and compare crop-rotation strategies**. It combines:
- **NASA POWER** daily climate data (temperature, rainfall, humidity),
- the farmer's **soil information and priorities**, and
- a small **Sindh crop catalogue**,

into transparent, explainable comparison scores.

> ⚠️ **Important:** This is a prototype. It does **not** guarantee yield, profit, soil
> improvement or water savings, and it is **not** a trained machine-learning model — it is a
> transparent rule-based comparison tool. Real farming decisions require local agricultural
> expertise and verified soil tests.

## Features
- **Home dashboard** — branding, demo location, NASA data status, climate indicators, prototype disclaimer.
- **Farm profile** — location, coordinates, soil type, pH, salinity, drainage, irrigation (with *Unknown* options everywhere).
- **NASA climate dashboard** — genuine NASA POWER Daily Point API calls, with clear **Live / Cached / Sample** status, units, period, coordinates and provenance.
- **Crop catalogue** — 6 Sindh-relevant crops with water demand, season, rotation role and references.
- **Crop rotation explorer** — compares strategies on Water fit, Climate fit, Soil/rotation diversity and Farmer priority fit, with an explanation for every score and adjustable priorities.
- **Methodology & sources** — full transparency on data, scoring and limitations.

## How to run (Windows, step by step)
You need **Python 3.10 or newer** installed (tick *"Add Python to PATH"* during install).

**Easiest way — double-click `run.bat`.** It creates a virtual environment, installs everything and launches the app.

**Or do it manually in Command Prompt (CMD):**
```
cd path\to\indus-cropwise-ai
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```
The app opens automatically in your browser at **http://localhost:8501**.
Press **Ctrl + C** in the CMD window to stop it.

> First launch downloads packages, so it may take a few minutes. Later launches are fast.

## Project structure
```
indus-cropwise-ai/
  app.py                 # Streamlit app (all 6 pages)
  requirements.txt
  run.bat                # Windows one-click launcher
  README.md  DATA_SOURCES.md  METHODOLOGY.md  AI_USAGE_DISCLOSURE.md  TEST_REPORT.md
  .streamlit/config.toml # theme
  data/
    crops.csv            # crop catalogue (with references)
    demo_climate.csv     # LABELLED synthetic sample (offline fallback only)
    demo_climate_meta.json
    cache/               # cached NASA POWER responses
  services/nasa_power.py # NASA POWER API + cache + sample fallback
  core/validation.py  core/scoring.py  core/rotation.py
  components/charts.py  components/ui.py
  tests/test_validation.py  tests/test_scoring.py
  screenshots/           # chart & dashboard previews
```

## Tests
```
cd indus-cropwise-ai
python tests\test_validation.py
python tests\test_scoring.py
```
(or `python -m pytest` if you have pytest). See **TEST_REPORT.md** for results.

## NASA data
NASA POWER Daily Point API (Agroclimatology community):
https://power.larc.nasa.gov/docs/services/api/temporal/daily/
Parameters used: `T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, RH2M`.
If NASA POWER is unreachable the app shows a **clearly labelled sample dataset** — never presented as live NASA data.

## Team INDUSASTRA
Fawad Ali Soomro (Team-Lead • Product scope • coordination • interface review • integration • deployment • 
final submission) · Aashiq Hussain (Co-Team Lead
NASA POWER data • backend logic • scoring engine • validation • testing • 
technical documentation)
## License / use
Educational prototype for NASA Space Apps 2026. Not affiliated with or endorsed by NASA.
No NASA logos or protected marks are used as team branding.

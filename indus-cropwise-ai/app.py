"""
INDUS CROPWISE AI  —  NASA-Powered Smart Crop Rotation & Climate Resilience Assistant
Team INDUSASTRA  |  NASA Space Apps Challenge 2026  |  Challenge: Field Shift
Tagline: ROOTED ON EARTH. REACHING BEYOND.

Educational decision-support PROTOTYPE. It does NOT guarantee yield, profit,
soil improvement or water savings, and it is NOT a trained machine-learning model.
"""
from __future__ import annotations
import datetime as dt

import pandas as pd
import streamlit as st

from components import ui
from components import charts
from core import validation, scoring, rotation
from services import nasa_power

st.set_page_config(page_title="Indus CropWise AI", page_icon="🌾",
                   layout="wide", initial_sidebar_state="expanded")
ui.inject_css()

# --------------------------------------------------------------------------- #
# Session state defaults                                                       #
# --------------------------------------------------------------------------- #
DEFAULT_FARM = {
    "location": "Hyderabad, Sindh, Pakistan (demo)",
    "latitude": 25.39, "longitude": 68.37,
    "farm_size": "", "soil_type": "Loam",
    "soil_ph": "Unknown", "salinity": "Unknown",
    "drainage": "Unknown", "irrigation": "Canal + Tube well",
    "organic_matter": "Unknown",
}
DEFAULT_PRIORITIES = {"water_saving": 60, "soil_health": 60, "income": 40, "food_security": 50}

for key, val in [("page", "Home"), ("farm", dict(DEFAULT_FARM)),
                 ("priorities", dict(DEFAULT_PRIORITIES)),
                 ("climate_result", None), ("climate_summary", {})]:
    if key not in st.session_state:
        st.session_state[key] = val


@st.cache_data(show_spinner=False, ttl=3600)
def cached_fetch(lat, lon, start, end):
    return nasa_power.fetch_power_daily(lat, lon, start, end)


@st.cache_data(show_spinner=False)
def cached_crops():
    return rotation.load_crops()


def default_dates():
    end = dt.date.today() - dt.timedelta(days=7)      # POWER processing lag
    start = end - dt.timedelta(days=365)
    return start, end


# --------------------------------------------------------------------------- #
# Sidebar navigation                                                           #
# --------------------------------------------------------------------------- #
PAGES = ["Home", "Farm Profile", "NASA Climate", "Crop Catalogue",
         "Rotation Explorer", "Methodology & Sources"]

with st.sidebar:
    st.markdown("### 🌾 INDUS CROPWISE AI")
    st.caption("Team INDUSASTRA · Field Shift · NASA Space Apps 2026")
    choice = st.radio("Navigate", PAGES, index=PAGES.index(st.session_state.page))
    if choice != st.session_state.page:
        st.session_state.page = choice
    st.markdown("---")
    r = st.session_state.climate_result
    if r:
        st.markdown("**Climate data status**")
        st.markdown(ui.status_badge(r["status"]), unsafe_allow_html=True)
    else:
        st.caption("Climate data not loaded yet.")
    st.markdown("---")
    st.caption("Educational prototype. Not a guarantee of yield, profit or savings.")

page = st.session_state.page


def go(p):
    st.session_state.page = p
    st.rerun()


# --------------------------------------------------------------------------- #
# PAGE: HOME                                                                   #
# --------------------------------------------------------------------------- #
if page == "Home":
    ui.hero("INDUS CROPWISE AI",
            "NASA-Powered Smart Crop Rotation & Climate Resilience Assistant")
    farm = st.session_state.farm

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        ui.metric_tile("Demo Location", "Hyderabad", "Sindh")
    with c2:
        ui.metric_tile("Coordinates", f"{farm['latitude']:.2f}, {farm['longitude']:.2f}", "lat, lon")
    with c3:
        r = st.session_state.climate_result
        status_txt = {"live": "Live", "cached": "Cached", "sample": "Sample"}.get(
            r["status"] if r else None, "Not loaded")
        ui.metric_tile("NASA Data", status_txt, "")
    with c4:
        s = st.session_state.climate_summary
        t = f"{s.get('mean_t2m'):.1f}" if s.get("mean_t2m") is not None else "—"
        ui.metric_tile("Mean Temp", t, "°C")

    st.write("")
    ui.disclaimer_banner(
        "This is an educational decision-support prototype built for the NASA Space Apps "
        "Challenge 2026 (Field Shift). It compares crop-rotation options using NASA climate "
        "data and transparent rules. It does NOT guarantee yield, profit, soil improvement "
        "or water savings, and it is not a trained machine-learning model. Real farming "
        "decisions require local agricultural expertise and verified soil tests.")

    ui.section("What this tool does",
               "Combine NASA Earth observations with your soil and priorities to explore crop rotations.")
    a, b, c = st.columns(3)
    with a:
        ui.info_card("🛰️", "Real NASA Climate",
                     "Pulls daily temperature, rainfall and humidity from the NASA POWER API "
                     "for your field's coordinates, with clear live / cached / sample status.")
    with b:
        ui.info_card("🌱", "Explainable Rotations",
                     "Compares rotation strategies on water fit, climate fit, soil diversity and "
                     "your own priorities — and explains every score, never a black box.")
    with c:
        ui.info_card("📊", "Transparent & Honest",
                     "Shows the data used, the assumptions made and what information is missing, "
                     "so you can judge the results yourself.")

    st.write("")
    left, right = st.columns([2, 1])
    with left:
        ui.note("New here? Start by setting your farm profile, load NASA climate data for your "
                "coordinates, then open the Rotation Explorer to compare strategies.")
    with right:
        if st.button("🚀 Start Farm Assessment", use_container_width=True):
            go("Farm Profile")

# --------------------------------------------------------------------------- #
# PAGE: FARM PROFILE                                                           #
# --------------------------------------------------------------------------- #
elif page == "Farm Profile":
    ui.section("Farm Profile", "Tell the tool about your field. Unknown is always an acceptable answer.")
    farm = st.session_state.farm
    with st.form("farm_form"):
        col1, col2 = st.columns(2)
        with col1:
            farm["location"] = st.text_input("Location / village", farm["location"])
            farm["latitude"] = st.number_input("Latitude", value=float(farm["latitude"]),
                                               format="%.4f", min_value=-90.0, max_value=90.0)
            farm["longitude"] = st.number_input("Longitude", value=float(farm["longitude"]),
                                                format="%.4f", min_value=-180.0, max_value=180.0)
            farm["farm_size"] = st.text_input("Farm size (optional, e.g. 5 acres)", farm["farm_size"])
            farm["irrigation"] = st.selectbox(
                "Irrigation availability",
                ["Canal + Tube well", "Canal", "Tube well", "Drip", "Partial / Supplemental",
                 "Rain-fed", "None", "Unknown"],
                index=0)
        with col2:
            farm["soil_type"] = st.selectbox(
                "Soil type / texture",
                ["Loam", "Clay", "Clay Loam", "Sandy Loam", "Sandy", "Silt Loam", "Unknown"],
                index=["Loam", "Clay", "Clay Loam", "Sandy Loam", "Sandy", "Silt Loam", "Unknown"].index(
                    farm.get("soil_type", "Loam") if farm.get("soil_type") in
                    ["Loam","Clay","Clay Loam","Sandy Loam","Sandy","Silt Loam","Unknown"] else "Loam"))
            farm["soil_ph"] = st.selectbox("Soil pH (optional)",
                                           ["Unknown", "Acidic (<6.5)", "Neutral (6.5–7.5)", "Alkaline (>7.5)"],
                                           index=0)
            farm["salinity"] = st.selectbox("Soil salinity status",
                                            ["Unknown", "Low", "Moderate", "High / Saline"], index=0)
            farm["drainage"] = st.selectbox("Drainage",
                                            ["Unknown", "Good", "Moderate", "Poor"], index=0)
            farm["organic_matter"] = st.selectbox("Organic matter (if known)",
                                                  ["Unknown", "Low", "Medium", "High"], index=0)
        submitted = st.form_submit_button("💾 Save farm profile")
    if submitted:
        ok, msg = validation.validate_coordinates(farm["latitude"], farm["longitude"])
        if not ok:
            st.error(msg)
        else:
            st.session_state.farm = farm
            if msg != "OK":
                st.warning(msg)
            st.success("Farm profile saved. Next: load NASA climate data.")
            frac, missing = validation.completeness_of_soil_profile(farm)
            if missing:
                ui.note(f"Soil profile is {frac*100:.0f}% complete. Unknown fields "
                        f"({', '.join(m.replace('_',' ') for m in missing)}) will reduce the "
                        f"confidence of soil-related scores — that's fine, the tool will tell you where.")

# --------------------------------------------------------------------------- #
# PAGE: NASA CLIMATE                                                           #
# --------------------------------------------------------------------------- #
elif page == "NASA Climate":
    ui.section("NASA Climate Dashboard",
               "Daily climate from the NASA POWER API (Agroclimatology community) for your field.")
    farm = st.session_state.farm
    d_start, d_end = default_dates()

    c1, c2, c3 = st.columns(3)
    with c1:
        lat = st.number_input("Latitude", value=float(farm["latitude"]), format="%.4f")
        lon = st.number_input("Longitude", value=float(farm["longitude"]), format="%.4f")
    with c2:
        start = st.date_input("Start date", value=d_start, max_value=dt.date.today())
        end = st.date_input("End date", value=d_end, max_value=dt.date.today())
    with c3:
        st.write("")
        st.write("")
        fetch = st.button("🛰️ Fetch NASA POWER data", use_container_width=True)
        st.caption("Source: power.larc.nasa.gov · Community: AG · Time standard: UTC")

    okc, msgc = validation.validate_coordinates(lat, lon)
    okd, msgd = validation.validate_date_range(start, end)
    if not okc:
        st.error(f"Coordinates: {msgc}")
    elif not okd:
        st.error(f"Dates: {msgd}")
    elif fetch:
        with st.spinner("Contacting NASA POWER…"):
            res = cached_fetch(lat, lon, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
        st.session_state.climate_result = res
        st.session_state.climate_summary = nasa_power.summarize_climate(res["df"])
        st.session_state.farm["latitude"] = lat
        st.session_state.farm["longitude"] = lon

    res = st.session_state.climate_result
    if res is None:
        ui.note("No climate data loaded yet. Set your coordinates and dates, then press "
                "**Fetch NASA POWER data**.")
    else:
        st.markdown(ui.status_badge(res["status"]), unsafe_allow_html=True)
        if res["status"] == "sample":
            ui.disclaimer_banner("NASA POWER was unreachable, so this shows AI-generated SAMPLE "
                                 "data (approximating Hyderabad). These are NOT NASA observations.")
        elif res["status"] == "cached":
            ui.note("Served from a previously saved NASA POWER response (cached), not a fresh live call.")

        df = res["df"]; units = res["units"]; s = st.session_state.climate_summary
        m1, m2, m3, m4 = st.columns(4)
        with m1: ui.metric_tile("Mean Temp", f"{s.get('mean_t2m'):.1f}" if s.get('mean_t2m') is not None else "—", "°C")
        with m2: ui.metric_tile("Mean Max Temp", f"{s.get('mean_tmax'):.1f}" if s.get('mean_tmax') is not None else "—", "°C")
        with m3: ui.metric_tile("Annual Precip (est.)", f"{s.get('annual_precip_mm')}" if s.get('annual_precip_mm') is not None else "—", "mm")
        with m4: ui.metric_tile("Days of data", f"{s.get('n_days','—')}", "")

        st.plotly_chart(charts.climate_timeseries(df, units), use_container_width=True, key="ts")
        st.plotly_chart(charts.monthly_climatology(df, units), use_container_width=True, key="monthly")

        with st.expander("Data provenance & parameters"):
            prov = pd.DataFrame({
                "Field": ["Data source", "Status", "Coordinates", "Period",
                          "Parameters", "Retrieved at", "Request URL"],
                "Value": ["NASA POWER Daily Point API", res["status"].upper(),
                          f"{res['coordinates']['latitude']}, {res['coordinates']['longitude']}",
                          f"{res['period'][0]} to {res['period'][1]}" if res['period'] else "—",
                          ", ".join(f"{c} [{units.get(c,'')}]" for c in df.columns),
                          res["retrieved_at"], res["source_url"]],
            })
            st.table(prov)
            st.caption("Messages: " + " | ".join(res["messages"]))

# --------------------------------------------------------------------------- #
# PAGE: CROP CATALOGUE                                                         #
# --------------------------------------------------------------------------- #
elif page == "Crop Catalogue":
    ui.section("Crop Catalogue", "A small, Sindh-relevant catalogue. Agronomic facts are "
               "general references, not field-specific recommendations.")
    crops = cached_crops()
    cols = st.columns(2)
    for i, (name, c) in enumerate(crops.items()):
        with cols[i % 2]:
            legume = "🟢 Legume (N-fixing)" if str(c.get("is_legume")).lower() == "yes" else "Cereal / non-legume"
            html = (f"<h3>🌱 {name}</h3>"
                    f"<p><b>Family:</b> {c.get('crop_family')}<br>"
                    f"<b>Season:</b> {c.get('season')}<br>"
                    f"<b>Water demand:</b> {c.get('water_demand')} (index {c.get('water_demand_index')}/5)<br>"
                    f"<b>Role:</b> {legume} · {c.get('nitrogen_role')}<br>"
                    f"<b>Rotation role:</b> {c.get('rotation_role')}<br>"
                    f"<b>Salinity:</b> {c.get('salinity_tolerance')} · "
                    f"<b>Drainage:</b> {c.get('drainage_preference')}<br>"
                    f"<b>Soil note:</b> {c.get('soil_note')}<br>"
                    f"<a href='{c.get('reference_url')}' target='_blank'>Reference ↗</a></p>")
            st.markdown(f"<div class='ica-card' style='margin-bottom:14px'>{html}</div>",
                        unsafe_allow_html=True)
    ui.note("Reference: FAO Land & Water — Crop Information portal. See DATA_SOURCES.md for the "
            "full list of agricultural references used.")

# --------------------------------------------------------------------------- #
# PAGE: ROTATION EXPLORER                                                      #
# --------------------------------------------------------------------------- #
elif page == "Rotation Explorer":
    ui.section("Crop Rotation Explorer",
               "Compare rotation strategies. Scores are illustrative prototype comparisons, "
               "not validated agronomic measurements.")
    crops = cached_crops()
    farm = st.session_state.farm
    climate = st.session_state.climate_summary or None

    st.markdown("**Your farming priorities** — slide to tell the tool what matters most.")
    pr = st.session_state.priorities
    p1, p2, p3, p4 = st.columns(4)
    with p1: pr["water_saving"] = st.slider("Water saving", 0, 100, int(pr["water_saving"]))
    with p2: pr["soil_health"] = st.slider("Soil health", 0, 100, int(pr["soil_health"]))
    with p3: pr["income"] = st.slider("Income", 0, 100, int(pr["income"]))
    with p4: pr["food_security"] = st.slider("Food security", 0, 100, int(pr["food_security"]))
    st.session_state.priorities = pr

    if climate is None:
        ui.note("No NASA climate summary loaded — the **Climate fit** component will be marked "
                "insufficient and weights re-normalised. Load data on the NASA Climate page for a "
                "fuller comparison.")

    strategies = rotation.default_strategies()

    # Optional custom rotation
    with st.expander("➕ Build your own rotation (optional)"):
        picks = st.multiselect("Pick 2–4 crops in sequence order", list(crops.keys()))
        custom_name = st.text_input("Name", "My Custom Rotation")
        if len(picks) >= 2:
            strategies = dict(strategies)
            strategies[custom_name] = (picks, "User-defined custom rotation.")

    # Score everything
    results, summaries = {}, {}
    for name, (seq, desc) in strategies.items():
        seq_dicts = rotation.build_rotation(seq, crops)
        results[name] = scoring.score_rotation(seq_dicts, farm, climate, pr)
        results[name]["_desc"] = desc
        results[name]["_seq"] = seq
        summaries[name] = rotation.summarize_rotation(seq, crops)

    ranked = sorted([(n, r) for n, r in results.items() if r["total"] is not None],
                    key=lambda kv: kv[1]["total"], reverse=True)

    g1, g2 = st.columns([1, 1])
    with g1:
        st.plotly_chart(charts.rotation_total_bar(results), use_container_width=True, key="totbar")
    with g2:
        st.plotly_chart(charts.component_breakdown(results), use_container_width=True, key="compbd")

    if ranked:
        top_name = ranked[0][0]
        ui.note(f"For <b>your current priorities</b>, <b>{top_name}</b> scores highest "
                f"({ranked[0][1]['total']}/100). This is a comparison aid only — it is not a "
                f"guarantee that this sequence is agronomically best for your field.")

    st.markdown("### Rotation details")
    for name, r in results.items():
        total_txt = f"{r['total']}/100" if r["total"] is not None else "insufficient data"
        rank = next((i + 1 for i, (n, _) in enumerate(ranked) if n == name), None)
        with st.expander(f"🌾 {name} — {total_txt}" + (f"   ·   rank #{rank}" if rank else "")):
            st.markdown(f"**Sequence:** {' → '.join(r['_seq'])}")
            st.caption(r["_desc"])
            sm = summaries[name]
            st.markdown(f"- Families: {', '.join(sm['families'])}  \n"
                        f"- Contains legume: {'Yes' if sm['has_legume'] else 'No'}  \n"
                        f"- Mean water-demand index: {sm['mean_water_index']}/5")
            st.plotly_chart(charts.water_demand_gauge(sm["mean_water_index"]),
                            use_container_width=True, key=f"gauge_{name}")
            st.markdown("**Score breakdown**")
            rows = []
            for cn, c in r["components"].items():
                rows.append({
                    "Component": cn.replace("_", " ").title(),
                    "Score": "—" if c["score"] is None else str(c["score"]),
                    "Base weight": f"{int(c['base_weight']*100)}%",
                    "Weight used": f"{int(c.get('weight_used',0)*100)}%" if not c["insufficient"] else "0% (dropped)",
                    "Why": c["explanation"],
                })
            st.table(pd.DataFrame(rows))
            if r["warnings"]:
                for w in r["warnings"]:
                    st.warning(w)

# --------------------------------------------------------------------------- #
# PAGE: METHODOLOGY & SOURCES                                                  #
# --------------------------------------------------------------------------- #
elif page == "Methodology & Sources":
    ui.section("Explanation, Methodology & Data Sources",
               "Everything the tool uses, how scores are calculated, and what it cannot do.")

    st.markdown("#### 1. NASA data used")
    st.markdown(
        "- **NASA POWER Daily Point API** (Agroclimatology community) — daily `T2M`, `T2M_MAX`, "
        "`T2M_MIN`, `PRECTOTCORR`, `RH2M` for the field's coordinates.\n"
        "- Docs: https://power.larc.nasa.gov/docs/services/api/temporal/daily/\n"
        "- Parameter dictionary: https://power.larc.nasa.gov/parameters/")

    st.markdown("#### 2. Other datasets")
    st.markdown(
        "- **Crop catalogue** (`data/crops.csv`) — compiled from FAO Land & Water crop "
        "information and standard agronomy for Sindh crops.\n"
        "- **Sample climate** (`data/demo_climate.csv`) — AI-generated synthetic fallback, "
        "clearly labelled, used ONLY when NASA POWER is unreachable.")

    st.markdown("#### 3. Scoring methodology")
    w = scoring.BASE_WEIGHTS
    st.markdown(
        f"Each rotation gets four component scores (0–100), combined with base weights:\n"
        f"- **Water fit — {int(w['water_fit']*100)}%:** mean crop water demand vs. estimated "
        f"water availability (irrigation + rainfall).\n"
        f"- **Climate fit — {int(w['climate_fit']*100)}%:** season coverage (Kharif/Rabi) and a "
        f"heat-stress penalty from NASA max temperature.\n"
        f"- **Soil / rotation diversity — {int(w['soil_rotation_diversity']*100)}%:** crop-family "
        f"diversity, legume inclusion, repeated-family and salinity penalties.\n"
        f"- **Farmer priority fit — {int(w['farmer_priority_fit']*100)}%:** how the rotation serves "
        f"your weighted priorities (water, soil, income, food).")
    st.latex(r"Score = 0.30\cdot Water + 0.25\cdot Climate + 0.25\cdot Soil + 0.20\cdot Priority")
    st.markdown(
        "If a component lacks essential data it is marked **insufficient**, its weight is removed, "
        "and the remaining weights are re-normalised. Scores are deterministic — never random.")

    st.markdown("#### 4. Assumptions & missing information")
    st.markdown(
        "- Water availability is estimated from irrigation type and rainfall, not measured flow.\n"
        "- Income and food-security tags are illustrative orderings, not market prices.\n"
        "- Unknown soil fields reduce confidence in soil-related scores (shown as warnings).")

    st.markdown("#### 5. Limitations")
    ui.disclaimer_banner(
        "This prototype does NOT guarantee yield, profit, soil improvement or water savings. "
        "It is a transparent comparison aid, not a validated agronomic model and not a trained "
        "machine-learning system. Real decisions require local agricultural expertise, verified "
        "soil tests and extension advice.")
    st.caption("See README.md, METHODOLOGY.md, DATA_SOURCES.md and AI_USAGE_DISCLOSURE.md in the "
               "project folder for the full write-up.")

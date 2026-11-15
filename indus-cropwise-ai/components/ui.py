"""
components/ui.py
----------------
Reusable Streamlit UI helpers + a professional CSS theme for INDUS CROPWISE AI.
Palette: navy #0B1730, blue #1479C9, cyan #24B9D6, pale #EAF4FB, green, amber.
"""
from __future__ import annotations
import streamlit as st

NAVY = "#0B1730"
BLUE = "#1479C9"
CYAN = "#24B9D6"
PALE = "#EAF4FB"
GREEN = "#27AE60"
AMBER = "#E6A817"


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"]  { font-family: 'Inter', 'Segoe UI', sans-serif; }
        .block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1200px; }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0B1730 0%, #10234A 100%);
        }
        section[data-testid="stSidebar"] * { color: #EAF4FB !important; }
        section[data-testid="stSidebar"] .stRadio label { font-weight: 500; }

        /* Hero header */
        .ica-hero {
            background: linear-gradient(120deg, #0B1730 0%, #1479C9 60%, #24B9D6 100%);
            border-radius: 18px; padding: 26px 30px; color: #fff;
            box-shadow: 0 10px 30px rgba(11,23,48,0.25); margin-bottom: 18px;
        }
        .ica-hero h1 { font-size: 30px; font-weight: 800; margin: 0; letter-spacing: .3px; }
        .ica-hero .tag { font-size: 13px; letter-spacing: 3px; opacity: .85; text-transform: uppercase; }
        .ica-hero .sub { font-size: 15px; opacity: .95; margin-top: 6px; }

        /* Cards */
        .ica-card {
            background: #fff; border: 1px solid #E3ECF5; border-radius: 14px;
            padding: 18px 20px; box-shadow: 0 4px 14px rgba(11,23,48,0.06);
            height: 100%;
        }
        .ica-card h3 { color: #0B1730; font-size: 16px; margin: 0 0 6px 0; font-weight: 700; }
        .ica-card p { color: #4A5A70; font-size: 13.5px; margin: 0; line-height: 1.5; }
        .ica-card .icon { font-size: 22px; }

        /* Metric tiles */
        .ica-metric {
            background: linear-gradient(135deg,#fff 0%, #F5FAFF 100%);
            border: 1px solid #E3ECF5; border-left: 5px solid #1479C9;
            border-radius: 12px; padding: 14px 16px;
        }
        .ica-metric .label { font-size: 12px; color: #6B7A90; text-transform: uppercase; letter-spacing: .6px; }
        .ica-metric .value { font-size: 24px; font-weight: 800; color: #0B1730; }
        .ica-metric .unit { font-size: 13px; color: #1479C9; font-weight: 600; }

        /* Badges */
        .ica-badge { display:inline-block; padding: 4px 12px; border-radius: 20px;
            font-size: 12px; font-weight: 700; letter-spacing:.3px; }
        .badge-live   { background:#E3F6EC; color:#1E7A46; border:1px solid #27AE60; }
        .badge-cached { background:#FFF4E0; color:#9A6B00; border:1px solid #E6A817; }
        .badge-sample { background:#FDE8E8; color:#B03A3A; border:1px solid #E57373; }

        /* Disclaimer */
        .ica-disclaimer {
            background:#FFF8E8; border:1px solid #E6A817; border-radius:12px;
            padding:12px 16px; color:#7A5A00; font-size:13px; margin: 8px 0 14px 0;
        }
        .ica-note {
            background:#EAF4FB; border-left:4px solid #1479C9; border-radius:8px;
            padding:10px 14px; color:#234; font-size:13px; margin:8px 0;
        }

        /* Section titles */
        .ica-section { color:#0B1730; font-size:20px; font-weight:800; margin: 6px 0 2px 0; }
        .ica-section-sub { color:#6B7A90; font-size:13.5px; margin-bottom:12px; }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg,#1479C9,#24B9D6); color:#fff;
            border:none; border-radius:10px; padding:10px 22px; font-weight:700;
            box-shadow:0 6px 16px rgba(20,121,201,.28);
        }
        .stButton>button:hover { filter:brightness(1.05); }

        /* Rotation score pill */
        .score-pill { font-size:30px; font-weight:800; color:#0B1730; }
        .rank-chip { background:#27AE60; color:#fff; border-radius:8px; padding:2px 10px;
            font-size:12px; font-weight:700; }

        #MainMenu {visibility:hidden;} footer {visibility:hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title, subtitle, tagline="ROOTED ON EARTH. REACHING BEYOND."):
    st.markdown(
        f"""<div class="ica-hero">
              <div class="tag">{tagline}</div>
              <h1>{title}</h1>
              <div class="sub">{subtitle}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def section(title, subtitle=""):
    st.markdown(f'<div class="ica-section">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="ica-section-sub">{subtitle}</div>', unsafe_allow_html=True)


def info_card(icon, title, text):
    st.markdown(
        f"""<div class="ica-card"><div class="icon">{icon}</div>
             <h3>{title}</h3><p>{text}</p></div>""",
        unsafe_allow_html=True,
    )


def metric_tile(label, value, unit=""):
    st.markdown(
        f"""<div class="ica-metric"><div class="label">{label}</div>
             <div class="value">{value} <span class="unit">{unit}</span></div></div>""",
        unsafe_allow_html=True,
    )


def status_badge(status: str):
    status = (status or "").lower()
    text = {"live": "LIVE NASA DATA", "cached": "CACHED NASA DATA",
            "sample": "SAMPLE DATA (NOT NASA)"}.get(status, status.upper())
    cls = {"live": "badge-live", "cached": "badge-cached", "sample": "badge-sample"}.get(status, "badge-sample")
    return f'<span class="ica-badge {cls}">{text}</span>'


def disclaimer_banner(text):
    st.markdown(f'<div class="ica-disclaimer">⚠️ {text}</div>', unsafe_allow_html=True)


def note(text):
    st.markdown(f'<div class="ica-note">{text}</div>', unsafe_allow_html=True)

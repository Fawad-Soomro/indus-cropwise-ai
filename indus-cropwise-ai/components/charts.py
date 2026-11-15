"""
components/charts.py
--------------------
Plotly figures for INDUS CROPWISE AI, themed with the project palette.
All functions return a go.Figure (no Streamlit import -> reusable/testable).
"""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Project palette
NAVY = "#0B1730"
BLUE = "#1479C9"
CYAN = "#24B9D6"
PALE = "#EAF4FB"
GREEN = "#27AE60"
AMBER = "#E6A817"
GREY = "#7A8699"

PALETTE = [BLUE, CYAN, GREEN, AMBER, "#8E44AD", "#E57373"]


def _base_layout(fig, title=None, height=420):
    fig.update_layout(
        title=dict(text=title, font=dict(color=NAVY, size=18)) if title else None,
        template="plotly_white",
        height=height,
        margin=dict(l=40, r=30, t=60 if title else 30, b=40),
        font=dict(family="Segoe UI, Roboto, sans-serif", color=NAVY, size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def climate_timeseries(df: pd.DataFrame, units: dict, title="Daily Climate — Temperature & Precipitation"):
    """Temperature lines + precipitation bars on a secondary axis."""
    num = df.apply(pd.to_numeric, errors="coerce")
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if "PRECTOTCORR" in num:
        fig.add_trace(go.Bar(x=num.index, y=num["PRECTOTCORR"], name="Precipitation",
                             marker_color=CYAN, opacity=0.55,
                             hovertemplate="%{y:.1f} mm<extra>Precip</extra>"),
                      secondary_y=True)
    for col, color in (("T2M_MAX", AMBER), ("T2M", BLUE), ("T2M_MIN", NAVY)):
        if col in num:
            fig.add_trace(go.Scatter(x=num.index, y=num[col], name=col, mode="lines",
                                     line=dict(color=color, width=1.8)),
                          secondary_y=False)
    _base_layout(fig, title)
    fig.update_yaxes(title_text=f"Temperature ({units.get('T2M','C')})", secondary_y=False)
    fig.update_yaxes(title_text=f"Precip ({units.get('PRECTOTCORR','mm/day')})",
                     secondary_y=True, showgrid=False)
    return fig


def monthly_climatology(df: pd.DataFrame, units: dict, title="Monthly Climatology"):
    """Monthly mean temperature (line) and total precipitation (bars)."""
    num = df.apply(pd.to_numeric, errors="coerce").copy()
    num["month"] = num.index.month
    grp = num.groupby("month")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    idx = sorted(grp.groups.keys())
    labels = [months[m - 1] for m in idx]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if "PRECTOTCORR" in num:
        fig.add_trace(go.Bar(x=labels, y=grp["PRECTOTCORR"].sum().reindex(idx).values,
                             name="Total precip", marker_color=CYAN, opacity=0.65),
                      secondary_y=True)
    if "T2M" in num:
        fig.add_trace(go.Scatter(x=labels, y=grp["T2M"].mean().reindex(idx).values,
                                 name="Mean temp", mode="lines+markers",
                                 line=dict(color=BLUE, width=2.5)),
                      secondary_y=False)
    _base_layout(fig, title, height=380)
    fig.update_yaxes(title_text="Mean Temp (C)", secondary_y=False)
    fig.update_yaxes(title_text="Total Precip (mm)", secondary_y=True, showgrid=False)
    return fig


def rotation_total_bar(results: dict, title="Rotation Comparison — Total Score"):
    """results: {rotation_name: score_dict}. Horizontal bar of totals."""
    names, totals, colors = [], [], []
    for name, r in results.items():
        if r.get("total") is None:
            continue
        names.append(name)
        totals.append(r["total"])
    order = sorted(range(len(totals)), key=lambda i: totals[i])
    names = [names[i] for i in order]
    totals = [totals[i] for i in order]
    colors = [GREEN if t == max(totals) else BLUE for t in totals]
    fig = go.Figure(go.Bar(x=totals, y=names, orientation="h",
                           marker_color=colors,
                           text=[f"{t:.1f}" for t in totals], textposition="outside",
                           hovertemplate="%{y}: %{x:.1f}/100<extra></extra>"))
    _base_layout(fig, title, height=360)
    fig.update_xaxes(range=[0, 105], title_text="Score (0–100)")
    return fig


def component_breakdown(results: dict, title="Component Scores by Rotation"):
    """Grouped bar: each component across rotations."""
    comp_order = ["water_fit", "climate_fit", "soil_rotation_diversity", "farmer_priority_fit"]
    comp_label = {"water_fit": "Water", "climate_fit": "Climate",
                  "soil_rotation_diversity": "Soil/Div.", "farmer_priority_fit": "Priority"}
    fig = go.Figure()
    for i, (name, r) in enumerate(results.items()):
        ys = []
        for c in comp_order:
            s = r["components"].get(c, {}).get("score")
            ys.append(s if s is not None else 0)
        fig.add_trace(go.Bar(name=name, x=[comp_label[c] for c in comp_order], y=ys,
                             marker_color=PALETTE[i % len(PALETTE)]))
    fig.update_layout(barmode="group")
    _base_layout(fig, title, height=400)
    fig.update_yaxes(range=[0, 105], title_text="Score (0–100)")
    return fig


def water_demand_gauge(mean_index: float, title="Rotation Water Demand"):
    """Simple gauge for a rotation's mean water-demand index (1..5)."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=mean_index,
        number={"suffix": " / 5"},
        gauge={"axis": {"range": [0, 5]},
               "bar": {"color": BLUE},
               "steps": [{"range": [0, 2], "color": "#D6F0E4"},
                         {"range": [2, 3.5], "color": PALE},
                         {"range": [3.5, 5], "color": "#FBE3C0"}]},
        title={"text": title, "font": {"size": 14, "color": NAVY}},
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
    return fig

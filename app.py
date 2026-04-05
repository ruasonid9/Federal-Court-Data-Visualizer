"""
Federal Court Case Explorer
----------------------------
Uses the free CourtListener API (courtlistener.com) to pull real federal
court opinions and visualize them by charge/topic type.

No API key required to get started — but you can register for a free
token at courtlistener.com to get higher rate limits.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Federal Court Explorer",
    page_icon="⚖️",
    layout="wide",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 2rem; }
    .stAlert { border-radius: 8px; }
    h1 { font-size: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
BASE_URL = "https://www.courtlistener.com/api/rest/v4/search/"

# Charge / topic presets — each maps to a search query sent to CourtListener
CHARGE_TYPES = {
    "Drug Offenses":        "drug possession trafficking narcotics",
    "Immigration":          "immigration deportation asylum removal",
    "Civil Rights (§1983)": "civil rights section 1983 excessive force",
    "White Collar / Fraud": "wire fraud securities fraud embezzlement",
    "Gun / Firearms":       "firearm weapon unlawful possession",
    "Sentencing":           "sentencing guidelines mandatory minimum",
}

# Federal circuit courts — label : CourtListener court slug
COURTS = {
    "All Federal Circuits": None,
    "1st Circuit":  "ca1",
    "2nd Circuit":  "ca2",
    "3rd Circuit":  "ca3",
    "4th Circuit":  "ca4",
    "5th Circuit":  "ca5",
    "6th Circuit":  "ca6",
    "7th Circuit":  "ca7",
    "8th Circuit":  "ca8",
    "9th Circuit":  "ca9",
    "10th Circuit": "ca10",
    "11th Circuit": "ca11",
    "D.C. Circuit": "cadc",
}


# ── API helper ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)   # cache results for 10 minutes so we don't hammer the API
def fetch_cases(query: str, court_slug: str | None,
                year_start: int, year_end: int,
                max_pages: int = 5) -> pd.DataFrame:
    """
    Hit the CourtListener search API and return a tidy DataFrame.
    We page through results (up to max_pages) to get enough data to chart.
    """
    all_results = []
    params = {
        "q":           query,
        "type":        "o",                        # "o" = opinions
        "order_by":    "score desc",
        "filed_after":  f"{year_start}-01-01",
        "filed_before": f"{year_end}-12-31",
        "format":      "json",
    }
    if court_slug:
        params["court"] = court_slug

    # Optional: add your CourtListener token here for higher rate limits
    headers = {
        # "Authorization": "Token YOUR_TOKEN_HERE"
    }

    next_url = BASE_URL
    for page in range(max_pages):
        try:
            resp = requests.get(next_url, params=params if page == 0 else {},
                                headers=headers, timeout=10)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error(f"API error: {e}")
            break

        data = resp.json()
        results = data.get("results", [])
        if not results:
            break

        all_results.extend(results)

        # Follow pagination
        next_url = data.get("next")
        if not next_url:
            break
        time.sleep(0.3)   # be polite to the API

    if not all_results:
        return pd.DataFrame()

    # ── Flatten the fields we care about ──────────────────────────────────────
    rows = []
    for r in all_results:
        # Date filed can be None for some old records — skip those
        filed = r.get("dateFiled") or r.get("date_filed")
        if not filed:
            continue
        rows.append({
            "case_name":   r.get("caseName") or r.get("case_name", "Unknown"),
            "court":       r.get("court", "Unknown"),
            "date_filed":  pd.to_datetime(filed, errors="coerce"),
            "year":        int(str(filed)[:4]),
            "status":      r.get("status", "Unknown"),
            "url":         "https://www.courtlistener.com" + r.get("absolute_url", ""),
        })

    df = pd.DataFrame(rows).dropna(subset=["date_filed"])
    return df


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚖️ Filters")

    charge_label = st.selectbox("Charge / Topic Type", list(CHARGE_TYPES.keys()))
    charge_query = CHARGE_TYPES[charge_label]

    court_label  = st.selectbox("Court", list(COURTS.keys()))
    court_slug   = COURTS[court_label]

    year_range = st.slider(
        "Year Range",
        min_value=2000,
        max_value=date.today().year,
        value=(2015, date.today().year),
    )

    st.divider()
    st.caption("Data from [CourtListener](https://www.courtlistener.com/) — Free Law Project")
    st.caption("Fetches up to ~500 recent matching opinions.")

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("Federal Court Case Explorer")
st.markdown(f"Showing **{charge_label}** cases · {court_label} · {year_range[0]}–{year_range[1]}")

with st.spinner("Fetching cases from CourtListener…"):
    df = fetch_cases(charge_query, court_slug, year_range[0], year_range[1])

if df.empty:
    st.warning("No cases found. Try broadening the filters (wider year range or 'All Federal Circuits').")
    st.stop()

# ── KPI Row ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Cases Found", f"{len(df):,}")
col2.metric("Courts Represented", df["court"].nunique())
col3.metric("Year Span", f"{df['year'].min()} – {df['year'].max()}")

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
left, right = st.columns(2)

# Bar chart — cases by court
with left:
    st.subheader("Cases by Court")
    court_counts = (
        df["court"]
        .value_counts()
        .reset_index()
        .rename(columns={"count": "Cases", "court": "Court"})
        .head(12)
    )
    fig_bar = px.bar(
        court_counts,
        x="Cases",
        y="Court",
        orientation="h",
        color="Cases",
        color_continuous_scale="Blues",
        template="plotly_white",
    )
    fig_bar.update_layout(
        coloraxis_showscale=False,
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Line chart — cases over time
with right:
    st.subheader("Filing Trend Over Time")
    yearly = df.groupby("year").size().reset_index(name="Cases")
    fig_line = px.line(
        yearly,
        x="year",
        y="Cases",
        markers=True,
        template="plotly_white",
        color_discrete_sequence=["#1d6fa4"],
    )
    fig_line.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Cases",
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig_line, use_container_width=True)

# Heatmap — cases by court × year (only if multi-court view)
if court_slug is None and df["court"].nunique() > 1:
    st.subheader("Court Activity Heatmap (Top 10 Courts)")
    top_courts = df["court"].value_counts().head(10).index.tolist()
    heat_df = (
        df[df["court"].isin(top_courts)]
        .groupby(["year", "court"])
        .size()
        .reset_index(name="Cases")
        .pivot(index="court", columns="year", values="Cases")
        .fillna(0)
    )
    fig_heat = px.imshow(
        heat_df,
        color_continuous_scale="Blues",
        aspect="auto",
        template="plotly_white",
        labels=dict(x="Year", y="Court", color="Cases"),
    )
    fig_heat.update_layout(margin=dict(l=0, r=0, t=10, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

# ── Case table ────────────────────────────────────────────────────────────────
st.subheader("Case List")
st.caption("Click a row to copy the case name. URLs link to the full opinion on CourtListener.")

display_df = df[["case_name", "court", "date_filed", "url"]].copy()
display_df["date_filed"] = display_df["date_filed"].dt.strftime("%Y-%m-%d")
display_df = display_df.rename(columns={
    "case_name":  "Case Name",
    "court":      "Court",
    "date_filed": "Date Filed",
    "url":        "Link",
})

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Link": st.column_config.LinkColumn("Opinion Link", display_text="View →")
    },
)

# ── Download ──────────────────────────────────────────────────────────────────
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download results as CSV",
    data=csv,
    file_name=f"court_cases_{charge_label.replace(' ', '_')}.csv",
    mime="text/csv",
)

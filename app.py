import json
import html
import pandas as pd
import streamlit as st
import folium
import plotly.graph_objects as go
from statistics_panel import show_statistics
from streamlit_folium import st_folium

st.set_page_config(page_title="AgriPriority Rwanda", page_icon="🌾", layout="wide")

DATA_FILE = "AgriPriority_Decision_Model_V3.csv"
MAP_FILE = "AgriPriority_Districts_30.geojson"
CATEGORIES = [
    "Priority field verification",
    "Investigate crop performance",
    "Environmental monitoring",
    "Routine monitoring",
]
PALETTE = {
    "Priority field verification": "#D15B57",
    "Investigate crop performance": "#DCA143",
    "Environmental monitoring": "#528FC4",
    "Routine monitoring": "#59A77E",
}
# Presentation helpers: colors convey screening categories, not probabilities.
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1320px;}
h1, h2, h3 {letter-spacing: -0.025em;}
div[data-testid="stMetric"] {
  background: #f7f9fb; border: 1px solid #e3e8ef;
  border-radius: 14px; padding: 18px 20px; min-height: 122px;
}
div[data-testid="stMetricLabel"] {
    font-weight: 550;
    min-height: 2.5rem;
    white-space: normal !important;
    overflow: visible !important;
}

div[data-testid="stMetricLabel"] p {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: anywhere;
    line-height: 1.25;
}
div[data-testid="stMetricValue"] {font-variant-numeric: tabular-nums;}
div[data-testid="stMetricValue"] div {
  font-size: clamp(1.35rem, 2vw, 2rem);
  overflow-wrap: anywhere;
}

[data-testid="stSidebar"] {border-right: 1px solid #e2e8f0;}
.ap-banner {padding: 17px 20px; border-radius: 14px;
  border: 1px solid; border-left-width: 6px; margin: 10px 0 18px;}
.ap-banner-title {font-size: 0.80rem; font-weight: 700; letter-spacing: .045em;
 text-transform: uppercase; margin-bottom: 4px;}
.ap-banner-category {font-size: 1.22rem; font-weight: 750;}
.ap-banner-copy {font-size: .92rem; margin-top: 8px;}
.ap-legend {display:flex; align-items:center; gap:9px;
  padding:9px 12px; border:1px solid #e2e8f0; border-radius:10px;
  font-size:.88rem; min-height: 53px;}
.ap-dot {width:13px; height:13px; border-radius:4px; flex:0 0 13px;}
</style>
""", unsafe_allow_html=True)

REQUIRED = [
    "district", "priority_category", "evidence_summary",
    "mean_cropland_ndvi_anomaly", "mean_rainfall_anomaly_percent",
    "change_maize_yield_kg_ha_2025_to_2026_pct",
    "change_bean_yield_kg_ha_2025_to_2026_pct",
    "nisr_physical_cultivated_land_ha_2026",
    "nisr_maize_cultivated_area_ha_2026",
    "priority_field_verification_count",
    "recommendation_stability_pct", "field_verification_frequency_pct",
    "stability_label",
]

@st.cache_data
def load_data():
    table = pd.read_csv(DATA_FILE)
    missing = [field for field in REQUIRED if field not in table.columns]
    if missing:
        raise ValueError("Missing CSV fields: " + ", ".join(missing))
    table["district"] = table["district"].astype(str).str.strip()
    if len(table) != 30 or table["district"].nunique() != 30:
        raise ValueError("Expected exactly 30 unique district records.")
    if table[REQUIRED].isna().any().any():
        raise ValueError("Missing values in required district indicators.")
    return table

@st.cache_data
def load_geo():
    with open(MAP_FILE, encoding="utf-8") as handle:
        boundaries = json.load(handle)
    return boundaries

def lon_lat_points(obj):
    """Extract map bounds from nested polygon and multipolygon coordinates."""
    if isinstance(obj, (list, tuple)):
        if len(obj) >= 2 and all(isinstance(x, (int, float)) for x in obj[:2]):
            yield (float(obj[0]), float(obj[1]))
        else:
            for child in obj:
                yield from lon_lat_points(child)

def get_clicked_district(map_response, valid_names):
    """GeoJSON clicks are returned as last_active_drawing in streamlit-folium."""
    if not map_response:
        return None
    clicked = map_response.get("last_active_drawing")
    if isinstance(clicked, dict):
        name = clicked.get("properties", {}).get("District")
        if name in valid_names:
            return name
    return None

try:
    df = load_data()
    geo = load_geo()
    geo_names = [f.get("properties", {}).get("District") for f in geo["features"]]
    if len(geo_names) != 30 or set(geo_names) != set(df["district"]):
        raise ValueError("District names in GeoJSON do not match the CSV.")
except Exception as exc:
    st.error(f"Unable to load AgriPriority data: {exc}")
    st.stop()

district_names = sorted(df["district"].tolist())
if st.session_state.get("chosen_district") not in district_names:
    st.session_state["chosen_district"] = district_names[0]
if "map_version" not in st.session_state:
    st.session_state["map_version"] = 0
if "map_focus" not in st.session_state:
    st.session_state["map_focus"] = "all"

# Each selected district gets a fresh selectbox key. This avoids writing
# to widget-owned session state after the widget has been instantiated.
def sidebar_district_changed(select_key):
    st.session_state["chosen_district"] = st.session_state[select_key]
    st.session_state["map_focus"] = "district"
    st.session_state["map_version"] += 1

def show_all_rwanda():
    st.session_state["map_focus"] = "all"
    st.session_state["map_version"] += 1

st.title("🌾 AgriPriority Rwanda")
st.caption("NISR Big Data Hackathon 2026 · District-level agricultural screening prototype")
st.warning(
    "These are preliminary screening recommendations, not validated crop-loss "
    "predictions or proof that rainfall caused a yield change."
)

with st.sidebar:
    st.header("Explore Rwanda")
    sidebar_key = f"district_select_{st.session_state['chosen_district']}"
    st.selectbox(
        "District profile",
        district_names,
        index=district_names.index(st.session_state["chosen_district"]),
        key=sidebar_key,
        on_change=sidebar_district_changed,
        args=(sidebar_key,),
        help="Selecting a district zooms to its boundaries; you can also click the map."
    )
    st.button("🌍 Show all Rwanda", on_click=show_all_rwanda, use_container_width=True)
    st.subheader("Show recommendation categories")
    enabled = {}
    for category in CATEGORIES:
        enabled[category] = st.checkbox(category, value=True, key=f"filter_{category}")
    st.caption(
        "NISR Season B 2025–2026; MODIS NDVI and CHIRPS rainfall for "
        "March–June 2026, compared with March–June 2019–2025."
    )

selected_district = st.session_state["chosen_district"]
lookup = df.set_index("district")
selected = lookup.loc[selected_district]
category_lookup = lookup["priority_category"].to_dict()
rain_lookup = lookup["mean_rainfall_anomaly_percent"].to_dict()
filtered = df.loc[df["priority_category"].map(enabled)].copy()

# Add display properties to a private, fresh GeoJSON object.
map_geo = json.loads(json.dumps(geo))
for feature in map_geo["features"]:
    name = feature["properties"]["District"]
    feature["properties"]["Recommendation"] = category_lookup[name]
    feature["properties"]["Rainfall anomaly (%)"] = round(float(rain_lookup[name]), 1)

# Calculate bounding rectangles for the national overview and each district.
# GeoJSON is in WGS84 (longitude, latitude). Folium uses (latitude, longitude).
all_points = [
    point
    for feature in geo["features"]
    for point in lon_lat_points(feature["geometry"]["coordinates"])
]
if not all_points:
    st.error("District GeoJSON does not contain usable map coordinates.")
    st.stop()

def points_bounds(points):
    min_lon = min(p[0] for p in points)
    max_lon = max(p[0] for p in points)
    min_lat = min(p[1] for p in points)
    max_lat = max(p[1] for p in points)
    return [[min_lat, min_lon], [max_lat, max_lon]]

rwanda_bounds = points_bounds(all_points)
selected_geometry = next(
    f["geometry"] for f in geo["features"]
    if f["properties"]["District"] == selected_district
)
district_bounds = points_bounds(list(lon_lat_points(selected_geometry["coordinates"])))
focus_on_district = st.session_state["map_focus"] == "district"
view_bounds = district_bounds if focus_on_district else rwanda_bounds

st.subheader("Interactive district map")
st.caption(
    "Selecting a district zooms to its boundaries. Click any district to update "
    "the profile; use 'Show all Rwanda' to return to the national view."
)

m = folium.Map(
    location=[
        (view_bounds[0][0] + view_bounds[1][0]) / 2,
        (view_bounds[0][1] + view_bounds[1][1]) / 2,
    ],
    zoom_start=6,
    tiles="OpenStreetMap",
    control_scale=True,
    prefer_canvas=True,
)
m.fit_bounds(view_bounds, padding=(36, 36), max_zoom=11 if focus_on_district else 6)

def style_polygon(feature):
    name = feature["properties"]["District"]
    category = category_lookup[name]
    visible = enabled.get(category, False)
    chosen = name == selected_district
    return {
        "fillColor": PALETTE[category] if visible else "#BFC5CA",
        "color": "#171717" if chosen else "#52525B",
        "weight": 4 if chosen else 0.8,
        "fillOpacity": 0.78 if visible else 0.12,
    }

folium.GeoJson(
    map_geo,
    name="District screening categories",
    style_function=style_polygon,
    highlight_function=lambda feature: {
        "color": "#111827",
        "weight": 3,
        "fillOpacity": 0.9,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["District", "Recommendation", "Rainfall anomaly (%)"],
        aliases=["District", "Category", "Rainfall anomaly (%)"],
        labels=True,
        sticky=True,
    ),
).add_to(m)

response = st_folium(
    m,
    key=f"agripriority_district_map_{st.session_state['map_version']}",
    use_container_width=True,
    height=570,
    returned_objects=["last_active_drawing"],
)

# A click updates the same profile controlled by the sidebar.
clicked_name = get_clicked_district(response, set(district_names))
if clicked_name and clicked_name != selected_district:
    st.session_state["chosen_district"] = clicked_name
    st.session_state["map_focus"] = "district"
    # Use a new map component after selection so an old click is not replayed.
    # Do not assign to the selectbox key here: Streamlit forbids that.
    st.session_state["map_version"] += 1
    st.rerun()

st.markdown("**Map legend**")
cols = st.columns(4)
for col, category in zip(cols, CATEGORIES):
    with col:
        st.markdown(
            '<div class="ap-legend">'
            f'<span class="ap-dot" style="background:{PALETTE[category]}"></span>'
            f'<span>{html.escape(category)}</span></div>',
            unsafe_allow_html=True,
        )

st.caption(
    "Grey districts are filtered out; selected district has a thick black border. "
    "Boundary source: supplied Rwanda shapefile (authority and publication date not independently verified)."
)

st.divider()
st.subheader(f"District profile — {selected_district}")
category_color = PALETTE[selected["priority_category"]]
st.markdown(
    '<div class="ap-banner" style="background:color-mix(in srgb, '
    f'{category_color} 11%, transparent);border-color:{category_color};">'
    '<div class="ap-banner-title">District screening recommendation</div>'
    f'<div class="ap-banner-category">{html.escape(str(selected["priority_category"]))}</div>'
    f'<div class="ap-banner-copy"><b>Evidence:</b> '
    f'{html.escape(str(selected["evidence_summary"]))}</div>'
    '</div>',
    unsafe_allow_html=True,
)

# Explain the screening evidence and the next reasonable field action.
def explain_district(row):
    rain = float(row["mean_rainfall_anomaly_percent"])
    ndvi = float(row["mean_cropland_ndvi_anomaly"])
    maize = float(row["change_maize_yield_kg_ha_2025_to_2026_pct"])
    beans = float(row["change_bean_yield_kg_ha_2025_to_2026_pct"])
    farmland = float(row["nisr_physical_cultivated_land_ha_2026"])
    category = row["priority_category"]
    findings = [
        f"CHIRPS rainfall was {abs(rain):.1f}% {'below' if rain < 0 else 'above'} "
        "the March–June 2019–2025 seasonal reference." if rain != 0 else
        "CHIRPS rainfall matched its historical seasonal reference.",
        f"MODIS cropland-masked NDVI changed by {ndvi:+.3f} versus the reference "
        f"({'lower' if ndvi < 0 else 'higher' if ndvi > 0 else 'unchanged'} greenness).",
        f"NISR maize yield changed {maize:+.1f}% and bean yield {beans:+.1f}% "
        "between Season B 2025 and Season B 2026.",
        f"NISR reports approximately {farmland:,.0f} hectares of physically cultivated land "
        "in this district for Season B 2026.",
    ]
    actions = {
        "Priority field verification": (
            "Prioritize a field review with local agronomists; check crop growth stage, "
            "rainfall timing, field conditions, pests and inputs before considering support."
        ),
        "Investigate crop performance": (
            "Review the yield change with agricultural extension officers and compare "
            "crop area, planting dates, pests, soil conditions and management practices."
        ),
        "Environmental monitoring": (
            "Track the next rainfall and vegetation observations and ask extension "
            "officers whether localized crop issues are being reported."
        ),
        "Routine monitoring": (
            "Continue regular monitoring; revisit the district if future indicators "
            "or verified field reports change."
        ),
    }
    stability = float(row["recommendation_stability_pct"])
    robustness = (
        f"The current category was repeated in {int(row['same_category_scenarios'])} "
        f"of 9 tested threshold scenarios ({stability:.1f}%). "
        "This measures sensitivity to chosen rules, NOT probability or validation accuracy."
    )
    return findings, actions.get(category, "Review the district indicators with local experts."), robustness

st.subheader("Why this district?")
st.caption("Evidence behind the provisional recommendation and suggested follow-up")
observations, proposed_action, robustness_note = explain_district(selected)
for observation in observations:
    st.markdown(f"- {observation}")
st.markdown(f"**Suggested next action:** {proposed_action}")
st.info(robustness_note)
st.caption(
    "The screening rules use illustrative rainfall (−15%) and yield (−5%) thresholds, "
    "and NDVI below its reference. A year-on-year yield change does not establish "
    "a cause, and the cropland mask is from 2021. These findings require field verification."
)

st.subheader("Key district indicators")
metric_columns = st.columns(4)
metric_columns[0].metric(
    "Rainfall anomaly",
    f"{selected['mean_rainfall_anomaly_percent']:+.1f}%",
    help="CHIRPS rainfall departure from the March–June historical reference.",
)
metric_columns[1].metric(
    "NDVI anomaly",
    f"{selected['mean_cropland_ndvi_anomaly']:+.3f}",
    help="MODIS cropland-masked NDVI change, not a direct crop-loss measure.",
)
metric_columns[2].metric(
    "Cultivated land (ha)",
    f"{selected['nisr_physical_cultivated_land_ha_2026']:,.0f}",
    help="NISR estimate of physically cultivated land for Season B 2026.",
)
metric_columns[3].metric(
    "Field-verification scenarios",
    f"{int(selected['priority_field_verification_count'])} / 9",
    help="Count of tested threshold scenarios; not a probability.",
)

left, right = st.columns(2, gap="large")
with left:
    st.subheader("NISR crop indicators")
    m1, m2 = st.columns(2)
    m1.metric("Maize yield · 2025–26", f"{selected['change_maize_yield_kg_ha_2025_to_2026_pct']:+.1f}%")
    m2.metric("Bean yield · 2025–26", f"{selected['change_bean_yield_kg_ha_2025_to_2026_pct']:+.1f}%")
    st.metric("Maize cultivated area · 2026", f"{selected['nisr_maize_cultivated_area_ha_2026']:,.0f} ha")

with right:
    st.subheader("Sensitivity to assumptions")
    s1, s2 = st.columns(2)
    s1.metric("V2 category stability", f"{selected['recommendation_stability_pct']:.1f}%")
    s2.metric("Field verification frequency", f"{selected['field_verification_frequency_pct']:.1f}%")
    st.markdown(f"**Classification stability:** {selected['stability_label']}")
    st.caption(
        "Nine scenarios test rainfall thresholds −10%, −15%, −20% and "
        "yield thresholds −3%, −5%, −10%. Frequency is NOT a probability."
    )

st.divider()
st.subheader("National comparison · 30 districts")
chart_counts = df["priority_category"].value_counts().reindex(CATEGORIES, fill_value=0)
chart_total = int(chart_counts.sum())
chart_percentages = [100 * int(chart_counts[category]) / chart_total if chart_total else 0 for category in CATEGORIES]
category_chart = go.Figure(
    go.Bar(
        x=[int(chart_counts[category]) for category in CATEGORIES],
        y=CATEGORIES,
        orientation="h",
        marker=dict(
            color=[PALETTE[category] for category in CATEGORIES],
            line=dict(color="#FFFFFF", width=1.5),
        ),
        text=[f"{int(chart_counts[category])} ({percentage:.1f}%)" for category, percentage in zip(CATEGORIES, chart_percentages)],
        textposition="outside",
        cliponaxis=False,
        customdata=chart_percentages,
        hovertemplate="<b>%{y}</b><br>Districts: %{x}<br>Share of districts: %{customdata:.1f}%<extra></extra>",
    )
)
category_chart.update_layout(
    title=dict(text="Districts by screening category", font=dict(size=18, color="#263445"), x=0),
    font=dict(family="Arial, sans-serif", size=12, color="#475569"),
    height=340,
    margin=dict(l=12, r=80, t=55, b=30),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
    bargap=0.35,
)
category_chart.update_xaxes(title_text="Number of districts", dtick=5, rangemode="tozero", showgrid=True, gridcolor="rgba(148,163,184,0.22)", zeroline=False)
category_chart.update_yaxes(title_text="", autorange="reversed", showgrid=False)
st.plotly_chart(category_chart, use_container_width=True, key="national_category_chart")
st.caption("Bar labels show the district count and percentage of all 30 districts. Colours match the map and statistical evidence charts.")
view_fields = [
    "district", "priority_category",
    "mean_rainfall_anomaly_percent", "mean_cropland_ndvi_anomaly",
    "change_maize_yield_kg_ha_2025_to_2026_pct",
    "change_bean_yield_kg_ha_2025_to_2026_pct",
    "nisr_physical_cultivated_land_ha_2026",
    "priority_field_verification_count", "recommendation_stability_pct",
]
st.dataframe(
    filtered[view_fields].rename(columns={
        "district": "District",
        "priority_category": "Recommendation",
        "mean_rainfall_anomaly_percent": "Rainfall anomaly (%)",
        "mean_cropland_ndvi_anomaly": "NDVI anomaly",
        "change_maize_yield_kg_ha_2025_to_2026_pct": "Maize yield change (%)",
        "change_bean_yield_kg_ha_2025_to_2026_pct": "Bean yield change (%)",
        "nisr_physical_cultivated_land_ha_2026": "NISR cultivated land (ha)",
        "priority_field_verification_count": "Field-verification scenarios",
        "recommendation_stability_pct": "Category stability (%)",
    }),
    use_container_width=True, hide_index=True
)
st.download_button(
    "Download filtered district results (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="AgriPriority_filtered_districts.csv",
    mime="text/csv",
)

show_statistics(df)

with st.expander("Sources, screening rules and limitations"):
    st.markdown("""
**Sources:** NISR Seasonal Agricultural Survey, Season B 2025 and 2026;
MODIS MOD13Q1 NDVI; CHIRPS daily rainfall; ESA WorldCover 2021
cropland mask. District boundaries supplied by the project team.

**V2 screening rules:** A district is flagged for an environmental concern
if its rainfall anomaly is ≤ −15% or NDVI anomaly is below 0.
An agricultural performance concern is flagged if maize or bean yield changed
by ≤ −5%. Field verification is indicated when at least one environmental
and one agricultural concern coincide.

**V3 sensitivity:** Nine scenarios vary rainfall thresholds (−10%, −15%,
−20%) and yield thresholds (−3%, −5%, −10%). Stability describes
agreement across these assumed rules. It does not measure model accuracy,
probability of crop failure, or confidence in source-data quality.

**Important limitations:** MODIS NDVI represents mixed 250 m pixels, not
individual farms; the cropland mask reflects 2021, not 2026; seasonal
NDVI does not perfectly correspond to crop growth cycles; CHIRPS is
coarser than NDVI; survey statistics carry uncertainty, and historical
changes do not prove causal effects of rainfall. Boundary source authority
and date must be confirmed. This prototype supports prioritizing review,
not allocating resources without field verification.
""")

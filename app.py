import json
import pandas as pd
import streamlit as st
import folium
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
    "Priority field verification": "#C4473C",
    "Investigate crop performance": "#E6A23C",
    "Environmental monitoring": "#438DBD",
    "Routine monitoring": "#58A76B",
}
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
if st.session_state.get("district_select") not in district_names:
    st.session_state["district_select"] = st.session_state["chosen_district"]

def sidebar_district_changed():
    st.session_state["chosen_district"] = st.session_state["district_select"]

st.title("🌾 AgriPriority Rwanda")
st.caption("NISR Big Data Hackathon 2026 · District-level agricultural screening prototype")
st.warning(
    "These are preliminary screening recommendations, not validated crop-loss "
    "predictions or proof that rainfall caused a yield change."
)

with st.sidebar:
    st.header("Explore Rwanda")
    st.selectbox(
        "District profile",
        district_names,
        key="district_select",
        on_change=sidebar_district_changed,
        help="You can also click a polygon on the map."
    )
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

# Fit Rwanda boundary to the map on every application update.
all_points = [
    point
    for feature in geo["features"]
    for point in lon_lat_points(feature["geometry"]["coordinates"])
]
if not all_points:
    st.error("District GeoJSON does not contain usable map coordinates.")
    st.stop()
min_lon = min(p[0] for p in all_points)
max_lon = max(p[0] for p in all_points)
min_lat = min(p[1] for p in all_points)
max_lat = max(p[1] for p in all_points)

st.subheader("Interactive district map")
st.caption("Click a district to update the profile below. Hover over a district to see its recommendation and rainfall anomaly.")

m = folium.Map(
    location=[(min_lat + max_lat) / 2, (min_lon + max_lon) / 2],
    zoom_start=8,
    tiles="OpenStreetMap",
    control_scale=True,
    prefer_canvas=True,
)
m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]], padding=(20, 20))

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
    key="agripriority_district_map",
    use_container_width=True,
    height=570,
    returned_objects=["last_active_drawing"],
)

# A click updates the same profile controlled by the sidebar.
clicked_name = get_clicked_district(response, set(district_names))
if clicked_name and clicked_name != selected_district:
    st.session_state["chosen_district"] = clicked_name
    st.session_state["district_select"] = clicked_name
    st.rerun()

st.markdown("**Map legend**")
cols = st.columns(4)
for col, category in zip(cols, CATEGORIES):
    with col:
        st.markdown(
            f'<span style="display:inline-block;background:{PALETTE[category]};'
            f'width:14px;height:14px;border-radius:3px;vertical-align:middle;'
            f'margin-right:6px"></span>{category}',
            unsafe_allow_html=True,
        )
st.caption(
    "Grey districts are filtered out; selected district has a thick black border. "
    "Boundary source: supplied Rwanda shapefile (authority and publication date not independently verified)."
)

st.divider()
st.subheader(f"District profile — {selected_district}")
st.write("**V2 screening recommendation:**", selected["priority_category"])
st.write("**Supporting evidence:**", selected["evidence_summary"])

metric_columns = st.columns(4)
metric_columns[0].metric(
    "Rainfall anomaly",
    f"{selected['mean_rainfall_anomaly_percent']:+.1f}%",
)
metric_columns[1].metric(
    "NDVI anomaly",
    f"{selected['mean_cropland_ndvi_anomaly']:+.3f}",
)
metric_columns[2].metric(
    "NISR cultivated land",
    f"{selected['nisr_physical_cultivated_land_ha_2026']:,.0f} ha",
)
metric_columns[3].metric(
    "Field-verification scenarios",
    f"{int(selected['priority_field_verification_count'])} / 9",
)

left, right = st.columns(2)
with left:
    st.subheader("NISR crop indicators")
    st.metric(
        "Maize yield change · 2025–2026",
        f"{selected['change_maize_yield_kg_ha_2025_to_2026_pct']:+.1f}%",
    )
    st.metric(
        "Bean yield change · 2025–2026",
        f"{selected['change_bean_yield_kg_ha_2025_to_2026_pct']:+.1f}%",
    )
    st.metric(
        "Maize cultivated area · 2026",
        f"{selected['nisr_maize_cultivated_area_ha_2026']:,.0f} ha",
    )

with right:
    st.subheader("Sensitivity to assumptions")
    st.metric(
        "Same V2 category across scenarios",
        f"{selected['recommendation_stability_pct']:.1f}%",
    )
    st.write("**Classification stability:**", selected["stability_label"])
    st.metric(
        "Field-verification scenario frequency",
        f"{selected['field_verification_frequency_pct']:.1f}%",
    )
    st.caption(
        "Nine scenarios test rainfall thresholds −10%, −15%, −20% and "
        "yield thresholds −3%, −5%, −10%. Frequency is NOT a probability."
    )

st.divider()
st.subheader("National comparison · 30 districts")
st.bar_chart(
    df["priority_category"].value_counts().reindex(CATEGORIES, fill_value=0)
    .rename("Districts")
)
view_fields = [
    "district", "priority_category",
    "mean_rainfall_anomaly_percent", "mean_cropland_ndvi_anomaly",
    "change_maize_yield_kg_ha_2025_to_2026_pct",
    "change_bean_yield_kg_ha_2025_to_2026_pct",
    "nisr_physical_cultivated_land_ha_2026",
    "priority_field_verification_count", "recommendation_stability_pct",
]
st.dataframe(filtered[view_fields], use_container_width=True, hide_index=True)
st.download_button(
    "Download filtered district results (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="AgriPriority_filtered_districts.csv",
    mime="text/csv",
)

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

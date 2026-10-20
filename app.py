import pandas as pd
import streamlit as st

st.set_page_config(page_title='AgriPriority Rwanda', page_icon='🌾', layout='wide')

DATA_FILE = 'AgriPriority_Decision_Model_V3.csv'
CATEGORIES = ['Priority field verification', 'Investigate crop performance', 'Environmental monitoring', 'Routine monitoring']

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    necessary = ['district', 'priority_category', 'evidence_summary', 'mean_cropland_ndvi_anomaly',
                 'mean_rainfall_anomaly_percent', 'change_maize_yield_kg_ha_2025_to_2026_pct',
                 'change_bean_yield_kg_ha_2025_to_2026_pct', 'nisr_physical_cultivated_land_ha_2026',
                 'nisr_maize_cultivated_area_ha_2026', 'priority_field_verification_count',
                 'recommendation_stability_pct', 'field_verification_frequency_pct', 'stability_label']
    missing = [c for c in necessary if c not in df.columns]
    if missing:
        raise ValueError('Missing columns: ' + ', '.join(missing))
    if len(df) != 30 or df['district'].nunique() != 30:
        raise ValueError('Dataset must contain exactly 30 unique Rwanda districts')
    df['district'] = df['district'].astype(str).str.strip()
    return df

try:
    df = load_data()
except Exception as exc:
    st.error(f'Unable to load district data: {exc}')
    st.stop()

st.title('🌾 AgriPriority Rwanda')
st.caption('NISR Big Data Hackathon 2026 · District-level agricultural screening prototype')
st.warning('Screening information only. These indicators do not establish crop failure, forecast yield, or prove rainfall caused a yield change.')

with st.sidebar:
    st.header('Explore Rwanda')
    district = st.selectbox('Select district', sorted(df['district'].unique()))
    selected_categories = st.multiselect('Filter recommendations', CATEGORIES, default=CATEGORIES)
    st.caption('Reference: NISR Season B 2025–2026; MODIS NDVI and CHIRPS rainfall for March–June 2026 compared with March–June 2019–2025.')

row = df.loc[df['district'].eq(district)].iloc[0]
filtered = df[df['priority_category'].isin(selected_categories)].copy()

# ------------------------------------------------------------------
# Geographic overview from user-supplied district polygons.
# Shapefile converted from TM_Rwanda to EPSG:4326 (GeoJSON).
# ------------------------------------------------------------------
import json
import folium
from streamlit_folium import st_folium

MAP_FILE = 'AgriPriority_Districts_30.geojson'
@st.cache_data
def read_boundaries():
    with open(MAP_FILE, encoding='utf-8') as f:
        geo = json.load(f)
    district_names = {feature['properties']['District'] for feature in geo['features']}
    if len(geo['features']) != 30 or district_names != set(df['district']):
        raise ValueError('District boundary names do not match the 30 district records')
    return geo

try:
    geo = read_boundaries()
    st.subheader('Interactive district map')
    st.caption('Colours show provisional V2 recommendation categories. Hover over a polygon for district details; use the sidebar to switch the district profile.')
    category_by_district = dict(zip(df.district, df.priority_category))
    rainfall_by_district = dict(zip(df.district, df.mean_rainfall_anomaly_percent))
    selected_set = set(filtered.district)
    palette = {
        'Priority field verification': '#C0392B',
        'Investigate crop performance': '#E6A23C',
        'Environmental monitoring': '#4E9CD3',
        'Routine monitoring': '#58A76B',
    }
    for feature in geo['features']:
        name = feature['properties']['District']
        feature['properties']['Recommendation'] = category_by_district[name]
        feature['properties']['Rainfall anomaly (%)'] = round(float(rainfall_by_district[name]), 1)
    m = folium.Map(location=[-1.94, 29.87], zoom_start=8, tiles='CartoDB positron')
    folium.GeoJson(
        geo,
        name='District recommendation',
        style_function=lambda feature: {
            'fillColor': palette.get(category_by_district[feature['properties']['District']], '#aaaaaa')
                 if feature['properties']['District'] in selected_set else '#cccccc',
            'color': '#222222' if feature['properties']['District'] == district else '#555555',
            'weight': 3 if feature['properties']['District'] == district else 0.8,
            'fillOpacity': 0.82 if feature['properties']['District'] in selected_set else 0.16,
        },
        highlight_function=lambda _: {'weight': 3, 'color': '#121212', 'fillOpacity': 0.95},
        tooltip=folium.GeoJsonTooltip(
            fields=['District', 'Recommendation', 'Rainfall anomaly (%)'],
            labels=True,
            sticky=True,
        ),
    ).add_to(m)
    st_folium(m, height=485, use_container_width=True, returned_objects=[])
    st.caption('Red: field verification · Orange: investigate crop performance · Blue: environmental monitoring · Green: routine monitoring · Grey: filtered out. Boundaries from supplied shapefile; publication authority/date not independently verified.')
except Exception as exc:
    st.error(f'Map unavailable: {exc}')

st.subheader(f'District profile — {district}')
st.write('**V2 recommendation:**', row['priority_category'])
st.write('**Evidence:**', row['evidence_summary'])

m1, m2, m3, m4 = st.columns(4)
m1.metric('Rainfall anomaly', f"{row['mean_rainfall_anomaly_percent']:+.1f}%")
m2.metric('NDVI anomaly', f"{row['mean_cropland_ndvi_anomaly']:+.3f}")
m3.metric('NISR cultivated land', f"{row['nisr_physical_cultivated_land_ha_2026']:,.0f} ha")
m4.metric('Field-verification scenarios', f"{int(row['priority_field_verification_count'])} / 9")

c1, c2 = st.columns(2)
with c1:
    st.subheader('NISR crop indicators')
    st.metric('Maize yield change, 2025 → 2026', f"{row['change_maize_yield_kg_ha_2025_to_2026_pct']:+.1f}%")
    st.metric('Bean yield change, 2025 → 2026', f"{row['change_bean_yield_kg_ha_2025_to_2026_pct']:+.1f}%")
    st.metric('Maize cultivated area (2026)', f"{row['nisr_maize_cultivated_area_ha_2026']:,.0f} ha")
with c2:
    st.subheader('Sensitivity to assumptions')
    st.metric('Same V2 category across scenarios', f"{row['recommendation_stability_pct']:.1f}%")
    st.write('**Classification stability:**', row['stability_label'])
    st.metric('Field-verification frequency', f"{row['field_verification_frequency_pct']:.1f}%")
    st.caption('Nine scenarios: rainfall thresholds −10%, −15%, −20%, and yield decline thresholds −3%, −5%, −10%. Frequencies describe rule sensitivity—not probabilities or accuracy.')

st.divider()
st.subheader('National comparison — all 30 districts')
summary = df['priority_category'].value_counts().reindex(CATEGORIES, fill_value=0)
st.bar_chart(summary.rename('Districts'))

show_cols = ['district', 'priority_category', 'mean_rainfall_anomaly_percent',
             'mean_cropland_ndvi_anomaly', 'change_maize_yield_kg_ha_2025_to_2026_pct',
             'change_bean_yield_kg_ha_2025_to_2026_pct', 'nisr_physical_cultivated_land_ha_2026',
             'priority_field_verification_count', 'recommendation_stability_pct']
st.dataframe(filtered[show_cols], hide_index=True, use_container_width=True)
st.download_button('Download filtered results (CSV)', filtered.to_csv(index=False).encode('utf-8'), 'AgriPriority_filtered_districts.csv', mime='text/csv')

with st.expander('Methods, sources and limitations', expanded=False):
    st.markdown('''
**Sources:** NISR Seasonal Agricultural Survey, Season B 2025 and 2026; MODIS MOD13Q1 NDVI; CHIRPS daily rainfall; ESA WorldCover 2021 cropland mask; GAUL 2015 administrative units (provisional mapping reference).

**V2 screening rules:** rainfall anomaly ≤ −15%, NDVI anomaly < 0, or maize/bean yield change ≤ −5%. A field-verification recommendation occurs when at least one environmental signal and at least one crop-yield signal coincide. Scenarios vary rainfall thresholds (−10/−15/−20%) and yield thresholds (−3/−5/−10%).

**Limitations:** threshold choices are illustrative and unvalidated; MODIS 250 m mixed pixels cannot identify individual farm conditions; cropland mask represents 2021; NDVI greenness is not equivalent to crop yield or crop damage; March–June composites do not resolve all planting/harvest differences; CHIRPS is coarser than NDVI and rainfall anomalies are not proof of causality; district-wide NISR estimates contain survey uncertainty. No farm-level conclusions should be drawn. District polygons come from a user-supplied Rwanda shapefile, simplified for web display; its original publication authority and date have not been independently verified.

**Interpretation:** 'High stability' is consistency of a V2 label across the nine selected scenarios, **not** validation confidence, model precision, or likelihood of crop failure.
''')

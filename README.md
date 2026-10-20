# AgriPriority Rwanda — Streamlit Prototype

An interactive dashboard for the NISR Big Data Hackathon 2026, using a 30-district agricultural screening dataset developed from NISR Season B 2025–2026 indicators, MODIS NDVI and CHIRPS rainfall anomalies.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Create a public GitHub repository.
2. Upload `app.py`, `requirements.txt`, and `AgriPriority_Decision_Model_V3.csv` to the repository root.
3. At https://share.streamlit.io/ choose **Create app** and select the repository, branch, and `app.py`.
4. Deploy, test the district selector and charts, and share the public URL.

## Methods and caution

The dashboard shows **screening classifications**, not independently validated crop-loss predictions. The default thresholds are illustrative; the robustness percentages describe how often classifications hold under nine prespecified threshold scenarios. The app does not contain a GIS map because no matching district polygon geometry is bundled.

## Attribution and disclosure

Underlying sources include NISR Seasonal Agricultural Survey Season B 2025 and 2026, MODIS MOD13Q1, CHIRPS and ESA WorldCover 2021. Verify the provenance and licenses of the source tables before submission. The hackathon requires disclosure of AI assistance; this prototype's application code was drafted with ChatGPT assistance and should be reviewed and tested by the participating team.


## Interactive district map
Upload `AgriPriority_Districts_30.geojson` to the repository root. The map displays the provisional district recommendation category; the sidebar selects the district profile. The GeoJSON was created from the supplied DISTRICT_RW.zip, converted to WGS84 and simplified by 75 m for performance. Verify original boundary provenance before calling it official.

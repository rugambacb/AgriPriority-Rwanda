# AgriPriority Rwanda — Visual Release V3.4
Preserves the working Version 3.3 GIS map, auto district zoom, map-click selection, NISR/MODIS/CHIRPS data, and nine-scenario screening.

## What's new
- Softer consistent recommendation palette (map, legend, recommendation card, chart).
- Highlighted district recommendation banner.
- Bordered KPI cards and clearer 2-column NISR/sensitivity panel.
- Horizontal color-matched national comparison chart.
- Human-readable table column labels. CSV export keeps original field names.

## Deploy
Upload all five files to root of the existing GitHub repository, replacing matching filenames; commit. Existing Streamlit Cloud app auto redeploys with `app.py`. Do not upload the ZIP itself.

## Validate
Select Kayonza and inspect recommendation banner, metrics and chart. Click Kirehe and confirm map zoom/profile. Use Show all Rwanda, filters and CSV download. Check app logs if a dependency error appears.

## Scientific notice
These are preliminary screening categories, NOT validated crop-loss predictions. Rainfall and NDVI are indicators; thresholds are illustrative. Confirm boundary source and source-date provenance before official use.

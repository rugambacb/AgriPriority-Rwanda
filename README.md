# AgriPriority Rwanda — V3.4.1 stability fix

Fixes the app-startup crash from Altair imports in the Python 3.14 Streamlit Cloud environment.
The color-coded national comparison chart now uses dependency-free HTML bars.
All map click/zoom interactions, 30-district geometry, NISR stats, metrics, legend, and recommendations remain unchanged.

## Deployment
Extract this ZIP, upload all five files directly to the existing GitHub repository root and commit, replacing old versions. Streamlit Community Cloud will redeploy automatically. Entry file is `app.py`.

## Quick checks
- App loads with no import traceback.
- Select Kayonza: the "Why this district?" and KPI cards appear.
- Chart shows 4 colored horizontal bars with counts 4, 4, 15, 7.
- Click Kirehe on the map; district profile and zoom update.
- "Show all Rwanda" returns to overview.

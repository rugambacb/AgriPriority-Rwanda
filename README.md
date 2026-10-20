# AgriPriority Rwanda — interactive district map V3

Streamlit dashboard with 30 districts, NISR Season B 2025–2026 indicators, MODIS NDVI, CHIRPS rainfall, and nine-scenario classification stability.

## Deployment (Streamlit Community Cloud)
1. Upload **all five files** in this folder to the root of the public `AgriPriority-Rwanda` GitHub repository.
2. Keep the branch `main` and the Streamlit entry point `app.py`.
3. Streamlit Community Cloud will redeploy after you commit.

## Main improvements
- Automatically fits the Rwanda boundaries on the interactive map.
- Clicking a district polygon updates the sidebar selection and profile.
- Selected district has a thick black outline.
- Checkbox category filters replace multiselect tags.
- Inline category legend under the map.
- OpenStreetMap tiles (no CARTO key required).

## Validation checklist
- Open the app and click Kirehe; sidebar and district profile should show Kirehe.
- Pick Bugesera from sidebar; its map polygon should have a thick outline.
- Disable a category; its polygons should become grey.
- Verify the whole country fits in the map.
- Confirm all 30 rows appear if all filters are enabled.

## Scientific limitations
V2 categories and V3 robustness figures are *screening tools*, not validated predictions. MODIS pixels are mixed at ~250 m, WorldCover cropland mask is from 2021, CHIRPS rainfall is coarser, and NISR reported changes do not establish causation. District polygon origin needs source verification.

## Version 3.1 patch
- Fixes `StreamlitWidgetAlreadyInstantiatedError` after clicking a polygon: the sidebar selectbox key is never assigned after widget creation.
- Gives each new map interaction a new component key so old click events are not replayed on rerun.
- Limits first-visit zoom to level 6 to show all Rwanda district polygons in the embedded map.
- Deployment: replace all five files in the root of your existing GitHub repository and commit. No new Streamlit app is required.

Live Streamlit behavior must be tested after deploying; syntax and local input validation have been checked.

## Version 3.2: Zoom to selected district
- Selecting a district from the sidebar automatically frames its full polygon.
- Clicking a district polygon frames it and updates the profile.
- **Show all Rwanda** resets to a full-country overview without clearing the selection.
- The selected district retains its thick outline and all NISR indicators are unchanged.

## V3.3 addition
The district profile now includes a “Why this district?” panel: four evidence statements, a category-specific follow-up action, and V3 sensitivity context. No existing model thresholds or ranking values were changed.

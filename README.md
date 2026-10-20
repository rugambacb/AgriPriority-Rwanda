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

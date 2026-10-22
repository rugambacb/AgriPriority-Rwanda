# AgriPriority Streamlit — UI Fix v2

This package preserves the existing AgriPriority screening logic, 30-district datasets, map interactions, and statistical evidence. It contains targeted presentation fixes based on the latest deployed screenshots.

## Changes in this version

- Shortened KPI labels so Streamlit cards can display them without ellipses, with tooltips retaining the fuller meaning.
- Forced the NISR 2025-versus-2026 comparison chart to use a categorical year axis, preventing misleading fractional year ticks such as 2024.5 and 2025.5.
- Shortened national-comparison table headings and added concise number formatting/tooltips for rainfall, NDVI, crop yield, cultivated land, field checks, and stability.
- Kept the sensitivity heatmap scenario labels compact and allowed more bottom margin for them.
- Preserved the underlying screening rules and values; these are display/layout changes, not changes to statistical calculations.

## Deployment

1. Extract this ZIP.
2. In the GitHub repository used by Streamlit Community Cloud, replace `app.py` and `statistics_panel.py` with the versions in this package. Keep both files in the repository root beside the CSV and GeoJSON files.
3. Keep `requirements.txt` compatible with the existing app (this package retains the project's requirements).
4. Commit the changes and wait for Streamlit Cloud to finish redeploying.
5. Refresh the app and check the district KPI cards, the national comparison table, the NISR year-comparison chart, and the Sensitivity evidence tab.

If the repository has newer or independently updated data files, keep those current data files rather than overwriting them with older copies from this package. Only the two Python files need to change for the UI fixes.

## Validation performed

- Python syntax compilation passed for `app.py` and `statistics_panel.py`.
- Both included CSV datasets contain 30 rows for 30 unique districts.
- Static Plotly check confirmed the NISR comparison x-axis is explicitly categorical with ticks `2025` and `2026`.
- A live Streamlit browser render was not available in this environment, so visual confirmation after redeployment is still needed.

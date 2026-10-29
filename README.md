# AgriPriority Rwanda — V4.3 National Statistical Insights

This builds directly on the latest working `UI_FIX_v2` package and keeps the existing map, district profiles, year comparison, comparisons, scatterplots, sensitivity heatmap, NISR files, and threshold logic. The only additions are `national_insights.py` and two integration lines in `app.py`.

## Deploy
Upload all 8 files directly to the existing GitHub repository root, replacing matching files. Main file `app.py`. Streamlit Community Cloud will redeploy after commit.

## New section
After the existing Agricultural Statistics & Evidence Center, scroll to **National Statistical Insights**:
1. District rankings: choose indicator, direction and 5/10/15/30 districts.
2. Descriptive statistics: distribution, mean, median, min, max, sample standard deviation and number of observations.
3. Crop performance contrasts: compare positive/negative maize and bean yield changes and download filtered CSV.

## Interpretation
All results are descriptive and district-level. Survey-based yields may carry uncertainty. Districts are not weighted by cultivated area. Screening categories and nine-scenario classifications are not modified. Agricultural loss, causal effects, and model predictive accuracy are NOT estimated.

## Testing
Check Bugesera district profile, map click selection and zoom, each old statistics tab, then the three new insights tabs. Test empty crop-pattern selection.

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

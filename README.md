# AgriPriority Rwanda — Version 4.0: Statistical Evidence Dashboard

Preserves the working Map V3.4.1 district selection, automatic map zoom, category filters, agricultural explanation and V3 screening model. Adds interactive statistics with real NISR Season B 2025–2026 comparisons for all 30 districts.

## Install and deploy
Upload **all seven files** directly to your existing GitHub repository root (replace matching filenames). Entry point: `app.py`. Commit and Streamlit Community Cloud should redeploy.

New files: `statistics_panel.py` and `AgriPriority_NISR_SeasonB_2025_2026_Comparison_v1.csv`. Version 4 requires Plotly 6.4 or later as listed in `requirements.txt`. V3.4.1 avoided Altair because of an import incompatibility in a Python 3.14 environment. This release **does not import Altair**; Plotly is a separate library and must still be verified in your deployed environment.

## New tabs
1. NISR year comparison: select crop, measure and district; see 2025 vs 2026.
2. Compare districts: grouped analysis of chosen statistics.
3. Environmental relationships: interactive scatter chart and descriptive Pearson correlation (n=30 when no missingness).
4. Sensitivity evidence: heatmap of nine classification scenarios.

## Technical and scientific notes
- The NISR comparison file contains earlier exploratory June–August columns, but V4 charts only use the selected NISR 2025/2026 fields. The active V3 satellite/model file is the season-aligned MODIS/CHIRPS workflow.
- Empty crop cells are not converted to zeros; displays omit missing observations.
- Charts are descriptive and cannot establish crop-loss causation or probability.
- NISR Table 29 has a source-year discrepancy and is excluded.
- Validate original boundary dataset provenance and survey uncertainty before formal planning decisions.

## UI readability update (October 2026)
- KPI metric labels and values now explicitly override Streamlit truncation styles and can wrap instead of ending in ellipses.
- Sensitivity heatmap scenario labels use compact rainfall/yield thresholds, rotated labels, adjusted margins, and height based on the number of selected districts.
- No district data, decision thresholds, source values, or statistical calculations were changed for this UI update.

## Quick checks
Open the application, click Kirehe on the map, verify automatic zoom, then scroll to the Statistical Evidence Center. Choose Maize > Yield > Kayonza, inspect the 2025/2026 chart. Try the scatter plot and heatmap.

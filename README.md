# AgriPriority Rwanda — Version 4.1 Visual Refresh

This update improves chart clarity and consistency while preserving the existing district data, screening logic, map interactions, and statistical calculations.

## Visual improvements

- Uses a consistent screening-category palette across the map, national category chart, district comparisons, scatterplot, and sensitivity heatmap.
- Replaces the static national category bars with an interactive chart showing district counts and percentages.
- Makes 2025 and 2026 easier to distinguish in NISR year comparisons, with value labels and more readable hover details.
- Colours district-comparison bars by their existing screening category and keeps district values labelled.
- Improves scatterplot labels, hover precision, point contrast, axis styling, and the zero-change reference line.
- Clarifies sensitivity heatmap cells with `FLAG` / dash labels, compact scenario labels, and clearer hover text.
- Reduces the chance that long district-indicator values are clipped in metric cards.

## Deploy to the existing Streamlit Community Cloud app

1. Open the GitHub repository connected to the existing Streamlit app.
2. Upload **all seven files in this folder** to the repository root and replace the matching files:
   - `app.py`
   - `statistics_panel.py`
   - `requirements.txt`
   - `AgriPriority_Decision_Model_V3.csv`
   - `AgriPriority_Districts_30.geojson`
   - `AgriPriority_NISR_SeasonB_2025_2026_Comparison_v1.csv`
   - `README.md`
3. Commit the changes and allow Streamlit Community Cloud to redeploy.
4. Verify district selection and map zoom, then test each of the four Statistical Evidence Center tabs.

The application entry point remains `app.py`. The project does not import Altair. Plotly remains required as specified in `requirements.txt`.

## Scientific interpretation

The charts are descriptive. District-level relationships do not establish causation, two years do not establish a long-term trend, and screening categories are not probabilities or validated crop-loss predictions. Missing survey values are not replaced with zero. Field verification and source-data validation remain necessary before operational decisions.

# AgriPriority V4.4 — Executive Statistical Overview

Built on working V4.3. Adds an executive overview at the top with 30-district metrics, the existing four screening-category counts, the five lowest rainfall/maize-yield/bean-yield changes, and scientific interpretation. Interactive selector switches the latter chart.

## Deployment

Upload all 9 ZIP contents into the **root** of the existing GitHub repository, replacing files with the same names. Set Streamlit entrypoint to `app.py`. Commit to redeploy.

New file: `executive_overview.py`. All other data, rules, maps, the four original stats tabs and V4.3 national-insights tabs are preserved.

## Important limitations

Figures are descriptive, based on 30 districts. The average rainfall anomaly is not area-weighted. Rankings do not imply confirmed crop losses, causal relationships, or predictive confidence. Two NISR survey years do not establish a long-term trend.

## Quick test

Open app: look for Executive statistical overview before interactive district map. Change ranking selector across rainfall, maize and beans. Then verify clicking a map district still updates the profile, and previous detailed analysis tabs still work.

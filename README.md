# AgriPriority Rwanda

### Turning Agricultural Data into Actionable Evidence

**Developed by Team TerraSignal**\
**NISR Big Data Hackathon 2026 · Agricultural Productivity Track**

------------------------------------------------------------------------

## Project Overview

AgriPriority Rwanda is an interactive, geospatial decision-support
platform developed to help identify districts that may require closer
agricultural investigation and field verification.

The platform brings together district-level agricultural statistics from
the National Institute of Statistics of Rwanda (NISR) and environmental
indicators derived from satellite and rainfall datasets. It presents
this evidence through interactive maps, district profiles, statistical
comparisons, and sensitivity analysis.

By connecting agricultural performance with environmental conditions,
AgriPriority helps users explore where important changes are occurring,
understand the evidence behind district-level screening results, and
identify where further investigation may be useful.

**AgriPriority is an evidence-screening and prioritization tool. It does
not predict crop failure, establish the causes of yield changes, or
replace field assessments by agricultural professionals.**

## The Challenge

Agricultural conditions vary across Rwanda's districts. Changes in crop
yields, cultivated and harvested areas, rainfall, and vegetation
conditions can provide important signals, but these indicators are often
examined separately.

Decision-makers need a clear way to explore these different sources of
evidence together, compare districts, and identify locations that may
deserve further attention.

AgriPriority addresses this need by integrating agricultural survey
statistics and Earth observation indicators into one district-level
analytical platform.

## Our Approach

We developed AgriPriority around three complementary evidence groups:

1.  **Agricultural statistics:** NISR Season B data for 2025 and 2026,
    including maize and bean yields, cultivated areas, harvested areas,
    and production.
2.  **Rainfall conditions:** CHIRPS rainfall estimates used to assess
    seasonal rainfall anomalies against a historical reference.
3.  **Vegetation conditions:** MODIS NDVI observations used to examine
    changes in vegetation greenness over cropland areas.

These indicators are brought together at district level. The platform
displays the underlying measurements alongside its provisional screening
categories so users can examine the evidence rather than relying on a
category alone.

## What the Platform Provides

### 1. National Overview

The executive overview summarizes the agricultural and environmental
indicators across Rwanda's 30 districts. It provides a national snapshot
of district screening categories and selected changes in crop
performance.

### 2. Interactive GIS Map

The map displays Rwanda's district boundaries and screening categories.
Users can select a district directly from the map or the district
selector. The map zooms to the selected district and opens its
corresponding evidence profile.

### 3. District Evidence Profiles

Each district profile brings together relevant agricultural and
environmental indicators, including:

-   Maize and bean yield changes between Season B 2025 and 2026.
-   Cultivated area, harvested area, and crop production.
-   Seasonal rainfall anomaly.
-   Cropland NDVI anomaly.
-   The provisional screening category and the indicators contributing
    to it.

This allows users to examine the measurements behind a district's
screening result.

### 4. Agricultural Statistics and Evidence Center

The evidence center supports interactive analysis of NISR statistics.
Users can compare years, crops, indicators, and districts through charts
and tables.

It also includes exploratory comparisons between environmental anomalies
and yield changes, including Pearson correlation, to help examine
patterns across districts.

### 5. National Statistical Insights

National insights provide district rankings, descriptive summaries, and
comparisons between maize and bean yield changes. These views help
identify the distribution of observed changes and differences between
crops and districts.

### 6. Screening Sensitivity Analysis

The sensitivity matrix shows how district screening categories change
under nine combinations of rainfall and crop-yield thresholds. This
helps users understand how strongly the results depend on the selected
screening assumptions.

## Data Sources

  -----------------------------------------------------------------------
  Source                  Information used        Role in AgriPriority
  ----------------------- ----------------------- -----------------------
  National Institute of   Maize and bean yield,   Agricultural
  Statistics of Rwanda    cultivated area,        performance and
  (NISR), Seasonal        harvested area, and     year-to-year
  Agricultural Survey     production              comparisons
  (SAS), Season B 2025                            
  and 2026                                        

  CHIRPS Daily            Daily precipitation     Seasonal rainfall
                          estimates               totals and rainfall
                                                  anomalies

  MODIS MOD13Q1 Version   NDVI observations       Seasonal
  6.1                                             vegetation-condition
                                                  anomalies

  ESA WorldCover 2021     Land-cover              Cropland mask for
                          classification; class   vegetation analysis
                          40 identifies cropland  

  FAO GAUL 2015, Level 2, District boundaries     Spatial organization
  and the project                                 and district-level
  district GIS layer                              analysis
  -----------------------------------------------------------------------

## Methodology

### Agricultural Statistics

NISR Season B 2025 and 2026 district statistics are used to compare
maize and bean performance. Where the previous-year value is valid,
percentage change in yield is calculated as:

\[ `\text{Yield change (\%)}`{=tex} =
`\frac{\text{Yield}_{2026}-\text{Yield}_{2025}}`{=tex}
{`\text{Yield}`{=tex}\_{2025}}`\times 100`{=tex} \]

Cultivated area, harvested area, and production are also presented to
provide context for interpreting yield changes.

### Rainfall Anomaly

CHIRPS daily precipitation is summed over the March--June season for
2026 and for each year from 2019 to 2025. The historical reference is
based on the median of the seven annual seasonal rainfall totals.

At pixel level, rainfall anomaly is calculated as:

\[ `\text{Rainfall anomaly (\%)}`{=tex} =
`\frac{\text{Rainfall}_{2026}-\text{Historical median}}`{=tex}
{`\text{Historical median}`{=tex}}`\times 100`{=tex} \]

The district rainfall indicator is the spatial mean of the pixel-level
anomalies within the district. It is therefore not necessarily equal to
the percentage change calculated from district-aggregated rainfall
totals.

### Vegetation Anomaly

MODIS MOD13Q1 Version 6.1 provides NDVI observations at a nominal
spatial resolution of 250 metres. The NDVI scale factor of 0.0001 is
applied, and observations are filtered using the SummaryQA quality band,
retaining values of 0 or 1.

Seasonal median NDVI composites are produced for March--June 2026 and
for each historical year from 2019 to 2025. The historical reference is
the median of the annual seasonal composites.

The NDVI anomaly is calculated as the difference between the 2026
seasonal NDVI composite and the historical reference. ESA WorldCover
2021 class 40 is used to restrict the vegetation analysis to mapped
cropland.

NDVI anomaly is a dimensionless difference in vegetation greenness; it
is not a direct measurement of crop yield or crop damage.

### District-Level Screening

AgriPriority uses a transparent rule-based framework to group districts
according to agricultural and environmental signals.

  -----------------------------------------------------------------------
  Screening condition                 Rule
  ----------------------------------- -----------------------------------
  Environmental concern               Rainfall anomaly ≤ −15% **or** NDVI
                                      anomaly \< 0

  Crop-performance concern            Maize or bean yield change ≤ −5%

  Priority field verification         Both environmental and
                                      crop-performance concerns are
                                      present

  Crop investigation                  Crop-performance concern only

  Environmental monitoring            Environmental concern only

  Routine monitoring                  Neither concern is triggered
  -----------------------------------------------------------------------

The platform also evaluates nine sensitivity scenarios by varying the
rainfall threshold (−10%, −15%, and −20%) and crop-yield threshold (−3%,
−5%, and −10%).

Scenario frequency indicates how often a district receives a particular
classification across the tested threshold combinations. It is **not** a
probability, confidence score, survey uncertainty estimate, or measure
of predictive accuracy.

## Validation and Quality Checks

We carried out source-data comparisons and independent processing checks
to assess the consistency and reproducibility of the indicators used by
AgriPriority.

-   **NISR yield verification:** 120 district-level maize and bean yield
    comparisons across 2025 and 2026 were checked against the supplied
    NISR source workbooks.
-   **NISR area and production verification:** 420 selected comparisons
    covering physical cultivated land, crop cultivated area, harvested
    area, and production were checked. The unit conversion for physical
    cultivated land reported in thousands of hectares was accounted for.
-   **MODIS NDVI reproducibility:** An independent district-level
    processing output reproduced the 30 district NDVI anomaly values in
    the optimized dataset.
-   **CHIRPS rainfall reproducibility:** An independent median-baseline
    calculation closely reproduced the dashboard rainfall anomalies.
    Small residual differences remain between the independent audit and
    the optimized dataset.

These checks assess consistency between source tables, processed
datasets, and independent calculations. They do not establish
field-level accuracy, prove the cause of agricultural changes, or
measure the predictive performance of the screening framework.

## Interpreting the Results Responsibly

AgriPriority is designed to support investigation, not to make
definitive claims about agricultural damage.

The results should be interpreted with the following considerations:

-   NISR district statistics are survey estimates. Survey confidence
    intervals are not incorporated into the current screening framework.
-   The comparison covers two Season B survey years, 2025 and 2026. It
    should not be interpreted as a long-term agricultural trend.
-   CHIRPS and MODIS have different spatial resolutions and measurement
    characteristics. Satellite-derived district indicators are affected
    by spatial aggregation, compositing, masking, and mixed pixels.
-   ESA WorldCover 2021 is used as a historical cropland mask; it is not
    a field inventory of cropland in 2026.
-   Relationships between environmental anomalies and yield changes are
    exploratory. Correlation does not establish causation.
-   A district with a negative rainfall anomaly or NDVI anomaly is not
    necessarily experiencing confirmed crop losses. Likewise, positive
    average NDVI can coexist with declining crop yields.
-   The screening thresholds are exploratory and should be interpreted
    alongside local knowledge and field verification.

A district identified for priority field verification is a location
recommended for further investigation, not a confirmed finding of crop
damage.

## Technology

AgriPriority is developed using:

-   **Python** for data processing and application logic.
-   **Streamlit** for the interactive dashboard.
-   **GeoPandas / GIS data formats** for district-level spatial
    information.
-   **Google Earth Engine** for satellite and rainfall data processing.
-   **Interactive charts and maps** for statistical and geospatial
    exploration.

## Running the Application

To run AgriPriority locally, use a supported Python 3 environment. From
the project root:

``` bash
python -m pip install -r requirements.txt
streamlit run app.py
```

An internet connection is required for the OpenStreetMap basemap.

## Team

**TerraSignal**\
NISR Big Data Hackathon 2026\
Agricultural Productivity Track

## Acknowledgement

AgriPriority Rwanda was developed for the NISR Big Data Hackathon 2026
using NISR Seasonal Agricultural Survey statistics and publicly
available Earth observation datasets.

**AgriPriority Rwanda --- Turning Agricultural Data into Actionable
Evidence.**

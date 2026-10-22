"""AgriPriority evidence center: descriptive charts, not risk predictions."""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

SOURCE = "AgriPriority_NISR_SeasonB_2025_2026_Comparison_v1.csv"

# Keep the year colours visually distinct and consistent across year comparisons.
YEAR_COLORS = {"2025": "#94A3B8", "2026": "#2563EB"}
CATEGORY_COLORS = {
    "Priority field verification": "#D15B57",
    "Investigate crop performance": "#DCA143",
    "Environmental monitoring": "#528FC4",
    "Routine monitoring": "#59A77E",
}
CATEGORIES = list(CATEGORY_COLORS)
CROPS = {
    "Maize": "maize",
    "Beans": "bean",
    "Irish potato": "irish_potato",
    "Cassava": "cassava",
    "Rice": "rice",
    "Sorghum": "sorghum",
    "Sweet potato": "sweet_potato",
}
MEASURES = {
    "Yield (kg/ha)": ("yield_kg_ha", "kg/ha"),
    "Production (metric tonnes)": ("production_mt", "metric tonnes"),
    "Cultivated area (ha)": ("cultivated_area_ha", "ha"),
    "Harvested area (ha)": ("harvested_area_ha", "ha"),
}
SCENARIOS = [f"Rain_{r}_Yield_{y}" for r in (-10, -15, -20) for y in (-3, -5, -10)]


@st.cache_data
def get_nisr():
    nisr = pd.read_csv(SOURCE)
    nisr["district"] = nisr["district"].astype(str).str.strip()
    if len(nisr) != 30 or nisr["district"].nunique() != 30:
        raise ValueError("NISR comparison must have 30 unique districts")
    return nisr


def clean_plot(fig, title, ytitle=None, *, height=440):
    """Apply a consistent, restrained style without changing the underlying data."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#263445"), x=0, xanchor="left"),
        font=dict(family="Arial, sans-serif", size=12, color="#475569"),
        margin=dict(l=18, r=34, t=76, b=48),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
        hoverlabel=dict(bgcolor="#172033", font=dict(color="#FFFFFF", size=12)),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, x=0,
            title_text="", font=dict(size=11),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#D8E0E8",
        tickfont=dict(color="#64748B"),
        title_font=dict(color="#475569"),
    )
    fig.update_yaxes(
        gridcolor="rgba(148,163,184,0.22)",
        linecolor="#D8E0E8",
        tickfont=dict(color="#64748B"),
        title_font=dict(color="#475569"),
    )
    if ytitle:
        fig.update_yaxes(title_text=ytitle)
    return fig


def show_statistics(model):
    st.divider()
    st.header("📊 Agricultural Statistics & Evidence Center")
    st.caption(
        "Interactive analysis of NISR Seasonal Agricultural Survey (Season B 2025 and 2026), "
        "compared with MODIS and CHIRPS indicators. Two seasons are a two-point comparison, "
        "not an established long-term trend."
    )
    try:
        nisr = get_nisr()
    except Exception as ex:
        st.error(f"Cannot load the NISR statistical data: {ex}")
        return

    model = model.copy()
    model["district"] = model["district"].astype(str).str.strip()
    if set(model.district) != set(nisr.district):
        st.error("District names differ between NISR and satellite model. Do not graph unverified joins.")
        return
    stat = model.merge(nisr, on="district", how="inner", validate="one_to_one", suffixes=("", "_nisr"))

    t1, t2, t3, t4 = st.tabs([
        "NISR year comparison", "Compare districts", "Environmental relationships", "Sensitivity evidence"
    ])

    with t1:
        st.subheader("NISR Season B: 2025 versus 2026")
        c1, c2, c3 = st.columns(3)
        with c1:
            crop_label = st.selectbox("Crop", list(CROPS), key="nisr_crop")
        with c2:
            measure_label = st.selectbox("Statistic", list(MEASURES), key="nisr_measure")
        district_list = sorted(stat.district)
        preferred = st.session_state.get("chosen_district")
        default_index = district_list.index(preferred) if preferred in set(district_list) else 0
        with c3:
            selected_name = st.selectbox(
                "District", district_list, index=default_index, key="nisr_year_district"
            )

        crop = CROPS[crop_label]
        suffix, units = MEASURES[measure_label]
        c25 = f"nisr_{crop}_{suffix}_2025"
        c26 = f"nisr_{crop}_{suffix}_2026"
        if not {c25, c26}.issubset(stat.columns):
            st.info("The uploaded NISR comparison does not contain both years for this crop/statistic. Select another option.")
        else:
            point = stat.loc[stat.district == selected_name].iloc[0]
            values = [point[c25], point[c26]]
            if pd.isna(values).any():
                st.info("NISR reports a missing value for this district and measure. No zero was imputed.")
            else:
                values = [float(value) for value in values]
                fig = go.Figure(
                    go.Bar(
                        x=["2025", "2026"],
                        y=values,
                        marker=dict(
                            color=[YEAR_COLORS["2025"], YEAR_COLORS["2026"]],
                            line=dict(color="#FFFFFF", width=1.5),
                        ),
                        text=[f"{value:,.1f}" for value in values],
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="<b>Season B %{x}</b><br>%{y:,.2f} " + units + "<extra></extra>",
                    )
                )
                clean_plot(fig, f"{crop_label} · {measure_label} · {selected_name}", units, height=410)
                fig.update_layout(showlegend=False, bargap=0.52)
                fig.update_yaxes(rangemode="tozero")
                st.plotly_chart(fig, use_container_width=True, key="year_compare_chart")
                diff = values[1] - values[0]
                if values[0] != 0:
                    pct_change = (diff / values[0]) * 100
                    change_text = f" ({pct_change:+.1f}% relative to 2025)"
                else:
                    change_text = " (percentage change not calculated because the 2025 baseline is zero)"
                st.write(
                    f"**Interpretation:** {selected_name} reported {values[0]:,.1f} {units} in Season B 2025 "
                    f"and {values[1]:,.1f} {units} in Season B 2026 (difference: {diff:+,.1f} {units})"
                    f"{change_text}. This is a descriptive year-on-year comparison, not evidence of cause."
                )
        st.caption("Source: NISR Season B survey tables for the two years. Missing reported statistics are not interpreted as zero.")

    with t2:
        st.subheader("Compare statistics across districts")
        d1, d2, d3 = st.columns([2, 1, 1])
        with d1:
            chosen = st.multiselect(
                "Districts to compare", sorted(stat.district),
                default=[x for x in ["Kirehe", "Kayonza", "Ruhango", "Rulindo"] if x in set(stat.district)],
                key="stat_compare_districts",
            )
        with d2:
            indicator = st.selectbox(
                "Indicator",
                ["Physical cultivated land (ha)", "Maize yield (kg/ha)", "Bean yield (kg/ha)",
                 "Maize production (metric tonnes)", "Bean production (metric tonnes)"],
                key="compare_indicator",
            )
        with d3:
            year = st.selectbox("Year", [2025, 2026], index=1, key="compare_year")

        fields = {
            "Physical cultivated land (ha)": "nisr_physical_cultivated_land_ha",
            "Maize yield (kg/ha)": "nisr_maize_yield_kg_ha",
            "Bean yield (kg/ha)": "nisr_bean_yield_kg_ha",
            "Maize production (metric tonnes)": "nisr_maize_production_mt",
            "Bean production (metric tonnes)": "nisr_bean_production_mt",
        }
        col = fields[indicator] + "_" + str(year)
        comp = stat.loc[stat.district.isin(chosen), ["district", col, "priority_category"]].dropna(subset=[col])
        comp = comp.sort_values(col, ascending=True)
        if comp.empty:
            st.info("Choose at least one district with available data.")
        else:
            fig = px.bar(
                comp,
                x=col,
                y="district",
                orientation="h",
                text=col,
                color="priority_category",
                color_discrete_map=CATEGORY_COLORS,
                category_orders={"priority_category": CATEGORIES},
                labels={col: indicator, "district": "District", "priority_category": "Screening category"},
                custom_data=["priority_category"],
            )
            fig.update_traces(
                texttemplate="%{text:,.1f}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate="<b>%{y}</b><br>" + indicator + ": %{x:,.1f}<br>Category: %{customdata[0]}<extra></extra>",
                marker_line_color="#FFFFFF",
                marker_line_width=1,
            )
            fig.update_yaxes(categoryorder="total ascending")
            clean_plot(fig, f"{indicator} · {year}", height=max(400, 76 * len(comp) + 110))
            st.plotly_chart(fig, use_container_width=True, key="district_compare_chart")
            st.caption(
                "Bar colours match the district screening categories used on the map and scatterplot. "
                "These are district-level totals or averages as labelled; more cultivated land is not evidence of greater crop loss."
            )

    with t3:
        st.subheader("How do environmental anomalies relate to crop-yield changes?")
        c1, c2 = st.columns(2)
        with c1:
            environment = st.selectbox("Horizontal axis", ["Rainfall anomaly (%)", "NDVI anomaly"], key="env_axis")
        with c2:
            target = st.selectbox("Crop yield change", ["Maize", "Beans"], key="yield_axis")
        xcol = "mean_rainfall_anomaly_percent" if environment.startswith("Rainfall") else "mean_cropland_ndvi_anomaly"
        ycol = f'change_{"maize" if target == "Maize" else "bean"}_yield_kg_ha_2025_to_2026_pct'
        d = stat[["district", xcol, ycol, "priority_category"]].dropna()
        fig = px.scatter(
            d,
            x=xcol,
            y=ycol,
            hover_name="district",
            color="priority_category",
            color_discrete_map=CATEGORY_COLORS,
            category_orders={"priority_category": CATEGORIES},
            labels={xcol: environment, ycol: f"{target} yield change (%)", "priority_category": "Screening category"},
            hover_data={xcol: ":.3f", ycol: ":+.1f"},
        )
        fig.update_traces(marker=dict(size=13, opacity=0.88, line=dict(color="#FFFFFF", width=1.4)))
        fig.add_hline(y=0, line_dash="dot", line_color="#64748B", line_width=1.4)
        clean_plot(fig, f"{environment} vs. {target.lower()} yield change", height=500)
        st.plotly_chart(fig, use_container_width=True, key="env_scatter_chart")
        if len(d) >= 3 and d[xcol].nunique() > 1 and d[ycol].nunique() > 1:
            r = d[xcol].corr(d[ycol])
            st.write(
                f"**Pearson correlation (r): {r:+.2f}; n = {len(d)} districts.** "
                "This is a descriptive cross-district association, not evidence that rainfall or NDVI caused the yield changes. "
                "District-level averages can conceal local variation."
            )
        else:
            st.caption("Insufficient variation or observations to calculate a meaningful correlation.")

    with t4:
        st.subheader("Stability of field-verification recommendations")
        options = st.multiselect(
            "Districts for sensitivity heatmap", sorted(stat.district),
            default=[x for x in ["Kirehe", "Kayonza", "Ruhango", "Rulindo", "Gasabo"] if x in set(stat.district)],
            key="scenario_districts",
        )
        valid = [column for column in SCENARIOS if column in stat.columns]
        if options and len(valid) == 9:
            heat = stat.set_index("district").loc[options, valid].eq("Priority field verification").astype(int)
            scenario_labels = [column.replace("Rain_", "R ").replace("_Yield_", " | Y ") for column in heat.columns]
            cell_text = [["FLAG" if value else "—" for value in row] for row in heat.values]
            fig = go.Figure(
                go.Heatmap(
                    z=heat.values,
                    x=scenario_labels,
                    y=heat.index.tolist(),
                    text=cell_text,
                    texttemplate="%{text}",
                    textfont=dict(size=10, color="#263445"),
                    zmin=0,
                    zmax=1,
                    colorscale=[[0, "#E8EEF4"], [0.499, "#E8EEF4"], [0.5, "#D15B57"], [1, "#D15B57"]],
                    showscale=False,
                    xgap=3,
                    ygap=3,
                    hovertemplate="District: %{y}<br>Scenario: %{x}<br>Field verification flagged: %{z}<extra></extra>",
                )
            )
            clean_plot(fig, "Field-verification rule matches by district and scenario", height=max(420, 48 * len(options) + 180))
            fig.update_xaxes(tickangle=-28, title_text="R = rainfall threshold (%) · Y = yield threshold (%)")
            fig.update_yaxes(title_text="District", autorange="reversed")
            st.plotly_chart(fig, use_container_width=True, key="scenario_heatmap_chart")
            st.caption(
                "Each column varies the rainfall-deficit and yield-decline screening thresholds. "
                "Red cells are rule matches, not observed losses or probabilities. A dash means the scenario did not flag field verification."
            )
        else:
            st.info("Select districts to view the nine-scenario classification sensitivity.")

    st.download_button(
        "Download NISR comparison dataset (CSV)",
        nisr.to_csv(index=False).encode("utf-8"),
        file_name="AgriPriority_NISR_SeasonB_2025_2026_Comparison.csv",
        mime="text/csv",
        key="download_stat_evidence",
    )
    with st.expander("Statistical interpretation and source notes"):
        st.markdown(
            """**Unit of analysis:** 30 districts, compared over two NISR Season B surveys (2025 and 2026). **Satellite period:** March–June 2026 relative to March–June 2019–2025. **NDVI:** MODIS 250 m with ESA WorldCover 2021 cropland mask. **Rainfall:** CHIRPS gridded rainfall.

NISR area, production, and yield estimates are different quantities and should not be conflated. Survey uncertainty, district-level averaging, the historic cropland mask, mixed MODIS pixels, and selected screening thresholds limit the conclusions. Correlations are exploratory and do not establish a causal relationship. Two years do not establish a long-term agricultural trend.

The workbook's Table 29 has a source-year inconsistency and its indicators are not included in these visualizations. District boundary provenance requires final verification."""
        )

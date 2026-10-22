"""AgriPriority evidence center: descriptive charts, not risk predictions."""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

SOURCE = "AgriPriority_NISR_SeasonB_2025_2026_Comparison_v1.csv"
COLORS = {"2025": "#96ADBF", "2026": "#3477A6"}
CROPS = {"Maize": "maize", "Beans": "bean", "Irish potato": "irish_potato", "Cassava": "cassava", "Rice": "rice", "Sorghum": "sorghum", "Sweet potato": "sweet_potato"}
MEASURES = {"Yield (kg/ha)": ("yield_kg_ha", "kg/ha"), "Production (metric tonnes)": ("production_mt", "metric tonnes"), "Cultivated area (ha)": ("cultivated_area_ha", "ha"), "Harvested area (ha)": ("harvested_area_ha", "ha")}
SCENARIOS = [f"Rain_{r}_Yield_{y}" for r in (-10,-15,-20) for y in (-3,-5,-10)]

@st.cache_data
def get_nisr():
    nisr = pd.read_csv(SOURCE)
    nisr['district'] = nisr['district'].str.strip()
    if len(nisr) != 30 or nisr['district'].nunique() != 30:
        raise ValueError("NISR comparison must have 30 unique districts")
    return nisr

def clean_plot(fig, title, ytitle=None):
    fig.update_layout(title=dict(text=title, font=dict(size=17)),
        font=dict(size=12), margin=dict(l=12,r=12,t=62,b=24),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest', legend=dict(orientation='h', y=1.1))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='rgba(140,150,160,0.16)', title_text=ytitle)
    return fig

def show_statistics(model):
    st.divider()
    st.header("📊 Agricultural Statistics & Evidence Center")
    st.caption("Interactive analysis of NISR Seasonal Agricultural Survey (Season B 2025 and 2026), compared with MODIS and CHIRPS indicators. Two seasons are a two-point comparison, not an established long-term trend.")
    try:
        nisr = get_nisr()
    except Exception as ex:
        st.error(f"Cannot load the NISR statistical data: {ex}")
        return
    model = model.copy()
    model['district'] = model['district'].str.strip()
    if set(model.district) != set(nisr.district):
        st.error("District names differ between NISR and satellite model. Do not graph unverified joins.")
        return
    stat = model.merge(nisr, on='district', how='inner', validate='one_to_one', suffixes=('', '_nisr'))

    t1, t2, t3, t4 = st.tabs(["NISR year comparison", "Compare districts", "Environmental relationships", "Sensitivity evidence"])
    with t1:
        st.subheader("NISR Season B: 2025 versus 2026")
        c1,c2,c3 = st.columns(3)
        with c1: crop_label = st.selectbox('Crop', list(CROPS), key='nisr_crop')
        with c2: measure_label = st.selectbox('Statistic', list(MEASURES), key='nisr_measure')
        with c3: selected_name = st.selectbox('District', sorted(stat.district), index=sorted(stat.district).index(st.session_state.get('chosen_district')) if st.session_state.get('chosen_district') in set(stat.district) else 0, key='nisr_year_district')
        crop = CROPS[crop_label]; suffix, units = MEASURES[measure_label]
        c25=f'nisr_{crop}_{suffix}_2025'; c26=f'nisr_{crop}_{suffix}_2026'
        if not {c25,c26}.issubset(stat.columns):
            st.info('The uploaded NISR comparison does not contain both years for this crop/statistic. Select another option.')
        else:
            point=stat.loc[stat.district == selected_name].iloc[0]
            values=[point[c25],point[c26]]
            if pd.isna(values).any():
                st.info('NISR reports a missing value for this district and measure. No zero was imputed.')
            else:
                fig=go.Figure(go.Bar(x=['2025','2026'], y=values, marker_color=[COLORS['2025'],COLORS['2026']], text=[f'{x:,.1f}' for x in values], textposition='outside', cliponaxis=False, hovertemplate='%{x}: %{y:,.2f} '+units+'<extra></extra>'))
                clean_plot(fig, f'{crop_label} — {measure_label} in {selected_name}', units)
                # Explicit categorical axis prevents Plotly from treating year strings as numbers
                # and adding misleading half-year ticks such as 2024.5 or 2025.5.
                fig.update_xaxes(
                    type='category', categoryorder='array', categoryarray=['2025','2026'],
                    tickmode='array', tickvals=['2025','2026'], ticktext=['2025','2026'],
                    title_text='NISR Season B year', automargin=True,
                )
                st.plotly_chart(fig, use_container_width=True, key='year_compare_chart')
                diff=values[1]-values[0]
                st.write(f'**Interpretation:** {selected_name} reported {values[0]:,.1f} {units} in Season B 2025 and {values[1]:,.1f} {units} in Season B 2026 (difference: {diff:+,.1f} {units}). This is a descriptive year-on-year comparison, not evidence of cause.')
        st.caption('Source: NISR Season B survey tables for the two years. Missing reported statistics are not interpreted as zero.')

    with t2:
        st.subheader('Compare statistics across districts')
        d1,d2,d3=st.columns([2,1,1])
        with d1: chosen=st.multiselect('Districts to compare', sorted(stat.district), default=[x for x in ['Kirehe','Kayonza','Ruhango','Rulindo'] if x in set(stat.district)], key='stat_compare_districts')
        with d2: indicator=st.selectbox('Indicator', ['Physical cultivated land (ha)', 'Maize yield (kg/ha)', 'Bean yield (kg/ha)', 'Maize production (metric tonnes)', 'Bean production (metric tonnes)'], key='compare_indicator')
        with d3: year=st.selectbox('Year', [2025,2026], index=1, key='compare_year')
        fields={'Physical cultivated land (ha)':'nisr_physical_cultivated_land_ha', 'Maize yield (kg/ha)':'nisr_maize_yield_kg_ha','Bean yield (kg/ha)':'nisr_bean_yield_kg_ha','Maize production (metric tonnes)':'nisr_maize_production_mt','Bean production (metric tonnes)':'nisr_bean_production_mt'}
        col=fields[indicator]+'_'+str(year)
        comp=stat.loc[stat.district.isin(chosen), ['district',col]].dropna().sort_values(col)
        if comp.empty: st.info('Choose at least one district with available data.')
        else:
            fig=px.bar(comp, x=col,y='district', orientation='h', text=col, labels={col:indicator,'district':'District'}, color_discrete_sequence=['#528FC4'])
            fig.update_traces(texttemplate='%{text:,.1f}', textposition='outside', cliponaxis=False)
            st.plotly_chart(clean_plot(fig, f'{indicator} · {year}'), use_container_width=True, key='district_compare_chart')
            st.caption('Comparisons reflect total district-level statistics. More cultivated land is not evidence of greater crop loss.')

    with t3:
        st.subheader('How do environmental anomalies relate to crop-yield changes?')
        c1,c2=st.columns(2)
        with c1: environment=st.selectbox('Horizontal axis', ['Rainfall anomaly (%)', 'NDVI anomaly'], key='env_axis')
        with c2: target=st.selectbox('Crop yield change', ['Maize','Beans'], key='yield_axis')
        xcol='mean_rainfall_anomaly_percent' if environment.startswith('Rainfall') else 'mean_cropland_ndvi_anomaly'
        ycol=f'change_{"maize" if target == "Maize" else "bean"}_yield_kg_ha_2025_to_2026_pct'
        d=stat[['district',xcol,ycol,'priority_category']].dropna()
        fig=px.scatter(d,x=xcol,y=ycol,hover_name='district',color='priority_category',color_discrete_map={
        'Priority field verification':'#D15B57','Investigate crop performance':'#DCA143',
        'Environmental monitoring':'#528FC4','Routine monitoring':'#59A77E'},
        labels={xcol:environment,ycol:f'{target} yield change (%)', 'priority_category':'Screening category'})
        fig.update_traces(marker=dict(size=12,opacity=.8,line=dict(color='white',width=1)))
        fig.add_hline(y=0,line_dash='dot',line_color='#9BA4AE')
        st.plotly_chart(clean_plot(fig,f'{environment} vs {target.lower()} yield change'),use_container_width=True,key='env_scatter_chart')
        if len(d)>=3 and d[xcol].nunique()>1 and d[ycol].nunique()>1:
            r=d[xcol].corr(d[ycol])
            st.write(f'**Pearson correlation (r): {r:+.2f}; n = {len(d)} districts.** This is a descriptive cross-district association, not evidence that rainfall or NDVI caused the yield changes. District-level averages can conceal local variation.')
        else:st.caption('Insufficient variation or observations to calculate a meaningful correlation.')

    with t4:
        st.subheader('Stability of field-verification recommendations')
        options=st.multiselect('Districts for sensitivity heatmap', sorted(stat.district), default=[x for x in ['Kirehe','Kayonza','Ruhango','Rulindo','Gasabo'] if x in set(stat.district)], key='scenario_districts')
        valid=[c for c in SCENARIOS if c in stat.columns]
        if options and len(valid)==9:
            heat=stat.set_index('district').loc[options,valid].eq('Priority field verification').astype(int)
            # Compact, explicit labels plus a rotated x-axis keep all nine
            # threshold combinations readable on laptop and desktop screens.
            scenario_labels = [
                f"R{int(column.split('_')[1])} / Y{int(column.split('_')[3])}"
                for column in heat.columns
            ]
            fig=go.Figure(go.Heatmap(
                z=heat.values, x=scenario_labels, y=heat.index.tolist(),
                zmin=0, zmax=1,
                colorscale=[[0,'#e6edf3'],[0.499,'#e6edf3'],[0.5,'#D15B57'],[1,'#D15B57']],
                showscale=False,
                hovertemplate='District: %{y}<br>Scenario: %{x}<br>Field verification: %{z}<extra></extra>'
            ))
            fig = clean_plot(fig, 'Red cell = field verification under that scenario')
            fig.update_layout(
                height=max(360, 34 * len(options) + 150),
                margin=dict(l=95, r=20, t=65, b=135),
            )
            fig.update_xaxes(type='category', tickangle=-40, tickfont=dict(size=10), automargin=True, title_text='Rainfall / yield thresholds')
            fig.update_yaxes(tickfont=dict(size=11), automargin=True)
            st.plotly_chart(fig,use_container_width=True,key='scenario_heatmap_chart')
            st.caption('Each column varies the rainfall-deficit and yield-decline screening thresholds. Red cells are rule matches, not observed losses or probabilities.')
        else: st.info('Select districts to view the nine-scenario classification sensitivity.')
    st.download_button('Download NISR comparison dataset (CSV)',nisr.to_csv(index=False).encode('utf-8'),file_name='AgriPriority_NISR_SeasonB_2025_2026_Comparison.csv',mime='text/csv',key='download_stat_evidence')
    with st.expander('Statistical interpretation and source notes'):
        st.markdown("""**Unit of analysis:** 30 districts, compared over two NISR Season B surveys (2025 and 2026). **Satellite period:** March–June 2026 relative to March–June 2019–2025. **NDVI:** MODIS 250 m with ESA WorldCover 2021 cropland mask. **Rainfall:** CHIRPS gridded rainfall.\n\nNISR area, production, and yield estimates are different quantities and should not be conflated. Survey uncertainty, district-level averaging, the historic cropland mask, mixed MODIS pixels, and selected screening thresholds limit the conclusions. Correlations are exploratory and do not establish a causal relationship. Two years do not establish a long-term agricultural trend.\n\nThe workbook's Table 29 has a source-year inconsistency and its indicators are not included in these visualizations. District boundary provenance requires final verification.""")

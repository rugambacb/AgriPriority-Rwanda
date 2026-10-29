"""National exploratory statistical summaries; no risk or crop-loss predictions."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

CATEGORY_COLORS = {
    "Priority field verification": "#D15B57",
    "Investigate crop performance": "#DCA143",
    "Environmental monitoring": "#528FC4",
    "Routine monitoring": "#59A77E",
}
INDICATORS = {
    "Rainfall anomaly (%)": ("mean_rainfall_anomaly_percent", "%", 1),
    "NDVI anomaly": ("mean_cropland_ndvi_anomaly", "NDVI units", 3),
    "Maize yield change (%)": ("change_maize_yield_kg_ha_2025_to_2026_pct", "%", 1),
    "Bean yield change (%)": ("change_bean_yield_kg_ha_2025_to_2026_pct", "%", 1),
    "Physically cultivated land 2026 (ha)": ("nisr_physical_cultivated_land_ha_2026", "ha", 0),
    "Category stability (%)": ("recommendation_stability_pct", "%", 1),
}

def _make_bar(data, field, label, digits, largest=False):
    """Chart calculated from district observations, not derived losses."""
    descending = largest
    d = data.sort_values(field, ascending=not descending)
    colors = [CATEGORY_COLORS.get(c, "#64748B") for c in d["priority_category"]]
    values = d[field].astype(float)
    labels = [f"{v:+,.{digits}f}" if v < 0 else f"{v:,.{digits}f}" for v in values]
    fig = go.Figure(go.Bar(
        x=values, y=d["district"], orientation="h", marker_color=colors,
        text=labels, textposition="outside", cliponaxis=False,
        customdata=d[["priority_category"]].to_numpy(),
        hovertemplate="%{y}<br>Value: %{x:,.3f}<br>Screening category: %{customdata[0]}<extra></extra>"
    ))
    fig.update_layout(
        height=max(320, 55*len(d)+100), margin=dict(l=15,r=100,t=20,b=55),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title=label,yaxis_title=None,font=dict(size=12),showlegend=False,
    )
    fig.update_xaxes(zeroline=True, zerolinecolor="#75859A", gridcolor="rgba(140,150,160,.15)")
    fig.update_yaxes(showgrid=False, categoryorder="array", categoryarray=d["district"].tolist())
    return fig

def show_national_insights(source):
    st.divider()
    st.header("📈 National Statistical Insights")
    st.caption(
        "Exploratory district-level statistics from the 30-district AgriPriority V3 dataset. "
        "Results describe observed survey comparisons and satellite anomalies; they are not "
        "crop-loss estimates, causal effects, or verified risk scores."
    )
    required = ["district", "priority_category", *[v[0] for v in INDICATORS.values()]]
    missing = [col for col in required if col not in source.columns]
    if missing:
        st.error("National insights unavailable; missing columns: " + ", ".join(missing))
        return
    df = source[required].copy()
    if df["district"].nunique() != 30 or len(df) != 30:
        st.error("National insights require exactly 30 unique districts.")
        return
    t1,t2,t3 = st.tabs(["District rankings", "Descriptive statistics", "Crop performance contrasts"])
    with t1:
        st.subheader("District rankings")
        a,b,c=st.columns([2,1,1])
        with a:
            label=st.selectbox("Statistical indicator", list(INDICATORS), key="insights_indicator")
        with b:
            direction=st.selectbox("Rank by", ["Lowest values", "Highest values"], key="insights_direction")
        with c:
            how_many=st.selectbox("Districts shown", [5,10,15,30],index=1,key="insights_n")
        field,unit,precision=INDICATORS[label]
        eligible=df.dropna(subset=[field]).copy()
        if eligible.empty:
            st.info("No district measurements are available for this indicator.")
        else:
            largest=direction=="Highest values"
            ranked=eligible.sort_values(field,ascending=not largest).head(how_many)
            st.plotly_chart(_make_bar(ranked,field,label,precision,largest),use_container_width=True,key="insights_rank_chart")
            lead=ranked.iloc[0]
            st.markdown(f"**Finding:** {lead['district']} has the {'highest' if largest else 'lowest'} value among the districts shown: **{lead[field]:,.{precision}f} {unit}**.")
            st.caption("The category colours identify existing screening recommendations. Ranking by an indicator is not a new risk classification or evidence of crop damage.")
            st.dataframe(ranked[["district",field,"priority_category"]].rename(columns={"district":"District",field:label,"priority_category":"Existing screening category"}),use_container_width=True,hide_index=True)
    with t2:
        st.subheader("Distribution across the 30 districts")
        indicator=st.selectbox("Summary indicator",list(INDICATORS),key="insights_summary_indicator")
        field,unit,precision=INDICATORS[indicator]
        data=pd.to_numeric(df[field],errors="coerce").dropna()
        if data.empty:
            st.info("No observations for this indicator.")
        else:
            stats=pd.DataFrame({"Statistic":["Districts with data","Mean","Median","Minimum","Maximum","Sample standard deviation"],
                                "Value":[len(data), data.mean(), data.median(),data.min(),data.max(),data.std(ddof=1)]})
            stats["Value"]=[str(len(data)) if i==0 else (f"{v:,.{precision}f}" if pd.notna(v) else "n/a") for i,v in enumerate(stats["Value"])]
            st.dataframe(stats, use_container_width=True,hide_index=True)
            fig=go.Figure(go.Histogram(x=data,nbinsx=min(12,max(5,len(data)//2)),marker_color="#528FC4",hovertemplate="Value: %{x}<br>Districts: %{y}<extra></extra>"))
            fig.add_vline(x=float(data.median()),line_dash="dash",line_color="#D15B57",annotation_text="Median",annotation_position="top")
            fig.update_layout(height=360,xaxis_title=f"{indicator}",yaxis_title="Number of districts",bargap=.08,margin=dict(l=30,r=30,t=35,b=45),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            fig.update_yaxes(gridcolor="rgba(140,150,160,.18)")
            st.plotly_chart(fig,use_container_width=True,key="insights_hist")
            st.caption(f"Unweighted descriptive statistics across {len(data)} districts with available measurements. Each district contributes equally, regardless of farm area. Standard deviation uses n−1; no survey confidence interval or statistical significance is implied.")
    with t3:
        st.subheader("Where maize and bean yields changed in different directions")
        maize="change_maize_yield_kg_ha_2025_to_2026_pct"
        beans="change_bean_yield_kg_ha_2025_to_2026_pct"
        crop=df[["district","priority_category",maize,beans]].dropna().copy()
        crop["Pattern"]=crop.apply(lambda r: (
            "Maize decreased, beans increased" if r[maize]<0 and r[beans]>0 else
            "Maize increased, beans decreased" if r[maize]>0 and r[beans]<0 else
            "Both decreased" if r[maize]<0 and r[beans]<0 else
            "Both increased" if r[maize]>0 and r[beans]>0 else "One or both unchanged"
        ),axis=1)
        counts=crop["Pattern"].value_counts()
        st.markdown(f"**{int(counts.get('Maize decreased, beans increased',0)+counts.get('Maize increased, beans decreased',0))} of {len(crop)} districts** show opposing directions in maize and bean yield change.")
        pattern=st.multiselect("Choose patterns", ["Maize decreased, beans increased","Maize increased, beans decreased","Both decreased","Both increased","One or both unchanged"],default=["Maize decreased, beans increased","Maize increased, beans decreased"],key="insights_patterns")
        selected=crop.loc[crop["Pattern"].isin(pattern)].sort_values("district")
        if selected.empty:
            st.info("No districts match these patterns. Try another selection.")
        else:
            fig=go.Figure()
            for field,name,color in [(maize,"Maize","#528FC4"),(beans,"Beans","#DCA143")]:
                fig.add_bar(name=name,x=selected["district"],y=selected[field],marker_color=color,hovertemplate="%{x}<br>Yield change: %{y:+.2f}%<extra>"+name+"</extra>")
            fig.add_hline(y=0,line_color="#64748B",line_width=1)
            fig.update_layout(barmode="group",height=max(400,len(selected)*14+260),margin=dict(l=25,r=20,t=40,b=90),yaxis_title="Yield change, 2025–2026 (%)",xaxis_title="District",legend=dict(orientation="h",y=1.12),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            fig.update_xaxes(tickangle=-45)
            fig.update_yaxes(gridcolor="rgba(140,150,160,.18)")
            st.plotly_chart(fig,use_container_width=True,key="insights_crop_contrast")
            table=selected[["district",maize,beans,"Pattern","priority_category"]].rename(columns={"district":"District",maize:"Maize yield change (%)",beans:"Bean yield change (%)","priority_category":"Existing screening category"})
            st.dataframe(table,use_container_width=True,hide_index=True,column_config={"Maize yield change (%)":st.column_config.NumberColumn(format="%.1f"),"Bean yield change (%)":st.column_config.NumberColumn(format="%.1f")})
            st.download_button("Download selected crop comparisons (CSV)",table.to_csv(index=False).encode("utf-8"),"AgriPriority_crop_contrasts.csv","text/csv",key="insights_contrast_download")
        st.caption("Two surveys show year-on-year changes, not a long-term trend. District crop yields can respond to multiple influences; opposite movements are not proof of a particular cause.")

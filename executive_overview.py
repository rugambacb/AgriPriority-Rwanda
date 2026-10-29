"""Executive overview. District-level descriptive evidence; not risk probabilities."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PALETTE = {
    "Priority field verification": "#D15B57",
    "Investigate crop performance": "#DCA143",
    "Environmental monitoring": "#528FC4",
    "Routine monitoring": "#59A77E",
}


def show_executive_overview(frame):
    df = frame.copy()
    assert len(df) == 30 and df["district"].nunique() == 30
    rain = "mean_rainfall_anomaly_percent"
    maize = "change_maize_yield_kg_ha_2025_to_2026_pct"
    bean = "change_bean_yield_kg_ha_2025_to_2026_pct"
    opposing = int((((df[maize] > 0) & (df[bean] < 0)) | ((df[maize] < 0) & (df[bean] > 0))).sum())
    flagged = int((df["priority_category"] == "Priority field verification").sum())

    st.subheader("📊 Executive statistical overview")
    st.caption("At-a-glance evidence from all 30 districts. Figures are descriptive district-level indicators, not nationally area-weighted estimates, verified crop losses, or predictive risk scores.")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Districts analyzed", f"{len(df)}")
    k2.metric("Field-review category", f"{flagged} / 30", help="Districts provisionally classified for priority field verification under the V2 rules.")
    k3.metric("Mean rainfall anomaly", f"{df[rain].mean():+.1f}%", help="Arithmetic mean of 30 district-level CHIRPS anomalies; NOT an area-weighted national rainfall estimate.")
    k4.metric("Opposite crop changes", f"{opposing} / 30", help="Districts where maize and bean yield changes have opposite signs, based on two NISR Season B surveys.")

    left, right = st.columns([1, 1.2], gap="large")
    with left:
        st.markdown("**Screening recommendations · 30 districts**")
        cats = list(PALETTE)
        counts = df["priority_category"].value_counts().reindex(cats, fill_value=0)
        fig = go.Figure(go.Bar(
            x=counts.to_numpy(), y=cats, orientation="h",
            marker_color=[PALETTE[k] for k in cats],
            text=[f"{n} ({n/30:.1%})" for n in counts],
            textposition="outside",
            hovertemplate="%{y}: %{x} districts<extra></extra>",
        ))
        fig.update_layout(height=280, margin=dict(l=10, r=76, t=10, b=28),
            showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Number of districts", range=[0, 19], dtick=5),
            yaxis=dict(autorange="reversed", title=None),
        )
        st.plotly_chart(fig, use_container_width=True, key="executive_categories_chart")
    with right:
        st.markdown("**Evidence leaders: five largest observed changes**")
        choice = st.selectbox("Explore indicator", ["Rainfall deficits", "Maize yield declines", "Bean yield declines"], key="executive_indicator")
        field, unit = {"Rainfall deficits": (rain,"%"), "Maize yield declines": (maize,"%"), "Bean yield declines": (bean,"%")}[choice]
        top = df.sort_values(field).head(5).copy()
        top = top.sort_values(field, ascending=False)
        fig2 = go.Figure(go.Bar(
            x=top[field].tolist(), y=top["district"].tolist(), orientation="h",
            marker_color=[PALETTE[c] for c in top["priority_category"]],
            text=[f"{v:+.1f}{unit}" for v in top[field]], textposition="outside",
            hovertemplate="%{y}: %{x:.2f}%<extra></extra>"
        ))
        fig2.update_layout(height=280, margin=dict(l=10,r=65,t=8,b=32),
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Change (%)", zeroline=True, zerolinecolor="#94A3B8"),
            yaxis=dict(title=None))
        st.plotly_chart(fig2, use_container_width=True, key="executive_change_chart")
    st.caption("Bar colours represent existing screening categories. Ranking shows the five lowest measured values, which are not necessarily confirmed crop losses or the five highest-risk districts.")
    with st.expander("What does the evidence mean?"):
        st.markdown(
            "**Interpretation:** The 30 districts have different rainfall anomalies and maize/bean yield changes. "
            "A field-review recommendation is a screening priority, not proof of failure. "
            "Compare crops separately: a declining yield in one crop can coincide with an increase in another. "
            "Positive NDVI anomalies can occur alongside yield declines because cropland-averaged greenness is not crop-specific yield. "
            "**Limitations:** Two NISR Season B surveys establish a comparison, not a long-term trend; "
            "survey uncertainty, 250 m MODIS pixels, CHIRPS resolution, and the historical cropland mask limit inference. "
            "Use the detailed statistics and sensitivity tabs below before interpreting individual districts."
        )
    st.divider()

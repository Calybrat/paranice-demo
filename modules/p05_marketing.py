import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    return pd.read_csv(DATA/"marketing.csv")

def render():
    m = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Marketing & Canales</div>
        <div class="cb-sub">Inversión, retorno publicitario (ROAS) y desempeño por canal digital</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        paises_all = ["Todos"] + sorted(m["pais"].unique().tolist())
        pais_sel = st.selectbox("País", paises_all, key="mk_pais")
    with col_f2:
        meses = sorted(m["mes"].unique())
        rango = st.select_slider("Rango de meses", options=meses, value=(meses[max(0,len(meses)-6)], meses[-1]), key="mk_rango")

    mf = m[(m["mes"] >= rango[0]) & (m["mes"] <= rango[1])]
    if pais_sel != "Todos": mf = mf[mf["pais"] == pais_sel]

    inversion_total = mf["inversion_cop"].sum()
    ingresos_atrib = mf["ingresos_atribuidos_cop"].sum()
    roas = ingresos_atrib / inversion_total if inversion_total else 0
    clics_total = mf["clics"].sum()
    imp_total = mf["impresiones"].sum()
    ctr = clics_total / imp_total * 100 if imp_total else 0
    cpc = inversion_total / clics_total if clics_total else 0
    mejor_canal = mf.groupby("canal").apply(
        lambda g: g["ingresos_atribuidos_cop"].sum()/g["inversion_cop"].sum() if g["inversion_cop"].sum() else 0,
        include_groups=False).idxmax()

    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Inversión total", cop(inversion_total, 1), "Canales pagos", True, "💵"), unsafe_allow_html=True)
    k2.markdown(kpi("Ingresos atribuidos", cop(ingresos_atrib, 1), "", True, "📈"), unsafe_allow_html=True)
    k3.markdown(kpi("ROAS blended", f"{roas:.1f}x", "Meta: 3x", roas >= 3, "🎯"), unsafe_allow_html=True)
    k4.markdown(kpi("CTR promedio", pct(ctr, 2), "", ctr > 1, "👆"), unsafe_allow_html=True)
    k5.markdown(kpi("CPC promedio", cop(cpc), "", True, "💰"), unsafe_allow_html=True)
    k6.markdown(kpi("Mejor canal (ROAS)", mejor_canal, "", True, "🏅"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.4, 1], gap="medium")
    with c1:
        canal_agg = mf.groupby("canal").agg(inversion=("inversion_cop","sum"), ingresos=("ingresos_atribuidos_cop","sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=canal_agg["canal"], y=canal_agg["inversion"], name="Inversión", marker_color=MUTED))
        fig.add_trace(go.Bar(x=canal_agg["canal"], y=canal_agg["ingresos"], name="Ingresos atribuidos", marker_color=GREEN))
        fig.update_layout(barmode="group")
        st.plotly_chart(dark(fig, 340, "Inversión vs. ingresos por canal"), use_container_width=True)
    with c2:
        canal_agg["roas"] = canal_agg["ingresos"] / canal_agg["inversion"].replace(0, np.nan)
        canal_agg = canal_agg.sort_values("roas")
        fig = go.Figure(go.Bar(x=canal_agg["roas"], y=canal_agg["canal"], orientation="h",
                                marker_color=[GREEN if r >= 3 else AMBER for r in canal_agg["roas"].fillna(0)],
                                text=[f"{r:.1f}x" if pd.notna(r) else "—" for r in canal_agg["roas"]],
                                textposition="outside"))
        st.plotly_chart(dark(fig, 340, "ROAS por canal"), use_container_width=True)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        piv = mf[mf["canal"] != "Orgánico/SEO"].groupby(["mes","canal"])["inversion_cop"].sum().reset_index()
        fig = go.Figure()
        for i, canal in enumerate(sorted(piv["canal"].unique())):
            sub = piv[piv["canal"] == canal]
            fig.add_trace(go.Scatter(x=sub["mes"], y=sub["inversion_cop"], name=canal, mode="lines",
                                      stackgroup="one", line=dict(width=0.5, color=PALETTE[i % len(PALETTE)])))
        st.plotly_chart(dark(fig, 320, "Inversión mensual por canal"), use_container_width=True)
    with c4:
        funnel_vals = [imp_total, clics_total, mf["pedidos_atribuidos"].sum()]
        fig = go.Figure(go.Funnel(
            y=["Impresiones","Clics","Pedidos atribuidos"], x=funnel_vals,
            marker=dict(color=[GREEN, CREAM, CORAL]),
            textinfo="value+percent initial",
        ))
        st.plotly_chart(dark(fig, 320, "Funnel de adquisición"), use_container_width=True)

    st.markdown(f"<p style='font-size:13px;font-weight:700;color:{TEXT};margin:16px 0 8px'>📋 Resumen por canal y país</p>", unsafe_allow_html=True)
    tabla = mf.groupby(["canal","pais"]).agg(
        inversion=("inversion_cop","sum"), ingresos=("ingresos_atribuidos_cop","sum"),
        pedidos=("pedidos_atribuidos","sum"), clics=("clics","sum")).reset_index()
    tabla["roas"] = (tabla["ingresos"] / tabla["inversion"].replace(0, np.nan)).astype(float).round(2)
    tabla["inversion"] = tabla["inversion"].apply(cop)
    tabla["ingresos"] = tabla["ingresos"].apply(cop)
    st.dataframe(tabla.sort_values("roas", ascending=False), hide_index=True, use_container_width=True)

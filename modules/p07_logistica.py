import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    e = pd.read_csv(DATA/"envios.csv")
    e["fecha_pedido"] = pd.to_datetime(e["fecha_pedido"])
    e["fecha_entrega_prometida"] = pd.to_datetime(e["fecha_entrega_prometida"])
    e["fecha_entrega_real"] = pd.to_datetime(e["fecha_entrega_real"], errors="coerce")
    return e

def render():
    e = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Logística & Envíos</div>
        <div class="cb-sub">Cumplimiento de entregas (OTD), tiempos de tránsito y costo de envío por país</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    hoy = pd.Timestamp("2026-08-31")
    ent = e[e["estado"] == "Entregado"]
    otd = (ent["entregado_a_tiempo"] == True).mean() * 100 if len(ent) else 0
    dias_prom = ent["dias_transito"].mean() if len(ent) else 0
    costo_prom = e["costo_envio_cop"].mean()
    pct_costo_venta = (e["costo_envio_cop"].sum() / e["valor_pedido_cop"].sum() * 100) if e["valor_pedido_cop"].sum() else 0
    retrasados = e[(e["estado"] == "En tránsito") & (e["fecha_entrega_prometida"] < hoy)].shape[0]
    total_envios = len(e)

    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Total envíos", f"{total_envios:,}", "Histórico", True, "📮"), unsafe_allow_html=True)
    k2.markdown(kpi("OTD global", pct(otd), "Meta: 90%", otd >= 90, "🚚"), unsafe_allow_html=True)
    k3.markdown(kpi("Días tránsito prom.", f"{dias_prom:.1f} días", "", dias_prom < 5, "⏱️"), unsafe_allow_html=True)
    k4.markdown(kpi("Costo envío promedio", cop(costo_prom), "", True, "💸"), unsafe_allow_html=True)
    k5.markdown(kpi("Envío / Venta", pct(pct_costo_venta), "% del ticket", pct_costo_venta < 15, "📊"), unsafe_allow_html=True)
    k6.markdown(kpi("Envíos retrasados", str(retrasados), "En tránsito, fuera de SLA", retrasados == 0, "⚠️"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        otd_pais = ent.groupby("pais_destino").apply(
            lambda g: (g["entregado_a_tiempo"] == True).mean() * 100, include_groups=False).sort_values()
        fig = go.Figure(go.Bar(x=otd_pais.values, y=otd_pais.index, orientation="h",
                                marker_color=[GREEN if v >= 90 else AMBER for v in otd_pais.values],
                                text=[f"{v:.1f}%" for v in otd_pais.values], textposition="outside"))
        st.plotly_chart(dark(fig, 300, "OTD por país de destino"), use_container_width=True)
    with c2:
        costo_pais = e.groupby("pais_destino")["costo_envio_cop"].mean().sort_values(ascending=True)
        fig = go.Figure(go.Bar(x=costo_pais.values, y=costo_pais.index, orientation="h",
                                marker_color=CREAM,
                                hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                customdata=[cop(v) for v in costo_pais.values]))
        st.plotly_chart(dark(fig, 300, "Costo de envío promedio por país"), use_container_width=True)
    with c3:
        transp = ent.groupby("transportadora").apply(
            lambda g: (g["entregado_a_tiempo"] == True).mean() * 100, include_groups=False).sort_values(ascending=True)
        fig = go.Figure(go.Bar(x=transp.values, y=transp.index, orientation="h",
                                marker_color=[GREEN if v >= 90 else AMBER for v in transp.values],
                                text=[f"{v:.1f}%" for v in transp.values], textposition="outside"))
        st.plotly_chart(dark(fig, 300, "OTD por transportadora"), use_container_width=True)

    c4, c5 = st.columns(2, gap="medium")
    with c4:
        e_mes = e.copy()
        e_mes["mes_p"] = e_mes["fecha_pedido"].dt.to_period("M").astype(str)
        tr_mes = e_mes[e_mes["estado"] == "Entregado"].groupby("mes_p")["dias_transito"].mean()
        fig = go.Figure(go.Scatter(x=tr_mes.index, y=tr_mes.values, mode="lines+markers",
                                    line=dict(color=GREEN, width=2), marker=dict(color=CREAM, size=5)))
        st.plotly_chart(dark(fig, 300, "Tiempo de tránsito promedio por mes"), use_container_width=True)
    with c5:
        estado_count = e["estado"].value_counts()
        fig = go.Figure(go.Pie(labels=estado_count.index, values=estado_count.values, hole=0.55,
                                marker_colors=PALETTE, textinfo="label+percent"))
        st.plotly_chart(dark(fig, 300, "Envíos por estado"), use_container_width=True)

    st.markdown(f"<p style='font-size:13px;font-weight:700;color:{TEXT};margin:16px 0 8px'>⚠️ Envíos retrasados (en tránsito, fuera de SLA)</p>", unsafe_allow_html=True)
    ret_df = e[(e["estado"] == "En tránsito") & (e["fecha_entrega_prometida"] < hoy)].sort_values("fecha_entrega_prometida")[
        ["envio_id","pedido_id","pais_destino","ciudad_destino","transportadora","fecha_pedido","fecha_entrega_prometida"]].copy()
    ret_df["fecha_pedido"] = ret_df["fecha_pedido"].dt.strftime("%Y-%m-%d")
    ret_df["fecha_entrega_prometida"] = ret_df["fecha_entrega_prometida"].dt.strftime("%Y-%m-%d")
    if len(ret_df):
        st.dataframe(ret_df, hide_index=True, use_container_width=True)
    else:
        st.success("No hay envíos retrasados en este momento.")

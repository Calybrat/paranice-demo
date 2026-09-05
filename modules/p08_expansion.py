import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    g = pd.read_csv(DATA/"paises_mensual.csv")
    g["periodo"] = pd.to_datetime(g["periodo"])
    return g

LANZAMIENTOS = {"Colombia": "Ene 2025", "Costa Rica": "Abr 2025", "Estados Unidos": "Oct 2025"}

def render():
    g = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Expansión Internacional</div>
        <div class="cb-sub">Comparativo Colombia · Costa Rica · Estados Unidos — tracción de cada mercado desde su lanzamiento</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    ultimo_mes = g["periodo"].max()
    g_ult3 = g[g["periodo"] >= ultimo_mes - pd.DateOffset(months=2)]
    total_ventas = g["ventas_cop"].sum()
    por_pais = g.groupby("pais")["ventas_cop"].sum()

    g_prev = g[g["periodo"] == ultimo_mes - pd.DateOffset(months=1)]
    g_curr = g[g["periodo"] == ultimo_mes]
    crecimiento_mom = {}
    for pais in g["pais"].unique():
        prev = g_prev[g_prev["pais"] == pais]["ventas_cop"].sum()
        curr = g_curr[g_curr["pais"] == pais]["ventas_cop"].sum()
        crecimiento_mom[pais] = (curr - prev) / prev * 100 if prev else 0

    k1, k2, k3, k4 = st.columns(4, gap="small")
    k1.markdown(kpi("Mercados activos", str(g["pais"].nunique()), "CO · CR · USA", True, "🌎"), unsafe_allow_html=True)
    k2.markdown(kpi("Ventas Colombia", pct(por_pais.get("Colombia",0)/total_ventas*100), f"desde {LANZAMIENTOS['Colombia']}", True, "🇨🇴"), unsafe_allow_html=True)
    k3.markdown(kpi("Ventas Costa Rica", pct(por_pais.get("Costa Rica",0)/total_ventas*100), f"desde {LANZAMIENTOS['Costa Rica']}", True, "🇨🇷"), unsafe_allow_html=True)
    k4.markdown(kpi("Ventas Estados Unidos", pct(por_pais.get("Estados Unidos",0)/total_ventas*100), f"desde {LANZAMIENTOS['Estados Unidos']}", True, "🇺🇸"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.5, 1], gap="medium")
    with c1:
        fig = go.Figure()
        for i, pais in enumerate(sorted(g["pais"].unique())):
            sub = g[g["pais"] == pais].sort_values("periodo")
            fig.add_trace(go.Scatter(x=sub["periodo"], y=sub["ventas_cop"], mode="lines+markers",
                                      name=pais, line=dict(width=2, color=PALETTE[i % len(PALETTE)])))
        st.plotly_chart(dark(fig, 360, "Ventas mensuales por país"), use_container_width=True)
    with c2:
        fig = go.Figure(go.Pie(labels=por_pais.index, values=por_pais.values, hole=0.55,
                                marker_colors=PALETTE, textinfo="label+percent"))
        st.plotly_chart(dark(fig, 360, "Participación acumulada por país"), use_container_width=True)

    c3, c4, c5 = st.columns(3, gap="medium")
    with c3:
        colores = [GREEN if crecimiento_mom[p] >= 0 else RED for p in crecimiento_mom]
        fig = go.Figure(go.Bar(x=list(crecimiento_mom.keys()), y=list(crecimiento_mom.values()), marker_color=colores,
                                text=[f"{v:+.1f}%" for v in crecimiento_mom.values()], textposition="outside"))
        st.plotly_chart(dark(fig, 300, "Crecimiento mes vs. mes anterior"), use_container_width=True)
    with c4:
        clientes_pais = g.groupby("pais")["clientes_activos"].sum()
        fig = go.Figure(go.Bar(x=clientes_pais.index, y=clientes_pais.values, marker_color=CREAM,
                                text=clientes_pais.values, textposition="outside"))
        st.plotly_chart(dark(fig, 300, "Clientes-mes activos acumulados"), use_container_width=True)
    with c5:
        ticket_pais = g.groupby("pais").apply(
            lambda d: (d["ventas_cop"].sum()/d["pedidos"].sum()) if d["pedidos"].sum() else 0, include_groups=False)
        fig = go.Figure(go.Bar(x=ticket_pais.index, y=ticket_pais.values, marker_color=SKY,
                                text=[cop(v) for v in ticket_pais.values], textposition="outside"))
        st.plotly_chart(dark(fig, 300, "Ticket promedio por país"), use_container_width=True)

    st.markdown(f"<p style='font-size:13px;font-weight:700;color:{TEXT};margin:16px 0 8px'>📋 Comparativo mensual (últimos 3 meses)</p>", unsafe_allow_html=True)
    tabla = g_ult3.groupby("pais").agg(
        ventas=("ventas_cop","sum"), pedidos=("pedidos","sum"), clientes=("clientes_activos","sum"),
        ticket_prom=("ticket_promedio_cop","mean")).reset_index().sort_values("ventas", ascending=False)
    tabla["ventas"] = tabla["ventas"].apply(cop)
    tabla["ticket_prom"] = tabla["ticket_prom"].apply(cop)
    st.dataframe(tabla, hide_index=True, use_container_width=True)

    st.markdown(f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:12px;padding:16px 20px;margin-top:6px">
      <p style="font-size:13px;font-weight:700;color:{TEXT};margin:0 0 6px">🗓️ Línea de tiempo de expansión</p>
      <p style="font-size:12px;color:{MUTED};margin:0">
        🇨🇴 Colombia — mercado base desde {LANZAMIENTOS['Colombia']} &nbsp;·&nbsp;
        🇨🇷 Costa Rica — lanzado en {LANZAMIENTOS['Costa Rica']} &nbsp;·&nbsp;
        🇺🇸 Estados Unidos — lanzado en {LANZAMIENTOS['Estados Unidos']}
      </p>
    </div>""", unsafe_allow_html=True)

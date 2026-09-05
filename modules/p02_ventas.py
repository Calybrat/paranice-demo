import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    p = pd.read_csv(DATA/"pedidos.csv")
    p["fecha"] = pd.to_datetime(p["fecha"])
    return p

def render():
    p = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Ventas & E-commerce</div>
        <div class="cb-sub">Desempeño comercial de la tienda en línea · pedidos, ticket promedio y canales</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        anios = sorted(p["fecha"].dt.year.unique().tolist(), reverse=True)
        anio_sel = st.selectbox("Año", anios, key="vt_anio")
    with col_f2:
        paises_all = ["Todos"] + sorted(p["pais"].unique().tolist())
        pais_sel  = st.selectbox("País", paises_all, key="vt_pais")
    with col_f3:
        canales_all = ["Todos"] + sorted(p["canal"].unique().tolist())
        canal_sel = st.selectbox("Canal", canales_all, key="vt_canal")

    pf = p[p["fecha"].dt.year == anio_sel]
    if pais_sel != "Todos": pf = pf[pf["pais"] == pais_sel]
    if canal_sel != "Todos": pf = pf[pf["canal"] == canal_sel]

    ped_unicos = pf.drop_duplicates("pedido_id")
    total = pf["total_cop"].sum()
    n_pedidos = pf["pedido_id"].nunique()
    aov = total / n_pedidos if n_pedidos else 0
    n_clientes = pf["cliente_id"].nunique()
    desc_prom = ped_unicos["descuento_pct"].mean() * 100 if len(ped_unicos) else 0
    margen = pf["margen_pct"].mean() * 100 if len(pf) else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Ventas", cop(total, 1), f"Año {anio_sel}", True, "💰"), unsafe_allow_html=True)
    k2.markdown(kpi("Pedidos", f"{n_pedidos:,}", "", True, "🧾"), unsafe_allow_html=True)
    k3.markdown(kpi("Ticket promedio (AOV)", cop(aov), "", True, "🛒"), unsafe_allow_html=True)
    k4.markdown(kpi("Clientes únicos", f"{n_clientes:,}", "", True, "🧑‍🤝‍🧑"), unsafe_allow_html=True)
    k5.markdown(kpi("Descuento promedio", pct(desc_prom), "", desc_prom < 8, "🏷️"), unsafe_allow_html=True)
    k6.markdown(kpi("Margen bruto", pct(margen), "Meta: 60%", margen >= 60, "📊"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.6, 1], gap="medium")
    with c1:
        sem = ped_unicos.copy()
        sem["semana"] = sem["fecha"].dt.to_period("W").apply(lambda r: r.start_time)
        agg = sem.groupby("semana")["total_cop"].sum().reset_index()
        fig = go.Figure(go.Scatter(x=agg["semana"], y=agg["total_cop"], mode="lines+markers",
                                    line=dict(color=GREEN, width=2), marker=dict(size=5, color=CREAM),
                                    fill="tozeroy", fillcolor=f"{GREEN}22",
                                    hovertemplate="<b>%{x|%d %b %Y}</b><br>%{customdata}<extra></extra>",
                                    customdata=[cop(v,1) for v in agg["total_cop"]]))
        st.plotly_chart(dark(fig, 320, "Ventas semanales"), use_container_width=True)
    with c2:
        mp = ped_unicos.groupby("metodo_pago")["total_cop"].sum().reset_index().sort_values("total_cop")
        fig = go.Figure(go.Bar(x=mp["total_cop"], y=mp["metodo_pago"], orientation="h",
                                marker_color=PALETTE[:len(mp)],
                                hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                customdata=[cop(v,1) for v in mp["total_cop"]]))
        st.plotly_chart(dark(fig, 320, "Ventas por método de pago"), use_container_width=True)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        top_prod = pf.groupby("producto")["total_cop"].sum().nlargest(10).reset_index().sort_values("total_cop")
        fig = go.Figure(go.Bar(x=top_prod["total_cop"], y=top_prod["producto"], orientation="h",
                                marker_color=GREEN,
                                hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                customdata=[cop(v,1) for v in top_prod["total_cop"]]))
        st.plotly_chart(dark(fig, 340, "Top 10 productos por ingresos"), use_container_width=True)
    with c4:
        canal_mes = ped_unicos.copy()
        canal_mes["mes_p"] = canal_mes["fecha"].dt.to_period("M").astype(str)
        piv = canal_mes.groupby(["mes_p","canal"])["total_cop"].sum().reset_index()
        fig = go.Figure()
        for i, canal in enumerate(sorted(piv["canal"].unique())):
            sub = piv[piv["canal"] == canal]
            fig.add_trace(go.Bar(x=sub["mes_p"], y=sub["total_cop"], name=canal, marker_color=PALETTE[i % len(PALETTE)]))
        fig.update_layout(barmode="stack")
        st.plotly_chart(dark(fig, 340, f"Ventas por canal · {anio_sel}"), use_container_width=True)

    st.markdown(f"<p style='font-size:13px;font-weight:700;color:{TEXT};margin:16px 0 8px'>🧾 Pedidos recientes</p>", unsafe_allow_html=True)
    recientes = ped_unicos.sort_values("fecha", ascending=False).head(20)[
        ["pedido_id","fecha","pais","ciudad","canal","metodo_pago","total_cop"]].copy()
    recientes["fecha"] = recientes["fecha"].dt.strftime("%Y-%m-%d")
    recientes["total_cop"] = recientes["total_cop"].apply(cop)
    st.dataframe(recientes, hide_index=True, use_container_width=True)

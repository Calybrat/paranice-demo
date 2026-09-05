import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    c = pd.read_csv(DATA/"clientes.csv")
    c["fecha_primera_compra"] = pd.to_datetime(c["fecha_primera_compra"])
    m = pd.read_csv(DATA/"marketing.csv")
    return c, m

def render():
    c, m = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Clientes & Retención</div>
        <div class="cb-sub">Adquisición, valor de vida (LTV) y satisfacción de los clientes de Paranice</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    total_clientes = len(c)
    pct_recompra = c["cliente_recurrente"].mean() * 100
    ltv_prom = c["ltv_cop"].mean()
    nps_prom = c["nps_score"].mean()

    c["mes_primera"] = c["fecha_primera_compra"].dt.strftime("%Y-%m")
    nuevos_por_mes = c.groupby("mes_primera").size()
    m_paid = m[m["canal"] != "Orgánico/SEO"]
    gasto_total = m_paid["inversion_cop"].sum()
    cac_blended = gasto_total / total_clientes if total_clientes else 0
    ltv_cac = ltv_prom / cac_blended if cac_blended else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Clientes totales", f"{total_clientes:,}", "Con al menos 1 compra", True, "🧑‍🤝‍🧑"), unsafe_allow_html=True)
    k2.markdown(kpi("Tasa de recompra", pct(pct_recompra), "≥2 pedidos", pct_recompra > 40, "🔁"), unsafe_allow_html=True)
    k3.markdown(kpi("LTV promedio", cop(ltv_prom), "Por cliente", True, "💎"), unsafe_allow_html=True)
    k4.markdown(kpi("CAC estimado", cop(cac_blended), "Blended, canales pagos", cac_blended < ltv_prom*0.3, "🎯"), unsafe_allow_html=True)
    k5.markdown(kpi("Ratio LTV:CAC", f"{ltv_cac:.1f}x", "Meta: >3x", ltv_cac >= 3, "⚖️"), unsafe_allow_html=True)
    k6.markdown(kpi("NPS promedio", f"{nps_prom:.1f}/10", "Encuesta post-compra", nps_prom >= 7, "🙂"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.4, 1], gap="medium")
    with c1:
        agg = nuevos_por_mes.reset_index()
        agg.columns = ["mes","nuevos"]
        fig = go.Figure(go.Bar(x=agg["mes"], y=agg["nuevos"], marker_color=GREEN))
        fig.add_trace(go.Scatter(x=agg["mes"], y=agg["nuevos"].rolling(3, min_periods=1).mean(),
                                  mode="lines", line=dict(color=CORAL, width=2, dash="dot"), name="Media 3 meses"))
        st.plotly_chart(dark(fig, 340, "Clientes nuevos por mes"), use_container_width=True)
    with c2:
        seg = c["segmento"].value_counts().reindex(["VIP","Recurrente","Compra única"]).fillna(0)
        fig = go.Figure(go.Pie(labels=seg.index, values=seg.values, hole=0.55,
                                marker_colors=[CORAL, GREEN, MUTED], textinfo="label+percent"))
        st.plotly_chart(dark(fig, 340, "Clientes por segmento"), use_container_width=True)

    c3, c4, c5 = st.columns(3, gap="medium")
    with c3:
        ltv_pais = c.groupby("pais")["ltv_cop"].mean().sort_values(ascending=True)
        fig = go.Figure(go.Bar(x=ltv_pais.values, y=ltv_pais.index, orientation="h",
                                marker_color=PALETTE[:len(ltv_pais)],
                                hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                customdata=[cop(v) for v in ltv_pais.values]))
        st.plotly_chart(dark(fig, 300, "LTV promedio por país"), use_container_width=True)
    with c4:
        nps_dist = c["nps_score"].value_counts().sort_index()
        colors = [RED if s <= 6 else AMBER if s <= 8 else GREEN for s in nps_dist.index]
        fig = go.Figure(go.Bar(x=nps_dist.index.astype(str), y=nps_dist.values, marker_color=colors))
        st.plotly_chart(dark(fig, 300, "Distribución de NPS (0–10)"), use_container_width=True)
    with c5:
        ciudad = c.groupby("ciudad").size().nlargest(8).reset_index(name="clientes").sort_values("clientes")
        fig = go.Figure(go.Bar(x=ciudad["clientes"], y=ciudad["ciudad"], orientation="h", marker_color=CREAM))
        st.plotly_chart(dark(fig, 300, "Top 8 ciudades por clientes"), use_container_width=True)

    promotores = (c["nps_score"] >= 9).mean() * 100
    detractores = (c["nps_score"] <= 6).mean() * 100
    nps_neto = promotores - detractores
    st.markdown(f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:12px;padding:16px 20px;margin-top:6px">
      <p style="font-size:13px;font-weight:700;color:{TEXT};margin:0 0 6px">📊 NPS neto: <span style="color:{GREEN if nps_neto>=30 else AMBER}">{nps_neto:.0f}</span></p>
      <p style="font-size:12px;color:{MUTED};margin:0">Promotores (9–10): {pct(promotores)} · Pasivos (7–8): {pct(100-promotores-detractores)} · Detractores (0–6): {pct(detractores)}</p>
    </div>""", unsafe_allow_html=True)

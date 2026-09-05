import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    inv = pd.read_csv(DATA/"inventario.csv")
    prod = pd.read_csv(DATA/"produccion.csv")
    prod["fecha_produccion"] = pd.to_datetime(prod["fecha_produccion"])
    pro = pd.read_csv(DATA/"proveedores.csv")
    return inv, prod, pro

def render():
    inv, prod, pro = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Inventario & Producción</div>
        <div class="cb-sub">Stock multi-bodega y control de calidad de lotes (prevención de contaminación cruzada de gluten)</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    valor_total = inv["valor_inventario"].sum()
    criticos = inv[inv["estado"] == "Crítico"].shape[0]
    bajos = inv[inv["estado"] == "Bajo"].shape[0]
    cobertura = inv["dias_cobertura"].mean()

    p2026 = prod[prod["fecha_produccion"].dt.year == 2026]
    n_lotes = len(p2026)
    tasa_aprobacion = (p2026["estado_calidad"] == "Aprobado").mean() * 100 if n_lotes else 0
    ppm_prom = p2026[p2026["es_sin_gluten"] == True]["resultado_gluten_ppm"].mean()

    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Valor inventario", cop(valor_total, 1), "3 bodegas", True, "📦"), unsafe_allow_html=True)
    k2.markdown(kpi("SKUs críticos", str(criticos), f"{bajos} en nivel bajo", criticos == 0, "🚨"), unsafe_allow_html=True)
    k3.markdown(kpi("Cobertura promedio", f"{cobertura:.0f} días", "", cobertura > 20, "📅"), unsafe_allow_html=True)
    k4.markdown(kpi("Lotes producidos", f"{n_lotes:,}", "2026 YTD", True, "🏭"), unsafe_allow_html=True)
    k5.markdown(kpi("Tasa de aprobación QC", pct(tasa_aprobacion), "Meta: ≥97%", tasa_aprobacion >= 97, "✅"), unsafe_allow_html=True)
    k6.markdown(kpi("PPM gluten promedio", f"{ppm_prom:.1f} ppm", "Límite: 20 ppm", ppm_prom < 15, "🧪"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        bod = inv.groupby("bodega")["valor_inventario"].sum().sort_values(ascending=True)
        fig = go.Figure(go.Bar(x=bod.values, y=bod.index, orientation="h",
                                marker_color=PALETTE[:len(bod)],
                                hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                customdata=[cop(v,1) for v in bod.values]))
        st.plotly_chart(dark(fig, 300, "Valor de inventario por bodega"), use_container_width=True)
    with c2:
        estado_count = inv["estado"].value_counts().reindex(["Crítico","Bajo","Normal","Alto"]).fillna(0)
        fig = go.Figure(go.Pie(labels=estado_count.index, values=estado_count.values, hole=0.55,
                                marker_colors=[RED, AMBER, GREEN, SKY], textinfo="label+value"))
        st.plotly_chart(dark(fig, 300, "SKUs por estado de stock"), use_container_width=True)
    with c3:
        calidad_count = prod["estado_calidad"].value_counts().reindex(["Aprobado","Cuarentena","Rechazado"]).fillna(0)
        fig = go.Figure(go.Bar(x=calidad_count.index, y=calidad_count.values,
                                marker_color=[GREEN, AMBER, RED],
                                text=calidad_count.values, textposition="outside"))
        st.plotly_chart(dark(fig, 300, "Lotes por resultado de calidad (histórico)"), use_container_width=True)

    c4, c5 = st.columns(2, gap="medium")
    with c4:
        gf = prod[prod["es_sin_gluten"] == True].copy()
        fig = go.Figure(go.Histogram(x=gf["resultado_gluten_ppm"], nbinsx=20, marker_color=GREEN))
        fig.add_vline(x=20, line_dash="dash", line_color=RED, annotation_text="Límite 20ppm", annotation_font_color=RED)
        st.plotly_chart(dark(fig, 320, "Distribución de resultados de gluten (ppm) — SKUs sin gluten"), use_container_width=True)
    with c5:
        criticos_df = inv[inv["estado"].isin(["Crítico","Bajo"])].sort_values("dias_cobertura").head(10)[
            ["producto","bodega","stock_actual","stock_minimo","dias_cobertura","estado"]]
        st.markdown(f"<p style='font-size:12px;color:{MUTED};margin-bottom:6px'>⚠️ SKUs con menor cobertura</p>", unsafe_allow_html=True)
        st.dataframe(criticos_df, hide_index=True, use_container_width=True, height=320)

    st.markdown(f"<p style='font-size:13px;font-weight:700;color:{TEXT};margin:16px 0 8px'>🧪 Lotes recientes en cuarentena o rechazados</p>", unsafe_allow_html=True)
    alertas = prod[prod["estado_calidad"].isin(["Cuarentena","Rechazado"])].sort_values("fecha_produccion", ascending=False).head(15)[
        ["lote_id","fecha_produccion","producto","cantidad_kg","resultado_gluten_ppm","estado_calidad"]].copy()
    alertas["fecha_produccion"] = alertas["fecha_produccion"].dt.strftime("%Y-%m-%d")
    st.dataframe(alertas, hide_index=True, use_container_width=True)

    st.markdown(f"<div style='height:8px'></div>", unsafe_allow_html=True)
    with st.expander("🌎  Proveedores de insumos clave", expanded=False):
        c6, c7 = st.columns([1.3, 1], gap="medium")
        with c6:
            pro_sorted = pro.sort_values("score_general", ascending=True)
            fig = go.Figure(go.Bar(x=pro_sorted["score_general"], y=pro_sorted["proveedor"], orientation="h",
                                    marker_color=[GREEN if v >= 8.5 else AMBER for v in pro_sorted["score_general"]],
                                    text=pro_sorted["score_general"], textposition="outside"))
            st.plotly_chart(dark(fig, 320, "Score general de proveedores (calidad · puntualidad · precio)"), use_container_width=True)
        with c7:
            lt = pro.sort_values("lead_time_avg_dias", ascending=False)[["proveedor","pais","especialidad","lead_time_avg_dias"]]
            st.markdown(f"<p style='font-size:12px;color:{MUTED};margin-bottom:6px'>Lead time promedio por proveedor (días)</p>", unsafe_allow_html=True)
            st.dataframe(lt, hide_index=True, use_container_width=True, height=320)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *


@st.cache_data
def load():
    p = leer_csv("produccion.csv"); p["fecha"] = pd.to_datetime(p["fecha"])
    i = leer_csv("inventario.csv")
    pr = leer_csv("proveedores.csv")
    return p, i, pr


def render():
    prod, inv, prov = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Producción & Calidad",
        "Planta, lotes y el ensayo de gluten que sostiene el claim de la marca · "
        "más inventario y proveedores de insumos",
        "personaje_8.png"), unsafe_allow_html=True)

    st.markdown(panel("Por qué la calidad aquí es un tema de negocio, no solo de laboratorio", """
        La promesa de Paranice es <b>libre de gluten</b> y el sitio lo dice explícitamente: se evita la
        contaminación cruzada tratando cada hojuela con cuidado. El estándar internacional exige
        <b>menos de 20 ppm</b>. Un lote por encima de ese umbral no es solo producto perdido: es riesgo
        reputacional y de salud del consumidor. Este tablero deja esa trazabilidad a la vista.
    """, "🧪"), unsafe_allow_html=True)

    meses = sorted(prod["mes"].unique())
    f1, f2 = st.columns([1.4, 1])
    with f1:
        rango = st.select_slider("Rango de meses", options=meses,
                                 value=(meses[max(0, len(meses)-6)], meses[-1]), key="pd_rango")
    with f2:
        cat = st.multiselect("Categorías", sorted(prod["categoria"].unique()),
                             default=sorted(prod["categoria"].unique()), key="pd_cat")

    pf = prod[(prod["mes"] >= rango[0]) & (prod["mes"] <= rango[1])]
    if cat:
        pf = pf[pf["categoria"].isin(cat)]
    if pf.empty:
        st.warning("No hay lotes con los filtros seleccionados.")
        return

    lotes = len(pf)
    unidades = int(pf["unidades_producidas"].sum())
    aprobacion = (pf["estado_calidad"] == "Aprobado").mean() * 100
    merma = pf["merma_pct"].mean()
    cumplimiento = pf["cumplimiento_plan_pct"].mean()
    gf = pf[pf["es_sin_gluten"] == True]
    ppm = gf["gluten_ppm"].mean()
    fuera = int((gf["gluten_ppm"] > 20).sum())
    costo_perdido = pf[pf["estado_calidad"] == "Rechazado"]["costo_lote_cop"].sum()

    k = st.columns(6, gap="small")
    k[0].markdown(kpi("Lotes producidos", f"{lotes:,}", f"{unidades:,} unidades", True, "🏭"),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("Aprobación de calidad", pct(aprobacion), "Meta: 98%", aprobacion >= 98, "✅"),
                  unsafe_allow_html=True)
    k[2].markdown(kpi("Gluten promedio", f"{ppm:.1f} ppm", "Límite legal: 20 ppm", ppm < 12, "🧪",
                      "Promedio de los ensayos de lote."), unsafe_allow_html=True)
    k[3].markdown(kpi("Lotes fuera de norma", str(fuera), "Por encima de 20 ppm", fuera == 0, "🚨"),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("Merma", pct(merma), "Meta: menos de 3%", merma < 3, "🗑️",
                      "Producto que se pierde en el proceso."), unsafe_allow_html=True)
    k[5].markdown(kpi("Costo de lo rechazado", cop(costo_perdido, 1), "En el período", costo_perdido == 0,
                      "💸"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🧪  Calidad y gluten", "⚙️  Planta", "📦  Inventario y proveedores"])

    with t1:
        c1, c2 = st.columns([1.4, 1], gap="medium")
        with c1:
            fig = go.Figure(go.Histogram(x=gf["gluten_ppm"], nbinsx=26, marker_color=PURPLE,
                                         opacity=0.88))
            fig.add_vline(x=20, line_dash="dash", line_color=BAD,
                          annotation_text="Límite 20 ppm", annotation_font_color=BAD)
            fig.add_vline(x=15, line_dash="dot", line_color=WARN,
                          annotation_text="Alerta 15 ppm", annotation_font_color=WARN)
            st.plotly_chart(light(fig, 340, "Distribución de resultados de gluten (ppm)"),
                            use_container_width=True)
        with c2:
            estados = pf["estado_calidad"].value_counts().reindex(
                ["Aprobado", "Cuarentena", "Rechazado"]).fillna(0)
            fig = go.Figure(go.Bar(x=estados.index, y=estados.values,
                                   marker_color=[GOOD, WARN, BAD],
                                   text=[int(x) for x in estados.values], textposition="outside"))
            st.plotly_chart(light(fig, 340, "Resultado de los lotes"), use_container_width=True)

        ev = pf.groupby("mes").agg(ppm=("gluten_ppm", "mean"),
                                   aprob=("estado_calidad", lambda s: (s == "Aprobado").mean() * 100)).reset_index()
        c3, c4 = st.columns(2, gap="medium")
        with c3:
            fig = go.Figure(go.Scatter(x=ev["mes"], y=ev["ppm"], mode="lines+markers",
                                       line=dict(color=PURPLE, width=3), fill="tozeroy",
                                       fillcolor="rgba(42,29,101,.08)"))
            fig.add_hline(y=20, line_dash="dash", line_color=BAD)
            st.plotly_chart(light(fig, 300, "Gluten promedio por mes (ppm)"), use_container_width=True)
        with c4:
            fig = go.Figure(go.Bar(x=ev["mes"], y=ev["aprob"],
                                   marker_color=[GOOD if x >= 98 else WARN for x in ev["aprob"]],
                                   text=[f"{x:.0f}%" for x in ev["aprob"]], textposition="outside"))
            fig.update_yaxes(range=[80, 105], ticksuffix="%")
            st.plotly_chart(light(fig, 300, "Tasa de aprobación mensual"), use_container_width=True)

        alertas = pf[pf["estado_calidad"] != "Aprobado"].sort_values("fecha", ascending=False)
        if len(alertas):
            st.markdown(f"<p style='font-size:13px;font-weight:800;color:{PURPLE};margin:14px 0 6px'>"
                        f"🚨 Lotes con hallazgo — trazabilidad completa</p>", unsafe_allow_html=True)
            vista = alertas[["lote_id", "fecha", "producto", "linea", "turno",
                             "unidades_producidas", "gluten_ppm", "estado_calidad", "costo_lote_cop"]].copy()
            vista["fecha"] = vista["fecha"].dt.strftime("%Y-%m-%d")
            vista["costo_lote_cop"] = vista["costo_lote_cop"].apply(cop)
            vista.columns = ["Lote", "Fecha", "Producto", "Línea", "Turno", "Unidades",
                             "Gluten ppm", "Estado", "Costo del lote"]
            st.dataframe(vista, hide_index=True, use_container_width=True)
        else:
            st.success("Ningún lote con hallazgo de calidad en el período seleccionado.")

    with t2:
        c5, c6 = st.columns(2, gap="medium")
        with c5:
            linea = pf.groupby("linea").agg(merma=("merma_pct", "mean"),
                                            cumpl=("cumplimiento_plan_pct", "mean"),
                                            lotes=("lote_id", "count")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=linea["linea"], y=linea["merma"], name="Merma %",
                                 marker_color=[BAD if x > 3 else GOOD for x in linea["merma"]],
                                 text=[f"{x:.1f}%" for x in linea["merma"]], textposition="outside"))
            st.plotly_chart(light(fig, 320, "Merma por línea de producción"), use_container_width=True)
        with c6:
            turno = pf.groupby("turno").agg(merma=("merma_pct", "mean"),
                                            cumpl=("cumplimiento_plan_pct", "mean")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=turno["turno"], y=turno["cumpl"], name="Cumplimiento del plan %",
                                 marker_color=PURPLE,
                                 text=[f"{x:.1f}%" for x in turno["cumpl"]], textposition="outside"))
            fig.update_yaxes(range=[90, 100], ticksuffix="%")
            st.plotly_chart(light(fig, 320, "Cumplimiento del plan por turno"), use_container_width=True)

        c7, c8 = st.columns([1.4, 1], gap="medium")
        with c7:
            ev2 = pf.groupby("mes").agg(planeadas=("unidades_planeadas", "sum"),
                                        producidas=("unidades_producidas", "sum")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=ev2["mes"], y=ev2["planeadas"], name="Plan", marker_color=LAVENDER_LT))
            fig.add_trace(go.Bar(x=ev2["mes"], y=ev2["producidas"], name="Producido", marker_color=PURPLE))
            fig.update_layout(barmode="overlay")
            st.plotly_chart(light(fig, 320, "Plan vs. producción real (unidades)"), use_container_width=True)
        with c8:
            merma_sku = pf.groupby("producto")["merma_pct"].mean().nlargest(8).sort_values()
            fig = go.Figure(go.Bar(x=merma_sku.values, y=merma_sku.index, orientation="h",
                                   marker_color=[BAD if x > 3.5 else WARN for x in merma_sku.values],
                                   text=[f"{x:.1f}%" for x in merma_sku.values], textposition="outside"))
            fig.update_xaxes(range=[0, merma_sku.max() * 1.35])
            st.plotly_chart(light(fig, 320, "Referencias con más merma"), use_container_width=True)

        peor_linea = linea.loc[linea["merma"].idxmax()]
        st.markdown(panel("Oportunidad en planta", f"""
        · La línea con más merma es <b>{peor_linea['linea']}</b> ({peor_linea['merma']:.1f}%).
          Bajarla al promedio de la planta liberaría cerca de
          <b>{cop(pf['costo_lote_cop'].sum() * (peor_linea['merma'] - pf['merma_pct'].mean()) / 100, 1)}</b>
          en el período.<br>
        · El cumplimiento del plan va en <b>{cumplimiento:.1f}%</b>: cada punto que falta se traduce
          en faltantes para las cadenas y en fill rate más bajo.
        """, "⚙️"), unsafe_allow_html=True)

    with t3:
        criticos = inv[inv["estado"] == "Crítico"]
        sobre = inv[inv["estado"] == "Sobre-stock"]
        k2 = st.columns(4, gap="small")
        k2[0].markdown(kpi("Valor del inventario", cop(inv["valor_inventario_cop"].sum(), 1),
                           f"{inv['cedi'].nunique()} bodegas", True, "📦"), unsafe_allow_html=True)
        k2[1].markdown(kpi("Referencias críticas", str(len(criticos)), "Menos de 12 días de cobertura",
                           len(criticos) == 0, "🚨"), unsafe_allow_html=True)
        k2[2].markdown(kpi("Sobre-stock", str(len(sobre)), "Más de 75 días de cobertura",
                           len(sobre) < 10, "🐌", "Capital de trabajo dormido."), unsafe_allow_html=True)
        k2[3].markdown(kpi("Cobertura promedio", f"{inv['dias_cobertura'].mean():.0f} días",
                           "Objetivo: 30–45 días", 25 <= inv["dias_cobertura"].mean() <= 60, "📅"),
                       unsafe_allow_html=True)

        c9, c10 = st.columns(2, gap="medium")
        with c9:
            porc = inv.groupby("cedi")["valor_inventario_cop"].sum().sort_values()
            fig = go.Figure(go.Bar(x=porc.values, y=porc.index, orientation="h", marker_color=PURPLE,
                                   customdata=[cop(x, 1) for x in porc.values],
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 300, "Inventario por bodega"), use_container_width=True)
        with c10:
            est = inv["estado"].value_counts().reindex(["Crítico", "Bajo", "Normal", "Sobre-stock"]).fillna(0)
            fig = go.Figure(go.Bar(x=est.index, y=est.values,
                                   marker_color=[BAD, WARN, GOOD, INFO],
                                   text=[int(x) for x in est.values], textposition="outside"))
            st.plotly_chart(light(fig, 300, "Referencias por estado de inventario"), use_container_width=True)

        if len(criticos):
            st.markdown(f"<p style='font-size:13px;font-weight:800;color:{PURPLE};margin:12px 0 6px'>"
                        f"🚨 Reponer ya</p>", unsafe_allow_html=True)
            vista = criticos.sort_values("dias_cobertura")[
                ["producto", "cedi", "stock_unidades", "venta_diaria_prom", "dias_cobertura"]].copy()
            vista.columns = ["Producto", "Bodega", "Stock", "Venta diaria", "Días de cobertura"]
            st.dataframe(vista, hide_index=True, use_container_width=True)

        st.markdown(f"<p style='font-size:13px;font-weight:800;color:{PURPLE};margin:16px 0 6px'>"
                    f"🌎 Proveedores de insumos clave</p>", unsafe_allow_html=True)
        c11, c12 = st.columns([1.2, 1], gap="medium")
        with c11:
            o = prov.sort_values("score_general")
            fig = go.Figure(go.Bar(x=o["score_general"], y=o["proveedor"], orientation="h",
                                   marker_color=[GOOD if x >= 8.5 else WARN for x in o["score_general"]],
                                   text=[f"{x:.1f}" for x in o["score_general"]], textposition="outside"))
            fig.update_xaxes(range=[0, 11])
            st.plotly_chart(light(fig, 320, "Calificación general de proveedores"),
                            use_container_width=True)
        with c12:
            vista = prov[["proveedor", "pais", "especialidad", "lead_time_dias", "moneda"]].sort_values(
                "lead_time_dias", ascending=False)
            vista.columns = ["Proveedor", "País", "Insumo", "Lead time (días)", "Moneda"]
            st.dataframe(vista, hide_index=True, use_container_width=True, height=320)
        st.caption("Los insumos importados (avena certificada, almendra, pistacho) tienen lead times largos "
                   "y exposición a tasa de cambio: son el cuello de botella típico para responder a un pico de demanda.")

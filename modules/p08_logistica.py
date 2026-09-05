import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

HOY = pd.Timestamp("2026-08-31")


@st.cache_data
def load():
    d = leer_csv("despachos.csv")
    for c in ("fecha_pedido", "fecha_prometida", "fecha_entrega"):
        d[c] = pd.to_datetime(d[c], errors="coerce")
    d["mes"] = d["fecha_pedido"].dt.strftime("%Y-%m")
    return d


def render():
    d = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Logística & Cumplimiento",
        "Dos operaciones distintas en un solo tablero: entregar completo y a tiempo a las cadenas, "
        "y que el pedido del cliente llegue rápido a su casa",
        "personaje_6.png"), unsafe_allow_html=True)

    meses = sorted(d["mes"].dropna().unique())
    f1, f2 = st.columns([1.4, 1])
    with f1:
        rango = st.select_slider("Rango de meses", options=meses,
                                 value=(meses[max(0, len(meses)-6)], meses[-1]), key="lg_rango")
    with f2:
        pais = st.multiselect("Países", sorted(d["pais"].unique()),
                              default=sorted(d["pais"].unique()), key="lg_pais")

    df = d[(d["mes"] >= rango[0]) & (d["mes"] <= rango[1])]
    if pais:
        df = df[df["pais"].isin(pais)]
    if df.empty:
        st.warning("No hay despachos con los filtros seleccionados.")
        return

    b2b = df[df["tipo_canal"] != "D2C"]
    b2c = df[df["tipo_canal"] == "D2C"]
    b2b_ent = b2b[b2b["estado"] == "Entregado"]
    b2c_ent = b2c[b2c["estado"] == "Entregado"]

    otif = b2b_ent["otif"].mean() * 100 if len(b2b_ent) else 0
    fill = b2b_ent["fill_rate"].mean() * 100 if len(b2b_ent) else 0
    otd_b2c = b2c_ent["entregado_a_tiempo"].mean() * 100 if len(b2c_ent) else 0
    dias_b2c = b2c_ent["dias_transito"].mean() if len(b2c_ent) else 0
    costo = df["costo_logistico_cop"].sum()
    pct_costo = costo / df["valor_cop"].sum() * 100 if df["valor_cop"].sum() else 0
    en_transito = int((df["estado"] == "En tránsito").sum())

    k = st.columns(6, gap="small")
    k[0].markdown(kpi("OTIF a cadenas", pct(otif), "Meta: 95%", otif >= 95, "✅",
                      "Completo y a tiempo: lo que miden Éxito y Carulla."), unsafe_allow_html=True)
    k[1].markdown(kpi("Fill rate", pct(fill), "% de lo pedido que se despacha", fill >= 97, "📦"),
                  unsafe_allow_html=True)
    k[2].markdown(kpi("Entregas a tiempo web", pct(otd_b2c), "Pedidos de consumidor", otd_b2c >= 92,
                      "🏠"), unsafe_allow_html=True)
    k[3].markdown(kpi("Días de entrega web", f"{dias_b2c:.1f}", "Promedio puerta a puerta",
                      dias_b2c <= 4, "⏱️"), unsafe_allow_html=True)
    k[4].markdown(kpi("Costo logístico", cop(costo, 1), f"{pct_costo:.1f}% de la venta",
                      pct_costo < 5, "💸"), unsafe_allow_html=True)
    k[5].markdown(kpi("En tránsito hoy", f"{en_transito:,}", "Despachos abiertos", True, "🚚"),
                  unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🏬  Cumplimiento a cadenas", "🏠  Entregas al consumidor", "💸  Costo logístico"])

    with t1:
        st.markdown(panel("El indicador que decide si una cadena te da más espacio", """
        Las grandes superficies miden a sus proveedores por <b>OTIF</b> (On Time In Full): entregar
        la orden completa y en la fecha pactada. Un OTIF bajo genera multas, órdenes canceladas y
        pérdida de espacio en góndola. El <b>fill rate</b> muestra si el problema es de producción
        (no había producto) y el cumplimiento de fecha, si es de transporte.
        """, "📏"), unsafe_allow_html=True)

        c1, c2 = st.columns([1.4, 1], gap="medium")
        with c1:
            ev = b2b_ent.groupby("mes").agg(otif=("otif", "mean"), fill=("fill_rate", "mean"),
                                            a_tiempo=("entregado_a_tiempo", "mean")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ev["mes"], y=ev["otif"] * 100, name="OTIF",
                                     mode="lines+markers", line=dict(color=PURPLE, width=3)))
            fig.add_trace(go.Scatter(x=ev["mes"], y=ev["fill"] * 100, name="Fill rate",
                                     mode="lines+markers", line=dict(color=PINK, width=2)))
            fig.add_trace(go.Scatter(x=ev["mes"], y=ev["a_tiempo"] * 100, name="A tiempo",
                                     mode="lines+markers", line=dict(color=LAVENDER, width=2, dash="dot")))
            fig.add_hline(y=95, line_dash="dash", line_color=GOOD,
                          annotation_text="Meta 95%", annotation_font_color=GOOD)
            fig.update_yaxes(ticksuffix="%")
            st.plotly_chart(light(fig, 350, "Cumplimiento mes a mes"), use_container_width=True)
        with c2:
            por_canal = b2b_ent.groupby("canal").agg(otif=("otif", "mean"),
                                                     ordenes=("despacho_id", "count")).reset_index()
            por_canal["otif"] = por_canal["otif"] * 100
            por_canal = por_canal.sort_values("otif")
            fig = go.Figure(go.Bar(x=por_canal["otif"], y=por_canal["canal"], orientation="h",
                                   marker_color=[GOOD if x >= 95 else WARN if x >= 88 else BAD
                                                 for x in por_canal["otif"]],
                                   text=[f"{x:.0f}%" for x in por_canal["otif"]], textposition="outside"))
            fig.update_xaxes(range=[0, 115])
            st.plotly_chart(light(fig, 350, "OTIF por cliente"), use_container_width=True)

        incompletas = b2b_ent[b2b_ent["fill_rate"] < 0.98]
        tarde = b2b_ent[b2b_ent["entregado_a_tiempo"] == False]
        c3, c4 = st.columns(2, gap="medium")
        with c3:
            causas = pd.Series({
                "Incompletas (faltó producto)": len(incompletas),
                "Tarde (llegó fuera de fecha)": len(tarde),
                "Completas y a tiempo": int(b2b_ent["otif"].sum()),
            })
            fig = go.Figure(go.Bar(x=causas.index, y=causas.values,
                                   marker_color=[WARN, BAD, GOOD],
                                   text=causas.values, textposition="outside"))
            st.plotly_chart(light(fig, 300, "Por qué se cae el OTIF"), use_container_width=True)
        with c4:
            valor_incompleto = incompletas["valor_cop"].sum() * (1 - incompletas["fill_rate"].mean()) \
                if len(incompletas) else 0
            st.markdown(panel("Traducción a plata", f"""
            · <b>{len(incompletas)}</b> órdenes salieron incompletas en el período. Lo que no se despachó
              vale aproximadamente <b>{cop(valor_incompleto, 1)}</b> de venta que la cadena pidió y
              Paranice no pudo entregar.<br>
            · <b>{len(tarde)}</b> llegaron fuera de fecha. En cadenas grandes esto suele venir con multa
              o con rechazo en el muelle.<br>
            · Subir el OTIF de <b>{otif:.0f}%</b> a 95% es la palanca más directa para pedir más espacio
              en góndola en la próxima negociación.
            """, "💸"), unsafe_allow_html=True)

    with t2:
        c5, c6 = st.columns([1.4, 1], gap="medium")
        with c5:
            ev2 = b2c_ent.groupby("mes").agg(dias=("dias_transito", "mean"),
                                             a_tiempo=("entregado_a_tiempo", "mean")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=ev2["mes"], y=ev2["dias"], name="Días de entrega",
                                 marker_color=LAVENDER))
            fig.add_trace(go.Scatter(x=ev2["mes"], y=ev2["a_tiempo"] * 100, name="% a tiempo",
                                     mode="lines+markers", line=dict(color=PURPLE, width=3), yaxis="y2"))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, ticksuffix="%"))
            st.plotly_chart(light(fig, 340, "Tiempo de entrega y cumplimiento al consumidor"),
                            use_container_width=True)
        with c6:
            transp = b2c_ent.groupby("transportadora").agg(
                a_tiempo=("entregado_a_tiempo", "mean"), envios=("despacho_id", "count")).reset_index()
            transp["a_tiempo"] = transp["a_tiempo"] * 100
            transp = transp[transp["envios"] > 20].sort_values("a_tiempo")
            fig = go.Figure(go.Bar(x=transp["a_tiempo"], y=transp["transportadora"], orientation="h",
                                   marker_color=[GOOD if x >= 92 else WARN for x in transp["a_tiempo"]],
                                   text=[f"{x:.0f}%" for x in transp["a_tiempo"]], textposition="outside"))
            fig.update_xaxes(range=[0, 115])
            st.plotly_chart(light(fig, 340, "Cumplimiento por transportadora"), use_container_width=True)

        c7, c8 = st.columns(2, gap="medium")
        with c7:
            ciu = b2c_ent.groupby("ciudad").agg(dias=("dias_transito", "mean"),
                                                envios=("despacho_id", "count")).reset_index()
            ciu = ciu[ciu["envios"] > 30].nlargest(10, "dias").sort_values("dias")
            fig = go.Figure(go.Bar(x=ciu["dias"], y=ciu["ciudad"], orientation="h",
                                   marker_color=[BAD if x > 5 else WARN if x > 3.5 else GOOD
                                                 for x in ciu["dias"]],
                                   text=[f"{x:.1f} d" for x in ciu["dias"]], textposition="outside"))
            fig.update_xaxes(range=[0, ciu["dias"].max() * 1.3 if len(ciu) else 8])
            st.plotly_chart(light(fig, 300, "Ciudades donde más se demora la entrega"),
                            use_container_width=True)
        with c8:
            atrasados = df[(df["estado"] == "En tránsito") & (df["fecha_prometida"] < HOY)]
            st.markdown(f"<p style='font-size:13px;font-weight:800;color:{PURPLE};margin:0 0 6px'>"
                        f"⚠️ Pedidos que ya pasaron la fecha prometida ({len(atrasados)})</p>",
                        unsafe_allow_html=True)
            if len(atrasados):
                vista = atrasados.nsmallest(12, "fecha_prometida")[
                    ["documento_id", "canal", "ciudad", "transportadora", "fecha_prometida", "valor_cop"]].copy()
                vista["fecha_prometida"] = vista["fecha_prometida"].dt.strftime("%Y-%m-%d")
                vista["valor_cop"] = vista["valor_cop"].apply(cop)
                vista.columns = ["Documento", "Canal", "Ciudad", "Transportadora", "Prometida", "Valor"]
                st.dataframe(vista, hide_index=True, use_container_width=True, height=280)
            else:
                st.success("No hay pedidos vencidos en tránsito.")

    with t3:
        c9, c10 = st.columns([1.4, 1], gap="medium")
        with c9:
            ev3 = df.groupby("mes").agg(costo=("costo_logistico_cop", "sum"),
                                        venta=("valor_cop", "sum")).reset_index()
            ev3["pct"] = ev3["costo"] / ev3["venta"] * 100
            fig = go.Figure()
            fig.add_trace(go.Bar(x=ev3["mes"], y=ev3["costo"], name="Costo logístico",
                                 marker_color=LAVENDER))
            fig.add_trace(go.Scatter(x=ev3["mes"], y=ev3["pct"], name="% sobre la venta",
                                     mode="lines+markers", line=dict(color=CORAL, width=3), yaxis="y2"))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, ticksuffix="%"))
            st.plotly_chart(light(fig, 340, "Cuánto cuesta mover el producto"), use_container_width=True)
        with c10:
            por_tipo = df.groupby("tipo_canal").agg(costo=("costo_logistico_cop", "sum"),
                                                    venta=("valor_cop", "sum")).reset_index()
            por_tipo["pct"] = por_tipo["costo"] / por_tipo["venta"] * 100
            por_tipo = por_tipo.sort_values("pct")
            fig = go.Figure(go.Bar(x=por_tipo["pct"], y=por_tipo["tipo_canal"], orientation="h",
                                   marker_color=[GOOD if x < 4 else WARN if x < 8 else BAD
                                                 for x in por_tipo["pct"]],
                                   text=[f"{x:.1f}%" for x in por_tipo["pct"]], textposition="outside"))
            fig.update_xaxes(range=[0, por_tipo["pct"].max() * 1.35 if len(por_tipo) else 10])
            st.plotly_chart(light(fig, 340, "Costo logístico sobre venta, por tipo de canal"),
                            use_container_width=True)

        caro = por_tipo.iloc[-1] if len(por_tipo) else None
        if caro is not None:
            st.markdown(panel("Dónde duele el costo de entregar", f"""
            · <b>{caro['tipo_canal']}</b> es el canal donde entregar cuesta más caro
              ({caro['pct']:.1f}% de la venta). En el canal propio ese costo se puede
              compensar subiendo el ticket promedio: cada pedido que sube de
              {cop(120000)} a {cop(150000)} diluye el mismo flete.<br>
            · Hoy el pedido mínimo del sitio es de $50.000. Un umbral de envío gratis un poco por
              encima del ticket promedio es la palanca más rápida para mejorar este número.
            """, "🚚"), unsafe_allow_html=True)

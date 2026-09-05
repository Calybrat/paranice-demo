import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *
from utils import datos

PROPIOS = ["Email (Omnisend)", "WhatsApp", "Orgánico/SEO"]


def load():
    return datos.marketing(), datos.contenido()


def render():
    mkt, cont = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Marketing & Contenido",
        "Qué tanto rinde cada peso de pauta, cuánto aportan los canales propios "
        "(Omnisend, WhatsApp, SEO) y cómo se comporta el blog de recetas",
        "personaje_3.png"), unsafe_allow_html=True)

    meses = sorted(mkt["mes"].unique())
    f1, f2 = st.columns([1.4, 1])
    with f1:
        rango = st.select_slider("Rango de meses", options=meses,
                                 value=(meses[max(0, len(meses)-6)], meses[-1]), key="mk_rango")
    with f2:
        canales = st.multiselect("Canales", sorted(mkt["canal"].unique()),
                                 default=sorted(mkt["canal"].unique()), key="mk_can")

    mf = mkt[(mkt["mes"] >= rango[0]) & (mkt["mes"] <= rango[1])]
    if canales:
        mf = mf[mf["canal"].isin(canales)]
    if mf.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        return

    inversion = mf["inversion_cop"].sum()
    ingresos = mf["ingresos_cop"].sum()
    roas = ingresos / inversion if inversion else 0
    nuevos = mf["clientes_nuevos"].sum()
    cac = inversion / nuevos if nuevos else 0
    ing_propios = mf[mf["canal"].isin(PROPIOS)]["ingresos_cop"].sum()
    pct_propios = ing_propios / ingresos * 100 if ingresos else 0
    clics, imp = mf["clics"].sum(), mf["impresiones"].sum()
    ctr = clics / imp * 100 if imp else 0

    k = st.columns(6, gap="small")
    k[0].markdown(kpi("Inversión en pauta", cop(inversion, 1), f"{rango[0]} → {rango[1]}", True, "💵"),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("Ingresos atribuidos", cop(ingresos, 1), "Venta del canal propio", True, "📈"),
                  unsafe_allow_html=True)
    k[2].markdown(kpi("ROAS", f"{roas:.1f}x", "Meta: 3x", roas >= 3, "🎯",
                      "Pesos vendidos por cada peso invertido."), unsafe_allow_html=True)
    k[3].markdown(kpi("CAC", cop(cac), f"{nuevos:,} clientes nuevos", True, "🧲"), unsafe_allow_html=True)
    k[4].markdown(kpi("Peso de canales propios", pct(pct_propios), "Email · WhatsApp · SEO",
                      pct_propios > 25, "💜",
                      "Venta que no depende de pagar pauta."), unsafe_allow_html=True)
    k[5].markdown(kpi("CTR", pct(ctr, 2), f"{clics:,} clics", ctr > 1, "👆"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["💰  Rendimiento por canal", "📈  Evolución", "📝  Blog y contenido"])

    with t1:
        agg = mf.groupby("canal").agg(inversion=("inversion_cop", "sum"),
                                      ingresos=("ingresos_cop", "sum"),
                                      nuevos=("clientes_nuevos", "sum"),
                                      pedidos=("pedidos", "sum")).reset_index()
        agg["roas"] = agg["ingresos"] / agg["inversion"].replace(0, np.nan)
        agg["cac"] = agg["inversion"] / agg["nuevos"].replace(0, np.nan)

        c1, c2 = st.columns([1.35, 1], gap="medium")
        with c1:
            ordenado = agg.sort_values("ingresos")
            fig = go.Figure()
            fig.add_trace(go.Bar(y=ordenado["canal"], x=ordenado["inversion"], orientation="h",
                                 name="Inversión", marker_color=LAVENDER_LT))
            fig.add_trace(go.Bar(y=ordenado["canal"], x=ordenado["ingresos"], orientation="h",
                                 name="Ingresos atribuidos", marker_color=PURPLE, opacity=0.9))
            fig.update_layout(barmode="overlay")
            st.plotly_chart(light(fig, 360, "Inversión vs. ingresos por canal"), use_container_width=True)
        with c2:
            con_roas = agg.dropna(subset=["roas"]).sort_values("roas")
            fig = go.Figure(go.Bar(x=con_roas["roas"], y=con_roas["canal"], orientation="h",
                                   marker_color=[GOOD if x >= 3 else WARN if x >= 2 else BAD
                                                 for x in con_roas["roas"]],
                                   text=[f"{x:.1f}x" for x in con_roas["roas"]], textposition="outside"))
            fig.update_xaxes(range=[0, con_roas["roas"].max() * 1.28 if len(con_roas) else 5])
            st.plotly_chart(light(fig, 360, "ROAS por canal"), use_container_width=True)

        if len(agg.dropna(subset=["roas"])):
            mejor = agg.loc[agg["roas"].idxmax()]
            peor = agg.loc[agg["roas"].idxmin()]
            st.markdown(panel("Dónde mover el presupuesto", f"""
            · <b>{mejor['canal']}</b> devuelve {mejor['roas']:.1f}x por cada peso invertido — es el canal
              más eficiente y hoy solo recibe {mejor['inversion']/inversion*100:.0f}% del presupuesto.<br>
            · <b>{peor['canal']}</b> está en {peor['roas']:.1f}x. Si no mejora el creativo o la segmentación,
              cada peso ahí rinde menos que en cualquier otro lado.<br>
            · Los canales propios (Omnisend, WhatsApp, SEO) ya generan <b>{pct(pct_propios)}</b> de la venta
              directa: son el mejor seguro contra subidas de costo en Meta y TikTok.
            """, "🎯"), unsafe_allow_html=True)

        vista = agg.copy().sort_values("ingresos", ascending=False)
        vista["inversion"] = vista["inversion"].apply(lambda x: cop(x, 1))
        vista["ingresos"] = vista["ingresos"].apply(lambda x: cop(x, 1))
        vista["cac"] = vista["cac"].apply(lambda x: cop(x) if pd.notna(x) else "—")
        vista["roas"] = vista["roas"].apply(lambda x: f"{x:.2f}x" if pd.notna(x) else "orgánico")
        vista.columns = ["Canal", "Inversión", "Ingresos", "Clientes nuevos", "Pedidos", "ROAS", "CAC"]
        st.dataframe(vista, hide_index=True, use_container_width=True)

    with t2:
        c3, c4 = st.columns([1.5, 1], gap="medium")
        with c3:
            piv = mf[mf["inversion_cop"] > 0].groupby(["mes", "canal"])["inversion_cop"].sum().reset_index()
            fig = go.Figure()
            for i, cn in enumerate(sorted(piv["canal"].unique())):
                sub = piv[piv["canal"] == cn]
                fig.add_trace(go.Scatter(x=sub["mes"], y=sub["inversion_cop"], name=cn, mode="lines",
                                         stackgroup="one", line=dict(width=0.5, color=PALETTE[i % len(PALETTE)])))
            st.plotly_chart(light(fig, 350, "Inversión mensual por canal"), use_container_width=True)
        with c4:
            ev = mf.groupby("mes").agg(inv=("inversion_cop", "sum"), ing=("ingresos_cop", "sum"),
                                       nuevos=("clientes_nuevos", "sum")).reset_index()
            ev["roas"] = ev["ing"] / ev["inv"].replace(0, np.nan)
            ev["cac"] = ev["inv"] / ev["nuevos"].replace(0, np.nan)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ev["mes"], y=ev["roas"], name="ROAS", mode="lines+markers",
                                     line=dict(color=PURPLE, width=3)))
            fig.add_hline(y=3, line_dash="dash", line_color=GOOD,
                          annotation_text="Meta 3x", annotation_font_color=GOOD)
            st.plotly_chart(light(fig, 350, "ROAS mes a mes"), use_container_width=True)

        c5, c6 = st.columns(2, gap="medium")
        with c5:
            fig = go.Figure(go.Scatter(x=ev["mes"], y=ev["cac"], mode="lines+markers",
                                       line=dict(color=CORAL, width=3), fill="tozeroy",
                                       fillcolor="rgba(239,125,87,.12)",
                                       customdata=[cop(x) if pd.notna(x) else "—" for x in ev["cac"]],
                                       hovertemplate="<b>%{x}</b><br>CAC %{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 300, "Costo de adquirir un cliente (CAC)"), use_container_width=True)
        with c6:
            fig = go.Figure(go.Bar(x=ev["mes"], y=ev["nuevos"], marker_color=PINK,
                                   text=ev["nuevos"], textposition="outside"))
            st.plotly_chart(light(fig, 300, "Clientes nuevos por mes"), use_container_width=True)

    with t3:
        st.markdown(panel("El blog es un activo, no un adorno", """
        Paranice publica recetas en <i>Mundo Paranice</i> (Baked Goods, Brunch, Desserts, Bebidas y
        Helados, Snacks y The Paranice Lab). Ese contenido atrae tráfico que no se paga y que después
        compra. Aquí se ve qué secciones traen visitas y cuáles terminan en pedido.
        """, "📝"), unsafe_allow_html=True)

        cf = cont[(cont["mes"] >= rango[0]) & (cont["mes"] <= rango[1])]
        agg_c = cf.groupby("seccion").agg(visitas=("visitas", "sum"),
                                          publicaciones=("publicaciones", "sum"),
                                          pedidos=("pedidos_asistidos", "sum"),
                                          tiempo=("tiempo_medio_seg", "mean")).reset_index()
        agg_c["conversion_pct"] = (agg_c["pedidos"] / agg_c["visitas"] * 100).round(2)

        c7, c8 = st.columns(2, gap="medium")
        with c7:
            o = agg_c.sort_values("visitas")
            fig = go.Figure(go.Bar(x=o["visitas"], y=o["seccion"], orientation="h", marker_color=PURPLE,
                                   text=[f"{int(x):,}" for x in o["visitas"]], textposition="outside"))
            fig.update_xaxes(range=[0, o["visitas"].max() * 1.25])
            st.plotly_chart(light(fig, 320, "Visitas por sección del blog"), use_container_width=True)
        with c8:
            o2 = agg_c.sort_values("conversion_pct")
            fig = go.Figure(go.Bar(x=o2["conversion_pct"], y=o2["seccion"], orientation="h",
                                   marker_color=PINK,
                                   text=[f"{x:.2f}%" for x in o2["conversion_pct"]], textposition="outside"))
            fig.update_xaxes(range=[0, o2["conversion_pct"].max() * 1.3])
            st.plotly_chart(light(fig, 320, "Qué sección termina en pedido"), use_container_width=True)

        if len(agg_c):
            mejor_c = agg_c.loc[agg_c["conversion_pct"].idxmax()]
            mas_visitas = agg_c.loc[agg_c["visitas"].idxmax()]
            st.markdown(panel("Lectura de contenido", f"""
            · <b>{mas_visitas['seccion']}</b> es la sección que más tráfico trae
              ({int(mas_visitas['visitas']):,} visitas en el período).<br>
            · <b>{mejor_c['seccion']}</b> es la que mejor convierte ({mejor_c['conversion_pct']:.2f}%):
              publicar más ahí rinde más que publicar en la que solo trae visitas.<br>
            · El contenido asistió <b>{int(agg_c['pedidos'].sum()):,} pedidos</b> en el período,
              sin costo de pauta.
            """, "💡"), unsafe_allow_html=True)

        ev_c = cf.groupby("mes").agg(visitas=("visitas", "sum"), pedidos=("pedidos_asistidos", "sum")).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ev_c["mes"], y=ev_c["visitas"], name="Visitas", marker_color=LAVENDER))
        fig.add_trace(go.Scatter(x=ev_c["mes"], y=ev_c["pedidos"], name="Pedidos asistidos",
                                 mode="lines+markers", line=dict(color=PURPLE, width=3), yaxis="y2"))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False))
        st.plotly_chart(light(fig, 300, "Tráfico del blog y pedidos que asiste"), use_container_width=True)

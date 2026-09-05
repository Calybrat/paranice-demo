import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *
from utils import datos


def load():
    return datos.productos(), datos.precios_canal(), datos.ventas()


def render():
    prods, precios, v = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Portafolio & Precios",
        "Las 28 referencias del catálogo, qué margen deja cada una y cuánto se separa el precio "
        "entre la tienda propia y los demás canales",
        "personaje_8.png"), unsafe_allow_html=True)

    v26 = v[v["mes"] >= "2026-01"]

    n_sku = len(prods)
    gf = prods["sin_gluten"].mean() * 100
    vegan = prods["vegano"].mean() * 100
    _agg_cat = v26.groupby("categoria", observed=True)[["margen_cop", "venta_cop"]].sum()
    margen_cat = _agg_cat["margen_cop"] / _agg_cat["venta_cop"] * 100
    top_sku = v26.groupby("producto")["venta_cop"].sum().idxmax() if len(v26) else "—"
    brecha_max = precios.groupby("canal")["brecha_vs_propio_pct"].mean().max()

    k = st.columns(5, gap="small")
    k[0].markdown(kpi("Referencias activas", str(n_sku), "6 categorías", True, "🥣"), unsafe_allow_html=True)
    k[1].markdown(kpi("Catálogo sin gluten", pct(gf), "Del total de referencias", gf > 75, "🌾",
                      "El claim central de la marca."), unsafe_allow_html=True)
    k[2].markdown(kpi("Catálogo vegano", pct(vegan), "Del total de referencias", vegan > 60, "🌱"),
                  unsafe_allow_html=True)
    k[3].markdown(kpi("Más vendido 2026", top_sku, "Por facturación", True, "⭐"), unsafe_allow_html=True)
    k[4].markdown(kpi("Brecha de precio máx.", pct(brecha_max), "Canal más caro vs. tienda propia",
                      brecha_max < 25, "⚠️", "Diferencia de PVP que ve el consumidor."),
                  unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🏷️  Arquitectura de precios", "💎  Rentabilidad por referencia", "📋  Catálogo"])

    with t1:
        st.markdown(panel("El punto ciego más caro de una marca omnicanal", """
        El mismo producto no cuesta lo mismo en paranice.co, en Éxito o en Fithub. Una brecha sana
        protege al retail; una brecha grande hace que el consumidor sienta que en unos lados lo
        “estafan” y presiona a las cadenas a pedir descuentos. Aquí se ve el PVP que ve el consumidor
        en cada canal, cuánto factura Paranice y qué margen le queda después de la comisión del canal.
        """, "🧭"), unsafe_allow_html=True)

        sku_sel = st.selectbox("Elige una referencia", sorted(precios["nombre"].unique()), key="pf_sku")
        det = precios[precios["nombre"] == sku_sel].sort_values("pvp_consumidor_cop")

        c1, c2 = st.columns([1.4, 1], gap="medium")
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=det["canal"], y=det["pvp_consumidor_cop"], name="PVP al consumidor",
                                 marker_color=LAVENDER_LT,
                                 text=[cop(x) for x in det["pvp_consumidor_cop"]], textposition="outside"))
            fig.add_trace(go.Bar(x=det["canal"], y=det["precio_factura_paranice_cop"],
                                 name="Lo que factura Paranice", marker_color=PURPLE,
                                 text=[cop(x) for x in det["precio_factura_paranice_cop"]],
                                 textposition="inside"))
            fig.add_trace(go.Scatter(x=det["canal"], y=det["costo_unitario_cop"], name="Costo unitario",
                                     mode="lines+markers", line=dict(color=BAD, width=2, dash="dot")))
            fig.update_layout(barmode="overlay")
            st.plotly_chart(light(fig, 380, f"{sku_sel} · precio por canal"), use_container_width=True)
        with c2:
            fig = go.Figure(go.Bar(x=det["margen_paranice_pct"], y=det["canal"], orientation="h",
                                   marker_color=[GOOD if x >= 55 else WARN if x >= 45 else BAD
                                                 for x in det["margen_paranice_pct"]],
                                   text=[f"{x:.0f}%" for x in det["margen_paranice_pct"]],
                                   textposition="outside"))
            fig.update_xaxes(range=[0, 100])
            st.plotly_chart(light(fig, 380, "Margen que le queda a Paranice"), use_container_width=True)

        mejor = det.loc[det["margen_paranice_pct"].idxmax()]
        peor = det.loc[det["margen_paranice_pct"].idxmin()]
        caro = det.loc[det["pvp_consumidor_cop"].idxmax()]
        st.markdown(panel("Lectura de esta referencia", f"""
        · El consumidor paga <b>{cop(caro['pvp_consumidor_cop'])}</b> en {caro['canal']} y
          <b>{cop(det[det['canal'] == 'E-commerce propio']['pvp_consumidor_cop'].iloc[0]) if 'E-commerce propio' in det['canal'].values else '—'}</b>
          en la tienda propia: una brecha de <b>{caro['brecha_vs_propio_pct']:.0f}%</b>.<br>
        · Paranice gana <b>{mejor['margen_paranice_pct']:.0f}%</b> vendiendo por {mejor['canal']}
          y <b>{peor['margen_paranice_pct']:.0f}%</b> por {peor['canal']}.<br>
        · Cada unidad que se mueve del canal propio al de menor margen cuesta cerca de
          <b>{cop(mejor['precio_factura_paranice_cop'] - peor['precio_factura_paranice_cop'])}</b> de ingreso.
        """, "💡"), unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        mapa = precios.pivot_table(index="nombre", columns="canal", values="pvp_consumidor_cop", aggfunc="max")
        st.markdown(f"<p style='font-size:13px;font-weight:800;color:{PURPLE};margin:8px 0'>Mapa de PVP por canal (COP)</p>",
                    unsafe_allow_html=True)
        st.dataframe(mapa.style.format("{:,.0f}"), use_container_width=True, height=340)

    with t2:
        rent = v26.groupby(["producto", "categoria"]).agg(
            ventas=("venta_cop", "sum"), unidades=("unidades", "sum"),
            margen=("margen_cop", "sum")).reset_index()
        rent["margen_pct"] = (rent["margen"] / rent["ventas"] * 100).round(1)
        rent["margen_unidad"] = (rent["margen"] / rent["unidades"]).round()

        c3, c4 = st.columns(2, gap="medium")
        with c3:
            fig = go.Figure()
            for i, cat in enumerate(sorted(rent["categoria"].unique())):
                sub = rent[rent["categoria"] == cat]
                fig.add_trace(go.Scatter(
                    x=sub["unidades"], y=sub["margen_pct"], mode="markers+text", name=cat,
                    text=sub["producto"], textposition="top center", textfont=dict(size=8.5),
                    marker=dict(size=sub["ventas"] / sub["ventas"].max() * 34 + 9,
                                color=PALETTE[i % len(PALETTE)], opacity=0.82,
                                line=dict(width=1, color="white")),
                    hovertemplate="<b>%{text}</b><br>%{x:,.0f} und · margen %{y:.1f}%<extra></extra>"))
            fig.update_xaxes(title="Unidades vendidas 2026")
            fig.update_yaxes(title="Margen %")
            st.plotly_chart(light(fig, 420, "Volumen vs. margen (el tamaño es la facturación)"),
                            use_container_width=True)
        with c4:
            top_m = rent.nlargest(12, "margen").sort_values("margen")
            fig = go.Figure(go.Bar(x=top_m["margen"], y=top_m["producto"], orientation="h",
                                   marker_color=PURPLE,
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in top_m["margen"]]))
            st.plotly_chart(light(fig, 420, "Referencias que más margen aportan (2026)"),
                            use_container_width=True)

        if len(rent):
            estrella = rent.loc[rent["margen"].idxmax()]
            flojo = rent.nsmallest(1, "ventas").iloc[0]
            st.markdown(panel("Dónde está la plata del portafolio", f"""
            · <b>{estrella['producto']}</b> aporta {cop(estrella['margen'], 1)} de margen en 2026,
              con {estrella['margen_pct']:.0f}% sobre venta. Es el producto que hay que proteger de quiebres.<br>
            · <b>{flojo['producto']}</b> es el de menor facturación del período: vale la pena revisar
              si se sostiene por estrategia de portafolio o si está consumiendo espacio y capital de trabajo.<br>
            · El <b>20% de las referencias concentra el
              {rent.nlargest(max(1, int(len(rent) * .2)), 'ventas')['ventas'].sum() / rent['ventas'].sum() * 100:.0f}%</b>
              de la venta: ahí es donde primero hay que garantizar disponibilidad.
            """, "💎"), unsafe_allow_html=True)

        vista = rent.sort_values("ventas", ascending=False).copy()
        vista["ventas"] = vista["ventas"].apply(lambda x: cop(x, 1))
        vista["margen"] = vista["margen"].apply(lambda x: cop(x, 1))
        vista["margen_unidad"] = vista["margen_unidad"].apply(cop)
        vista["unidades"] = vista["unidades"].apply(lambda x: f"{int(x):,}")
        vista.columns = ["Producto", "Categoría", "Ventas 2026", "Unidades", "Margen $",
                         "Margen %", "Margen/unidad"]
        st.dataframe(vista, hide_index=True, use_container_width=True)

    with t3:
        cat = prods.copy()
        for col, etiqueta in [("sin_gluten", "Sin gluten"), ("vegano", "Vegano"),
                              ("sin_azucar", "Sin azúcar añadida"), ("keto", "Keto friendly")]:
            cat[etiqueta] = cat[col].map({1: "Sí", 0: "—"})
        cat["PVP propio"] = cat["pvp_propio_cop"].apply(cop)
        cat["Costo"] = cat["costo_unitario_cop"].apply(cop)
        cat["Margen %"] = cat["margen_bruto_pct"]
        vista = cat[["sku", "nombre", "categoria", "presentacion", "PVP propio", "Costo", "Margen %",
                     "Sin gluten", "Vegano", "Sin azúcar añadida", "Keto friendly", "fecha_lanzamiento"]]
        vista.columns = ["SKU", "Producto", "Categoría", "Presentación", "PVP propio", "Costo",
                         "Margen %", "Sin gluten", "Vegano", "Sin azúcar", "Keto", "Lanzamiento"]
        st.dataframe(vista, hide_index=True, use_container_width=True, height=560)
        st.caption("Catálogo y precios tomados de paranice.co (agosto 2026). Costos y márgenes son estimados de demostración.")

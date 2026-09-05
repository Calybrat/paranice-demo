import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *
from utils import datos


def load():
    return datos.sellout(), datos.puntos_venta(), datos.despachos()


def render():
    so, pdv, desp = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Retail & Sell-Out",
        "Qué tanto rota Paranice en la góndola de Éxito, Carulla, Fithub y tiendas naturistas — "
        "y dónde se está quedando sin producto",
        "personaje_7.png"), unsafe_allow_html=True)

    st.markdown(panel("Por qué importa este tablero", """
        Vender a una cadena (<b>sell-in</b>) no es lo mismo que vender en la góndola (<b>sell-out</b>).
        Si el sell-in crece pero el sell-out no, el inventario se acumula en la cadena y el siguiente
        pedido no llega. Aquí se ven las dos curvas juntas, la rotación por punto de venta y los
        días en que el producto estuvo agotado en el anaquel.
    """, "🧭"), unsafe_allow_html=True)

    meses = sorted(so["mes"].unique())
    f1, f2, f3 = st.columns(3)
    with f1:
        rango = st.select_slider("Rango de meses", options=meses,
                                 value=(meses[max(0, len(meses)-6)], meses[-1]), key="rt_rango")
    with f2:
        cadenas = st.multiselect("Cadenas", sorted(so["cadena"].unique()),
                                 default=sorted(so["cadena"].unique()), key="rt_cad")
    with f3:
        ciudades = st.multiselect("Ciudades", sorted(so["ciudad"].unique()),
                                  default=sorted(so["ciudad"].unique()), key="rt_ciu")

    sf = so[(so["mes"] >= rango[0]) & (so["mes"] <= rango[1])]
    if cadenas:
        sf = sf[sf["cadena"].isin(cadenas)]
    if ciudades:
        sf = sf[sf["ciudad"].isin(ciudades)]

    if sf.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        return

    sell_in = int(sf["unidades_sell_in"].sum())
    sell_out = int(sf["unidades_sell_out"].sum())
    ratio = sell_out / sell_in * 100 if sell_in else 0
    valor_so = sf["valor_sell_out_cop"].sum()
    n_pdv = int(sf.groupby(["cadena", "ciudad"])["pdv_activos"].max().sum())
    rotacion = sf["unidades_sell_out"].sum() / max(n_pdv, 1) / max(len(sf["mes"].unique()), 1)
    dias_quiebre = sf["dias_sin_stock"].mean()
    inv_cadena = int(sf["inventario_cadena_und"].sum())

    retail_desp = desp[(desp["estado"] == "Entregado") & (desp["canal"].isin(sf["cadena"].unique()))]
    fill = retail_desp["fill_rate"].mean() * 100 if len(retail_desp) else 0
    otif = retail_desp["otif"].mean() * 100 if len(retail_desp) else 0

    k = st.columns(6, gap="small")
    k[0].markdown(kpi("Puntos de venta", f"{n_pdv:,}", "Con producto en el período", True, "🏬",
                      "Cobertura real en cadenas."), unsafe_allow_html=True)
    k[1].markdown(kpi("Sell-out", f"{sell_out:,} und", cop(valor_so, 1) + " a PVP", True, "🛍️",
                      "Unidades que el consumidor se llevó."), unsafe_allow_html=True)
    k[2].markdown(kpi("Sell-out / Sell-in", pct(ratio), "Ideal: 90–100%", ratio >= 88, "⚖️",
                      "Si baja mucho, se acumula inventario en la cadena."), unsafe_allow_html=True)
    k[3].markdown(kpi("Rotación", f"{rotacion:.1f} und", "Por PDV por mes", rotacion >= 8, "🔄",
                      "Cuánto vende cada punto al mes."), unsafe_allow_html=True)
    k[4].markdown(kpi("Días sin stock", f"{dias_quiebre:.1f}", "Promedio por referencia/mes",
                      dias_quiebre < 3, "🚫", "Días con la góndola vacía: venta que se pierde."),
                  unsafe_allow_html=True)
    k[5].markdown(kpi("OTIF a cadenas", pct(otif), f"Fill rate {fill:.1f}%", otif >= 90, "✅",
                      "Órdenes entregadas completas y a tiempo."), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["📊  Sell-in vs Sell-out", "🚫  Quiebres y cobertura", "🏆  Desempeño por SKU"])

    with t1:
        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            ev = sf.groupby("mes").agg(sell_in=("unidades_sell_in", "sum"),
                                       sell_out=("unidades_sell_out", "sum")).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=ev["mes"], y=ev["sell_in"], name="Sell-in (a la cadena)",
                                 marker_color=LAVENDER))
            fig.add_trace(go.Scatter(x=ev["mes"], y=ev["sell_out"], name="Sell-out (al consumidor)",
                                     mode="lines+markers", line=dict(color=PURPLE, width=3),
                                     marker=dict(size=7)))
            st.plotly_chart(light(fig, 350, "Sell-in vs. sell-out (unidades)"), use_container_width=True)
        with c2:
            por_cadena = sf.groupby("cadena").agg(
                sell_in=("unidades_sell_in", "sum"), sell_out=("unidades_sell_out", "sum")).reset_index()
            por_cadena["ratio"] = (por_cadena["sell_out"] / por_cadena["sell_in"] * 100).round(1)
            por_cadena = por_cadena.sort_values("ratio")
            fig = go.Figure(go.Bar(x=por_cadena["ratio"], y=por_cadena["cadena"], orientation="h",
                                   marker_color=[GOOD if x >= 88 else WARN for x in por_cadena["ratio"]],
                                   text=[f"{x:.0f}%" for x in por_cadena["ratio"]], textposition="outside"))
            fig.update_xaxes(range=[0, 118])
            st.plotly_chart(light(fig, 350, "Conversión sell-in → sell-out por cadena"),
                            use_container_width=True)

        c3, c4 = st.columns(2, gap="medium")
        with c3:
            val = sf.groupby("cadena")["valor_sell_out_cop"].sum().sort_values()
            fig = go.Figure(go.Bar(x=val.values, y=val.index, orientation="h", marker_color=PURPLE,
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in val.values]))
            st.plotly_chart(light(fig, 300, "Valor de sell-out por cadena (a PVP)"),
                            use_container_width=True)
        with c4:
            rot_ciudad = sf.groupby("ciudad").apply(
                lambda g: g["unidades_sell_out"].sum() / max(g.groupby("cadena")["pdv_activos"].max().sum(), 1)
                / max(len(g["mes"].unique()), 1), include_groups=False).sort_values()
            fig = go.Figure(go.Bar(x=rot_ciudad.values, y=rot_ciudad.index, orientation="h",
                                   marker_color=PINK,
                                   text=[f"{x:.1f}" for x in rot_ciudad.values], textposition="outside"))
            st.plotly_chart(light(fig, 300, "Rotación por ciudad (und/PDV/mes)"), use_container_width=True)

    with t2:
        c5, c6 = st.columns([1, 1], gap="medium")
        with c5:
            q = sf.groupby("cadena")["dias_sin_stock"].mean().sort_values()
            fig = go.Figure(go.Bar(x=q.values, y=q.index, orientation="h",
                                   marker_color=[GOOD if x < 3 else WARN if x < 5 else BAD for x in q.values],
                                   text=[f"{x:.1f} días" for x in q.values], textposition="outside"))
            fig.update_xaxes(range=[0, max(q.values) * 1.4 if len(q) else 10])
            st.plotly_chart(light(fig, 320, "Días promedio sin stock en góndola"), use_container_width=True)
        with c6:
            heat = sf.pivot_table(index="cadena", columns="ciudad", values="dias_sin_stock", aggfunc="mean")
            fig = go.Figure(go.Heatmap(z=heat.values, x=heat.columns, y=heat.index,
                                       colorscale=[[0, "#eaf6f0"], [0.5, CREAM], [1, BAD]],
                                       hovertemplate="<b>%{y}</b> · %{x}<br>%{z:.1f} días sin stock<extra></extra>"))
            st.plotly_chart(light(fig, 320, "Dónde se agota el producto (días sin stock)"),
                            use_container_width=True)

        peores = sf.groupby(["cadena", "ciudad", "producto"]).agg(
            dias_sin_stock=("dias_sin_stock", "mean"),
            sell_out=("unidades_sell_out", "sum"),
            valor=("valor_sell_out_cop", "sum")).reset_index().nlargest(12, "dias_sin_stock")
        venta_perdida = (peores["valor"] / peores["sell_out"].replace(0, pd.NA)
                         * peores["dias_sin_stock"] * peores["sell_out"] / 30).fillna(0).sum()
        st.markdown(panel("Venta que se está dejando sobre la mesa", f"""
        Los 12 casos con más días de góndola vacía equivalen a una venta estimada no realizada de
        <b>{cop(venta_perdida, 1)}</b> en el período. Cada día sin stock en una cadena también
        castiga el espacio que la cadena asigna a la marca en el siguiente ciclo.
        """, "💸"), unsafe_allow_html=True)
        vista = peores.copy()
        vista["dias_sin_stock"] = vista["dias_sin_stock"].round(1)
        vista["valor"] = vista["valor"].apply(lambda x: cop(x, 1))
        vista.columns = ["Cadena", "Ciudad", "Producto", "Días sin stock", "Sell-out und", "Valor sell-out"]
        st.dataframe(vista, hide_index=True, use_container_width=True)

    with t3:
        sku = sf.groupby(["producto", "categoria"]).agg(
            sell_in=("unidades_sell_in", "sum"), sell_out=("unidades_sell_out", "sum"),
            valor=("valor_sell_out_cop", "sum"), dias_sin_stock=("dias_sin_stock", "mean"),
            rotacion=("rotacion_und_pdv_mes", "mean")).reset_index()
        sku["conversion_pct"] = (sku["sell_out"] / sku["sell_in"] * 100).round(1)
        sku = sku.sort_values("valor", ascending=False)

        c7, c8 = st.columns(2, gap="medium")
        with c7:
            top = sku.nlargest(10, "rotacion").sort_values("rotacion")
            fig = go.Figure(go.Bar(x=top["rotacion"], y=top["producto"], orientation="h",
                                   marker_color=GOOD,
                                   text=[f"{x:.1f}" for x in top["rotacion"]], textposition="outside"))
            st.plotly_chart(light(fig, 340, "Top 10 por rotación (und/PDV/mes)"), use_container_width=True)
        with c8:
            bottom = sku.nsmallest(10, "rotacion").sort_values("rotacion", ascending=False)
            fig = go.Figure(go.Bar(x=bottom["rotacion"], y=bottom["producto"], orientation="h",
                                   marker_color=WARN,
                                   text=[f"{x:.1f}" for x in bottom["rotacion"]], textposition="outside"))
            st.plotly_chart(light(fig, 340, "10 referencias con menor rotación"), use_container_width=True)

        if len(sku):
            mejor, peor = sku.loc[sku["rotacion"].idxmax()], sku.loc[sku["rotacion"].idxmin()]
            st.markdown(panel("Decisión de surtido", f"""
            · <b>{mejor['producto']}</b> es el que más rota ({mejor['rotacion']:.1f} und/PDV/mes):
              candidato natural a pedir más espacio o una segunda cara en góndola.<br>
            · <b>{peor['producto']}</b> rota {peor['rotacion']:.1f} und/PDV/mes. Antes de que la cadena
              lo descontinúe, conviene decidir: activación, cambio de precio, o sacarlo del canal
              y dejarlo solo en la tienda propia.
            """, "🎯"), unsafe_allow_html=True)

        vista = sku.copy()
        vista["valor"] = vista["valor"].apply(lambda x: cop(x, 1))
        vista["dias_sin_stock"] = vista["dias_sin_stock"].round(1)
        vista["rotacion"] = vista["rotacion"].round(1)
        vista.columns = ["Producto", "Categoría", "Sell-in und", "Sell-out und", "Valor sell-out",
                         "Días sin stock", "Rotación", "Conversión %"]
        st.dataframe(vista, hide_index=True, use_container_width=True)

    with st.expander("📍  Ver los puntos de venta", expanded=False):
        resumen = pdv.groupby(["cadena", "formato"]).size().reset_index(name="Puntos")
        c9, c10 = st.columns([1, 1.3])
        with c9:
            st.dataframe(resumen, hide_index=True, use_container_width=True)
        with c10:
            por_ciudad = pdv.groupby(["ciudad", "cadena"]).size().reset_index(name="n")
            fig = go.Figure()
            for i, cad in enumerate(sorted(por_ciudad["cadena"].unique())):
                sub = por_ciudad[por_ciudad["cadena"] == cad]
                fig.add_trace(go.Bar(x=sub["ciudad"], y=sub["n"], name=cad,
                                     marker_color=PALETTE[i % len(PALETTE)]))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 280, "Puntos de venta por ciudad"), use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *
from utils import datos

DATA = Path(__file__).parent.parent / "data"


def load():
    return datos.ventas(), datos.canales()


def render():
    v, can = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Ventas Omnicanal",
        "Todo lo que factura Paranice en un solo lugar: tienda propia, cadenas, marketplaces, "
        "especializado e internacional",
        "personaje_6.png"), unsafe_allow_html=True)

    meses = sorted(v["mes"].unique())
    f1, f2, f3 = st.columns(3)
    with f1:
        rango = st.select_slider("Rango de meses", options=meses,
                                 value=(meses[max(0, len(meses)-12)], meses[-1]), key="vt_rango")
    with f2:
        canal_sel = st.multiselect("Canales", sorted(v["canal"].unique()),
                                   default=sorted(v["canal"].unique()), key="vt_canal")
    with f3:
        cat_sel = st.multiselect("Categorías", sorted(v["categoria"].unique()),
                                 default=sorted(v["categoria"].unique()), key="vt_cat")

    vf = v[(v["mes"] >= rango[0]) & (v["mes"] <= rango[1])]
    if canal_sel:
        vf = vf[vf["canal"].isin(canal_sel)]
    if cat_sel:
        vf = vf[vf["categoria"].isin(cat_sel)]

    if vf.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        return

    ventas = vf["venta_cop"].sum()
    unidades = int(vf["unidades"].sum())
    docs = vf["documento_id"].nunique()
    margen = vf["margen_cop"].sum() / ventas * 100
    d2c = vf[vf["tipo_canal"] == "D2C"]
    part_d2c = d2c["venta_cop"].sum() / ventas * 100
    precio_medio = ventas / unidades if unidades else 0

    k = st.columns(6, gap="small")
    k[0].markdown(kpi("Ventas", cop(ventas, 1), f"{rango[0]} → {rango[1]}", True, "💰"), unsafe_allow_html=True)
    k[1].markdown(kpi("Unidades", f"{unidades:,}", "Productos vendidos", True, "📦"), unsafe_allow_html=True)
    k[2].markdown(kpi("Documentos", f"{docs:,}", "Pedidos web + órdenes de compra", True, "🧾"), unsafe_allow_html=True)
    k[3].markdown(kpi("Margen bruto", pct(margen), "Sobre ventas del período", margen >= 55, "📊"), unsafe_allow_html=True)
    k[4].markdown(kpi("Precio medio/unidad", cop(precio_medio), "Facturado por Paranice", True, "🏷️"), unsafe_allow_html=True)
    k[5].markdown(kpi("Peso del canal propio", pct(part_d2c), "Venta directa sin intermediario",
                      part_d2c > 15, "💜"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["📈  Evolución", "🗺️  Geografía", "🔎  Detalle por canal"])

    with t1:
        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            piv = vf.groupby(["mes", "canal"])["venta_cop"].sum().reset_index()
            fig = go.Figure()
            for i, cn in enumerate(sorted(piv["canal"].unique())):
                sub = piv[piv["canal"] == cn]
                fig.add_trace(go.Scatter(x=sub["mes"], y=sub["venta_cop"], name=cn, mode="lines+markers",
                                         line=dict(width=2.2, color=PALETTE[i % len(PALETTE)]),
                                         marker=dict(size=5)))
            st.plotly_chart(light(fig, 360, "Ventas mensuales por canal"), use_container_width=True)
        with c2:
            tot_mes = vf.groupby("mes")["venta_cop"].sum().reset_index()
            tot_mes["var"] = tot_mes["venta_cop"].pct_change() * 100
            fig = go.Figure(go.Bar(x=tot_mes["mes"], y=tot_mes["var"],
                                   marker_color=[GOOD if x >= 0 else BAD for x in tot_mes["var"].fillna(0)],
                                   text=[f"{x:+.0f}%" if pd.notna(x) else "" for x in tot_mes["var"]],
                                   textposition="outside"))
            st.plotly_chart(light(fig, 360, "Crecimiento mes a mes (%)"), use_container_width=True)

        c3, c4 = st.columns(2, gap="medium")
        with c3:
            piv2 = vf.groupby(["mes", "tipo_canal"])["venta_cop"].sum().reset_index()
            tot = piv2.groupby("mes")["venta_cop"].transform("sum")
            piv2["part"] = piv2["venta_cop"] / tot * 100
            fig = go.Figure()
            for i, t in enumerate(sorted(piv2["tipo_canal"].unique())):
                sub = piv2[piv2["tipo_canal"] == t]
                fig.add_trace(go.Scatter(x=sub["mes"], y=sub["part"], name=t, mode="lines",
                                         stackgroup="one", line=dict(width=0.5, color=PALETTE[i % len(PALETTE)])))
            fig.update_yaxes(ticksuffix="%")
            st.plotly_chart(light(fig, 320, "Cómo cambia el mix de canales (% de la venta)"),
                            use_container_width=True)
        with c4:
            cat_mes = vf.groupby(["mes", "categoria"])["venta_cop"].sum().reset_index()
            fig = go.Figure()
            for i, cc in enumerate(sorted(cat_mes["categoria"].unique())):
                sub = cat_mes[cat_mes["categoria"] == cc]
                fig.add_trace(go.Bar(x=sub["mes"], y=sub["venta_cop"], name=cc,
                                     marker_color=PALETTE[i % len(PALETTE)]))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 320, "Ventas por categoría"), use_container_width=True)

    with t2:
        c5, c6 = st.columns([1, 1], gap="medium")
        with c5:
            ciu = vf[vf["pais"] == "Colombia"].groupby("ciudad")["venta_cop"].sum().nlargest(8).sort_values()
            fig = go.Figure(go.Bar(x=ciu.values, y=ciu.index, orientation="h", marker_color=PURPLE,
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in ciu.values]))
            st.plotly_chart(light(fig, 340, "Ventas por ciudad · Colombia"), use_container_width=True)
        with c6:
            pais = vf.groupby("pais")["venta_cop"].sum().sort_values()
            fig = go.Figure(go.Bar(x=pais.values, y=pais.index, orientation="h",
                                   marker_color=[PINK, LAVENDER, PURPLE][:len(pais)],
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                   customdata=[cop(x, 1) for x in pais.values]))
            st.plotly_chart(light(fig, 340, "Ventas por país"), use_container_width=True)

        ciudad_canal = vf[vf["pais"] == "Colombia"].pivot_table(
            index="ciudad", columns="tipo_canal", values="venta_cop", aggfunc="sum").fillna(0)
        if not ciudad_canal.empty:
            fig = go.Figure(go.Heatmap(
                z=ciudad_canal.values, x=ciudad_canal.columns, y=ciudad_canal.index,
                colorscale=[[0, "#f7f4fb"], [0.5, LAVENDER], [1, PURPLE]],
                hovertemplate="<b>%{y}</b> · %{x}<br>%{z:,.0f} COP<extra></extra>"))
            st.plotly_chart(light(fig, 300, "Dónde vende cada tipo de canal (COP)"), use_container_width=True)

    with t3:
        detalle = vf.groupby(["canal", "tipo_canal"]).agg(
            ventas=("venta_cop", "sum"), unidades=("unidades", "sum"),
            documentos=("documento_id", "nunique"), margen=("margen_cop", "sum")).reset_index()
        detalle["margen_pct"] = (detalle["margen"] / detalle["ventas"] * 100).round(1)
        detalle["participacion_pct"] = (detalle["ventas"] / detalle["ventas"].sum() * 100).round(1)
        detalle["ticket_medio"] = (detalle["ventas"] / detalle["documentos"]).round()
        detalle = detalle.sort_values("ventas", ascending=False)

        vista = detalle.copy()
        vista["ventas"] = vista["ventas"].apply(lambda x: cop(x, 1))
        vista["margen"] = vista["margen"].apply(lambda x: cop(x, 1))
        vista["ticket_medio"] = vista["ticket_medio"].apply(cop)
        vista["unidades"] = vista["unidades"].apply(lambda x: f"{int(x):,}")
        vista.columns = ["Canal", "Tipo", "Ventas", "Unidades", "Documentos", "Margen $",
                         "Margen %", "Part. %", "Ticket medio"]
        st.dataframe(vista, hide_index=True, use_container_width=True)

        mejor = detalle.iloc[0]
        mayor_margen = detalle.loc[detalle["margen_pct"].idxmax()]
        menor_margen = detalle.loc[detalle["margen_pct"].idxmin()]
        st.markdown(panel("Cómo leer esta tabla", f"""
        · <b>{mejor['canal']}</b> aporta {mejor['participacion_pct']:.0f}% de la venta del período.<br>
        · El canal más rentable es <b>{mayor_margen['canal']}</b> ({mayor_margen['margen_pct']:.0f}% de margen)
          y el menos rentable es <b>{menor_margen['canal']}</b> ({menor_margen['margen_pct']:.0f}%).
          La diferencia es lo que cuesta llegar al consumidor por un tercero.<br>
        · Mover un punto de mix desde <b>{menor_margen['canal']}</b> hacia el canal propio libera cerca de
          <b>{cop(vf['venta_cop'].sum() * 0.01 * (mayor_margen['margen_pct'] - menor_margen['margen_pct']) / 100, 1)}</b>
          de margen adicional en un período como este.
        """, "💡"), unsafe_allow_html=True)

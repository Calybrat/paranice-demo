import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *
from utils import datos

DATA = Path(__file__).parent.parent / "data"
HOY = pd.Timestamp("2026-08-31")


def load():
    return (datos.ventas(), datos.finanzas(), datos.clientes(), datos.despachos(),
            datos.cartera(), datos.inventario(), datos.sellout(), datos.produccion())


def render():
    v, fin, cli, desp, car, inv, so, prod = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Dashboard General",
        "Vista única del negocio · e-commerce propio, Éxito, Carulla, Rappi, Fithub, naturistas, "
        "Costa Rica y EE.UU. · corte al 31 de agosto de 2026",
        "personaje_2.png"), unsafe_allow_html=True)

    meses = sorted(v["mes"].unique())
    c_f1, c_f2, c_f3 = st.columns([2, 2, 2])
    with c_f1:
        periodo = st.selectbox("Período", ["Último mes", "Últimos 3 meses", "2026 (YTD)", "Todo el histórico"],
                               key="db_per")
    with c_f2:
        pais_sel = st.selectbox("País", ["Todos"] + sorted(v["pais"].unique()), key="db_pais")
    with c_f3:
        tipo_sel = st.selectbox("Tipo de canal", ["Todos"] + sorted(v["tipo_canal"].unique()), key="db_tipo")

    if periodo == "Último mes":
        act, ant = [meses[-1]], [meses[-2]]
    elif periodo == "Últimos 3 meses":
        act, ant = meses[-3:], meses[-6:-3]
    elif periodo == "2026 (YTD)":
        act = [m for m in meses if m.startswith("2026")]
        ant = [m for m in meses if m.startswith("2025")][:len(act)]
    else:
        act, ant = meses, []

    vf = v[v["mes"].isin(act)]
    vp = v[v["mes"].isin(ant)]
    if pais_sel != "Todos":
        vf, vp = vf[vf["pais"] == pais_sel], vp[vp["pais"] == pais_sel]
    if tipo_sel != "Todos":
        vf, vp = vf[vf["tipo_canal"] == tipo_sel], vp[vp["tipo_canal"] == tipo_sel]

    ventas_act, ventas_ant = vf["venta_cop"].sum(), vp["venta_cop"].sum()
    delta = (ventas_act - ventas_ant) / ventas_ant * 100 if ventas_ant else 0
    margen = vf["margen_cop"].sum() / ventas_act * 100 if ventas_act else 0

    fin_act = fin[fin["mes"].isin(act)]
    ebitda_pct = (fin_act["ebitda_cop"].sum() / fin_act["ingresos_cop"].sum() * 100
                  if fin_act["ingresos_cop"].sum() else 0)

    d2c = vf[vf["tipo_canal"] == "D2C"]
    aov = d2c["venta_cop"].sum() / d2c["documento_id"].nunique() if d2c["documento_id"].nunique() else 0
    recompra = cli["recurrente"].mean() * 100 if len(cli) else 0

    ent = desp[(desp["estado"] == "Entregado") & (desp["tipo_canal"] != "D2C")]
    otif = ent["otif"].mean() * 100 if len(ent) else 0

    abierta = car[~car["pagada"]]
    vencida = abierta[abierta["dias_mora"] > 0]["valor_cop"].sum()
    pct_venc = vencida / abierta["valor_cop"].sum() * 100 if abierta["valor_cop"].sum() else 0

    pdv_activos = int(so[so["mes"].isin(act)]["pdv_activos"].groupby(
        [so[so["mes"].isin(act)]["cadena"], so[so["mes"].isin(act)]["ciudad"]]).max().sum()) if len(so) else 0

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k = st.columns(4, gap="small")
    k[0].markdown(kpi("Ventas del período", cop(ventas_act, 1),
                      f"{'▲' if delta >= 0 else '▼'} {abs(delta):.1f}% vs período anterior", delta >= 0,
                      "💰", "Facturación de Paranice en todos los canales."), unsafe_allow_html=True)
    k[1].markdown(kpi("Margen bruto", pct(margen), "Meta interna: 58%", margen >= 58,
                      "📊", "Venta menos costo de producto, antes de gastos."), unsafe_allow_html=True)
    k[2].markdown(kpi("EBITDA", pct(ebitda_pct), "Después de mercadeo, logística y nómina", ebitda_pct >= 10,
                      "🏦", "Lo que deja la operación cada mes."), unsafe_allow_html=True)
    k[3].markdown(kpi("Ticket promedio web", cop(aov), "Pedido mínimo del sitio: $50.000", aov >= 90000,
                      "🛒", "Cuánto gasta en promedio quien compra en paranice.co."), unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    k2 = st.columns(4, gap="small")
    k2[0].markdown(kpi("Cobertura retail", f"{pdv_activos:,} PDV", "Éxito · Carulla · Fithub · naturistas",
                       pdv_activos > 100, "🏬", "Puntos de venta que movieron producto."), unsafe_allow_html=True)
    k2[1].markdown(kpi("OTIF a cadenas", pct(otif), "Meta: 95%", otif >= 95,
                       "📦", "Órdenes entregadas completas y a tiempo."), unsafe_allow_html=True)
    k2[2].markdown(kpi("Cartera vencida", cop(vencida, 1), f"{pct_venc:.1f}% de la cartera abierta",
                       pct_venc < 20, "⏳", "Plata facturada a cadenas que ya debería estar cobrada."), unsafe_allow_html=True)
    k2[3].markdown(kpi("Recompra web", pct(recompra), "Clientes con 2+ pedidos", recompra > 30,
                       "🔁", "Qué tanto vuelven los clientes del canal propio."), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ── Gráficos ──────────────────────────────────────────────────────────────
    c1, c2 = st.columns([1.65, 1], gap="medium")
    with c1:
        piv = v.groupby(["mes", "tipo_canal"])["venta_cop"].sum().reset_index()
        fig = go.Figure()
        for i, t in enumerate(["D2C", "Retail", "Marketplace", "Especializado", "Internacional"]):
            sub = piv[piv["tipo_canal"] == t]
            if len(sub):
                fig.add_trace(go.Bar(x=sub["mes"], y=sub["venta_cop"], name=t,
                                     marker_color=PALETTE[i % len(PALETTE)]))
        fig.update_layout(barmode="stack")
        st.plotly_chart(light(fig, 330, "Ventas mensuales por tipo de canal (COP)"), use_container_width=True)
    with c2:
        mix = vf.groupby("canal")["venta_cop"].sum().sort_values(ascending=False)
        fig = go.Figure(go.Pie(labels=mix.index, values=mix.values, hole=0.58,
                               marker_colors=PALETTE, textinfo="percent",
                               hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
                               customdata=[cop(x, 1) for x in mix.values]))
        st.plotly_chart(light(fig, 330, "Mix de canales del período"), use_container_width=True)

    c3, c4, c5 = st.columns(3, gap="medium")
    with c3:
        top = vf.groupby("producto")["venta_cop"].sum().nlargest(8).sort_values()
        fig = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h", marker_color=PURPLE,
                               hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                               customdata=[cop(x, 1) for x in top.values]))
        st.plotly_chart(light(fig, 300, "Top 8 productos"), use_container_width=True)
    with c4:
        cat = vf.groupby("categoria")["venta_cop"].sum().sort_values()
        fig = go.Figure(go.Bar(x=cat.values, y=cat.index, orientation="h", marker_color=PINK,
                               hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                               customdata=[cop(x, 1) for x in cat.values]))
        st.plotly_chart(light(fig, 300, "Ventas por categoría"), use_container_width=True)
    with c5:
        _agg = vf.groupby("tipo_canal", observed=True)[["margen_cop", "venta_cop"]].sum()
        mg = (_agg["margen_cop"] / _agg["venta_cop"] * 100).sort_values()
        fig = go.Figure(go.Bar(x=mg.values, y=mg.index, orientation="h",
                               marker_color=[GOOD if x >= 55 else WARN for x in mg.values],
                               text=[f"{x:.0f}%" for x in mg.values], textposition="outside"))
        fig.update_xaxes(range=[0, max(mg.values) * 1.25 if len(mg) else 100])
        st.plotly_chart(light(fig, 300, "Margen bruto por tipo de canal"), use_container_width=True)

    # ── Lectura automática + alertas ──────────────────────────────────────────
    mejor_canal = vf.groupby("canal")["venta_cop"].sum().idxmax() if len(vf) else "—"
    peor_margen = mg.idxmin() if len(mg) else "—"
    criticos = inv[inv["estado"] == "Crítico"]
    lotes_alerta = prod[prod["estado_calidad"] != "Aprobado"]
    quiebres = so[so["mes"].isin(act)].nlargest(5, "dias_sin_stock")

    c6, c7 = st.columns([1, 1], gap="medium")
    with c6:
        st.markdown(panel("Lectura del período", f"""
        · <b>{mejor_canal}</b> es el canal que más factura en el período.<br>
        · El margen más bajo está en <b>{peor_margen}</b> ({mg.min():.0f}%): es el costo de ganar
          cobertura y volumen a través de terceros.<br>
        · La recompra del canal propio va en <b>{pct(recompra)}</b>; cada punto que suba baja
          la dependencia de pauta.<br>
        · Hay <b>{cop(vencida, 1)}</b> de cartera vencida ({pct_venc:.0f}% de lo abierto),
          principalmente de cadenas que pagan a 45–60 días.
        """, "🔍"), unsafe_allow_html=True)
    with c7:
        st.markdown(panel("Qué necesita atención hoy", f"""
        · <b>{len(criticos)} referencias</b> con inventario crítico (menos de 12 días de cobertura).<br>
        · <b>{len(lotes_alerta)} lotes</b> en cuarentena o rechazados por ensayo de gluten.<br>
        · <b>{int(quiebres['dias_sin_stock'].sum()) if len(quiebres) else 0} días</b> de góndola vacía
          acumulados en los 5 casos más críticos de quiebre en cadenas.<br>
        · <b>{int((desp['estado'] == 'En tránsito').sum())} despachos</b> siguen en tránsito.
        """, "⚠️"), unsafe_allow_html=True)

    with st.expander("Ver detalle de alertas", expanded=False):
        a1, a2, a3 = st.columns(3)
        with a1:
            st.markdown(f"<b style='color:{BAD}'>📦 Inventario crítico</b>", unsafe_allow_html=True)
            st.dataframe(criticos[["producto", "cedi", "stock_unidades", "dias_cobertura"]].head(8),
                         hide_index=True, use_container_width=True)
        with a2:
            st.markdown(f"<b style='color:{WARN}'>🧪 Lotes con hallazgo de calidad</b>", unsafe_allow_html=True)
            st.dataframe(lotes_alerta.sort_values("fecha", ascending=False)[
                ["lote_id", "producto", "gluten_ppm", "estado_calidad"]].head(8),
                hide_index=True, use_container_width=True)
        with a3:
            st.markdown(f"<b style='color:{WARN}'>🏬 Quiebres en góndola</b>", unsafe_allow_html=True)
            st.dataframe(quiebres[["cadena", "ciudad", "producto", "dias_sin_stock"]],
                         hide_index=True, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *
from utils import datos


def load():
    return datos.clientes(), datos.ventas(), datos.marketing()


def render():
    cli, v, mkt = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Clientes & Recompra",
        "Quién compra en paranice.co, cuánto cuesta traerlo, cuánto deja y qué tanto vuelve",
        "personaje_4.png"), unsafe_allow_html=True)

    total = len(cli)
    recompra = cli["recurrente"].mean() * 100
    ltv = cli["ltv_cop"].mean()
    ticket = cli["ticket_promedio_cop"].mean()
    inversion = mkt["inversion_cop"].sum()
    nuevos = mkt["clientes_nuevos"].sum()
    cac = inversion / nuevos if nuevos else 0
    ratio = ltv / cac if cac else 0
    en_riesgo = int(cli["en_riesgo_fuga"].sum())
    valor_riesgo = cli[cli["en_riesgo_fuga"]]["ltv_cop"].sum()

    k = st.columns(6, gap="small")
    k[0].markdown(kpi("Clientes", f"{total:,}", "Han comprado al menos una vez", True, "💜"),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("Recompra", pct(recompra), "Referencia D2C: 30%", recompra >= 30, "🔁",
                      "Clientes con 2 o más pedidos."), unsafe_allow_html=True)
    k[2].markdown(kpi("LTV promedio", cop(ltv), "Valor histórico por cliente", True, "💎"),
                  unsafe_allow_html=True)
    k[3].markdown(kpi("CAC", cop(cac), "Costo de traer un cliente nuevo", cac < ltv * 0.35, "🎯"),
                  unsafe_allow_html=True)
    k[4].markdown(kpi("LTV / CAC", f"{ratio:.1f}x", "Meta: más de 3x", ratio >= 3, "⚖️",
                      "Cuántas veces recuperas lo que inviertes en captar."), unsafe_allow_html=True)
    k[5].markdown(kpi("En riesgo de fuga", f"{en_riesgo:,}", cop(valor_riesgo, 1) + " en juego",
                      en_riesgo < total * 0.1, "🚨",
                      "Compraron 2+ veces y llevan más de 120 días sin volver."), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["📈  Adquisición y recompra", "🧩  Segmentos", "🚨  Recuperables"])

    with t1:
        c1, c2 = st.columns([1.5, 1], gap="medium")
        with c1:
            cli["mes_alta"] = cli["primera_compra"].dt.strftime("%Y-%m")
            nuevos_mes = cli.groupby("mes_alta").size().reset_index(name="nuevos")
            d2c = v[v["tipo_canal"] == "D2C"].drop_duplicates("documento_id")
            ped_mes = d2c.groupby("mes")["documento_id"].nunique().reset_index(name="pedidos")
            comp = ped_mes.merge(nuevos_mes, left_on="mes", right_on="mes_alta", how="left").fillna(0)
            comp["recurrentes"] = comp["pedidos"] - comp["nuevos"]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=comp["mes"], y=comp["nuevos"], name="Pedidos de clientes nuevos",
                                 marker_color=PINK))
            fig.add_trace(go.Bar(x=comp["mes"], y=comp["recurrentes"], name="Pedidos de clientes que vuelven",
                                 marker_color=PURPLE))
            fig.update_layout(barmode="stack")
            st.plotly_chart(light(fig, 350, "De dónde salen los pedidos cada mes"),
                            use_container_width=True)
        with c2:
            comp["pct_recurrente"] = comp["recurrentes"] / comp["pedidos"] * 100
            fig = go.Figure(go.Scatter(x=comp["mes"], y=comp["pct_recurrente"], mode="lines+markers",
                                       line=dict(color=PURPLE, width=3), fill="tozeroy",
                                       fillcolor="rgba(42,29,101,.10)"))
            fig.update_yaxes(ticksuffix="%")
            st.plotly_chart(light(fig, 350, "% de pedidos que vienen de clientes que ya compraron"),
                            use_container_width=True)

        c3, c4 = st.columns(2, gap="medium")
        with c3:
            cac_canal = mkt.groupby("canal").agg(inv=("inversion_cop", "sum"),
                                                 nuevos=("clientes_nuevos", "sum")).reset_index()
            cac_canal = cac_canal[cac_canal["inv"] > 0]
            cac_canal["cac"] = cac_canal["inv"] / cac_canal["nuevos"].replace(0, pd.NA)
            cac_canal = cac_canal.dropna(subset=["cac"]).sort_values("cac")
            fig = go.Figure(go.Bar(x=cac_canal["cac"], y=cac_canal["canal"], orientation="h",
                                   marker_color=[GOOD if x < ltv * 0.35 else WARN for x in cac_canal["cac"]],
                                   text=[cop(x) for x in cac_canal["cac"]], textposition="outside"))
            fig.update_xaxes(range=[0, cac_canal["cac"].max() * 1.35])
            st.plotly_chart(light(fig, 320, "Cuánto cuesta un cliente nuevo por canal"),
                            use_container_width=True)
        with c4:
            ciudad = cli.groupby("ciudad").agg(clientes=("cliente_id", "count"),
                                               ltv=("ltv_cop", "mean")).reset_index()
            ciudad = ciudad.nlargest(10, "clientes").sort_values("clientes")
            fig = go.Figure(go.Bar(x=ciudad["clientes"], y=ciudad["ciudad"], orientation="h",
                                   marker_color=PURPLE,
                                   customdata=[cop(x) for x in ciudad["ltv"]],
                                   hovertemplate="<b>%{y}</b><br>%{x:,} clientes · LTV %{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 320, "Ciudades con más clientes"), use_container_width=True)

    with t2:
        orden = ["Primera compra", "Repite", "Fiel", "Embajador"]
        seg = cli.groupby("segmento").agg(clientes=("cliente_id", "count"),
                                          ltv=("ltv_cop", "mean"),
                                          ventas=("ltv_cop", "sum"),
                                          ticket=("ticket_promedio_cop", "mean")).reindex(orden).fillna(0)

        c5, c6 = st.columns([1, 1.3], gap="medium")
        with c5:
            fig = go.Figure(go.Pie(labels=seg.index, values=seg["clientes"], hole=0.58,
                                   marker_colors=[LAVENDER_LT, LAVENDER, PINK, PURPLE],
                                   textinfo="label+percent"))
            st.plotly_chart(light(fig, 340, "Cuántos clientes hay en cada segmento"),
                            use_container_width=True)
        with c6:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=seg.index, y=seg["ventas"], name="Facturación acumulada",
                                 marker_color=PURPLE,
                                 customdata=[cop(x, 1) for x in seg["ventas"]],
                                 hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 340, "Cuánta plata aporta cada segmento"),
                            use_container_width=True)

        emb = seg.loc["Embajador"] if "Embajador" in seg.index else None
        primera = seg.loc["Primera compra"] if "Primera compra" in seg.index else None
        if emb is not None and primera is not None and seg["ventas"].sum() > 0:
            st.markdown(panel("Lectura de segmentos", f"""
            · Los <b>Embajadores</b> son {emb['clientes']/seg['clientes'].sum()*100:.0f}% de los clientes
              pero aportan {emb['ventas']/seg['ventas'].sum()*100:.0f}% de la facturación del canal propio,
              con un LTV de {cop(emb['ltv'])}.<br>
            · Los de <b>Primera compra</b> son {primera['clientes']/seg['clientes'].sum()*100:.0f}% de la base:
              el mayor potencial está en llevar una parte de ellos a la segunda compra, que es la más difícil.<br>
            · Subir la recompra del <b>{pct(recompra)}</b> actual a un 45% significaría, con la base de hoy,
              cerca de <b>{cop(cli['ticket_promedio_cop'].mean() * total * 0.067, 1)}</b> adicionales
              sin gastar un peso más en pauta.
            """, "🧩"), unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        vista = seg.reset_index()
        vista["ltv"] = vista["ltv"].apply(cop)
        vista["ventas"] = vista["ventas"].apply(lambda x: cop(x, 1))
        vista["ticket"] = vista["ticket"].apply(cop)
        vista.columns = ["Segmento", "Clientes", "LTV promedio", "Facturación", "Ticket promedio"]
        st.dataframe(vista, hide_index=True, use_container_width=True)

    with t3:
        st.markdown(panel("Lista de acción", """
        Estos clientes ya compraron más de una vez —o sea, les gustó el producto— pero llevan más de
        120 días sin volver. Es la base más barata de reactivar: ya conocen la marca y no hay que
        pagar pauta para alcanzarlos, basta un correo por Omnisend o un WhatsApp.
        """, "🚨"), unsafe_allow_html=True)

        riesgo = cli[cli["en_riesgo_fuga"]].sort_values("ltv_cop", ascending=False)
        c7, c8 = st.columns([1, 1], gap="medium")
        with c7:
            por_ciudad = riesgo.groupby("ciudad")["ltv_cop"].sum().nlargest(8).sort_values()
            fig = go.Figure(go.Bar(x=por_ciudad.values, y=por_ciudad.index, orientation="h",
                                   marker_color=WARN,
                                   customdata=[cop(x, 1) for x in por_ciudad.values],
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 300, "Valor en riesgo por ciudad"), use_container_width=True)
        with c8:
            bins = pd.cut(riesgo["dias_sin_comprar"], [120, 180, 240, 300, 10000],
                          labels=["120–180 días", "180–240", "240–300", "+300"])
            dist = bins.value_counts().reindex(["120–180 días", "180–240", "240–300", "+300"])
            fig = go.Figure(go.Bar(x=dist.index.astype(str), y=dist.values,
                                   marker_color=[WARN, "#e08b3c", BAD, "#b3384a"],
                                   text=dist.values, textposition="outside"))
            st.plotly_chart(light(fig, 300, "Hace cuánto no compran"), use_container_width=True)

        vista = riesgo.head(50)[["cliente_id", "ciudad", "canal_captacion", "pedidos",
                                 "ltv_cop", "ultima_compra", "dias_sin_comprar", "segmento"]].copy()
        vista["ltv_cop"] = vista["ltv_cop"].apply(cop)
        vista["ultima_compra"] = vista["ultima_compra"].dt.strftime("%Y-%m-%d")
        vista.columns = ["Cliente", "Ciudad", "Cómo llegó", "Pedidos", "LTV", "Última compra",
                         "Días sin comprar", "Segmento"]
        st.dataframe(vista, hide_index=True, use_container_width=True)
        st.caption("En el producto final esta lista se puede exportar o enviar directo a Omnisend/WhatsApp.")

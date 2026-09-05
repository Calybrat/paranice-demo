import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *
from utils import datos

HOY = pd.Timestamp("2026-08-31")


def load():
    return datos.finanzas(), datos.cartera(), datos.empleados()


def render():
    fin, car, emp = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Finanzas & Cartera",
        "Rentabilidad mes a mes y la plata que está en la calle: cuánto deben las cadenas y hace cuánto",
        "personaje_2.png"), unsafe_allow_html=True)

    meses = sorted(fin["mes"].unique())
    rango = st.select_slider("Rango de meses", options=meses,
                             value=(meses[max(0, len(meses)-12)], meses[-1]), key="fn_rango")
    ff = fin[(fin["mes"] >= rango[0]) & (fin["mes"] <= rango[1])]

    ingresos = ff["ingresos_cop"].sum()
    mb = ff["margen_bruto_cop"].sum()
    ebitda = ff["ebitda_cop"].sum()
    mb_pct = mb / ingresos * 100 if ingresos else 0
    eb_pct = ebitda / ingresos * 100 if ingresos else 0
    mkt_pct = ff["gasto_marketing_cop"].sum() / ingresos * 100 if ingresos else 0
    nomina_pct = ff["nomina_cop"].sum() / ingresos * 100 if ingresos else 0

    abierta = car[~car["pagada"]]
    total_abierto = abierta["valor_cop"].sum()
    vencida = abierta[abierta["dias_mora"] > 0]["valor_cop"].sum()
    pct_venc = vencida / total_abierto * 100 if total_abierto else 0
    dso = (abierta["dias_mora"] + abierta["plazo_dias"]).mean() if len(abierta) else 0

    k = st.columns(6, gap="small")
    k[0].markdown(kpi("Ingresos del período", cop(ingresos, 1), f"{rango[0]} → {rango[1]}", True, "💰"),
                  unsafe_allow_html=True)
    k[1].markdown(kpi("Margen bruto", pct(mb_pct), cop(mb, 1), mb_pct >= 50, "📊"), unsafe_allow_html=True)
    k[2].markdown(kpi("EBITDA", pct(eb_pct), cop(ebitda, 1), eb_pct >= 10, "🏦",
                      "Lo que queda después de todos los gastos operativos."), unsafe_allow_html=True)
    k[3].markdown(kpi("Peso de la nómina", pct(nomina_pct), "Administrativa y comercial",
                      nomina_pct < 25, "👥"), unsafe_allow_html=True)
    k[4].markdown(kpi("Cartera abierta", cop(total_abierto, 1), f"{pct_venc:.0f}% ya vencida",
                      pct_venc < 20, "⏳"), unsafe_allow_html=True)
    k[5].markdown(kpi("Días de cobro (DSO)", f"{dso:.0f}", "Objetivo: menos de 60", dso < 60, "📅",
                      "Cuánto tarda en volver la plata facturada."), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["📉  Resultado mensual", "⏳  Cartera y cobranza", "👥  Nómina"])

    with t1:
        c1, c2 = st.columns([1.6, 1], gap="medium")
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=ff["mes"], y=ff["margen_bruto_cop"], name="Margen bruto",
                                 marker_color=LAVENDER_LT))
            fig.add_trace(go.Bar(x=ff["mes"], y=-ff["gasto_marketing_cop"], name="Marketing",
                                 marker_color=PINK))
            fig.add_trace(go.Bar(x=ff["mes"], y=-ff["nomina_cop"], name="Nómina",
                                 marker_color=LAVENDER))
            fig.add_trace(go.Bar(x=ff["mes"], y=-ff["gasto_logistica_cop"], name="Logística",
                                 marker_color=CREAM))
            fig.add_trace(go.Bar(x=ff["mes"], y=-ff["otros_gastos_cop"], name="Otros",
                                 marker_color="#d9d2e8"))
            fig.add_trace(go.Scatter(x=ff["mes"], y=ff["ebitda_cop"], name="EBITDA",
                                     mode="lines+markers", line=dict(color=PURPLE, width=3.5),
                                     marker=dict(size=7)))
            fig.update_layout(barmode="relative")
            st.plotly_chart(light(fig, 380, "De dónde sale (y a dónde se va) el margen"),
                            use_container_width=True)
        with c2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ff["mes"], y=ff["margen_bruto_pct"], name="Margen bruto %",
                                     mode="lines+markers", line=dict(color=PINK, width=3)))
            fig.add_trace(go.Scatter(x=ff["mes"], y=ff["ebitda_pct"], name="EBITDA %",
                                     mode="lines+markers", line=dict(color=PURPLE, width=3)))
            fig.update_yaxes(ticksuffix="%")
            st.plotly_chart(light(fig, 380, "Rentabilidad en porcentaje"), use_container_width=True)

        ultimo = ff.iloc[-1]
        primero = ff.iloc[0]
        st.markdown(panel("Lectura financiera", f"""
        · El último mes cerró con <b>{cop(ultimo['ingresos_cop'], 1)}</b> de ingresos,
          <b>{ultimo['margen_bruto_pct']:.1f}%</b> de margen bruto y
          <b>{ultimo['ebitda_pct']:.1f}%</b> de EBITDA.<br>
        · El margen bruto pasó de {primero['margen_bruto_pct']:.1f}% a {ultimo['margen_bruto_pct']:.1f}%
          en el período: la mezcla de canales es lo que más lo mueve, porque cada canal deja un margen distinto.<br>
        · Marketing pesa <b>{pct(mkt_pct)}</b> de la venta y la nómina administrativa
          <b>{pct(nomina_pct)}</b>. Son las dos palancas de gasto con mayor efecto sobre el EBITDA.
        """, "📉"), unsafe_allow_html=True)

        vista = ff.copy()
        for col in ["ingresos_cop", "costo_ventas_cop", "margen_bruto_cop", "gasto_marketing_cop",
                    "gasto_logistica_cop", "nomina_cop", "otros_gastos_cop", "ebitda_cop"]:
            vista[col] = vista[col].apply(lambda x: cop(x, 1))
        for col in ["margen_bruto_pct", "ebitda_pct"]:
            vista[col] = vista[col].apply(lambda x: pct(x))
        vista.columns = ["Mes", "Ingresos", "Costo de ventas", "Margen bruto", "Margen %",
                         "Marketing", "Logística", "Nómina", "Otros", "EBITDA", "EBITDA %"]
        st.dataframe(vista, hide_index=True, use_container_width=True)

    with t2:
        st.markdown(panel("Por qué esto define el flujo de caja", """
        Las cadenas pagan a 45 y 60 días, y el consumidor del canal propio paga de inmediato.
        Eso significa que mientras más crezca el peso de retail, más capital de trabajo necesita
        Paranice para financiar el crecimiento. Esta vista muestra cuánta plata está en la calle,
        quién la debe y hace cuánto.
        """, "⏳"), unsafe_allow_html=True)

        buckets = {
            "Vigente": abierta[abierta["dias_mora"] == 0]["valor_cop"].sum(),
            "1–30 días": abierta[abierta["dias_mora"].between(1, 30)]["valor_cop"].sum(),
            "31–60 días": abierta[abierta["dias_mora"].between(31, 60)]["valor_cop"].sum(),
            "61–90 días": abierta[abierta["dias_mora"].between(61, 90)]["valor_cop"].sum(),
            "+90 días": abierta[abierta["dias_mora"] > 90]["valor_cop"].sum(),
        }
        c3, c4 = st.columns([1.3, 1], gap="medium")
        with c3:
            fig = go.Figure(go.Bar(x=list(buckets.keys()), y=list(buckets.values()),
                                   marker_color=[GOOD, WARN, "#e08b3c", BAD, "#b3384a"],
                                   customdata=[cop(x, 1) for x in buckets.values()],
                                   hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 340, "Antigüedad de la cartera (aging)"), use_container_width=True)
        with c4:
            por_cliente = abierta.groupby("cliente")["valor_cop"].sum().sort_values()
            fig = go.Figure(go.Bar(x=por_cliente.values, y=por_cliente.index, orientation="h",
                                   marker_color=PURPLE,
                                   customdata=[cop(x, 1) for x in por_cliente.values],
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 340, "Quién debe la plata"), use_container_width=True)

        c5, c6 = st.columns(2, gap="medium")
        with c5:
            mora_cliente = abierta[abierta["dias_mora"] > 0].groupby("cliente").agg(
                valor=("valor_cop", "sum"), mora=("dias_mora", "mean")).reset_index().sort_values("valor")
            fig = go.Figure(go.Bar(x=mora_cliente["valor"], y=mora_cliente["cliente"], orientation="h",
                                   marker_color=[BAD if x > 45 else WARN for x in mora_cliente["mora"]],
                                   customdata=[f"{x:.0f} días" for x in mora_cliente["mora"]],
                                   hovertemplate="<b>%{y}</b><br>mora promedio %{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 300, "Cartera vencida por cliente"), use_container_width=True)
        with c6:
            recaudo = car[car["pagada"]].copy()
            recaudo["mes_fac"] = recaudo["fecha_factura"].dt.strftime("%Y-%m")
            ev = recaudo.groupby("mes_fac")["valor_cop"].sum().reset_index()
            fig = go.Figure(go.Bar(x=ev["mes_fac"], y=ev["valor_cop"], marker_color=GOOD,
                                   customdata=[cop(x, 1) for x in ev["valor_cop"]],
                                   hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 300, "Facturación ya recaudada, por mes de emisión"),
                            use_container_width=True)

        criticas = abierta[abierta["dias_mora"] > 60].sort_values("dias_mora", ascending=False)
        st.markdown(f"<p style='font-size:13px;font-weight:800;color:{PURPLE};margin:14px 0 6px'>"
                    f"🚨 Facturas con más de 60 días de mora ({len(criticas)})</p>", unsafe_allow_html=True)
        if len(criticas):
            vista = criticas.head(25)[["factura_id", "cliente", "fecha_factura", "fecha_vencimiento",
                                       "plazo_dias", "dias_mora", "valor_cop", "estado"]].copy()
            vista["fecha_factura"] = vista["fecha_factura"].dt.strftime("%Y-%m-%d")
            vista["fecha_vencimiento"] = vista["fecha_vencimiento"].dt.strftime("%Y-%m-%d")
            vista["valor_cop"] = vista["valor_cop"].apply(cop)
            vista.columns = ["Factura", "Cliente", "Emitida", "Vence", "Plazo", "Días mora", "Valor", "Estado"]
            st.dataframe(vista, hide_index=True, use_container_width=True)
        else:
            st.success("No hay facturas con más de 60 días de mora.")

    with t3:
        activos = emp[emp["activo"]]
        nomina_total = activos["salario_cop"].sum() * 1.52
        c7, c8 = st.columns(2, gap="medium")
        with c7:
            area = activos.groupby("area").agg(personas=("empleado_id", "count"),
                                               nomina=("salario_cop", "sum")).reset_index()
            area["nomina"] = area["nomina"] * 1.52
            area = area.sort_values("nomina")
            fig = go.Figure(go.Bar(x=area["nomina"], y=area["area"], orientation="h", marker_color=PURPLE,
                                   customdata=[f"{int(p)} personas · {cop(n, 1)}"
                                               for p, n in zip(area["personas"], area["nomina"])],
                                   hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>"))
            st.plotly_chart(light(fig, 340, "Nómina mensual por área (con prestaciones)"),
                            use_container_width=True)
        with c8:
            riesgo = activos.groupby("rotacion_riesgo").size().reindex(["Bajo", "Medio", "Alto"]).fillna(0)
            fig = go.Figure(go.Bar(x=riesgo.index, y=riesgo.values,
                                   marker_color=[GOOD, WARN, BAD],
                                   text=[int(x) for x in riesgo.values], textposition="outside"))
            st.plotly_chart(light(fig, 340, "Riesgo de rotación del equipo"), use_container_width=True)

        k2 = st.columns(4, gap="small")
        k2[0].markdown(kpi("Personas activas", f"{len(activos)}", f"{emp['area'].nunique()} áreas", True, "👥"),
                       unsafe_allow_html=True)
        k2[1].markdown(kpi("Nómina mensual", cop(nomina_total, 1), "Incluye prestaciones", True, "💵"),
                       unsafe_allow_html=True)
        k2[2].markdown(kpi("Antigüedad promedio", f"{activos['antiguedad_anios'].mean():.1f} años", "",
                           activos["antiguedad_anios"].mean() > 1.5, "📆"), unsafe_allow_html=True)
        k2[3].markdown(kpi("Contratos indefinidos",
                           pct((activos["tipo_contrato"] == "Indefinido").mean() * 100), "Del total activo",
                           True, "📝"), unsafe_allow_html=True)

        st.caption("La nómina de planta se contabiliza dentro del costo del producto; en el EBITDA de "
                   "arriba solo entra la nómina administrativa y comercial para no contarla dos veces.")

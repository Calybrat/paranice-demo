import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

BANDERAS = {"Colombia": "🇨🇴", "Costa Rica": "🇨🇷", "Estados Unidos": "🇺🇸"}
LANZAMIENTOS = {"Colombia": "mercado base", "Costa Rica": "mayo 2025", "Estados Unidos": "octubre 2025"}


@st.cache_data
def load():
    v = leer_csv("ventas.csv")
    d = leer_csv("despachos.csv")
    return v, d


def render():
    v, d = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Expansión Internacional",
        "Colombia, Costa Rica y Estados Unidos: qué tan sano es el negocio en cada mercado, "
        "no solo cuánto vende",
        "personaje_palenquera.png"), unsafe_allow_html=True)

    total = v["venta_cop"].sum()
    por_pais = v.groupby("pais").agg(ventas=("venta_cop", "sum"), margen=("margen_cop", "sum"),
                                     unidades=("unidades", "sum"),
                                     docs=("documento_id", "nunique")).reset_index()
    por_pais["margen_pct"] = por_pais["margen"] / por_pais["ventas"] * 100
    por_pais["part"] = por_pais["ventas"] / total * 100

    meses = sorted(v["mes"].unique())
    ult, prev = meses[-1], meses[-2]

    k = st.columns(len(por_pais) + 1, gap="small")
    k[0].markdown(kpi("Mercados activos", str(len(por_pais)), "Con venta en el histórico", True, "🌎"),
                  unsafe_allow_html=True)
    for i, (_, r) in enumerate(por_pais.sort_values("ventas", ascending=False).iterrows()):
        act = v[(v["mes"] == ult) & (v["pais"] == r["pais"])]["venta_cop"].sum()
        ant = v[(v["mes"] == prev) & (v["pais"] == r["pais"])]["venta_cop"].sum()
        var = (act - ant) / ant * 100 if ant else 0
        k[i + 1].markdown(kpi(f"{BANDERAS.get(r['pais'], '')} {r['pais']}", pct(r["part"]),
                              f"{'▲' if var >= 0 else '▼'} {abs(var):.0f}% último mes", var >= 0,
                              "", f"Margen {r['margen_pct']:.0f}% · {LANZAMIENTOS.get(r['pais'], '')}"),
                          unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.6, 1], gap="medium")
    with c1:
        piv = v.groupby(["mes", "pais"])["venta_cop"].sum().reset_index()
        fig = go.Figure()
        for i, p in enumerate(sorted(piv["pais"].unique())):
            sub = piv[piv["pais"] == p]
            fig.add_trace(go.Scatter(x=sub["mes"], y=sub["venta_cop"], name=f"{BANDERAS.get(p,'')} {p}",
                                     mode="lines+markers", line=dict(width=2.6, color=PALETTE[i % len(PALETTE)]),
                                     marker=dict(size=6)))
        st.plotly_chart(light(fig, 360, "Ventas mensuales por mercado (COP)"), use_container_width=True)
    with c2:
        fig = go.Figure(go.Pie(labels=[f"{BANDERAS.get(p,'')} {p}" for p in por_pais["pais"]],
                               values=por_pais["ventas"], hole=0.58,
                               marker_colors=[PURPLE, PINK, CREAM], textinfo="label+percent"))
        st.plotly_chart(light(fig, 360, "Participación acumulada"), use_container_width=True)

    st.markdown(f"<p style='font-size:14px;font-weight:800;color:{PURPLE};margin:16px 0 8px'>"
                f"Salud de cada mercado, no solo su tamaño</p>", unsafe_allow_html=True)

    ent = d[d["estado"] == "Entregado"]
    filas = []
    for _, r in por_pais.iterrows():
        pais = r["pais"]
        sub_v = v[v["pais"] == pais]
        sub_d = ent[ent["pais"] == pais]
        primeros = sub_v["mes"].min()
        ultimos_3 = sub_v[sub_v["mes"] >= meses[-3]]["venta_cop"].sum()
        previos_3 = sub_v[(sub_v["mes"] >= meses[-6]) & (sub_v["mes"] < meses[-3])]["venta_cop"].sum()
        crec = (ultimos_3 - previos_3) / previos_3 * 100 if previos_3 else 0
        filas.append({
            "País": f"{BANDERAS.get(pais,'')} {pais}",
            "Ventas acumuladas": r["ventas"],
            "Participación %": round(r["part"], 1),
            "Margen %": round(r["margen_pct"], 1),
            "Crecimiento últ. trimestre %": round(crec, 1),
            "Ticket promedio": r["ventas"] / r["docs"] if r["docs"] else 0,
            "Costo logístico %": (sub_d["costo_logistico_cop"].sum() / sub_d["valor_cop"].sum() * 100
                                  if len(sub_d) and sub_d["valor_cop"].sum() else 0),
            "Entregas a tiempo %": (sub_d["entregado_a_tiempo"].mean() * 100
                                    if sub_d["entregado_a_tiempo"].notna().any() else 0),
            "Primer mes": primeros,
        })
    comp = pd.DataFrame(filas).sort_values("Ventas acumuladas", ascending=False)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        fig = go.Figure(go.Bar(x=comp["País"], y=comp["Margen %"],
                               marker_color=[GOOD if x >= 55 else WARN for x in comp["Margen %"]],
                               text=[f"{x:.0f}%" for x in comp["Margen %"]], textposition="outside"))
        st.plotly_chart(light(fig, 300, "Margen bruto por mercado"), use_container_width=True)
    with c4:
        fig = go.Figure(go.Bar(x=comp["País"], y=comp["Costo logístico %"],
                               marker_color=[GOOD if x < 4 else WARN if x < 8 else BAD
                                             for x in comp["Costo logístico %"]],
                               text=[f"{x:.1f}%" for x in comp["Costo logístico %"]],
                               textposition="outside"))
        st.plotly_chart(light(fig, 300, "Costo de entregar en cada mercado"), use_container_width=True)

    vista = comp.copy()
    vista["Ventas acumuladas"] = vista["Ventas acumuladas"].apply(lambda x: cop(x, 1))
    vista["Ticket promedio"] = vista["Ticket promedio"].apply(cop)
    vista["Costo logístico %"] = vista["Costo logístico %"].round(1)
    vista["Entregas a tiempo %"] = vista["Entregas a tiempo %"].round(1)
    st.dataframe(vista, hide_index=True, use_container_width=True)

    mejor_margen = comp.loc[comp["Margen %"].idxmax()]
    mayor_crec = comp.loc[comp["Crecimiento últ. trimestre %"].idxmax()]
    st.markdown(panel("Lectura de la expansión", f"""
    · <b>{mejor_margen['País']}</b> es el mercado con mejor margen ({mejor_margen['Margen %']:.0f}%):
      en Estados Unidos la marca vende directo por paranice.us, sin la comisión de una cadena de por medio,
      aunque el flete pesa mucho más.<br>
    · <b>{mayor_crec['País']}</b> es el que más crece en el último trimestre
      ({mayor_crec['Crecimiento últ. trimestre %']:+.0f}%).<br>
    · Colombia sigue financiando la expansión: cada punto de margen que se gana aquí es capital
      de trabajo para sostener el crecimiento afuera, donde el ciclo de caja es más largo.
    """, "🌎"), unsafe_allow_html=True)

    with st.expander("📦  Qué se vende en cada mercado", expanded=False):
        cat_pais = v.pivot_table(index="categoria", columns="pais", values="venta_cop", aggfunc="sum").fillna(0)
        cat_pct = cat_pais / cat_pais.sum() * 100
        fig = go.Figure(go.Heatmap(z=cat_pct.values, x=cat_pct.columns, y=cat_pct.index,
                                   colorscale=[[0, "#faf7fc"], [0.5, LAVENDER], [1, PURPLE]],
                                   text=cat_pct.round(1).values, texttemplate="%{text}%",
                                   hovertemplate="<b>%{y}</b> · %{x}<br>%{z:.1f}% de ese mercado<extra></extra>"))
        st.plotly_chart(light(fig, 320, "Peso de cada categoría dentro de cada mercado (%)"),
                        use_container_width=True)

        top_pais = v.groupby(["pais", "producto"])["venta_cop"].sum().reset_index()
        cols = st.columns(len(por_pais))
        for i, p in enumerate(sorted(v["pais"].unique())):
            sub = top_pais[top_pais["pais"] == p].nlargest(5, "venta_cop")
            with cols[i]:
                st.markdown(f"<b style='color:{PURPLE}'>{BANDERAS.get(p,'')} {p}</b>", unsafe_allow_html=True)
                vista = sub[["producto", "venta_cop"]].copy()
                vista["venta_cop"] = vista["venta_cop"].apply(lambda x: cop(x, 1))
                vista.columns = ["Producto", "Ventas"]
                st.dataframe(vista, hide_index=True, use_container_width=True)

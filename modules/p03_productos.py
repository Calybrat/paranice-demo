import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    p = pd.read_csv(DATA/"pedidos.csv")
    p["fecha"] = pd.to_datetime(p["fecha"])
    prod = pd.read_csv(DATA/"productos.csv")
    return p, prod

def render():
    p, prod = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Productos & Categorías</div>
        <div class="cb-sub">Catálogo, mezcla de ventas y márgenes · GranOLAs, Pancakes & Waffles, Avena & Harinas, Esparcibles, Combos, Merch</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    p26 = p[p["fecha"].dt.year == 2026]

    n_skus = prod["producto_id"].nunique()
    cat_top = p26.groupby("categoria")["total_cop"].sum().idxmax()
    margen_prom = p26["margen_pct"].mean() * 100

    p26_attrs = p26.merge(prod[["producto_id","sin_gluten","vegano"]], on="producto_id", how="left")
    total_p26 = p26_attrs["total_cop"].sum()
    pct_gf = p26_attrs.loc[p26_attrs["sin_gluten"] == True, "total_cop"].sum() / total_p26 * 100 if total_p26 else 0
    pct_vegano_v = p26_attrs.loc[p26_attrs["vegano"] == True, "total_cop"].sum() / total_p26 * 100 if total_p26 else 0
    prod_estrella = p26.groupby("producto")["total_cop"].sum().idxmax()

    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.markdown(kpi("SKUs activos", str(n_skus), "6 categorías", True, "🥣"), unsafe_allow_html=True)
    k2.markdown(kpi("Categoría líder", cat_top, "2026 YTD", True, "🏆"), unsafe_allow_html=True)
    k3.markdown(kpi("Margen bruto prom.", pct(margen_prom), "Meta: 60%", margen_prom >= 60, "📊"), unsafe_allow_html=True)
    k4.markdown(kpi("Ventas sin gluten", pct(pct_gf), "% del ingreso", pct_gf > 70, "🌾"), unsafe_allow_html=True)
    k5.markdown(kpi("Ventas veganas", pct(pct_vegano_v), "% del ingreso", pct_vegano_v > 60, "🌱"), unsafe_allow_html=True)
    k6.markdown(kpi("Producto estrella", prod_estrella, "2026 YTD", True, "⭐"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.4, 1], gap="medium")
    with c1:
        top = p26.groupby("producto")["total_cop"].sum().nlargest(15).reset_index().sort_values("total_cop")
        fig = go.Figure(go.Bar(x=top["total_cop"], y=top["producto"], orientation="h",
                                marker_color=GREEN,
                                hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
                                customdata=[cop(v,1) for v in top["total_cop"]]))
        st.plotly_chart(dark(fig, 420, "Top 15 productos · Ingresos 2026 YTD"), use_container_width=True)
    with c2:
        mg = p26.merge(prod[["producto_id","categoria"]].drop_duplicates(), on="producto_id", suffixes=("","_m"))
        mgc = p26.groupby("categoria")["margen_pct"].mean().sort_values(ascending=False) * 100
        fig = go.Figure(go.Bar(x=mgc.values, y=mgc.index, orientation="h",
                                marker_color=[GREEN if v >= 60 else AMBER for v in mgc.values],
                                hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>"))
        st.plotly_chart(dark(fig, 420, "Margen bruto por categoría"), use_container_width=True)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        pm = p.drop_duplicates(["pedido_id","producto_id"]).copy()
        pm["mes_p"] = pm["fecha"].dt.to_period("M").astype(str)
        piv = pm[pm["fecha"] >= "2025-06-01"].groupby(["mes_p","categoria"])["total_cop"].sum().reset_index()
        fig = go.Figure()
        for i, cat in enumerate(sorted(piv["categoria"].unique())):
            sub = piv[piv["categoria"] == cat]
            fig.add_trace(go.Scatter(x=sub["mes_p"], y=sub["total_cop"], name=cat, mode="lines",
                                      stackgroup="one", line=dict(width=0.5, color=PALETTE[i % len(PALETTE)])))
        st.plotly_chart(dark(fig, 320, "Evolución de ventas por categoría"), use_container_width=True)
    with c4:
        atributos = pd.DataFrame({
            "Atributo": ["Sin gluten","Vegano","Sin azúcar añadida"],
            "SKUs": [prod["sin_gluten"].sum(), prod["vegano"].sum(), prod["sin_azucar"].sum()],
        })
        fig = go.Figure(go.Bar(x=atributos["Atributo"], y=atributos["SKUs"],
                                marker_color=[GREEN, CREAM, CORAL],
                                text=atributos["SKUs"], textposition="outside"))
        st.plotly_chart(dark(fig, 320, "Catálogo por atributo saludable"), use_container_width=True)

    st.markdown(f"<p style='font-size:13px;font-weight:700;color:{TEXT};margin:16px 0 8px'>📋 Catálogo completo</p>", unsafe_allow_html=True)
    cat_df = prod.copy()
    cat_df["margen_pct"] = ((cat_df["precio_venta"] - cat_df["costo_unitario"]) / cat_df["precio_venta"] * 100).round(1)
    cat_df["precio_venta"] = cat_df["precio_venta"].apply(cop)
    cat_df["costo_unitario"] = cat_df["costo_unitario"].apply(cop)
    show_cols = ["producto_id","nombre","categoria","precio_venta","costo_unitario","margen_pct","sin_gluten","vegano","sin_azucar"]
    st.dataframe(cat_df[show_cols], hide_index=True, use_container_width=True)

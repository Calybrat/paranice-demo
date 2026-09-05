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
    c = pd.read_csv(DATA/"clientes.csv")
    e = pd.read_csv(DATA/"envios.csv")
    e["fecha_pedido"] = pd.to_datetime(e["fecha_pedido"])
    inv = pd.read_csv(DATA/"inventario.csv")
    prod = pd.read_csv(DATA/"produccion.csv")
    m = pd.read_csv(DATA/"marketing.csv")
    return p, c, e, inv, prod, m

def render():
    p, c, e, inv, prod, m = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Paranice · Dashboard General</div>
        <div class="cb-sub">Alimentos saludables sin gluten · Colombia · Costa Rica · Estados Unidos · Resumen ejecutivo · 31 de agosto 2026</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    # ── Filters ────────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        periodo = st.selectbox("Período", ["Últimos 30 días","Últimos 60 días","Últimos 90 días","2026 (YTD)","2025 completo"], key="db_per")
    with col_f2:
        paises_all = ["Todos"] + sorted(p["pais"].unique().tolist())
        pais_sel  = st.selectbox("País", paises_all, key="db_pais")
    with col_f3:
        cats_all = ["Todas"] + sorted(p["categoria"].unique().tolist())
        cat_sel  = st.selectbox("Categoría", cats_all, key="db_cat")

    cutoff = {"Últimos 30 días": 30, "Últimos 60 días": 60, "Últimos 90 días": 90}.get(periodo)
    ref_date = pd.Timestamp("2026-08-31")
    if cutoff:
        pf = p[p["fecha"] >= ref_date - pd.Timedelta(days=cutoff)]
        pp = p[(p["fecha"] >= ref_date - pd.Timedelta(days=cutoff*2)) &
               (p["fecha"] < ref_date - pd.Timedelta(days=cutoff))]
    elif periodo == "2026 (YTD)":
        pf = p[p["fecha"].dt.year == 2026]
        pp = p[p["fecha"].dt.year == 2025]
    else:
        pf = p[p["fecha"].dt.year == 2025]
        pp = pd.DataFrame(columns=p.columns)

    if pais_sel != "Todos":
        pf = pf[pf["pais"] == pais_sel]; pp = pp[pp["pais"] == pais_sel]
    if cat_sel != "Todas":
        pf = pf[pf["categoria"] == cat_sel]; pp = pp[pp["categoria"] == cat_sel]

    ventas_act = pf["total_cop"].sum()
    ventas_ant = pp["total_cop"].sum()
    delta_v    = (ventas_act - ventas_ant) / ventas_ant * 100 if ventas_ant else 0

    n_pedidos  = pf["pedido_id"].nunique()
    aov        = ventas_act / n_pedidos if n_pedidos else 0
    clientes_act = pf["cliente_id"].nunique()
    margen_avg   = pf["margen_pct"].mean() * 100 if len(pf) else 0

    pct_recompra = c["cliente_recurrente"].mean() * 100 if len(c) else 0

    m_paid = m[m["canal"] != "Orgánico/SEO"]
    roas_blended = m_paid["ingresos_atribuidos_cop"].sum() / m_paid["inversion_cop"].sum() if m_paid["inversion_cop"].sum() else 0

    ent = e[e["estado"] == "Entregado"]
    otd = (ent["entregado_a_tiempo"] == True).sum() / len(ent) * 100 if len(ent) else 0

    inv_critico = inv[inv["estado"] == "Crítico"].shape[0]
    inv_bajo    = inv[inv["estado"] == "Bajo"].shape[0]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    k1.markdown(kpi("Ventas período", cop(ventas_act, 1),
        f"{'▲' if delta_v>=0 else '▼'} {abs(delta_v):.1f}% vs anterior", delta_v >= 0, "💰"), unsafe_allow_html=True)
    k2.markdown(kpi("Ticket promedio", cop(aov), f"{n_pedidos:,} pedidos", True, "🛒"), unsafe_allow_html=True)
    k3.markdown(kpi("Clientes activos", str(clientes_act), "", True, "🧑‍🤝‍🧑"), unsafe_allow_html=True)
    k4.markdown(kpi("Tasa de recompra", pct(pct_recompra), "Histórico", pct_recompra > 40, "🔁"), unsafe_allow_html=True)
    k5.markdown(kpi("ROAS marketing", f"{roas_blended:.1f}x", "Canales pagos", roas_blended >= 3, "📣"), unsafe_allow_html=True)
    k6.markdown(kpi("OTD envíos", pct(otd), f"Meta: 90%", otd >= 90, "🚚"), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ── Row 1: Ventas mensual + por país ─────────────────────────────────────
    c1, c2 = st.columns([1.6, 1], gap="medium")

    with c1:
        pm = p[p["fecha"].dt.year.isin([2025, 2026])].drop_duplicates("pedido_id").copy()
        pm["mes_p"] = pm["fecha"].dt.to_period("M").astype(str)
        vm_agg = pm.groupby("mes_p")["total_cop"].sum().reset_index().sort_values("mes_p")
        fig = go.Figure()
        colors = [GREEN if mo.startswith("2025") else CREAM for mo in vm_agg["mes_p"]]
        fig.add_trace(go.Bar(
            x=vm_agg["mes_p"], y=vm_agg["total_cop"],
            marker_color=colors, name="Ventas",
            hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v, 1) for v in vm_agg["total_cop"]],
        ))
        fig.add_trace(go.Scatter(
            x=vm_agg["mes_p"], y=vm_agg["total_cop"].rolling(3, min_periods=1).mean(),
            mode="lines", line=dict(color=CORAL, width=2, dash="dot"),
            name="Media 3 meses",
        ))
        st.plotly_chart(dark(fig, 320, "Ventas mensuales · 2025–2026 (COP)"), use_container_width=True)

    with c2:
        vs = pf.groupby("pais")["total_cop"].sum().reset_index().sort_values("total_cop", ascending=True)
        fig = go.Figure(go.Bar(
            x=vs["total_cop"], y=vs["pais"], orientation="h",
            marker=dict(color=PALETTE[:len(vs)]),
            hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v, 1) for v in vs["total_cop"]],
        ))
        st.plotly_chart(dark(fig, 320, "Ventas por país"), use_container_width=True)

    # ── Row 2: Categorías + Canales + Recompra ───────────────────────────────
    c3, c4, c5 = st.columns(3, gap="medium")

    with c3:
        vc = pf.groupby("categoria")["total_cop"].sum().reset_index().sort_values("total_cop", ascending=False)
        fig = go.Figure(go.Pie(
            labels=vc["categoria"], values=vc["total_cop"],
            hole=0.52, marker_colors=PALETTE,
            textinfo="label+percent", textfont_size=11,
            hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v, 1) for v in vc["total_cop"]],
        ))
        st.plotly_chart(dark(fig, 300, "Ventas por categoría"), use_container_width=True)

    with c4:
        vcan = pf.groupby("canal")["total_cop"].sum().nlargest(6).reset_index().sort_values("total_cop")
        fig = go.Figure(go.Bar(
            x=vcan["total_cop"], y=vcan["canal"], orientation="h",
            marker_color=CREAM,
            hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
            customdata=[cop(v, 1) for v in vcan["total_cop"]],
        ))
        st.plotly_chart(dark(fig, 300, "Ventas por canal de adquisición"), use_container_width=True)

    with c5:
        seg = c["segmento"].value_counts().reindex(["VIP","Recurrente","Compra única"]).fillna(0)
        fig = go.Figure(go.Bar(
            x=seg.index, y=seg.values,
            marker_color=[CORAL, GREEN, MUTED],
        ))
        st.plotly_chart(dark(fig, 300, "Clientes por segmento"), use_container_width=True)

    # ── Alertas ───────────────────────────────────────────────────────────────
    st.markdown(f"<div style='height:8px'></div>", unsafe_allow_html=True)
    with st.expander("⚠️  Alertas del sistema", expanded=True):
        a1, a2, a3 = st.columns(3)
        criticos = inv[inv["estado"] == "Crítico"][["bodega","producto","stock_actual","stock_minimo"]].head(5)
        rechazos = prod[prod["estado_calidad"].isin(["Rechazado","Cuarentena"])].sort_values("fecha_produccion", ascending=False)[
            ["lote_id","producto","resultado_gluten_ppm","estado_calidad"]].head(5)
        env_retrasados = e[(e["estado"]=="En tránsito") &
                            (e["fecha_pedido"] < ref_date - pd.Timedelta(days=7))][["pedido_id","ciudad_destino","transportadora"]].head(5)
        with a1:
            st.markdown(f"<span style='color:{RED};font-weight:700'>📦 Stock crítico ({len(criticos)} SKUs)</span>", unsafe_allow_html=True)
            st.dataframe(criticos, hide_index=True, use_container_width=True)
        with a2:
            st.markdown(f"<span style='color:{AMBER};font-weight:700'>🧪 Lotes en cuarentena/rechazo ({len(rechazos)})</span>", unsafe_allow_html=True)
            st.dataframe(rechazos, hide_index=True, use_container_width=True)
        with a3:
            st.markdown(f"<span style='color:{AMBER};font-weight:700'>🚚 Envíos demorados ({len(env_retrasados)})</span>", unsafe_allow_html=True)
            st.dataframe(env_retrasados, hide_index=True, use_container_width=True)

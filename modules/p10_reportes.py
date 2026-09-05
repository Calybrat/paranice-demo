import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

@st.cache_data
def load():
    p = pd.read_csv(DATA/"pedidos.csv")
    p["fecha"] = pd.to_datetime(p["fecha"])
    c = pd.read_csv(DATA/"clientes.csv")
    inv = pd.read_csv(DATA/"inventario.csv")
    prod = pd.read_csv(DATA/"produccion.csv")
    prod["fecha_produccion"] = pd.to_datetime(prod["fecha_produccion"])
    e = pd.read_csv(DATA/"envios.csv")
    m = pd.read_csv(DATA/"marketing.csv")
    g = pd.read_csv(DATA/"paises_mensual.csv")
    g["periodo"] = pd.to_datetime(g["periodo"])
    return p, c, inv, prod, e, m, g

HOY = date(2026, 8, 31)
HOY_STR = "31 de agosto de 2026"

STYLE = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  * {{ box-sizing:border-box; margin:0; padding:0 }}
  body {{ font-family:'Inter',Arial,sans-serif; background:#fff; color:#12210f; font-size:13px; line-height:1.5 }}
  .rpt-page {{ max-width:900px; margin:0 auto; padding:32px }}
  .rpt-header {{ display:flex; align-items:center; gap:16px; padding-bottom:20px;
    border-bottom:3px solid #4d9a5c; margin-bottom:24px }}
  .rpt-logo {{ width:48px; height:48px; border-radius:12px;
    background:linear-gradient(135deg,#4d9a5c,#e8c07d);
    display:flex; align-items:center; justify-content:center;
    font-size:24px; font-weight:900; color:#12210f }}
  .rpt-company {{ flex:1 }}
  .rpt-company h1 {{ font-size:22px; font-weight:800; color:#12210f }}
  .rpt-company p {{ font-size:12px; color:#7d8f79; margin-top:2px }}
  .rpt-meta {{ text-align:right; font-size:11px; color:#7d8f79 }}
  .rpt-meta strong {{ color:#4d9a5c; font-size:14px; display:block; margin-bottom:2px }}
  .rpt-title {{ font-size:18px; font-weight:800; color:#4d9a5c;
    margin:0 0 20px; padding:12px 16px; background:#f2f8f0;
    border-left:4px solid #4d9a5c; border-radius:0 8px 8px 0 }}
  .kpi-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:24px }}
  .kpi-box {{ background:#f7faf5; border:1px solid #e2ecdd; border-radius:10px; padding:16px }}
  .kpi-label {{ font-size:10px; text-transform:uppercase; letter-spacing:.08em; color:#7d8f79; margin-bottom:6px }}
  .kpi-val {{ font-size:22px; font-weight:800; color:#12210f; line-height:1 }}
  .kpi-delta {{ font-size:11px; margin-top:4px }}
  .kpi-good {{ color:#22c55e }} .kpi-bad {{ color:#ef4444 }}
  .section-title {{ font-size:13px; font-weight:700; color:#4d9a5c; margin:20px 0 10px;
    text-transform:uppercase; letter-spacing:.06em }}
  table {{ width:100%; border-collapse:collapse; font-size:12px; margin-bottom:16px }}
  thead th {{ background:#4d9a5c; color:#fff; padding:8px 10px; text-align:left;
    font-size:11px; font-weight:600; letter-spacing:.04em }}
  tbody tr:nth-child(even) td {{ background:#f7faf5 }}
  tbody td {{ padding:7px 10px; border-bottom:1px solid #eef4ec }}
  .tag-red {{ background:#fef2f2; color:#ef4444; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:600 }}
  .tag-amber {{ background:#fffbeb; color:#f59e0b; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:600 }}
  .tag-green {{ background:#f0fdf4; color:#22c55e; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:600 }}
  .tag-blue {{ background:#eff6ff; color:#3b82f6; padding:2px 8px; border-radius:99px; font-size:10px; font-weight:600 }}
  .alert-box {{ background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:14px 16px; margin-bottom:16px }}
  .alert-box h4 {{ color:#ef4444; font-size:12px; margin-bottom:8px }}
  .rpt-footer {{ margin-top:32px; padding-top:16px; border-top:1px solid #eef4ec;
    display:flex; justify-content:space-between; font-size:10px; color:#a8b8a4 }}
  .print-note {{ background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px;
    padding:10px 14px; margin-bottom:20px; font-size:11px; color:#166534 }}
  @media print {{
    .print-note {{ display:none }}
    body {{ font-size:12px }}
    .rpt-page {{ padding:16px }}
  }}
</style>"""

HEADER_HTML = f"""
<div class="rpt-header">
  <div class="rpt-logo">P</div>
  <div class="rpt-company">
    <h1>Paranice</h1>
    <p>Alimentos saludables sin gluten · Colombia · Costa Rica · Estados Unidos</p>
  </div>
  <div class="rpt-meta">
    <strong>Panel de Inteligencia de Negocios</strong>
    Generado: {HOY_STR}<br>
    <span style="color:#e8c07d;font-size:10px">Powered by Calybrat</span>
  </div>
</div>"""

FOOTER_HTML = """
<div class="rpt-footer">
  <span>Paranice · Confidencial</span>
  <span>Generado automáticamente por Calybrat BI · 2026</span>
</div>"""

def kpi_box(label, val, delta="", good=True):
    d = f'<div class="kpi-delta {"kpi-good" if good else "kpi-bad"}">{delta}</div>' if delta else ""
    return f'<div class="kpi-box"><div class="kpi-label">{label}</div><div class="kpi-val">{val}</div>{d}</div>'

def tag(text, color="blue"):
    return f'<span class="tag-{color}">{text}</span>'


def build_ejecutivo(p, c, inv, prod, e, m, g):
    p26 = p[p["fecha"].dt.year == 2026]
    p25 = p[p["fecha"].dt.year == 2025]
    total26 = p26["total_cop"].sum(); total25 = p25["total_cop"].sum()
    crecimiento = (total26 - total25) / total25 * 100 if total25 else 0
    margen = p26["margen_pct"].mean()*100 if len(p26) else 0
    pct_recompra = c["cliente_recurrente"].mean()*100
    ent = e[e["estado"]=="Entregado"]
    otd = (ent["entregado_a_tiempo"]==True).mean()*100 if len(ent) else 0
    m_paid = m[m["canal"]!="Orgánico/SEO"]
    roas = m_paid["ingresos_atribuidos_cop"].sum()/m_paid["inversion_cop"].sum() if m_paid["inversion_cop"].sum() else 0

    ventas_mes = p26.drop_duplicates("pedido_id").groupby(p26.drop_duplicates("pedido_id")["fecha"].dt.to_period("M").astype(str))["total_cop"].sum().tail(3)
    ventas_tabla = "".join([f"<tr><td>{mo}</td><td style='text-align:right'>{cop(s,1)}</td></tr>" for mo,s in ventas_mes.items()])

    top_prod = p26.groupby("producto")["total_cop"].sum().nlargest(5).reset_index()
    prod_tabla = "".join([f"<tr><td>{r['producto']}</td><td style='text-align:right'>{cop(r['total_cop'],1)}</td></tr>" for _,r in top_prod.iterrows()])

    por_pais = g.groupby("pais")["ventas_cop"].sum().sort_values(ascending=False)
    pais_tabla = "".join([f"<tr><td>{pa}</td><td style='text-align:right'>{cop(v,1)}</td><td style='text-align:right'>{v/por_pais.sum()*100:.1f}%</td></tr>" for pa,v in por_pais.items()])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte Ejecutivo Mensual — Paranice</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">📊 Reporte Ejecutivo Mensual — Agosto 2026</div>

      <div class="kpi-grid">
        {kpi_box("Ventas 2026 YTD", cop(total26,1), f"{'▲' if crecimiento>=0 else '▼'} {abs(crecimiento):.1f}% vs 2025", crecimiento>=0)}
        {kpi_box("Margen bruto", pct(margen), "Meta: 60%", margen>=60)}
        {kpi_box("Tasa de recompra", pct(pct_recompra), "Clientes con ≥2 pedidos", pct_recompra>40)}
        {kpi_box("Clientes totales", f"{len(c):,}", "Con al menos 1 compra", True)}
        {kpi_box("OTD envíos", pct(otd), "Meta: 90%", otd>=90)}
        {kpi_box("ROAS marketing", f"{roas:.1f}x", "Canales pagos", roas>=3)}
      </div>

      <div class="section-title">Ventas últimos 3 meses</div>
      <table><thead><tr><th>Período</th><th style="text-align:right">Ventas COP</th></tr></thead>
      <tbody>{ventas_tabla}</tbody></table>

      <div class="section-title">Top 5 productos 2026 YTD</div>
      <table><thead><tr><th>Producto</th><th style="text-align:right">Ventas COP</th></tr></thead>
      <tbody>{prod_tabla}</tbody></table>

      <div class="section-title">Ventas por país (acumulado)</div>
      <table><thead><tr><th>País</th><th style="text-align:right">Ventas COP</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{pais_tabla}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def build_ventas(p, pais_sel, cat_sel):
    df = p[p["fecha"].dt.year == 2026].copy()
    if pais_sel != "Todos": df = df[df["pais"] == pais_sel]
    if cat_sel  != "Todas": df = df[df["categoria"] == cat_sel]

    total = df["total_cop"].sum()
    n_ped = df["pedido_id"].nunique()
    ticket = total / n_ped if n_ped else 0
    margen = df["margen_pct"].mean()*100 if len(df) else 0

    top_prod = df.groupby(["producto","categoria"])["total_cop"].sum().nlargest(10).reset_index()
    rows_prod = "".join([
        f"<tr><td>{r['producto']}</td><td>{r['categoria']}</td>"
        f"<td style='text-align:right'>{cop(r['total_cop'],1)}</td>"
        f"<td style='text-align:right'>{r['total_cop']/total*100:.1f}%</td></tr>"
        for _,r in top_prod.iterrows()])

    canal_det = df.drop_duplicates("pedido_id").groupby("canal").agg(ventas=("total_cop","sum"),pedidos=("pedido_id","count")).reset_index().sort_values("ventas",ascending=False)
    rows_canal = "".join([f"<tr><td>{r['canal']}</td><td style='text-align:right'>{cop(r['ventas'],1)}</td><td style='text-align:right'>{int(r['pedidos'])}</td><td style='text-align:right'>{r['ventas']/total*100:.1f}%</td></tr>" for _,r in canal_det.iterrows()])

    filtros = f"País: {pais_sel} · Categoría: {cat_sel}"
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte de Ventas — Paranice</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">💰 Reporte de Ventas y E-commerce — 2026 YTD</div>
      <p style="font-size:11px;color:#7d8f79;margin-bottom:16px">Filtros: {filtros}</p>
      <div class="kpi-grid">
        {kpi_box("Ventas totales", cop(total,1), "", True)}
        {kpi_box("Pedidos", f"{n_ped:,}", "", True)}
        {kpi_box("Ticket promedio", cop(ticket), "", True)}
        {kpi_box("Margen bruto prom", pct(margen), "Meta: 60%", margen>=60)}
        {kpi_box("Líneas de producto", f"{len(df):,}", "", True)}
        {kpi_box("Categorías activas", str(df['categoria'].nunique()), "", True)}
      </div>
      <div class="section-title">Top 10 productos por ingresos</div>
      <table><thead><tr><th>Producto</th><th>Categoría</th><th style="text-align:right">Ventas COP</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{rows_prod}</tbody></table>
      <div class="section-title">Detalle por canal</div>
      <table><thead><tr><th>Canal</th><th style="text-align:right">Ventas COP</th><th style="text-align:right">Pedidos</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{rows_canal}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def build_clientes(c):
    total = len(c)
    pct_rec = c["cliente_recurrente"].mean()*100
    seg = c["segmento"].value_counts()
    rows_seg = "".join([f"<tr><td>{s}</td><td style='text-align:right'>{n:,}</td><td style='text-align:right'>{n/total*100:.1f}%</td></tr>" for s,n in seg.items()])

    ltv_pais = c.groupby("pais")["ltv_cop"].mean().sort_values(ascending=False)
    rows_pais = "".join([f"<tr><td>{pa}</td><td style='text-align:right'>{cop(v)}</td></tr>" for pa,v in ltv_pais.items()])

    top_ciudad = c.groupby("ciudad").size().nlargest(10).reset_index(name="clientes")
    rows_ciudad = "".join([f"<tr><td>{r['ciudad']}</td><td style='text-align:right'>{int(r['clientes'])}</td></tr>" for _,r in top_ciudad.iterrows()])

    promotores = (c["nps_score"]>=9).mean()*100
    detractores = (c["nps_score"]<=6).mean()*100
    nps_neto = promotores - detractores

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte de Clientes — Paranice</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">🧑‍🤝‍🧑 Reporte de Clientes y Retención — {HOY_STR}</div>
      <div class="kpi-grid">
        {kpi_box("Clientes totales", f"{total:,}", "", True)}
        {kpi_box("Tasa de recompra", pct(pct_rec), "Meta: >40%", pct_rec>40)}
        {kpi_box("LTV promedio", cop(c['ltv_cop'].mean()), "", True)}
        {kpi_box("NPS neto", f"{nps_neto:.0f}", "Promotores - detractores", nps_neto>=30)}
        {kpi_box("NPS promedio", f"{c['nps_score'].mean():.1f}/10", "", c['nps_score'].mean()>=7)}
        {kpi_box("Clientes VIP", f"{(c['segmento']=='VIP').sum():,}", "Top 20% LTV", True)}
      </div>
      <div class="section-title">Clientes por segmento</div>
      <table><thead><tr><th>Segmento</th><th style="text-align:right">Clientes</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{rows_seg}</tbody></table>
      <div class="section-title">LTV promedio por país</div>
      <table><thead><tr><th>País</th><th style="text-align:right">LTV COP</th></tr></thead>
      <tbody>{rows_pais}</tbody></table>
      <div class="section-title">Top 10 ciudades por clientes</div>
      <table><thead><tr><th>Ciudad</th><th style="text-align:right">Clientes</th></tr></thead>
      <tbody>{rows_ciudad}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def build_inventario(inv, prod):
    crit = inv[inv["estado"]=="Crítico"].sort_values("stock_actual")
    bajos = inv[inv["estado"]=="Bajo"].sort_values("dias_cobertura")
    total_val = inv["valor_inventario"].sum()
    tasa_qc = (prod["estado_calidad"]=="Aprobado").mean()*100

    rows_crit = "".join([
        f"<tr><td>{r['producto']}</td><td>{r['bodega']}</td>"
        f"<td style='text-align:right;font-weight:700;color:#ef4444'>{r['stock_actual']:.0f}</td>"
        f"<td style='text-align:right'>{r['stock_minimo']:.0f}</td>"
        f"<td style='text-align:right'>{r['dias_cobertura']:.0f}</td>"
        f"<td>{tag('CRÍTICO','red')}</td></tr>"
        for _,r in crit.head(15).iterrows()])

    lotes_qc = prod[prod["estado_calidad"]!="Aprobado"].sort_values("fecha_produccion", ascending=False).head(10)
    rows_qc = "".join([
        f"<tr><td>{r['lote_id']}</td><td>{r['producto']}</td>"
        f"<td style='text-align:right'>{r['resultado_gluten_ppm']:.1f} ppm</td>"
        f"<td>{tag(r['estado_calidad'], 'red' if r['estado_calidad']=='Rechazado' else 'amber')}</td></tr>"
        for _,r in lotes_qc.iterrows()])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte de Inventario y Calidad — Paranice</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">📦 Reporte de Inventario y Control de Calidad — {HOY_STR}</div>
      <div class="kpi-grid">
        {kpi_box("Valor total inventario", cop(total_val,1), "3 bodegas", True)}
        {kpi_box("SKUs críticos", str(len(crit)), "Reabastecer con urgencia", len(crit)==0)}
        {kpi_box("SKUs en nivel bajo", str(len(bajos)), "", len(bajos)==0)}
        {kpi_box("Cobertura prom.", f"{inv['dias_cobertura'].mean():.0f} días", "", True)}
        {kpi_box("Tasa aprobación QC", pct(tasa_qc), "Meta: ≥97%", tasa_qc>=97)}
        {kpi_box("Lotes en cuarentena/rechazo", str((prod['estado_calidad']!='Aprobado').sum()), "Histórico", False)}
      </div>
      <div class="alert-box">
        <h4>⚠️ Acción requerida: {len(crit)} SKUs por debajo del mínimo</h4>
        <p>Se recomienda emitir órdenes de compra a los proveedores correspondientes de forma inmediata.</p>
      </div>
      <div class="section-title">SKUs en estado CRÍTICO</div>
      <table><thead><tr><th>Producto</th><th>Bodega</th><th style="text-align:right">Stock</th><th style="text-align:right">Mínimo</th><th style="text-align:right">Cobertura (d)</th><th>Estado</th></tr></thead>
      <tbody>{rows_crit}</tbody></table>
      <div class="section-title">Lotes en cuarentena o rechazados (últimos 10)</div>
      <table><thead><tr><th>Lote</th><th>Producto</th><th style="text-align:right">Resultado</th><th>Estado</th></tr></thead>
      <tbody>{rows_qc}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def build_expansion(g):
    por_pais = g.groupby("pais")["ventas_cop"].sum().sort_values(ascending=False)
    grand_total = por_pais.sum()
    rows_pais = "".join([f"<tr><td>{pa}</td><td style='text-align:right'>{cop(v,1)}</td><td style='text-align:right'>{v/grand_total*100:.1f}%</td></tr>" for pa,v in por_pais.items()])

    ultimo = g["periodo"].max()
    comp = g[g["periodo"]>=ultimo - pd.DateOffset(months=2)].groupby("pais").agg(
        ventas=("ventas_cop","sum"), pedidos=("pedidos","sum"), ticket=("ticket_promedio_cop","mean")).reset_index()
    rows_comp = "".join([
        f"<tr><td>{r['pais']}</td><td style='text-align:right'>{cop(r['ventas'],1)}</td>"
        f"<td style='text-align:right'>{int(r['pedidos'])}</td><td style='text-align:right'>{cop(r['ticket'])}</td></tr>"
        for _,r in comp.iterrows()])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>Reporte de Expansión Internacional — Paranice</title>{STYLE}</head><body>
    <div class="rpt-page">
      <div class="print-note">💡 Para guardar como PDF: <strong>Ctrl+P → Guardar como PDF</strong></div>
      {HEADER_HTML}
      <div class="rpt-title">🌎 Reporte de Expansión Internacional — {HOY_STR}</div>
      <div class="kpi-grid">
        {kpi_box("Mercados activos", "3", "Colombia · Costa Rica · Estados Unidos", True)}
        {kpi_box("Ventas consolidadas", cop(grand_total,1), "Acumulado", True)}
        {kpi_box("Part. Colombia", pct(por_pais.get('Colombia',0)/grand_total*100), "", True)}
        {kpi_box("Part. Costa Rica", pct(por_pais.get('Costa Rica',0)/grand_total*100), "Lanzado abr-2025", True)}
        {kpi_box("Part. Estados Unidos", pct(por_pais.get('Estados Unidos',0)/grand_total*100), "Lanzado oct-2025", True)}
        {kpi_box("Países en rampa", "2", "Costa Rica y EEUU", True)}
      </div>
      <div class="section-title">Participación de ingresos por país</div>
      <table><thead><tr><th>País</th><th style="text-align:right">Ventas COP</th><th style="text-align:right">Part. %</th></tr></thead>
      <tbody>{rows_pais}</tbody></table>
      <div class="section-title">Comparativo últimos 3 meses</div>
      <table><thead><tr><th>País</th><th style="text-align:right">Ventas</th><th style="text-align:right">Pedidos</th><th style="text-align:right">Ticket prom.</th></tr></thead>
      <tbody>{rows_comp}</tbody></table>
      {FOOTER_HTML}
    </div></body></html>"""


def render():
    p, c, inv, prod, e, m, g = load()
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Reportes Automáticos</div>
        <div class="cb-sub">Templates listos para descargar · Imprimir → Guardar como PDF</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:12px;padding:16px 20px;margin-bottom:20px">
      <p style="font-size:13px;font-weight:600;color:{TEXT};margin:0 0 8px">📄 Cómo descargar como PDF</p>
      <p style="font-size:12px;color:{MUTED};margin:0;line-height:1.7">
        1. Haz clic en <strong style="color:{GREEN}">Descargar reporte</strong> para obtener el archivo HTML.<br>
        2. Abre el archivo descargado en tu navegador.<br>
        3. Presiona <strong>Ctrl+P</strong> (Windows) o <strong>Cmd+P</strong> (Mac).<br>
        4. En "Destino", selecciona <strong>"Guardar como PDF"</strong> y haz clic en Guardar.
      </p>
    </div>""", unsafe_allow_html=True)

    TEMPLATES = {
        "📊 Reporte Ejecutivo Mensual":     "Resumen general: ventas, recompra, OTD, ROAS y expansión. Ideal para fundadores.",
        "💰 Reporte de Ventas y E-commerce":"Análisis por país, canal y producto con top 10 productos.",
        "🧑‍🤝‍🧑 Reporte de Clientes y Retención":"Segmentación, LTV, NPS y ciudades top.",
        "📦 Reporte de Inventario y Calidad":"Stock crítico por bodega y trazabilidad de control de calidad (ppm gluten).",
        "🌎 Reporte de Expansión Internacional":"Colombia, Costa Rica y Estados Unidos — comparativo de tracción.",
    }

    for i, (nombre, desc) in enumerate(TEMPLATES.items()):
        with st.expander(nombre, expanded=(i==0)):
            col_info, col_btn = st.columns([3,1])
            with col_info:
                st.markdown(f"<p style='color:{MUTED};font-size:13px;margin:4px 0 12px'>{desc}</p>", unsafe_allow_html=True)

            if "Ventas" in nombre:
                cc1,cc2 = st.columns(2)
                with cc1:
                    paises = ["Todos"] + sorted(p["pais"].unique().tolist())
                    pais_sel = st.selectbox("País", paises, key=f"rpt_pais_{i}")
                with cc2:
                    cats = ["Todas"] + sorted(p["categoria"].unique().tolist())
                    cat_sel = st.selectbox("Categoría", cats, key=f"rpt_cat_{i}")
            else:
                pais_sel = "Todos"; cat_sel = "Todas"

            if "Ejecutivo" in nombre:
                html = build_ejecutivo(p, c, inv, prod, e, m, g)
                fname = "paranice_reporte_ejecutivo.html"
            elif "Ventas" in nombre:
                html = build_ventas(p, pais_sel, cat_sel)
                fname = "paranice_reporte_ventas.html"
            elif "Clientes" in nombre:
                html = build_clientes(c)
                fname = "paranice_reporte_clientes.html"
            elif "Inventario" in nombre:
                html = build_inventario(inv, prod)
                fname = "paranice_reporte_inventario.html"
            else:
                html = build_expansion(g)
                fname = "paranice_reporte_expansion.html"

            st.markdown(_preview(nombre, p, c, inv, prod, e, m, g), unsafe_allow_html=True)

            with col_btn:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                st.download_button(
                    label="⬇️ Descargar reporte",
                    data=html.encode("utf-8"),
                    file_name=fname,
                    mime="text/html",
                    key=f"dl_{i}",
                    use_container_width=True,
                )


def _preview(nombre, p, c, inv, prod, e, m, g):
    p26 = p[p["fecha"].dt.year==2026]
    if "Ejecutivo" in nombre or "Ventas" in nombre:
        total = p26["total_cop"].sum()
        mg = p26["margen_pct"].mean()*100
        n_cli = p26["cliente_id"].nunique()
        items = [("Ventas 2026 YTD", cop(total,1)), ("Margen", pct(mg)), ("Clientes activos", str(n_cli))]
    elif "Clientes" in nombre:
        items = [("Total clientes", f"{len(c):,}"), ("Recompra", pct(c['cliente_recurrente'].mean()*100)), ("LTV prom.", cop(c['ltv_cop'].mean()))]
    elif "Inventario" in nombre:
        crit = (inv["estado"]=="Crítico").sum(); bajo = (inv["estado"]=="Bajo").sum()
        items = [("Valor total", cop(inv["valor_inventario"].sum(),1)), ("Críticos", str(crit)), ("Bajos", str(bajo))]
    else:
        grand = g["ventas_cop"].sum()
        items = [("Ventas consolidadas", cop(grand,1)), ("Mercados", "3"), ("País líder", g.groupby('pais')['ventas_cop'].sum().idxmax())]

    boxes = "".join([f'<div style="background:{SURF2};border:1px solid {BORDER};border-radius:8px;padding:10px 14px;flex:1">'
                     f'<div style="font-size:10px;color:{MUTED};text-transform:uppercase;letter-spacing:.06em">{lab}</div>'
                     f'<div style="font-size:18px;font-weight:800;color:{TEXT};margin-top:4px">{val}</div></div>'
                     for lab,val in items])
    return f'<div style="display:flex;gap:10px;margin:8px 0 4px">{boxes}</div>'

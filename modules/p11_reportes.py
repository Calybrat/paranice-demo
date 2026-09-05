import streamlit as st
import pandas as pd
from datetime import date
from utils.formatters import *
from utils import datos

HOY_STR = "31 de agosto de 2026"


def load():
    return (datos.ventas(), datos.finanzas(), datos.clientes(), datos.cartera(),
            datos.sellout(), datos.despachos(), datos.produccion(), datos.marketing())


STYLE = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
  * {{ box-sizing:border-box; margin:0; padding:0 }}
  body {{ font-family:'Nunito',Arial,sans-serif; background:#fff; color:{PURPLE}; font-size:13px; line-height:1.55 }}
  .pg {{ max-width:920px; margin:0 auto; padding:34px }}
  .hd {{ display:flex; align-items:center; gap:16px; padding-bottom:18px;
        border-bottom:3px solid {PURPLE}; margin-bottom:22px }}
  .hd img {{ height:38px }}
  .hd .meta {{ margin-left:auto; text-align:right; font-size:11px; color:#8b83a3 }}
  .hd .meta strong {{ color:{PURPLE}; font-size:13px; display:block }}
  .ttl {{ font-size:19px; font-weight:900; color:{PURPLE}; margin:0 0 18px;
         padding:12px 16px; background:{LAVENDER_BG}; border-left:5px solid {PINK}; border-radius:0 10px 10px 0 }}
  .kpis {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:22px }}
  .kpi {{ background:#faf8fd; border:1px solid {BORDER}; border-radius:12px; padding:14px }}
  .kpi .l {{ font-size:9.5px; text-transform:uppercase; letter-spacing:.08em; color:#8b83a3; font-weight:800 }}
  .kpi .v {{ font-size:21px; font-weight:900; color:{PURPLE}; line-height:1.15; margin-top:4px }}
  .kpi .d {{ font-size:10.5px; margin-top:3px; font-weight:700 }}
  .ok {{ color:{GOOD} }} .bad {{ color:{BAD} }}
  h3 {{ font-size:12px; font-weight:900; color:{PINK}; margin:20px 0 8px;
       text-transform:uppercase; letter-spacing:.07em }}
  table {{ width:100%; border-collapse:collapse; font-size:11.5px; margin-bottom:14px }}
  thead th {{ background:{PURPLE}; color:#fff; padding:8px 10px; text-align:left; font-size:10.5px; font-weight:800 }}
  tbody td {{ padding:7px 10px; border-bottom:1px solid #eee8f5 }}
  tbody tr:nth-child(even) td {{ background:#faf8fd }}
  .note {{ background:{PINK_LT}; border:1px solid {PINK}; border-radius:10px; padding:12px 14px;
          margin-bottom:16px; font-size:11.5px }}
  .print {{ background:#eef7f1; border:1px solid #bfe3ce; border-radius:10px; padding:10px 14px;
           margin-bottom:18px; font-size:11px; color:#1f6b45 }}
  .ft {{ margin-top:28px; padding-top:14px; border-top:1px solid #eee8f5; display:flex;
        justify-content:space-between; font-size:10px; color:#a89fbd }}
  @media print {{ .print {{ display:none }} .pg {{ padding:12px }} }}
</style>"""


def _hd():
    logo = asset_b64("logo_horizontal_morado.png")
    img = f'<img src="{logo}" alt="Paranice">' if logo else '<b style="font-size:22px">paranice</b>'
    return f"""<div class="hd">{img}
      <div class="meta"><strong>Panel de negocio</strong>Generado: {HOY_STR}<br>
      <span style="color:{PINK}">Powered by Calybrat</span></div></div>"""


FT = """<div class="ft"><span>Paranice · Documento interno</span>
<span>Generado automáticamente por Calybrat · 2026</span></div>"""


def _kpi(l, v, d="", ok=True):
    dd = f'<div class="d {"ok" if ok else "bad"}">{d}</div>' if d else ""
    return f'<div class="kpi"><div class="l">{l}</div><div class="v">{v}</div>{dd}</div>'


def _tabla(df, cols):
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in fila) + "</tr>" for fila in df)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _doc(titulo, cuerpo):
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>{titulo} — Paranice</title>{STYLE}</head><body><div class="pg">
<div class="print">💡 Para guardarlo en PDF: abre este archivo y presiona <b>Ctrl+P</b> (o Cmd+P) → "Guardar como PDF".</div>
{_hd()}<div class="ttl">{titulo}</div>{cuerpo}{FT}</div></body></html>"""


def rpt_ejecutivo(v, f, c, car, so, d, m):
    ult = f.iloc[-1]
    prev = f.iloc[-2]
    var = (ult["ingresos_cop"] - prev["ingresos_cop"]) / prev["ingresos_cop"] * 100
    abierta = car[~car["pagada"]]
    venc = abierta[abierta["dias_mora"] > 0]["valor_cop"].sum()
    ent = d[(d["estado"] == "Entregado") & (d["tipo_canal"] != "D2C")]
    otif = ent["otif"].mean() * 100 if len(ent) else 0
    mp = m[m["inversion_cop"] > 0]
    roas = mp["ingresos_cop"].sum() / mp["inversion_cop"].sum() if len(mp) else 0

    canal = v[v["mes"] == ult["mes"]].groupby("canal").agg(
        ventas=("venta_cop", "sum"), margen=("margen_cop", "sum")).reset_index()
    canal["m%"] = (canal["margen"] / canal["ventas"] * 100).round(1)
    canal = canal.sort_values("ventas", ascending=False)
    filas_canal = [(r["canal"], cop(r["ventas"], 1),
                    f"{r['ventas']/canal['ventas'].sum()*100:.1f}%", f"{r['m%']:.1f}%")
                   for _, r in canal.iterrows()]

    top = v[v["mes"] == ult["mes"]].groupby("producto")["venta_cop"].sum().nlargest(8)
    filas_top = [(p, cop(x, 1)) for p, x in top.items()]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Ingresos del mes", cop(ult['ingresos_cop'],1), f"{'▲' if var>=0 else '▼'} {abs(var):.1f}% vs mes anterior", var>=0)}
      {_kpi("Margen bruto", f"{ult['margen_bruto_pct']:.1f}%", "Meta 58%", ult['margen_bruto_pct']>=52)}
      {_kpi("EBITDA", f"{ult['ebitda_pct']:.1f}%", cop(ult['ebitda_cop'],1), ult['ebitda_pct']>=10)}
      {_kpi("OTIF a cadenas", f"{otif:.1f}%", "Meta 95%", otif>=95)}
      {_kpi("Cartera vencida", cop(venc,1), f"{venc/abierta['valor_cop'].sum()*100:.0f}% de lo abierto", venc/abierta['valor_cop'].sum()<0.2)}
      {_kpi("ROAS marketing", f"{roas:.1f}x", "Meta 3x", roas>=3)}
    </div>
    <div class="note"><b>Resumen:</b> el mes cerró en {cop(ult['ingresos_cop'],1)} con un EBITDA de
    {ult['ebitda_pct']:.1f}%. El canal de mayor facturación fue <b>{canal.iloc[0]['canal']}</b> y el de
    mejor margen <b>{canal.loc[canal['m%'].idxmax()]['canal']}</b> ({canal['m%'].max():.0f}%).</div>
    <h3>Resultado por canal — {ult['mes']}</h3>
    {_tabla(filas_canal, ["Canal", "Ventas", "Participación", "Margen"])}
    <h3>Productos más vendidos del mes</h3>
    {_tabla(filas_top, ["Producto", "Ventas"])}
    <h3>Resultado de los últimos 6 meses</h3>
    {_tabla([(r['mes'], cop(r['ingresos_cop'],1), f"{r['margen_bruto_pct']:.1f}%",
              cop(r['ebitda_cop'],1), f"{r['ebitda_pct']:.1f}%") for _, r in f.tail(6).iterrows()],
            ["Mes", "Ingresos", "Margen bruto", "EBITDA", "EBITDA %"])}"""
    return _doc("📊 Reporte ejecutivo mensual — agosto 2026", cuerpo)


def rpt_retail(so, d):
    ult3 = sorted(so["mes"].unique())[-3:]
    sf = so[so["mes"].isin(ult3)]
    cadena = sf.groupby("cadena").agg(
        sell_in=("unidades_sell_in", "sum"), sell_out=("unidades_sell_out", "sum"),
        valor=("valor_sell_out_cop", "sum"), quiebre=("dias_sin_stock", "mean"),
        pdv=("pdv_activos", "max")).reset_index()
    cadena["conv"] = (cadena["sell_out"] / cadena["sell_in"] * 100).round(1)
    filas = [(r["cadena"], f"{int(r['pdv'])}", f"{int(r['sell_in']):,}", f"{int(r['sell_out']):,}",
              f"{r['conv']:.0f}%", cop(r["valor"], 1), f"{r['quiebre']:.1f} días")
             for _, r in cadena.sort_values("valor", ascending=False).iterrows()]

    peores = sf.groupby(["cadena", "ciudad", "producto"])["dias_sin_stock"].mean().nlargest(12)
    filas_q = [(c, ci, p, f"{x:.1f} días") for (c, ci, p), x in peores.items()]

    ent = d[(d["estado"] == "Entregado") & (d["tipo_canal"].isin(["Retail", "Especializado", "Marketplace"]))]
    otif = ent.groupby("canal")["otif"].mean().sort_values(ascending=False) * 100
    filas_o = [(c, f"{x:.1f}%") for c, x in otif.items()]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Sell-out (3 meses)", f"{int(sf['unidades_sell_out'].sum()):,} und", cop(sf['valor_sell_out_cop'].sum(),1))}
      {_kpi("Conversión sell-in→out", f"{sf['unidades_sell_out'].sum()/sf['unidades_sell_in'].sum()*100:.0f}%", "Ideal 90-100%", sf['unidades_sell_out'].sum()/sf['unidades_sell_in'].sum()>=0.88)}
      {_kpi("Días sin stock", f"{sf['dias_sin_stock'].mean():.1f}", "Promedio por referencia", sf['dias_sin_stock'].mean()<3)}
    </div>
    <div class="note"><b>Para la próxima negociación con la cadena:</b> el sell-out de los últimos tres
    meses fue de {cop(sf['valor_sell_out_cop'].sum(),1)} a precio de góndola. Los quiebres de stock son
    el argumento más fuerte para pedir más espacio y mejor pronóstico de pedido.</div>
    <h3>Desempeño por cadena — últimos 3 meses</h3>
    {_tabla(filas, ["Cadena", "PDV", "Sell-in", "Sell-out", "Conversión", "Valor sell-out", "Días sin stock"])}
    <h3>OTIF por cliente</h3>
    {_tabla(filas_o, ["Cliente", "OTIF"])}
    <h3>Dónde más se agotó el producto</h3>
    {_tabla(filas_q, ["Cadena", "Ciudad", "Producto", "Días sin stock"])}"""
    return _doc("🏬 Reporte de retail y sell-out", cuerpo)


def rpt_clientes(c, m):
    seg = c.groupby("segmento").agg(n=("cliente_id", "count"), ltv=("ltv_cop", "mean"),
                                    total=("ltv_cop", "sum")).reindex(
        ["Primera compra", "Repite", "Fiel", "Embajador"]).fillna(0)
    filas = [(s, f"{int(r['n']):,}", f"{r['n']/seg['n'].sum()*100:.1f}%", cop(r["ltv"]),
              cop(r["total"], 1)) for s, r in seg.iterrows()]
    mp = m[m["inversion_cop"] > 0]
    cac = mp["inversion_cop"].sum() / mp["clientes_nuevos"].sum() if mp["clientes_nuevos"].sum() else 0
    canal = m.groupby("canal").agg(inv=("inversion_cop", "sum"), nuevos=("clientes_nuevos", "sum"),
                                   ing=("ingresos_cop", "sum")).reset_index()
    canal["cac"] = canal.apply(lambda r: r["inv"] / r["nuevos"] if r["nuevos"] and r["inv"] else 0, axis=1)
    canal["roas"] = canal.apply(lambda r: r["ing"] / r["inv"] if r["inv"] else None, axis=1)
    filas_c = [(r["canal"], cop(r["inv"], 1), f"{int(r['nuevos']):,}",
                cop(r["cac"]) if r["cac"] else "orgánico",
                f"{r['roas']:.1f}x" if pd.notna(r["roas"]) else "—")
               for _, r in canal.sort_values("ing", ascending=False).iterrows()]
    riesgo = c[c["en_riesgo_fuga"]]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Clientes del canal propio", f"{len(c):,}")}
      {_kpi("Tasa de recompra", f"{c['recurrente'].mean()*100:.1f}%", "Referencia D2C 30%", c['recurrente'].mean()>0.3)}
      {_kpi("LTV promedio", cop(c['ltv_cop'].mean()))}
      {_kpi("CAC", cop(cac))}
      {_kpi("LTV / CAC", f"{c['ltv_cop'].mean()/cac:.1f}x" if cac else "—", "Meta >3x", (c['ltv_cop'].mean()/cac if cac else 0)>=3)}
      {_kpi("En riesgo de fuga", f"{len(riesgo):,}", cop(riesgo['ltv_cop'].sum(),1)+" en juego", False)}
    </div>
    <div class="note"><b>Acción sugerida:</b> hay {len(riesgo):,} clientes que ya compraron más de una vez
    y llevan más de 120 días sin volver, con {cop(riesgo['ltv_cop'].sum(),1)} de valor histórico.
    Reactivarlos por Omnisend o WhatsApp no cuesta pauta.</div>
    <h3>Segmentos de cliente</h3>
    {_tabla(filas, ["Segmento", "Clientes", "% de la base", "LTV promedio", "Facturación acumulada"])}
    <h3>Adquisición por canal</h3>
    {_tabla(filas_c, ["Canal", "Inversión", "Clientes nuevos", "CAC", "ROAS"])}"""
    return _doc("💜 Reporte de clientes y recompra", cuerpo)


def rpt_calidad(p):
    ult6 = sorted(p["mes"].unique())[-6:]
    pf = p[p["mes"].isin(ult6)]
    gf = pf[pf["es_sin_gluten"] == True]
    alertas = pf[pf["estado_calidad"] != "Aprobado"].sort_values("fecha", ascending=False)
    filas = [(r["lote_id"], r["fecha"], r["producto"], r["linea"], r["turno"],
              f"{r['gluten_ppm']:.1f} ppm" if pd.notna(r["gluten_ppm"]) else "—",
              r["estado_calidad"], cop(r["costo_lote_cop"], 1))
             for _, r in alertas.head(20).iterrows()]
    mes = pf.groupby("mes").agg(lotes=("lote_id", "count"), ppm=("gluten_ppm", "mean"),
                                aprob=("estado_calidad", lambda s: (s == "Aprobado").mean() * 100),
                                merma=("merma_pct", "mean")).reset_index()
    filas_m = [(r["mes"], f"{int(r['lotes'])}", f"{r['ppm']:.1f}", f"{r['aprob']:.1f}%",
                f"{r['merma']:.2f}%") for _, r in mes.iterrows()]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Lotes producidos", f"{len(pf):,}", "Últimos 6 meses")}
      {_kpi("Aprobación de calidad", f"{(pf['estado_calidad']=='Aprobado').mean()*100:.1f}%", "Meta 98%", (pf['estado_calidad']=='Aprobado').mean()>=0.98)}
      {_kpi("Gluten promedio", f"{gf['gluten_ppm'].mean():.1f} ppm", "Límite legal 20 ppm", gf['gluten_ppm'].mean()<12)}
      {_kpi("Lotes fuera de norma", f"{int((gf['gluten_ppm']>20).sum())}", "Por encima de 20 ppm", (gf['gluten_ppm']>20).sum()==0)}
      {_kpi("Merma promedio", f"{pf['merma_pct'].mean():.2f}%", "Meta <3%", pf['merma_pct'].mean()<3)}
      {_kpi("Costo de lo rechazado", cop(pf[pf['estado_calidad']=='Rechazado']['costo_lote_cop'].sum(),1), "", False)}
    </div>
    <div class="note"><b>Trazabilidad:</b> este documento respalda el claim "libre de gluten" del
    portafolio. El estándar internacional exige menos de 20 ppm; cada lote por encima de ese umbral
    quedó bloqueado y no salió al mercado.</div>
    <h3>Evolución mensual</h3>
    {_tabla(filas_m, ["Mes", "Lotes", "Gluten ppm", "Aprobación", "Merma"])}
    <h3>Lotes con hallazgo — detalle</h3>
    {_tabla(filas, ["Lote", "Fecha", "Producto", "Línea", "Turno", "Gluten", "Estado", "Costo"]) if filas else "<p>Sin hallazgos en el período.</p>"}"""
    return _doc("🧪 Reporte de calidad y trazabilidad de gluten", cuerpo)


def rpt_cartera(car):
    abierta = car[~car["pagada"]]
    buckets = {
        "Vigente": abierta[abierta["dias_mora"] == 0]["valor_cop"].sum(),
        "1–30 días": abierta[abierta["dias_mora"].between(1, 30)]["valor_cop"].sum(),
        "31–60 días": abierta[abierta["dias_mora"].between(31, 60)]["valor_cop"].sum(),
        "61–90 días": abierta[abierta["dias_mora"].between(61, 90)]["valor_cop"].sum(),
        "+90 días": abierta[abierta["dias_mora"] > 90]["valor_cop"].sum(),
    }
    total = sum(buckets.values())
    filas_b = [(k, cop(x, 1), f"{x/total*100:.1f}%") for k, x in buckets.items()]
    cli = abierta.groupby("cliente").agg(valor=("valor_cop", "sum"), mora=("dias_mora", "mean"),
                                         facturas=("factura_id", "count")).reset_index()
    filas_c = [(r["cliente"], f"{int(r['facturas'])}", cop(r["valor"], 1), f"{r['mora']:.0f} días")
               for _, r in cli.sort_values("valor", ascending=False).iterrows()]
    criticas = abierta[abierta["dias_mora"] > 60].sort_values("dias_mora", ascending=False).head(20)
    filas_x = [(r["factura_id"], r["cliente"], r["fecha_vencimiento"], f"{int(r['dias_mora'])} días",
                cop(r["valor_cop"], 1)) for _, r in criticas.iterrows()]

    cuerpo = f"""
    <div class="kpis">
      {_kpi("Cartera abierta", cop(total,1), f"{len(abierta):,} facturas")}
      {_kpi("Vencida", cop(total-buckets['Vigente'],1), f"{(total-buckets['Vigente'])/total*100:.0f}% del total", (total-buckets['Vigente'])/total<0.2)}
      {_kpi("Más de 90 días", cop(buckets['+90 días'],1), "Riesgo alto", buckets['+90 días']==0)}
    </div>
    <div class="note"><b>Flujo de caja:</b> las cadenas pagan a 45–60 días. Mientras más crezca el peso
    de retail en el mix, más capital de trabajo se necesita para financiar el crecimiento.</div>
    <h3>Antigüedad de la cartera</h3>
    {_tabla(filas_b, ["Bucket", "Valor", "Participación"])}
    <h3>Cartera por cliente</h3>
    {_tabla(filas_c, ["Cliente", "Facturas", "Saldo", "Mora promedio"])}
    <h3>Facturas con más de 60 días de mora</h3>
    {_tabla(filas_x, ["Factura", "Cliente", "Vencimiento", "Mora", "Valor"]) if filas_x else "<p>Sin facturas críticas.</p>"}"""
    return _doc("⏳ Reporte de cartera y cobranza", cuerpo)


def render():
    v, f, c, car, so, d, p, m = load()

    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Reportes Automáticos",
        "Los mismos documentos que hoy toma días armar en Excel, listos para descargar o imprimir en PDF",
        "personaje_4.png"), unsafe_allow_html=True)

    st.markdown(panel("Cómo se usa", """
        Cada reporte se genera con los datos del momento en que lo descargas. Ábrelo en el navegador
        y presiona <b>Ctrl+P</b> (o <b>Cmd+P</b> en Mac) → <b>Guardar como PDF</b> para enviarlo a
        junta, a un banco, a una cadena o al equipo.
    """, "📄"), unsafe_allow_html=True)

    reportes = [
        ("📊 Reporte ejecutivo mensual",
         "Ingresos, margen, EBITDA, OTIF y ROAS del mes, con resultado por canal. Para junta directiva.",
         lambda: rpt_ejecutivo(v, f, c, car, so, d, m), "paranice_reporte_ejecutivo.html"),
        ("🏬 Reporte de retail y sell-out",
         "Rotación, quiebres y OTIF por cadena. Es el documento para sentarse a negociar con Éxito o Carulla.",
         lambda: rpt_retail(so, d), "paranice_reporte_retail.html"),
        ("💜 Reporte de clientes y recompra",
         "Segmentos, LTV, CAC y la lista de clientes en riesgo de fuga. Para marketing y CRM.",
         lambda: rpt_clientes(c, m), "paranice_reporte_clientes.html"),
        ("🧪 Reporte de calidad y gluten",
         "Trazabilidad de lotes y ensayos de gluten. Respalda el claim libre de gluten ante clientes y autoridades.",
         lambda: rpt_calidad(p), "paranice_reporte_calidad.html"),
        ("⏳ Reporte de cartera y cobranza",
         "Aging, saldo por cadena y facturas críticas. Para finanzas y para la reunión de cobro.",
         lambda: rpt_cartera(car), "paranice_reporte_cartera.html"),
    ]

    for i, (nombre, desc, generador, archivo) in enumerate(reportes):
        with st.expander(nombre, expanded=(i == 0)):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<p style='color:{MUTED};font-size:13px;margin:2px 0 10px'>{desc}</p>",
                            unsafe_allow_html=True)
            html = generador()
            with col2:
                st.download_button("⬇️  Descargar", data=html.encode("utf-8"), file_name=archivo,
                                   mime="text/html", key=f"dl_{i}", use_container_width=True)
            st.caption(f"Archivo: {archivo} · se genera con los datos de hoy")

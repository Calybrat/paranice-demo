import streamlit as st
import pandas as pd
from utils.formatters import *
from utils import config, datos

CONTEXTO = """
Eres el Agente de Inteligencia de Negocio de Paranice, marca colombiana de alimentos saludables
fundada en 2019 en Bogotá (antes conocida como Why Not). Su promesa de marca es que lo indulgente
por fin sea nutritivo: productos libres de gluten, sin azúcar añadida, veganos y keto friendly.

Portafolio real (6 categorías, 28 referencias):
  · GranOLAS 300 g — Vanilla Shortbread, Chip Cookie, Fudge Cake, Pistachio Cookie
  · Esparcibles a base de nueces — Buttery Pistachio Cookie, Golden Butter Cookie,
    Peanutty Banana Shake, Creamy y Crunchy Cocoa Hazelnut, Golden Cinnamon Roll, Baby Spreads
  · Mezclas para Pancakes & Waffles — a base de almendra (285 g) y de avena (300 g)
  · Avena & Harinas — avena en hojuelas, harina de avena, harina de almendra
  · Combos y Merch

Canales reales: tienda propia paranice.co (WooCommerce, pedido mínimo $50.000, Mercado Pago,
Omnisend para email), cadenas Éxito y Carulla, marketplace Rappi, especializado Fithub y tiendas
naturistas, y los mercados de Costa Rica y Estados Unidos (paranice.us).

Diferencial operativo: el control de contaminación cruzada. Cada lote libre de gluten se ensaya
en ppm y el límite internacional es 20 ppm.

Responde SIEMPRE en español, de forma directa, breve y orientada a decisiones. Cuando des una cifra,
di qué significa para el negocio y qué haría falta decidir. Nada de jerga técnica innecesaria.
"""

SUGERIDAS = [
    "¿Cómo vamos este mes?",
    "¿Qué canal me deja más margen?",
    "¿Dónde se está agotando el producto?",
    "¿Cuánto me deben las cadenas?",
    "¿Cómo va la recompra y el CAC?",
    "¿Cómo está la calidad del gluten?",
    "¿Cómo van Costa Rica y Estados Unidos?",
    "¿Qué productos debería impulsar?",
]


def load():
    return (datos.ventas(), datos.finanzas(), datos.clientes(), datos.cartera(),
            datos.sellout(), datos.despachos(), datos.produccion(), datos.marketing())


def resumen_datos() -> str:
    try:
        v, f, c, car, so, d, p, m = load()
        ult = f.iloc[-1]
        abierta = car[~car["pagada"]]
        ent = d[(d["estado"] == "Entregado") & (d["tipo_canal"] != "D2C")]
        mp = m[m["inversion_cop"] > 0]
        gf = p[p["es_sin_gluten"] == True]
        canal = v[v["mes"] == ult["mes"]].groupby("canal")["venta_cop"].sum().sort_values(ascending=False)
        return f"""
=== DATOS DE PARANICE AL 31 DE AGOSTO DE 2026 ===
ÚLTIMO MES ({ult['mes']}): ingresos {cop(ult['ingresos_cop'],1)} · margen bruto {ult['margen_bruto_pct']:.1f}% · EBITDA {ult['ebitda_pct']:.1f}%
CANALES DEL MES: {' · '.join(f'{k}: {cop(x,1)}' for k, x in canal.items())}
AÑO 2026 (ene-ago): {cop(v[v['mes'] >= '2026-01']['venta_cop'].sum(), 1)}
CANAL PROPIO: {len(c):,} clientes · recompra {c['recurrente'].mean()*100:.1f}% · LTV {cop(c['ltv_cop'].mean())} · ticket {cop(c['ticket_promedio_cop'].mean())}
MARKETING: ROAS {mp['ingresos_cop'].sum()/mp['inversion_cop'].sum():.1f}x · CAC {cop(mp['inversion_cop'].sum()/mp['clientes_nuevos'].sum())}
RETAIL: sell-out {int(so['unidades_sell_out'].sum()):,} und · conversión sell-in→out {so['unidades_sell_out'].sum()/so['unidades_sell_in'].sum()*100:.0f}% · días sin stock {so['dias_sin_stock'].mean():.1f}
CUMPLIMIENTO: OTIF a cadenas {ent['otif'].mean()*100:.1f}% · fill rate {ent['fill_rate'].mean()*100:.1f}%
CARTERA: abierta {cop(abierta['valor_cop'].sum(),1)} · vencida {cop(abierta[abierta['dias_mora']>0]['valor_cop'].sum(),1)}
CALIDAD: aprobación {(p['estado_calidad']=='Aprobado').mean()*100:.1f}% · gluten promedio {gf['gluten_ppm'].mean():.1f} ppm · lotes fuera de norma {(gf['gluten_ppm']>20).sum()}
MERCADOS: {' · '.join(f'{k}: {cop(x,1)}' for k, x in v.groupby('pais')['venta_cop'].sum().sort_values(ascending=False).items())}
"""
    except Exception as ex:
        return f"[No se pudieron cargar los datos: {ex}]"


def responder_demo(pregunta: str) -> str:
    q = pregunta.lower()
    v, f, c, car, so, d, p, m = load()
    ult, prev = f.iloc[-1], f.iloc[-2]

    if any(x in q for x in ["cómo vamos", "como vamos", "mes", "resumen", "general", "ventas"]):
        var = (ult["ingresos_cop"] - prev["ingresos_cop"]) / prev["ingresos_cop"] * 100
        canal = v[v["mes"] == ult["mes"]].groupby("canal")["venta_cop"].sum().sort_values(ascending=False)
        return (f"📊 Agosto 2026 cerró en {cop(ult['ingresos_cop'],1)}, "
                f"{'arriba' if var>=0 else 'abajo'} {abs(var):.1f}% frente a julio.\n\n"
                f"• Margen bruto: {ult['margen_bruto_pct']:.1f}%\n"
                f"• EBITDA: {ult['ebitda_pct']:.1f}% ({cop(ult['ebitda_cop'],1)})\n"
                f"• Canal que más facturó: {canal.index[0]} con {cop(canal.iloc[0],1)}\n"
                f"• Año corrido: {cop(v[v['mes']>='2026-01']['venta_cop'].sum(),1)}\n\n"
                f"Lo que hay que vigilar: el mix se está inclinando a retail, que deja menos margen "
                f"y paga a 60 días. Cada punto que crezca el canal propio mejora margen y caja al tiempo.")

    if any(x in q for x in ["margen", "canal", "rentab", "utilidad"]):
        g = v.groupby("canal", observed=True)[["venta_cop", "margen_cop"]].sum()
        g = pd.DataFrame({"ventas": g["venta_cop"],
                          "margen": g["margen_cop"] / g["venta_cop"] * 100}
                         ).sort_values("margen", ascending=False)
        lineas = "\n".join(f"  • {k}: {r['margen']:.0f}% de margen · {cop(r['ventas'],1)} vendidos"
                           for k, r in g.iterrows())
        return (f"💰 Margen por canal:\n\n{lineas}\n\n"
                f"El canal propio y Estados Unidos son los más rentables porque no hay comisión de "
                f"cadena de por medio. Éxito y Carulla dan volumen y cobertura, pero se quedan con "
                f"cerca de un tercio del precio de góndola. La decisión no es abandonar retail: es "
                f"cuánto invertir en llevar al comprador de góndola hacia la tienda propia.")

    if any(x in q for x in ["agot", "quiebre", "stock", "góndola", "gondola", "inventario"]):
        peores = so.groupby(["cadena", "ciudad", "producto"])["dias_sin_stock"].mean().nlargest(5)
        lineas = "\n".join(f"  • {p_} en {cad} de {ciu}: {x:.1f} días sin stock"
                           for (cad, ciu, p_), x in peores.items())
        return (f"🚫 Días sin stock en góndola (promedio {so['dias_sin_stock'].mean():.1f} por referencia/mes):\n\n"
                f"{lineas}\n\n"
                f"Cada día sin producto es venta perdida y, peor, la cadena reasigna ese espacio. "
                f"La conversión de sell-in a sell-out va en {so['unidades_sell_out'].sum()/so['unidades_sell_in'].sum()*100:.0f}%, "
                f"así que el problema no es que sobre inventario en la cadena, es que la reposición "
                f"no está llegando al ritmo de la rotación.")

    if any(x in q for x in ["deben", "cartera", "cobro", "cobranza", "caja", "pago"]):
        abierta = car[~car["pagada"]]
        venc = abierta[abierta["dias_mora"] > 0]
        top = abierta.groupby("cliente")["valor_cop"].sum().sort_values(ascending=False)
        lineas = "\n".join(f"  • {k}: {cop(x,1)}" for k, x in top.head(5).items())
        return (f"⏳ Cartera abierta: {cop(abierta['valor_cop'].sum(),1)} en {len(abierta):,} facturas.\n\n"
                f"• Vencida: {cop(venc['valor_cop'].sum(),1)} ({venc['valor_cop'].sum()/abierta['valor_cop'].sum()*100:.0f}% de lo abierto)\n"
                f"• Con más de 90 días: {cop(abierta[abierta['dias_mora']>90]['valor_cop'].sum(),1)}\n\n"
                f"Quién debe más:\n{lineas}\n\n"
                f"Éxito y Carulla pagan a 60 días: mientras retail crezca, la caja se aprieta aunque "
                f"la utilidad se vea bien en el papel.")

    if any(x in q for x in ["recompra", "cac", "cliente", "ltv", "fuga", "retención", "retencion"]):
        mp = m[m["inversion_cop"] > 0]
        cac = mp["inversion_cop"].sum() / mp["clientes_nuevos"].sum()
        riesgo = c[c["en_riesgo_fuga"]]
        return (f"💜 Canal propio: {len(c):,} clientes.\n\n"
                f"• Recompra: {c['recurrente'].mean()*100:.1f}% (la referencia sana en D2C es 30%)\n"
                f"• LTV promedio: {cop(c['ltv_cop'].mean())} · ticket promedio {cop(c['ticket_promedio_cop'].mean())}\n"
                f"• CAC: {cop(cac)} → relación LTV/CAC de {c['ltv_cop'].mean()/cac:.1f}x\n"
                f"• En riesgo de fuga: {len(riesgo):,} clientes con {cop(riesgo['ltv_cop'].sum(),1)} de valor histórico\n\n"
                f"La palanca más barata hoy no es traer gente nueva, es reactivar esos {len(riesgo):,} "
                f"que ya compraron dos o más veces y llevan más de 120 días sin volver.")

    if any(x in q for x in ["gluten", "calidad", "lote", "ppm", "contamina"]):
        gf = p[p["es_sin_gluten"] == True]
        fuera = int((gf["gluten_ppm"] > 20).sum())
        return (f"🧪 Calidad de los últimos meses:\n\n"
                f"• Aprobación de lotes: {(p['estado_calidad']=='Aprobado').mean()*100:.1f}%\n"
                f"• Gluten promedio: {gf['gluten_ppm'].mean():.1f} ppm (el límite internacional es 20)\n"
                f"• Lotes fuera de norma: {fuera} · en cuarentena: {int((p['estado_calidad']=='Cuarentena').sum())}\n"
                f"• Merma promedio: {p['merma_pct'].mean():.2f}%\n"
                f"• Costo de lo rechazado: {cop(p[p['estado_calidad']=='Rechazado']['costo_lote_cop'].sum(),1)}\n\n"
                f"{'Todo bajo control.' if fuera==0 else f'Los {fuera} lotes por encima de 20 ppm quedaron bloqueados y no salieron al mercado, que es exactamente lo que debe pasar. Vale la pena revisar la línea y el turno donde ocurrieron.'}")

    if any(x in q for x in ["costa rica", "estados unidos", "internacional", "expansión", "expansion", "país", "pais", "usa"]):
        g = v.groupby("pais", observed=True)[["venta_cop", "margen_cop"]].sum()
        g = pd.DataFrame({"ventas": g["venta_cop"],
                          "margen": g["margen_cop"] / g["venta_cop"] * 100}
                         ).sort_values("ventas", ascending=False)
        lineas = "\n".join(f"  • {k}: {cop(r['ventas'],1)} ({r['ventas']/g['ventas'].sum()*100:.0f}% del total) · margen {r['margen']:.0f}%"
                           for k, r in g.iterrows())
        return (f"🌎 Los tres mercados:\n\n{lineas}\n\n"
                f"Estados Unidos deja el mejor margen porque se vende directo por paranice.us, sin "
                f"comisión de cadena, aunque el flete pesa mucho más. Costa Rica va por distribuidor, "
                f"lo que da alcance rápido pero recorta margen. Colombia sigue financiando la expansión.")

    if any(x in q for x in ["producto", "impuls", "sku", "portafolio", "referencia"]):
        v26 = v[v["mes"] >= "2026-01"]
        g = v26.groupby("producto").agg(ventas=("venta_cop", "sum"), margen=("margen_cop", "sum"))
        g["m%"] = g["margen"] / g["ventas"] * 100
        top = g.nlargest(5, "margen")
        lineas = "\n".join(f"  • {k}: {cop(r['ventas'],1)} · margen {r['m%']:.0f}%" for k, r in top.iterrows())
        floja = g.nsmallest(3, "ventas")
        return (f"🥣 Los que más margen aportan en 2026:\n\n{lineas}\n\n"
                f"Referencias con menor tracción: {', '.join(floja.index)}.\n\n"
                f"Con 28 referencias en 6 categorías, la pregunta no es qué agregar sino qué proteger: "
                f"garantizar que los de arriba nunca se agoten vale más que lanzar un sabor nuevo.")

    return (f"Te puedo ayudar con cualquiera de estos temas:\n\n"
            f"📊 Ventas y resultado del mes · 💰 Margen por canal · 🏬 Retail y quiebres de stock\n"
            f"⏳ Cartera y flujo de caja · 💜 Clientes, recompra y CAC · 🧪 Calidad y gluten\n"
            f"🌎 Costa Rica y Estados Unidos · 🥣 Portafolio de productos\n\n"
            f"Para orientarte: agosto cerró en {cop(ult['ingresos_cop'],1)} con "
            f"{ult['ebitda_pct']:.1f}% de EBITDA, la recompra del canal propio va en "
            f"{c['recurrente'].mean()*100:.1f}% y hay {cop(car[~car['pagada']]['valor_cop'].sum(),1)} "
            f"de cartera abierta.")


def llamar_claude(api_key: str, pregunta: str) -> str:
    try:
        import anthropic
        cliente = anthropic.Anthropic(api_key=api_key)
        historial = [{"role": msg["role"], "content": msg["content"]}
                     for msg in st.session_state.ag_msgs[:-1]]
        historial.append({"role": "user", "content": pregunta})
        r = cliente.messages.create(
            model=config.modelo_agente(),
            max_tokens=1200,
            system=CONTEXTO + "\n\n" + resumen_datos(),
            messages=historial,
        )
        return r.content[0].text
    except Exception as ex:
        return f"No se pudo conectar con Claude: {ex}"


def _procesar(pregunta, modo_demo, api_key):
    st.session_state.ag_msgs.append({"role": "user", "content": pregunta})
    if modo_demo or not api_key:
        resp = responder_demo(pregunta)
    else:
        resp = llamar_claude(api_key, pregunta)
    st.session_state.ag_msgs.append({"role": "assistant", "content": resp})


def render():
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(encabezado(
        "Agente IA Paranice",
        "Pregúntale al negocio en español, como si le escribieras a alguien del equipo",
        "personaje_3.png"), unsafe_allow_html=True)

    if "ag_msgs" not in st.session_state:
        st.session_state.ag_msgs = []
    if "ag_pend" not in st.session_state:
        st.session_state.ag_pend = None

    # La llave sale de la configuración (st.secrets o variable de entorno). Solo
    # si no hay ninguna configurada se le pide al usuario que la pegue.
    key_configurada = config.anthropic_api_key()
    c1, c2 = st.columns([3, 1])
    with c1:
        if key_configurada:
            api_key = key_configurada
            st.markdown(
                f'<div style="padding:6px 0 2px"><span class="pn-badge">🔗 Claude conectado '
                f'· {config.modelo_agente()}</span></div>',
                unsafe_allow_html=True)
        else:
            api_key = st.text_input("API Key de Anthropic (opcional)", type="password",
                                    placeholder="sk-ant-…", key="ag_key",
                                    help="Con una API key el agente responde cualquier pregunta "
                                         "libre sobre los datos. Sin ella funciona el modo demo. "
                                         "Para dejarla fija: .streamlit/secrets.toml "
                                         "(ver secrets.example.toml).")
    with c2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        modo_demo = st.toggle("Modo demo", value=not key_configurada, key="ag_demo")

    st.markdown(f"<p style='font-size:13px;font-weight:800;color:{PURPLE};margin:14px 0 8px'>"
                f"💡 Preguntas frecuentes</p>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, q in enumerate(SUGERIDAS):
        if cols[i % 4].button(q, key=f"sug_{i}", use_container_width=True):
            st.session_state.ag_pend = q

    if st.session_state.ag_pend:
        _procesar(st.session_state.ag_pend, modo_demo, api_key)
        st.session_state.ag_pend = None

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    for msg in st.session_state.ag_msgs:
        es_user = msg["role"] == "user"
        color = PINK if es_user else PURPLE
        etiqueta = "Tú" if es_user else "🤖 Agente Paranice"
        fondo = PINK_LT if es_user else SURF
        st.markdown(f"""
        <div style="background:{fondo};border:1px solid {BORDER};border-radius:14px;
          padding:14px 18px;margin:8px 0;border-left:4px solid {color}">
          <p style="font-size:10.5px;font-weight:900;color:{color};margin:0 0 8px;
            text-transform:uppercase;letter-spacing:.08em">{etiqueta}</p>
          <p style="color:{PURPLE};margin:0;line-height:1.7;white-space:pre-wrap;font-size:13.5px">{msg['content']}</p>
        </div>""", unsafe_allow_html=True)

    pregunta = st.chat_input("Escribe tu pregunta sobre el negocio…")
    if pregunta:
        _procesar(pregunta, modo_demo, api_key)
        st.rerun()

    if st.session_state.ag_msgs:
        if st.button("🗑️  Limpiar conversación", key="ag_clear"):
            st.session_state.ag_msgs = []
            st.rerun()
    else:
        st.markdown(panel("Qué puedes preguntarle", """
        Este agente ve los mismos datos de todo el panel. En el producto final se conecta a las
        fuentes reales de Paranice (WooCommerce, el ERP, los reportes de sell-out de las cadenas)
        y responde en segundos lo que hoy toma horas de Excel: <i>“¿cuánto me debe Carulla?”</i>,
        <i>“¿qué referencia se está agotando en Medellín?”</i>, <i>“¿me conviene meterle más plata a Meta?”</i>.
        """, "🤖"), unsafe_allow_html=True)

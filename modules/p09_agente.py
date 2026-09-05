import streamlit as st
import pandas as pd
from pathlib import Path
from utils.formatters import *

DATA = Path(__file__).parent.parent / "data"

CONTEXTO_PARANICE = """
Eres el Agente de Inteligencia de Paranice, marca colombiana de alimentos saludables (granolas, esparcibles,
mezclas para pancakes/waffles, harinas y avena) sin gluten, sin azúcar añadida y veganas, vendida por
e-commerce D2C con presencia en Colombia, Costa Rica y Estados Unidos.

Datos clave de la empresa:
- Categorías: GranOLAs, Pancakes & Waffles, Avena & Harinas, Esparcibles, Combos, Merch.
- Canales de venta: Instagram Ads, Google Ads, TikTok Ads, Email/WhatsApp, Orgánico/SEO, Referidos.
- Bodegas: CEDI Bogotá (Colombia), Hub San José (Costa Rica), 3PL Miami (Estados Unidos).
- Insumos importados clave: avena certificada libre de gluten (Finlandia), almendra (EEUU), cacao (Ecuador), pistacho (Perú).
- Control de calidad: cada lote sin gluten se testea en ppm; el límite regulatorio de referencia es 20 ppm.
Responde siempre en español, de manera directa y profesional, orientado a decisiones de negocio.
"""

def build_context() -> str:
    try:
        p = pd.read_csv(DATA/"pedidos.csv")
        p["fecha"] = pd.to_datetime(p["fecha"])
        c = pd.read_csv(DATA/"clientes.csv")
        inv = pd.read_csv(DATA/"inventario.csv")
        prod = pd.read_csv(DATA/"produccion.csv")
        e = pd.read_csv(DATA/"envios.csv")
        m = pd.read_csv(DATA/"marketing.csv")
        g = pd.read_csv(DATA/"paises_mensual.csv")

        p26 = p[p["fecha"].dt.year == 2026]
        criticos = inv[inv["estado"] == "Crítico"].shape[0]
        bajos = inv[inv["estado"] == "Bajo"].shape[0]
        ent = e[e["estado"] == "Entregado"]
        otd = (ent["entregado_a_tiempo"] == True).mean() * 100 if len(ent) else 0
        m_paid = m[m["canal"] != "Orgánico/SEO"]
        roas = m_paid["ingresos_atribuidos_cop"].sum() / m_paid["inversion_cop"].sum() if m_paid["inversion_cop"].sum() else 0

        resumen = f"""
=== RESUMEN OPERATIVO PARANICE (al 31 ago 2026) ===
VENTAS 2026 YTD: {cop(p26['total_cop'].sum(),1)} COP
  - Producto estrella: {p26.groupby('producto')['total_cop'].sum().idxmax()}
  - Mejor categoría: {p26.groupby('categoria')['total_cop'].sum().idxmax()}
  - Mejor país: {p26.groupby('pais')['total_cop'].sum().idxmax()}
  - Ticket promedio: {cop(p26.drop_duplicates('pedido_id')['total_cop'].mean())}

CLIENTES:
  - Total con compra: {len(c):,}
  - Tasa de recompra: {pct(c['cliente_recurrente'].mean()*100)}
  - LTV promedio: {cop(c['ltv_cop'].mean())}
  - NPS promedio: {c['nps_score'].mean():.1f}/10

MARKETING:
  - ROAS blended (canales pagos): {roas:.1f}x

INVENTARIO Y CALIDAD:
  - SKUs críticos: {criticos} | SKUs bajos: {bajos}
  - Tasa aprobación QC (lotes 2026): {pct((prod[prod['fecha_produccion']>='2026-01-01']['estado_calidad']=='Aprobado').mean()*100)}

LOGÍSTICA:
  - OTD (On-Time Delivery): {otd:.1f}%

EXPANSIÓN (participación acumulada por país):
{chr(10).join([f"  - {pais}: {cop(v,1)}" for pais, v in g.groupby('pais')['ventas_cop'].sum().items()])}
"""
        return resumen
    except Exception as ex:
        return f"[No se pudieron cargar datos: {ex}]"

SUGERIDAS = [
    "¿Cuáles son las ventas YTD?",
    "¿Cuál es la tasa de recompra de clientes?",
    "¿Qué canal de marketing tiene mejor ROAS?",
    "¿Qué productos tienen stock crítico?",
    "¿Cómo va la expansión a Costa Rica y Estados Unidos?",
    "¿Cuál es el estado de calidad de los lotes sin gluten?",
    "¿Cómo está el OTD de los envíos?",
    "¿Cuál es el margen por categoría?",
]

def _procesar(pregunta: str, usar_demo: bool, api_key: str):
    st.session_state.ag_messages.append({"role": "user", "content": pregunta})
    if usar_demo:
        resp = generar_respuesta_demo(pregunta)
    elif api_key and api_key.startswith("sk-"):
        resp = llamar_claude(api_key, pregunta, build_context())
    else:
        resp = "Activa el Modo demo o ingresa un API key de Anthropic para recibir respuestas."
    st.session_state.ag_messages.append({"role": "assistant", "content": resp})

def render():
    st.markdown(HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="cb-header">
      <div class="cb-logo">P</div>
      <div>
        <div class="cb-title">Agente IA Paranice</div>
        <div class="cb-sub">Asistente inteligente · Consultas en lenguaje natural · Powered by Claude</div>
      </div>
    </div><div class="cb-rule"></div>""", unsafe_allow_html=True)

    if "ag_messages" not in st.session_state:
        st.session_state.ag_messages = []
    if "ag_pending" not in st.session_state:
        st.session_state.ag_pending = None

    col_a, col_b = st.columns([3, 1])
    with col_a:
        api_key = st.text_input("API Key de Anthropic", type="password",
            placeholder="sk-ant-...", key="ag_api",
            help="Ingresa tu API key de Anthropic para activar el agente con IA real")
    with col_b:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        usar_demo = st.toggle("Modo demo", value=True, key="ag_demo")

    st.markdown(f"<p style='font-size:13px;font-weight:700;color:{TEXT};margin:12px 0 8px'>💡 Preguntas sugeridas</p>", unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, q in enumerate(SUGERIDAS):
        if cols[idx % 4].button(q, key=f"sug_{idx}", use_container_width=True):
            st.session_state.ag_pending = q

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.session_state.ag_pending:
        _procesar(st.session_state.ag_pending, usar_demo, api_key)
        st.session_state.ag_pending = None

    for msg in st.session_state.ag_messages:
        role_color = GREEN if msg["role"] == "user" else CORAL
        role_label = "Tú" if msg["role"] == "user" else "🤖 Agente Paranice"
        st.markdown(f"""
        <div style="background:{SURF};border:1px solid {BORDER};border-radius:10px;
          padding:14px 18px;margin:6px 0;border-left:3px solid {role_color}">
          <p style="font-size:11px;font-weight:700;color:{role_color};margin:0 0 8px;
            text-transform:uppercase;letter-spacing:.08em">{role_label}</p>
          <p style="color:{TEXT};margin:0;line-height:1.65;white-space:pre-wrap">{msg['content']}</p>
        </div>""", unsafe_allow_html=True)

    pregunta = st.chat_input("Escribe cualquier pregunta sobre el negocio de Paranice...")
    if pregunta:
        _procesar(pregunta, usar_demo, api_key)
        st.rerun()

    if st.button("🗑️ Limpiar conversación", key="ag_clear"):
        st.session_state.ag_messages = []
        st.rerun()


def generar_respuesta_demo(pregunta: str) -> str:
    p_ = pregunta.lower()
    try:
        p = pd.read_csv(DATA/"pedidos.csv")
        p["fecha"] = pd.to_datetime(p["fecha"])
        c = pd.read_csv(DATA/"clientes.csv")
        inv = pd.read_csv(DATA/"inventario.csv")
        prod = pd.read_csv(DATA/"produccion.csv")
        e = pd.read_csv(DATA/"envios.csv")
        m = pd.read_csv(DATA/"marketing.csv")
        g = pd.read_csv(DATA/"paises_mensual.csv")
        p26 = p[p["fecha"].dt.year == 2026]
    except Exception as ex:
        return f"Error cargando datos: {ex}"

    if any(x in p_ for x in ["venta","ingreso","ytd","facturación"]):
        total = p26["total_cop"].sum()
        top_cat = p26.groupby("categoria")["total_cop"].sum().idxmax()
        top_prod = p26.groupby("producto")["total_cop"].sum().idxmax()
        top_pais = p26.groupby("pais")["total_cop"].sum().idxmax()
        return (f"📊 Ventas acumuladas 2026 (YTD): {cop(total,1)} COP\n\n"
                f"• Producto estrella: {top_prod}\n"
                f"• Mejor categoría: {top_cat}\n"
                f"• País líder: {top_pais}\n"
                f"• Ticket promedio: {cop(p26.drop_duplicates('pedido_id')['total_cop'].mean())}\n\n"
                f"El crecimiento sigue liderado por {top_cat}, con tracción fuerte en {top_pais}.")

    elif any(x in p_ for x in ["recompra","retención","recurrente","churn","fideliza"]):
        pct_rec = c["cliente_recurrente"].mean()*100
        vip = (c["segmento"]=="VIP").sum()
        return (f"🔁 Retención de clientes:\n\n"
                f"• Tasa de recompra: {pct(pct_rec)}\n"
                f"• Clientes VIP (top 20% LTV): {vip:,}\n"
                f"• LTV promedio: {cop(c['ltv_cop'].mean())}\n"
                f"• NPS promedio: {c['nps_score'].mean():.1f}/10\n\n"
                f"{'✅ La recompra está saludable para un negocio D2C.' if pct_rec>40 else '⚠️ La recompra está por debajo del punto de referencia (40%) para D2C.'}")

    elif any(x in p_ for x in ["marketing","roas","canal","publicidad","cac"]):
        m_paid = m[m["canal"]!="Orgánico/SEO"]
        roas_canal = m_paid.groupby("canal").apply(
            lambda x: x["ingresos_atribuidos_cop"].sum()/x["inversion_cop"].sum() if x["inversion_cop"].sum() else 0,
            include_groups=False).sort_values(ascending=False)
        top_canal = roas_canal.idxmax()
        lines = "\n".join([f"  • {ca}: {v:.1f}x" for ca, v in roas_canal.items()])
        return (f"📣 Desempeño de marketing:\n\n"
                f"• Mejor canal por ROAS: {top_canal} ({roas_canal.max():.1f}x)\n"
                f"• Inversión total (pagos): {cop(m_paid['inversion_cop'].sum(),1)}\n\n"
                f"ROAS por canal:\n{lines}")

    elif any(x in p_ for x in ["stock","inventario","crítico","bodega","escasez"]):
        crit = inv[inv["estado"]=="Crítico"]
        bajo = inv[inv["estado"]=="Bajo"]
        return (f"📦 Estado del inventario:\n\n"
                f"• Valor total: {cop(inv['valor_inventario'].sum(),1)} COP\n"
                f"• SKUs críticos: {len(crit)}\n"
                f"• SKUs en nivel bajo: {len(bajo)}\n"
                f"• Cobertura promedio: {inv['dias_cobertura'].mean():.0f} días\n\n"
                f"Productos críticos:\n" +
                "\n".join([f"  • {r['producto']} ({r['bodega']}): stock {r['stock_actual']} / mín {r['stock_minimo']}"
                            for _, r in crit.head(5).iterrows()]))

    elif any(x in p_ for x in ["gluten","calidad","contamina","ppm","lote"]):
        gf = prod[prod["es_sin_gluten"]==True]
        tasa = (prod["estado_calidad"]=="Aprobado").mean()*100
        return (f"🧪 Control de calidad (sin gluten):\n\n"
                f"• Tasa de aprobación de lotes: {pct(tasa)}\n"
                f"• PPM gluten promedio: {gf['resultado_gluten_ppm'].mean():.1f} ppm (límite: 20 ppm)\n"
                f"• Lotes en cuarentena/rechazo (histórico): {(prod['estado_calidad']!='Aprobado').sum()}\n\n"
                f"{'✅ La operación está dentro de los estándares de inocuidad.' if tasa>=97 else '⚠️ Revisar el proceso: la tasa de aprobación está por debajo del 97%.'}")

    elif any(x in p_ for x in ["envío","entrega","otd","logística","transporte"]):
        ent = e[e["estado"]=="Entregado"]
        otd = (ent["entregado_a_tiempo"]==True).mean()*100 if len(ent) else 0
        otd_pais = ent.groupby("pais_destino").apply(lambda x: (x["entregado_a_tiempo"]==True).mean()*100, include_groups=False)
        lines = "\n".join([f"  • {pa}: {v:.1f}%" for pa, v in otd_pais.items()])
        return (f"🚚 Logística y envíos:\n\n"
                f"• OTD global: {pct(otd)}\n"
                f"• Total envíos: {len(e):,}\n\n"
                f"OTD por país:\n{lines}\n\n"
                f"{'✅ Cumpliendo la meta del 90%.' if otd>=90 else '⚠️ Por debajo de la meta del 90%. Revisar transportadoras con más retrasos.'}")

    elif any(x in p_ for x in ["expansión","costa rica","estados unidos","internacional","país","usa"]):
        por_pais = g.groupby("pais")["ventas_cop"].sum()
        lines = "\n".join([f"  • {pa}: {cop(v,1)} ({v/por_pais.sum()*100:.1f}%)" for pa, v in por_pais.items()])
        return ("🌎 Expansión internacional:\n\n"
                f"{lines}\n\n"
                "Colombia sigue siendo el mercado base; Costa Rica (lanzado abr-2025) y Estados Unidos "
                "(lanzado oct-2025) están en rampa de adopción con crecimiento mes a mes positivo.")

    elif any(x in p_ for x in ["margen","rentabilidad","ganancia","utilidad"]):
        mg = p26.groupby("categoria")["margen_pct"].mean().sort_values(ascending=False) * 100
        lines = "\n".join([f"  • {cat}: {v:.1f}%" for cat, v in mg.items()])
        return (f"📊 Margen bruto promedio 2026:\n\n"
                f"• General: {p26['margen_pct'].mean()*100:.1f}%\n\n"
                f"Por categoría:\n{lines}\n\n"
                f"{'✅ El margen supera la meta del 60%.' if p26['margen_pct'].mean()*100>=60 else '⚠️ El margen está por debajo de la meta del 60%.'}")

    else:
        total26 = p26["total_cop"].sum()
        top_cat = p26.groupby("categoria")["total_cop"].sum().idxmax()
        crit = (inv["estado"]=="Crítico").sum()
        ent = e[e["estado"]=="Entregado"]
        otd = (ent["entregado_a_tiempo"]==True).mean()*100 if len(ent) else 0
        return (f"Entendido. Aquí un resumen rápido del negocio para orientarte:\n\n"
                f"📊 Ventas 2026 YTD: {cop(total26,1)} COP · Categoría líder: {top_cat}\n"
                f"🔁 Tasa de recompra: {pct(c['cliente_recurrente'].mean()*100)} · LTV prom: {cop(c['ltv_cop'].mean())}\n"
                f"📦 Stock: {crit} SKUs en estado crítico\n"
                f"🚚 OTD: {otd:.1f}%\n\n"
                f"Puedo profundizar en cualquier tema. Usa las preguntas sugeridas arriba o escríbeme directamente.\n"
                f"Temas disponibles: ventas, clientes, marketing, inventario, calidad/gluten, logística, expansión, márgenes.")


def llamar_claude(api_key: str, pregunta: str, contexto: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        historial = [{"role": m["role"], "content": m["content"]}
                     for m in st.session_state.ag_messages[:-1]]
        historial.append({"role": "user", "content": pregunta})
        response = client.messages.create(
            model="claude-opus-5",
            max_tokens=1024,
            system=CONTEXTO_PARANICE + "\n\n" + contexto,
            messages=historial
        )
        return response.content[0].text
    except Exception as ex:
        return f"Error al conectar con Claude: {ex}"

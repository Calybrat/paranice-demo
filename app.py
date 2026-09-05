import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from utils.formatters import (CSS, HEADER_CSS, asset_b64, BORDER, TEXT, MUTED,
                              PURPLE, CREAM, CREAM_LT, PINK, LAVENDER_LT)
from utils.visitas import registrar_visita, panel_solicitado, render_panel_visitas

st.set_page_config(
    page_title="Paranice · Panel de Negocio | Calybrat",
    page_icon="💜",
    layout="wide",
)

# El demo es de acceso libre: solo se deja constancia de la visita.
registrar_visita()

st.markdown(CSS + HEADER_CSS, unsafe_allow_html=True)

# Secciones agrupadas para que el panel sea fácil de recorrer
GRUPOS = [
    ("Vista general", [
        ("🏠  Dashboard General",        "p01_dashboard"),
    ]),
    ("Comercial", [
        ("🛒  Ventas Omnicanal",         "p02_ventas"),
        ("🏬  Retail & Sell-Out",        "p03_retail"),
        ("🥣  Portafolio & Precios",     "p04_portafolio"),
        ("💜  Clientes & Recompra",      "p05_clientes"),
        ("📣  Marketing & Contenido",    "p06_marketing"),
    ]),
    ("Operación", [
        ("🏭  Producción & Calidad",     "p07_produccion"),
        ("🚚  Logística & Cumplimiento", "p08_logistica"),
    ]),
    ("Dirección", [
        ("💰  Finanzas & Cartera",       "p09_finanzas"),
        ("🌎  Expansión Internacional",  "p10_expansion"),
        ("📄  Reportes Automáticos",     "p11_reportes"),
        ("🤖  Agente IA Paranice",       "p12_agente"),
    ]),
]
PAGES = {label: mod for _, items in GRUPOS for label, mod in items}

with st.sidebar:
    logo = asset_b64("logo_horizontal_crema.png")
    logo_html = (f'<img src="{logo}" style="width:150px;height:auto">' if logo
                 else '<div style="font-size:22px;font-weight:900;color:#f4e1c1">paranice</div>')
    st.markdown(f"""
    <div style="padding:10px 4px 6px">
      {logo_html}
      <div style="font-size:11px;color:{CREAM}99;margin-top:6px;font-weight:700;
        letter-spacing:.08em;text-transform:uppercase">Panel de negocio</div>
      <div style="height:2px;border-radius:99px;margin:14px 0 10px;
        background:linear-gradient(90deg,{PINK},{CREAM},transparent)"></div>
    </div>
    """, unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = list(PAGES.keys())[0]

    for grupo, items in GRUPOS:
        st.markdown(
            f'<div style="font-size:10px;font-weight:800;letter-spacing:.12em;'
            f'text-transform:uppercase;color:{CREAM}88;margin:12px 0 4px 4px">{grupo}</div>',
            unsafe_allow_html=True)
        for label, _mod in items:
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state.page = label

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    pj = asset_b64("personaje_3.png")
    pj_html = f'<img src="{pj}" style="height:54px;width:auto;margin-bottom:6px">' if pj else ""
    st.markdown(f"""
    <div style="padding:14px 16px 10px;text-align:center;border-top:1px solid {CREAM}33">
      {pj_html}
      <div style="font-size:10.5px;color:{CREAM}88;margin-bottom:2px">Construido por</div>
      <div style="font-size:14px;font-weight:900;color:{CREAM}">Calybrat</div>
      <div style="font-size:9.5px;color:{CREAM}66;margin-top:3px">© 2026 · Demo con datos simulados</div>
    </div>
    """, unsafe_allow_html=True)

# ── Panel interno de accesos (solo con ?accesos=… en la URL) ──────────────────
if panel_solicitado():
    render_panel_visitas()
    st.stop()

# ── Módulo activo ─────────────────────────────────────────────────────────────
module_name = PAGES[st.session_state.page]
try:
    mod = __import__(f"modules.{module_name}", fromlist=[module_name])
    mod.render()
except Exception as e:
    st.error(f"Error cargando módulo: {e}")
    import traceback
    st.code(traceback.format_exc())

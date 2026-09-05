"""
Paleta e identidad visual de Paranice.

Colores extraídos del CSS real de paranice.co (tema whynot-web):
  #2a1d65 morado principal · #f4e1c1 crema · #a299ba lavanda · #e6a4c4 rosa
Tipografía de marca: Filson Soft (Mostardesign) → se usa Nunito como
equivalente libre (geométrica redondeada, mismo carácter).
"""
import base64
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# ── Paleta de marca ──────────────────────────────────────────────────────────
PURPLE       = "#2a1d65"   # morado principal (logo)
PURPLE_DEEP  = "#1f165c"
PURPLE_MID   = "#4b3f7a"
PURPLE_SOFT  = "#6b5ca5"
LAVENDER     = "#a299ba"
LAVENDER_LT  = "#cfcadb"
LAVENDER_BG  = "#e8e4f3"
CREAM        = "#f4e1c1"
CREAM_LT     = "#faf3e6"
PINK         = "#e6a4c4"
PINK_LT      = "#f7e4ed"

# Roles de superficie (tema claro, como la marca)
BG      = "#fdfaf5"
SURF    = "#ffffff"
SURF2   = "#f7f4fb"
BORDER  = "#e3ddef"
TEXT    = PURPLE
MUTED   = "#8b83a3"
DIM     = LAVENDER_LT

# Semánticos
GOOD  = "#3f9e75"
WARN  = "#e0a03c"
BAD   = "#d95f6a"
INFO  = "#5b8fd6"
GREEN = GOOD
AMBER = WARN
RED   = BAD
SKY   = INFO
CORAL = "#ef7d57"

PALETTE = [PURPLE, PINK, CREAM, LAVENDER, GOOD, WARN, PURPLE_SOFT, INFO]
GRAD = [PURPLE, PINK]

_ASSETS = Path(__file__).parent.parent / "assets"


_DATA = Path(__file__).parent.parent / "data"


def leer_csv(nombre: str, **kw) -> pd.DataFrame:
    """Lee un archivo de data/, esté comprimido (.csv.gz) o no."""
    kw.setdefault("low_memory", False)
    for candidato in (_DATA / nombre, _DATA / f"{nombre}.gz"):
        if candidato.exists():
            return pd.read_csv(candidato, **kw)
    raise FileNotFoundError(f"No se encontró {nombre} en {_DATA}")


def asset_b64(nombre: str) -> str:
    """Devuelve un asset de marca como data URI listo para <img src=...>."""
    ruta = _ASSETS / nombre
    if not ruta.exists():
        return ""
    mime = "image/svg+xml" if ruta.suffix == ".svg" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(ruta.read_bytes()).decode()}"


def cop(v, decimals=0) -> str:
    """Formatea pesos: $1,23B · $456M · $12,3K"""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if abs(v) >= 1_000_000_000:
        return f"${v/1_000_000_000:,.{decimals}f}B"
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:,.{decimals}f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:,.{decimals}f}K"
    return f"${v:,.{decimals}f}"


def num(v, decimals=0) -> str:
    try:
        return f"{float(v):,.{decimals}f}"
    except (TypeError, ValueError):
        return "—"


def pct(v, decimals=1) -> str:
    try:
        return f"{float(v):.{decimals}f}%"
    except (TypeError, ValueError):
        return "—"


def light(fig: go.Figure, height: int = 340, title: str = "") -> go.Figure:
    """Aplica el tema claro de Paranice a una figura de Plotly.

    La leyenda nunca se dibuja arriba: a esa altura compite por el mismo
    espacio que el título y termina solapándolo en cuanto hay más de un
    par de series (o un donut con varias porciones). En vez de eso se
    ubica debajo del gráfico (barras/líneas) o a la derecha (donuts),
    con margen reservado a propósito para que nunca se monte encima de
    nada.
    """
    is_pie = any(getattr(tr, "type", None) == "pie" for tr in fig.data)
    n_entries = 0
    for tr in fig.data:
        if getattr(tr, "type", None) == "pie":
            labels = tr.labels
            n_entries += len(labels) if labels is not None else 0
        elif getattr(tr, "name", None):
            n_entries += 1
    show_legend = is_pie or n_entries >= 1

    if is_pie:
        legend = dict(orientation="v", x=1.02, y=0.5, xanchor="left", yanchor="middle",
                      font=dict(color=MUTED, size=11))
        margin = dict(l=6, r=132, t=40 if title else 16, b=16)
    elif show_legend:
        rows = 1 if n_entries <= 4 else (2 if n_entries <= 8 else 3)
        legend = dict(orientation="h", y=-0.30 - 0.14 * (rows - 1), x=0.5,
                      xanchor="center", yanchor="top", font=dict(color=MUTED, size=11))
        margin = dict(l=6, r=34, t=40 if title else 16, b=64 + 30 * rows)
    else:
        legend = dict()
        margin = dict(l=6, r=34, t=40 if title else 16, b=16)

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=PURPLE, family="Nunito, sans-serif"),
                   x=0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Nunito, -apple-system, system-ui, sans-serif", color=MUTED, size=12),
        height=height,
        margin=margin,
        legend=legend,
        showlegend=show_legend,
        hovermode="x unified",
        colorway=PALETTE,
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor="#efebf7", zeroline=False, tickfont=dict(color=MUTED))
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    return fig


# Alias retro-compatible
dark = light


def kpi(label: str, value: str, delta: str = "", delta_good: bool = True,
        icon: str = "", ayuda: str = "") -> str:
    """Tarjeta de KPI. `ayuda` explica en una línea cómo leer el indicador."""
    color = GOOD if delta_good else BAD
    delta_html = f'<p style="font-size:12px;font-weight:700;color:{color};margin:5px 0 0">{delta}</p>' if delta else ""
    icon_html  = f'<div style="font-size:20px;margin-bottom:6px;line-height:1">{icon}</div>' if icon else ""
    ayuda_html = f'<p style="font-size:10.5px;color:{MUTED};margin:6px 0 0;line-height:1.35">{ayuda}</p>' if ayuda else ""
    return f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:16px;padding:16px 16px;height:100%;
      box-shadow:0 1px 3px rgba(42,29,101,.06)">
      {icon_html}
      <p style="font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:{MUTED};margin:0;font-weight:700">{label}</p>
      <p style="font-size:25px;font-weight:800;color:{PURPLE};margin:5px 0 0;letter-spacing:-.5px;line-height:1.1">{value}</p>
      {delta_html}{ayuda_html}
    </div>"""


def panel(titulo: str, cuerpo_html: str, icono: str = "") -> str:
    """Panel de texto/insight con el look de la marca."""
    return f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:16px;padding:18px 20px;margin:6px 0 2px;
      box-shadow:0 1px 3px rgba(42,29,101,.06)">
      <p style="font-size:13px;font-weight:800;color:{PURPLE};margin:0 0 8px">{icono} {titulo}</p>
      <div style="font-size:12.5px;color:{MUTED};margin:0;line-height:1.7">{cuerpo_html}</div>
    </div>"""


def estado_color(estado: str) -> str:
    m = {"Crítico": BAD, "Bajo": WARN, "Normal": GOOD, "Alto": INFO,
         "Entregado": GOOD, "En tránsito": INFO, "Generado": MUTED,
         "Rechazado": BAD, "Cuarentena": WARN, "Aprobado": GOOD,
         "Vigente": GOOD, "Vencida 1-30": WARN, "Vencida 31-60": "#e08b3c",
         "Vencida 61-90": BAD, "Vencida +90": "#b3384a"}
    return m.get(estado, MUTED)


CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
  html, body, [class*="css"] {{ font-family:'Nunito',-apple-system,system-ui,sans-serif; }}
  .stApp {{ background:{BG}; color:{TEXT}; }}
  section[data-testid="stSidebar"] {{ background:{PURPLE}; border-right:none; }}
  section[data-testid="stSidebar"] * {{ color:{CREAM_LT}; }}
  section[data-testid="stSidebar"] .stButton button {{
      background:rgba(255,255,255,.06); color:{CREAM_LT} !important;
      border:1px solid rgba(244,225,193,.18); border-radius:12px;
      text-align:left; font-weight:700; font-size:13px; padding:8px 12px;
      transition:all .15s ease; }}
  section[data-testid="stSidebar"] .stButton button:hover {{
      background:{PINK}33; border-color:{PINK}; color:#fff !important; }}
  .block-container {{ padding-top:1.6rem !important; max-width:1500px; }}
  h1,h2,h3,h4 {{ color:{PURPLE} !important; font-family:'Nunito',sans-serif !important; font-weight:800 !important; }}
  div[data-testid="stMetricValue"] {{ color:{PURPLE}; }}
  .stDataFrame {{ border-radius:12px; overflow:hidden; border:1px solid {BORDER}; }}
  thead tr th {{ background:{LAVENDER_BG} !important; color:{PURPLE} !important; font-size:11.5px !important;
      text-transform:uppercase; letter-spacing:.05em; font-weight:800 !important; }}
  tbody tr:hover td {{ background:{PINK_LT} !important; }}
  div[data-baseweb="select"] > div {{ background:{SURF} !important; border-color:{BORDER} !important; border-radius:10px !important; }}
  div[data-baseweb="select"] span {{ color:{PURPLE} !important; }}
  .stMultiSelect span[data-baseweb="tag"] {{ background:{PURPLE} !important; color:#fff !important; }}
  .stMultiSelect span[data-baseweb="tag"] span {{ color:#fff !important; -webkit-text-fill-color:#fff !important; }}
  button[kind="primary"] {{ background:{PURPLE} !important; border:none !important; border-radius:12px !important; }}
  .stTabs [data-baseweb="tab"] {{ background:{SURF2}; border-radius:12px 12px 0 0; font-weight:700; color:{MUTED}; }}
  .stTabs [aria-selected="true"] {{ background:{SURF} !important; color:{PURPLE} !important; border-bottom:2px solid {PINK}; }}
  div[data-testid="stExpander"] {{ border:1px solid {BORDER} !important; background:{SURF} !important; border-radius:14px !important; }}
  div[data-testid="stExpander"] summary {{ font-weight:800; color:{PURPLE} !important; }}
  label, .stSelectbox label, .stSlider label {{ color:{MUTED} !important; font-weight:700 !important; font-size:12px !important; }}
  hr {{ border-color:{BORDER}; }}
</style>
"""

HEADER_CSS = f"""
<style>
  .pn-header {{ display:flex;align-items:center;gap:16px;padding:2px 0 }}
  .pn-logo-img {{ height:38px;width:auto }}
  .pn-title {{ font-size:23px;font-weight:900;color:{PURPLE};letter-spacing:-.4px;line-height:1.15 }}
  .pn-sub {{ font-size:12.5px;color:{MUTED};margin-top:3px;font-weight:600 }}
  .pn-rule {{ height:3px;border-radius:99px;
      background:linear-gradient(90deg,{PURPLE},{PINK} 45%,{CREAM} 80%,transparent);
      margin:14px 0 20px }}
  .pn-badge {{ display:inline-block;background:{LAVENDER_BG};color:{PURPLE};
      border:1px solid {LAVENDER_LT};border-radius:999px;
      padding:3px 12px;font-size:11px;font-weight:800;letter-spacing:.04em }}
  .pn-badge-pink {{ display:inline-block;background:{PINK_LT};color:#b3557f;
      border:1px solid {PINK};border-radius:999px;
      padding:3px 12px;font-size:11px;font-weight:800;letter-spacing:.04em }}
</style>
"""


def encabezado(titulo: str, subtitulo: str, personaje: str = "") -> str:
    """Encabezado de módulo con el logo real de Paranice."""
    logo = asset_b64("logo_horizontal_morado.png")
    logo_html = (f'<img src="{logo}" class="pn-logo-img" alt="Paranice">'
                 if logo else f'<div class="pn-title">paranice</div>')
    pj = asset_b64(personaje) if personaje else ""
    pj_html = (f'<img src="{pj}" style="height:56px;width:auto;margin-left:auto" alt="">'
               if pj else "")
    return f"""
    <div class="pn-header">
      {logo_html}
      <div style="border-left:2px solid {LAVENDER_LT};padding-left:16px">
        <div class="pn-title">{titulo}</div>
        <div class="pn-sub">{subtitulo}</div>
      </div>
      {pj_html}
    </div><div class="pn-rule"></div>"""

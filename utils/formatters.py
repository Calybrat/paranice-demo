import plotly.graph_objects as go

BG     = "#0b120d"
SURF   = "#121a14"
SURF2  = "#19231b"
BORDER = "rgba(255,255,255,0.08)"
TEXT   = "#f1f3ee"
MUTED  = "#8a9a86"
DIM    = "#3a4a3a"
GREEN  = "#4d9a5c"
CREAM  = "#e8c07d"
AMBER  = "#f59e0b"
CORAL  = "#f4714f"
RED    = "#ef4444"
SKY    = "#38bdf8"
GRAD   = [GREEN, CREAM]

PALETTE = [GREEN, CREAM, CORAL, "#38bdf8", "#a78bfa", RED, "#34d399", "#f59e0b"]


def cop(v, decimals=0) -> str:
    """Format COP value: 1.23B, 456M, 12.3K"""
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


def pct(v, decimals=1) -> str:
    try:
        return f"{float(v):.{decimals}f}%"
    except (TypeError, ValueError):
        return "—"


def dark(fig: go.Figure, height: int = 340, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=TEXT), x=0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, system-ui, sans-serif", color=MUTED, size=12),
        height=height,
        margin=dict(l=6, r=6, t=44 if title else 16, b=6),
        legend=dict(orientation="h", y=1.12, x=0, font=dict(color=MUTED, size=11)),
        hovermode="x unified",
        colorway=PALETTE,
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False, tickfont=dict(color=MUTED))
    return fig


def kpi(label: str, value: str, delta: str = "", delta_good: bool = True, icon: str = "") -> str:
    color = GREEN if delta_good else RED
    delta_html = f'<p style="font-size:12px;color:{color};margin:4px 0 0">{delta}</p>' if delta else ""
    icon_html  = f'<div style="font-size:22px;margin-bottom:8px">{icon}</div>' if icon else ""
    return f"""
    <div style="background:{SURF};border:1px solid {BORDER};border-radius:12px;padding:18px 16px;height:100%">
      {icon_html}
      <p style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:{MUTED};margin:0">{label}</p>
      <p style="font-size:26px;font-weight:800;color:{TEXT};margin:6px 0 0;letter-spacing:-.5px;line-height:1">{value}</p>
      {delta_html}
    </div>"""


def estado_color(estado: str) -> str:
    m = {"Crítico": RED, "Bajo": AMBER, "Normal": GREEN, "Alto": SKY,
         "Entregado": GREEN, "En tránsito": SKY, "Generado": MUTED,
         "Rechazado": RED, "Cuarentena": AMBER, "Aprobado": GREEN,
         "Confirmada": SKY, "En aduana": AMBER, "Recibida": GREEN}
    return m.get(estado, MUTED)


CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] {{ font-family:'Inter',-apple-system,system-ui,sans-serif; }}
  .stApp {{ background:{BG}; color:{TEXT}; }}
  section[data-testid="stSidebar"] {{ background:#080e09; border-right:1px solid {BORDER}; }}
  .block-container {{ padding-top:1.8rem !important; }}
  div[data-testid="stMetricValue"] {{ color:{TEXT}; }}
  .stDataFrame {{ border-radius:10px; overflow:hidden; }}
  thead tr th {{ background:{SURF2} !important; color:{MUTED} !important; font-size:12px !important; text-transform:uppercase; letter-spacing:.06em; }}
  tbody tr:hover td {{ background:rgba(77,154,92,.08) !important; }}
  div[data-baseweb="select"] > div {{ background:{SURF} !important; border-color:{BORDER} !important; }}
  div[data-baseweb="select"] span {{ color:{TEXT} !important; }}
  .stMultiSelect span[data-baseweb="tag"] {{ background:{GREEN}33 !important; }}
  button[kind="primary"] {{ background:linear-gradient(135deg,{GREEN},{CREAM}) !important; border:none !important; color:#12210f !important; }}
  .stTabs [data-baseweb="tab"] {{ background:{SURF}; border-radius:8px 8px 0 0; }}
  .stTabs [aria-selected="true"] {{ background:{GREEN}22 !important; }}
  div[data-testid="stExpander"] {{ border-color:{BORDER} !important; background:{SURF} !important; }}
</style>
"""

HEADER_CSS = f"""
<style>
  .cb-header {{ display:flex;align-items:center;gap:16px;padding:2px 0 }}
  .cb-logo {{ width:44px;height:44px;border-radius:11px;
    background:linear-gradient(135deg,{GREEN},{CREAM});
    display:flex;align-items:center;justify-content:center;
    font-size:22px;font-weight:900;color:#12210f;
    box-shadow:0 0 18px {GREEN}66 }}
  .cb-title {{ font-size:24px;font-weight:800;color:{TEXT};letter-spacing:-.4px }}
  .cb-sub {{ font-size:13px;color:{MUTED};margin-top:2px }}
  .cb-rule {{ height:1px;background:linear-gradient(90deg,{GREEN},{CREAM},transparent);margin:14px 0 20px }}
  .cb-badge {{ display:inline-block;background:{GREEN}22;color:{GREEN};
    border:1px solid {GREEN}44;border-radius:999px;
    padding:2px 12px;font-size:11px;font-weight:700;letter-spacing:.06em }}
  .cb-teal  {{ display:inline-block;background:{CORAL}22;color:{CORAL};
    border:1px solid {CORAL}44;border-radius:999px;
    padding:2px 12px;font-size:11px;font-weight:700;letter-spacing:.06em }}
</style>
"""

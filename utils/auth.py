import json
import datetime
import urllib.request
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml

_ROOT     = Path(__file__).parent.parent
_CONFIG   = _ROOT / "config.yaml"
_LOG_FILE = _ROOT / "visit_log.json"


def _load_config():
    if not _CONFIG.exists():
        st.error("config.yaml no encontrado. Corre auth_setup.py primero.")
        st.stop()
    with open(_CONFIG, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_ip() -> str:
    try:
        h = st.context.headers
        for key in ("X-Forwarded-For", "x-forwarded-for", "X-Real-Ip", "x-real-ip"):
            val = h.get(key, "")
            if val:
                return val.split(",")[0].strip()
    except Exception:
        pass
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=3) as r:
            return json.loads(r.read()).get("ip", "desconocida")
    except Exception:
        return "desconocida"


def _get_location(ip: str) -> dict:
    if not ip or ip in ("desconocida", "127.0.0.1", "::1"):
        return {"ciudad": "local", "pais": "—"}
    try:
        url  = f"http://ip-api.com/json/{ip}?fields=status,country,city,regionName"
        with urllib.request.urlopen(url, timeout=3) as r:
            data = json.loads(r.read())
        if data.get("status") == "success":
            return {
                "ciudad": data.get("city", "—"),
                "region": data.get("regionName", "—"),
                "pais":   data.get("country", "—"),
            }
    except Exception:
        pass
    return {"ciudad": "—", "pais": "—"}


def _log_visit(username: str, name: str):
    ip  = _get_ip()
    loc = _get_location(ip)
    log = []
    if _LOG_FILE.exists():
        try:
            log = json.loads(_LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            log = []
    log.append({
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "username":  username,
        "name":      name,
        "ip":        ip,
        "ciudad":    loc.get("ciudad", "—"),
        "region":    loc.get("region", "—"),
        "pais":      loc.get("pais", "—"),
    })
    _LOG_FILE.write_text(
        json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def require_login():
    """Muestra login si no autenticado. Retorna (name, username, authenticator)."""
    config = _load_config()
    auth = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    if not st.session_state.get("authentication_status"):
        st.markdown("""
        <style>
        [data-testid="stAppViewContainer"]{background:#0b120d}
        [data-testid="stHeader"]{display:none}
        div[data-testid="stForm"]{
          max-width:380px;margin:60px auto 0;padding:36px;
          background:#141f16;border-radius:16px;
          border:1px solid rgba(77,154,92,.25);
          box-shadow:0 0 40px rgba(77,154,92,.12)}
        </style>
        <div style="max-width:380px;margin:60px auto 0;padding:0 0 0">
          <div style="text-align:center;margin-bottom:24px">
            <div style="width:52px;height:52px;border-radius:14px;
              background:linear-gradient(135deg,#4d9a5c,#e8c07d);
              display:inline-flex;align-items:center;justify-content:center;
              font-size:24px;font-weight:900;color:#12210f;margin-bottom:14px">P</div>
            <div style="font-size:20px;font-weight:800;color:#fff">Paranice · Panel BI</div>
            <div style="font-size:12px;color:rgba(255,255,255,.35);margin-top:4px">Powered by Calybrat</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    auth.login(location="main", fields={
        "Form name": " ",
        "Username":  "Usuario",
        "Password":  "Contraseña",
        "Login":     "Entrar",
    })

    auth_status = st.session_state.get("authentication_status")
    name        = st.session_state.get("name", "")
    username    = st.session_state.get("username", "")

    if auth_status is False:
        st.error("Usuario o contraseña incorrectos.")
        st.stop()
    elif not auth_status:
        st.stop()

    flag = f"_visit_logged_{username}"
    if not st.session_state.get(flag):
        _log_visit(username, name)
        st.session_state[flag] = True

    return name, username, auth


def render_visit_log():
    """Panel de visitas — solo para el admin."""
    st.subheader("Registro de accesos")
    if not _LOG_FILE.exists():
        st.info("Aún no hay visitas registradas.")
        return
    try:
        log = json.loads(_LOG_FILE.read_text(encoding="utf-8"))
    except Exception:
        st.warning("No se pudo leer el log.")
        return
    if not log:
        st.info("Log vacío.")
        return

    import pandas as pd
    rows = []
    for e in log[::-1]:
        ubicacion = ", ".join(filter(lambda x: x and x != "—", [
            e.get("ciudad", ""), e.get("region", ""), e.get("pais", "")
        ])) or "—"
        rows.append({
            "Fecha / Hora": e.get("timestamp", ""),
            "Nombre":       e.get("name", ""),
            "Usuario":      e.get("username", ""),
            "Ubicación":    ubicacion,
            "IP":           e.get("ip", "—"),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"{len(log)} acceso(s) registrado(s).")

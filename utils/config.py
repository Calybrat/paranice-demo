"""
Lectura centralizada de credenciales y ajustes del panel.

Un solo sitio del que salen las llaves, para no tener que pegarlas a mano ni
repartirlas por el código. El orden de búsqueda es siempre el mismo:

  1. `st.secrets`      → producción (Streamlit Cloud: Settings → Secrets)
  2. variable de entorno → desarrollo local (`.env` o el shell)
  3. valor por defecto  → lo que se usa si no hay nada configurado

Así el mismo código corre en local, en Codespaces y en la nube sin cambios.
Para configurarlo: copia `.streamlit/secrets.example.toml` a
`.streamlit/secrets.toml` (o `.env.example` a `.env`) y llena lo que necesites.
Ninguno de los dos archivos reales se sube al repo: están en .gitignore.
"""
import os

try:
    import streamlit as st
except ImportError:      # permite importar este módulo fuera de Streamlit
    st = None


# Modelo por defecto del Agente IA. Se puede sobrescribir con
# ANTHROPIC_MODEL en el entorno o en secrets.
MODELO_AGENTE_DEFECTO = "claude-sonnet-5"


def get(nombre: str, defecto: str = "") -> str:
    """Devuelve un ajuste buscándolo en secrets, luego en el entorno."""
    if st is not None:
        try:
            if nombre in st.secrets:
                return str(st.secrets[nombre]).strip()
        except Exception:
            # No hay secrets.toml: es lo normal en local, se sigue de largo.
            pass
    return os.environ.get(nombre, defecto).strip()


def anthropic_api_key() -> str:
    """API key de Anthropic para el Agente IA. Vacío = no configurada."""
    return get("ANTHROPIC_API_KEY")


def modelo_agente() -> str:
    """Modelo que usa el Agente IA cuando hay API key."""
    return get("ANTHROPIC_MODEL", MODELO_AGENTE_DEFECTO)


def agente_configurado() -> bool:
    """True si el agente puede hablar con Claude sin pedirle nada al usuario."""
    return bool(anthropic_api_key())

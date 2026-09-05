"""
Carga de datos compartida.

Todos los módulos leen de aquí para que cada tabla se cargue UNA sola vez en
memoria (st.cache_data cachea por función, así que si cada módulo definiera su
propio loader se guardaría una copia por módulo). Además se usan tipos
`category` en las columnas de texto repetido, que reduce el consumo de memoria
del orden de 10x — importante para que el panel corra holgado en la nube.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

_DATA = Path(__file__).parent.parent / "data"


def _leer(nombre: str, **kw) -> pd.DataFrame:
    kw.setdefault("low_memory", False)
    for candidato in (_DATA / nombre, _DATA / f"{nombre}.gz"):
        if candidato.exists():
            return pd.read_csv(candidato, **kw)
    raise FileNotFoundError(f"No se encontró {nombre} en {_DATA}")


def _categorizar(df: pd.DataFrame, columnas) -> pd.DataFrame:
    for c in columnas:
        if c in df.columns:
            df[c] = df[c].astype("category")
    return df


@st.cache_data(show_spinner="Cargando ventas…")
def ventas(con_fecha: bool = True) -> pd.DataFrame:
    df = _leer("ventas.csv")
    df = _categorizar(df, ["mes", "tipo_documento", "canal", "tipo_canal", "pais", "ciudad",
                           "canal_captacion", "sku", "producto", "categoria", "documento_id",
                           "cliente_id"])
    for c in ["unidades", "precio_unitario_cop", "venta_cop", "costo_cop", "margen_cop"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], downcast="integer")
    for c in ["descuento_pct", "margen_pct"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], downcast="float")
    if con_fecha:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df


@st.cache_data(show_spinner="Cargando despachos…")
def despachos(con_fechas: bool = True) -> pd.DataFrame:
    df = _leer("despachos.csv")
    df = _categorizar(df, ["tipo_documento", "canal", "tipo_canal", "pais", "ciudad",
                           "transportadora", "estado", "despacho_id", "documento_id"])
    for c in ["dias_transito", "unidades", "valor_cop", "costo_logistico_cop"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], downcast="integer")
    if con_fechas:
        for c in ("fecha_pedido", "fecha_prometida", "fecha_entrega"):
            df[c] = pd.to_datetime(df[c], errors="coerce")
        df["mes"] = df["fecha_pedido"].dt.strftime("%Y-%m")
    return df


@st.cache_data(show_spinner="Cargando clientes…")
def clientes(con_fechas: bool = True) -> pd.DataFrame:
    df = _leer("clientes_d2c.csv")
    df = _categorizar(df, ["pais", "ciudad", "canal_captacion", "segmento"])
    if con_fechas:
        df["primera_compra"] = pd.to_datetime(df["primera_compra"])
        df["ultima_compra"] = pd.to_datetime(df["ultima_compra"])
    return df


@st.cache_data
def finanzas() -> pd.DataFrame:
    return _leer("finanzas_mensual.csv")


@st.cache_data
def cartera(con_fechas: bool = True) -> pd.DataFrame:
    df = _leer("cartera.csv")
    df = _categorizar(df, ["cliente", "tipo_canal", "pais", "estado"])
    if con_fechas:
        for c in ("fecha_factura", "fecha_vencimiento"):
            df[c] = pd.to_datetime(df[c])
    return df


@st.cache_data
def sellout() -> pd.DataFrame:
    return _categorizar(_leer("sellout.csv"),
                        ["mes", "cadena", "ciudad", "sku", "producto", "categoria"])


@st.cache_data
def produccion(con_fecha: bool = True) -> pd.DataFrame:
    df = _leer("produccion.csv")
    df = _categorizar(df, ["mes", "sku", "producto", "categoria", "turno", "linea", "estado_calidad"])
    if con_fecha:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df


@st.cache_data
def inventario() -> pd.DataFrame:
    return _leer("inventario.csv")


@st.cache_data
def marketing() -> pd.DataFrame:
    return _leer("marketing.csv")


@st.cache_data
def contenido() -> pd.DataFrame:
    return _leer("contenido.csv")


@st.cache_data
def productos() -> pd.DataFrame:
    return _leer("productos.csv")


@st.cache_data
def precios_canal() -> pd.DataFrame:
    return _leer("precios_canal.csv")


@st.cache_data
def canales() -> pd.DataFrame:
    return _leer("canales.csv")


@st.cache_data
def puntos_venta() -> pd.DataFrame:
    return _leer("puntos_venta.csv")


@st.cache_data
def proveedores() -> pd.DataFrame:
    return _leer("proveedores.csv")


@st.cache_data
def empleados() -> pd.DataFrame:
    return _leer("empleados.csv")

# CLAUDE.md — Paranice · Panel de Negocio (demo de Calybrat)

Este archivo lo lee Claude automáticamente al abrir el repo. Es el resumen operativo.
**El contexto completo está en [`docs/CONTEXTO_TECNICO.md`](docs/CONTEXTO_TECNICO.md)** — léelo
antes de hacer cualquier cambio que no sea trivial. Cubre también los repos hermanos
(`nutramerican-demo`, `cimpa-demo`, `calybrat-website`) y el inventario de APIs y conexiones.

---

## Qué es esto

Demo comercial que **Calybrat** (Juan David y Nico) construyó para **Paranice**, marca colombiana de
alimentos saludables (sin gluten, sin azúcar añadida, veganos, keto). Es un **panel de negocio en
Streamlit, en español, con 12 módulos**.

La tesis: Paranice **no es un e-commerce puro ni una marca de retail — es las dos cosas, en tres
países** (Colombia, Costa Rica, EE.UU.), y hoy esa información vive repartida entre WooCommerce, los
reportes de las cadenas, los Excel de producción y los informes del contador.

Es una **herramienta de venta**, no un producto entregado. Se abre sin usuario ni clave, a propósito.

---

## Comandos

```bash
pip install -r requirements.txt
streamlit run app.py            # http://localhost:8501
python3 data/generate_data.py   # regenera los 18 CSV de data/ (semilla fija = reproducible)
```

Panel oculto de visitas: agregar `?accesos=calybrat` a la URL.

---

## Arquitectura en 6 líneas

```
app.py               navegación (4 grupos de menú) + sidebar de marca + import dinámico de módulos
utils/formatters.py  paleta, cop()/num()/pct(), light() para gráficas, kpi()/panel()/encabezado(), CSS
utils/datos.py       ÚNICA fuente de carga de datos, cacheada con @st.cache_data
utils/config.py      ÚNICA fuente de credenciales y ajustes: st.secrets → entorno → defecto
utils/visitas.py     registro de visitas + panel oculto
modules/p01…p12_*.py un módulo por pantalla, cada uno expone render()
data/                generate_data.py + 18 CSV versionados (para que el deploy no tenga que generarlos)
```

**Repos hermanos** (misma estructura, distinto cliente): `Calybrat/nutramerican-demo` (15 módulos,
el más grande) · `nicolasgort01/cimpa-demo` (el primero, todavía con login) ·
`nicolasgort01/calybrat-website` (sitio estático en Netlify).

Los 12 módulos: `p01` Dashboard · `p02` Ventas Omnicanal · `p03` Retail & Sell-Out ·
`p04` Portafolio & Precios · `p05` Clientes & Recompra · `p06` Marketing & Contenido ·
`p07` Producción & Calidad · `p08` Logística & Cumplimiento · `p09` Finanzas & Cartera ·
`p10` Expansión Internacional · `p11` Reportes Automáticos · `p12` Agente IA.

---

## Reglas que no se rompen

1. **Ningún módulo lee un CSV directamente.** Siempre `from utils import datos`.
   Motivo: cada `@st.cache_data` por módulo guardaba su propia copia — se llegó a ~1,5 GB y eso tumba
   Streamlit Cloud. Hoy son ~224 MB con una sola copia por tabla.
2. **No convertir columnas de texto a `dtype category`.** `utils.datos._categorizar()` es un **no-op a
   propósito**. Con `category`, `groupby` devuelve combinaciones inexistentes y aparecían filas con
   venta $0 (p. ej. Paranice US facturando cero antes de existir).
3. **No activar `runOnSave`** en `.streamlit/config.toml`. `registrar_visita()` escribe
   `visit_log.json` dentro del directorio vigilado → bucle infinito de recargas.
4. **Toda gráfica pasa por `light(fig, alto, titulo)`.** Ahí vive el tema y la lógica de leyendas
   (debajo en barras/líneas, al lado en donuts) que evita que se solapen con el título.
5. **Toda plata se formatea con `cop()`**, todo porcentaje con `pct()`. Nada de f-strings crudos.
6. **Colores solo desde las constantes** de `utils/formatters.py` (`PURPLE #2a1d65`, `CREAM #f4e1c1`,
   `PINK #e6a4c4`, `GOOD/WARN/BAD`, `PALETTE`). Nunca hardcodear un hex nuevo.
7. **Ninguna credencial se escribe en el código ni se pide en la UI.** Todo sale de
   `utils/config.py` (`st.secrets` → variable de entorno → defecto). Las plantillas son
   `.streamlit/secrets.example.toml` y `.env.example`; los archivos reales están en `.gitignore`.
8. **Todo en español**: código, comentarios, docstrings y UI.
9. **La fecha de corte es el 31 de agosto de 2026** y está fijada en 7 archivos
   (ver la tabla en `docs/CONTEXTO_TECNICO.md` §3.4). Si cambias una, cámbialas todas.

---

## Estilo de la UI (esto vende el demo)

- Cada KPI dice **qué significa para el negocio**, no solo el número.
- Cada módulo cierra con una lectura que **propone una decisión**, no un resumen.
- Los títulos de gráficas son lenguaje humano ("Dónde se agota el producto", "Quién debe la plata"),
  nunca nombres de columnas.
- Patrón de módulo: `encabezado()` → filtros → fila(s) de `kpi()` → `st.tabs` con gráficas → `panel()` de lectura.

---

## Datos

Todo sintético salvo lo que se tomó de fuentes públicas: **catálogo y precios reales** de
`paranice.co` (Store API de WooCommerce, ago-2026), categorías, canales, brecha de precios observada,
identidad de marca y perfil de empresa (LinkedIn).

Horizonte **ene-2025 → 31-ago-2026**. Semilla `default_rng(11)` → reproducible.
Volumen: 173.200 líneas de venta · 70.241 documentos · $35,7 B COP · 40.865 clientes D2C · 150 PDV.

Las reglas de negocio codificadas (estacionalidad, rampa de canal, pedido mínimo $50.000, OTIF,
probabilidades de pago de cartera, gluten en ppm) están documentadas en
`docs/CONTEXTO_TECNICO.md` §1.3. **Léelas antes de tocar `data/generate_data.py`.**

---

## Conexiones

El único servicio externo opcional es la **API de Anthropic** para el Agente IA (módulo 12). Se
configura con `ANTHROPIC_API_KEY` en `.streamlit/secrets.toml` o `.env` — copia la plantilla
correspondiente. Sin llave, el agente corre en modo demo, que es el comportamiento correcto para un
demo enviado en frío. El inventario completo de APIs, plataformas y conectores está en
`docs/CONTEXTO_TECNICO.md` §5.

---

## Commits

- Mensaje en español, asunto corto + cuerpo que explica **el porqué**.
- Si verificaste, dilo: *"Verificado: los 12 módulos y la navegación completa corren sin errores."*
- Firma la coautoría de Claude con `Co-Authored-By:`.
- Rama de trabajo actual: `claude/claude-teams-context-docs-3peucs`.

---

## Antes de dar un cambio por bueno

No hay tests ni CI. La verificación es manual:
```bash
streamlit run app.py
```
y navegar **los 12 módulos**, con sus pestañas y filtros, mirando que ninguno lance error y que las
gráficas no se solapen.

Como mínimo, esta prueba de humo (importa los 12 módulos y verifica que exponen `render()`):
```bash
python3 -c "
import importlib, sys; sys.path.insert(0, '.')
mods = ['p01_dashboard','p02_ventas','p03_retail','p04_portafolio','p05_clientes','p06_marketing',
        'p07_produccion','p08_logistica','p09_finanzas','p10_expansion','p11_reportes','p12_agente']
[print(m, 'OK') for m in mods if callable(getattr(importlib.import_module('modules.'+m), 'render'))]
"
```

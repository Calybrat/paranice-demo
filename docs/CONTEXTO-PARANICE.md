# Contexto completo · Demo Paranice de Calybrat

> **Para qué existe este documento**
> Es la memoria del proyecto. Está escrito para que cualquiera —una persona nueva
> del equipo o una cuenta compartida de Claude (Teams)— pueda leerlo una vez y
> quedar con el mismo contexto que tienen hoy Juan David y Nico, sin haber estado
> en ninguna de las conversaciones anteriores.
>
> Si vas a subir contexto a Claude Teams, **este es el archivo que se sube**.
> Instrucciones de cómo hacerlo: `docs/ONBOARDING-CLAUDE-TEAMS.md`.

- **Repositorio:** `github.com/Calybrat/paranice-demo`
- **Rama de trabajo actual:** `claude/claude-teams-context-docs-3peucs` (idéntica a `main`)
- **Última actualización de este documento:** 6 de septiembre de 2026
- **Autores del repo:** `Calybrat` (Juan David) y `nicolasgort01` (Nico)

---

## Índice

1. [Resumen en 10 líneas](#1-resumen-en-10-líneas)
2. [Quién es quién](#2-quién-es-quién)
3. [El negocio de Paranice](#3-el-negocio-de-paranice)
4. [Qué construimos: el demo](#4-qué-construimos-el-demo)
5. [Los 12 módulos, uno por uno](#5-los-12-módulos-uno-por-uno)
6. [Modelo de datos](#6-modelo-de-datos)
7. [Reglas de negocio codificadas en el generador](#7-reglas-de-negocio-codificadas-en-el-generador)
8. [Las cifras que el demo muestra hoy](#8-las-cifras-que-el-demo-muestra-hoy)
9. [Historia del proyecto y decisiones técnicas](#9-historia-del-proyecto-y-decisiones-técnicas)
10. [Convenciones de código y de escritura](#10-convenciones-de-código-y-de-escritura)
11. [Cómo correrlo, desplegarlo y regenerar datos](#11-cómo-correrlo-desplegarlo-y-regenerar-datos)
12. [Estado actual, deuda técnica y roadmap](#12-estado-actual-deuda-técnica-y-roadmap)
13. [Glosario](#13-glosario)

---

## 1. Resumen en 10 líneas

- **Calybrat** construyó un **demo comercial** para **Paranice**, marca colombiana de alimentos saludables.
- Es un **panel de negocio (BI) en Streamlit**, en español, con **12 módulos**.
- La tesis del demo: Paranice **no es un e-commerce puro ni una marca de retail: es las dos cosas, en tres países**, y hoy esa información vive repartida entre WooCommerce, los reportes de las cadenas, Excel de producción y los informes del contador.
- **Los datos transaccionales son simulados** (`data/generate_data.py`). Lo que sí es real: catálogo, precios, categorías, canales, identidad de marca y perfil de empresa, tomados de fuentes públicas.
- Horizonte de datos: **enero 2025 → 31 de agosto de 2026** (esa fecha es "hoy" en todo el demo).
- **Acceso libre**: el demo se abre sin usuario ni clave, a propósito, para poder enviárselo en frío al cliente.
- Cada visita queda registrada (fecha, IP, ciudad); el registro se ve con `?accesos=calybrat` en la URL.
- Escala: **173.200 líneas de venta · 70.241 documentos · $35,7 B COP históricos · 40.865 clientes D2C**.
- Stack: Python + Streamlit + pandas + Plotly (+ `anthropic` opcional para el módulo del agente).
- Desplegable en Streamlit Cloud; los CSV van versionados en el repo para que el deploy no tenga que generarlos.

---

## 2. Quién es quién

| Quién | Rol | Aparece en el repo como |
|---|---|---|
| **Calybrat** | La empresa que construye. Es quien firma el demo ("Construido por Calybrat"). | Autor de commits `Calybrat` |
| **Juan David** | Socio de Calybrat. Autor de la mayoría de los commits de producto. | `Calybrat` · `juandavidmunevar19@gmail.com` |
| **Nico** | Socio de Calybrat. Autor de los commits de arreglos visuales y devcontainer. | `nicolasgort01` |
| **Paranice** | El cliente objetivo del demo. Marca de alimentos saludables, Bogotá, fundada en 2019 (antes "Why Not"). | — |

**Lo importante para entender el tono del proyecto:** el demo es una **herramienta de venta**.
No es un producto entregado, es la prueba de que Calybrat entiende el negocio del cliente mejor que
un dashboard genérico. Por eso cada módulo tiene una "lectura del período" en lenguaje de negocio y
no solo gráficas.

---

## 3. El negocio de Paranice

### 3.1 Qué vende

Alimentos "indulgentes pero nutritivos": **libres de gluten, sin azúcar añadida, veganos y keto friendly**.
**28 referencias en 6 categorías** (catálogo real, tomado de la API pública de WooCommerce de
`paranice.co/wp-json/wc/store/products`, agosto 2026):

| Categoría | Referencias | Presentación | Rango de PVP propio |
|---|---|---|---|
| **GranOLAS** | Vanilla Shortbread, Chip Cookie, Fudge Cake, Pistachio Cookie | 300 g | $37.950 – $44.950 |
| **Esparcibles** (cremas de nueces) | Buttery Pistachio Cookie, Golden Butter Cookie, Peanutty Banana Shake, Creamy Cocoa Hazelnut, Crunchy Cocoa Hazelnut, Golden Cinnamon Roll, Baby Spreads | 200 g / 45 g | $19.500 – $63.500 |
| **Pancakes & Waffles** | Almendra (Vainilla, Choco Chips, Churro) · Avena (Banano, Brownie, Vainilla) | 285 g / 300 g | $32.890 – $41.690 |
| **Avena & Harinas** | Avena en hojuelas, Harina de avena, Harina de almendra | 1000 g / 250 g | $31.350 – $34.650 |
| **Combos** | Three Pack GranOLA, Three Pack Spread, Three Pack Mezclas, Perfect Mix & Match, Mini Wafflera, Deck de Cartas, Rompecabezas | surtido / kit | $69.258 – $128.774 |
| **Merch** | New Year Resolution | kit | $100.000 |

El catálogo completo con SKU, costo unitario, atributos (sin gluten / vegano / sin azúcar / keto) y
fecha de lanzamiento está codificado en `data/generate_data.py` (constante `PRODUCTOS`) y se
materializa en `data/productos.csv`.

### 3.2 Dónde vende — los 8 canales

Esta tabla es **el corazón del demo**: explica por qué el mismo producto vale distinto en cada lado
y por qué crecer en retail aprieta la caja.

| Canal | Tipo | País | Factor PVP | Margen del canal | Plazo de pago | Peso en el mix | Lanzamiento |
|---|---|---|---|---|---|---|---|
| E-commerce propio (paranice.co) | D2C | Colombia | 1,00× | 0 % | 0 días | 17,5 % | ene-2025 |
| Éxito | Retail | Colombia | 1,11× | 32 % | 60 días | 23,0 % | ene-2025 |
| Carulla | Retail | Colombia | 1,13× | 32 % | 60 días | 15,0 % | abr-2025 |
| Rappi | Marketplace | Colombia | 1,15× | 25 % | 30 días | 7,5 % | ene-2025 |
| Fithub | Especializado | Colombia | 1,23× | 30 % | 45 días | 7,0 % | jun-2025 |
| Tiendas naturistas | Especializado | Colombia | 1,18× | 28 % | 45 días | 7,5 % | ene-2025 |
| Paranice US (paranice.us) | Internacional | EE.UU. | 1,30× | 0 % | 15 días | 11,5 % | oct-2025 |
| Distribuidor CR | Internacional | Costa Rica | 1,22× | 30 % | 45 días | 5,5 % | may-2025 |

- **Factor PVP** = cuánto le cuesta el producto al consumidor en ese canal frente al PVP de la tienda propia.
- **Margen del canal** = lo que se queda el canal sobre el PVP (0 en venta directa).
- **Brecha real observada** (dato público, no inventado): GranOLA Pistacho 300 g cuesta
  **$44.950 en paranice.co, $49.900 en Éxito y $55.400 en Fithub**.

### 3.3 Reglas del canal propio

- Pedido mínimo **$50.000** (regla real del sitio, codificada en el generador de ventas).
- Pasarela: **Mercado Pago**. Email marketing: **Omnisend**. CMS/tienda: **WooCommerce**.
- Blog de recetas propio con secciones: Baked Goods, Brunch, Desserts, Bebidas y Helados, Recipe,
  Snacks, The Paranice Lab. En el demo es un activo medible, no un adorno.

### 3.4 Operación física

- **Puntos de venta:** 150 PDV en 4 cadenas — Éxito (46, formatos WOW / Superior / Vecino),
  Carulla (28, FreshMarket / Express), Fithub (14), tiendas naturistas (62).
- **Ciudades Colombia:** Bogotá (42 %), Medellín (19 %), Cali (12 %), Barranquilla (9 %),
  Bucaramanga (7 %), Cartagena (5 %), Pereira (4 %), Manizales (2 %).
- **CEDIS:** CEDI Bogotá (planta, 70 %), Cross-dock Medellín (12 %), 3PL Miami (12 %),
  Distribuidor San José (6 %).
- **Proveedores (8):** avena certificada GF de Finlandia, almendra de California, pistacho/macadamia
  de Perú, cacao de Ecuador, maní, endulzantes, empaque y marañón en Colombia.
- **Equipo:** 112 personas activas en 8 áreas (banda 51–200 de LinkedIn). Producción es la más
  grande (41). La nómina de planta ya está dentro del COGS; en el P&G solo entra la
  administrativa y comercial, para no contarla dos veces.

### 3.5 El diferencial que sostiene la marca

El claim **"libre de gluten"** depende de evitar contaminación cruzada. Cada lote se ensaya en
**ppm de gluten** y el límite internacional es **20 ppm**. En el demo:

- `> 20 ppm` → lote **Rechazado** (no sale al mercado).
- `15–20 ppm` → **Cuarentena**.
- resto → **Aprobado**.

Esto no es un detalle de laboratorio: es riesgo sanitario y reputacional, y por eso tiene módulo propio.

### 3.6 Identidad de marca (real, tomada del sitio)

| Elemento | Valor |
|---|---|
| Morado principal | `#2a1d65` |
| Crema | `#f4e1c1` |
| Lavanda | `#a299ba` |
| Rosa | `#e6a4c4` |
| Tipografía de marca | Filson Soft (Mostardesign) |
| Equivalente libre usado | **Nunito** (geométrica redondeada, mismo carácter) |
| Assets | Logo horizontal en morado y crema, favicon, 7 personajes ilustrados, nubes SVG |

Todo eso vive en `assets/` y en la paleta de `utils/formatters.py`.

---

## 4. Qué construimos: el demo

### 4.1 Stack

```
Python 3.11
streamlit >= 1.35      · UI, navegación, caché
pandas    >= 2.0       · datos (probado también con pandas 3)
numpy     >= 1.24      · generación de datos
plotly    >= 5.18      · todas las gráficas
anthropic >= 0.25      · opcional, solo para el módulo 12 (Agente IA)
```

### 4.2 Estructura de archivos

```
app.py                    navegación, sidebar de marca, carga dinámica de módulos
utils/formatters.py       paleta, helpers de formato (cop/num/pct), tema de gráficas,
                          componentes HTML (kpi, panel, encabezado), CSS global
utils/datos.py            carga de datos compartida y cacheada — TODOS los módulos leen de aquí
utils/visitas.py          registro de visitas (IP + ciudad) y panel oculto de accesos
modules/p01…p12_*.py      un archivo por módulo, cada uno expone render()
data/generate_data.py     generador de todos los datos del demo (772 líneas)
data/*.csv(.gz)           18 datasets generados, versionados en el repo
assets/                   logo, favicon, personajes, nubes
.streamlit/config.toml    tema claro de marca, sin telemetría, toolbar mínima
.devcontainer/            Codespaces: instala requirements y levanta streamlit en el puerto 8501
visit_log.json            registro de visitas (se reinicia en cada despliegue de Streamlit Cloud)
```

### 4.3 Cómo funciona la navegación

`app.py` define `GRUPOS`: cuatro grupos de menú (**Vista general · Comercial · Operación · Dirección**)
que mapean etiqueta → nombre de módulo. El módulo activo se guarda en `st.session_state.page` y se
importa dinámicamente con `__import__("modules.<nombre>")`, llamando a su `render()`.
Si un módulo revienta, la excepción se muestra en pantalla con el traceback (útil en demo, hay que
revisarlo antes de producción).

---

## 5. Los 12 módulos, uno por uno

Cada módulo sigue el mismo patrón: **encabezado de marca → filtros → fila(s) de KPIs → pestañas con
gráficas → paneles de "lectura" en lenguaje de negocio**.

### p01 · Dashboard General (Vista general)
El estado del negocio en una pantalla. Filtros de período (último mes / 3 meses / 2026 YTD / histórico),
país y tipo de canal.
**KPIs:** ventas del período con delta vs. período anterior · margen bruto (meta 58 %) · EBITDA ·
ticket promedio web · cobertura retail en PDV · OTIF a cadenas (meta 95 %) · cartera vencida · recompra web.
**Gráficas:** ventas mensuales apiladas por tipo de canal · mix de canales (donut) · top 8 productos ·
ventas por categoría · margen bruto por tipo de canal.
**Cierre:** panel "Lectura del período" + panel "Qué necesita atención hoy" + expander con tres tablas
de alertas (inventario crítico, lotes con hallazgo de calidad, quiebres en góndola).

### p02 · Ventas Omnicanal (Comercial)
Todo lo facturado, por canal, categoría, ciudad y país.
**KPIs:** ventas · unidades · documentos · margen bruto · precio medio por unidad · peso del canal propio.
**Pestañas:** Evolución (ventas mensuales por canal, crecimiento mes a mes, cambio del mix) ·
Geografía (ciudades de Colombia, países, dónde vende cada tipo de canal) · Detalle por canal.

### p03 · Retail & Sell-Out (Comercial)
El módulo que traduce "qué pasa en la góndola".
**KPIs:** PDV activos · sell-out en unidades y valor a PVP · conversión sell-in→sell-out (ideal 90–100 %) ·
rotación und/PDV/mes · días sin stock · OTIF y fill rate.
**Pestañas:** Sell-in vs Sell-out · Quiebres y cobertura (incluye el cálculo de "venta que se está
dejando sobre la mesa") · Desempeño por SKU (top y bottom 10 por rotación, decisión de surtido).

### p04 · Portafolio & Precios (Comercial)
Las 28 referencias, su margen y la arquitectura de precios por canal.
**KPIs:** referencias activas · % de catálogo sin gluten · % vegano · más vendido 2026 · brecha de precio máxima.
**Pestañas:** Arquitectura de precios (elige un SKU y ve su PVP y el margen que le queda a Paranice en
cada canal) · Rentabilidad por referencia (burbujas volumen vs. margen) · Catálogo completo.
**Mensaje central:** el conflicto de canal es el punto ciego más caro de una marca omnicanal.

### p05 · Clientes & Recompra (Comercial)
Solo canal propio (D2C).
**KPIs:** clientes · recompra (referencia D2C 30 %) · LTV · CAC · LTV/CAC (meta >3×) · clientes en riesgo de fuga.
**Pestañas:** Adquisición y recompra · Segmentos (Embajador / Fiel / Repite / Primera compra) ·
Recuperables (lista accionable de quienes ya compraron 2+ veces y llevan >120 días sin volver).

### p06 · Marketing & Contenido (Comercial)
**KPIs:** inversión en pauta · ingresos atribuidos · ROAS (meta 3×) · CAC · peso de canales propios
(email, WhatsApp, SEO) · CTR.
**Pestañas:** Rendimiento por canal (Meta, Google, TikTok, Omnisend, WhatsApp, Influencers, Orgánico) ·
Evolución mensual · Blog y contenido (visitas y pedidos asistidos por sección).

### p07 · Producción & Calidad (Operación)
**KPIs:** lotes producidos · aprobación de calidad (meta 98 %) · gluten promedio en ppm (límite 20) ·
lotes fuera de norma · merma (meta <3 %) · costo de lo rechazado.
**Pestañas:** Calidad y gluten (distribución de ppm, evolución mensual) · Planta (merma por línea,
cumplimiento por turno, plan vs. real) · Inventario y proveedores (valor del inventario, referencias
críticas, sobre-stock, scoring de proveedores).

### p08 · Logística & Cumplimiento (Operación)
**KPIs:** OTIF a cadenas · fill rate · entregas a tiempo al consumidor · días de entrega web ·
costo logístico (absoluto y como % de la venta) · despachos en tránsito.
**Pestañas:** Cumplimiento a cadenas (por qué se cae el OTIF, traducción a plata) ·
Entregas al consumidor (por transportadora y ciudad) · Costo logístico por tipo de canal.

### p09 · Finanzas & Cartera (Dirección)
**KPIs:** ingresos · margen bruto · EBITDA · peso de la nómina · cartera abierta y % vencida ·
DSO (objetivo <60 días).
**Pestañas:** Resultado mensual (waterfall de dónde sale y a dónde se va el margen) ·
Cartera y cobranza (aging, quién debe, recaudo por mes de emisión) · Nómina por área y riesgo de rotación.

### p10 · Expansión Internacional (Dirección)
Colombia, Costa Rica y Estados Unidos comparados **por salud, no solo por tamaño**: participación,
margen bruto por mercado, costo de entregar en cada uno, mix de categorías por país.

### p11 · Reportes Automáticos (Dirección)
Cinco documentos HTML autocontenidos, con la identidad de Paranice y el pie "Powered by Calybrat",
que se descargan y se imprimen a PDF con Ctrl+P:
1. **Reporte ejecutivo mensual** — para junta directiva.
2. **Reporte de retail y sell-out** — el documento para sentarse a negociar con Éxito o Carulla.
3. **Reporte de clientes y recompra** — para marketing y CRM.
4. **Reporte de calidad y gluten** — respalda el claim ante clientes y autoridades.
5. **Reporte de cartera y cobranza** — para finanzas y la reunión de cobro.

### p12 · Agente IA Paranice (Dirección)
Chat en español sobre los datos del negocio. Dos modos:
- **Modo demo (por defecto, sin API key):** `responder_demo()` hace *matching* por palabras clave sobre
  8 temas (resumen del mes, margen por canal, quiebres de stock, cartera, recompra/CAC, calidad de
  gluten, mercados internacionales, portafolio) y arma la respuesta con cifras reales calculadas al vuelo.
- **Modo Claude (con API key de Anthropic pegada en la UI):** manda a la API el prompt `CONTEXTO`
  (quién es Paranice, portafolio, canales, diferencial) + `resumen_datos()` (un bloque compacto con
  las cifras del negocio al 31-ago-2026) + el historial de la conversación.
- 8 preguntas sugeridas en botones. El modelo está fijado en el código: ⚠️ hoy dice `claude-sonnet-4-5`,
  que conviene actualizar (ver §12).

---

## 6. Modelo de datos

Todo se genera con `python3 data/generate_data.py`. Semilla fija: `np.random.default_rng(11)`
→ **los datos son reproducibles**. Horizonte: `INICIO = 2025-01-01` → `HOY = 2026-08-31`. TRM de
referencia: **4.100 COP/USD**.

| Archivo | Filas | Columnas | Qué es |
|---|---:|---:|---|
| `productos.csv` | 28 | 13 | Catálogo: SKU, nombre, categoría, presentación, PVP propio, costo, atributos, lanzamiento, margen bruto % |
| `canales.csv` | 8 | 8 | Canal, tipo, país, factor PVP, margen del canal, plazo de pago, peso en el mix, lanzamiento |
| `precios_canal.csv` | 224 | 11 | 28 SKU × 8 canales: PVP al consumidor, precio que factura Paranice, margen y brecha vs. tienda propia |
| `puntos_venta.csv` | 150 | 6 | PDV por cadena, formato, ciudad, zona, apertura |
| `cedis.csv` | 4 | 5 | Centros de distribución y su peso |
| `proveedores.csv` | 8 | 10 | Proveedor, país, moneda, lead time, especialidad y scores (calidad/puntualidad/precio/general) |
| `empleados.csv` | 112 | 11 | Persona, área, sede, contrato, ingreso, antigüedad, salario, riesgo de rotación |
| **`ventas.csv.gz`** | **173.200** | 20 | Línea de venta: fecha, documento, canal, país, ciudad, cliente, SKU, unidades, precio, descuento, venta, costo, margen |
| **`despachos.csv.gz`** | **70.241** | 19 | Un despacho por documento: fechas prometida/entrega, transportadora, estado, fill rate, OTIF, costo logístico |
| **`clientes_d2c.csv.gz`** | **40.865** | 16 | Cliente del canal propio: pedidos, LTV, ticket, NPS, segmento, días sin comprar, riesgo de fuga |
| `sellout.csv` | 10.079 | 13 | Mes × cadena × ciudad × SKU: sell-in, sell-out, rotación, días sin stock, inventario en cadena |
| `cartera.csv` | 3.205 | 12 | Factura B2B: fechas, plazo, valor, días de mora, estado, pagada |
| `produccion.csv` | 1.058 | 17 | Lote: unidades planeadas/producidas, merma, turno, línea, gluten ppm, estado de calidad, costo |
| `inventario.csv` | 112 | 13 | CEDI × SKU: stock, venta diaria, días de cobertura, estado, lotes por vencer |
| `marketing.csv` | 140 | 10 | Mes × canal: inversión, impresiones, clics, pedidos, clientes nuevos, ingresos, CAC, ROAS |
| `contenido.csv` | 140 | 6 | Mes × sección del blog: publicaciones, visitas, pedidos asistidos, tiempo medio |
| `finanzas_mensual.csv` | 20 | 11 | P&G por mes: ingresos, COGS, margen bruto, marketing, logística, nómina, otros, EBITDA |

Los tres archivos grandes van comprimidos (`.csv.gz`) y `utils/datos._leer()` los encuentra con o sin
la extensión `.gz`.

### Cómo se encadena la generación

```
gen_maestros()      → productos, canales, proveedores, cedis
gen_precios_canal() → precios por SKU × canal
gen_puntos_venta()  → 150 PDV
gen_ventas()        → el dataset madre (todo lo demás se deriva de aquí)
gen_clientes_d2c()  ← ventas
gen_sellout()       ← ventas + PDV + precios
gen_despachos()     ← ventas
gen_cartera()       ← ventas + canales
gen_produccion()    ← productos + ventas
gen_inventario()    ← productos + ventas
gen_marketing()     ← ventas + clientes   (y genera contenido.csv)
gen_empleados()
gen_finanzas()      ← ventas + marketing + empleados + despachos
```

---

## 7. Reglas de negocio codificadas en el generador

Esto es lo que hace que los datos "se sientan" reales. Si alguien va a tocar el generador, tiene que
conocer estas reglas:

**Ventas**
- Facturación base del mes 1: **$1.950 M COP**, con crecimiento compuesto de **1,6 % mensual**.
- **Estacionalidad**: enero 1,28× (propósitos saludables) · noviembre 1,32× y diciembre 1,20× (regalo) ·
  julio 0,86× (bajo).
- **Rampa de canal**: un canal recién lanzado arranca en 45 % de su potencial y llega a 100 % en 240 días.
- Un SKU solo se puede vender después de su fecha de lanzamiento.
- **D2C**: 1–3 ítems por pedido, descuentos de 0/5/10/15 %, y si el pedido queda bajo **$50.000** se le
  agrega un ítem — la regla real del sitio.
- **B2B**: órdenes de compra (Poisson, media 2,2 por canal/día) de 3 a 8 SKU, repartidas con Dirichlet.
- **Base de clientes**: la probabilidad de que un pedido sea de cliente nuevo baja de 78 % a 56 % a
  medida que avanza el tiempo (la base madura); los compradores recientes tienen 70 % de probabilidad
  de ser los que vuelven.

**Cumplimiento (despachos)**
- SLA: D2C Colombia 3 días · EE.UU. 7 · Costa Rica 6. B2B: retail 4 · marketplace 3 · especializado 5 ·
  internacional 12.
- Probabilidad de entrega a tiempo: 93 % retail, 95 % marketplace, 94 % especializado, 88 % internacional.
- **Fill rate**: 94 % de las órdenes salen completas; el resto cae a una normal centrada en 86 %.
- **OTIF = a tiempo Y fill ≥ 98 %**.

**Cartera**
- Solo B2B (el D2C se cobra al instante). Se toman los últimos 200 días.
- La probabilidad de estar pagada sube con el vencimiento: 12 % dentro del plazo → 70 % a 15 días de
  vencida → 92 % a 45 → 97 % después.
- Estados: Vigente · Vencida 1-30 · 31-60 · 61-90 · +90.

**Producción y calidad**
- Lotes de lunes a viernes desde julio 2025, 2–5 por día, ponderados por demanda real del SKU.
- Merma: normal centrada en 2,8 %, acotada entre 0,2 % y 14 %.
- Gluten: uniforme 0–12 ppm; con **1,6 % de probabilidad** el lote se dispara a 16–42 ppm →
  cuarentena o rechazo.

**Inventario**
- Stock objetivo = 45 días de venta. Estados: Crítico (<12 días) · Bajo (<25) · Normal (<75) · Sobre-stock.

**Marketing**
- ROAS objetivo por canal: Meta 3,2× · Google 4,3× · TikTok 2,4× · Email (Omnisend) 11× · WhatsApp 9× ·
  Influencers 2,9× · Orgánico/SEO sin inversión.
- La inversión se deriva hacia atrás desde los ingresos atribuidos, con ruido de ±15 %.

**Finanzas**
- EBITDA = ingresos − COGS − marketing − logística − nómina − otros (4,5–6,5 % de ingresos).
- La nómina del P&G **excluye Producción** (ya está en el COGS) y se multiplica por **1,52** por prestaciones.

---

## 8. Las cifras que el demo muestra hoy

Calculadas sobre los CSV actuales del repo (corte 31-ago-2026):

| Indicador | Valor |
|---|---|
| Venta histórica (ene-2025 → ago-2026) | **$35,7 B COP** |
| Venta 2026 YTD (ene–ago) | **$18,6 B COP** |
| Último mes (ago-2026) | **$2.305 M** · margen bruto **52,0 %** · EBITDA **16,8 %** |
| Margen bruto global | 51,3 % |
| Ranking de canales (histórico) | Éxito $9,76 B · Propio $7,44 B · Carulla $5,40 B · Rappi $3,21 B · Naturistas $3,20 B · Paranice US $2,58 B · Fithub $2,23 B · Distribuidor CR $1,89 B |
| Por país | Colombia $30,14 B · EE.UU. $3,36 B · Costa Rica $2,21 B |
| Clientes D2C | 40.865 · recompra **38,2 %** · LTV $182.041 · ticket $120.609 |
| En riesgo de fuga | 10.634 clientes |
| Marketing | ROAS **3,7×** · CAC **$25.673** |
| Cartera | abierta **$3,14 B** · vencida **$0,57 B** |
| Cumplimiento | OTIF **88,0 %** · fill rate **99,1 %** |
| Calidad | 1.058 lotes · aprobación **99,0 %** · gluten promedio **6,1 ppm** · 10 lotes fuera de norma |
| Retail | conversión sell-in→out **86 %** · 2,5 días sin stock promedio · 150 PDV |

> Si alguien regenera los datos con otra semilla o cambia `HOY`, **estas cifras cambian** y este
> capítulo queda desactualizado. Regla: si tocas el generador, vuelve a correr los números y actualiza
> esta tabla.

---

## 9. Historia del proyecto y decisiones técnicas

Diez commits, en orden. Cada uno resolvió algo real; vale la pena conocer el porqué antes de volver a tocarlo.

### 1 · `8e346e2` — Demo inicial (4-sep-2026)
Primer panel BI: 10 módulos, datos sintéticos calibrados sobre paranice.co, con login
(`streamlit-authenticator`, `config.yaml`, `auth_setup.py`).

### 2 · `8102a16` — Rediseño completo: panel omnicanal con la identidad real
**El commit más importante del proyecto.** Se investigó el negocio en fuentes públicas
(paranice.co y su Store API de WooCommerce, paranice.us, LinkedIn, Éxito/Carulla/Rappi) y se rehizo todo:
- Identidad real: logo, personajes, paleta del CSS del tema, Nunito, tema claro.
- **Corrección del modelo de negocio**: no es un e-commerce puro, es **omnicanal**. Entraron los 8
  canales, la arquitectura de precios, sell-in vs sell-out, la cartera a 45–60 días y la trazabilidad
  de gluten en ppm.
- De 10 a **12 módulos**, agrupados en Vista general / Comercial / Operación / Dirección.
- Se botaron los datasets viejos (`pedidos.csv`, `envios.csv`, `clientes.csv`…) y entraron los nuevos.

### 3 · `f38d00e` — Carga de datos compartida: 1.478 MB → 53 MB
Cada módulo definía su propio `load()` con `@st.cache_data`, así que **Streamlit guardaba una copia
del dataset por módulo**: con siete módulos leyendo `ventas.csv` se llegaba a ~1,5 GB, lo que habría
tumbado la app en Streamlit Cloud. Se creó `utils/datos.py` como única fuente de carga cacheada.
**Regla que quedó: ningún módulo lee CSV por su cuenta. Todos importan `from utils import datos`.**

### 4 · `3e61998` — Correctitud de datos: sin filas fantasma y compatible con pandas 3
Dos arreglos que evitan mostrar datos que no ocurrieron:
- Se **quitó la conversión a dtype `category`**. Al agrupar por columnas categóricas, pandas devuelve
  también las combinaciones inexistentes: aparecían 21 filas con venta $0, por ejemplo Paranice US
  facturando cero en meses anteriores a su lanzamiento. La memoria total quedó en **~224 MB**, que es
  aceptable. La función `_categorizar()` sigue existiendo pero **devuelve el DataFrame intacto a propósito**.
- Se reemplazó `groupby().apply(..., include_groups=False)` por agregaciones directas, porque
  `include_groups` cambia de comportamiento entre versiones de pandas y podía romper la app en la nube.

### 5 · `003c247` — Se fijó `streamlit-authenticator <0.5`
Para que un cambio mayor de la librería no rompiera el login. (Quedó obsoleto con el commit siguiente.)

### 6 · `2e0d4fb` — Se quitó el login
**Decisión de producto, no técnica:** para enviárselo en frío al cliente, pedir credenciales es
fricción innecesaria. El control de acceso se implementa en el producto final.
- Fuera el gate de autenticación, `config.yaml` y `auth_setup.py`.
- `utils/auth.py` → **`utils/visitas.py`**: se conservó el registro de visitas (fecha, IP, ciudad
  aproximada), ahora anónimo y sin bloquear la entrada.
- El panel de accesos quedó oculto tras **`?accesos=calybrat`** en la URL.
- `requirements.txt` bajó de 8 a 5 dependencias: sin `streamlit-authenticator` se cae también la
  cadena de `cryptography`, lo que hace el despliegue en Streamlit Cloud más rápido y menos frágil.

### 7 · `155d32c` — Arreglos visuales (Nico)
- `light()`: las leyendas se movieron **debajo** (barras/líneas) o **al lado** (donuts) en vez de
  encima del título, donde se solapaban en casi toda gráfica de varias series. El margen se reserva a
  propósito según cuántas entradas tenga la leyenda.
- `cliponaxis=False` en barras para que las etiquetas de fuera no queden cortadas.
- Texto invisible en los tags del multiselect (había que sobrescribir el color del span anidado).
- Porcentajes de los donuts a 1 decimal fijo, en vez de la precisión variable de Plotly.
- Columnas de porcentaje de las tablas pasadas por `pct()` para que siempre lleven signo y decimales
  consistentes; se agregó `$` al mapa de precios por canal.

### 8 y 9 · `7ccbc55` + `634063f` — `runOnSave`, puesto y revertido
Se activó `runOnSave` para desarrollo local y hubo que **revertirlo el mismo día**:
`registrar_visita()` escribe `visit_log.json` **dentro del directorio vigilado**, así que cada sesión
disparaba una recarga, que registraba otra visita, que disparaba otra recarga — un bucle
autoinfligido que se veía como la pantalla de "your app is in the oven" atascada.
**No volver a activar `runOnSave` sin sacar antes `visit_log.json` del directorio del proyecto.**

### 10 · `f1c9085` — Dev container
`.devcontainer/devcontainer.json` para GitHub Codespaces: imagen Python 3.11, instala
`requirements.txt` y levanta `streamlit run app.py` en el puerto 8501 al conectarse.

---

## 10. Convenciones de código y de escritura

### Código
- **Todo en español**: nombres de funciones, variables, comentarios, docstrings y textos de UI.
  (Excepción: los nombres comerciales de producto, que son los reales de la marca.)
- Cada módulo expone **`render()`** y, casi siempre, un `load()` que delega en `utils.datos`.
- Los módulos hacen `from utils.formatters import *` (import con asterisco, a propósito, para tener la
  paleta y los helpers a mano).
- **Nunca leer un CSV directamente desde un módulo.** Siempre `from utils import datos`.
- Helpers de formato obligatorios: `cop()` para plata ($1,23B / $456M / $12,3K), `num()`, `pct()`.
- Toda gráfica de Plotly pasa por **`light(fig, alto, titulo)`** — ahí vive el tema, la paleta y la
  lógica de leyendas. (`dark` es un alias retro-compatible de `light`.)
- Componentes HTML de marca: **`kpi()`** (tarjeta de indicador, con `ayuda` de una línea que explica
  cómo leerlo), **`panel()`** (bloque de lectura/insight), **`encabezado()`** (título de módulo con logo).
- Los colores no se escriben a mano: se usan las constantes de `formatters` (`PURPLE`, `PINK`, `CREAM`,
  `GOOD`, `WARN`, `BAD`, `PALETTE`…).

### Escritura (esto es tan importante como el código)
El demo se vende por cómo habla. El estándar es:
- Español claro, de negocio, **sin jerga técnica innecesaria**.
- Cada KPI dice **qué significa para el negocio**, no solo el número ("Plata facturada a cadenas que
  ya debería estar cobrada").
- Cada módulo cierra con una lectura que **propone una decisión**, no un resumen ("La palanca más
  barata hoy no es traer gente nueva, es reactivar esos 10.634 que ya compraron dos o más veces").
- Los títulos de gráficas son preguntas o afirmaciones en lenguaje humano ("Dónde se agota el producto",
  "Quién debe la plata"), no nombres de columnas.

### Commits
- Mensajes en español (los de Nico están en inglés; ambos estilos conviven).
- Asunto corto + cuerpo explicando **el porqué**, no el qué.
- Cuando el cambio se verificó, se dice: *"Verificado: los 12 módulos y la navegación completa corren sin errores."*
- Se firma la coautoría de Claude con `Co-Authored-By:`.

---

## 11. Cómo correrlo, desplegarlo y regenerar datos

### Local
```bash
pip install -r requirements.txt
streamlit run app.py
```
Abre en `http://localhost:8501`. No pide usuario ni clave.

### Codespaces / Dev container
Abrir el repo en GitHub Codespaces: el `devcontainer` instala dependencias y levanta la app sola en el puerto 8501.

### Regenerar los datos
```bash
python3 data/generate_data.py
```
Reescribe los 18 CSV en `data/`. Con la semilla actual (11) el resultado es idéntico cada vez.
**Ojo:** si cambias `HOY` en el generador hay que actualizar también las fechas fijadas en el código:

| Archivo | Constante / texto |
|---|---|
| `data/generate_data.py` | `HOY = date(2026, 8, 31)` · `INICIO` · `TRM` |
| `modules/p01_dashboard.py` | `HOY = pd.Timestamp("2026-08-31")` y el subtítulo "corte al 31 de agosto de 2026" |
| `modules/p08_logistica.py` | `HOY` |
| `modules/p09_finanzas.py` | `HOY` |
| `modules/p11_reportes.py` | `HOY_STR = "31 de agosto de 2026"` y el título "Reporte ejecutivo mensual — agosto 2026" |
| `modules/p12_agente.py` | textos "agosto cerró en…" y el encabezado de `resumen_datos()` |
| `modules/p04_portafolio.py` | caption "Catálogo y precios tomados de paranice.co (agosto 2026)" |

### Despliegue (Streamlit Cloud)
- Los CSV van **versionados en el repo** (5,8 MB) justamente para que el deploy no tenga que generarlos.
- `visit_log.json` **se reinicia con cada despliegue** — el sistema de archivos de Streamlit Cloud es efímero.
- `.streamlit/secrets.toml` está en `.gitignore`.
- El tema y la toolbar mínima vienen de `.streamlit/config.toml`; `showErrorDetails = false` para que
  el cliente no vea tracebacks.

### El panel de accesos
`https://<url-del-demo>/?accesos=calybrat` → tabla con fecha/hora, ubicación aproximada e IP de cada visita.

---

## 12. Estado actual, deuda técnica y roadmap

### Estado
El demo está **completo y funcional**: 12 módulos, datos coherentes, identidad de marca aplicada,
sin login, listo para enviar en frío. La rama `claude/claude-teams-context-docs-3peucs` está a la par
de `main`.

### Deuda técnica conocida (ninguna es bloqueante, todas son reales)

| # | Tema | Detalle | Prioridad |
|---|---|---|---|
| 1 | **Modelo del agente desactualizado** | `p12_agente.py` fija `model="claude-sonnet-4-5"`. Conviene pasarlo a un modelo vigente y, mejor aún, sacarlo a una constante o a `st.secrets`. | Alta |
| 2 | **API key en la UI** | El agente pide la API key en un `text_input`. Para el producto final debe ir por `st.secrets`, nunca escrita por el usuario. | Alta |
| 3 | **Fechas fijadas en 7 archivos** | Cambiar el corte hoy implica editar a mano varios sitios (ver tabla de §11). Debería salir todo de una sola constante compartida. | Media |
| 4 | **`leer_csv()` duplicado** | Existe en `utils/formatters.py` y en `utils/datos.py` (`_leer`). El de formatters ya no debería usarse. | Media |
| 5 | **`visit_log.json` dentro del repo** | Es lo que causó el bucle de `runOnSave` y además se pierde en cada deploy. Un almacenamiento externo lo resolvería. | Media |
| 6 | **Geolocalización por HTTP plano** | `utils/visitas.py` llama a `http://ip-api.com` (sin TLS) y a `api.ipify.org`. Funciona, pero es una dependencia externa no cifrada. | Media |
| 7 | **`?accesos=calybrat` es seguridad por oscuridad** | Suficiente para un demo, insuficiente para producción. | Baja (por diseño) |
| 8 | **Tracebacks en pantalla** | `app.py` imprime el traceback si un módulo falla. Bien para desarrollo, mal para una demo frente al cliente. | Baja |
| 9 | **Sin pruebas ni CI** | No hay tests ni workflow de GitHub Actions. La verificación es manual ("navegar los 12 módulos"). | Baja |
| 10 | **`_categorizar()` es un no-op** | Se conserva por compatibilidad y **debe seguir siendo un no-op** (ver §9.4). Si alguien la "arregla", vuelven las filas fantasma. | ⚠️ No tocar |

### Roadmap natural (si el cliente dice que sí)
1. Conectar fuentes reales: **WooCommerce** (ventas D2C), el **ERP**, los reportes de **sell-out** de las cadenas.
2. Autenticación y roles de verdad (dirección / comercial / operación).
3. El agente sobre datos reales y con herramientas, no sobre un resumen precalculado.
4. Alertas automáticas (quiebre de góndola, lote fuera de norma, factura vencida) por correo o WhatsApp.
5. Persistencia real de reportes y su envío programado.

---

## 13. Glosario

| Término | Qué significa aquí |
|---|---|
| **D2C** | *Direct to consumer.* La venta por la tienda propia, sin intermediario. |
| **Sell-in** | Lo que Paranice le factura a la cadena. |
| **Sell-out** | Lo que la cadena le vende al consumidor final. Es el dato que importa y el que llega tarde. |
| **Rotación** | Unidades vendidas por punto de venta por mes. |
| **Quiebre de góndola** | Días en que el producto estuvo agotado en el PDV. Venta perdida y riesgo de perder el espacio. |
| **OTIF** | *On Time In Full.* Órdenes entregadas completas y a tiempo. En el demo: a tiempo **y** fill ≥ 98 %. Meta 95 %. |
| **Fill rate** | Porcentaje de lo pedido por la cadena que efectivamente se despachó. |
| **PVP** | Precio de venta al público (lo que paga el consumidor en ese canal). |
| **Margen del canal** | Lo que se queda el canal sobre el PVP. |
| **COGS** | Costo de la mercancía vendida. Incluye la nómina de planta. |
| **EBITDA** | Utilidad antes de intereses, impuestos, depreciación y amortización. Aquí: ingresos − COGS − marketing − logística − nómina admin/comercial − otros. |
| **Cartera / aging** | Facturas por cobrar y su antigüedad (Vigente, 1-30, 31-60, 61-90, +90 días). |
| **DSO** | *Days Sales Outstanding.* Días promedio que toma cobrar. Objetivo: <60. |
| **LTV** | Valor histórico acumulado de un cliente. |
| **CAC** | Costo de adquirir un cliente nuevo. |
| **LTV/CAC** | Relación entre ambos. Meta: más de 3×. |
| **ROAS** | *Return on ad spend.* Ingresos por cada peso de pauta. Meta: 3×. |
| **CTR** | Clics sobre impresiones. |
| **ppm** | Partes por millón de gluten en un lote. Límite internacional para el claim "libre de gluten": **20 ppm**. |
| **Merma** | Porcentaje de unidades planeadas que se pierden en producción. Meta: <3 %. |
| **CEDI** | Centro de distribución. |
| **TRM** | Tasa representativa del mercado (COP por USD). En el demo: 4.100. |
| **Riesgo de fuga** | Cliente con 2+ pedidos que lleva más de 120 días sin comprar. |

---

*Documento mantenido por Calybrat. Si cambias el código, cambia este archivo en el mismo commit.*

# CONTEXTO_TECNICO · Calybrat

> **Qué es este archivo**
> El lado **técnico y de producto** del contexto de Calybrat: qué software existe hoy, por qué está
> hecho así, qué falta y dónde está cada cosa. Cubre los cuatro repositorios: `paranice-demo`,
> `nutramerican-demo`, `cimpa-demo` y `calybrat-website`.
>
> **Su documento hermano es `CONTEXTO_CALYBRAT.md`** (el que mantiene Nico), que cubre el lado
> **comercial, web y de estrategia**. Los dos siguen la misma estructura a propósito, para que se
> puedan leer juntos hoy y fusionar en un solo documento maestro más adelante sin pelearse.
>
> **Frontera entre los dos, para que no se contradigan:**
> · Lo que pasa **dentro de un repo** (código, datos, decisiones técnicas, deuda) → **este archivo**.
> · Lo que pasa **fuera** (clientes, propuesta comercial, precios, posicionamiento, la web como
>   pieza de marketing) → **CONTEXTO_CALYBRAT.md**.
> · Si algo cae en la mitad (por ejemplo, por qué el demo no tiene login), va en este archivo y el
>   otro lo referencia.

- **Última actualización:** 6 de septiembre de 2026
- **Mantiene:** Juan David · **Documento hermano:** Nico
- **Estructura:** 1) qué existe · 2) decisiones y porqué · 3) pendientes y bugs · 4) archivos y rutas · 5) APIs y conexiones · 6) glosario

---

## Índice

- [1. Qué se construyó / qué existe hoy](#1-qué-se-construyó--qué-existe-hoy)
  - [1.1 Mapa de los cuatro repositorios](#11-mapa-de-los-cuatro-repositorios)
  - [1.2 El patrón común de los demos](#12-el-patrón-común-de-los-demos)
  - [1.3 paranice-demo](#13-paranice-demo)
  - [1.4 nutramerican-demo](#14-nutramerican-demo)
  - [1.5 cimpa-demo](#15-cimpa-demo)
  - [1.6 calybrat-website](#16-calybrat-website)
- [2. Decisiones tomadas y por qué](#2-decisiones-tomadas-y-por-qué)
- [3. Pendientes y bugs conocidos sin resolver](#3-pendientes-y-bugs-conocidos-sin-resolver)
- [4. Archivos y rutas relevantes](#4-archivos-y-rutas-relevantes)
- [5. APIs y conexiones](#5-apis-y-conexiones)
- [6. Glosario](#6-glosario)

---

# 1. Qué se construyó / qué existe hoy

## 1.1 Mapa de los cuatro repositorios

| Repo | Dueño | Qué es | Estado | Escala |
|---|---|---|---|---|
| **`Calybrat/paranice-demo`** | Juan David | Panel BI para **Paranice** (alimentos saludables sin gluten) | Terminado, listo para enviar | 12 módulos · 173.200 líneas de venta · $35,7 B COP |
| **`Calybrat/nutramerican-demo`** | Juan David | Panel BI para **Nutramerican Pharma** (suplementos deportivos + planta) | Terminado, el más grande | 15 módulos · 269.533 líneas de venta · $147,6 B COP |
| **`nicolasgort01/cimpa-demo`** | Nico | Panel BI para **CIMPA** (distribuidor de insumos para industria de alimentos) | El primero; quedó con login | 10 módulos · 13.645 líneas de venta |
| **`nicolasgort01/calybrat-website`** | Nico | El sitio de Calybrat (HTML/CSS/JS, Netlify) | Vivo, iterando | 5 páginas |

**El linaje importa:** CIMPA fue el primero. Paranice se construyó sobre esa estructura y la depuró.
Nutramerican se construyó sobre las dos anteriores y es el más completo. Las lecciones viajan hacia
adelante, **pero no siempre hacia atrás** — de ahí varios de los pendientes de la sección 3.

## 1.2 El patrón común de los demos

Los tres paneles comparten el mismo esqueleto. Quien entienda uno, entiende los tres:

```
app.py                  navegación + sidebar de marca + import dinámico de módulos
utils/formatters.py     paleta de la marca del cliente, cop()/num()/pct(),
                        tema de gráficas, componentes HTML (kpi, panel, encabezado), CSS
utils/datos.py          carga de datos compartida y cacheada (única fuente)
utils/visitas.py        registro de visitas + panel oculto con ?accesos=calybrat
modules/pNN_*.py        un archivo por pantalla, cada uno expone render()
data/generate_data.py   generador de todos los datos, con semilla fija
data/*.csv(.gz)         datasets generados, versionados en el repo
assets/                 identidad visual real del cliente
```

**Decisiones de producto que comparten los tres** (el porqué está en la sección 2):
- Streamlit + pandas + Plotly, en **español**, tema claro con la paleta real del cliente.
- **Datos transaccionales simulados**, pero catálogo, precios, canales, sedes e identidad **reales**,
  tomados de fuentes públicas del cliente.
- Corte de datos: **31 de agosto de 2026** en los tres. Horizonte: enero 2025 → esa fecha.
- **Acceso libre, sin login** (excepto CIMPA, que se quedó con el login del principio).
- Un módulo de **reportes descargables en HTML** que se imprimen a PDF con Ctrl+P.
- Un módulo de **Agente IA** con dos modos: demo (respuestas armadas con los datos, sin API) y
  Claude real (con API key).

## 1.3 paranice-demo

### El negocio
**Paranice**: marca colombiana de alimentos saludables fundada en 2019 en Bogotá (antes "Why Not").
Promesa: que lo indulgente sea nutritivo — libre de gluten, sin azúcar añadida, vegano, keto.

**La tesis del demo:** Paranice no es un e-commerce puro ni una marca de retail — **es las dos cosas,
en tres países**. Esa información hoy vive repartida entre WooCommerce, los reportes de las cadenas,
los Excel de producción y los informes del contador.

**Portafolio real: 28 referencias en 6 categorías** (de la Store API de WooCommerce de `paranice.co`, ago-2026):

| Categoría | Referencias | Rango de PVP |
|---|---|---|
| GranOLAS (300 g) | Vanilla Shortbread, Chip Cookie, Fudge Cake, Pistachio Cookie | $37.950 – $44.950 |
| Esparcibles (200 g / 45 g) | Buttery Pistachio, Golden Butter, Peanutty Banana, Creamy y Crunchy Cocoa Hazelnut, Golden Cinnamon Roll, Baby Spreads | $19.500 – $63.500 |
| Pancakes & Waffles (285/300 g) | Almendra (Vainilla, Choco Chips, Churro) · Avena (Banano, Brownie, Vainilla) | $32.890 – $41.690 |
| Avena & Harinas | Avena en hojuelas, Harina de avena, Harina de almendra | $31.350 – $34.650 |
| Combos | 3 Pack GranOLA, 3 Pack Spread, 3 Pack Mezclas, Mix & Match, Mini Wafflera, Deck, Rompecabezas | $69.258 – $128.774 |
| Merch | New Year Resolution | $100.000 |

**Los 8 canales** — el corazón del demo:

| Canal | Tipo | País | Factor PVP | Margen canal | Plazo pago | Mix | Lanzamiento |
|---|---|---|---|---|---|---|---|
| E-commerce propio | D2C | Colombia | 1,00× | 0 % | 0 d | 17,5 % | ene-2025 |
| Éxito | Retail | Colombia | 1,11× | 32 % | 60 d | 23,0 % | ene-2025 |
| Carulla | Retail | Colombia | 1,13× | 32 % | 60 d | 15,0 % | abr-2025 |
| Rappi | Marketplace | Colombia | 1,15× | 25 % | 30 d | 7,5 % | ene-2025 |
| Fithub | Especializado | Colombia | 1,23× | 30 % | 45 d | 7,0 % | jun-2025 |
| Tiendas naturistas | Especializado | Colombia | 1,18× | 28 % | 45 d | 7,5 % | ene-2025 |
| Paranice US | Internacional | EE.UU. | 1,30× | 0 % | 15 d | 11,5 % | oct-2025 |
| Distribuidor CR | Internacional | Costa Rica | 1,22× | 30 % | 45 d | 5,5 % | may-2025 |

**Brecha de precios real observada** (dato público): GranOLA Pistacho 300 g → **$44.950** en
paranice.co · **$49.900** en Éxito · **$55.400** en Fithub.

**Otros datos reales:** pedido mínimo del sitio $50.000 · Mercado Pago · Omnisend · WooCommerce ·
150 PDV (Éxito 46, Carulla 28, Fithub 14, naturistas 62) · 4 CEDIS (Bogotá planta, cross-dock
Medellín, 3PL Miami, distribuidor San José) · 8 proveedores · 112 empleados en 8 áreas.

**El diferencial:** el claim "libre de gluten" depende de evitar contaminación cruzada. Cada lote se
ensaya en **ppm** y el límite internacional es **20 ppm**. En el demo: >20 → **Rechazado**;
15–20 → **Cuarentena**; resto → **Aprobado**.

**Identidad:** morado `#2a1d65`, crema `#f4e1c1`, lavanda `#a299ba`, rosa `#e6a4c4`. Tipografía de
marca Filson Soft → se usa **Nunito** como equivalente libre. Logo, favicon y 7 personajes ilustrados.

### Los 12 módulos

| # | Módulo | Grupo | KPIs principales |
|---|---|---|---|
| p01 | Dashboard General | Vista general | Ventas y delta · margen bruto (meta 58 %) · EBITDA · ticket web · cobertura PDV · OTIF (meta 95 %) · cartera vencida · recompra |
| p02 | Ventas Omnicanal | Comercial | Ventas · unidades · documentos · margen · precio medio · peso del canal propio |
| p03 | Retail & Sell-Out | Comercial | PDV activos · sell-out · conversión sell-in→out (ideal 90–100 %) · rotación und/PDV/mes · días sin stock · OTIF y fill rate |
| p04 | Portafolio & Precios | Comercial | Referencias activas · % sin gluten · % vegano · más vendido · brecha de precio máxima |
| p05 | Clientes & Recompra | Comercial | Clientes · recompra (ref. 30 %) · LTV · CAC · LTV/CAC (meta >3×) · en riesgo de fuga |
| p06 | Marketing & Contenido | Comercial | Inversión · ingresos atribuidos · ROAS (meta 3×) · CAC · peso de canales propios · CTR |
| p07 | Producción & Calidad | Operación | Lotes · aprobación (meta 98 %) · gluten ppm · fuera de norma · merma (<3 %) · costo de lo rechazado |
| p08 | Logística & Cumplimiento | Operación | OTIF · fill rate · entregas a tiempo web · días de entrega · costo logístico · en tránsito |
| p09 | Finanzas & Cartera | Dirección | Ingresos · margen · EBITDA · peso nómina · cartera abierta · DSO (<60) |
| p10 | Expansión Internacional | Dirección | Los 3 mercados por salud, no por tamaño |
| p11 | Reportes Automáticos | Dirección | 5 documentos HTML → PDF |
| p12 | Agente IA | Dirección | Chat en español, modo demo o Claude real |

**Los 5 reportes de p11:** ejecutivo mensual (junta) · retail y sell-out (para negociar con Éxito o
Carulla) · clientes y recompra (marketing/CRM) · calidad y gluten (respalda el claim ante autoridades) ·
cartera y cobranza (finanzas).

### Los datos (18 tablas)

Semilla `default_rng(11)` → reproducible. `HOY = 2026-08-31`, `INICIO = 2025-01-01`, TRM 4.100.

| Archivo | Filas | Qué es |
|---|---:|---|
| `ventas.csv.gz` | 173.200 | Línea de venta (el dataset madre) |
| `despachos.csv.gz` | 70.241 | Un despacho por documento: SLA, transportadora, fill rate, OTIF |
| `clientes_d2c.csv.gz` | 40.865 | Cliente del canal propio: LTV, ticket, NPS, segmento, riesgo de fuga |
| `sellout.csv` | 10.079 | Mes × cadena × ciudad × SKU: sell-in, sell-out, rotación, días sin stock |
| `cartera.csv` | 3.205 | Factura B2B: plazo, mora, estado |
| `produccion.csv` | 1.058 | Lote: merma, turno, línea, gluten ppm, estado de calidad |
| `precios_canal.csv` | 224 | 28 SKU × 8 canales |
| `puntos_venta.csv` | 150 | PDV por cadena, formato, ciudad, zona |
| `marketing.csv` / `contenido.csv` | 140 / 140 | Mes × canal · mes × sección del blog |
| `inventario.csv` | 112 | CEDI × SKU: cobertura y estado |
| `empleados.csv` | 112 | Área, sede, contrato, salario, riesgo de rotación |
| `productos.csv` · `canales.csv` · `proveedores.csv` · `cedis.csv` · `finanzas_mensual.csv` | 28 · 8 · 8 · 4 · 20 | Maestros y P&G mensual |

**Cadena de generación:** maestros → precios → PDV → **ventas** → (clientes, sell-out, despachos,
cartera, producción, inventario, marketing, contenido) → empleados → finanzas.

### Reglas de negocio codificadas en el generador
Esto es lo que hace que los datos se sientan reales. **Léelo antes de tocar `generate_data.py`.**

- **Ventas:** base $1.950 M el primer mes, +1,6 % compuesto mensual. Estacionalidad: enero 1,28×
  (propósitos), nov 1,32× y dic 1,20× (regalo), julio 0,86×. Rampa de canal nuevo: arranca en 45 % y
  llega a 100 % en 240 días. Un SKU no se vende antes de su lanzamiento.
- **D2C:** 1–3 ítems por pedido, descuentos 0/5/10/15 %, y si el pedido queda bajo $50.000 se agrega
  un ítem (la regla real del sitio).
- **B2B:** órdenes Poisson (media 2,2 por canal/día), 3–8 SKU repartidos con Dirichlet.
- **Clientes:** la probabilidad de que un pedido sea de cliente nuevo baja de 78 % a 56 % con el
  tiempo; los compradores recientes tienen 70 % de probabilidad de ser los que vuelven.
- **Cumplimiento:** SLA D2C 3/7/6 días (CO/US/CR); B2B 4/3/5/12. Puntualidad 93/95/94/88 %.
  Fill rate: 94 % completas, el resto normal en 86 %. **OTIF = a tiempo Y fill ≥ 98 %**.
- **Cartera:** solo B2B, últimos 200 días. Probabilidad de estar pagada: 12 % dentro del plazo →
  70 % a 15 días vencida → 92 % a 45 → 97 % después.
- **Producción:** lun-vie desde jul-2025, 2–5 lotes/día ponderados por demanda. Merma normal 2,8 %
  (0,2–14 %). Gluten uniforme 0–12 ppm, con 1,6 % de probabilidad se dispara a 16–42 ppm.
- **Inventario:** objetivo 45 días. Crítico <12 · Bajo <25 · Normal <75 · Sobre-stock.
- **Marketing:** ROAS objetivo Meta 3,2× · Google 4,3× · TikTok 2,4× · Omnisend 11× · WhatsApp 9× ·
  Influencers 2,9×. La inversión se deriva hacia atrás desde los ingresos, ±15 %.
- **Finanzas:** EBITDA = ingresos − COGS − marketing − logística − nómina − otros (4,5–6,5 %).
  La nómina del P&G **excluye Producción** (ya está en el COGS) y se multiplica por 1,52 por prestaciones.

### Cifras que produce hoy

| Indicador | Valor |
|---|---|
| Venta histórica (ene-2025 → ago-2026) | **$35,7 B COP** |
| Venta 2026 YTD (ene–ago) | **$18,6 B COP** |
| Último mes (ago-2026) | $2.305 M · margen bruto 52,0 % · EBITDA 16,8 % |
| Margen bruto global | 51,3 % |
| Canales (histórico) | Éxito $9,76 B · Propio $7,44 B · Carulla $5,40 B · Rappi $3,21 B · Naturistas $3,20 B · US $2,58 B · Fithub $2,23 B · CR $1,89 B |
| Países | Colombia $30,14 B · EE.UU. $3,36 B · Costa Rica $2,21 B |
| Clientes D2C | 40.865 · recompra 38,2 % · LTV $182.041 · ticket $120.609 · 10.634 en riesgo de fuga |
| Marketing | ROAS 3,7× · CAC $25.673 |
| Cartera | abierta $3,14 B · vencida $0,57 B |
| Cumplimiento | OTIF 88,0 % · fill rate 99,1 % |
| Calidad | 1.058 lotes · aprobación 99,0 % · 6,1 ppm promedio · 10 fuera de norma |
| Retail | conversión 86 % · 2,5 días sin stock · 150 PDV |

## 1.4 nutramerican-demo

### El negocio
**Nutramerican Pharma**: no es una marca de suplementos, es **una fábrica certificada que además
tiene marcas propias, ocho tiendas, e-commerce, distribución nacional, maquila para terceros y
exportación a seis países**. Cada una de esas cosas se mide distinto — ahí es donde un dashboard
estándar se queda corto.

**Portafolio real: 52 referencias en 7 categorías y 6 marcas propias** (de `nutramerican.com/productos`,
sep-2026), **con el render oficial de cada producto** descargado del CDN de la compañía.
Marcas: **BiPro** y **Megaplex**, más las líneas Stacks, Nutra, Radical y merch.
Categorías: Módulos proteicos · Control de peso · Hipercalóricos · Energía y recuperación ·
Snacks proteicos · Nutrición general · Merch.

**Los 12 canales:**

| Canal | Tipo | País | Factor PVP | Margen canal | Plazo | Mix |
|---|---|---|---|---|---|---|
| Tiendas Nutramerican | Tienda propia | Colombia | 1,00× | 0 % | 0 d | 22,5 % |
| Distribuidores | Mayorista | Colombia | 1,18× | 30 % | 45 d | 23,5 % |
| nutramerican.com | E-commerce | Colombia | 1,00× | 0 % | 0 d | 14,0 % |
| Cadenas & Farmacias | Retail | Colombia | 1,24× | 34 % | **75 d** | 14,0 % |
| Maquila & Marca Propia | Maquila | Colombia | **0,62×** | 0 % | 60 d | 9,5 % |
| Gimnasios & Wellness | Especializado | Colombia | 1,20× | 28 % | 45 d | 6,0 % |
| Distribuidor Ecuador / México / Honduras / Panamá | Internacional | — | 1,14–1,22× | 26–28 % | 60 d | 8,9 % |
| Nutramerican España / USA LLC | Internacional | — | 1,45× / 1,52× | 20 % / 15 % | 45 / 30 d | 1,6 % |

**Operación real:** planta de fabricación en **Cantarrana, Palmira (Valle)**, 2.500 m², 1.000 t de
almacenamiento, 6 líneas y 3 turnos · comercializadora **ELITENUT S.A.S.** en Yumbo, bodega C-11 ·
**8 tiendas propias** con dirección, teléfono, horario y coordenadas reales (Bogotá Norte, Bogotá
Kennedy, Cali, Medellín, Barranquilla, Bucaramanga, Pereira, Cúcuta) · 5 bodegas incluyendo
**3PL MELONN** en Bogotá y Medellín · línea gratuita **#590** para servicio al cliente.

**Regulatorio (lo que diferencia este demo):** certificación **FSSC 22000** obtenida el 28 de marzo
de 2024 · habilitación **FDA** · **un registro INVIMA por producto**, con dos números reales
publicados (BiPro Classic `RSA-0007428-2019`, Crea Stack `NSA-0015613-2024`) y el resto simulados y
marcados como tal. Un registro vencido saca el producto del mercado y nadie se entera hasta que
alguien lo pide.

**Divisa:** la proteína de suero se importa en dólares y se vende en pesos, con más de 60 días de
tránsito. La TRM mueve el EBITDA sin que nadie tome una decisión comercial → por eso hay un módulo
de abastecimiento con **simulador de sensibilidad del EBITDA a la TRM**.

**Identidad:** paleta tomada de las variables CSS del propio sitio — `--nutra-blue #0071e3`,
`--nutra-gold #e5bb47`, `--nutra-ink #0b0c0f`, rojo de la franja `#D8232A`, azul de las estrellas
`#004BE0`. Tipografía **Montserrat**, la misma de la web.

### Los 15 módulos

| # | Módulo | Grupo | KPIs principales |
|---|---|---|---|
| p01 | Dashboard Ejecutivo | Vista general | Facturación · unidades · margen · EBITDA · liberación de lotes · OTIF · cartera vencida · recompra |
| p02 | Ventas Omnicanal | Comercial | Facturación · unidades · margen · precio neto medio · descuento medio |
| p03 | Tiendas Nutramerican | Comercial | Venta · visitantes · conversión · ticket · contribución · **venta por m²** |
| p04 | Portafolio & Precios | Comercial | Referencias · marcas · concentración · margen · cola larga |
| p05 | Clientes & Recompra | Comercial | Clientes · recompra · **ciclo de recompra** · LTV/CAC · reactivables |
| p06 | Marketing & Megaplex Stars | Comercial | ROAS · CAC · **retorno por embajador atleta** · ferias y eventos |
| p07 | Producción & Planta | Operación | Lotes · cumplimiento del plan · **OEE** · merma · volumen |
| p08 | Calidad & Regulatorio | Operación | Liberación · proteína declarada · lotes retenidos · NC FSSC · **registros INVIMA en riesgo** · farmacovigilancia |
| p09 | Abastecimiento & Divisa | Operación | Compras · **exposición en dólares** · diferencia en cambio · impacto sobre el EBITDA |
| p10 | Logística & Inventario | Operación | OTIF · tiempo de entrega · costo logístico · devoluciones · lotes añejos |
| p11 | Finanzas & Cartera | Dirección | Ingresos · margen · EBITDA · DSO · DIO · DPO · **ciclo de conversión de caja** |
| p12 | Expansión Internacional | Dirección | 6 mercados por salud |
| p13 | Servicio al Cliente & PQR | Dirección | PQR · primera respuesta · cierre · CSAT · **qué se puede automatizar** |
| p14 | Reportes Automáticos | Dirección | 6 documentos HTML → PDF |
| p15 | Agente IA | Dirección | Chat en español |

### Los datos (25 tablas)
Semilla `default_rng(2026)`. Mismo corte: `HOY = 2026-08-31`.

Las grandes: `ventas.csv.gz` **269.533** · `clientes.csv.gz` **111.689** · `despachos.csv.gz` **52.000** ·
`pqr.csv` **7.981** · `produccion.csv.gz` y `ensayos_calidad.csv` **1.550** cada una ·
`precios_canal.csv` 572 · `cartera.csv` 490 · `inventario.csv` 260 · `compras.csv` 210 ·
`tiendas_mensual.csv` 160 · `marketing.csv` 180 · `no_conformidades.csv` 74 ·
`registros_invima.csv` 51 · `farmacovigilancia.csv` 96 · `embajadores.csv` 34 · `trm.csv` 20.

Tablas que **no existen en Paranice** y que son la razón de ser de este demo:
`tiendas_mensual` (tráfico, conversión, venta/m², contribución por tienda), `registros_invima`
(vigencia y días para vencer), `no_conformidades` (FSSC 22000), `ensayos_calidad` (proteína declarada),
`farmacovigilancia`, `compras` + `trm` (exposición en divisa), `pqr`, `embajadores`, `eventos`.

**P&G más completo que el de Paranice:** además de EBITDA trae depreciación, gasto financiero,
**diferencia en cambio**, utilidad antes de impuestos y utilidad neta.

### Cifras que produce hoy

| Indicador | Valor |
|---|---|
| Venta histórica | **$147,6 B COP** · 1,5 M de unidades |
| Venta 2026 YTD | **$67,0 B COP** |
| Último mes (ago-2026) | $7.783 M · margen bruto 52,4 % · **EBITDA 12,5 %** · utilidad neta $434 M |
| Canales top | Tiendas $38,4 B · Distribuidores $34,5 B · nutramerican.com $23,5 B · Cadenas $20,5 B · Maquila $10,5 B · Gimnasios $9,3 B |
| Internacional | Ecuador $4,39 B · Honduras $3,28 B · México $2,31 B · Panamá $0,55 B · España $0,28 B · EE.UU. $0,11 B |
| Clientes | 111.689 identificados |

## 1.5 cimpa-demo

**CIMPA**: distribuidor de **insumos e ingredientes para la industria de alimentos** (lácteos,
cárnicos) — cuajos, cultivos, estabilizantes, fosfatos, condimentos, de marcas como Chr. Hansen,
Danisco, BASF, Kerry, Givaudan, IFF, Brenntag.

Fue **el primer demo** y de él salió la estructura de los otros dos. Diferencias con los posteriores:

- **Tiene login** (`streamlit-authenticator` + `config.yaml` + `auth_setup.py` + `utils/auth.py`) —
  justo lo que Paranice terminó quitando.
- **Tema oscuro** con degradado morado/teal, no la identidad del cliente.
- **No tiene `utils/datos.py`**: cada módulo carga sus propios CSV (el problema de memoria que
  Paranice diagnosticó y arregló después).
- **No tiene `.streamlit/config.toml`**.
- 7 sedes (5 puntos de venta + 2 CEDIS: Mosquera y Siberia), 50 productos, semilla `default_rng(42)`.
- 10 módulos: dashboard, inventario multi-bodega, ventas y clientes, cartera y cobranza, logística,
  proveedores y compras, talento humano, consolidado del grupo, reportes y agente IA.
- Historial de commits informal ("cambioo", "reverse") frente al estilo cuidado de los otros dos.

## 1.6 calybrat-website

El sitio de Calybrat. **Stack:** HTML + CSS + JS plano (`index.html`, `styles.css`, `app.js`),
desplegado en **Netlify** (`netlify.toml`). Sin framework ni build.

**5 páginas:** `/` (home) · `/demo/` · `/precios/` · `/contacto/` · `/nosotros/`.

Su evolución (11 commits) es una historia de **simplificación progresiva**: se pasó de una sola
página con secciones separadas (demo, problema, cómo funciona, módulos, casos, industrias) a una
sección con pestañas, después a tres páginas, y finalmente a **4 ítems de navegación** con el
sub-nav pegajoso eliminado. En el camino se quitaron CIMPA, Poblado y Paranice del marquee de
confianza y se simplificó el panel del agente a una pregunta/respuesta estática por industria.

> **Este repo es territorio de `CONTEXTO_CALYBRAT.md`.** Aquí solo queda anotado que existe, con qué
> está hecho y dónde vive, para que este documento no contradiga al otro.

---

# 2. Decisiones tomadas y por qué

Esta sección es la que no se puede reconstruir mirando el código. **Cada decisión tiene un porqué que
costó tiempo aprender**; si alguien la revierte sin conocerlo, vuelve a pisar la misma mina.

## 2.1 Decisiones de producto (aplican a los tres demos)

### Datos simulados, pero identidad y catálogo reales
**Qué se decidió:** todo lo transaccional es sintético, generado con semilla fija. Pero el catálogo,
los precios, los canales, las sedes, las certificaciones y la identidad visual se toman de **fuentes
públicas del cliente**.
**Por qué:** un dashboard con datos genéricos se ve como una plantilla. Cuando el cliente abre el
panel y ve **sus** 28 (o 52) referencias con **sus** precios, **su** logo y **su** paleta, la
conversación cambia: deja de discutir si el software sirve y empieza a discutir su negocio.
El costo es investigación previa (Store API de WooCommerce, el sitio, LinkedIn, prensa), y vale la pena.

### Semilla fija en el generador
**Qué:** `default_rng(11)` en Paranice, `2026` en Nutramerican, `42` en CIMPA.
**Por qué:** el demo tiene que dar **las mismas cifras** cada vez que se abre. Si los números
cambiaran entre demostraciones, cualquier cifra citada en una reunión anterior quedaría desmentida.

### Los CSV se versionan en el repo
**Qué:** los datasets generados van commiteados (5,8 MB en Paranice), no se generan en el deploy.
**Por qué:** Streamlit Cloud tendría que correr el generador en cada arranque — lento y frágil.
Con los CSV en el repo el deploy es un `pip install` y listo.

### Un solo corte temporal: 31 de agosto de 2026
**Qué:** los tres demos tienen la misma fecha de "hoy", con datos desde enero de 2025.
**Por qué:** 20 meses dan suficiente histórico para ver estacionalidad y tendencia, y una fecha fija
hace que los textos ("agosto cerró en…") sean escribibles.
**El costo:** esa fecha quedó regada en varios archivos por demo (ver pendiente 3.4).

### Sin login (Paranice y Nutramerican)
**Qué:** el demo se abre sin usuario ni clave. CIMPA se quedó con el login del principio.
**Por qué:** para enviárselo **en frío** al cliente, pedir credenciales es fricción innecesaria: el
cliente no las va a pedir, no las va a guardar y probablemente no va a entrar. El control de acceso
se implementa en el producto final, no en la pieza de venta.
**Consecuencia:** se conservó el **registro de visitas** (fecha, IP, ciudad aproximada) para saber
cuándo y desde dónde lo abrieron, y el panel de ese registro quedó tras `?accesos=calybrat`.
**Beneficio colateral:** `requirements.txt` bajó de 8 a 5 dependencias — al caer
`streamlit-authenticator` se cayó también la cadena de `cryptography`, y el deploy quedó más rápido
y menos frágil.

### El agente con dos modos
**Qué:** modo demo (respuestas armadas con los datos reales por *matching* de palabras clave) y modo
Claude (con API key).
**Por qué:** el demo tiene que funcionar **sin depender de una API key ni de red**. Si el cliente lo
abre y el agente falla porque no hay llave, se cae la parte más vistosa de la demostración. El modo
demo garantiza que siempre responda algo correcto y con cifras reales.

### Reportes en HTML, no en PDF
**Qué:** los reportes se descargan como HTML autocontenido y se imprimen a PDF con Ctrl+P.
**Por qué:** generar PDF en Python obliga a meter una dependencia pesada (wkhtmltopdf, WeasyPrint,
reportlab) que además hay que hacer funcionar en Streamlit Cloud. Un HTML con `@media print` da el
mismo resultado, pesa nada y se puede abrir en cualquier parte.

### El tono de la interfaz es parte del producto
**Qué:** cada KPI explica qué significa para el negocio; cada módulo cierra proponiendo una decisión;
los títulos de gráficas son lenguaje humano ("Quién debe la plata"), no nombres de columnas.
**Por qué:** el demo se vende por cómo habla. Un panel que solo muestra números obliga al cliente a
traducirlos; uno que ya los tradujo demuestra que entendemos el negocio.

## 2.2 Decisiones técnicas (con la historia de cómo se llegó a ellas)

### Carga de datos centralizada — `utils/datos.py`
**El problema:** cada módulo definía su propio `load()` con `@st.cache_data`. Streamlit cachea **por
función**, así que guardaba **una copia del dataset por módulo**: con siete módulos leyendo
`ventas.csv` se llegaba a **~1,5 GB**. Eso habría tumbado la app en Streamlit Cloud.
**La solución:** `utils/datos.py` como única fuente de carga cacheada. Una copia por tabla.
**Regla que quedó:** *ningún módulo lee un CSV por su cuenta*.
**Estado:** hecho en Paranice y Nutramerican. **CIMPA sigue sin esto** (pendiente 3.6).

### No convertir texto a `dtype category`
**El problema:** para bajar memoria se convirtieron las columnas de texto a `category`. Al agrupar
por columnas categóricas, **pandas devuelve también las combinaciones que no existen**: aparecían 21
filas con venta $0 — por ejemplo Paranice US facturando cero en meses **anteriores a su lanzamiento**.
Un dato que nunca ocurrió, mostrado como si hubiera ocurrido.
**La decisión:** se revirtió. Se prefiere gastar memoria (~224 MB en total) antes que mostrar un dato falso.
**Importante:** la función `_categorizar()` **sigue existiendo pero devuelve el DataFrame intacto a
propósito**. Si alguien la "arregla", vuelven las filas fantasma.

### Fuera `groupby().apply(..., include_groups=False)`
**El problema:** `include_groups` es justamente uno de los parámetros de transición entre pandas 2 y
3; su comportamiento cambia entre versiones y podía romper la app en la nube.
**La solución:** se reemplazó por agregaciones vectorizadas directas. En Nutramerican se verificó
numéricamente que el resultado es idéntico.

### Fijar las dependencias por rango probado (solo Nutramerican)
**El problema:** `pandas>=2.0.0` en Streamlit Community Cloud habría instalado **pandas 3.0**, que no
es lo que se probó: el salto de major cambia el manejo de copias y el dtype de texto por defecto.
**La solución:** `pandas>=2.2,<3`, con numpy y plotly también acotados, y un comentario en el archivo
diciendo con qué versiones se verificó (streamlit 1.50, pandas 2.3.3, numpy 2.0.2, plotly 7.0.0).
**Estado:** hecho solo en Nutramerican. **Paranice y CIMPA siguen abiertos** (pendiente 3.1).

### Las leyendas de Plotly van abajo o al lado, nunca arriba
**El problema:** con la leyenda arriba, a esa altura compite por el mismo espacio que el título y lo
solapaba en cuanto había más de un par de series o un donut con varias porciones. Pasaba en casi
toda gráfica de varias series.
**La solución:** en `light()`, la leyenda va **debajo** (barras/líneas, con el margen inferior
calculado según cuántas filas de leyenda haya) o **al lado derecho** (donuts), con margen reservado
a propósito. Además `cliponaxis=False` en barras, para que las etiquetas de fuera no queden cortadas.

### `runOnSave` desactivado (Paranice)
**El problema:** se activó para desarrollo local y hubo que revertirlo **el mismo día**.
`registrar_visita()` escribe `visit_log.json` **dentro del directorio vigilado**, así que cada sesión
disparaba una recarga → que registraba otra visita → que disparaba otra recarga. Un bucle
autoinfligido, visible como la pantalla de *"your app is in the oven"* atascada.
**La regla:** no activar `runOnSave` mientras `visit_log.json` viva en el directorio del proyecto.
**⚠️ Nutramerican tiene `runOnSave = true` y el mismo `visitas.py` → ver bug 3.2.**

### Credenciales centralizadas — `utils/config.py` (nuevo, sep-2026)
**El problema:** la API key del agente se pedía en un `text_input` de la interfaz y el modelo estaba
escrito a mano en el código (`claude-sonnet-4-5`, ya desactualizado).
**La solución:** `utils/config.py` lee en orden **`st.secrets` → variable de entorno → valor por
defecto**. El agente ahora toma la llave de ahí y **solo pide que la peguen si no hay ninguna
configurada**; cuando sí la hay, muestra un chip "Claude conectado" y arranca fuera de modo demo.
El modelo por defecto pasó a `claude-sonnet-5` y es configurable con `ANTHROPIC_MODEL`.
**Estado:** hecho en Paranice. **Falta portarlo a Nutramerican y CIMPA** (pendiente 3.3).

## 2.3 Decisiones de proceso

- **Commits en español**, asunto corto + cuerpo que explica **el porqué**, no el qué. Cuando el
  cambio se verificó, se dice explícitamente ("Verificado: los 12 módulos y la navegación completa
  corren sin errores"). Se firma la coautoría de Claude con `Co-Authored-By:`.
- **La verificación es manual**: correr la app y navegar todos los módulos con sus pestañas y filtros.
  No hay tests ni CI (pendiente 3.8).
- **Un repo por cliente**, sin monorepo ni librería compartida. Se copia la estructura y se adapta.
  Es deliberado para que cada demo pueda divergir sin romper a los demás — el costo es que los
  arreglos no se propagan solos (que es el origen de media sección 3).

---

# 3. Pendientes y bugs conocidos sin resolver

Ordenados por prioridad. **Ninguno bloquea el demo hoy**, pero el 3.2 es un bug real y reproducible.

## 3.1 · Alta · `paranice-demo` y `cimpa-demo` no tienen las dependencias acotadas
`requirements.txt` de Paranice dice `pandas>=2.0.0`, que en Streamlit Community Cloud instala
**pandas 3.0** — justo lo que Nutramerican decidió evitar por el cambio de major (manejo de copias y
dtype de texto por defecto). Paranice *parece* correr con pandas 3, pero no está verificado a fondo.
**Arreglo:** copiar el bloque de rangos de `nutramerican-demo/requirements.txt`, con su comentario.

## 3.2 · Alta · 🐛 BUG · `nutramerican-demo` tiene el bucle de recarga que Paranice ya arregló
`.streamlit/config.toml` línea 13 dice **`runOnSave = true`**, y su `utils/visitas.py` es
**byte a byte idéntico** al de Paranice: escribe `visit_log.json` dentro del directorio del proyecto
en cada sesión. Esa es exactamente la combinación que en Paranice produjo el bucle infinito de
recargas (commit `7ccbc55` puesto y `634063f` revertido el mismo día).
**Reproducción:** correr `streamlit run app.py` en local y abrir el panel → se queda en
*"your app is in the oven"*.
**Arreglo (una línea):** borrar `runOnSave = true` de `nutramerican-demo/.streamlit/config.toml`.
**Nota:** no se tocó desde esta sesión porque el trabajo estaba acotado a `paranice-demo`.

## 3.3 · Alta · `utils/config.py` solo existe en Paranice
Nutramerican y CIMPA siguen pidiendo la API key en la interfaz y con el modelo escrito a mano
(`claude-sonnet-4-5`, desactualizado).
**Arreglo:** copiar `utils/config.py`, `.env.example` y `.streamlit/secrets.example.toml`, y aplicar
el mismo cambio en `p15_agente.py` / `p09_agente.py` (son ~15 líneas).

## 3.4 · Media · La fecha de corte está fijada en varios archivos por repo
Cambiar el corte obliga a editar a mano cada sitio. En Paranice son **7**:

| Archivo | Qué tiene |
|---|---|
| `data/generate_data.py` | `HOY = date(2026, 8, 31)`, `INICIO`, `TRM` |
| `modules/p01_dashboard.py` | `HOY` + subtítulo "corte al 31 de agosto de 2026" |
| `modules/p08_logistica.py` | `HOY` |
| `modules/p09_finanzas.py` | `HOY` |
| `modules/p11_reportes.py` | `HOY_STR` + título "…— agosto 2026" |
| `modules/p12_agente.py` | textos "agosto cerró en…" y encabezado de `resumen_datos()` |
| `modules/p04_portafolio.py` | caption "…(agosto 2026)" |

**Arreglo:** una constante compartida (`utils/config.py` ya es el sitio natural) de la que salgan la
fecha y su versión en texto.

## 3.5 · Media · `leer_csv()` duplicado en Paranice
Existe en `utils/formatters.py` y en `utils/datos.py` (`_leer`). El de `formatters` quedó huérfano
tras centralizar la carga y ya no debería usarse. **Arreglo:** borrarlo y verificar que nadie lo importa.

## 3.6 · Media · `cimpa-demo` no tiene carga de datos centralizada
Arrastra el problema de memoria que Paranice diagnosticó (una copia del dataset por módulo). Sus
datasets son mucho más chicos (13.645 filas de venta contra 173.200), así que no revienta — pero es
la misma deuda sin pagar. **Arreglo:** portar `utils/datos.py`.

## 3.7 · Media · `visit_log.json` vive dentro del repo
Causa el bug 3.2, se pierde en cada despliegue de Streamlit Cloud (sistema de archivos efímero) y
mete escrituras en el directorio del proyecto. **Arreglo:** mandarlo a almacenamiento externo o, como
mínimo, fuera del directorio vigilado.

## 3.8 · Media · Sin pruebas ni CI en ningún repo
La verificación es manual. Como mínimo valdría una prueba de humo que importe todos los módulos y
verifique que exponen `render()` — es lo que se corrió a mano en esta sesión y toma segundos.

## 3.9 · Baja · Geolocalización por HTTP plano
`utils/visitas.py` llama a `http://ip-api.com` **sin TLS** y a `https://api.ipify.org`. Funciona,
pero es una dependencia externa no cifrada y sin control de errores más allá del `try/except`.

## 3.10 · Baja · `?accesos=calybrat` es seguridad por oscuridad
Suficiente para un demo, insuficiente para producción. Está asumido, no es un descuido.

## 3.11 · Baja · Tracebacks visibles en pantalla
`app.py` imprime el traceback completo si un módulo falla. Útil en desarrollo, feo frente al cliente.
`showErrorDetails = false` en `config.toml` no lo tapa, porque el `try/except` de `app.py` lo escribe
con `st.code()`.

## 3.12 · ⚠️ No tocar · `_categorizar()` es un no-op a propósito
No es deuda: es la solución. Si alguien la "arregla" para que vuelva a convertir a `category`,
regresan las filas fantasma con venta $0 (ver 2.2).

---

# 4. Archivos y rutas relevantes

## 4.1 Rutas de los repos

| Repo | Clone URL | Rama principal |
|---|---|---|
| paranice-demo | `https://github.com/Calybrat/paranice-demo` | `main` (trabajo en `claude/claude-teams-context-docs-3peucs`) |
| nutramerican-demo | `https://github.com/Calybrat/nutramerican-demo` | `main` |
| cimpa-demo | `https://github.com/nicolasgort01/cimpa-demo` | `main` |
| calybrat-website | `https://github.com/nicolasgort01/calybrat-website` | `main` |

## 4.2 Dónde tocar qué (aplica a Paranice y Nutramerican por igual)

| Si quieres… | Ve a… |
|---|---|
| Cambiar la paleta, un formato de número o el tema de las gráficas | `utils/formatters.py` |
| Cambiar cómo se cargan los datos o agregar una tabla | `utils/datos.py` |
| Cambiar credenciales, el modelo del agente o cualquier ajuste | `utils/config.py` *(solo Paranice hoy)* |
| Cambiar las reglas del negocio simulado o regenerar datos | `data/generate_data.py` |
| Agregar o cambiar una pantalla | `modules/pNN_*.py` + registrarla en `GRUPOS` de `app.py` |
| Cambiar el menú, los grupos o el sidebar | `app.py` |
| Cambiar el registro de visitas o el panel de accesos | `utils/visitas.py` |
| Cambiar el tema de Streamlit o la toolbar | `.streamlit/config.toml` |
| Cambiar los reportes descargables | `modules/p11_reportes.py` (Paranice) · `p14_reportes.py` (Nutramerican) |
| Cambiar el agente, su prompt o sus preguntas sugeridas | `modules/p12_agente.py` (Paranice) · `p15_agente.py` (Nutramerican) |

## 4.3 Archivos de contexto y configuración

| Archivo | Qué es |
|---|---|
| `CLAUDE.md` | Reglas del repo. **Claude Code lo carga solo** al abrir el proyecto |
| `docs/CONTEXTO_TECNICO.md` | Este documento |
| `docs/ONBOARDING-CLAUDE-TEAMS.md` | Cómo montar el contexto en la cuenta compartida |
| `README.md` | Cara pública del repo |
| `.streamlit/secrets.example.toml` | Plantilla de secretos → copiar a `secrets.toml` (ignorado por git) |
| `.env.example` | Plantilla para desarrollo local → copiar a `.env` (ignorado por git) |
| `.devcontainer/devcontainer.json` | Codespaces: Python 3.11, instala requirements, levanta el puerto 8501 |
| `.gitignore` | Ignora `__pycache__`, `.env`, `.streamlit/secrets.toml` |

## 4.4 Comandos

```bash
# correr cualquiera de los tres paneles
pip install -r requirements.txt
streamlit run app.py                  # http://localhost:8501

# regenerar los datos (semilla fija: mismo resultado siempre)
python3 data/generate_data.py

# prueba de humo: los módulos importan y exponen render()
python3 -c "import importlib,sys; sys.path.insert(0,'.'); \
  [importlib.import_module(m).render for m in ['modules.p01_dashboard']]"

# panel oculto de visitas
# → abrir la URL del demo con ?accesos=calybrat
```

---

# 5. APIs y conexiones

Inventario de **todo lo que se conecta con algo externo**, dividido en cuatro grupos para que no se
confundan: lo que consume nuestro código, dónde vive desplegado, los conectores de la cuenta de
Claude, y los sistemas del cliente que el producto final tendría que integrar.

## 5.1 APIs que consume nuestro código

| API | Para qué | Auth | Dónde se configura | Estado |
|---|---|---|---|---|
| **Anthropic API** | El Agente IA de los paneles (módulo 12 / 15 / 09) | API key `sk-ant-…` | `ANTHROPIC_API_KEY` en `st.secrets` o `.env` | **Opcional** — sin llave el agente corre en modo demo |
| **WooCommerce Store API** de `paranice.co` | Se usó para extraer las 28 referencias reales con sus PVP | Ninguna (pública) | — | Consulta puntual (ago-2026), no se llama en runtime |
| **`nutramerican.com/productos`** + su CDN | Las 52 referencias, sus PVP y **los renders oficiales** | Ninguna (pública) | — | Consulta puntual (sep-2026); las imágenes quedaron en `assets/productos/` |
| **`ip-api.com`** | Ciudad/región/país aproximados de cada visita | Ninguna (plan gratuito) | `utils/visitas.py` | ⚠️ **HTTP plano, sin TLS** (ver 3.9) |
| **`api.ipify.org`** | IP pública, como respaldo si no llega por cabeceras | Ninguna | `utils/visitas.py` | Solo se usa si fallan las cabeceras `X-Forwarded-For` |
| **Google Fonts** | Nunito (Paranice) · Montserrat (Nutramerican) | Ninguna | `@import` en el CSS de `utils/formatters.py` | Se carga en el navegador del visitante |

**Detalle del Agente IA:** manda a la API el prompt `CONTEXTO` (quién es el cliente, portafolio,
canales, diferencial) + `resumen_datos()` (un bloque compacto con las cifras del negocio al corte) +
el historial de la conversación. `max_tokens=1200`. Modelo por defecto **`claude-sonnet-5`**,
configurable con `ANTHROPIC_MODEL`.

### Cómo conectar el agente (2 minutos)

```bash
# 1. Sacar la llave en https://console.anthropic.com → API Keys
# 2. Local:
cp .streamlit/secrets.example.toml .streamlit/secrets.toml   # y pegar la llave
#    (alternativa) cp .env.example .env

# 3. Streamlit Cloud: Manage app → Settings → Secrets → pegar:
#    ANTHROPIC_API_KEY = "sk-ant-..."
```

Con eso, el módulo del agente muestra el chip **"🔗 Claude conectado · claude-sonnet-5"**, arranca
fuera de modo demo y ya no le pide la llave a nadie. Sin eso, sigue funcionando en modo demo — que es
el comportamiento correcto para un demo que se manda en frío.

## 5.2 Dónde vive desplegado

| Plataforma | Qué corre ahí | Notas de operación |
|---|---|---|
| **GitHub** | Los 4 repos | 2 bajo `Calybrat/`, 2 bajo `nicolasgort01/` — ver 3 y 4 |
| **Streamlit Community Cloud** | Los tres paneles | Los secretos se pegan en *Settings → Secrets*. **El sistema de archivos es efímero**: `visit_log.json` se reinicia en cada despliegue |
| **Netlify** | `calybrat-website` | Configurado en `netlify.toml`, sitio estático sin build |
| **GitHub Codespaces** | Entorno de desarrollo de Paranice | `.devcontainer/devcontainer.json`: Python 3.11, instala requirements, abre el 8501 |

## 5.3 Conectores de Claude activos en la cuenta

Verificado el 6 de septiembre de 2026. Estos son los que ya están conectados y disponibles en el chat:

| Conector | Estado | Para qué nos sirve |
|---|---|---|
| **HubSpot** | ✅ Conectado y habilitado | El CRM. Consultar contactos, empresas y negocios; crear y actualizar registros; leer campañas y analítica de marketing |
| **Gmail** | ✅ Conectado y habilitado | Buscar hilos, redactar respuestas y borradores, resumir conversaciones con clientes |
| **Google Calendar** | ✅ Conectado y habilitado | Agenda, crear eventos, buscar espacios para reuniones |
| **Google Drive** | ✅ Conectado y habilitado | Buscar, leer y subir archivos — útil para propuestas y material comercial |
| **Apollo.io** | ✅ Conectado y habilitado | Prospección: buscar contactos y empresas, enriquecer datos, secuencias y tareas. **Ojo: consume créditos** — las respuestas traen el costo estimado y el saldo |
| **Smartlead AI** | ⚠️ Instalado pero **sin conectar** ni habilitado en el chat | Email en frío. Si se va a usar, hay que autenticarlo y habilitarlo en la configuración de conectores |

**Cómo agregar o arreglar un conector:** en claude.ai → *Settings → Connectors*. Si aparece conectado
pero sus herramientas no responden en un chat, es que está **apagado para ese chat**: se habilita en
la configuración de conectores de la conversación.

**Al pasar a Teams:** la autenticación de estos conectores es **por persona**, no por espacio de
trabajo. Que estén conectados en una cuenta no los conecta en la otra — **cada quien va a tener que
autenticar los suyos** la primera vez. Lo que sí se comparte es el Proyecto y su conocimiento.

**GitHub** también está disponible como conector/herramienta dentro de las sesiones de Claude Code,
que es como se leyeron y modificaron los repos en esta sesión.

## 5.4 Sistemas del cliente que el producto final integraría

**Estos no son nuestros y hoy no están conectados a nada** — aparecen mencionados en los demos como
las fuentes que reemplazarían a los datos simulados. Es la lista de integraciones a cotizar cuando un
cliente diga que sí:

**Paranice:**
- **WooCommerce** (`paranice.co`) — ventas del canal propio. Tiene REST API con llaves de consumidor.
- **Mercado Pago** — pagos del canal propio.
- **Omnisend** — email marketing; de ahí saldrían las métricas reales de campañas.
- **Reportes de sell-out de Éxito, Carulla, Rappi y Fithub** — hoy llegan por archivo, no por API.
  Es el punto más difícil de la integración y el más valioso del panel.
- **El ERP y los Excel de producción** — lotes, ensayos de gluten, inventario.

**Nutramerican:**
- **ERP** — el corazón de la operación.
- **POS de las 8 tiendas** — tráfico, tickets, conversión.
- **E-commerce** (`nutramerican.com`).
- **MELONN** — operador 3PL de Bogotá y Medellín; estados de despacho y entrega.
- **INVIMA** — vigencia de registros sanitarios (hoy es una carpeta, no una API).
- **TRM del Banco de la República** — para la exposición en divisa. Es dato público y sí tiene fuente
  consultable.
- **WhatsApp Business y la línea #590** — los PQR.

## 5.5 Reglas de manejo de credenciales

1. **Ninguna llave se commitea, nunca.** `.env` y `.streamlit/secrets.toml` están en `.gitignore`
   en los tres repos.
2. Lo que se versiona son las **plantillas**: `.env.example` y `.streamlit/secrets.example.toml`.
3. En producción las llaves van en los **Secrets de Streamlit Cloud**, no en archivos.
4. **El orden de resolución siempre es el mismo**: `st.secrets` → variable de entorno → valor por
   defecto (`utils/config.py`).
5. Si una llave se filtra, se rota en la consola del proveedor. Como todo lo nuestro es de solo
   lectura sobre datos simulados, el daño se limita al consumo de la API.

---

# 6. Glosario

| Término | Qué significa aquí |
|---|---|
| **D2C** | *Direct to consumer.* La venta por la tienda propia, sin intermediario |
| **Sell-in** | Lo que la marca le factura a la cadena |
| **Sell-out** | Lo que la cadena le vende al consumidor final. Es el dato que importa y el que llega tarde |
| **Rotación** | Unidades vendidas por punto de venta por mes |
| **Quiebre de góndola** | Días en que el producto estuvo agotado en el PDV: venta perdida y riesgo de perder el espacio |
| **OTIF** | *On Time In Full.* Órdenes entregadas completas y a tiempo. Aquí: a tiempo **y** fill ≥ 98 %. Meta 95 % |
| **Fill rate** | Porcentaje de lo pedido por la cadena que efectivamente se despachó |
| **PVP** | Precio de venta al público en ese canal |
| **Margen del canal** | Lo que se queda el canal sobre el PVP |
| **Factor PVP** | Cuánto cuesta el producto en ese canal frente al PVP de la tienda propia |
| **COGS** | Costo de la mercancía vendida. Incluye la nómina de planta |
| **EBITDA** | Utilidad antes de intereses, impuestos, depreciación y amortización |
| **Cartera / aging** | Facturas por cobrar y su antigüedad (Vigente, 1-30, 31-60, 61-90, +90 días) |
| **DSO / DIO / DPO** | Días de cartera / de inventario / de proveedores |
| **Ciclo de conversión de caja** | DSO + DIO − DPO. Cuántos días pasan entre pagar y cobrar |
| **LTV** | Valor histórico acumulado de un cliente |
| **CAC** | Costo de adquirir un cliente nuevo |
| **LTV/CAC** | Relación entre ambos. Meta: más de 3× |
| **ROAS** | *Return on ad spend.* Ingresos por cada peso de pauta. Meta 3× |
| **CTR** | Clics sobre impresiones |
| **ppm** | Partes por millón de gluten en un lote. Límite para el claim "libre de gluten": **20 ppm** |
| **Merma** | Porcentaje de unidades planeadas que se pierden en producción. Meta <3 % |
| **OEE** | *Overall Equipment Effectiveness.* Qué tan bien se aprovecha la capacidad de planta (Nutramerican) |
| **FSSC 22000** | Certificación de inocuidad alimentaria. Nutramerican la tiene desde el 28-mar-2024 |
| **INVIMA** | Autoridad sanitaria colombiana. Cada producto necesita su registro vigente |
| **Farmacovigilancia** | Seguimiento a reportes de eventos adversos de los productos |
| **CEDI** | Centro de distribución |
| **3PL** | Operador logístico tercerizado (MELONN, en Nutramerican) |
| **TRM** | Tasa representativa del mercado (COP por USD) |
| **Maquila** | Fabricar para la marca de un tercero |
| **PQR** | Peticiones, quejas y reclamos |
| **CSAT** | Satisfacción del cliente tras atender un caso |
| **Riesgo de fuga** | Cliente con 2+ pedidos que lleva más de 120 días sin comprar |
| **Cola larga** | Las referencias de bajo volumen que igual consumen registro, corrida de planta e inventario |

---

*Documento hermano: `CONTEXTO_CALYBRAT.md` (Nico) — lado comercial, web y estrategia.*
*Si cambias el código, cambia este archivo en el mismo commit.*

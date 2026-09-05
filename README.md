# Paranice · Panel de Negocio

Demo construido por **Calybrat** para Paranice: un panel único donde el equipo ve, en un mismo
lugar y en tiempo real, lo que hoy vive repartido entre el back de WooCommerce, los reportes que
mandan las cadenas, los Excel de producción y los informes del contador.

---

## Por qué este panel y no un dashboard genérico

Paranice no es un e-commerce puro ni una marca de retail: es **las dos cosas a la vez**, en
**tres países**. Ese es exactamente el punto ciego que este panel resuelve.

| Realidad del negocio | Qué problema genera | Módulo que lo resuelve |
|---|---|---|
| Vende en tienda propia, Éxito, Carulla, Rappi, Fithub, naturistas, Costa Rica y EE.UU. | Cada canal reporta distinto y tarde; nadie ve el total | **Ventas Omnicanal** |
| Las cadenas reportan sell-out con retraso | No se sabe qué rota en góndola ni dónde se agotó | **Retail & Sell-Out** |
| El mismo producto vale $44.950 en la web, $49.900 en Éxito y $55.400 en Fithub | Conflicto de canal y presión de descuentos | **Portafolio & Precios** |
| Éxito y Carulla pagan a 60 días | Crecer en retail aprieta la caja aunque la utilidad se vea bien | **Finanzas & Cartera** |
| El claim "libre de gluten" depende de evitar contaminación cruzada | Un lote sobre 20 ppm es riesgo sanitario y reputacional | **Producción & Calidad** |
| El canal propio depende de pauta en Meta/Google/TikTok | Si sube el CAC, se cae la rentabilidad | **Marketing & Contenido** · **Clientes & Recompra** |
| Operación en Colombia, Costa Rica y Estados Unidos | Cada mercado tiene margen y costo logístico distinto | **Expansión Internacional** |

---

## Los 12 módulos

**Vista general** — `Dashboard General`: el estado del negocio en una pantalla, con alertas.

**Comercial**
- `Ventas Omnicanal` — todo lo que se factura, por canal, categoría, ciudad y país.
- `Retail & Sell-Out` — sell-in vs. sell-out, rotación por punto de venta, quiebres de góndola, OTIF.
- `Portafolio & Precios` — las 28 referencias, margen por SKU y arquitectura de precios por canal.
- `Clientes & Recompra` — LTV, CAC, segmentos y lista de clientes en riesgo de fuga.
- `Marketing & Contenido` — ROAS por canal, CAC y desempeño del blog de recetas.

**Operación**
- `Producción & Calidad` — lotes, ensayos de gluten en ppm, merma, inventario y proveedores.
- `Logística & Cumplimiento` — OTIF y fill rate a cadenas + entregas al consumidor.

**Dirección**
- `Finanzas & Cartera` — P&G mensual, EBITDA, aging de cartera y nómina.
- `Expansión Internacional` — Colombia, Costa Rica y EE.UU. comparados por salud, no solo por tamaño.
- `Reportes Automáticos` — 5 documentos listos para descargar e imprimir en PDF.
- `Agente IA Paranice` — preguntas en español sobre los datos del negocio.

---

## Sobre los datos

Los datos transaccionales son **simulados**, generados por `data/generate_data.py`. Lo que **sí es
real** y fue tomado de fuentes públicas para que el demo se sienta propio:

- **Catálogo y precios** — las 28 referencias y sus PVP salen de la API pública de la tienda
  (`paranice.co/wp-json/wc/store/products`, agosto 2026).
- **Categorías reales** — GranOLAS · Esparcibles · Pancakes & Waffles · Avena & Harinas · Combos · Merch.
- **Canales reales** — tienda propia (pedido mínimo $50.000, Mercado Pago, Omnisend), Éxito, Carulla,
  Rappi, Fithub, tiendas naturistas, Costa Rica y `paranice.us`.
- **Brecha de precios observada** — GranOLA Pistacho 300 g: $44.950 en paranice.co, $49.900 en Éxito,
  $55.400 en Fithub.
- **Identidad de marca** — logo, personajes ilustrados, morado `#2a1d65` y crema `#f4e1c1`
  tomados del sitio; tipografía Nunito como equivalente libre de Filson Soft.
- **Perfil de empresa** — fundada en 2019 en Bogotá, banda de 51–200 empleados (LinkedIn).

Para regenerar los datos:

```bash
python3 data/generate_data.py
```

---

## Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

Usuarios de acceso al demo:

| Usuario | Clave |
|---|---|
| `paranice_demo` | `Paranice2026` |
| `nicolas` | `Admin2026` |

Para cambiar o agregar usuarios: edita `auth_setup.py` y corre `python3 auth_setup.py`.

---

## Estructura

```
app.py                  navegación y login
utils/formatters.py     paleta de marca, helpers de formato y de gráficas
utils/auth.py           login y registro de visitas
modules/p01…p12         un archivo por módulo
data/generate_data.py   generador de los datos del demo
data/*.csv(.gz)         datos generados
assets/                 logo y personajes de la marca
```

---

Construido por [Calybrat](https://calybrat.com) · 2026

# Cómo montar el contexto de Paranice en la cuenta compartida (Claude Teams)

Guía práctica para que **Juan David y Nico trabajen con el mismo contexto** desde la cuenta de
equipo, sin tener que repetirle a Claude lo que ya sabemos.

La idea de fondo: **no hay que "migrar" conversaciones**. Las conversaciones viejas no se mueven de
cuenta y tampoco hace falta: todo lo que importaba de ellas ya está destilado en tres archivos de
este repo. Con eso, cualquier chat nuevo en la cuenta compartida arranca sabiendo lo mismo que
sabemos nosotros.

---

## Los tres archivos que son el contexto

| Archivo | Qué es | Quién lo lee |
|---|---|---|
| **`docs/CONTEXTO-PARANICE.md`** | La memoria completa: negocio, datos, módulos, decisiones, cifras, glosario. ~620 líneas. | El humano nuevo · Claude en la web (conocimiento del proyecto) |
| **`CLAUDE.md`** | El resumen operativo con las reglas que no se rompen. | **Claude Code lo lee solo**, automáticamente, al abrir el repo |
| **`README.md`** | La cara pública del demo: qué resuelve y cómo se corre. | Cualquiera que llegue al repo |

Están escritos para que se puedan leer sueltos, sin el resto del repo.

---

## Paso 1 · Crear el Proyecto en la cuenta de equipo

En Claude (web), en la cuenta compartida, crea un **Proyecto** llamado por ejemplo
**"Paranice · Demo Calybrat"**. Un proyecto es lo que hace que el contexto sea compartido: las
instrucciones y el conocimiento que le cargues quedan disponibles para los dos, en toda conversación
que abran dentro de él.

## Paso 2 · Subir el conocimiento del proyecto

Sube al conocimiento del proyecto, en este orden:

1. `docs/CONTEXTO-PARANICE.md` ← **el importante**
2. `README.md`
3. `data/generate_data.py` (opcional, pero muy útil: es la fuente de verdad de todas las reglas de negocio)
4. `utils/formatters.py` (opcional: paleta y helpers, para que Claude no invente colores ni formatos)

Con esos cuatro, Claude puede responder casi cualquier pregunta del proyecto sin abrir el repo.

## Paso 3 · Pegar las instrucciones del proyecto

Copia este bloque tal cual en las **instrucciones personalizadas** del proyecto:

```
Eres el asistente del proyecto "Paranice · Panel de Negocio", un demo comercial que Calybrat
(Juan David y Nico) construyó para Paranice, marca colombiana de alimentos saludables sin
gluten, sin azúcar añadida, veganos y keto.

Contexto: el archivo CONTEXTO-PARANICE.md del conocimiento del proyecto es la fuente de verdad.
Consúltalo antes de responder sobre el negocio, los datos, los módulos o las decisiones técnicas.
Si algo no está ahí, dilo en vez de suponerlo.

Sobre el proyecto:
- Es un panel BI en Streamlit, en español, con 12 módulos, desplegado sin login a propósito.
- Los datos transaccionales son simulados (data/generate_data.py, semilla fija). El catálogo,
  los precios, los canales y la identidad de marca son reales, de fuentes públicas.
- La fecha de corte de todo el demo es el 31 de agosto de 2026.
- Es una herramienta de venta: se juzga tanto por cómo habla como por cómo funciona.

Cómo quiero que trabajes:
- Responde en español, claro y de negocio, sin jerga innecesaria.
- Cuando des una cifra, di qué significa para el negocio y qué decisión habilita.
- Si propones código, respeta las reglas de CLAUDE.md: ningún módulo lee CSV directo (todo por
  utils/datos), nunca dtype category, nunca runOnSave, toda gráfica pasa por light(), toda plata
  por cop() y todo porcentaje por pct(), colores solo desde las constantes de utils/formatters.
- Los textos de UI van en español y cada KPI explica qué significa para el negocio.
- No inventes cifras del demo: o las calculas de los datos, o las citas del documento de contexto.
```

## Paso 4 · Conectar el repositorio

Conecta `github.com/Calybrat/paranice-demo` al proyecto (conector de GitHub). Así Claude ve el código
actual y no solo la foto del momento en que subiste los archivos.

## Paso 5 · Claude Code, para los dos

Cuando cualquiera de los dos abra el repo con **Claude Code** (terminal, web o la extensión del
editor), `CLAUDE.md` se carga **solo**. No hay que pegar nada. Si trabajan desde la cuenta de equipo,
los dos arrancan con exactamente las mismas reglas.

---

## Cómo mantenerlo vivo (la única regla)

> **Si cambias el código, cambia el documento en el mismo commit.**

El contexto solo sirve si está al día. En concreto:

| Si cambias… | Actualiza… |
|---|---|
| Un módulo, sus KPIs o sus pestañas | `docs/CONTEXTO-PARANICE.md` §5 |
| `data/generate_data.py` (reglas, semilla, fechas) | §6, §7 y **vuelve a correr las cifras de §8** |
| Una decisión técnica o un arreglo con historia | §9 (agrega el commit y el porqué) |
| Una regla que no se puede romper | `CLAUDE.md` §"Reglas que no se rompen" |
| Deuda técnica resuelta o nueva | §12 |

Cuando cambies `docs/CONTEXTO-PARANICE.md`, vuelve a subirlo al conocimiento del proyecto en la web
(el conector de GitHub sí se actualiza solo; los archivos subidos a mano, no).

---

## Cosas que la cuenta compartida NO hereda

Para que nadie las busque:

- **Las conversaciones anteriores.** No se migran entre cuentas. Por eso existe §9 del documento de
  contexto: ahí está el porqué de cada decisión que se tomó en esas conversaciones.
- **La API key de Anthropic del módulo 12.** Hoy se pega a mano en la UI del demo. Si se va a usar,
  cada quien pone la suya (y en el producto final debe salir de `st.secrets`).
- **`visit_log.json`.** Vive en el servidor donde esté desplegado el demo y se reinicia en cada deploy.

---

## Prueba de que quedó bien montado

Abre un chat nuevo en el proyecto y pregunta estas cinco. Si las responde bien y sin inventar,
el contexto quedó cargado:

1. *¿Por qué el demo no tiene login?*
   → Decisión de producto: pedir credenciales es fricción para enviarlo en frío; el control de acceso va en el producto final.
2. *¿Por qué no usamos `dtype category` en los datos?*
   → Porque `groupby` devolvía combinaciones inexistentes y aparecían filas con venta $0 (Paranice US facturando antes de existir).
3. *¿Cuánto vale la GranOLA de Pistacho en cada canal?*
   → $44.950 en paranice.co, $49.900 en Éxito, $55.400 en Fithub.
4. *¿Qué pasa si un lote da 25 ppm de gluten?*
   → Se rechaza; por encima de 20 ppm no sale al mercado (entre 15 y 20 va a cuarentena).
5. *¿Cuál es el canal que más factura y cuál el que más margen deja?*
   → Éxito factura más ($9,76 B históricos); el canal propio y Paranice US dejan más margen porque no hay comisión de cadena.

---

## Atajo si tienen prisa

Si solo van a hacer una cosa hoy: **suban `docs/CONTEXTO-PARANICE.md` al conocimiento del proyecto y
peguen el bloque de instrucciones del Paso 3.** Eso ya cubre el 90 % del contexto.

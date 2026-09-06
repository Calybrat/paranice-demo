# Cómo montar el contexto de Paranice en la cuenta compartida (Claude Teams)

Guía práctica para que **Juan David y Nico trabajen con el mismo contexto** desde la cuenta de
equipo, sin tener que repetirle a Claude lo que ya sabemos.

La idea de fondo: **no hay que "migrar" conversaciones**. Las conversaciones viejas no se mueven de
cuenta y tampoco hace falta: todo lo que importaba de ellas ya está destilado en archivos de texto.
Con eso, cualquier chat nuevo en la cuenta compartida arranca sabiendo lo mismo que sabemos nosotros.

---

## Los dos documentos maestros

El contexto se reparte en **dos archivos con la misma estructura**, uno por cada lado del negocio:

| Documento | Cubre | Lo mantiene |
|---|---|---|
| **`CONTEXTO_TECNICO.md`** (este repo, `docs/`) | El software: los 4 repos, qué existe, decisiones técnicas y su porqué, pendientes y bugs, rutas, APIs y conexiones | Juan David |
| **`CONTEXTO_CALYBRAT.md`** (repo de Nico) | Lo comercial, la web y la estrategia | Nico |

Ambos siguen la **misma estructura acordada**, justamente para que se puedan leer juntos hoy y
fusionar sin pelearse después:

1. Qué se construyó / qué existe hoy
2. Decisiones tomadas y por qué
3. Pendientes / bugs conocidos sin resolver
4. Archivos y rutas relevantes

*(El técnico agrega dos bloques propios: 5) APIs y conexiones · 6) glosario.)*

**La frontera entre los dos, para que no se contradigan:** lo que pasa **dentro de un repo** va en el
técnico; lo que pasa **fuera** (clientes, propuesta, precios, posicionamiento) va en el de Nico. Si
algo cae en la mitad —por ejemplo, por qué el demo no tiene login— vive en el técnico y el otro lo
referencia.

### Y además, en cada repo

| Archivo | Qué es | Quién lo lee |
|---|---|---|
| **`CLAUDE.md`** | El resumen operativo con las reglas que no se rompen | **Claude Code lo lee solo**, al abrir el repo |
| **`README.md`** | La cara pública del demo: qué resuelve y cómo se corre | Cualquiera que llegue al repo |

Todos están escritos para poder leerse sueltos, sin el resto del repo.

---

## Paso 1 · Crear el Proyecto en la cuenta de equipo

En Claude (web), en la cuenta compartida, crea un **Proyecto** llamado por ejemplo
**"Paranice · Demo Calybrat"**. Un proyecto es lo que hace que el contexto sea compartido: las
instrucciones y el conocimiento que le cargues quedan disponibles para los dos, en toda conversación
que abran dentro de él.

## Paso 2 · Subir el conocimiento del proyecto

Sube al conocimiento del proyecto, en este orden:

1. `docs/CONTEXTO_TECNICO.md` ← **el importante del lado técnico**
2. `CONTEXTO_CALYBRAT.md` ← **el de Nico**, el lado comercial
3. `README.md` de `paranice-demo` y de `nutramerican-demo`
4. `data/generate_data.py` (opcional, pero muy útil: es la fuente de verdad de las reglas de negocio)
5. `utils/formatters.py` (opcional: paleta y helpers, para que Claude no invente colores ni formatos)

**No hace falta fusionar los dos documentos maestros para arrancar.** Claude lee varios documentos de
contexto a la vez; súbanlos tal cual. La fusión en un solo documento maestro es una tarea de mediano
plazo, cuando empiecen a aparecer contradicciones — y para eso están la estructura común y la
frontera declarada arriba.

## Paso 3 · Pegar las instrucciones del proyecto

Copia este bloque tal cual en las **instrucciones personalizadas** del proyecto:

```
Eres el asistente de Calybrat, el estudio de Juan David y Nico. Calybrat construye paneles de
negocio (BI) a la medida como pieza de venta: demos que usan la identidad, el catálogo y los
canales reales del cliente, con datos transaccionales simulados.

Fuentes de verdad, en el conocimiento del proyecto:
- CONTEXTO_TECNICO.md   → el software: los 4 repos, qué existe, decisiones técnicas y su porqué,
                          pendientes y bugs, rutas, APIs y conexiones.
- CONTEXTO_CALYBRAT.md  → lo comercial, la web y la estrategia.
Consúltalos antes de responder. Si algo no está ahí, dilo en vez de suponerlo. Si los dos se
contradicen, dilo también en vez de escoger uno en silencio.

Lo que existe hoy:
- paranice-demo (12 módulos) y nutramerican-demo (15 módulos): paneles Streamlit en español.
- cimpa-demo: el primero, todavía con login. calybrat-website: el sitio, estático en Netlify.
- Todos con corte de datos al 31 de agosto de 2026 y generador con semilla fija.

Cómo quiero que trabajes:
- Responde en español, claro y de negocio, sin jerga innecesaria.
- Cuando des una cifra, di qué significa para el negocio y qué decisión habilita.
- Si propones código, respeta las reglas de CLAUDE.md: ningún módulo lee CSV directo (todo por
  utils/datos), ninguna credencial en el código ni en la UI (todo por utils/config), nunca dtype
  category, nunca runOnSave, toda gráfica pasa por light(), toda plata por cop() y todo
  porcentaje por pct(), colores solo desde las constantes de utils/formatters.
- Los textos de UI van en español y cada KPI explica qué significa para el negocio.
- No inventes cifras de los demos: o las calculas de los datos, o las citas del documento.
```

## Paso 4 · Conectar el repositorio

Conecta los repos al proyecto con el conector de GitHub, para que Claude vea el código actual y no
solo la foto del momento en que subiste los archivos:

- `github.com/Calybrat/paranice-demo`
- `github.com/Calybrat/nutramerican-demo`
- `github.com/nicolasgort01/cimpa-demo`
- `github.com/nicolasgort01/calybrat-website`

**Sobre los demás conectores** (HubSpot, Gmail, Google Calendar, Google Drive, Apollo.io): hoy están
conectados y funcionando, pero **su autenticación es por persona, no por espacio de trabajo**. Al
pasar a Teams, cada uno va a tener que autenticar los suyos la primera vez desde
*Settings → Connectors*. Lo que sí se comparte es el Proyecto y su conocimiento. Smartlead AI está
instalado pero sin conectar; si lo van a usar, hay que autenticarlo. El inventario completo está en
`CONTEXTO_TECNICO.md` §5.3.

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
| Un módulo, sus KPIs o sus pestañas | `docs/CONTEXTO_TECNICO.md` §1 (el repo que toque) |
| `data/generate_data.py` (reglas, semilla, fechas) | §1 — y **vuelve a correr las cifras** de la tabla del repo |
| Una decisión técnica o un arreglo con historia | §2 (agrega la decisión y el porqué) |
| Deuda técnica resuelta o nueva | §3 |
| Una ruta, un archivo nuevo o un comando | §4 |
| Una API, una llave o un conector | §5 |
| Una regla que no se puede romper | `CLAUDE.md` §"Reglas que no se rompen" |

Cuando cambies `docs/CONTEXTO_TECNICO.md`, vuelve a subirlo al conocimiento del proyecto en la web
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
5. *¿Cuál es el canal que más factura en Paranice y cuál el que más margen deja?*
   → Éxito factura más ($9,76 B históricos); el canal propio y Paranice US dejan más margen porque no hay comisión de cadena.
6. *¿Qué bug conocido tiene nutramerican-demo?*
   → `runOnSave = true` con el mismo `visitas.py` que escribe en el directorio vigilado: el bucle de recargas que Paranice ya diagnosticó y revirtió.
7. *¿Dónde se configura la API key del agente?*
   → En `utils/config.py`, que la lee de `st.secrets` o del entorno; nunca en el código ni en la UI.

---

## Atajo si tienen prisa

Si solo van a hacer una cosa hoy: **suban los dos documentos maestros al conocimiento del proyecto y
peguen el bloque de instrucciones del Paso 3.** Eso ya cubre el 90 % del contexto; los conectores y
la fusión pueden esperar.

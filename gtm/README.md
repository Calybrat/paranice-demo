# Calybrat · Motor de Prospección (Apollo → Smartlead → HubSpot)

> ⚠️ **Nota de ubicación.** Este repositorio es el *demo de Paranice*, un entregable
> de cara a un cliente. Esta carpeta contiene operación comercial **interna de
> Calybrat**. Si el repo se comparte con Paranice, esta carpeta debe moverse a un
> repositorio propio (`calybrat/gtm-engine`). Ver "Pendiente #0".

Diagnóstico y arquitectura del ciclo de prospección. Fecha de corte: **2026-09-05**.

---

## 1. Diagnóstico: qué dicen los números hoy

Datos reales tomados de la cuenta de Smartlead (reporte semanal #35, 24–30 ago) y
del portal de HubSpot `343445240`.

| Métrica | Valor | Lectura |
|---|---|---|
| Correos enviados (7 días) | 1.228 | Volumen sano para 5 buzones |
| Leads únicos contactados | 1.038 | — |
| Tasa de rebote | 0,10 % | **Excelente.** La infraestructura no es el problema |
| Buzones desconectados | 0 | Warmup activo en los 5 |
| Tasa de respuesta | 0,58 % | ≈ 6 respuestas sobre 1.038 |
| **Tasa de respuesta positiva** | **0,00 %** | **Cero. Este es el problema.** |
| Contactos en HubSpot | 179 | Todos en etapa `lead` |
| Negocios (deals) en HubSpot | **0** | No hay embudo: nada que medir |
| Créditos de Apollo restantes | **0** | 2.621 consumidos. Bloqueado |

**Conclusión:** la máquina *envía* bien y *entrega* bien. Lo que falla es **a quién
se le escribe y qué se le dice**. Un 0,10 % de rebote con 0,00 % de respuesta
positiva descarta deliverability y apunta directo a segmentación y mensaje.

---

## 2. El hallazgo de fondo: dos ICP distintos en 48 horas

Las 106 empresas cargadas en HubSpot son en realidad **dos listas sin relación**:

**Lote del 2 de septiembre — Hotelería y hospitalidad (~70 empresas)**
Marriott, Hilton, Hyatt, Sofitel, GHL Hoteles, Hoteles Dann, Viaggio, Blue Doors,
Hoteles MS, Aviatur, Club Campestre, apartamentos y hostales en Cartagena, Medellín
y Bogotá.

**Lote del 4 de septiembre — Industria, manufactura y distribución (~35 empresas)**
Corpacero y Agofer (acero), NitroFert y Cosmoagro (agroquímicos), Mathiesen y
Merquimia (químicos), Altipal (distribución), Gilmedica (dispositivos médicos),
Agaval (textil), Eduardoño (astillero), Sucafina (café).

Son dos negocios distintos, con dos compradores distintos, dos dolores distintos y
dos mensajes distintos. Se lanzaron con 48 horas de diferencia y **hoy no hay forma
de saber cuál de los dos funcionó mejor**, porque ningún contacto lleva marca de
campaña, industria ni origen.

### Registros que ensucian la base
`google.com`, `zohocorp.com`, `smartlead-team.com`, `smartleadupdates.com`,
`apollomailtester.com` y `calybratgroup.com` (la propia Calybrat) están cargados
como empresas. Son ruido del sincronizador de correo y distorsionan cualquier conteo.

---

## 3. Por qué hoy es imposible el ciclo de retroalimentación

El objetivo — *"saber qué campañas y qué industrias responden mejor"* — requiere
poder cruzar tres cosas por cada contacto: **de dónde salió**, **qué se le envió** y
**qué contestó**. Hoy falta todo eso:

| Se necesita | Estado actual |
|---|---|
| Industria de la empresa | Campo `industry` **vacío en las 106 empresas** |
| Tamaño de empresa | `numberofemployees` **vacío** |
| País | `country` **vacío** |
| Campaña de origen | **No existe el campo** |
| Respuesta / sentimiento | **No se sincroniza desde Smartlead** |
| Conversión a negocio | **0 deals creados** |

Todos los contactos entraron con `hs_analytics_source = OFFLINE`, es decir: **carga
manual de CSV**. Ese es el eslabón roto de la cadena.

---

## 4. Arquitectura objetivo

```
   APOLLO                SMARTLEAD              ZOHO MAIL             HUBSPOT
 (fuente de leads)   (motor de envío)      (buzones de salida)      (verdad única)
       │                     │                      │                    │
       │  1. Búsqueda ICP    │                      │                    │
       │     + enriquecido   │                      │                    │
       ├────────────────────>│                      │                    │
       │   marca: campaign_id, icp, industria       │                    │
       │                     │                      │                    │
       │                     │  2. Secuencia A/B    │                    │
       │                     ├─────────────────────>│                    │
       │                     │                      │  3. Envío + warmup │
       │                     │                      │                    │
       │                     │  4. Eventos: abierto, respondido,         │
       │                     │     sentimiento, rebote                   │
       │                     ├──────────────────────────────────────────>│
       │                     │        sync_smartlead_hubspot.py          │
       │                     │                                           │
       │                     │  5. Respuesta positiva ──> crea DEAL      │
       │                     │                                           │
       │<────────────────────┴───────────────────────────────────────────┤
       │  6. Retroalimentación: qué ICP, qué industria y qué asunto      │
       │     produjeron deals. Ajusta la siguiente búsqueda en Apollo.   │
```

El paso **4 y 5 es el que no existe hoy** y es el que convierte esto en una máquina
en vez de cuatro herramientas sueltas. `sync_smartlead_hubspot.py` lo implementa.

---

## 5. Esquema de atribución en HubSpot

Propiedades a crear en el objeto **Contacto** (grupo `calybrat_outbound`).
Sin esto, el ciclo no cierra. Detalle en [`hubspot_properties.md`](hubspot_properties.md).

| Propiedad interna | Tipo | Para qué |
|---|---|---|
| `cb_campaign_id` | texto | ID de campaña en Smartlead |
| `cb_campaign_name` | texto | Nombre legible de la campaña |
| `cb_icp` | desplegable | `hoteleria` · `industria` · `otro` |
| `cb_industry` | texto | Industria tomada de Apollo (no de HubSpot) |
| `cb_persona` | texto | Cargo objetivo (ej. Gerente General, Compras) |
| `cb_sequence_step` | número | Paso de la secuencia en el que respondió |
| `cb_reply_status` | desplegable | `sin_respuesta` · `positiva` · `neutral` · `negativa` · `baja` |
| `cb_replied_at` | fecha | Fecha de la respuesta |
| `cb_email_variant` | texto | Variante A/B del asunto y cuerpo |
| `cb_source_batch` | texto | Lote de carga (fecha + búsqueda de Apollo) |

Con estos diez campos, la pregunta *"¿qué industria responde mejor?"* pasa a ser una
sola consulta, y `analiza_rendimiento.py` la responde sola.

---

## 6. Pendientes que requieren acción de Juan o Nicolás

**#0 — Mover esta carpeta.** Operación interna de Calybrat dentro del repo demo de
un cliente. Crear `calybrat/gtm-engine` y trasladarla.

**#1 — Habilitar el conector de Smartlead.** Está instalado pero apagado para esta
sesión (`enabledInChat: false`). Sin él no puedo leer campañas ni respuestas desde
aquí. Se activa en los ajustes de conectores del chat.

**#2 — Recargar créditos de Apollo.** Quedan **0**. No se pueden extraer ni
enriquecer leads nuevos hasta recargar.

**#3 — Zoho.** No existe conector de *Zoho Mail* en el directorio (sí de Zoho CRM,
Books, Desk y Projects). **No hace falta**: los buzones de Zoho ya están conectados
dentro de Smartlead como cuentas de envío. Lo único pendiente en Zoho es
configuración DNS de una sola vez (SPF, DKIM, DMARC) — ver `deliverability.md`.

**#4 — Onboarding de HubSpot sin terminar.** El portal reporta `onboarded: false`, y
el objeto `CAMPAIGN` exige un plan superior. La atribución se hace con propiedades
personalizadas (sección 5), que sí funcionan en el plan actual.

**#5 — Decidir el ICP.** Es la decisión de negocio que desbloquea todo lo demás.
Ver la pregunta abierta al final de la conversación.

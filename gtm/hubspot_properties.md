# Propiedades de atribución en HubSpot

Portal: `343445240` · Objeto: **Contacto** · Grupo: `calybrat_outbound`

Sin estas propiedades el ciclo de retroalimentación no cierra: hoy los 179 contactos
entraron con `hs_analytics_source = OFFLINE` (carga de CSV) y no llevan marca de
campaña, industria ni resultado.

## Crearlas

```bash
export HUBSPOT_TOKEN=...        # app privada con alcance crm.schemas.contacts.write
python3 gtm/crear_propiedades.py --dry-run    # muestra qué crearía
python3 gtm/crear_propiedades.py              # las crea
```

El script es idempotente: si la propiedad ya existe la salta, así que se puede
volver a correr sin romper nada.

## Definición

| Interna | Etiqueta | Tipo | Valores |
|---|---|---|---|
| `cb_campaign_id` | ID de campaña | texto | ID numérico de Smartlead |
| `cb_campaign_name` | Campaña | texto | — |
| `cb_icp` | ICP | desplegable | `hoteleria`, `industria`, `otro` |
| `cb_industry` | Industria (Apollo) | texto | Se toma de Apollo, no del campo nativo |
| `cb_persona` | Cargo objetivo | texto | Gerente General, Compras, TI… |
| `cb_sequence_step` | Paso de secuencia | número | 1, 2, 3… |
| `cb_reply_status` | Estado de respuesta | desplegable | `sin_respuesta`, `positiva`, `neutral`, `negativa`, `baja` |
| `cb_replied_at` | Fecha de respuesta | fecha | — |
| `cb_email_variant` | Variante A/B | texto | A, B, C |
| `cb_source_batch` | Lote de origen | texto | Fecha + búsqueda de Apollo |

## Por qué `cb_industry` y no el campo nativo `industry`

El campo nativo de HubSpot usa una taxonomía cerrada que no coincide con la de
Apollo, y hoy está **vacío en las 106 empresas**. Guardar la industria tal como
viene de Apollo permite cruzar directamente contra la búsqueda que la generó, que
es justo lo que hace falta para decidir la siguiente lista.

## Limpieza pendiente de la base actual

Estos registros son ruido del sincronizador de correo y hay que borrarlos antes de
medir nada:

`google.com` · `zohocorp.com` · `smartlead-team.com` · `smartleadupdates.com`
`apollomailtester.com` · `calybratgroup.com` (la propia Calybrat)

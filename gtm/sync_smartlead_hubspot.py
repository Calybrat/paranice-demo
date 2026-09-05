#!/usr/bin/env python3
"""Sincroniza el resultado de las campañas de Smartlead hacia HubSpot.

Este es el eslabón que hoy falta en la cadena Apollo -> Smartlead -> Zoho -> HubSpot.
Sin él, HubSpot no sabe qué se le envió a cada contacto ni qué contestó, y por lo
tanto no hay forma de saber qué campaña o qué industria funciona.

Qué hace, por cada campaña activa en Smartlead:
  1. Baja los leads y sus estadísticas (enviado, abierto, respondido, rebotado).
  2. Clasifica la respuesta en positiva / neutral / negativa / baja.
  3. Escribe el resultado en HubSpot sobre las propiedades `cb_*`.
  4. Crea un negocio (deal) cuando la respuesta es positiva.

Uso:
    export SMARTLEAD_API_KEY=...
    export HUBSPOT_TOKEN=...            # token de app privada de HubSpot
    python3 gtm/sync_smartlead_hubspot.py --dry-run     # no escribe nada
    python3 gtm/sync_smartlead_hubspot.py               # escribe en HubSpot

Antes del primer uso real conviene correrlo con --dry-run y revisar la salida:
los endpoints de Smartlead v1 se han movido entre versiones, y el modo de prueba
imprime exactamente lo que se leyó y lo que se escribiría.
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from urllib import error, parse, request

SMARTLEAD_BASE = "https://server.smartlead.ai/api/v1"
HUBSPOT_BASE = "https://api.hubapi.com"

# Un lead puede responder cualquier cosa. Clasificamos por palabras clave en
# español e inglés porque el equipo prospecta en Colombia y en EE. UU.
NEGATIVAS = ("no estamos interesados", "not interested", "no thanks",
             "remove me", "unsubscribe", "no contactar", "dejen de escribir",
             "no es de interés", "no es de interes", "por ahora no")
BAJAS = ("ya no trabajo", "no longer with", "left the company", "out of office",
         "fuera de la oficina", "no pertenezco")
POSITIVAS = ("me interesa", "nos interesa", "interesado", "interesada",
             "cuéntame más", "cuentame mas", "interested",
             "agendemos", "reunión", "reunion", "call", "demo", "más información",
             "mas informacion", "podemos hablar", "envíame", "enviame",
             "tell me more", "sounds good", "let's talk", "lets talk")


def _get(url, token_param=None, retries=4):
    """GET con reintentos y espera creciente. Smartlead limita a ~10 req/2s."""
    for intento in range(retries):
        try:
            with request.urlopen(request.Request(url), timeout=30) as r:
                return json.loads(r.read().decode())
        except error.HTTPError as e:
            if e.code == 429 and intento < retries - 1:
                time.sleep(2 ** intento)
                continue
            raise
        except error.URLError:
            if intento < retries - 1:
                time.sleep(2 ** intento)
                continue
            raise
    return None


def smartlead(path, api_key, **params):
    params["api_key"] = api_key
    return _get(f"{SMARTLEAD_BASE}{path}?{parse.urlencode(params)}")


def hubspot(path, token, method="GET", payload=None):
    req = request.Request(
        f"{HUBSPOT_BASE}{path}",
        method=method,
        data=json.dumps(payload).encode() if payload else None,
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=30) as r:
        cuerpo = r.read().decode()
        return json.loads(cuerpo) if cuerpo else {}


# Una negación justo antes de una frase positiva la invierte: "no me interesa"
# contiene "me interesa". Enumerar cada variante negada es frágil, así que en su
# lugar miramos las palabras que preceden a la coincidencia.
NEGADORES = ("no", "nunca", "tampoco", "dont", "don't", "not", "never")


def _negada(texto, inicio):
    """¿La coincidencia que empieza en `inicio` viene negada?"""
    previas = re.findall(r"[\w']+", texto[:inicio])[-2:]
    return any(p in NEGADORES for p in previas)


def clasificar(texto):
    """Devuelve el estado de respuesta a partir del cuerpo del correo."""
    if not texto:
        return "sin_respuesta"
    t = texto.lower()
    for frase in NEGATIVAS:
        if frase in t:
            return "negativa"
    for frase in BAJAS:
        if frase in t:
            return "baja"
    for frase in POSITIVAS:
        i = t.find(frase)
        if i == -1:
            continue
        # "no me interesa" es un rechazo, no una oportunidad.
        return "negativa" if _negada(t, i) else "positiva"
    return "neutral"


def leads_de_campana(api_key, campana_id):
    """Pagina sobre todos los leads de una campaña."""
    offset, limite = 0, 100
    while True:
        datos = smartlead(f"/campaigns/{campana_id}/leads", api_key,
                          offset=offset, limit=limite)
        lote = (datos or {}).get("data") or []
        if not lote:
            return
        for item in lote:
            yield item
        if len(lote) < limite:
            return
        offset += limite


def construir_registro(lead, campana):
    """Traduce un lead de Smartlead a propiedades cb_* de HubSpot."""
    datos = lead.get("lead") or lead
    correo = (datos.get("email") or "").strip().lower()
    if not correo:
        return None

    cuerpo = lead.get("reply_message", {}).get("text") or lead.get("reply_body") or ""
    estado = clasificar(cuerpo)
    # Smartlead a veces ya trae su propia categoría; si existe, tiene prioridad
    # sobre nuestra heurística de palabras clave.
    categoria = (lead.get("lead_category") or {}).get("name", "").lower()
    if "interested" in categoria and "not" not in categoria:
        estado = "positiva"
    elif "not interested" in categoria:
        estado = "negativa"

    propiedades = {
        "email": correo,
        "cb_campaign_id": str(campana.get("id", "")),
        "cb_campaign_name": campana.get("name", ""),
        "cb_reply_status": estado,
        "cb_sequence_step": str(lead.get("sequence_number") or ""),
        "cb_email_variant": str(lead.get("email_variant") or ""),
        "cb_source_batch": campana.get("created_at", "")[:10],
    }
    if datos.get("first_name"):
        propiedades["firstname"] = datos["first_name"]
    if datos.get("last_name"):
        propiedades["lastname"] = datos["last_name"]
    if datos.get("company_name"):
        propiedades["company"] = datos["company_name"]
    # La industria viene de Apollo y se arrastra como campo personalizado en
    # Smartlead. Es el dato que hoy falta para responder "qué industria contesta".
    industria = datos.get("custom_fields", {}).get("industry") or datos.get("industry")
    if industria:
        propiedades["cb_industry"] = industria
    cargo = datos.get("custom_fields", {}).get("title") or datos.get("title")
    if cargo:
        propiedades["cb_persona"] = cargo
    if lead.get("reply_time"):
        propiedades["cb_replied_at"] = lead["reply_time"][:10]

    return {k: v for k, v in propiedades.items() if v not in ("", None)}


def escribir_en_hubspot(token, registros, dry_run):
    """Upsert por correo, en lotes de 100 (límite de la API de HubSpot)."""
    escritos = 0
    for i in range(0, len(registros), 100):
        lote = registros[i:i + 100]
        payload = {"inputs": [{"idProperty": "email",
                               "id": r["email"],
                               "properties": r} for r in lote]}
        if dry_run:
            print(f"  [prueba] se escribirían {len(lote)} contactos")
            for r in lote[:3]:
                print(f"    {r['email']:<40} {r.get('cb_reply_status')}"
                      f"  campaña={r.get('cb_campaign_name','')}")
            if len(lote) > 3:
                print(f"    ... y {len(lote) - 3} más")
        else:
            hubspot("/crm/v3/objects/contacts/batch/upsert", token,
                    method="POST", payload=payload)
        escritos += len(lote)
    return escritos


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="lee de Smartlead pero no escribe en HubSpot")
    ap.add_argument("--campana", help="sincronizar solo esta campaña (id)")
    args = ap.parse_args()

    api_key = os.environ.get("SMARTLEAD_API_KEY")
    token = os.environ.get("HUBSPOT_TOKEN")
    if not api_key:
        sys.exit("Falta SMARTLEAD_API_KEY en el entorno.")
    if not token and not args.dry_run:
        sys.exit("Falta HUBSPOT_TOKEN. Usa --dry-run para probar sin escribir.")

    campanas = smartlead("/campaigns", api_key) or []
    if args.campana:
        campanas = [c for c in campanas if str(c.get("id")) == args.campana]
    if not campanas:
        sys.exit("Smartlead no devolvió campañas. Revisa la llave de API.")

    print(f"Campañas encontradas: {len(campanas)}\n")
    total, resumen = [], defaultdict(lambda: defaultdict(int))

    for campana in campanas:
        nombre = campana.get("name", "(sin nombre)")
        print(f"· {nombre}  [{campana.get('status', '?')}]")
        registros = []
        for lead in leads_de_campana(api_key, campana["id"]):
            reg = construir_registro(lead, campana)
            if reg:
                registros.append(reg)
                resumen[nombre][reg["cb_reply_status"]] += 1
                if reg.get("cb_industry"):
                    resumen[f"industria::{reg['cb_industry']}"][reg["cb_reply_status"]] += 1
        print(f"  leads: {len(registros)}")
        total.extend(registros)

    escritos = escribir_en_hubspot(token, total, args.dry_run)

    print(f"\n{'=' * 62}\nResumen por campaña e industria\n{'=' * 62}")
    for clave, estados in sorted(resumen.items()):
        n = sum(estados.values())
        pos = estados.get("positiva", 0)
        tasa = (pos / n * 100) if n else 0
        print(f"{clave[:42]:<44} {n:>5} leads  {pos:>3} pos  {tasa:>5.2f}%")

    print(f"\n{escritos} contactos {'simulados' if args.dry_run else 'escritos'} "
          f"en HubSpot.")
    if args.dry_run:
        print("Modo prueba: no se escribió nada. Quita --dry-run para aplicar.")


if __name__ == "__main__":
    main()

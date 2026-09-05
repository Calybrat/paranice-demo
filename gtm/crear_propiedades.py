#!/usr/bin/env python3
"""Crea en HubSpot las propiedades de atribución `cb_*` del objeto Contacto.

Idempotente: salta las que ya existen. Ver hubspot_properties.md para el detalle.

    export HUBSPOT_TOKEN=...
    python3 gtm/crear_propiedades.py --dry-run
    python3 gtm/crear_propiedades.py
"""

import argparse
import json
import os
import sys
from urllib import error, request

BASE = "https://api.hubapi.com/crm/v3/properties/contacts"
GRUPO = "calybrat_outbound"


def _opciones(valores):
    return [{"label": v.replace("_", " ").capitalize(), "value": v, "displayOrder": i}
            for i, v in enumerate(valores)]


PROPIEDADES = [
    {"name": "cb_campaign_id", "label": "ID de campaña (Smartlead)", "type": "string",
     "fieldType": "text"},
    {"name": "cb_campaign_name", "label": "Campaña", "type": "string",
     "fieldType": "text"},
    {"name": "cb_icp", "label": "ICP", "type": "enumeration", "fieldType": "select",
     "options": _opciones(["hoteleria", "industria", "otro"])},
    {"name": "cb_industry", "label": "Industria (Apollo)", "type": "string",
     "fieldType": "text"},
    {"name": "cb_persona", "label": "Cargo objetivo", "type": "string",
     "fieldType": "text"},
    {"name": "cb_sequence_step", "label": "Paso de secuencia", "type": "number",
     "fieldType": "number"},
    {"name": "cb_reply_status", "label": "Estado de respuesta", "type": "enumeration",
     "fieldType": "select",
     "options": _opciones(["sin_respuesta", "positiva", "neutral", "negativa", "baja"])},
    {"name": "cb_replied_at", "label": "Fecha de respuesta", "type": "date",
     "fieldType": "date"},
    {"name": "cb_email_variant", "label": "Variante A/B", "type": "string",
     "fieldType": "text"},
    {"name": "cb_source_batch", "label": "Lote de origen", "type": "string",
     "fieldType": "text"},
]


def llamar(url, token, method="GET", payload=None):
    req = request.Request(
        url, method=method,
        data=json.dumps(payload).encode() if payload else None,
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"})
    with request.urlopen(req, timeout=30) as r:
        cuerpo = r.read().decode()
        return json.loads(cuerpo) if cuerpo else {}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = os.environ.get("HUBSPOT_TOKEN")
    if not token:
        sys.exit("Falta HUBSPOT_TOKEN en el entorno.")

    existentes = {p["name"] for p in llamar(BASE, token).get("results", [])}

    # El grupo debe existir antes que las propiedades.
    if not args.dry_run:
        try:
            llamar("https://api.hubapi.com/crm/v3/properties/contacts/groups",
                   token, "POST",
                   {"name": GRUPO, "label": "Calybrat · Outbound", "displayOrder": 10})
            print(f"grupo '{GRUPO}' creado")
        except error.HTTPError as e:
            if e.code != 409:      # 409 = ya existe
                raise
            print(f"grupo '{GRUPO}' ya existía")

    creadas = saltadas = 0
    for prop in PROPIEDADES:
        if prop["name"] in existentes:
            print(f"  = {prop['name']:<20} ya existe, se salta")
            saltadas += 1
            continue
        if args.dry_run:
            print(f"  + {prop['name']:<20} se crearía ({prop['fieldType']})")
        else:
            llamar(BASE, token, "POST", {**prop, "groupName": GRUPO})
            print(f"  + {prop['name']:<20} creada")
        creadas += 1

    print(f"\n{creadas} {'se crearían' if args.dry_run else 'creadas'}, "
          f"{saltadas} ya existían.")


if __name__ == "__main__":
    main()

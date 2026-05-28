#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
setup-airtable.py — Configura la base "Sistema Comercial Marli" en Airtable.

Compatible con Python 2.7 (macOS Mojave, /usr/bin/python) y Python 3.6+.
Sin dependencias externas: solo stdlib.

Pensado para ejecutarse desde TU máquina (no desde el entorno de Claude Code,
que tiene bloqueada la salida a api.airtable.com).

Uso:

    export AIRTABLE_TOKEN=patXXXXXXXX.YYYY...
    python scripts/setup-airtable.py inspect            # vuelca el schema actual
    python scripts/setup-airtable.py configure          # crea links, lookups y fórmulas
    python scripts/setup-airtable.py link-pairs         # enlaza Lucía→Diego, Marta→Sara
    python scripts/setup-airtable.py all                # configure + link-pairs

(En Mac/Linux modernos también funciona `python3 scripts/setup-airtable.py …`.)

Opcional:
    --base-id appyGM3EfHjhWrEAO     (por defecto)
    --dry-run                       solo imprime lo que haría
    --verbose                       muestra payloads y respuestas

Requisitos del PAT:
    - data.records:read, data.records:write
    - schema.bases:read, schema.bases:write
    - access scoped a appyGM3EfHjhWrEAO únicamente

Idempotente: si un campo ya existe con el mismo nombre, lo respeta y no lo recrea.
"""

from __future__ import print_function, unicode_literals

import argparse
import json
import os
import sys

try:  # Python 3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
except ImportError:  # Python 2
    from urllib2 import Request, urlopen, HTTPError

API = "https://api.airtable.com/v0"
BASE_ID_DEFAULT = "appyGM3EfHjhWrEAO"


def req(method, path, body=None, token=None, verbose=False):
    url = API + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    r = Request(url, data=data)
    r.get_method = lambda: method
    r.add_header("Authorization", "Bearer " + token)
    if body is not None:
        r.add_header("Content-Type", "application/json")
    if verbose:
        print(">>> {0} {1}".format(method, path))
        if body is not None:
            print(json.dumps(body, indent=2, ensure_ascii=False))
    try:
        resp = urlopen(r)
        raw = resp.read()
        payload = json.loads(raw.decode("utf-8")) if raw else {}
        if verbose:
            print("<<<", json.dumps(payload, indent=2, ensure_ascii=False)[:500])
        return payload
    except HTTPError as e:
        msg = e.read().decode("utf-8", "replace")
        print("ERROR {0} {1} {2}\n{3}".format(e.code, method, path, msg),
              file=sys.stderr)
        sys.exit(2)


def find_ci(items, name_key, name):
    for it in items:
        if (it.get(name_key) or "").lower() == name.lower():
            return it
    return None


def fetch_schema(base_id, token, verbose=False):
    return req("GET", "/meta/bases/{0}/tables".format(base_id),
               token=token, verbose=verbose)["tables"]


def list_records(base_id, table_id, token, verbose=False):
    out = []
    offset = None
    while True:
        path = "/{0}/{1}?pageSize=100".format(base_id, table_id)
        if offset:
            path += "&offset=" + offset
        page = req("GET", path, token=token, verbose=verbose)
        out.extend(page.get("records", []))
        offset = page.get("offset")
        if not offset:
            return out


# ---------------------------------------------------------------------------
# COMMAND: inspect
# ---------------------------------------------------------------------------

def cmd_inspect(args, token):
    tables = fetch_schema(args.base_id, token, args.verbose)
    for t in tables:
        print("\n## {0}  ({1})".format(t["name"], t["id"]))
        for f in t["fields"]:
            opts = f.get("options") or {}
            extra = ""
            if f["type"] in ("multipleRecordLinks", "multipleLookupValues"):
                extra = "  -> " + json.dumps(opts, ensure_ascii=False)
            print("  - {0:<30} {1:<25}{2}".format(f["name"], f["type"], extra))


# ---------------------------------------------------------------------------
# COMMAND: configure
# ---------------------------------------------------------------------------

def create_field(base_id, table, body, token, dry_run, verbose):
    existing = find_ci(table["fields"], "name", body["name"])
    if existing:
        print("  [ya] '{0}' existe ({1}, tipo {2})".format(
            body["name"], existing["id"], existing["type"]))
        return existing
    if dry_run:
        print("  [dry-run] crearia '{0}' ({1})".format(body["name"], body["type"]))
        return None
    new = req("POST",
              "/meta/bases/{0}/tables/{1}/fields".format(base_id, table["id"]),
              body=body, token=token, verbose=verbose)
    print("  [+] '{0}' creado ({1})".format(body["name"], new["id"]))
    table["fields"].append(new)
    return new


def cmd_configure(args, token):
    print("== Leyendo schema ==")
    tables = fetch_schema(args.base_id, token, args.verbose)

    t_equipo = find_ci(tables, "name", "Equipo")
    t_productos = find_ci(tables, "name", "Productos")
    t_leads = find_ci(tables, "name", "Leads")
    if not (t_equipo and t_productos and t_leads):
        print("ERROR: faltan tablas Equipo / Productos / Leads", file=sys.stderr)
        sys.exit(2)

    print("  Equipo:    " + t_equipo["id"])
    print("  Productos: " + t_productos["id"])
    print("  Leads:     " + t_leads["id"])

    # -------------------- EQUIPO --------------------
    print("\n== Equipo: autoenlace Closer asignado ==")
    create_field(args.base_id, t_equipo, {
        "name": "Closer asignado",
        "type": "multipleRecordLinks",
        "options": {
            "linkedTableId": t_equipo["id"],
            "prefersSingleRecordLink": True,
        },
        "description": "Cada setter enlaza aqui a su closer (single).",
    }, token, args.dry_run, args.verbose)

    # Re-fetch para tener el id real del nuevo Closer asignado
    tables = fetch_schema(args.base_id, token, args.verbose)
    t_equipo = find_ci(tables, "name", "Equipo")
    t_productos = find_ci(tables, "name", "Productos")
    t_leads = find_ci(tables, "name", "Leads")

    # -------------------- LEADS: links --------------------
    print("\n== Leads: link Setter ==")
    f_setter = create_field(args.base_id, t_leads, {
        "name": "Setter",
        "type": "multipleRecordLinks",
        "options": {
            "linkedTableId": t_equipo["id"],
            "prefersSingleRecordLink": True,
        },
        "description": "Setter responsable del lead.",
    }, token, args.dry_run, args.verbose)

    print("\n== Leads: link Producto ==")
    f_producto = create_field(args.base_id, t_leads, {
        "name": "Producto",
        "type": "multipleRecordLinks",
        "options": {
            "linkedTableId": t_productos["id"],
            "prefersSingleRecordLink": True,
        },
        "description": "Producto vendido (vacio hasta el cierre).",
    }, token, args.dry_run, args.verbose)

    # Re-fetch otra vez para tener los ids de Setter y Producto si se crearon ahora
    tables = fetch_schema(args.base_id, token, args.verbose)
    t_equipo = find_ci(tables, "name", "Equipo")
    t_productos = find_ci(tables, "name", "Productos")
    t_leads = find_ci(tables, "name", "Leads")
    f_setter = find_ci(t_leads["fields"], "name", "Setter")
    f_producto = find_ci(t_leads["fields"], "name", "Producto")

    # -------------------- LEADS: lookups via Setter --------------------
    if f_setter:
        print("\n== Leads: lookup Closer derivado ==")
        eq_closer = find_ci(t_equipo["fields"], "name", "Closer asignado")
        if eq_closer:
            create_field(args.base_id, t_leads, {
                "name": "Closer derivado",
                "type": "multipleLookupValues",
                "options": {
                    "recordLinkFieldId": f_setter["id"],
                    "fieldIdInLinkedTable": eq_closer["id"],
                },
                "description": "Closer al que va este lead. Se rellena solo desde el setter.",
            }, token, args.dry_run, args.verbose)

        eq_comision = (find_ci(t_equipo["fields"], "name", "comision_pct")
                       or find_ci(t_equipo["fields"], "name", "Comision pct")
                       or find_ci(t_equipo["fields"], "name", "comision"))
        if eq_comision:
            print("\n== Leads: lookup Comision_pct_setter ==")
            create_field(args.base_id, t_leads, {
                "name": "Comision_pct_setter",
                "type": "multipleLookupValues",
                "options": {
                    "recordLinkFieldId": f_setter["id"],
                    "fieldIdInLinkedTable": eq_comision["id"],
                },
            }, token, args.dry_run, args.verbose)
        else:
            print("  (!) No encuentro 'comision_pct' en Equipo. Crea ese campo a mano (0..1).")

    # -------------------- LEADS: lookups via Producto --------------------
    if f_producto:
        prod_fields = t_productos["fields"]
        prod_precio = find_ci(prod_fields, "name", "precio")
        prod_coste = (find_ci(prod_fields, "name", "coste_agencia")
                      or find_ci(prod_fields, "name", "coste agencia")
                      or find_ci(prod_fields, "name", "coste"))
        prod_margen = find_ci(prod_fields, "name", "margen")

        for label, src in (("Precio", prod_precio),
                           ("Coste agencia", prod_coste),
                           ("Margen", prod_margen)):
            if not src:
                print("  (!) No encuentro '{0}' en Productos; salto.".format(label))
                continue
            print("\n== Leads: lookup {0} ==".format(label))
            create_field(args.base_id, t_leads, {
                "name": label,
                "type": "multipleLookupValues",
                "options": {
                    "recordLinkFieldId": f_producto["id"],
                    "fieldIdInLinkedTable": src["id"],
                },
            }, token, args.dry_run, args.verbose)

    # -------------------- LEADS: campos auxiliares --------------------
    print("\n== Leads: campos auxiliares ==")
    create_field(args.base_id, t_leads, {
        "name": "Lote",
        "type": "number",
        "options": {"precision": 0},
        "description": "Cohorte del lead frio (1..N, ~500 por lote).",
    }, token, args.dry_run, args.verbose)

    create_field(args.base_id, t_leads, {
        "name": "Pareja asignada",
        "type": "singleSelect",
        "options": {"choices": [
            {"name": "Lucia-Diego", "color": "blueLight2"},
            {"name": "Marta-Sara", "color": "greenLight2"},
            {"name": "Jose", "color": "yellowLight2"},
        ]},
    }, token, args.dry_run, args.verbose)

    create_field(args.base_id, t_leads, {
        "name": "Proximo seguimiento",
        "type": "date",
        "options": {"dateFormat": {"format": "YYYY-MM-DD", "name": "iso"}},
    }, token, args.dry_run, args.verbose)

    create_field(args.base_id, t_leads, {
        "name": "Fecha ultimo cambio",
        "type": "lastModifiedTime",
        "options": {
            "isValid": True,
            "referencedFieldIds": None,
            "result": {
                "type": "dateTime",
                "options": {
                    "dateFormat": {"format": "YYYY-MM-DD", "name": "iso"},
                    "timeFormat": {"format": "HH:mm", "name": "24hour"},
                    "timeZone": "Europe/Madrid",
                },
            },
        },
    }, token, args.dry_run, args.verbose)

    # -------------------- LEADS: formulas --------------------
    print("\n== Leads: formulas (comisiones y metricas) ==")

    formulas = [
        ("Comision setter",
         "IF({Estado}='cerrado', IF({Margen}, {Margen}, 0) * IF({Comision_pct_setter}, {Comision_pct_setter}, 0), 0)"),
        ("Comision closer",
         "IF({Estado}='cerrado', IF({Margen}, {Margen}, 0) * 0.15, 0)"),
        ("Bonus mantenimiento closer",
         "IF(AND({Estado}='cerrado', {Mantenimiento}), 50, 0)"),
        ("Dias sin tocar",
         "DATETIME_DIFF(NOW(), {Fecha ultimo cambio}, 'days')"),
    ]
    for name, expr in formulas:
        create_field(args.base_id, t_leads, {
            "name": name,
            "type": "formula",
            "options": {"formula": expr},
        }, token, args.dry_run, args.verbose)

    print("\n== Listo. ==")
    print("Pendiente a mano (no automatizable via API):")
    print("  - Crear vistas Kanban + Grid agrupada + Ficha.")
    print("  - Subir los 10k leads y correr el script round-robin en Airtable Scripting.")
    print("  - Compartir la base con el equipo.")


# ---------------------------------------------------------------------------
# COMMAND: link-pairs
# ---------------------------------------------------------------------------

PAIRS = [("Lucia", "Diego"), ("Marta", "Sara")]


def cmd_link_pairs(args, token):
    print("== Enlazando setter -> closer en Equipo ==")
    tables = fetch_schema(args.base_id, token, args.verbose)
    t_equipo = find_ci(tables, "name", "Equipo")
    if not t_equipo:
        print("Falta tabla Equipo", file=sys.stderr)
        sys.exit(2)
    f_closer = find_ci(t_equipo["fields"], "name", "Closer asignado")
    if not f_closer:
        print("Crea primero 'Closer asignado' (corre `configure`).", file=sys.stderr)
        sys.exit(2)

    name_field = None
    for f in t_equipo["fields"]:
        if f.get("type") == "singleLineText" and "nombre" in f["name"].lower():
            name_field = f
            break
    if name_field is None:
        name_field = t_equipo["fields"][0]

    records = list_records(args.base_id, t_equipo["id"], token, args.verbose)
    by_name = {}
    for r in records:
        n = (r["fields"].get(name_field["name"]) or "").lower()
        # quita acentos basicos para que "lucía" matchee "lucia"
        n = (n.replace("á", "a").replace("é", "e").replace("í", "i")
              .replace("ó", "o").replace("ú", "u"))
        by_name[n] = r

    for setter, closer in PAIRS:
        s = by_name.get(setter.lower())
        c = by_name.get(closer.lower())
        if not s or not c:
            print("  (!) No encuentro {0} o {1}; salto.".format(setter, closer))
            continue
        if args.dry_run:
            print("  [dry-run] {0} -> {1}".format(setter, closer))
            continue
        req("PATCH",
            "/{0}/{1}/{2}".format(args.base_id, t_equipo["id"], s["id"]),
            body={"fields": {"Closer asignado": [c["id"]]}},
            token=token, verbose=args.verbose)
        print("  [+] {0} -> {1}".format(setter, closer))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Configura la base Airtable de Marli.")
    p.add_argument("command", choices=["inspect", "configure", "link-pairs", "all"])
    p.add_argument("--base-id", default=BASE_ID_DEFAULT)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    token = os.environ.get("AIRTABLE_TOKEN")
    if not token:
        print("Define AIRTABLE_TOKEN en el entorno.", file=sys.stderr)
        sys.exit(1)

    if args.command == "inspect":
        cmd_inspect(args, token)
    elif args.command == "configure":
        cmd_configure(args, token)
    elif args.command == "link-pairs":
        cmd_link_pairs(args, token)
    elif args.command == "all":
        cmd_configure(args, token)
        cmd_link_pairs(args, token)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
setup-airtable.py — Configura la base "Sistema Comercial Marli" en Airtable.

Pensado para ejecutarse desde TU máquina (no desde el entorno de Claude Code,
que tiene bloqueada la salida a api.airtable.com).

Uso:

    export AIRTABLE_TOKEN=patXXXXXXXX
    python3 scripts/setup-airtable.py inspect            # vuelca el schema actual
    python3 scripts/setup-airtable.py configure          # crea links, lookups y fórmulas
    python3 scripts/setup-airtable.py link-pairs         # enlaza Lucía→Diego, Marta→Sara
    python3 scripts/setup-airtable.py all                # configure + link-pairs

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

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.airtable.com/v0"
BASE_ID_DEFAULT = "appyGM3EfHjhWrEAO"


def req(method: str, path: str, body=None, token=None, verbose=False):
    url = f"{API}{path}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        r.add_header("Content-Type", "application/json")
    if verbose:
        print(f">>> {method} {path}")
        if body is not None:
            print(json.dumps(body, indent=2, ensure_ascii=False))
    try:
        with urllib.request.urlopen(r) as resp:
            payload = json.loads(resp.read() or b"{}")
            if verbose:
                print("<<<", json.dumps(payload, indent=2, ensure_ascii=False)[:500])
            return payload
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")
        print(f"ERROR {e.code} {method} {path}\n{msg}", file=sys.stderr)
        raise SystemExit(2)


def find(items, **kw):
    for it in items:
        if all(it.get(k) == v for k, v in kw.items()):
            return it
    return None


def find_ci(items, name_key, name):
    for it in items:
        if it.get(name_key, "").lower() == name.lower():
            return it
    return None


def fetch_schema(base_id, token, verbose=False):
    return req("GET", f"/meta/bases/{base_id}/tables", token=token, verbose=verbose)["tables"]


def list_records(base_id, table_id, token, verbose=False):
    out = []
    offset = None
    while True:
        path = f"/{base_id}/{table_id}?pageSize=100"
        if offset:
            path += f"&offset={offset}"
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
        print(f"\n## {t['name']}  ({t['id']})")
        for f in t["fields"]:
            opts = f.get("options") or {}
            extra = ""
            if f["type"] in ("multipleRecordLinks", "multipleLookupValues"):
                extra = f"  ⟶ {opts}"
            print(f"  - {f['name']:<30} {f['type']:<25}{extra}")


# ---------------------------------------------------------------------------
# COMMAND: configure
# ---------------------------------------------------------------------------

def create_field(base_id, table, body, token, dry_run, verbose):
    existing = find_ci(table["fields"], "name", body["name"])
    if existing:
        print(f"  ✓ '{body['name']}' ya existe ({existing['id']}, tipo {existing['type']})")
        return existing
    if dry_run:
        print(f"  [dry-run] crearía '{body['name']}' ({body['type']})")
        return None
    new = req("POST", f"/meta/bases/{base_id}/tables/{table['id']}/fields",
              body=body, token=token, verbose=verbose)
    print(f"  + '{body['name']}' creado ({new['id']})")
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
        raise SystemExit(2)

    print(f"  Equipo:    {t_equipo['id']}")
    print(f"  Productos: {t_productos['id']}")
    print(f"  Leads:     {t_leads['id']}")

    # -------------------- EQUIPO --------------------
    print("\n== Equipo: autoenlace Closer asignado ==")
    f_closer_asignado = create_field(args.base_id, t_equipo, {
        "name": "Closer asignado",
        "type": "multipleRecordLinks",
        "options": {
            "linkedTableId": t_equipo["id"],
            "prefersSingleRecordLink": True,
        },
        "description": "Cada setter enlaza aquí a su closer (single).",
    }, token, args.dry_run, args.verbose)

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
        "description": "Producto vendido (vacío hasta el cierre).",
    }, token, args.dry_run, args.verbose)

    # -------------------- LEADS: lookups via Setter --------------------
    if f_setter:
        print("\n== Leads: lookup Closer derivado ==")
        # localiza el id del campo 'Closer asignado' en Equipo (puede ser nuevo)
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

        # lookup comision_pct del setter
        eq_comision = find_ci(t_equipo["fields"], "name", "comision_pct") \
            or find_ci(t_equipo["fields"], "name", "Comision pct") \
            or find_ci(t_equipo["fields"], "name", "Comisión") \
            or find_ci(t_equipo["fields"], "name", "comision")
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
            print("  (!) No encuentro 'comision_pct' en Equipo. Crea ese campo a mano (% con 0..1) y vuelve a correr.")

    # -------------------- LEADS: lookups via Producto --------------------
    if f_producto:
        # Detectar nombres reales en Productos
        prod_fields = t_productos["fields"]
        prod_precio = find_ci(prod_fields, "name", "precio") or find_ci(prod_fields, "name", "Precio")
        prod_coste = find_ci(prod_fields, "name", "coste_agencia") \
            or find_ci(prod_fields, "name", "coste agencia") \
            or find_ci(prod_fields, "name", "Coste agencia") \
            or find_ci(prod_fields, "name", "coste")
        prod_margen = find_ci(prod_fields, "name", "margen") or find_ci(prod_fields, "name", "Margen")

        for label, src in [
            ("Precio", prod_precio),
            ("Coste agencia", prod_coste),
            ("Margen", prod_margen),
        ]:
            if not src:
                print(f"  (!) No encuentro '{label}' en Productos; saltando lookup.")
                continue
            print(f"\n== Leads: lookup {label} ==")
            create_field(args.base_id, t_leads, {
                "name": label,
                "type": "multipleLookupValues",
                "options": {
                    "recordLinkFieldId": f_producto["id"],
                    "fieldIdInLinkedTable": src["id"],
                },
            }, token, args.dry_run, args.verbose)

    # -------------------- LEADS: campos de gestión --------------------
    print("\n== Leads: campos auxiliares ==")
    create_field(args.base_id, t_leads, {
        "name": "Lote",
        "type": "number",
        "options": {"precision": 0},
        "description": "Cohorte del lead frío (1..N, ~500 por lote).",
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
            "result": {"type": "dateTime", "options": {"dateFormat": {"format": "YYYY-MM-DD", "name": "iso"},
                                                       "timeFormat": {"format": "HH:mm", "name": "24hour"},
                                                       "timeZone": "Europe/Madrid"}},
        },
    }, token, args.dry_run, args.verbose)

    # -------------------- LEADS: fórmulas --------------------
    print("\n== Leads: fórmulas (comisiones y métricas) ==")

    formulas = [
        ("Comision setter",
         "IF({Estado}='cerrado', IF({Margen}, {Margen}, 0) * IF({Comision_pct_setter}, {Comision_pct_setter}, 0), 0)"),
        ("Comision closer",
         "IF({Estado}='cerrado', IF({Margen}, {Margen}, 0) * 0.15, 0)"),
        ("Bonus mantenimiento closer",
         "IF(AND({Estado}='cerrado', {Mantenimiento}), 50, 0)"),
        ("Ficha completa",
         "IF(AND({Dolor detectado}, {Num pacientes}, {Objecion anticipada}, {Fecha videollamada}), '✅', '❌')"),
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
    print("Pendiente a mano (la API no lo permite o es más rápido en UI):")
    print("  · Crear vistas Kanban + Grid agrupada + Form/Grid de ficha.")
    print("  · Subir los 10k leads y correr el script round-robin en Airtable Scripting.")
    print("  · Compartir la base con el equipo.")


# ---------------------------------------------------------------------------
# COMMAND: link-pairs
# ---------------------------------------------------------------------------

PAIRS = [("Lucía", "Diego"), ("Lucia", "Diego"), ("Marta", "Sara")]


def cmd_link_pairs(args, token):
    print("== Enlazando setter → closer en Equipo ==")
    tables = fetch_schema(args.base_id, token, args.verbose)
    t_equipo = find_ci(tables, "name", "Equipo")
    if not t_equipo:
        raise SystemExit("Falta tabla Equipo")
    f_closer = find_ci(t_equipo["fields"], "name", "Closer asignado")
    if not f_closer:
        raise SystemExit("Crea primero el campo 'Closer asignado' (corre `configure`).")

    name_field = next((f for f in t_equipo["fields"]
                       if f.get("type") == "singleLineText"
                       and "nombre" in f["name"].lower()), None) \
        or t_equipo["fields"][0]  # fallback al primary

    records = list_records(args.base_id, t_equipo["id"], token, args.verbose)
    by_name = {(r["fields"].get(name_field["name"]) or "").lower(): r for r in records}

    for setter, closer in PAIRS:
        s = by_name.get(setter.lower())
        c = by_name.get(closer.lower())
        if not s or not c:
            print(f"  (!) No encuentro {setter} o {closer}; salto.")
            continue
        if args.dry_run:
            print(f"  [dry-run] {setter} → {closer}")
            continue
        req("PATCH", f"/{args.base_id}/{t_equipo['id']}/{s['id']}",
            body={"fields": {"Closer asignado": [c["id"]]}},
            token=token, verbose=args.verbose)
        print(f"  ✓ {setter} → {closer}")


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
        raise SystemExit(1)

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

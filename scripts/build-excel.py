#!/usr/bin/env python3
"""Genera Sistema-Comercial-Marli.xlsx con todas las hojas, fórmulas,
validaciones y datos de arranque.

Uso:  python3 scripts/build-excel.py
Salida: sistema-comercial-marli/Sistema-Comercial-Marli.xlsx
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.comments import Comment
import os

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "sistema-comercial-marli", "Sistema-Comercial-Marli.xlsx")

wb = Workbook()

# Estilos comunes
HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(bold=True, size=14, color="111827")
NOTE_FONT = Font(italic=True, color="6B7280", size=10)
THIN = Side(style="thin", color="D1D5DB")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

EUR = '#,##0.00 €'
PCT = '0.00%'
DATE = 'YYYY-MM-DD'


def set_header(ws, row, cols):
    for i, name in enumerate(cols, 1):
        c = ws.cell(row=row, column=i, value=name)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = CENTER
        c.border = BORDER


def fit_cols(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------------------------------------------------------------------
# 1. Hoja LÉEME
# ---------------------------------------------------------------------------
ws = wb.active
ws.title = "LÉEME"
ws["A1"] = "Sistema Comercial Marli — Plantilla Excel"
ws["A1"].font = TITLE_FONT
ws["A3"] = (
    "Esta plantilla recoge todo el sistema de gestión comercial: equipo, "
    "productos, pipeline de leads, comisiones y ranking. Está pensada para "
    "trabajar en local sin depender de servicios externos."
)
ws["A3"].alignment = LEFT
ws.row_dimensions[3].height = 60

ws["A5"] = "Orden de hojas"
ws["A5"].font = Font(bold=True, size=12)
guide = [
    ("Equipo", "Una fila por persona. El rol y la pareja determinan a quién va cada lead y qué comisión cobra."),
    ("Productos", "Catálogo con precio, coste y margen. Todas las comisiones se calculan sobre el MARGEN."),
    ("Parejas", "Mapeo Pareja→Setter→Closer→% comisiones. Solo se toca si cambias parejas o porcentajes."),
    ("Leads", "Pipeline. Aquí trabaja el equipo. Las columnas grises se calculan solas."),
    ("Ranking", "Métricas por setter y lote: tasa de contacto, agendado, presentación, cierre, € facturados, € comisión."),
    ("Comisiones", "Resumen mensual por persona. Se rellena solo a partir de Leads."),
    ("Round-Robin", "Generador del campo 'Pareja asignada' para los 10.000 leads fríos."),
]
for i, (sheet, desc) in enumerate(guide, start=6):
    ws.cell(row=i, column=1, value=sheet).font = Font(bold=True)
    ws.cell(row=i, column=2, value=desc).alignment = LEFT

ws["A14"] = "Reglas de oro"
ws["A14"].font = Font(bold=True, size=12)
rules = [
    "1. Una venta solo genera comisión si Estado='cerrado' y la Ficha estaba completa antes de la videollamada.",
    "2. Comisiones siempre sobre MARGEN, nunca sobre precio.",
    "3. Mantenimiento contratado = 50 € únicos extra al closer.",
    "4. No tocar columnas grises (fórmulas). Solo se introduce dato en las blancas.",
    "5. Los desplegables están protegidos: usa solo los valores válidos.",
]
for i, r in enumerate(rules, start=15):
    ws.cell(row=i, column=1, value=r).alignment = LEFT

ws["A22"] = "Productos y márgenes (referencia rápida)"
ws["A22"].font = Font(bold=True, size=12)
prod_ref = [
    ("Producto", "Precio", "Coste agencia", "Margen", "Setter (5%)", "Closer (15%)"),
    ("Automatización Informes", 449, 200, 249, 12.45, 37.35),
    ("Chatbot IA", 999, 500, 499, 24.95, 74.85),
    ("Pack Premium", 1349, 700, 649, 32.45, 97.35),
    ("Mantenimiento (300€/mes)", "-", "-", "-", "-", "+50€ únicos al closer"),
]
for i, row in enumerate(prod_ref, start=23):
    for j, val in enumerate(row, start=1):
        c = ws.cell(row=i, column=j, value=val)
        if i == 23:
            c.fill = HEADER_FILL
            c.font = HEADER_FONT
            c.alignment = CENTER
        else:
            c.border = BORDER

fit_cols(ws, [28, 20, 18, 14, 16, 30])


# ---------------------------------------------------------------------------
# 2. Hoja EQUIPO
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Equipo")
cols = ["ID", "Nombre", "Rol", "Email", "Pareja", "Comisión %", "Activo"]
set_header(ws, 1, cols)
equipo_data = [
    ("E01", "Lucía", "setter", "lucia@marliagency.com", "Lucia-Diego", 0.05, True),
    ("E02", "Marta", "setter", "marta@marliagency.com", "Marta-Sara", 0.05, True),
    ("E03", "Diego", "closer", "diego@marliagency.com", "Lucia-Diego", 0.15, True),
    ("E04", "Sara", "closer", "sara@marliagency.com", "Marta-Sara", 0.15, True),
    ("E05", "José", "closer", "jose@marliagency.com", "Jose", 0.20, True),
]
for i, row in enumerate(equipo_data, start=2):
    for j, v in enumerate(row, start=1):
        c = ws.cell(row=i, column=j, value=v)
        c.border = BORDER
        if j == 6:
            c.number_format = PCT
fit_cols(ws, [8, 16, 12, 28, 16, 14, 10])

dv_rol = DataValidation(type="list", formula1='"setter,closer,setter+closer"', allow_blank=False)
dv_rol.add(f"C2:C200")
ws.add_data_validation(dv_rol)

dv_pareja_eq = DataValidation(type="list", formula1='"Lucia-Diego,Marta-Sara,Jose"', allow_blank=False)
dv_pareja_eq.add(f"E2:E200")
ws.add_data_validation(dv_pareja_eq)


# ---------------------------------------------------------------------------
# 3. Hoja PRODUCTOS
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Productos")
cols = ["ID", "Nombre", "Precio", "Coste agencia", "Margen", "Tipo", "Notas"]
set_header(ws, 1, cols)
productos = [
    ("P01", "Automatización Informes", 449, 200, "=C2-D2", "one-time", "Informes automatizados para psicólogos"),
    ("P02", "Chatbot IA", 999, 500, "=C3-D3", "one-time", "Chatbot conversacional con IA"),
    ("P03", "Pack Premium", 1349, 700, "=C4-D4", "one-time", "Informes + Chatbot integrados"),
    ("P04", "Mantenimiento", 300, 0, "=C5-D5", "monthly", "Suscripción mensual. 50€ únicos al closer cuando se contrata."),
]
for i, row in enumerate(productos, start=2):
    for j, v in enumerate(row, start=1):
        c = ws.cell(row=i, column=j, value=v)
        c.border = BORDER
        if j in (3, 4, 5):
            c.number_format = EUR
fit_cols(ws, [8, 26, 12, 16, 12, 14, 40])

dv_tipo = DataValidation(type="list", formula1='"one-time,monthly"', allow_blank=False)
dv_tipo.add("F2:F200")
ws.add_data_validation(dv_tipo)


# ---------------------------------------------------------------------------
# 4. Hoja PAREJAS  (mapeo central para que el closer salga solo)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Parejas")
cols = ["Pareja", "Setter", "Closer", "Setter %", "Closer %", "Notas"]
set_header(ws, 1, cols)
parejas = [
    ("Lucia-Diego", "Lucía", "Diego", 0.05, 0.15, "Pareja estándar"),
    ("Marta-Sara",  "Marta", "Sara",  0.05, 0.15, "Pareja estándar"),
    ("Jose",        "José",  "José",  0.20, 0.20, "José vende en solitario (closer 20%)"),
    ("Jose-asistido","Otro setter", "José", 0.05, 0.10, "Setter agenda, José cierra (10% closer)"),
]
for i, row in enumerate(parejas, start=2):
    for j, v in enumerate(row, start=1):
        c = ws.cell(row=i, column=j, value=v)
        c.border = BORDER
        if j in (4, 5):
            c.number_format = PCT
fit_cols(ws, [16, 14, 14, 12, 12, 40])


# ---------------------------------------------------------------------------
# 5. Hoja LEADS  (la principal)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Leads")
cols = [
    "ID lead", "Nombre psicólogo", "Email", "Teléfono", "Ciudad",
    "Lote", "Pareja asignada", "Setter", "Closer derivado",
    "Estado", "Fecha último cambio",
    "Dolor detectado", "Nº pacientes", "Objeción anticipada", "Fecha videollamada",
    "Ficha completa",
    "Producto", "Precio", "Margen",
    "Euros cobrado", "Mantenimiento",
    "Comisión setter", "Comisión closer", "Bonus mantenimiento",
    "Notas",
]
set_header(ws, 1, cols)
fit_cols(ws, [10, 24, 24, 14, 14, 8, 14, 12, 14, 14, 16,
              28, 12, 28, 16, 14, 22, 12, 12, 14, 14, 16, 16, 18, 30])

GREY_FILL = PatternFill("solid", fgColor="F3F4F6")
GREY_FONT = Font(color="111827", italic=True)
auto_cols = [8, 9, 16, 18, 19, 22, 23, 24]   # Setter, Closer, Ficha completa, Precio, Margen, Comisiones
for col in auto_cols:
    letter = get_column_letter(col)
    ws.column_dimensions[letter].width = ws.column_dimensions[letter].width

N = 50   # filas de muestra. El usuario duplica filas para añadir más.
for r in range(2, 2 + N):
    # Setter = VLOOKUP(Pareja, Parejas, 2)
    ws.cell(row=r, column=8, value=f'=IFERROR(VLOOKUP(G{r},Parejas!A:F,2,FALSE),"")')
    # Closer = VLOOKUP(Pareja, Parejas, 3)
    ws.cell(row=r, column=9, value=f'=IFERROR(VLOOKUP(G{r},Parejas!A:F,3,FALSE),"")')
    # Ficha completa
    ws.cell(row=r, column=16,
            value=(f'=IF(AND(L{r}<>"",M{r}<>"",N{r}<>"",O{r}<>""),"✅","❌")'))
    # Precio = VLOOKUP(Producto, Productos, 3)
    ws.cell(row=r, column=18,
            value=f'=IFERROR(VLOOKUP(Q{r},Productos!B:F,2,FALSE),"")')
    # Margen = VLOOKUP(Producto, Productos, 5-1=4 from col B)
    ws.cell(row=r, column=19,
            value=f'=IFERROR(VLOOKUP(Q{r},Productos!B:F,4,FALSE),"")')
    # Comisión setter = IF Estado=cerrado, Margen * Setter%
    ws.cell(row=r, column=22,
            value=(f'=IFERROR(IF(J{r}="cerrado",'
                   f'S{r}*VLOOKUP(G{r},Parejas!A:E,4,FALSE),0),0)'))
    # Comisión closer = IF Estado=cerrado, Margen * Closer%
    ws.cell(row=r, column=23,
            value=(f'=IFERROR(IF(J{r}="cerrado",'
                   f'S{r}*VLOOKUP(G{r},Parejas!A:E,5,FALSE),0),0)'))
    # Bonus mantenimiento = IF cerrado AND Mantenimiento, 50
    ws.cell(row=r, column=24,
            value=f'=IF(AND(J{r}="cerrado",U{r}=TRUE),50,0)')

    for col in [8, 9, 16, 18, 19, 22, 23, 24]:
        c = ws.cell(row=r, column=col)
        c.fill = GREY_FILL
        c.font = GREY_FONT
        c.border = BORDER

    for col in [18, 19, 20, 22, 23, 24]:
        ws.cell(row=r, column=col).number_format = EUR

    ws.cell(row=r, column=11).number_format = DATE
    ws.cell(row=r, column=15).number_format = DATE

    # borders en celdas blancas también
    for col in range(1, len(cols) + 1):
        if col not in [8, 9, 16, 18, 19, 22, 23, 24]:
            ws.cell(row=r, column=col).border = BORDER

# Validaciones de datos
dv_estado = DataValidation(type="list",
    formula1='"frio,contactado,cita agendada,presentado,cerrado,perdido"',
    allow_blank=False)
dv_estado.add(f"J2:J{1+N}")
ws.add_data_validation(dv_estado)

dv_pareja = DataValidation(type="list",
    formula1='"Lucia-Diego,Marta-Sara,Jose,Jose-asistido"', allow_blank=False)
dv_pareja.add(f"G2:G{1+N}")
ws.add_data_validation(dv_pareja)

dv_prod = DataValidation(type="list",
    formula1='"Automatización Informes,Chatbot IA,Pack Premium"', allow_blank=True)
dv_prod.add(f"Q2:Q{1+N}")
ws.add_data_validation(dv_prod)

dv_mant = DataValidation(type="list", formula1='"TRUE,FALSE"', allow_blank=True)
dv_mant.add(f"U2:U{1+N}")
ws.add_data_validation(dv_mant)

# Datos de muestra (3 leads ejemplo)
samples = [
    ("L0001", "Clínica Ana Rodríguez",  "ana@clinica.com",   "611111111", "Madrid",  1, "Lucia-Diego",
     "", "", "presentado", "2026-05-20",
     "No capta pacientes online", 35, "Precio alto", "2026-05-22", "",
     "Pack Premium", "", "", 0, False, "", "", "", ""),
    ("L0002", "Centro Psicología Luna", "info@luna.es",      "622222222", "Barcelona", 1, "Marta-Sara",
     "", "", "cerrado", "2026-05-25",
     "Quiere captar más jóvenes", 60, "Tiempo de implantación", "2026-05-24", "",
     "Chatbot IA", "", "", 999, True, "", "", "", "Cerrado + mantenimiento"),
    ("L0003", "Psicólogo Juan Pérez",   "juan@gabinete.com", "633333333", "Valencia", 1, "Jose",
     "", "", "contactado", "2026-05-26",
     "Solo, sin equipo", 12, "Duda si IA cuadra con su perfil", "", "",
     "", "", "", 0, False, "", "", "", ""),
]
for r_idx, sample in enumerate(samples, start=2):
    for c_idx, val in enumerate(sample, start=1):
        if c_idx in [8, 9, 16, 18, 19, 22, 23, 24] and val == "":
            continue  # no sobreescribir fórmulas
        if val == "":
            continue
        ws.cell(row=r_idx, column=c_idx, value=val)

# Formato condicional en Ficha completa
ws.conditional_formatting.add(
    f"P2:P{1+N}",
    FormulaRule(formula=[f'P2="✅"'], fill=PatternFill("solid", fgColor="D1FAE5")))
ws.conditional_formatting.add(
    f"P2:P{1+N}",
    FormulaRule(formula=[f'P2="❌"'], fill=PatternFill("solid", fgColor="FEE2E2")))

# Congelar cabecera
ws.freeze_panes = "B2"


# ---------------------------------------------------------------------------
# 6. Hoja RANKING (por setter y lote)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Ranking")
ws["A1"] = "Ranking semanal por setter y lote"
ws["A1"].font = TITLE_FONT
ws["A2"] = "Cambia el lote en B4 para filtrar. Las métricas se recalculan solas."
ws["A2"].font = NOTE_FONT

ws["A4"] = "Lote a analizar:"
ws["A4"].font = Font(bold=True)
ws["B4"] = 1
ws["B4"].font = Font(bold=True)
ws["B4"].fill = PatternFill("solid", fgColor="FEF3C7")

cols_r = [
    "Setter", "Total leads", "Contactados", "Agendados", "Presentados",
    "Cerrados", "Perdidos",
    "Tasa contacto", "Tasa agendado", "Tasa presentación", "Tasa cierre",
    "€ facturado", "€ comisión",
]
set_header(ws, 6, cols_r)
fit_cols(ws, [14, 12, 13, 12, 13, 11, 11, 14, 14, 16, 13, 14, 14])

setters = ["Lucía", "Marta", "José"]
for i, s in enumerate(setters, start=7):
    ws.cell(row=i, column=1, value=s).font = Font(bold=True)
    # Total = COUNTIFS(setter, lote)
    ws.cell(row=i, column=2,
            value=f'=COUNTIFS(Leads!H:H,A{i},Leads!F:F,$B$4)')
    # Contactados = setter, lote, Estado<>frio
    ws.cell(row=i, column=3,
            value=f'=COUNTIFS(Leads!H:H,A{i},Leads!F:F,$B$4,Leads!J:J,"<>frio")')
    # Agendados = estados desde "cita agendada" en adelante
    ws.cell(row=i, column=4,
            value=(f'=COUNTIFS(Leads!H:H,A{i},Leads!F:F,$B$4,Leads!J:J,"cita agendada")'
                   f'+COUNTIFS(Leads!H:H,A{i},Leads!F:F,$B$4,Leads!J:J,"presentado")'
                   f'+COUNTIFS(Leads!H:H,A{i},Leads!F:F,$B$4,Leads!J:J,"cerrado")'))
    # Presentados = presentado + cerrado
    ws.cell(row=i, column=5,
            value=(f'=COUNTIFS(Leads!H:H,A{i},Leads!F:F,$B$4,Leads!J:J,"presentado")'
                   f'+COUNTIFS(Leads!H:H,A{i},Leads!F:F,$B$4,Leads!J:J,"cerrado")'))
    # Cerrados
    ws.cell(row=i, column=6,
            value=f'=COUNTIFS(Leads!H:H,A{i},Leads!F:F,$B$4,Leads!J:J,"cerrado")')
    # Perdidos
    ws.cell(row=i, column=7,
            value=f'=COUNTIFS(Leads!H:H,A{i},Leads!F:F,$B$4,Leads!J:J,"perdido")')
    # Tasa contacto = Contactados / Total
    ws.cell(row=i, column=8,  value=f'=IFERROR(C{i}/B{i},0)').number_format = PCT
    # Tasa agendado = Agendados / Contactados
    ws.cell(row=i, column=9,  value=f'=IFERROR(D{i}/C{i},0)').number_format = PCT
    # Tasa presentación = Presentados / Agendados
    ws.cell(row=i, column=10, value=f'=IFERROR(E{i}/D{i},0)').number_format = PCT
    # Tasa cierre = Cerrados / Presentados
    ws.cell(row=i, column=11, value=f'=IFERROR(F{i}/E{i},0)').number_format = PCT
    # € facturado
    ws.cell(row=i, column=12,
            value=f'=SUMIFS(Leads!T:T,Leads!H:H,A{i},Leads!F:F,$B$4)')
    ws.cell(row=i, column=12).number_format = EUR
    # € comisión setter
    ws.cell(row=i, column=13,
            value=f'=SUMIFS(Leads!V:V,Leads!H:H,A{i},Leads!F:F,$B$4)')
    ws.cell(row=i, column=13).number_format = EUR
    for col in range(1, 14):
        ws.cell(row=i, column=col).border = BORDER


# ---------------------------------------------------------------------------
# 7. Hoja COMISIONES (resumen mensual por persona)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Comisiones")
ws["A1"] = "Comisiones por persona (todos los lotes)"
ws["A1"].font = TITLE_FONT
ws["A2"] = "Suma todas las comisiones generadas en Leads, por persona."
ws["A2"].font = NOTE_FONT

cols_c = ["Persona", "Rol", "€ comisión setter", "€ comisión closer", "€ bonus mantenimiento", "€ TOTAL"]
set_header(ws, 4, cols_c)
fit_cols(ws, [14, 12, 20, 20, 22, 14])

personas = [
    ("Lucía", "setter"),
    ("Marta", "setter"),
    ("Diego", "closer"),
    ("Sara",  "closer"),
    ("José",  "closer"),
]
for i, (name, rol) in enumerate(personas, start=5):
    ws.cell(row=i, column=1, value=name).font = Font(bold=True)
    ws.cell(row=i, column=2, value=rol)
    # comisión setter (suma donde Setter = name)
    ws.cell(row=i, column=3,
            value=f'=SUMIF(Leads!H:H,A{i},Leads!V:V)').number_format = EUR
    # comisión closer (suma donde Closer derivado = name)
    ws.cell(row=i, column=4,
            value=f'=SUMIF(Leads!I:I,A{i},Leads!W:W)').number_format = EUR
    # bonus mantenimiento (solo closers, donde Closer derivado = name)
    ws.cell(row=i, column=5,
            value=f'=SUMIF(Leads!I:I,A{i},Leads!X:X)').number_format = EUR
    # total
    ws.cell(row=i, column=6, value=f'=C{i}+D{i}+E{i}').number_format = EUR
    for col in range(1, 7):
        ws.cell(row=i, column=col).border = BORDER


# ---------------------------------------------------------------------------
# 8. Hoja ROUND-ROBIN (helper para los 10k leads fríos)
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Round-Robin")
ws["A1"] = "Reparto round-robin de los 10.000 leads fríos"
ws["A1"].font = TITLE_FONT
ws["A3"] = (
    "Pega abajo (columna B) la lista de leads fríos. La columna 'Pareja' "
    "se rellena sola alternando Lucia-Diego / Marta-Sara / Jose. La columna "
    "'Lote' agrupa en cohortes de 500."
)
ws["A3"].alignment = LEFT
ws.row_dimensions[3].height = 50

set_header(ws, 5, ["#", "Nombre psicólogo", "Pareja", "Lote"])
fit_cols(ws, [6, 30, 14, 8])

for r in range(6, 6 + 200):  # 200 filas de muestra; el usuario amplía
    idx = r - 5
    ws.cell(row=r, column=1, value=idx)
    # Pareja: CHOOSE(MOD(idx-1,3)+1, "Lucia-Diego","Marta-Sara","Jose")
    ws.cell(row=r, column=3,
            value=f'=IF(B{r}="","",CHOOSE(MOD(A{r}-1,3)+1,"Lucia-Diego","Marta-Sara","Jose"))')
    # Lote = ceil(idx/500)
    ws.cell(row=r, column=4,
            value=f'=IF(B{r}="","",INT((A{r}-1)/500)+1)')
    for col in range(1, 5):
        ws.cell(row=r, column=col).border = BORDER


# ---------------------------------------------------------------------------
# Ordenar pestañas para que LÉEME quede primera
# ---------------------------------------------------------------------------
order = ["LÉEME", "Equipo", "Productos", "Parejas", "Leads", "Ranking",
         "Comisiones", "Round-Robin"]
wb._sheets = [wb[t] for t in order]

# Guardar
os.makedirs(os.path.dirname(OUT), exist_ok=True)
wb.save(OUT)
print("Generado:", OUT)

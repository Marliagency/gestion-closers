# Configurar Airtable — Sistema Comercial Marli

Esta guía termina de configurar la base `Sistema Comercial Marli` (`appyGM3EfHjhWrEAO`). Tu base ya trae las tres tablas (**Equipo**, **Productos**, **Leads**) con datos de ejemplo. Aquí montamos los enlaces que hacen que el closer se rellene solo, los campos calculados del ranking y las tres vistas operativas.

Tiempo estimado: 25-35 minutos a mano. Si prefieres ir más rápido, los pasos 1-5 y los enlaces de pareja están automatizados en `scripts/setup-airtable.py` (ver sección **Vía rápida** al final).

---

## Paso 1. Tabla `Equipo` — autoenlace `Closer asignado`

Esta es la jugada que define las parejas en un solo sitio.

1. Abre la tabla **Equipo**.
2. Botón `+` al final de las columnas → tipo de campo **`Link to another record`**.
3. Configura:
   - **Nombre del campo:** `Closer asignado`
   - **Tabla a enlazar:** `Equipo` (sí, a sí misma).
   - **Allow linking to multiple records:** OFF (solo un closer por setter).
4. Para cada **setter** (Lucía, Marta), abre su ficha y en `Closer asignado` enlaza al closer que le toque:
   - Lucía → Diego
   - Marta → Sara
5. Los closers dejan el campo vacío.

> Cuando crees el enlace, Airtable te ofrecerá generar automáticamente el campo recíproco en la misma tabla. Acéptalo y renómbralo a `Setters a mi cargo`: te servirá para ver, desde la fila de cada closer, qué setters le envían leads.

---

## Paso 2. Tabla `Leads` — enlace `Setter`

1. Abre la tabla **Leads**.
2. Crea un campo nuevo tipo **`Link to another record`**:
   - **Nombre:** `Setter`
   - **Tabla a enlazar:** `Equipo`
   - **Allow linking to multiple records:** OFF
3. Filtra los registros enlazables para que solo aparezcan setters: clic en el campo → `Customize field options` → `Limit record selection to a view` → crea en `Equipo` una vista filtrada `rol = setter` y selecciónala.
4. Para cada lead existente, enlázalo a su setter correspondiente.

Si quieres trazabilidad del closer original cuando José vende en solitario (donde no hay setter), añade también un campo opcional `Closer manual` (link a Equipo filtrado por `rol = closer`) y úsalo solo en esos casos.

---

## Paso 3. Tabla `Leads` — Lookup `Closer derivado`

Aquí está la magia: **el closer NO se escribe**, se trae automáticamente desde el setter.

1. En **Leads**, crea un campo nuevo tipo **`Lookup`**.
2. Configura:
   - **Nombre:** `Closer derivado`
   - **Linked record field:** `Setter`
   - **Field to look up:** `Closer asignado` (de la tabla Equipo)
3. Comprueba: en cualquier lead con setter asignado, debe aparecer su closer automáticamente. Si cambias la pareja en Equipo, todos los leads de ese setter se actualizan solos.

---

## Paso 4. Tabla `Leads` — Lookups de Producto y campos de comisión

Para que las comisiones se calculen solas, conviene que el lead tire del producto.

1. Crea (si no existe ya) un campo `Producto` en Leads tipo **`Link to another record`** → tabla `Productos`. Allow multiple: OFF.
2. Crea **Lookups** sobre Producto:
   - `Precio` ← `Precio` de Productos.
   - `Coste agencia` ← `Coste agencia` de Productos.
   - `Margen` ← `Margen` de Productos (o créalo como Formula `Precio - Coste agencia` directamente en Productos).
3. Crea un Lookup adicional sobre `Setter`:
   - `Comision_pct_setter` ← `comision_pct` de Equipo.
4. Crea otro Lookup sobre `Closer derivado`:
   - `Comision_pct_closer` ← `comision_pct` de Equipo.
5. Añade tres campos **Formula** en Leads:
   - `Comision setter` = `IF({Estado}='cerrado', {Margen} * {Comision_pct_setter}, 0)`
   - `Comision closer` = `IF({Estado}='cerrado', {Margen} * {Comision_pct_closer}, 0)`
   - `Bonus mantenimiento closer` = `IF(AND({Estado}='cerrado', {Mantenimiento}), 50, 0)`

> Con estos cuatro campos ya tienes el cálculo de comisiones en tiempo real, sin scripts.

---

## Paso 5. Tabla `Leads` — campos de gestión de los 10.000 leads fríos

Para trabajar con volumen y ranking:

| Campo | Tipo | Para qué |
|---|---|---|
| `Lote` | Number (integer) | Lote 1–20 al que pertenece el lead frío (lotes de ~500). |
| `Pareja asignada` | Single select (`Lucia-Diego`, `Marta-Sara`, `Jose`) | Pareja responsable, viene del reparto round-robin. |
| `Proximo seguimiento` | Date | Cuándo el setter tiene que volver a tocar el lead. |
| `Fecha ultimo cambio` | Last modified time | Auditoría, se calcula sola. |
| `Dias sin tocar` | Formula `DATETIME_DIFF(NOW(), {Fecha ultimo cambio}, 'days')` | Para detectar estancados. |
| `Ficha completa` | Formula `IF(AND({Dolor detectado}, {Num pacientes}, {Objecion anticipada}, {Fecha videollamada}), '✅', '❌')` | Validación visual. |

---

## Paso 6. Las tres vistas operativas en `Leads`

### Vista A — Pipeline (Kanban por estado)
- Tipo: **Kanban**.
- Stack by: `Estado` (frio → contactado → cita agendada → presentado → cerrado → perdido).
- Card fields visibles: `nombre_psicologo`, `Setter`, `Closer derivado`, `Fecha videollamada`, `Producto`, `Ficha completa`.
- Sort: `Fecha ultimo cambio` descendente.
- Uso: pipeline diario. Setters mueven hasta `cita agendada`; closers a partir de ahí.

### Vista B — Marcador semanal (Grid agrupada por Setter)
- Tipo: **Grid**.
- Group by: `Setter`.
- Sort dentro del grupo: `Estado` ascendente.
- Visibles: `nombre_psicologo`, `Estado`, `Closer derivado`, `Fecha videollamada`, `Producto`, `Euros cobrado`, `Mantenimiento`, `Comision setter`, `Comision closer`.
- En la cabecera de cada grupo, activa **Summary functions** (clic en la barra del grupo):
  - `Estado` → `Count` (total de leads del setter).
  - `Estado` → otro count con filtro condicional usando una fórmula auxiliar si quieres separar contactados/agendados.
  - `Euros cobrado` → `Sum`.
  - `Comision setter` → `Sum`.

### Vista C — Ficha de traspaso (Grid con todos los campos)
- Tipo: **Grid**.
- Visibles: todos los campos de la ficha en orden lógico (datos del psicólogo → estado → pareja → dolor/pacientes/objeción → fecha → producto/€/mantenimiento → comisiones).
- Sin agrupación.
- Activa `Row height = Tall` para leer cómodamente los textos largos.

### Vistas extra recomendadas

- **Mis leads (filtrada por setter)**: una vista por setter, con `FILTER WHERE Setter = <su nombre>`. Mejor: usa la función **personal views** de Airtable.
- **Hoy y mañana**: filtra por `Fecha videollamada` en las próximas 48 h. Útil para el closer.
- **Estancados**: `Dias sin tocar > 14 AND Estado NOT IN (cerrado, perdido)`.

---

## Paso 7. Ranking de setters

Crea una vista **Grid** en `Leads` agrupada por `Setter` con estos summary fields (configurables por lote):

| Métrica | Cómo se calcula en la summary del grupo |
|---|---|
| Total leads | Count de filas del grupo |
| Contactados | Count condicional `Estado != frio` (crea formula auxiliar `Es contactado`) |
| Agendados | Count `Estado IN (cita agendada, presentado, cerrado)` |
| Presentados | Count `Estado IN (presentado, cerrado)` |
| Cerrados | Count `Estado = cerrado` |
| **Tasa de contacto** | Formula auxiliar a nivel de grupo: `Contactados / Total leads` |
| **Tasa de agendado** | `Agendados / Contactados` |
| Tasa de presentación | `Presentados / Agendados` |
| Tasa de cierre | `Cerrados / Presentados` |
| € facturados | Sum de `Euros cobrado` |
| € comisión setter | Sum de `Comision setter` |

> Para que las **tasas en porcentaje** queden bien, lo más limpio es duplicar la base `Leads` en una tabla auxiliar `Resumen setters` con un registro por setter por lote, y formulizar ahí las ratios. Si prefieres rapidez, deja las tasas en la propia vista usando las summary functions y revísalas en el ritual semanal.

Filtra el ranking **por lote** con la barra de filtros (`Lote = 3`, por ejemplo) para comparar el rendimiento dentro de la misma cohorte de leads (es la única comparación justa: lotes distintos tienen calidad distinta).

---

## Paso 8. Asignación round-robin de los 10.000 leads fríos

Airtable no reparte solo: hay que decirle cómo. Dos caminos:

### 8.1 Manual rápido (sin scripts)
1. Importa el CSV de 10.000 leads (botón `+ Add or import` → `CSV file`).
2. Ordena por `id_lead` ascendente.
3. Selecciona las primeras 500 filas → edita `Pareja asignada = Lucia-Diego` y `Lote = 1`.
4. Siguientes 500 → `Marta-Sara`, `Lote = 1`. Y así.
5. Repite ciclo round-robin hasta agotar.

### 8.2 Automático con Airtable Scripting (recomendado)
- En la base, pestaña **Extensions** → añade **Scripting**.
- Pega un script tipo:
  ```
  let leads = await base.getTable('Leads').selectRecordsAsync();
  let parejas = ['Lucia-Diego', 'Marta-Sara', 'Jose'];
  let tamañoLote = 500;
  let updates = leads.records
    .filter(r => !r.getCellValue('Pareja asignada'))
    .map((r, i) => ({
      id: r.id,
      fields: {
        'Pareja asignada': { name: parejas[i % parejas.length] },
        'Lote': Math.floor(i / tamañoLote) + 1
      }
    }));
  while (updates.length) {
    await base.getTable('Leads').updateRecordsAsync(updates.splice(0, 50));
  }
  ```
- Pulsa **Run**. En segundos los 10k quedan repartidos.

---

## Paso 9. Permisos del equipo

1. Botón `Share` arriba a la derecha → invita a cada miembro con su email.
2. Permisos recomendados:
   - **Lucía, Marta, Diego, Sara, José:** Editor (pueden crear y editar pero no romper la estructura).
   - **Tú (admin):** Creator.
3. Comparte solo la base, no el workspace entero.

---

## Paso 10. Verificación final

Antes de soltar al equipo, comprueba:

- [ ] Al asignar `Setter = Lucía` a un lead nuevo, `Closer derivado` muestra `Diego` sin tocar nada.
- [ ] Al cambiar el setter en la tabla Equipo (ej. Marta pasa a tener a Diego), todos los leads de Marta actualizan su closer derivado.
- [ ] El Kanban muestra las seis columnas en orden.
- [ ] El ranking agrupado por Setter calcula totales y € facturados.
- [ ] Las fórmulas de comisión devuelven el importe correcto al marcar un lead como `cerrado`.
- [ ] Los 10k leads fríos están repartidos en lotes y parejas tras correr el script.

Si los seis puntos pasan, el sistema está listo. Pasa al archivo `AUTOMATIZACIONES.md`.

---

## Vía rápida: `scripts/setup-airtable.py`

Si prefieres no hacer los pasos 1-5 a mano, el script automatiza la creación de campos, lookups, fórmulas y el enlace setter→closer. Ejecútalo desde **tu máquina** (no desde el entorno de Claude Code, que tiene bloqueada la salida a `api.airtable.com`).

### Prerrequisitos
- Python 3.8 o superior. Sin dependencias externas.
- Un Personal Access Token con scopes `data.records:read/write` y `schema.bases:read/write`, con acceso solo a la base `appyGM3EfHjhWrEAO`.

### Pasos

```bash
git clone <repo> && cd gestion-closers
export AIRTABLE_TOKEN=patXXXXXXXXXXXXXX

# 1. Inspecciona el schema actual (sin tocar nada)
python3 scripts/setup-airtable.py inspect

# 2. Crea todos los campos (idempotente: si existen los respeta)
python3 scripts/setup-airtable.py configure

# 3. Enlaza Lucía → Diego y Marta → Sara
python3 scripts/setup-airtable.py link-pairs

# (o todo de golpe)
python3 scripts/setup-airtable.py all
```

Flags útiles:
- `--dry-run` para ver qué haría sin escribir nada.
- `--verbose` para ver los payloads y respuestas de la API.
- `--base-id <id>` si quieres apuntar a una base distinta.

### Qué hace y qué no

| Paso | Automatizado por el script | A mano en UI |
|---|---|---|
| 1. `Closer asignado` en Equipo | ✅ | — |
| 2. `Setter` en Leads | ✅ | — |
| 3. `Closer derivado` (lookup) | ✅ | — |
| 4. Lookups Producto + fórmulas de comisión | ✅ | — |
| 5. Campos `Lote`, `Pareja asignada`, `Proximo seguimiento`, `Fecha ultimo cambio`, `Dias sin tocar`, `Ficha completa` | ✅ | — |
| Enlazar Lucía→Diego y Marta→Sara | ✅ (`link-pairs`) | — |
| 6. Vistas Kanban / Marcador / Ficha | ❌ (la API no crea vistas) | ✅ |
| 7. Summary functions del ranking | ❌ | ✅ |
| 8. Reparto round-robin de los 10k | ❌ (mejor en Airtable Scripting) | ✅ |
| 9. Permisos del equipo | ❌ | ✅ |

Tiempo real con el script: ~2 min de ejecución + 10 min para crear vistas y compartir.


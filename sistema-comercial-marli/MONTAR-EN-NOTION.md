# Cómo montar el sistema en Notion

Esta guía te lleva de cero a tener las dos bases enlazadas, con el closer derivado automáticamente y las tres vistas listas para el equipo. Tiempo estimado: 30-40 minutos.

---

## Paso 1. Crear la tabla `Equipo`

1. En Notion, crea una página nueva y dentro añade una base de datos de tipo **Tabla**. Llámala `Equipo`.
2. Importa el archivo `equipo-importar.csv`:
   - Botón `···` arriba a la derecha → `Merge with CSV` → selecciona el archivo.
   - Si tu Notion no muestra "Merge with CSV", arrástralo directamente sobre la tabla.
3. Ajusta los tipos de cada propiedad (Notion los detecta como texto por defecto):

| Propiedad | Tipo recomendado |
|---|---|
| `id` | Title |
| `nombre` | Text |
| `rol` | Select (opciones: `setter`, `closer`) |
| `closer_asignado_id` | **Relation** → apuntando a la propia tabla `Equipo` (auto-relación) |
| `email` | Email |
| `comision_pct` | Number (formato porcentaje) |
| `activo` | Checkbox o Select (`si`/`no`) |

> **Truco:** al convertir `closer_asignado_id` en relación, Notion te pedirá vincular fila a fila. Para cada setter, abre su ficha y vincula manualmente al closer que le toque (Lucia → Diego, Marta → Sara).

---

## Paso 2. Crear la tabla `Leads`

1. En la misma página o en una nueva, crea otra base de datos de tipo **Tabla**. Llámala `Leads`.
2. Importa `leads-importar.csv` con el mismo método.
3. Ajusta los tipos:

| Propiedad | Tipo recomendado |
|---|---|
| `id_lead` | Title |
| `nombre_psicologo` | Text |
| `contacto` | Text (o Email/Phone si todos son del mismo tipo) |
| `estado` | Select (`frio`, `contactado`, `cita agendada`, `presentado`, `cerrado`, `perdido`) |
| `setter_id` | **Relation** → apuntando a la tabla `Equipo` |
| `closer_id_derivado` | **Rollup** (ver Paso 3) |
| `dolor_detectado` | Text |
| `num_pacientes` | Number |
| `objecion_anticipada` | Text |
| `fecha_videollamada` | Date (con hora) |
| `producto` | Select (`Automatizacion Informes`, `Chatbot IA`, `Pack Premium`) |
| `euros_cobrado` | Number (formato euros) |
| `mantenimiento` | Checkbox o Select |
| `fecha_ultimo_cambio` | Last edited time (Notion la rellena sola) |

---

## Paso 3. Enlazar Leads → Equipo y derivar el closer

Esta es la clave del sistema: **el closer no se escribe, se calcula desde el setter**.

### 3.1 Relacionar `setter_id` con `Equipo`
- En la tabla `Leads`, abre la propiedad `setter_id` y conviértela en tipo **Relation** apuntando a `Equipo`.
- Vincula cada lead a la fila correspondiente del setter en `Equipo`.

### 3.2 Crear el rollup `closer_id_derivado`
- En `Leads`, crea (o convierte) la propiedad `closer_id_derivado` a tipo **Rollup**.
- Configura el rollup así:
  - **Relation:** `setter_id`
  - **Property:** `closer_asignado_id` (de la tabla Equipo)
  - **Calculate:** `Show original` (o `Show unique values` si lo prefieres limpio)
- Resultado: cuando asignes un setter al lead, Notion mostrará automáticamente el closer asignado a ese setter. Si cambias la pareja en `Equipo`, todos los leads de ese setter se actualizan solos.

> **Nota sobre los CSV:** en `leads-importar.csv` la columna `closer_id_derivado` viene precargada por claridad, pero **es informativa**: en Notion ese campo lo calcula el rollup. No tienes que editarlo.

---

## Paso 4. Crear las tres vistas sobre `Leads`

### Vista A — Kanban por estado (Pipeline)
- Tipo: **Board**.
- Agrupar por: `estado`.
- Orden de columnas: `frio` → `contactado` → `cita agendada` → `presentado` → `cerrado` → `perdido`.
- Tarjeta visible: `nombre_psicologo`, `setter_id`, `closer_id_derivado`, `fecha_videollamada`, `producto`.
- Uso: pipeline diario. Los setters mueven hasta `cita agendada`; los closers mueven a partir de ahí.

### Vista B — Tabla agrupada por persona (Marcador semanal)
- Tipo: **Table**.
- Agrupar por: `setter_id` (o crea dos vistas, una por setter y otra por closer).
- Añade propiedades de tipo **Count** y **Rollup con filtro** en la cabecera de cada grupo:
  - Total leads del grupo: `Count all`.
  - Contactados esta semana: filtro `estado = contactado` + `fecha_ultimo_cambio` esta semana → `Count`.
  - Citas agendadas: filtro `estado = cita agendada` → `Count`.
  - Videollamadas presentadas: filtro `estado = presentado` o posterior → `Count`.
  - Cierres: filtro `estado = cerrado` → `Count`.
  - € facturados: `Sum` de `euros_cobrado` con filtro `estado = cerrado`.
- Uso: marcador del ritual semanal de 15 min.

### Vista C — Ficha de cada tarjeta (Traspaso)
- No es una vista aparte, es la plantilla de **página del lead** que se abre al hacer click en una tarjeta.
- En `Leads`, abre cualquier registro → `···` arriba → `Customize page` → ordena las propiedades en este orden para hacer el traspaso fácil:
  1. `nombre_psicologo`, `contacto`
  2. `estado`
  3. `setter_id`, `closer_id_derivado` (este último aparece solo, no se edita)
  4. `dolor_detectado`, `num_pacientes`, `objecion_anticipada`
  5. `fecha_videollamada`
  6. `producto`, `euros_cobrado`, `mantenimiento`
  7. `fecha_ultimo_cambio`
- Guarda esta disposición como plantilla por defecto: botón `New` → flecha → `+ New template` → `Set as default`.

---

## Paso 5. Verificación rápida

Antes de invitar al equipo, comprueba:

- [ ] Al crear un lead nuevo y asignarle `setter_id = Lucia`, aparece `closer_id_derivado = Diego` sin tocar nada.
- [ ] El Kanban muestra las seis columnas en orden.
- [ ] El marcador agrupado por persona calcula los `Count` solos.
- [ ] La ficha del lead muestra todas las propiedades en orden lógico.

Si los cuatro puntos pasan, el sistema está listo. Comparte la página con permisos de edición al equipo y pasa al archivo `AUTOMATIZACIONES.md`.

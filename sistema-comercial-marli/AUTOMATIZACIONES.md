# Plan de Automatizaciones — Airtable

Roadmap de automatizaciones para el sistema, ordenado por **impacto / esfuerzo**. No hace falta hacerlo todo a la vez: empieza por el Nivel 1 y crece desde ahí.

Para cada automatización indico qué herramienta la implementa mejor:

- **Airtable Automations (nativo):** disparadores y acciones dentro de la propia base. Incluido en todos los planes (con límites según plan).
- **Airtable Scripting:** scripts JavaScript dentro de Airtable, ideales para lógica de datos masiva sobre la misma base.
- **Make / Zapier:** orquestación visual cuando hay que enlazar Airtable con WhatsApp, Slack, Google Calendar, email, etc.
- **API de Airtable:** solo cuando lo anterior no llega (integraciones complejas, jobs externos, dashboards en otra herramienta).

---

## Nivel 1 — Imprescindibles (semana 1)

### 1.1 Notificar al closer cuando se le asigna una cita
- **Disparador:** un lead cambia `Estado` a `cita agendada`.
- **Acción:** mensaje al closer (Slack, Telegram, WhatsApp o email) con nombre del psicólogo, fecha/hora y enlace a la ficha.
- **Implementación:**
  - **Airtable Automations + email:** trigger `When record matches conditions` (Estado = cita agendada) → action `Send email` al campo `Closer derivado > email` (vía Lookup adicional).
  - **Make (recomendado para Slack/WhatsApp):** `Watch Records` filtrado por Estado → módulo Slack/WhatsApp/Email.

### 1.2 Validación visual de ficha completa
- **Disparador:** cualquier edición.
- **Acción:** campo `Ficha completa` muestra ✅ o ❌ y, opcionalmente, bloquea el avance a `presentado` si está incompleta.
- **Implementación:** ya queda hecho con la **Formula** descrita en `CONFIGURAR-AIRTABLE.md` Paso 5. Para bloquear el avance, añade una automation `When Estado changes to presentado AND Ficha completa = ❌` → acción `Update record` que revierta el estado y mande aviso al setter.

### 1.3 Sello automático `Fecha ultimo cambio`
- **Implementación:** campo nativo **Last modified time**. Sin configurar nada.

---

## Nivel 2 — Productividad (semana 2-3)

### 2.1 Recordatorio al lead 24h y 1h antes de la videollamada
- **Disparador:** la fecha actual está a 24 h (o 1 h) de `Fecha videollamada` y `Estado = cita agendada`.
- **Acción:** enviar email o WhatsApp al lead con el enlace de la videollamada.
- **Implementación:**
  - **Airtable Automations:** trigger `At a scheduled time` (cada hora) → script que consulta los leads que cumplen condición → action `Send email`.
  - **Make / Zapier:** scheduler diario que filtra `Fecha videollamada = mañana` y `Fecha videollamada > now + 23h` → envío.

### 2.2 Mover el lead a `perdido` si lleva X días sin cambio
- **Disparador:** `Dias sin tocar > 14` y `Estado NOT IN (cerrado, perdido)`.
- **Acción:** cambiar `Estado` a `perdido`, dejar comentario automático y notificar al setter para validar.
- **Implementación:** Airtable Automation programada (diaria, 02:00) → script que actualiza los registros que cumplen el filtro.

### 2.3 Crear evento de Google Calendar al agendar cita
- **Disparador:** `Estado` pasa a `cita agendada`.
- **Acción:** crear evento en el calendario del closer con el lead como invitado y enlace de Meet.
- **Implementación:** Airtable Automation con acción nativa de Google Calendar (planes pagos) o Make/Zapier (Airtable → Google Calendar).

### 2.4 Aviso al setter cuando su closer cierra una venta
- **Disparador:** `Estado` pasa a `cerrado` y el lead tiene `Setter` (no es venta solitaria de José).
- **Acción:** notificación al setter con el € cobrado y su comisión calculada.
- **Implementación:** Airtable Automation → Slack/Email.

---

## Nivel 3 — Dinero y ranking (cuando el volumen lo justifique)

### 3.1 Cálculo de comisiones automatizado
- Las fórmulas `Comision setter`, `Comision closer` y `Bonus mantenimiento closer` ya calculan en tiempo real (ver Paso 4 de `CONFIGURAR-AIRTABLE.md`).
- **Mejora:** tabla `Comisiones` con un registro por persona y mes, alimentada por una Automation que al pasar un lead a `cerrado` crea las filas correspondientes. Útil para liquidaciones mensuales.

### 3.2 Reporte semanal automático al equipo
- **Disparador:** todos los lunes a las 09:00.
- **Acción:** resumen por persona (tasa de contacto, tasa de agendado, agendados, cerrados, € facturados) y envío por Slack/email.
- **Implementación:**
  - **Airtable Automation programada** + Scripting que agrega datos y compone el mensaje.
  - O **Make** con módulos `Search records` → `Aggregate` → `Send email`.

### 3.3 Detección de leads estancados
- **Disparador:** lead lleva más de N días en el mismo estado (3 días en `contactado`, 7 en `cita agendada`).
- **Acción:** marcar campo `Estancado = true` y avisar al dueño.
- **Implementación:** Formula `Dias sin tocar` + Automation con trigger por condición.

### 3.4 Ranking público del equipo
- Vista `Ranking setters` (descrita en `CONFIGURAR-AIRTABLE.md` Paso 7) compartida con todo el equipo en modo lectura.
- Snapshot semanal vía Airtable Automation que copia los números a una tabla histórica `Ranking historico` para ver evolución por semana y por lote.

---

## Nivel 4 — Crecimiento (futuro)

### 4.1 Captura automática de leads desde formulario / Tally / web
- Webhook entrante → crea fila en `Leads` con `Estado = frio` y asigna automáticamente a la pareja con menos carga (siguiente del round-robin).
- **Implementación:** Make o Zapier + API de Airtable.

### 4.2 Reparto round-robin de nuevos lotes
- Script de Airtable que detecta leads sin `Pareja asignada` y los reparte respetando el orden round-robin desde el último asignado.
- **Implementación:** Airtable Scripting (ver Paso 8.2 de `CONFIGURAR-AIRTABLE.md`).

### 4.3 Dashboard ejecutivo (Looker Studio / Metabase)
- Conexión vía API de Airtable o exportación periódica a Google Sheets para alimentar un dashboard externo con KPIs históricos.

### 4.4 Enriquecimiento automático de leads
- Cuando entra un lead frío con email/web, llamar a Clearbit / Apollo / similar para traer nombre, ciudad, especialidad.
- **Implementación:** Make + API enriquecimiento + API Airtable.

---

## Resumen visual

| Nivel | Automatización | Herramienta |
|---|---|---|
| 1 | Notificar cita al closer | Airtable Automations + email / Make |
| 1 | Validación ficha completa | Airtable Formula + Automation |
| 1 | Fecha último cambio | Nativo (Last modified) |
| 2 | Recordatorios 24h / 1h al lead | Make / Zapier o Airtable scheduled |
| 2 | Auto-perdido a los 14 días | Airtable Automation + Scripting |
| 2 | Evento Google Calendar | Airtable Automation o Make |
| 2 | Aviso al setter al cerrar | Airtable Automation |
| 3 | Cálculo comisiones | Airtable Formula + tabla `Comisiones` |
| 3 | Reporte semanal | Airtable Scripting o Make |
| 3 | Detectar estancados | Formula + Automation |
| 3 | Ranking + snapshot histórico | Airtable Automation |
| 4 | Captura desde formulario | Make + API |
| 4 | Round-robin de nuevos lotes | Airtable Scripting |
| 4 | Dashboard externo | API + Looker/Sheets |
| 4 | Enriquecimiento | Make + API externa |

---

## Recomendación de arranque

Si tuvieras que elegir solo **tres** para empezar, serían **1.1**, **1.2** y **1.3**. Con eso el equipo ya nota el sistema "vivo" sin pagar plan adicional de Make. Después, en cuanto haya 30+ leads/semana en pipeline activo, ataca el Nivel 2 empezando por **2.1** (recordatorios) y **2.4** (aviso al setter al cerrar). El Nivel 3 entra cuando tengas dos meses de histórico y quieras pulir comisiones y ranking.

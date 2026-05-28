# Plan de Automatizaciones

Roadmap de automatizaciones para el sistema, ordenado por **impacto / esfuerzo**. No hace falta hacerlo todo de golpe: empieza por las tres primeras y crece desde ahí.

Para cada automatización indico **qué herramienta** la implementa mejor:

- **Notion nativo:** botones, automatizaciones de base de datos (disponibles en planes Plus y superiores).
- **Make / Zapier:** orquestación visual, ideal para enlazar Notion con WhatsApp, email, Google Calendar, etc.
- **API de Notion:** solo cuando necesitas lógica que las anteriores no cubren (cálculos complejos, reportes).

---

## Nivel 1 — Imprescindibles (semana 1)

### 1.1 Notificar al closer cuando se le asigna una cita
- **Disparador:** un lead cambia a estado `cita agendada`.
- **Acción:** mensaje al closer (Slack, Telegram, WhatsApp o email) con nombre del psicólogo, fecha/hora y link a la tarjeta.
- **Implementación:**
  - **Notion nativo:** automatización de base de datos → `When estado is set to 'cita agendada'` → `Notify` al usuario referenciado en `closer_id_derivado`. Limitación: requiere que el closer sea un usuario de Notion (no funciona bien con rollups), así que el camino más limpio es Make.
  - **Make (recomendado):** módulo Watch Database Items → filtro `estado = cita agendada` → módulo Slack/WhatsApp/Email.

### 1.2 Validación de ficha completa antes de avanzar
- **Disparador:** un lead intenta pasar a `cita agendada`.
- **Acción:** si falta `dolor_detectado`, `num_pacientes`, `objecion_anticipada` o `fecha_videollamada`, marcar la tarjeta con etiqueta `ficha incompleta` y notificar al setter.
- **Implementación:** Notion nativo con una propiedad fórmula tipo `if(empty(dolor) or empty(num_pacientes)...)` que devuelve "❌ Ficha incompleta" o "✅ OK". El setter ve el aviso en la tarjeta.

### 1.3 Marcar fecha de último cambio
- **Disparador:** cualquier edición.
- **Acción:** actualizar `fecha_ultimo_cambio`.
- **Implementación:** Notion nativo. La propiedad `Last edited time` lo hace solo, sin configurar nada.

---

## Nivel 2 — Productividad (semana 2-3)

### 2.1 Recordatorio al lead 24h y 1h antes de la videollamada
- **Disparador:** la fecha actual está a 24h (o 1h) de `fecha_videollamada` y `estado = cita agendada`.
- **Acción:** enviar email o WhatsApp al lead.
- **Implementación:** Make o Zapier con un módulo Scheduler diario que lee Notion, filtra y dispara el envío. Notion nativo no lo cubre porque no permite cron con desfase exacto.

### 2.2 Mover el lead a `perdido` si lleva X días sin cambio
- **Disparador:** `fecha_ultimo_cambio` hace más de 14 días y `estado` no es `cerrado` ni `perdido`.
- **Acción:** cambiar `estado` a `perdido` y avisar al setter para validar.
- **Implementación:** Make con scheduler diario. También se puede hacer con API de Notion + un script pequeño en cualquier servidor.

### 2.3 Crear el evento de Google Calendar al agendar cita
- **Disparador:** lead pasa a `cita agendada`.
- **Acción:** crear evento en el calendario del closer con el lead como invitado.
- **Implementación:** Make o Zapier (Notion → Google Calendar).

---

## Nivel 3 — Dinero (cuando el volumen lo justifique)

### 3.1 Calcular comisiones automáticamente
- **Disparador:** lead pasa a `cerrado`.
- **Acción:** calcular comisión de setter, closer y José (si aplica) sobre el margen y registrarlo en una tercera tabla `Comisiones`.
- **Implementación:**
  - **Notion nativo (parcial):** propiedades fórmula en `Leads` que calculen `comision_setter = margen * 0.05`, `comision_closer = margen * 0.15`, `bonus_mantenimiento = if(mantenimiento, 50, 0)`. Necesitas una propiedad `coste_agencia` para tener el margen.
  - **Make + API (completo):** al cerrar el lead, crear automáticamente filas en `Comisiones` por cada persona implicada con el importe.

### 3.2 Reporte semanal automático al equipo
- **Disparador:** todos los lunes a las 09:00.
- **Acción:** generar un resumen (contactados, agendados, presentados, cierres, € facturados) por persona y enviarlo por email/Slack.
- **Implementación:** Make con módulo Notion → Aggregate → Email/Slack. Alternativamente, una página de Notion con vistas filtradas y `embed` del marcador.

### 3.3 Detectar leads "estancados" en cada estado
- **Disparador:** lead lleva más de N días en el mismo estado (N depende del estado: 3 días en `contactado`, 7 en `cita agendada`, etc.).
- **Acción:** etiquetar como `🔥 estancado` y avisar al dueño.
- **Implementación:** Make + propiedad fórmula `days_in_state = dateBetween(now(), fecha_ultimo_cambio, "days")`.

---

## Nivel 4 — Crecimiento (futuro)

### 4.1 Captura automática de leads desde formulario / Tally / web
- Webhook entrante → crea fila en `Leads` con `estado = frio` y asigna automáticamente a la pareja con menos carga.
- **Implementación:** Make + API de Notion.

### 4.2 Asignación equilibrada de la lista fría
- Al cargar un lote de leads fríos, repartirlos por igual entre las parejas activas.
- **Implementación:** script Python o Node usando la API de Notion (round-robin sobre setters activos).

### 4.3 Dashboard de KPIs (conversión por etapa, LTV, etc.)
- **Implementación:** API de Notion → Google Sheets / Looker Studio / Metabase.

---

## Resumen visual

| Nivel | Automatización | Herramienta |
|---|---|---|
| 1 | Notificar cita al closer | Make |
| 1 | Validación ficha completa | Notion nativo (fórmula) |
| 1 | Fecha último cambio | Notion nativo (Last edited time) |
| 2 | Recordatorios 24h / 1h al lead | Make / Zapier |
| 2 | Auto-perdido a los 14 días | Make + API |
| 2 | Evento Google Calendar | Make / Zapier |
| 3 | Cálculo de comisiones | Notion fórmulas + Make |
| 3 | Reporte semanal | Make |
| 3 | Detectar estancados | Make + fórmula |
| 4 | Captura desde formulario | Make + API |
| 4 | Reparto equilibrado | Script + API |
| 4 | Dashboard KPIs | API + Looker/Sheets |

---

## Recomendación de arranque

Si tuvieras que elegir solo **tres** para empezar, serían 1.1, 1.2 y 1.3. Con eso el equipo ya nota el sistema "vivo" sin pagar plan de pago de Make. Después, en cuanto haya 30+ leads/semana, ataca el Nivel 2.

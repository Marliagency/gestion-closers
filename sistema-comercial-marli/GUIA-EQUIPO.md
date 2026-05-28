# Guía del Equipo Comercial Marli

Bienvenido/a. Esta guía explica cómo trabajamos en Marli como equipo remoto y asíncrono. Léela entera antes de empezar a mover leads. Es corta, pero contiene todo lo que necesitas para no pisar a tus compañeros y para cobrar bien tus comisiones.

El tablero vive en **Airtable**, base *Sistema Comercial Marli* (id `appyGM3EfHjhWrEAO`), con tres tablas: **Equipo**, **Productos** y **Leads**.

---

## 1. Roles y métricas

### Setter
- **Misión:** llenar la agenda del closer con citas de calidad.
- **Métricas semanales (ranking):**
  - **Tasa de contacto** = `contactados / total leads asignados`.
  - **Tasa de agendado** = `agendados / contactados`.
  - Tasa de presentación = `presentados / agendados` (calidad de la cita).
  - € facturados por su pareja (resultado real).
- **Comisión:** 5% sobre el margen. Solo si la cita se presenta y la ficha está completa.

### Closer
- **Misión:** cerrar la venta en la videollamada de 25 minutos.
- **Métricas semanales:**
  - Videollamadas presentadas.
  - Tasa de cierre = `cerrados / presentados`.
  - € facturados.
- **Comisión:** 15% sobre el margen. Además, **50 € únicos** por cada mantenimiento contratado.

### José (caso especial)
- Como closer sobre citas que le pase un setter → **10% sobre margen**.
- Vendiendo en solitario (gestiona todo el ciclo) → **20% sobre margen**.

---

## 2. Productos, margen y comisiones

La tabla **Productos** ya contiene esta información; aquí va de referencia rápida:

| Producto | Precio | Coste agencia IA | Margen |
|---|---|---|---|
| Automatización Informes | 449 € | 200 € | **249 €** |
| Chatbot IA | 999 € | 500 € | **499 €** |
| Pack Premium | 1.349 € | 700 € | **649 €** |
| Mantenimiento | 300 €/mes | — | 50 € únicos al closer |

Las comisiones se calculan **siempre sobre el margen**, nunca sobre el precio bruto.

### Ejemplo de reparto en una venta del Pack Premium (margen 649 €)
- Setter (5%): **32,45 €**
- Closer (15%): **97,35 €**
- Si el cliente contrata mantenimiento, +**50 €** únicos al closer.

### Ejemplo de venta en solitario por José (margen 249 € de Informes)
- José (20%): **49,80 €**

---

## 3. Flujo del lead, paso a paso

```
Lead frío  →  Contactado  →  Cita agendada  →  [TRASPASO]  →  Presentado  →  Cerrado / Perdido
   (setter)     (setter)        (setter)                       (closer)        (closer)
```

1. **Lead frío:** entra en la lista por lotes. Aún nadie lo ha tocado.
2. **Contactado:** el setter ha hablado con el psicólogo (mensaje, llamada, lo que sea). Anota `dolor_detectado`, `num_pacientes` y `objecion_anticipada`.
3. **Cita agendada:** el lead acepta la videollamada de 25 min. Se fija `fecha_videollamada`.
4. **Traspaso al closer:** sucede automáticamente porque cada setter tiene un closer fijo asignado en la tabla **Equipo**. El setter **no elige closer**: ya viene por la pareja, vía Lookup.
5. **Presentado:** la videollamada se ha realizado de verdad (el lead apareció).
6. **Cerrado:** firma y cobra. Se rellenan `producto`, `euros_cobrado` y `mantenimiento`.
7. **Perdido:** no compra. Cierra el lead con honestidad: aprenderemos más de los perdidos que de los cerrados.

---

## 4. Cómo el setter traspasa al closer

**El closer ya está asignado por la pareja.** No hay que buscarlo, no hay que pensar.

Cuando agendes una cita:

1. **Rellena la ficha completa** del lead: dolor, nº pacientes, objeción, fecha/hora.
2. **Cambia el estado** a `cita agendada`.
3. Airtable mostrará automáticamente el closer asignado (campo Lookup `Closer derivado` que sale de tu pareja en la tabla Equipo).
4. Tu compañero closer recibirá la notificación (manual al principio, automática cuando montemos los disparadores).

> **Importante:** sin ficha completa, la cita **no cuenta como válida** y no genera comisión de setter, aunque el lead se presente.

---

## 5. Reglas de oro del equipo

1. **Un dueño por lead.** Si está en tu lote o tu columna, es tuyo.
2. **No tocar leads ajenos.** Si ves algo raro en el lead de otro, deja un comentario en la ficha; no edites.
3. **Reparto de la lista fría por lotes.** El sistema reparte los 10.000 leads fríos en lotes mediante round-robin entre las parejas activas. Si terminas tu lote, avisa antes de pedir otro.
4. **Ritual semanal de 15 min** (lunes, 09:30). Cada uno cuenta:
   - Mis números de la semana pasada (tasa de contacto y de agendado).
   - Mi objetivo para esta semana.
   - Un bloqueo o una pregunta.
5. **Una cita solo cuenta si se presenta** y si la ficha estaba completa antes de la llamada. Las fantasma se registran para mejorar la tasa de presentación, pero no generan comisión.
6. **Honestidad por encima de todo.** Mejor un "perdido" claro que un "fantasma" en cita agendada eternamente.

---

## 6. Qué cuenta como cita válida

Una cita es válida cuando se cumplen **las tres** condiciones:

- [x] El lead se presenta a la videollamada (no fantasma).
- [x] La ficha está completa antes de la llamada: dolor, nº pacientes, objeción, fecha/hora.
- [x] El estado avanza a `presentado` o más allá.

Sin estas tres, no se genera comisión de setter.

---

## 7. Recordatorio final

Trabajamos remoto y en equipo. La base de Airtable es nuestra oficina. **Si no está en Airtable, no existe.** Mantén tus leads vivos, mueve el estado y rellena las fichas: así cobramos todos.

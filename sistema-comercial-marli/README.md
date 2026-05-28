# Sistema Comercial Marli

Sistema de gestión para el equipo comercial remoto de Marli (setters + closers), pensado para montarse en Notion con dos bases enlazadas y crecer con automatizaciones cuando haga falta.

---

## Archivos en este paquete

| # | Archivo | Para qué sirve |
|---|---|---|
| 1 | `equipo-importar.csv` | Tabla **Equipo** lista para importar a Notion (2 setters, 2 closers emparejados y José). |
| 2 | `leads-importar.csv` | Tabla **Leads** lista para importar (6 ejemplos cubriendo todos los estados del flujo). |
| 3 | `GUIA-EQUIPO.md` | Manual del equipo: roles, métricas, flujo del lead, reglas de oro. |
| 4 | `MONTAR-EN-NOTION.md` | Paso a paso para crear las dos bases, enlazarlas y dejar el closer derivado automáticamente. |
| 5 | `AUTOMATIZACIONES.md` | Roadmap priorizado de automatizaciones (Notion nativo, Make/Zapier, API). |
| 6 | `README.md` | Este índice. |

---

## Orden recomendado de uso

1. **Lee `GUIA-EQUIPO.md`** para entender cómo trabajamos y los conceptos clave (parejas setter-closer, qué cuenta como cita válida, comisiones).
2. **Sigue `MONTAR-EN-NOTION.md`** para crear las dos bases en Notion e importar los CSV. Tiempo: 30-40 min.
3. **Verifica** que al asignar un setter a un lead, el closer se rellena solo (rollup).
4. **Comparte la página de Notion** con el equipo y pásales `GUIA-EQUIPO.md`.
5. **Cuando el sistema esté en marcha**, abre `AUTOMATIZACIONES.md` e implementa el Nivel 1.

---

## Principio de diseño

Los datos viven en **dos tablas enlazadas**, no en una sola:

- `Equipo` → una fila por persona, define las parejas setter-closer en un único sitio.
- `Leads` → una fila por psicólogo, el closer **no se escribe**, se deriva del setter mediante una propiedad rollup.

Así, cambiar una pareja se hace en un solo lugar y todos los leads se actualizan solos. Y cualquier automatización futura (Make, Zapier, API) se enchufa sin tocar la estructura.

# Sistema Comercial Marli

Documentación de apoyo para la base de Airtable `Sistema Comercial Marli` (`appyGM3EfHjhWrEAO`), que organiza al equipo comercial remoto de Marli (setters + closers en parejas fijas, más José).

La base ya existe y trae tres tablas con datos de ejemplo:

- **Equipo** — una fila por persona del equipo.
- **Productos** — catálogo con precios, costes y márgenes.
- **Leads** — una fila por psicólogo, con estado en el pipeline.

Esta carpeta contiene los manuales y planes que rodean a esa base.

---

## Archivos

| # | Archivo | Para qué sirve |
|---|---|---|
| 1 | `GUIA-EQUIPO.md` | Manual del equipo: roles, métricas, productos y márgenes, flujo del lead, reglas de oro. Lo lee cada setter y closer antes de empezar. |
| 2 | `CONFIGURAR-AIRTABLE.md` | Pasos para terminar la base: enlace Setter (Leads→Equipo), autoenlace Closer asignado (Equipo→Equipo), Lookup Closer derivado, fórmulas de comisión, las tres vistas, ranking, reparto round-robin de los 10.000 leads fríos y permisos. |
| 3 | `AUTOMATIZACIONES.md` | Roadmap priorizado de automatizaciones (Airtable nativo, Scripting, Make/Zapier, API). |
| 4 | `README.md` | Este índice. |

---

## Orden recomendado de uso

1. **Lee `GUIA-EQUIPO.md`** para entender los roles, las parejas setter-closer, los márgenes y cómo se calculan las comisiones.
2. **Sigue `CONFIGURAR-AIRTABLE.md`** paso a paso sobre la base existente. Tiempo: 25-35 min. Al terminar, el `Closer derivado` de cada lead se rellena solo y las comisiones se calculan en tiempo real.
3. **Verifica** los 6 puntos del Paso 10 antes de soltar al equipo.
4. **Importa los 10k leads fríos** con el script round-robin del Paso 8.2.
5. **Comparte la base** con el equipo (Paso 9) y pásales `GUIA-EQUIPO.md`.
6. Cuando el sistema esté en marcha, abre `AUTOMATIZACIONES.md` e implementa el Nivel 1.

---

## Principio de diseño

Los datos viven en **tres tablas enlazadas**:

- `Equipo` → una fila por persona. El autoenlace `Closer asignado` define las parejas setter-closer en un único sitio.
- `Productos` → catálogo. Cada lead enlaza al producto y trae precio, coste y margen vía Lookup.
- `Leads` → una fila por psicólogo. El `Closer derivado` **no se escribe**, se trae desde el setter mediante Lookup. Las comisiones se calculan con fórmulas sobre el margen del producto.

Así, cambiar una pareja o el precio de un producto se hace en un solo lugar y todos los leads se actualizan solos. Y cualquier automatización futura (Airtable Automations, Make, Zapier, API) se enchufa sin tocar la estructura.

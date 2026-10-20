# ADR 0001 — Arquitectura: API interna + sitio público

Fecha: 2026-10-20 · Estado: aceptada

## Contexto

El primer Motor era un HTML autocontenido con datos incrustados. Queremos algo mantenible:
poder cargar una encuesta nueva sin reescribir el sitio, mostrar la procedencia de cada cifra
y tener una base para el widget móvil. No hay fecha límite ni infraestructura definida.

## Decisiones

1. **Backend real, pequeño y de solo lectura.** FastAPI + PostgreSQL/PostGIS.
   *Por qué:* series de tiempo (otra ENFR), versionado de datos, linaje por cifra y búsqueda
   geoespacial para el widget justifican una base. Python porque el pipeline y el análisis ya
   lo son. *Descartado:* todo-TypeScript (reescribiría el ETL) y 100% estático (actualizar =
   editar CSV a mano).
2. **Escritura solo por CLI.** Sin endpoints de escritura ni panel de admin.
   *Por qué:* elimina la superficie de ataque y la necesidad de usuarios/roles.
3. **La API es interna; el sitio es público.** API keys con alcances (`read`, `read:draft`),
   hasheadas (SHA-256: son aleatorias de 192 bits, no contraseñas elegidas por personas).
   El sitio consume la API de servidor a servidor; el navegador no la ve.
   *Por qué:* la barrera principal es de red (la API no se expone), la clave es defensa en
   profundidad. *Descartado:* OAuth/JWT/usuarios — sobreingeniería para 2–5 personas.
4. **Modelo de hechos `observation`** (jurisdicción × indicador × período) ligado a una
   `dataset_version` con estado `draft | published | archived`.
   *Por qué:* un año o indicador nuevo son filas, no migraciones. Un índice único parcial
   garantiza una sola versión publicada por dataset.
5. **Se guarda la confiabilidad que declara la fuente** (`cv`, `reliability`), no una propia.
   *Por qué:* ver `docs/DATOS.md` §1.
6. **Linaje en la base** (`dataset_indicator.source_ref`): el «Fuente» del sitio sale de
   acá, no de texto escrito a mano en los componentes.
7. **Una sola imagen Docker** para API y ETL; la migración corre al arrancar la API.
   Apto para Dokploy: el compose base no publica puertos.

## Consecuencias

- Más piezas que un sitio estático: base, API, ETL y web deben funcionar juntas.
  Mitigación: el sitio se pre-renderiza, así que si la API cae, las páginas siguen sirviéndose.
- `/v1/locate` resuelve sobre geometría simplificada (~440 m): cerca de un límite provincial
  puede errar. La capa viene del IGN (ver `data/geo/README.md`).
- Falta decidir cómo llega `../data` (insumos del ETL) al servidor de producción.

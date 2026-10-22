# MAPA — Atlas de diabetes en Argentina

Sitio público e interactivo sobre diabetes y determinantes sociales en las 24 jurisdicciones,
con una API interna que es la fuente de verdad de los datos.

> Estado: **backend y sitio funcionando** (datos + API + geometría del IGN + web con historia, mapa, mosaico,
> fichas, comparador y metodología).

## Arquitectura

```
 ETL (CLI, Python) ──► PostgreSQL + PostGIS ◄── API (FastAPI, solo lectura) ──► web (SvelteKit)
 valida y versiona      fuente de verdad          interna, con API key           pública
```

- **El ETL es la única vía de escritura.** La API no tiene endpoints de escritura: no hay
  panel de admin ni autenticación de usuarios que mantener ni que vulnerar.
- **La API es interna.** Toda ruta exige `X-API-Key` (salvo `/health`). El sitio público la
  consume de servidor a servidor; el navegador de la gente nunca le habla.
- **Los datos nuevos entran como borrador** y recién se ven en el sitio al publicarlos.
  Publicar archiva la versión anterior; volver atrás es republicar la archivada.
- Decisiones y motivos: [`docs/adr/0001-arquitectura.md`](docs/adr/0001-arquitectura.md) (backend) y
  [`docs/adr/0002-frontend.md`](docs/adr/0002-frontend.md) (sitio). Sitio: [`web/README.md`](web/README.md).
- **Hallazgos sobre los datos** (leer antes de escribir copy del sitio): [`docs/DATOS.md`](docs/DATOS.md).

## Levantar todo en local

Requiere Docker. Desde esta carpeta:

```bash
cp .env.example .env            # y cambiar POSTGRES_PASSWORD
docker compose up -d db api
docker compose run --rm etl bootstrap          # migra, siembra, carga y publica (solo dev)
docker compose run --rm etl keys create --name web --scope read     # → pegar en MAPA_WEB_API_KEY (.env)
docker compose up -d web
```

- Sitio: `http://127.0.0.1:3000` · API: `http://127.0.0.1:8000` (Swagger en `/docs`, solo en `dev`).
- Para una clave personal de la API: `docker compose run --rm etl keys create --name "mi-nombre" --scope read`.

```bash
curl -H "X-API-Key: <tu clave>" "http://127.0.0.1:8000/v1/observations?indicator=diabetes_treatment"
```

## Endpoints (`/v1`)

| Ruta | Alcance | Qué devuelve |
|---|---|---|
| `GET /indicators` | read | Indicadores con su **linaje** (fuente, cuadro, universo, notas) |
| `GET /jurisdictions` | read | Provincias y total del país |
| `GET /observations` | read | Cifras publicadas: valor, **CV** y **marca de confiabilidad de INDEC** |
| `GET /geo/provinces` | read | GeoJSON de provincias (con ETag) |
| `GET /locate?lat&lng` | read | Provincia que contiene un punto (para el widget) |
| `GET /versions` | read:draft | Versiones de datos, incluidos borradores |
| `GET /observations?version_id=` | read:draft | Revisar un borrador antes de publicarlo |

`GET /health` y `GET /ready` son abiertos.

## Operar los datos (CLI `mapa`)

```bash
docker compose run --rm etl etl load --all          # carga todo como borrador (idempotente)
docker compose run --rm etl etl versions            # ver estados
docker compose run --rm etl etl verify              # cruza el .xls oficial vs. el CSV del equipo
docker compose run --rm etl etl publish <id>        # publicar (archiva la anterior)
docker compose run --rm etl keys create --name X --scope read --scope read:draft
docker compose run --rm etl keys revoke <prefijo>
```

Las cifras salen de `../data` (montada de solo lectura; no se duplica) y la capa de provincias de
`data/geo/` (ver [`data/geo/README.md`](data/geo/README.md)). Para regenerarla: `mapa geo build --input <ign.json>`;
para controlarla: `mapa geo check`.

## Desarrollo y tests

```bash
cd api
uv sync
uv run pytest            # unitarios + integración (los de integración levantan PostGIS con Docker)
uv run ruff check .
```

- Migraciones: `uv run alembic revision --autogenerate -m "..."`. Un test falla si un modelo
  cambia sin su migración.
- `tests/test_geo_quality.py` controla lo que el ojo no ve en un mapa: capitales dentro de su
  provincia, sin solapes, tamaño de CABA, peso del archivo.

## Despliegue (Dokploy)

Usar [`docker-compose.prod.yml`](docker-compose.prod.yml), no el override local. El archivo
no publica puertos y empaqueta en la imagen interna sólo los insumos públicos agregados
que necesita el ETL; así no depende de un montaje al checkout temporal de Dokploy.
Asignar dominio **solo al servicio `web`**. `api` y `db` quedan en la red interna.
Las variables requeridas son `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` y
`MAPA_WEB_API_KEY`; se guardan en Dokploy, nunca en Git. La API registra de forma
idempotente la clave de lectura configurada, sin imprimirla. En producción se usa
`MAPA_ENVIRONMENT=prod`, que apaga `/docs` y el comando `bootstrap`.

La carga inicial se hace luego de crear el volumen nuevo: `mapa db seed`,
`mapa etl load --all`, revisión de versiones y publicación de cada borrador. El sitio
solo recibe dominio después de comprobar la carga. Antes de actualizar una base
existente, hacer un respaldo PostgreSQL. Las versiones de datos archivadas pueden
republicarse para revertir una carga; el código se revierte al commit anterior.

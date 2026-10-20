# MAPA — Atlas de diabetes en Argentina

Sitio público e interactivo sobre diabetes y determinantes sociales en las 24 jurisdicciones,
con una API interna que es la fuente de verdad de los datos.

> Estado: **backend (datos + API + geometría oficial del IGN) listo y probado**. El sitio (`web/`) es el próximo paso.

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
- Decisiones y motivos: [`docs/adr/0001-arquitectura.md`](docs/adr/0001-arquitectura.md).
- **Hallazgos sobre los datos** (leer antes de escribir copy del sitio): [`docs/DATOS.md`](docs/DATOS.md).

## Levantar todo en local

Requiere Docker. Desde esta carpeta:

```bash
cp .env.example .env            # y cambiar POSTGRES_PASSWORD
docker compose up -d db api
docker compose run --rm etl bootstrap          # migra, siembra, carga y publica (solo dev)
docker compose run --rm etl keys create --name "mi-nombre" --scope read
```

La API queda en `http://127.0.0.1:8000` (Swagger en `/docs`, solo en `dev`).

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

`docker-compose.yml` es apto para producción: no publica puertos. Para publicar el sitio se
asigna dominio **solo al servicio `web`**; `api` y `db` quedan en la red interna. En producción
poner `MAPA_ENVIRONMENT=prod` (apaga `/docs` y el comando `bootstrap`). Pendiente: servicio
`web`, y definir cómo llega `../data` (insumos del ETL) al servidor.

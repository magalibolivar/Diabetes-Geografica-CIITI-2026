# Capa de provincias

`argentina_provincias.geojson` — 24 jurisdicciones, WGS84, ~540 KB, **generada** con
`mapa geo build`. No editar a mano.

- **Fuente:** Instituto Geográfico Nacional (IGN), capa `ign:provincia`, servicio WFS.
- **Términos:** el servicio autoriza copiar, reprocesar, reutilizar y redistribuir libremente
  según el art. 2 de la Ley 27.275 (texto en sus `AccessConstraints`). Citar al IGN como fuente.
- **Descargada:** 2026-10-20 · **SHA-256 del original:** ver `metadata.input_sha256` en el archivo.
- **Procesamiento:** simplificación topológica (`coverage_simplify`, tolerancia 0,004° ≈ 440 m)
  y coordenadas a 4 decimales. Simplificar bordes compartidos una sola vez evita solapes y
  huecos entre provincias vecinas.
- **Controles** (`mapa geo check`, `tests/test_geo_quality.py`): las 24 capitales caen en su
  provincia, no hay solapes, la geometría es válida, CABA tiene el tamaño de CABA, el archivo pesa menos
  de 700 KB y Tierra del Fuego conserva Malvinas, islas australes y sector antártico.

## Tierra del Fuego, Antártida e Islas del Atlántico Sur

La feature oficial reúne territorios muy distintos y **se conserva completa** (decisión del equipo:
mostrar todo, también lo que no tiene datos). Cada parte se simplifica según cómo se dibuja:

| Parte | Cómo se dibuja en el sitio | Tolerancia |
|---|---|---|
| Isla Grande, de los Estados e islas menores | con las demás provincias, con los datos de la provincia | 0,004° (≈440 m) |
| Islas Malvinas | en su lugar, al este de Santa Cruz, **sin datos** | 0,01° (≈1 km) |
| Antártida Argentina, Georgias, Sandwich y Orcadas del Sur | en un recuadro polar, **sin datos** | 0,05° (≈5 km) |

Se descartan islotes diminutos de las dos últimas. A 5 km de tolerancia, un punto de la costa antártica
puede quedar fuera de la geometría (`/v1/locate`); no afecta a ningún caso de uso real.

Los territorios sin datos llevan a la ficha de Tierra del Fuego al tocarlos, porque administrativamente
son parte de esa provincia. Los datos de la encuesta describen solo sus localidades urbanas de la Isla Grande.

## Validez de la geometría

Simplificar partes por separado puede dejarlas superpuestas, y redondear coordenadas una por una puede
volver a romper polígonos válidos. Por eso el build repara con `make_valid` y ajusta a la grilla con
`set_precision` (que conserva la validez). Un test mira el archivo tal cual se publica.

## Regenerar

```bash
curl -o ign_provincia.json "https://wms.ign.gob.ar/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ign:provincia&outputFormat=application/json&srsName=EPSG:4326"   # ~110 MB
cd mapa/api && uv run mapa geo build --input ../../ign_provincia.json
```

El archivo descargado no se versiona.

## Por qué no se reutilizó el GeoJSON anterior (`geo/argentina_provincias.geojson`)

Venía de geoBoundaries (23 unidades, base 2006) con CABA agregada a mano: un polígono de 24
vértices que no contenía a CABA, y Buenos Aires superpuesta con Santa Fe y Entre Ríos. Ese
archivo sigue en `geo/` y en `Propuesta_Mapa_Interactivo_/Datos/` porque lo usan el paper y el
Motor anterior; **no lo toqué**.

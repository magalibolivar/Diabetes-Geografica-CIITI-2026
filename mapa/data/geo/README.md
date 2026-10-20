# Capa de provincias

`argentina_provincias.geojson` — 24 jurisdicciones, WGS84, ~480 KB, **generada** con
`mapa geo build`. No editar a mano.

- **Fuente:** Instituto Geográfico Nacional (IGN), capa `ign:provincia`, servicio WFS.
- **Términos:** el servicio autoriza copiar, reprocesar, reutilizar y redistribuir libremente
  según el art. 2 de la Ley 27.275 (texto en sus `AccessConstraints`). Citar al IGN como fuente.
- **Descargada:** 2026-10-20 · **SHA-256 del original:** ver `metadata.input_sha256` en el archivo.
- **Procesamiento:** simplificación topológica (`coverage_simplify`, tolerancia 0,004° ≈ 440 m)
  y coordenadas a 4 decimales. Simplificar bordes compartidos una sola vez evita solapes y
  huecos entre provincias vecinas.
- **Controles** (`mapa geo check`, `tests/test_geo_quality.py`): las 24 capitales caen en su
  provincia, no hay solapes, CABA tiene el tamaño de CABA, el archivo pesa menos de 700 KB.

## Decisión de cartografía: Tierra del Fuego

La feature oficial de Tierra del Fuego incluye el **sector antártico y las islas del Atlántico
Sur** (hasta 90°S), lo que arruina cualquier proyección web. Esta capa conserva solo el sector
insular austral (Isla Grande, Isla de los Estados e islas menores) y lo declara en
`metadata.modifications`.

Es una decisión de presentación, no una afirmación sobre el territorio. En Argentina, la Ley
26.651 exige el mapa bicontinental oficial en ámbitos educativos y organismos públicos: si el
sitio va a publicarse bajo la universidad conviene que el equipo decida cómo representar la
Antártida y las islas (p. ej. un recuadro). Los datos originales siguen disponibles: basta
re-ejecutar el build.

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

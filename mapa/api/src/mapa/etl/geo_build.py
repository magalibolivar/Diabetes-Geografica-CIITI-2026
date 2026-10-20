"""Construye la capa de provincias para la web a partir de la capa oficial del IGN.

Entrada : WFS del IGN, capa `ign:provincia` (24 jurisdicciones, resolución completa, ~110 MB).
Salida  : GeoJSON liviano (WGS84) con una feature por provincia, listo para el mapa.

El archivo de entrada NO se versiona (es enorme); sí queda registrado su SHA-256 en la
salida, de modo que cualquiera pueda volver a generarla con `mapa geo build`.
"""

import hashlib
import json
from datetime import date
from pathlib import Path

import shapely
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.geometry.base import BaseGeometry

from mapa import catalog
from mapa.etl.geo import as_multipolygon

IGN_WFS_URL = (
    "https://wms.ign.gob.ar/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature"
    "&typeName=ign:provincia&outputFormat=application/json&srsName=EPSG:4326"
)
IGN_TDF_NAME = "Tierra del Fuego, Antártida e Islas del Atlántico Sur"

# ~440 m. A 0,008° CABA ya se deforma; a 0,002° el archivo casi se duplica sin ganancia visible.
DEFAULT_TOLERANCE = 0.004
COORD_DECIMALS = 4  # ~11 m

# La feature oficial de «Tierra del Fuego, Antártida e Islas del Atlántico Sur» reúne territorios muy
# distintos. Se conservan TODOS (es la representación oficial) pero se simplifican según cómo se dibujan:
#   - sector insular austral (Isla Grande, de los Estados…): junto al resto del país, tolerancia común;
#   - Islas Malvinas: se dibujan a escala del mapa nacional, tolerancia fina;
#   - Antártida e islas australes (Georgias, Sandwich, Orcadas…): van en un recuadro chico, tolerancia gruesa.
TDF_MAIN_MAX_LON = -62.0
TDF_MAIN_MIN_LAT = -56.5
MALVINAS_BOX = (-62.0, -57.0, -53.5, -50.5)  # lon_min, lon_max, lat_min, lat_max
MALVINAS_TOLERANCE = 0.01
MALVINAS_MIN_AREA = 0.0005  # grados²: se descartan islotes menores (~5 km²)
REMOTE_TOLERANCE = 0.05
REMOTE_MIN_AREA = 0.003  # grados²

MODIFICATIONS = [
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur: se conserva todo el territorio oficial. "
    "Las partes que se dibujan chicas se simplifican más (Malvinas 0,01°; Antártida e islas australes 0,05°) "
    "y se descartan islotes menores.",
]


class GeoBuildError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_ign(path: Path) -> dict[str, BaseGeometry]:
    """GeoJSON del IGN -> {slug: geometría}. Exige exactamente las 24 provincias."""
    with path.open(encoding="utf-8") as fh:
        collection = json.load(fh)

    by_name = {j.name: j.slug for j in catalog.PROVINCES}
    by_name[IGN_TDF_NAME] = "tierra-del-fuego"

    shapes: dict[str, BaseGeometry] = {}
    for feature in collection["features"]:
        name = feature["properties"]["nam"]
        slug = by_name.get(name)
        if slug is None:
            raise GeoBuildError(f"Nombre de provincia desconocido en la capa del IGN: {name!r}")
        if slug in shapes:
            raise GeoBuildError(f"Provincia duplicada en la capa del IGN: {name!r}")
        shapes[slug] = shape(feature["geometry"])

    missing = {j.slug for j in catalog.PROVINCES} - set(shapes)
    if missing:
        raise GeoBuildError(f"Faltan provincias en la capa del IGN: {sorted(missing)}")
    return shapes


def classify_tdf_part(polygon: BaseGeometry) -> str:
    """'main' (sector insular austral), 'malvinas' o 'remote' (Antártida e islas australes)."""
    point = polygon.representative_point()
    x, y = point.x, point.y
    if x < TDF_MAIN_MAX_LON and y > TDF_MAIN_MIN_LAT:
        return "main"
    lon0, lon1, lat0, lat1 = MALVINAS_BOX
    if lon0 <= x <= lon1 and lat0 <= y <= lat1:
        return "malvinas"
    return "remote"


def split_tierra_del_fuego(geom: BaseGeometry) -> tuple[MultiPolygon, list[Polygon]]:
    """(sector principal, resto ya simplificado). El principal entra al coverage con las demás provincias."""
    main: list[Polygon] = []
    rest: list[Polygon] = []
    for part in geom.geoms:
        kind = classify_tdf_part(part)
        if kind == "main":
            main.append(part)
            continue
        if kind == "malvinas":
            tol, min_area = MALVINAS_TOLERANCE, MALVINAS_MIN_AREA
        else:
            tol, min_area = REMOTE_TOLERANCE, REMOTE_MIN_AREA
        if part.area < min_area:
            continue
        simple = part.simplify(tol, preserve_topology=True)
        if not simple.is_empty and simple.geom_type == "Polygon":
            rest.append(simple)
    if not main:
        raise GeoBuildError("Tierra del Fuego quedó sin su sector principal")
    return MultiPolygon(main), rest


def simplify(shapes: dict[str, BaseGeometry], tolerance: float) -> dict[str, MultiPolygon]:
    """Simplificación *topológica*: los bordes compartidos se simplifican una sola vez, así
    que las provincias vecinas no se solapan ni dejan huecos entre sí."""
    slugs = sorted(shapes)
    simplified = shapely.coverage_simplify([shapes[s] for s in slugs], tolerance=tolerance)
    return {slug: geom for slug, geom in zip(slugs, simplified, strict=True)}


def _round_coords(obj, decimals: int):
    if isinstance(obj, float):
        return round(obj, decimals)
    if isinstance(obj, list | tuple):
        return [_round_coords(o, decimals) for o in obj]
    return obj


def to_feature_collection(
    shapes: dict[str, MultiPolygon], *, input_sha256: str, tolerance: float, retrieved: date
) -> dict:
    features = []
    for j in catalog.PROVINCES:
        # set_precision ajusta a la grilla CONSERVANDO la validez; redondear número por número no.
        snapped = as_multipolygon(shapely.set_precision(shapes[j.slug], 10**-COORD_DECIMALS))
        geometry = shapely.geometry.mapping(snapped)
        features.append(
            {
                "type": "Feature",
                "id": j.slug,
                "properties": {"slug": j.slug, "iso_code": j.iso, "name": j.name},
                "geometry": {
                    "type": geometry["type"],
                    "coordinates": _round_coords(geometry["coordinates"], COORD_DECIMALS),
                },
            }
        )
    return {
        "type": "FeatureCollection",
        "metadata": {  # «foreign member» permitido por RFC 7946
            "source": "Instituto Geográfico Nacional (IGN) — capa ign:provincia, servicio WFS",
            "source_url": IGN_WFS_URL,
            "terms": (
                "El servicio WFS del IGN autoriza copiar, reprocesar, reutilizar y redistribuir "
                "libremente la información según el art. 2 de la Ley 27.275."
            ),
            "retrieved": retrieved.isoformat(),
            "input_sha256": input_sha256,
            "simplification": {
                "method": "GEOS coverage_simplify (topológica)",
                "tolerance_deg": tolerance,
                "coordinate_decimals": COORD_DECIMALS,
            },
            "modifications": MODIFICATIONS,
        },
        "features": features,
    }


def build(input_path: Path, *, tolerance: float = DEFAULT_TOLERANCE, retrieved: date | None = None):
    """Devuelve (FeatureCollection, {slug: geometría simplificada}) para controlar su calidad."""
    shapes = load_ign(input_path)
    shapes["tierra-del-fuego"], tdf_rest = split_tierra_del_fuego(shapes["tierra-del-fuego"])
    simplified = simplify(shapes, tolerance)
    simplified["tierra-del-fuego"] = MultiPolygon([*simplified["tierra-del-fuego"].geoms, *tdf_rest])
    # Simplificar partes por separado puede dejarlas superpuestas: se entrega siempre geometría válida.
    simplified = {slug: as_multipolygon(geom) for slug, geom in simplified.items()}
    collection = to_feature_collection(
        simplified,
        input_sha256=sha256_file(input_path),
        tolerance=tolerance,
        retrieved=retrieved or date.today(),
    )
    return collection, simplified


def vertex_count(shapes: dict[str, BaseGeometry]) -> int:
    return int(sum(shapely.get_num_coordinates(g) for g in shapes.values()))

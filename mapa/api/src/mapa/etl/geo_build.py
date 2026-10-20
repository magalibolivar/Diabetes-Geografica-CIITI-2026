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
from shapely.geometry import MultiPolygon, shape
from shapely.geometry.base import BaseGeometry

from mapa import catalog

IGN_WFS_URL = (
    "https://wms.ign.gob.ar/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature"
    "&typeName=ign:provincia&outputFormat=application/json&srsName=EPSG:4326"
)
IGN_TDF_NAME = "Tierra del Fuego, Antártida e Islas del Atlántico Sur"

# ~440 m. A 0,008° CABA ya se deforma; a 0,002° el archivo casi se duplica sin ganancia visible.
DEFAULT_TOLERANCE = 0.004
COORD_DECIMALS = 4  # ~11 m

# La feature oficial de Tierra del Fuego incluye el sector antártico (hasta 90°S) y las islas
# del Atlántico Sur, que rompen cualquier proyección web. Para el mapa se conserva el sector
# insular austral (Isla Grande, Isla de los Estados e islas menores).
TDF_MAX_LON = -62.0
TDF_MIN_LAT = -56.5

MODIFICATIONS = [
    "Tierra del Fuego: sólo se conservan los polígonos al oeste de 62°O y al norte de 56,5°S "
    "(Isla Grande, Isla de los Estados e islas menores). La feature oficial también incluye el "
    "sector antártico y las islas del Atlántico Sur, que no se dibujan en esta capa.",
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


def restrict_tierra_del_fuego(geom: BaseGeometry) -> MultiPolygon:
    kept = [
        p
        for p in geom.geoms
        if p.representative_point().x < TDF_MAX_LON and p.representative_point().y > TDF_MIN_LAT
    ]
    if not kept:
        raise GeoBuildError("Tierra del Fuego quedó vacía tras el recorte")
    return MultiPolygon(kept)


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
        geometry = shapely.geometry.mapping(shapes[j.slug])
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
    shapes["tierra-del-fuego"] = restrict_tierra_del_fuego(shapes["tierra-del-fuego"])
    simplified = simplify(shapes, tolerance)
    collection = to_feature_collection(
        simplified,
        input_sha256=sha256_file(input_path),
        tolerance=tolerance,
        retrieved=retrieved or date.today(),
    )
    return collection, simplified


def vertex_count(shapes: dict[str, BaseGeometry]) -> int:
    return int(sum(shapely.get_num_coordinates(g) for g in shapes.values()))

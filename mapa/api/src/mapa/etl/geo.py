import json
from pathlib import Path

from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.validation import make_valid

from mapa import catalog


class GeoError(ValueError):
    pass


def as_multipolygon(geom) -> MultiPolygon:
    if not geom.is_valid:
        geom = make_valid(geom)
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    if isinstance(geom, MultiPolygon):
        return geom
    polygons = [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]
    if not polygons:
        raise GeoError(f"Geometría no poligonal: {geom.geom_type}")
    return MultiPolygon(polygons)


def read_provinces(path: Path) -> dict[str, MultiPolygon]:
    """GeoJSON de provincias (generado por `mapa geo build`) -> {slug: MultiPolygon}.

    Falla si no calzan exactamente las 24 provincias del catálogo."""
    with path.open(encoding="utf-8") as fh:
        collection = json.load(fh)

    valid = {j.slug for j in catalog.PROVINCES}
    result: dict[str, MultiPolygon] = {}
    for feature in collection["features"]:
        slug = feature["properties"].get("slug")
        if slug not in valid:
            raise GeoError(f"Provincia desconocida en el GeoJSON: {slug!r}")
        if slug in result:
            raise GeoError(f"Provincia duplicada en el GeoJSON: {slug!r}")
        result[slug] = as_multipolygon(shape(feature["geometry"]))

    missing = valid - set(result)
    if missing:
        raise GeoError(f"Faltan provincias en el GeoJSON: {sorted(missing)}")
    return result

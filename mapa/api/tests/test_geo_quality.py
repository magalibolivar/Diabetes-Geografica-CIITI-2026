"""Calidad de la capa de provincias (IGN, generada con `mapa geo build`).

Un mapa puede \"verse bien\" a escala país y aun así ser incorrecto: estas pruebas miran lo que
el ojo no ve (capitales en su provincia, solapes, tamaño de CABA, peso del archivo)."""

import json

import pytest

from mapa import catalog
from mapa.config import get_settings
from mapa.etl import geo, geo_build, geoqa

GEO_FILE = get_settings().geo_file

pytestmark = pytest.mark.skipif(not GEO_FILE.exists(), reason="falta mapa/data/geo (mapa geo build)")

# CABA ocupa ~200 km²: a 34,6°S un grado² son ~10.170 km².
CABA_AREA_DEG2 = (0.017, 0.023)
MAX_FILE_KB = 700


@pytest.fixture(scope="module")
def shapes():
    return geo.read_provinces(GEO_FILE)


def test_cada_capital_cae_en_su_provincia(shapes):
    assert geoqa.capitals_outside(shapes) == []


def test_las_provincias_no_se_solapan(shapes):
    assert geoqa.overlaps(shapes) == []


def test_caba_tiene_el_tamano_de_caba(shapes):
    low, high = CABA_AREA_DEG2
    assert low < shapes["caba"].area < high


def test_buenos_aires_no_invade_a_sus_vecinas(shapes):
    """El GeoJSON anterior llegaba hasta -30°S y se pisaba con Santa Fe y Entre Ríos."""
    assert shapes["buenos-aires"].bounds[3] < -33.0


def test_tierra_del_fuego_conserva_todo_su_territorio_oficial(shapes):
    """La feature oficial incluye Malvinas, islas australes y el sector antártico."""
    tdf = shapes["tierra-del-fuego"]
    kinds = {geo_build.classify_tdf_part(p) for p in tdf.geoms}
    assert kinds == {"main", "malvinas", "remote"}
    assert tdf.bounds[1] < -80  # el sector antártico llega cerca del polo
    assert tdf.bounds[2] > -30  # y las Sandwich del Sur, casi a 26°O


def test_las_malvinas_estan_al_este_de_santa_cruz(shapes):
    malvinas = [p for p in shapes["tierra-del-fuego"].geoms if geo_build.classify_tdf_part(p) == "malvinas"]
    assert len(malvinas) >= 2  # Soledad y Gran Malvina, como mínimo
    assert max(p.area for p in malvinas) > 0.5


def test_el_archivo_es_liviano():
    assert GEO_FILE.stat().st_size / 1024 < MAX_FILE_KB


def test_declara_su_fuente_y_sus_modificaciones():
    meta = json.loads(GEO_FILE.read_text(encoding="utf-8"))["metadata"]
    assert "IGN" in meta["source"] and "Ley 27.275" in meta["terms"]
    assert len(meta["input_sha256"]) == 64
    assert any("Antártida" in m for m in meta["modifications"])


def test_la_geometria_publicada_es_valida():
    """Se mira el archivo tal cual, no tras `make_valid` al leerlo."""
    from shapely.geometry import shape

    for feature in json.loads(GEO_FILE.read_text(encoding="utf-8"))["features"]:
        assert shape(feature["geometry"]).is_valid, feature["id"]


def test_hay_una_feature_por_provincia(shapes):
    assert set(shapes) == {j.slug for j in catalog.PROVINCES}

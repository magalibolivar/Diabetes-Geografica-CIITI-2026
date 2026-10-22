"""Los parsers se prueban contra los archivos oficiales reales del repositorio."""

from decimal import Decimal

import pytest

from mapa import catalog
from mapa.config import get_settings
from mapa.etl import context, enfr, geo, nbi, verify

SOURCE_DIR = get_settings().source_dir
GEO_FILE = get_settings().geo_file

pytestmark = pytest.mark.skipif(
    not (SOURCE_DIR / enfr.FILENAME).exists(), reason="faltan los datos fuente del repo"
)


@pytest.fixture(scope="module")
def enfr_obs():
    return enfr.parse_enfr(SOURCE_DIR)


def _find(obs, jurisdiction, indicator):
    return next(o for o in obs if o.jurisdiction == jurisdiction and o.indicator == indicator)


def test_enfr_trae_9_indicadores_por_24_provincias_mas_el_total(enfr_obs):
    assert len(enfr_obs) == 9 * 25
    assert len({o.indicator for o in enfr_obs}) == 9


def test_enfr_total_del_pais(enfr_obs):
    total = _find(enfr_obs, "argentina", "diabetes_prevalence")
    assert (total.value, total.cv) == (Decimal("12.7"), Decimal("2.6"))


def test_enfr_conserva_el_cv_de_cada_cuadro(enfr_obs):
    assert all(o.cv is not None for o in enfr_obs)
    assert _find(enfr_obs, "caba", "diabetes_prevalence").cv == Decimal("10.2")
    assert _find(enfr_obs, "caba", "diabetes_treatment").cv == Decimal("9.4")
    assert _find(enfr_obs, "buenos-aires", "smoking").value == Decimal("23.1")  # hoja con \xa0


def test_enfr_conserva_las_marcas_de_confiabilidad_de_indec(enfr_obs):
    # Cuadro 7.5: los extremos del rango de tratamiento están marcados como «no confiables».
    for slug in ("la-pampa", "santa-cruz", "tierra-del-fuego"):
        assert _find(enfr_obs, slug, "diabetes_treatment").reliability == "unreliable"
    assert _find(enfr_obs, "chubut", "diabetes_treatment").reliability == "caution"
    assert _find(enfr_obs, "buenos-aires", "diabetes_treatment").reliability == "ok"


def test_el_xls_oficial_coincide_con_el_csv_validado():
    assert verify.cross_check_enfr(SOURCE_DIR) == []


@pytest.mark.parametrize("dataset", sorted({ds for ds, _ in catalog.CONTEXT_COLUMNS.values()}))
def test_contexto_trae_24_provincias(dataset):
    obs = context.parse_context(SOURCE_DIR, dataset)
    assert len(obs) == 24
    assert all(o.reliability is None for o in obs)  # la fuente no la evalúa


def test_densidad_de_tierra_del_fuego_ajustada():
    obs = context.parse_context(SOURCE_DIR, "indec-densidad-2022")
    assert _find(obs, "tierra-del-fuego", "population_density").value == Decimal("8.60")


def test_nbi_2022_conserva_2010_y_trae_24_provincias_mas_total():
    latest = nbi.parse_nbi_2022(SOURCE_DIR)
    historical = context.parse_context(SOURCE_DIR, "indec-nbi-2010")
    assert len(latest) == 25
    assert {o.jurisdiction for o in latest} == {j.slug for j in catalog.JURISDICTIONS}
    assert all(o.period == "2022" and o.cv is None for o in latest)
    assert _find(latest, "argentina", "nbi_households").value == Decimal("6.7")
    assert _find(latest, "chaco", "nbi_households").value == Decimal("11.2")
    assert all(o.period == "2010" for o in historical)


def test_geojson_calza_con_las_24_provincias():
    shapes = geo.read_provinces(GEO_FILE)
    assert set(shapes) == {j.slug for j in catalog.PROVINCES}
    assert all(s.geom_type == "MultiPolygon" and s.is_valid for s in shapes.values())

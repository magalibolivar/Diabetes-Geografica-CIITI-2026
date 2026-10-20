from mapa import catalog


def test_24_provincias_y_el_total_del_pais():
    assert len(catalog.PROVINCES) == 24
    assert sum(j.kind == "country" for j in catalog.JURISDICTIONS) == 1


def test_identificadores_unicos():
    for attr in ("slug", "iso", "name", "short"):
        values = [getattr(j, attr) for j in catalog.JURISDICTIONS]
        assert len(values) == len(set(values)), attr


def test_codigos_iso_de_argentina():
    codes = {j.iso for j in catalog.PROVINCES}
    assert all(c.startswith("AR-") and len(c) == 4 for c in codes)
    assert "AR-C" in codes  # CABA


def test_cada_indicador_tiene_linaje():
    linked = {link.indicator_slug for link in catalog.DATASET_INDICATORS}
    assert linked == {i.slug for i in catalog.INDICATORS}


def test_referencias_del_catalogo_son_consistentes():
    sources = {s.slug for s in catalog.SOURCES}
    assert all(d.source_slug in sources for d in catalog.DATASETS)
    datasets = set(catalog.DATASET_BY_SLUG)
    assert all(link.dataset_slug in datasets for link in catalog.DATASET_INDICATORS)
    for dataset, indicator in catalog.CONTEXT_COLUMNS.values():
        assert dataset in datasets and indicator in catalog.INDICATOR_BY_SLUG
    assert set(catalog.ENFR_CSV_COLUMNS.values()) <= set(catalog.INDICATOR_BY_SLUG)


def test_valores_de_enumeraciones():
    assert {i.higher_is for i in catalog.INDICATORS} <= {"better", "worse", "neutral"}
    assert {i.category for i in catalog.INDICATORS} <= {"outcome", "care", "risk_factor", "context"}

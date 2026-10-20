"""Carga (idempotente) de los datos de referencia: fuentes, datasets, indicadores,
jurisdicciones con su geometría."""

from pathlib import Path

from geoalchemy2.shape import from_shape
from sqlalchemy import select
from sqlalchemy.orm import Session

from mapa import catalog
from mapa.db.models import Dataset, DatasetIndicator, Indicator, Jurisdiction, Source
from mapa.etl.geo import read_provinces


def _get_or_create(session: Session, model, **lookup):
    instance = session.scalar(select(model).filter_by(**lookup))
    if instance is None:
        instance = model(**lookup)
        session.add(instance)
    return instance


def seed_reference(session: Session, geo_file: Path) -> None:
    sources = {}
    for s in catalog.SOURCES:
        row = _get_or_create(session, Source, slug=s.slug)
        row.name, row.publisher, row.url = s.name, s.publisher, s.url
        sources[s.slug] = row
    session.flush()

    datasets = {}
    for d in catalog.DATASETS:
        row = _get_or_create(session, Dataset, slug=d.slug)
        row.source_id = sources[d.source_slug].id
        row.name, row.reference_period = d.name, d.reference_period
        row.universe, row.notes = d.universe, d.notes
        datasets[d.slug] = row

    indicators = {}
    for i in catalog.INDICATORS:
        row = _get_or_create(session, Indicator, slug=i.slug)
        row.label, row.description, row.unit = i.label, i.description, i.unit
        row.decimals, row.higher_is, row.category = i.decimals, i.higher_is, i.category
        indicators[i.slug] = row
    session.flush()

    for link in catalog.DATASET_INDICATORS:
        row = session.get(
            DatasetIndicator,
            (datasets[link.dataset_slug].id, indicators[link.indicator_slug].id),
        )
        if row is None:
            row = DatasetIndicator(
                dataset_id=datasets[link.dataset_slug].id,
                indicator_id=indicators[link.indicator_slug].id,
            )
            session.add(row)
        row.source_ref, row.note = link.source_ref, link.note

    geometries = read_provinces(geo_file)
    for j in catalog.JURISDICTIONS:
        row = _get_or_create(session, Jurisdiction, slug=j.slug)
        row.iso_code, row.name, row.short_name = j.iso, j.name, j.short
        row.kind, row.region = j.kind, j.region
        geom = geometries.get(j.slug)
        row.geom = from_shape(geom, srid=4326) if geom is not None else None

    session.commit()

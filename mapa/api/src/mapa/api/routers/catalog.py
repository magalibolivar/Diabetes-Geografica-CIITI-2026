from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from mapa.api.schemas import IndicatorOut, JurisdictionOut, LineageOut
from mapa.db.models import Dataset, DatasetIndicator, Indicator, Jurisdiction, Source
from mapa.db.session import get_db

router = APIRouter(tags=["catálogo"])


@router.get("/indicators", response_model=list[IndicatorOut])
def list_indicators(db: Session = Depends(get_db)) -> list[IndicatorOut]:
    lineage_rows = db.execute(
        select(DatasetIndicator, Dataset, Source)
        .join(Dataset, Dataset.id == DatasetIndicator.dataset_id)
        .join(Source, Source.id == Dataset.source_id)
        .order_by(Dataset.reference_period.desc())
    ).all()
    lineage: dict[int, list[LineageOut]] = {}
    for link, dataset, source in lineage_rows:
        lineage.setdefault(link.indicator_id, []).append(
            LineageOut(
                dataset=dataset.slug,
                dataset_name=dataset.name,
                source_name=source.name,
                publisher=source.publisher,
                source_url=source.url,
                reference_period=dataset.reference_period,
                universe=dataset.universe,
                source_ref=link.source_ref,
                note=link.note,
                dataset_notes=dataset.notes,
            )
        )
    indicators = db.scalars(select(Indicator).order_by(Indicator.id)).all()
    return [
        IndicatorOut(
            slug=i.slug,
            label=i.label,
            description=i.description,
            unit=i.unit,
            decimals=i.decimals,
            higher_is=i.higher_is,
            category=i.category,
            lineage=lineage.get(i.id, []),
        )
        for i in indicators
    ]


@router.get("/jurisdictions", response_model=list[JurisdictionOut])
def list_jurisdictions(
    kind: str | None = Query(None, pattern="^(country|province)$"),
    db: Session = Depends(get_db),
) -> list[Jurisdiction]:
    stmt = select(Jurisdiction).order_by(Jurisdiction.name)
    if kind:
        stmt = stmt.where(Jurisdiction.kind == kind)
    return list(db.scalars(stmt))

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from mapa import security
from mapa.api.deps import Principal, authenticate
from mapa.api.schemas import ObservationOut
from mapa.db.models import Dataset, DatasetVersion, Indicator, Jurisdiction, Observation
from mapa.db.session import get_db

router = APIRouter(tags=["datos"])


@router.get("/observations", response_model=list[ObservationOut])
def list_observations(
    indicator: list[str] | None = Query(None, description="Slug(s) de indicador."),
    jurisdiction: list[str] | None = Query(None, description="Slug(s) de jurisdicción."),
    period: str | None = None,
    version_id: int | None = Query(
        None, description="Ver una versión puntual (incluye borradores). Requiere read:draft."
    ),
    limit: int = Query(5000, ge=1, le=20000),
    db: Session = Depends(get_db),
    principal: Principal = Depends(authenticate),
) -> list[ObservationOut]:
    stmt = (
        select(
            Observation,
            Jurisdiction.slug,
            Indicator.slug,
            Dataset.slug,
            DatasetVersion.status,
        )
        .join(DatasetVersion, DatasetVersion.id == Observation.version_id)
        .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
        .join(Jurisdiction, Jurisdiction.id == Observation.jurisdiction_id)
        .join(Indicator, Indicator.id == Observation.indicator_id)
        .order_by(Indicator.id, Jurisdiction.id, Observation.period)
        .limit(limit)
    )
    if version_id is not None:
        if not security.scope_allows(principal.scopes, "read:draft"):
            raise HTTPException(403, "Ver versiones puntuales requiere el alcance «read:draft».")
        stmt = stmt.where(Observation.version_id == version_id)
    else:
        stmt = stmt.where(DatasetVersion.status == "published")
    if indicator:
        stmt = stmt.where(Indicator.slug.in_(indicator))
    if jurisdiction:
        stmt = stmt.where(Jurisdiction.slug.in_(jurisdiction))
    if period:
        stmt = stmt.where(Observation.period == period)

    return [
        ObservationOut(
            jurisdiction=j_slug,
            indicator=i_slug,
            period=o.period,
            value=float(o.value),
            cv=float(o.cv) if o.cv is not None else None,
            reliability=o.reliability,
            dataset=d_slug,
            version_id=o.version_id,
            version_status=status,
        )
        for o, j_slug, i_slug, d_slug, status in db.execute(stmt)
    ]

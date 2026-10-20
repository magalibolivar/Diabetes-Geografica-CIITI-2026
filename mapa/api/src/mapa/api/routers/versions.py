from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from mapa.api.deps import require_scope
from mapa.api.schemas import VersionOut
from mapa.db.models import Dataset, DatasetVersion
from mapa.db.session import get_db

# Los borradores sólo los ve el equipo: este router exige read:draft.
router = APIRouter(tags=["versiones"], dependencies=[Depends(require_scope("read:draft"))])


@router.get("/versions", response_model=list[VersionOut])
def list_versions(db: Session = Depends(get_db)) -> list[VersionOut]:
    rows = db.execute(
        select(DatasetVersion, Dataset.slug)
        .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
        .order_by(Dataset.slug, DatasetVersion.id.desc())
    ).all()
    return [
        VersionOut(
            id=v.id,
            dataset=slug,
            status=v.status,
            n_observations=v.n_observations,
            content_hash=v.content_hash,
            created_at=v.created_at,
            published_at=v.published_at,
        )
        for v, slug in rows
    ]

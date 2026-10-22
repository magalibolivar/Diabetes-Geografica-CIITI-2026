"""Cargar un dataset crea una versión *draft*; publicarla la hace visible en el sitio.

- Idempotente: si el contenido es idéntico a una versión existente, no se duplica.
- Publicar archiva la versión publicada anterior del mismo dataset (rollback = volver a
  publicar la archivada).
"""

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from mapa import catalog
from mapa.db.models import Dataset, DatasetVersion, Indicator, Jurisdiction, Observation
from mapa.etl import context, enfr, nbi
from mapa.etl.raw import RawObservation

Reader = Callable[[Path], list[RawObservation]]


def _context_reader(slug: str) -> Reader:
    return lambda source_dir: context.parse_context(source_dir, slug)


READERS: dict[str, Reader] = {
    "enfr-2018": enfr.parse_enfr,
    "indec-nbi-2022": nbi.parse_nbi_2022,
    **{ds: _context_reader(ds) for ds, _ in catalog.CONTEXT_COLUMNS.values()},
}


def content_hash(observations: list[RawObservation]) -> str:
    rows = sorted(
        (o.jurisdiction, o.indicator, o.period, str(o.value), str(o.cv), str(o.reliability))
        for o in observations
    )
    return hashlib.sha256(repr(rows).encode()).hexdigest()


@dataclass(frozen=True)
class LoadResult:
    version: DatasetVersion
    created: bool


def load_dataset(session: Session, dataset_slug: str, source_dir: Path) -> LoadResult:
    dataset = session.scalar(select(Dataset).where(Dataset.slug == dataset_slug))
    if dataset is None:
        raise LookupError(f"Dataset desconocido o sin seed: {dataset_slug}")

    observations = READERS[dataset_slug](source_dir)
    digest = content_hash(observations)

    existing = session.scalar(
        select(DatasetVersion).where(
            DatasetVersion.dataset_id == dataset.id, DatasetVersion.content_hash == digest
        )
    )
    if existing is not None:
        return LoadResult(existing, created=False)

    jurisdictions = dict(session.execute(select(Jurisdiction.slug, Jurisdiction.id)).all())
    indicators = dict(session.execute(select(Indicator.slug, Indicator.id)).all())

    version = DatasetVersion(
        dataset_id=dataset.id,
        status="draft",
        content_hash=digest,
        n_observations=len(observations),
    )
    session.add(version)
    session.flush()
    session.add_all(
        Observation(
            version_id=version.id,
            jurisdiction_id=jurisdictions[o.jurisdiction],
            indicator_id=indicators[o.indicator],
            period=o.period,
            value=o.value,
            cv=o.cv,
            reliability=o.reliability,
        )
        for o in observations
    )
    session.commit()
    return LoadResult(version, created=True)


def publish_version(session: Session, version_id: int) -> DatasetVersion:
    version = session.get(DatasetVersion, version_id)
    if version is None:
        raise LookupError(f"No existe la versión {version_id}")
    if version.status == "published":
        return version

    session.execute(
        update(DatasetVersion)
        .where(DatasetVersion.dataset_id == version.dataset_id, DatasetVersion.status == "published")
        .values(status="archived")
    )
    session.flush()  # libera el índice parcial antes de publicar la nueva
    version.status = "published"
    version.published_at = datetime.now(UTC)
    session.commit()
    return version

from datetime import datetime

from pydantic import BaseModel


class LineageOut(BaseModel):
    """De dónde sale un indicador: la base del «Fuente» del sitio."""

    dataset: str
    dataset_name: str
    source_name: str
    publisher: str
    source_url: str | None
    reference_period: str
    universe: str | None
    source_ref: str
    note: str | None
    dataset_notes: str | None


class IndicatorOut(BaseModel):
    slug: str
    label: str
    description: str
    unit: str
    decimals: int
    higher_is: str
    category: str
    lineage: list[LineageOut]


class JurisdictionOut(BaseModel):
    slug: str
    iso_code: str
    name: str
    short_name: str
    kind: str
    region: str | None


class ObservationOut(BaseModel):
    jurisdiction: str
    indicator: str
    period: str
    value: float
    cv: float | None
    # ok | caution | unreliable (marca de INDEC) | null (la fuente no la informa)
    reliability: str | None
    dataset: str
    version_id: int
    version_status: str


class VersionOut(BaseModel):
    id: int
    dataset: str
    status: str
    n_observations: int
    content_hash: str
    created_at: datetime
    published_at: datetime | None


class LocateOut(BaseModel):
    jurisdiction: JurisdictionOut
    note: str = (
        "Resultado sobre geometrías simplificadas: cerca de un límite provincial puede ser inexacto."
    )

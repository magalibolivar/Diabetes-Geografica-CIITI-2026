"""Modelo de datos.

Idea central: una tabla de hechos `observation` (jurisdicción × indicador × período)
ligada a una `dataset_version`. Cargar una encuesta nueva o un año nuevo es agregar
filas, no cambiar el esquema. Los datos nuevos entran como `draft` y recién se ven en
el sitio público cuando se `publish`-an.
"""

from datetime import datetime
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Source(Base):
    __tablename__ = "source"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(Text)
    publisher: Mapped[str] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)


class Dataset(Base):
    __tablename__ = "dataset"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("source.id"))
    name: Mapped[str] = mapped_column(Text)
    reference_period: Mapped[str] = mapped_column(String(16))
    universe: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    source: Mapped[Source] = relationship()


class Indicator(Base):
    __tablename__ = "indicator"
    __table_args__ = (
        CheckConstraint("higher_is IN ('better', 'worse', 'neutral')", name="higher_is"),
        CheckConstraint(
            "category IN ('outcome', 'care', 'risk_factor', 'context')", name="category"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    label: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(16))
    decimals: Mapped[int] = mapped_column(Integer, server_default="1")
    higher_is: Mapped[str] = mapped_column(String(8))
    category: Mapped[str] = mapped_column(String(16))


class DatasetIndicator(Base):
    """Linaje: en qué dataset aparece un indicador y dónde exactamente (cuadro/hoja)."""

    __tablename__ = "dataset_indicator"

    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id"), primary_key=True)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicator.id"), primary_key=True)
    source_ref: Mapped[str] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)


class Jurisdiction(Base):
    __tablename__ = "jurisdiction"
    __table_args__ = (
        CheckConstraint("kind IN ('country', 'province')", name="kind"),
        Index("ix_jurisdiction_geom", "geom", postgresql_using="gist"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    iso_code: Mapped[str] = mapped_column(String(8), unique=True)
    name: Mapped[str] = mapped_column(Text)
    short_name: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(8))
    region: Mapped[str | None] = mapped_column(String(32))
    geom = mapped_column(Geometry("MULTIPOLYGON", srid=4326, spatial_index=False), nullable=True)


class DatasetVersion(Base):
    __tablename__ = "dataset_version"
    __table_args__ = (
        CheckConstraint("status IN ('draft', 'published', 'archived')", name="status"),
        UniqueConstraint("dataset_id", "content_hash", name="uq_dataset_version_content"),
        # A lo sumo una versión publicada por dataset.
        Index(
            "ix_one_published_per_dataset",
            "dataset_id",
            unique=True,
            postgresql_where=text("status = 'published'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id"))
    status: Mapped[str] = mapped_column(String(10), server_default="draft")
    content_hash: Mapped[str] = mapped_column(String(64))
    n_observations: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    note: Mapped[str | None] = mapped_column(Text)

    dataset: Mapped[Dataset] = relationship()


class Observation(Base):
    __tablename__ = "observation"
    __table_args__ = (
        CheckConstraint(
            "reliability IS NULL OR reliability IN ('ok', 'caution', 'unreliable')",
            name="reliability",
        ),
        UniqueConstraint(
            "version_id", "jurisdiction_id", "indicator_id", "period",
            name="uq_observation_key",
        ),
        Index("ix_observation_indicator_id_jurisdiction_id", "indicator_id", "jurisdiction_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    version_id: Mapped[int] = mapped_column(
        ForeignKey("dataset_version.id", ondelete="CASCADE")
    )
    jurisdiction_id: Mapped[int] = mapped_column(ForeignKey("jurisdiction.id"))
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicator.id"))
    period: Mapped[str] = mapped_column(String(16))
    value: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    # Coeficiente de variación (%) publicado por la fuente; NULL si la fuente no lo informa.
    cv: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    # Marca de confiabilidad de la fuente (nota al pie de INDEC): ok | caution | unreliable.
    # NULL = la fuente no evalúa confiabilidad para este dato.
    reliability: Mapped[str | None] = mapped_column(String(10))

    version: Mapped[DatasetVersion] = relationship()
    jurisdiction: Mapped[Jurisdiction] = relationship()
    indicator: Mapped[Indicator] = relationship()


class ApiKey(Base):
    __tablename__ = "api_key"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    prefix: Mapped[str] = mapped_column(String(16), unique=True)
    key_hash: Mapped[str] = mapped_column(String(64))
    scopes: Mapped[list[str]] = mapped_column(ARRAY(Text))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

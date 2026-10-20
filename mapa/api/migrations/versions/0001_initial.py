"""esquema inicial

Revision ID: 0001
Revises:
Create Date: 2026-10-20
"""
import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "source",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("publisher", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_source")),
        sa.UniqueConstraint("slug", name=op.f("uq_source_slug")),
    )

    op.create_table(
        "dataset",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("reference_period", sa.String(16), nullable=False),
        sa.Column("universe", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["source.id"], name=op.f("fk_dataset_source_id_source")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dataset")),
        sa.UniqueConstraint("slug", name=op.f("uq_dataset_slug")),
    )

    op.create_table(
        "indicator",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("unit", sa.String(16), nullable=False),
        sa.Column("decimals", sa.Integer(), server_default="1", nullable=False),
        sa.Column("higher_is", sa.String(8), nullable=False),
        sa.Column("category", sa.String(16), nullable=False),
        sa.CheckConstraint(
            "higher_is IN ('better', 'worse', 'neutral')", name=op.f("ck_indicator_higher_is")
        ),
        sa.CheckConstraint(
            "category IN ('outcome', 'care', 'risk_factor', 'context')", name=op.f("ck_indicator_category")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicator")),
        sa.UniqueConstraint("slug", name=op.f("uq_indicator_slug")),
    )

    op.create_table(
        "dataset_indicator",
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("source_ref", sa.Text(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dataset_id"], ["dataset.id"], name=op.f("fk_dataset_indicator_dataset_id_dataset")
        ),
        sa.ForeignKeyConstraint(
            ["indicator_id"], ["indicator.id"], name=op.f("fk_dataset_indicator_indicator_id_indicator")
        ),
        sa.PrimaryKeyConstraint("dataset_id", "indicator_id", name=op.f("pk_dataset_indicator")),
    )

    op.create_table(
        "jurisdiction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("iso_code", sa.String(8), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("short_name", sa.Text(), nullable=False),
        sa.Column("kind", sa.String(8), nullable=False),
        sa.Column("region", sa.String(32), nullable=True),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=False),
            nullable=True,
        ),
        sa.CheckConstraint("kind IN ('country', 'province')", name=op.f("ck_jurisdiction_kind")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jurisdiction")),
        sa.UniqueConstraint("slug", name=op.f("uq_jurisdiction_slug")),
        sa.UniqueConstraint("iso_code", name=op.f("uq_jurisdiction_iso_code")),
    )
    op.create_index("ix_jurisdiction_geom", "jurisdiction", ["geom"], postgresql_using="gist")

    op.create_table(
        "dataset_version",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(10), server_default="draft", nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("n_observations", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "status IN ('draft', 'published', 'archived')", name=op.f("ck_dataset_version_status")
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"], ["dataset.id"], name=op.f("fk_dataset_version_dataset_id_dataset")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dataset_version")),
        sa.UniqueConstraint("dataset_id", "content_hash", name="uq_dataset_version_content"),
    )
    op.create_index(
        "ix_one_published_per_dataset",
        "dataset_version",
        ["dataset_id"],
        unique=True,
        postgresql_where=sa.text("status = 'published'"),
    )

    op.create_table(
        "observation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("jurisdiction_id", sa.Integer(), nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(16), nullable=False),
        sa.Column("value", sa.Numeric(14, 4), nullable=False),
        sa.Column("cv", sa.Numeric(6, 2), nullable=True),
        sa.Column("reliability", sa.String(10), nullable=True),
        sa.CheckConstraint(
            "reliability IS NULL OR reliability IN ('ok', 'caution', 'unreliable')",
            name=op.f("ck_observation_reliability"),
        ),
        sa.ForeignKeyConstraint(
            ["version_id"], ["dataset_version.id"],
            name=op.f("fk_observation_version_id_dataset_version"), ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["jurisdiction_id"], ["jurisdiction.id"], name=op.f("fk_observation_jurisdiction_id_jurisdiction")
        ),
        sa.ForeignKeyConstraint(
            ["indicator_id"], ["indicator.id"], name=op.f("fk_observation_indicator_id_indicator")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_observation")),
        sa.UniqueConstraint(
            "version_id", "jurisdiction_id", "indicator_id", "period", name="uq_observation_key"
        ),
    )
    op.create_index(
        "ix_observation_indicator_id_jurisdiction_id", "observation", ["indicator_id", "jurisdiction_id"]
    )

    op.create_table(
        "api_key",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("prefix", sa.String(16), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("scopes", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_api_key")),
        sa.UniqueConstraint("prefix", name=op.f("uq_api_key_prefix")),
    )


def downgrade() -> None:
    op.drop_table("api_key")
    op.drop_index("ix_observation_indicator_id_jurisdiction_id", table_name="observation")
    op.drop_table("observation")
    op.drop_index("ix_one_published_per_dataset", table_name="dataset_version")
    op.drop_table("dataset_version")
    op.drop_index("ix_jurisdiction_geom", table_name="jurisdiction", postgresql_using="gist")
    op.drop_table("jurisdiction")
    op.drop_table("dataset_indicator")
    op.drop_table("indicator")
    op.drop_table("dataset")
    op.drop_table("source")

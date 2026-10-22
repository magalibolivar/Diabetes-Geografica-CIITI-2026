"""Línea de comandos de MAPA. Es la *única* vía de escritura de datos: la API es de lectura."""

import json
import os
import re
from datetime import UTC, date, datetime
from pathlib import Path

import typer
from alembic import command
from alembic.config import Config
from sqlalchemy import select

from mapa import catalog, security
from mapa.config import get_settings
from mapa.db.models import ApiKey, Dataset, DatasetVersion
from mapa.db.session import new_session
from mapa.etl import geo as etl_geo
from mapa.etl import geo_build, geoqa
from mapa.etl import load as etl_load
from mapa.etl import seed as etl_seed
from mapa.etl import verify as etl_verify

app = typer.Typer(help="MAPA — operaciones de datos y claves.", no_args_is_help=True)
db_app = typer.Typer(help="Esquema y datos de referencia.", no_args_is_help=True)
etl_app = typer.Typer(help="Carga y publicación de datos.", no_args_is_help=True)
keys_app = typer.Typer(help="API keys de la API interna.", no_args_is_help=True)
geo_app = typer.Typer(help="Capa geográfica de provincias.", no_args_is_help=True)
app.add_typer(db_app, name="db")
app.add_typer(etl_app, name="etl")
app.add_typer(keys_app, name="keys")
app.add_typer(geo_app, name="geo")


def _upgrade() -> None:
    command.upgrade(Config("alembic.ini"), "head")


@db_app.command("upgrade")
def db_upgrade() -> None:
    """Aplica las migraciones pendientes (alembic upgrade head). Correr desde mapa/api."""
    _upgrade()
    typer.echo("Esquema al día.")


@db_app.command("seed")
def db_seed() -> None:
    """Carga fuentes, datasets, indicadores y jurisdicciones (con geometría)."""
    with new_session() as session:
        etl_seed.seed_reference(session, get_settings().geo_file)
    typer.echo("Datos de referencia cargados.")


@etl_app.command("load")
def etl_load_cmd(
    dataset: str = typer.Argument(None, help="Slug del dataset; omitir con --all."),
    all_: bool = typer.Option(False, "--all", help="Cargar todos los datasets."),
    publish: bool = typer.Option(False, "--publish", help="Publicar apenas se carga."),
) -> None:
    """Carga un dataset como versión borrador (idempotente)."""
    slugs = [d.slug for d in catalog.DATASETS] if all_ else [dataset]
    if not all_ and not dataset:
        raise typer.BadParameter("Indicá un dataset o usá --all.")
    settings = get_settings()
    with new_session() as session:
        for slug in slugs:
            result = etl_load.load_dataset(session, slug, settings.source_dir)
            v = result.version
            estado = "creada" if result.created else "ya existía"
            typer.echo(f"{slug}: versión {v.id} {estado} ({v.n_observations} obs., {v.status})")
            if publish:
                etl_load.publish_version(session, v.id)
                typer.echo(f"{slug}: versión {v.id} publicada")


@etl_app.command("publish")
def etl_publish(version_id: int) -> None:
    """Publica una versión; archiva la publicada anterior del mismo dataset."""
    with new_session() as session:
        v = etl_load.publish_version(session, version_id)
        typer.echo(f"Versión {v.id} publicada.")


@etl_app.command("versions")
def etl_versions() -> None:
    """Lista las versiones de datos."""
    with new_session() as session:
        rows = session.execute(
            select(DatasetVersion, Dataset.slug)
            .join(Dataset, Dataset.id == DatasetVersion.dataset_id)
            .order_by(Dataset.slug, DatasetVersion.id)
        ).all()
        for v, slug in rows:
            typer.echo(
                f"{v.id:>3}  {slug:<24} {v.status:<10} {v.n_observations:>4} obs.  {v.content_hash[:10]}"
            )


@etl_app.command("verify")
def etl_verify_cmd() -> None:
    """Compara el .xls oficial de la ENFR contra el CSV validado por el equipo."""
    problems = etl_verify.cross_check_enfr(get_settings().source_dir)
    if problems:
        for p in problems:
            typer.echo(f"DIFIERE  {p}", err=True)
        raise typer.Exit(1)
    typer.echo("OK: el .xls oficial y el CSV coinciden en todas las provincias.")


@app.command()
def bootstrap() -> None:
    """Entorno de desarrollo desde cero: migra, siembra, carga y publica todo."""
    if get_settings().is_prod:
        typer.echo("bootstrap está deshabilitado en producción.", err=True)
        raise typer.Exit(1)
    _upgrade()
    db_seed()
    etl_load_cmd(dataset=None, all_=True, publish=True)


@keys_app.command("create")
def keys_create(
    name: str = typer.Option(..., help="Para quién es la clave (persona o servicio)."),
    scope: list[str] = typer.Option(["read"], help="read | read:draft (repetible)."),
) -> None:
    """Genera una API key. Se muestra una única vez."""
    invalid = [s for s in scope if s not in security.VALID_SCOPES]
    if invalid:
        raise typer.BadParameter(f"Alcances inválidos: {invalid}. Válidos: {security.VALID_SCOPES}")
    key = security.generate_key()
    with new_session() as session:
        session.add(ApiKey(name=name, prefix=key.prefix, key_hash=key.key_hash, scopes=scope))
        session.commit()
    typer.echo(f"Clave para «{name}» ({', '.join(scope)}):\n\n  {key.plaintext}\n")
    typer.echo("Guardala ahora: no se puede volver a mostrar.")


@keys_app.command("ensure-web")
def keys_ensure_web() -> None:
    """Sincroniza la clave web provista por el entorno, sin mostrarla ni rotarla."""
    plaintext = os.environ.get("MAPA_WEB_API_KEY", "")
    if not re.fullmatch(r"mk_[0-9a-f]{8}_[0-9a-f]{48}", plaintext):
        raise typer.BadParameter(
            "MAPA_WEB_API_KEY debe ser una clave aleatoria con formato mk_<8 hex>_<48 hex>"
        )
    prefix = security.parse_prefix(plaintext)
    with new_session() as session:
        existing = session.scalar(select(ApiKey).where(ApiKey.prefix == prefix))
        if existing is not None:
            if (
                existing.revoked_at
                or not security.verify_key(plaintext, existing.key_hash)
                or existing.scopes != ["read"]
            ):
                raise typer.BadParameter(
                    "La clave web configurada entra en conflicto con una clave existente"
                )
            typer.echo("Clave web de lectura ya configurada.")
            return
        session.add(ApiKey(name="web", prefix=prefix, key_hash=security.hash_key(plaintext), scopes=["read"]))
        session.commit()
    typer.echo("Clave web de lectura configurada.")


@keys_app.command("list")
def keys_list() -> None:
    """Lista las claves (sin el secreto)."""
    with new_session() as session:
        for k in session.scalars(select(ApiKey).order_by(ApiKey.id)):
            estado = "revocada" if k.revoked_at else "activa"
            typer.echo(f"{k.prefix}  {k.name:<24} {','.join(k.scopes):<16} {estado}")


@keys_app.command("revoke")
def keys_revoke(prefix: str) -> None:
    """Revoca una clave por su prefijo."""
    with new_session() as session:
        key = session.scalar(select(ApiKey).where(ApiKey.prefix == prefix))
        if key is None:
            typer.echo("No existe esa clave.", err=True)
            raise typer.Exit(1)
        key.revoked_at = datetime.now(UTC)
        session.commit()
    typer.echo(f"Clave {prefix} revocada.")


def _report_geo_quality(shapes) -> list[str]:
    problems = geoqa.capitals_outside(shapes) + geoqa.overlaps(shapes)
    for p in problems:
        typer.echo(f"PROBLEMA  {p}", err=True)
    return problems


@geo_app.command("build")
def geo_build_cmd(
    input_path: Path = typer.Option(
        ..., "--input", exists=True, dir_okay=False, help="GeoJSON del IGN (ign:provincia)."
    ),
    output: Path = typer.Option(None, help="Por defecto, MAPA_GEO_FILE."),
    tolerance: float = typer.Option(
        geo_build.DEFAULT_TOLERANCE, help="Tolerancia de simplificación (grados)."
    ),
    retrieved: datetime = typer.Option(
        None, formats=["%Y-%m-%d"], help="Fecha de descarga (por defecto, hoy)."
    ),
) -> None:
    """Genera la capa liviana de provincias desde la capa oficial del IGN y la controla."""
    output = output or get_settings().geo_file
    collection, shapes = geo_build.build(
        input_path, tolerance=tolerance, retrieved=retrieved.date() if retrieved else date.today()
    )
    if _report_geo_quality(shapes):
        raise typer.Exit(1)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(collection, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    typer.echo(
        f"{output}: {geo_build.vertex_count(shapes)} vértices, {output.stat().st_size / 1024:.0f} KB, "
        "24 capitales dentro de su provincia, sin solapes."
    )


@geo_app.command("check")
def geo_check() -> None:
    """Controla la calidad de la capa actual (capitales dentro de su provincia, sin solapes)."""
    shapes = etl_geo.read_provinces(get_settings().geo_file)
    if _report_geo_quality(shapes):
        raise typer.Exit(1)
    typer.echo("OK: geometría consistente.")

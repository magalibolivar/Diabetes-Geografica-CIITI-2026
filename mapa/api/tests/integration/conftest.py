"""Tests de integración contra una PostGIS real (testcontainers). Se saltean sin Docker."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

API_ROOT = Path(__file__).resolve().parents[2]


def alembic_config(url: str) -> Config:
    cfg = Config(str(API_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(API_ROOT / "migrations"))
    cfg.attributes["url"] = url
    return cfg


@pytest.fixture(scope="session")
def database_url():
    try:
        try:
            from testcontainers.community.postgres import PostgresContainer
        except ImportError:  # versiones anteriores de testcontainers
            from testcontainers.postgres import PostgresContainer

        container = PostgresContainer("postgis/postgis:16-3.4", driver="psycopg")
        container.start()
    except Exception as exc:  # Docker no disponible
        pytest.skip(f"Docker no disponible: {exc}")
    yield container.get_connection_url()
    container.stop()


@pytest.fixture(scope="session")
def migrated(database_url, monkeypatch_session):
    monkeypatch_session.setenv("MAPA_DATABASE_URL", database_url)
    from mapa.config import get_settings
    from mapa.db import session as db_session

    get_settings.cache_clear()
    db_session.get_engine.cache_clear()
    db_session._session_factory.cache_clear()

    command.upgrade(alembic_config(database_url), "head")
    return database_url


@pytest.fixture(scope="session")
def monkeypatch_session():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture(scope="session")
def seeded(migrated):
    from mapa.config import get_settings
    from mapa.db.session import new_session
    from mapa.etl import seed

    settings = get_settings()
    with new_session() as session:
        seed.seed_reference(session, settings.geo_file)
    return migrated


@pytest.fixture(scope="session")
def published(seeded):
    from mapa import catalog
    from mapa.config import get_settings
    from mapa.db.session import new_session
    from mapa.etl import load

    with new_session() as session:
        for dataset in catalog.DATASETS:
            result = load.load_dataset(session, dataset.slug, get_settings().source_dir)
            load.publish_version(session, result.version.id)
    return seeded


def _make_key(scopes: list[str]) -> str:
    from mapa import security
    from mapa.db.models import ApiKey
    from mapa.db.session import new_session

    key = security.generate_key()
    with new_session() as session:
        session.add(ApiKey(name="test", prefix=key.prefix, key_hash=key.key_hash, scopes=scopes))
        session.commit()
    return key.plaintext


@pytest.fixture(scope="session")
def read_key(published):
    return _make_key(["read"])


@pytest.fixture(scope="session")
def draft_key(published):
    return _make_key(["read", "read:draft"])


@pytest.fixture(scope="session")
def client(published):
    from fastapi.testclient import TestClient

    from mapa.api.main import create_app

    with TestClient(create_app()) as c:
        yield c

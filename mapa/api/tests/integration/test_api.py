from decimal import Decimal

import pytest

pytestmark = pytest.mark.integration


def auth(key: str) -> dict[str, str]:
    return {"X-API-Key": key}


def test_las_migraciones_coinciden_con_los_modelos(migrated):
    """Si alguien cambia un modelo sin escribir la migración, esto falla."""
    from alembic import command

    from .conftest import alembic_config

    command.check(alembic_config(migrated))


# ---- autenticación -----------------------------------------------------------------

def test_health_es_abierto(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").json()["status"] == "ready"


@pytest.mark.parametrize("path", ["/v1/indicators", "/v1/observations", "/v1/geo/provinces"])
def test_sin_clave_es_401(client, path):
    assert client.get(path).status_code == 401


def test_clave_invalida_es_401(client):
    assert client.get("/v1/indicators", headers=auth("mk_deadbeef_xxxx")).status_code == 401


def test_clave_valida_lee_el_catalogo(client, read_key):
    r = client.get("/v1/indicators", headers=auth(read_key))
    assert r.status_code == 200
    assert len(r.json()) == 13


def test_los_borradores_exigen_read_draft(client, read_key, draft_key):
    assert client.get("/v1/versions", headers=auth(read_key)).status_code == 403
    assert client.get("/v1/observations?version_id=1", headers=auth(read_key)).status_code == 403
    assert client.get("/v1/versions", headers=auth(draft_key)).status_code == 200


def test_clave_revocada_deja_de_funcionar(client, published):
    from datetime import UTC, datetime

    from sqlalchemy import select

    from mapa import security
    from mapa.db.models import ApiKey
    from mapa.db.session import new_session

    from .conftest import _make_key

    plaintext = _make_key(["read"])
    assert client.get("/v1/indicators", headers=auth(plaintext)).status_code == 200
    with new_session() as session:
        key = session.scalar(
            select(ApiKey).where(ApiKey.prefix == security.parse_prefix(plaintext))
        )
        key.revoked_at = datetime.now(UTC)
        session.commit()
    assert client.get("/v1/indicators", headers=auth(plaintext)).status_code == 401


# ---- datos --------------------------------------------------------------------------

def test_observaciones_publicadas(client, read_key):
    r = client.get("/v1/observations?limit=20000", headers=auth(read_key))
    rows = r.json()
    # 9 indicadores ENFR × (24 provincias + total) + 4 de contexto × 24 provincias
    assert len(rows) == 9 * 25 + 4 * 24
    assert {row["version_status"] for row in rows} == {"published"}


def test_la_marca_de_confiabilidad_de_indec_llega_por_la_api(client, read_key):
    r = client.get(
        "/v1/observations?indicator=diabetes_treatment&jurisdiction=la-pampa",
        headers=auth(read_key),
    )
    (row,) = r.json()
    assert row["value"] == pytest.approx(32.7)
    assert row["cv"] == pytest.approx(17.7)
    assert row["reliability"] == "unreliable"


def test_el_linaje_incluye_cuadro_y_universo(client, read_key):
    indicators = {i["slug"]: i for i in client.get("/v1/indicators", headers=auth(read_key)).json()}
    (lineage,) = indicators["diabetes_treatment"]["lineage"]
    assert lineage["source_ref"] == "Cuadro 7.5"
    assert "5.000" in lineage["universe"]
    assert "no es confiable" in lineage["dataset_notes"]


# ---- geo ----------------------------------------------------------------------------

def test_geojson_de_provincias_con_etag(client, read_key):
    r = client.get("/v1/geo/provinces", headers=auth(read_key))
    assert r.status_code == 200
    assert len(r.json()["features"]) == 24
    again = client.get(
        "/v1/geo/provinces", headers={**auth(read_key), "If-None-Match": r.headers["ETag"]}
    )
    assert again.status_code == 304


@pytest.mark.parametrize(
    ("lat", "lng", "slug"),
    [
        (-34.6037, -58.3816, "caba"),  # Obelisco
        (-32.9468, -60.6393, "santa-fe"),  # Rosario (antes resolvía como Buenos Aires)
        (-31.4201, -64.1888, "cordoba"),
        (-24.7821, -65.4232, "salta"),
        (-38.0055, -57.5426, "buenos-aires"),  # Mar del Plata
    ],
)
def test_locate_devuelve_la_provincia(client, read_key, lat, lng, slug):
    r = client.get(f"/v1/locate?lat={lat}&lng={lng}", headers=auth(read_key))
    assert r.json()["jurisdiction"]["slug"] == slug


def test_locate_fuera_del_pais_es_404(client, read_key):
    assert client.get("/v1/locate?lat=-40&lng=-50", headers=auth(read_key)).status_code == 404


# ---- flujo borrador -> publicado -> rollback ---------------------------------------

def test_borrador_publicacion_y_rollback(client, read_key, draft_key):
    from sqlalchemy import select

    from mapa.config import get_settings
    from mapa.db.models import Dataset, DatasetVersion
    from mapa.db.session import new_session
    from mapa.etl import load
    from mapa.etl.raw import RawObservation

    slug = "indec-nbi-2010"
    original = load.READERS[slug]

    def altered(source_dir):
        return [
            RawObservation(o.jurisdiction, o.indicator, o.period, o.value + Decimal(1))
            for o in original(source_dir)
        ]

    with new_session() as session:
        before = session.scalar(
            select(DatasetVersion)
            .join(Dataset)
            .where(Dataset.slug == slug, DatasetVersion.status == "published")
        )
        before_id = before.id

        # Re-cargar lo mismo no duplica.
        assert not load.load_dataset(session, slug, get_settings().source_dir).created

        # Un dato nuevo entra como borrador y NO aparece en el sitio público.
        load.READERS[slug] = altered
        try:
            draft = load.load_dataset(session, slug, get_settings().source_dir)
        finally:
            load.READERS[slug] = original
        assert draft.created and draft.version.status == "draft"

        public = client.get(
            "/v1/observations?indicator=nbi_households&jurisdiction=chaco", headers=auth(read_key)
        ).json()
        assert [r["version_id"] for r in public] == [before_id]

        # El equipo sí puede revisarlo.
        preview = client.get(
            f"/v1/observations?version_id={draft.version.id}&jurisdiction=chaco",
            headers=auth(draft_key),
        ).json()
        assert preview[0]["version_status"] == "draft"

        # Publicar archiva la anterior...
        load.publish_version(session, draft.version.id)
        public = client.get(
            "/v1/observations?indicator=nbi_households&jurisdiction=chaco", headers=auth(read_key)
        ).json()
        assert [r["version_id"] for r in public] == [draft.version.id]

        # ...y el rollback es volver a publicar la versión archivada.
        load.publish_version(session, before_id)
        public = client.get(
            "/v1/observations?indicator=nbi_households&jurisdiction=chaco", headers=auth(read_key)
        ).json()
        assert [r["version_id"] for r in public] == [before_id]

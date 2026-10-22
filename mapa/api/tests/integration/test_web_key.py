"""La clave interna de la web se instala sin exponerla en logs."""

from sqlalchemy import select

from mapa import security
from mapa.cli import keys_ensure_web
from mapa.db.models import ApiKey
from mapa.db.session import new_session


def test_ensure_web_es_idempotente_y_no_imprime_secreto(migrated, monkeypatch, capsys):
    key = security.generate_key()
    monkeypatch.setenv("MAPA_WEB_API_KEY", key.plaintext)

    keys_ensure_web()
    keys_ensure_web()

    with new_session() as session:
        rows = session.scalars(select(ApiKey).where(ApiKey.prefix == key.prefix)).all()
    assert len(rows) == 1
    assert rows[0].scopes == ["read"]
    assert security.verify_key(key.plaintext, rows[0].key_hash)
    assert key.plaintext not in capsys.readouterr().out

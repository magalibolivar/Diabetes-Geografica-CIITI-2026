from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import Session

from mapa import security
from mapa.db.models import ApiKey
from mapa.db.session import get_db

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
LAST_USED_GRANULARITY = timedelta(minutes=10)


@dataclass(frozen=True)
class Principal:
    key_id: int
    name: str
    scopes: tuple[str, ...]


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(401, detail, headers={"WWW-Authenticate": "ApiKey"})


def authenticate(
    raw_key: str | None = Security(api_key_header), db: Session = Depends(get_db)
) -> Principal:
    if not raw_key:
        raise _unauthorized("Falta la API key (header X-API-Key).")
    prefix = security.parse_prefix(raw_key)
    key = (
        db.scalar(select(ApiKey).where(ApiKey.prefix == prefix, ApiKey.revoked_at.is_(None)))
        if prefix
        else None
    )
    if key is None or not security.verify_key(raw_key, key.key_hash):
        raise _unauthorized("API key inválida o revocada.")

    now = datetime.now(UTC)
    if key.last_used_at is None or now - key.last_used_at > LAST_USED_GRANULARITY:
        key.last_used_at = now
        db.commit()
    return Principal(key.id, key.name, tuple(key.scopes))


def require_scope(scope: str):
    def dependency(principal: Principal = Depends(authenticate)) -> Principal:
        if not security.scope_allows(principal.scopes, scope):
            raise HTTPException(403, f"Esta clave no tiene el alcance «{scope}».")
        return principal

    return dependency

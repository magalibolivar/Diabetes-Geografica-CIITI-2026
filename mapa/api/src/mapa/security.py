"""API keys: formato mk_<prefijo>_<secreto>. En la base sólo se guarda el hash SHA-256.

Las claves son aleatorias de alta entropía (192 bits), por eso alcanza un hash rápido:
no hace falta un KDF lento como con contraseñas elegidas por personas.
"""

import hashlib
import hmac
import secrets
from dataclasses import dataclass

KEY_PREFIX = "mk"
VALID_SCOPES = ("read", "read:draft")
# read:draft incluye read.
IMPLIES = {"read:draft": {"read"}}


@dataclass(frozen=True)
class GeneratedKey:
    plaintext: str  # se muestra una única vez
    prefix: str
    key_hash: str


def hash_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode()).hexdigest()


def generate_key() -> GeneratedKey:
    prefix = secrets.token_hex(4)
    plaintext = f"{KEY_PREFIX}_{prefix}_{secrets.token_hex(24)}"
    return GeneratedKey(plaintext, prefix, hash_key(plaintext))


def parse_prefix(plaintext: str) -> str | None:
    parts = plaintext.split("_")
    if len(parts) != 3 or parts[0] != KEY_PREFIX or not parts[1]:
        return None
    return parts[1]


def verify_key(plaintext: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_key(plaintext), stored_hash)


def scope_allows(granted: list[str] | tuple[str, ...], required: str) -> bool:
    for scope in granted:
        if scope == required or required in IMPLIES.get(scope, ()):
            return True
    return False

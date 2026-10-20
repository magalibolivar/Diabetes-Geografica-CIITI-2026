from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _repo_root() -> Path:
    """<repo>/mapa/api/src/mapa/config.py -> <repo>. Sólo existe al correr desde el checkout;
    en el contenedor las rutas llegan por MAPA_SOURCE_DIR / MAPA_GEO_FILE."""
    parents = Path(__file__).resolve().parents
    return parents[4] if len(parents) > 4 else Path("/sources")


REPO_ROOT = _repo_root()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MAPA_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://mapa:mapa@localhost:5432/mapa"
    environment: str = "dev"  # dev | prod

    # Insumos del ETL (se montan de sólo lectura en Docker).
    source_dir: Path = REPO_ROOT / "data"
    # Capa oficial del IGN generada con `mapa geo build` (ver mapa/data/geo/README.md).
    geo_file: Path = REPO_ROOT / "mapa" / "data" / "geo" / "argentina_provincias.geojson"

    @property
    def is_prod(self) -> bool:
        return self.environment == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()

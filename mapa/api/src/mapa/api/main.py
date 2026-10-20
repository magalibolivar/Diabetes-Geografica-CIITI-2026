from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from mapa import __version__
from mapa.api.deps import require_scope
from mapa.api.routers import catalog, geo, observations, versions
from mapa.config import get_settings
from mapa.db.session import get_db


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="MAPA — API interna",
        version=__version__,
        description="Datos del atlas de diabetes en Argentina. Requiere API key (X-API-Key).",
        # En producción no se publica la documentación de una API interna.
        docs_url=None if settings.is_prod else "/docs",
        redoc_url=None,
        openapi_url=None if settings.is_prod else "/openapi.json",
    )

    @app.get("/health", tags=["sistema"])
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/ready", tags=["sistema"])
    def ready(db: Session = Depends(get_db)) -> dict[str, str]:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}

    reader = [Depends(require_scope("read"))]
    app.include_router(catalog.router, prefix="/v1", dependencies=reader)
    app.include_router(observations.router, prefix="/v1", dependencies=reader)
    app.include_router(geo.router, prefix="/v1", dependencies=reader)
    app.include_router(versions.router, prefix="/v1")
    return app


app = create_app()

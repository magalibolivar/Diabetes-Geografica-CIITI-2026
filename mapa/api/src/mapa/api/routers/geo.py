import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mapa.api.schemas import JurisdictionOut, LocateOut
from mapa.db.models import Jurisdiction
from mapa.db.session import get_db

router = APIRouter(tags=["geo"])


@router.get("/geo/provinces", response_class=Response)
def provinces_geojson(request: Request, db: Session = Depends(get_db)) -> Response:
    """Provincias como GeoJSON (WGS84). Con ETag para no reenviar lo que no cambió."""
    rows = db.execute(
        select(Jurisdiction, func.ST_AsGeoJSON(Jurisdiction.geom, 5))
        .where(Jurisdiction.kind == "province", Jurisdiction.geom.is_not(None))
        .order_by(Jurisdiction.id)
    ).all()
    collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": j.slug,
                "properties": {
                    "slug": j.slug,
                    "iso_code": j.iso_code,
                    "name": j.name,
                    "short_name": j.short_name,
                    "region": j.region,
                },
                "geometry": json.loads(geojson),
            }
            for j, geojson in rows
        ],
    }
    body = json.dumps(collection, separators=(",", ":"), ensure_ascii=False).encode()
    etag = f'"{hashlib.sha256(body).hexdigest()[:16]}"'
    headers = {"ETag": etag, "Cache-Control": "private, max-age=300"}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(body, media_type="application/geo+json", headers=headers)


@router.get("/locate", response_model=LocateOut)
def locate(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    db: Session = Depends(get_db),
) -> LocateOut:
    """¿En qué provincia cae un punto? Pensado para el widget móvil (GPS)."""
    point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
    jurisdiction = db.scalar(
        select(Jurisdiction)
        .where(Jurisdiction.kind == "province", func.ST_Intersects(Jurisdiction.geom, point))
        .order_by(Jurisdiction.id)
        .limit(1)
    )
    if jurisdiction is None:
        raise HTTPException(404, "El punto no cae dentro de ninguna provincia argentina.")
    return LocateOut(jurisdiction=JurisdictionOut.model_validate(jurisdiction, from_attributes=True))

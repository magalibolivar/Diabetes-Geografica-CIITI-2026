"""Indicadores de contexto (NBI, pobreza, cobertura, densidad).

Estas cifras se generaron con `src/05_build_argentina.py` (a partir de planillas del INDEC)
y viven en `data/processed/enfr2018_provincias.csv`. Las fuentes no publican CV ni marca
de confiabilidad comparables, así que `reliability` queda en NULL (= no evaluada).
Cada columna se carga como su propio dataset, con su propio período y su propia fuente.
"""

import csv
from decimal import Decimal
from pathlib import Path

from mapa import catalog
from mapa.etl.raw import RawObservation

FILENAME = Path("processed") / "enfr2018_provincias.csv"


def read_csv_rows(source_dir: Path) -> list[dict[str, str]]:
    path = source_dir / FILENAME
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra {path}")
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def parse_context(source_dir: Path, dataset_slug: str) -> list[RawObservation]:
    columns = [c for c, (ds, _) in catalog.CONTEXT_COLUMNS.items() if ds == dataset_slug]
    if len(columns) != 1:
        raise ValueError(f"{dataset_slug} no es un dataset de contexto")
    column = columns[0]
    _, indicator = catalog.CONTEXT_COLUMNS[column]
    period = catalog.DATASET_BY_SLUG[dataset_slug].reference_period

    observations = []
    for row in read_csv_rows(source_dir):
        jurisdiction = catalog.BY_SHORT[row["provincia"]]
        observations.append(
            RawObservation(
                jurisdiction=jurisdiction.slug,
                indicator=indicator,
                period=period,
                # Redondeo a 2 decimales: el CSV arrastra ruido de punto flotante (8.140961...).
                value=Decimal(row[column]).quantize(Decimal("0.01")),
            )
        )
    if len(observations) != len(catalog.PROVINCES):
        raise ValueError(f"{dataset_slug}: se esperaban 24 provincias, hay {len(observations)}")
    return observations

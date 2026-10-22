"""NBI 2022: porcentaje de hogares calculado de los conteos del Cuadro 2 del INDEC."""

import csv
from decimal import Decimal
from pathlib import Path

from mapa import catalog
from mapa.etl.raw import RawObservation

FILENAME = Path("processed") / "nbi_2022_hogares.csv"


def parse_nbi_2022(source_dir: Path) -> list[RawObservation]:
    path = source_dir / FILENAME
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra {path}")
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    expected = {jurisdiction.slug for jurisdiction in catalog.JURISDICTIONS}
    observed = [row["jurisdiction"] for row in rows]
    if len(observed) != len(expected) or set(observed) != expected:
        raise ValueError("NBI 2022 requiere 24 provincias y el total del país, sin duplicados")

    counts: dict[str, tuple[int, int]] = {}
    for row in rows:
        households = int(row["households"])
        with_nbi = int(row["with_nbi"])
        if households <= 0 or with_nbi < 0 or with_nbi > households:
            raise ValueError(f"Conteos NBI 2022 inválidos: {row['jurisdiction']}")
        counts[row["jurisdiction"]] = households, with_nbi

    provinces = [jurisdiction.slug for jurisdiction in catalog.PROVINCES]
    for index in (0, 1):
        if sum(counts[slug][index] for slug in provinces) != counts["argentina"][index]:
            raise ValueError("NBI 2022: los conteos provinciales no suman el total nacional")

    return [
        RawObservation(
            jurisdiction=slug,
            indicator="nbi_households",
            period="2022",
            value=(Decimal(with_nbi) * 100 / Decimal(households)).quantize(Decimal("0.1")),
        )
        for slug, (households, with_nbi) in counts.items()
    ]

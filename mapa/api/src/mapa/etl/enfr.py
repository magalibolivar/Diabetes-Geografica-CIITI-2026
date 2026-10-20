"""Lector de los cuadros oficiales de la ENFR 2018 (.xls del INDEC).

Cada hoja «Cuadro X.Y» trae, por jurisdicción: valor (%), CV y, a veces, una marca
(1) o (2) en una columna aparte. Esa marca es la evaluación de confiabilidad del propio
INDEC; la conservamos tal cual en lugar de inventar un umbral propio.
"""

from decimal import Decimal
from pathlib import Path

import xlrd

from mapa import catalog
from mapa.etl.raw import RawObservation

FILENAME = "cuadros_definitivos_enfr_2018.xls"
FLAGS = {"(1)": "caution", "(2)": "unreliable"}
TOTAL_ROW = "Total"
FIRST_DATA_ROW = 5  # fila 0-based del "Total"; las provincias empiezan más abajo
COUNTRY = next(j for j in catalog.JURISDICTIONS if j.kind == "country")


class EnfrParseError(ValueError):
    pass


def _decimal(cell: object) -> Decimal | None:
    text = str(cell).strip()
    if not text:
        return None
    return Decimal(text)


def _parse_sheet(sheet: xlrd.sheet.Sheet, indicator: str, period: str) -> list[RawObservation]:
    found: dict[str, RawObservation] = {}
    for r in range(FIRST_DATA_ROW, sheet.nrows):
        # Algunas hojas usan espacios no separables (p. ej. «Buenos\xa0Aires»).
        label = " ".join(str(sheet.cell_value(r, 0)).split())
        if label == TOTAL_ROW:
            jurisdiction = COUNTRY
        elif label in catalog.BY_SHORT and catalog.BY_SHORT[label].kind == "province":
            jurisdiction = catalog.BY_SHORT[label]
        else:
            continue  # regiones, pies de página, filas vacías

        value = _decimal(sheet.cell_value(r, 1))
        if value is None:
            raise EnfrParseError(f"{sheet.name}: fila '{label}' sin valor")
        cv = _decimal(sheet.cell_value(r, 2))
        flag = str(sheet.cell_value(r, 3)).strip() if sheet.ncols > 3 else ""
        if flag and flag not in FLAGS:
            raise EnfrParseError(f"{sheet.name}: marca desconocida {flag!r} en '{label}'")

        found[jurisdiction.slug] = RawObservation(
            jurisdiction=jurisdiction.slug,
            indicator=indicator,
            period=period,
            value=value,
            cv=cv,
            reliability=FLAGS.get(flag, "ok"),
        )

    expected = {j.slug for j in catalog.JURISDICTIONS}
    if set(found) != expected:
        raise EnfrParseError(
            f"{sheet.name}: jurisdicciones faltantes {sorted(expected - set(found))} "
            f"o inesperadas {sorted(set(found) - expected)}"
        )
    return list(found.values())


def parse_enfr(source_dir: Path) -> list[RawObservation]:
    path = source_dir / FILENAME
    if not path.exists():
        raise FileNotFoundError(f"No se encuentra {path}")
    workbook = xlrd.open_workbook(path)
    period = catalog.DATASET_BY_SLUG["enfr-2018"].reference_period

    observations: list[RawObservation] = []
    for link in catalog.DATASET_INDICATORS:
        if link.dataset_slug != "enfr-2018":
            continue
        sheet = workbook.sheet_by_name(link.source_ref)
        observations.extend(_parse_sheet(sheet, link.indicator_slug, period))
    return observations

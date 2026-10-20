"""Verificación cruzada: lo que leemos del .xls oficial debe coincidir con el CSV que ya
validó el equipo (data/processed/enfr2018_provincias.csv). Si alguna vez difieren, falla
ruidosamente en lugar de publicar un número distinto del que figura en el paper."""

from decimal import Decimal
from pathlib import Path

from mapa import catalog
from mapa.etl import context, enfr


def cross_check_enfr(source_dir: Path) -> list[str]:
    parsed = {(o.jurisdiction, o.indicator): o for o in enfr.parse_enfr(source_dir)}
    problems: list[str] = []
    for row in context.read_csv_rows(source_dir):
        jurisdiction = catalog.BY_SHORT[row["provincia"]]
        for column, indicator in catalog.ENFR_CSV_COLUMNS.items():
            from_xls = parsed[(jurisdiction.slug, indicator)].value
            from_csv = Decimal(row[column])
            if from_xls != from_csv:
                problems.append(
                    f"{row['provincia']} / {indicator}: xls={from_xls} csv={from_csv}"
                )
        # El CSV conserva el CV sólo de la prevalencia de diabetes.
        cv_xls = parsed[(jurisdiction.slug, "diabetes_prevalence")].cv
        if cv_xls != Decimal(row["cv_diabetes_pct"]):
            problems.append(f"{row['provincia']} / cv diabetes: xls={cv_xls} csv={row['cv_diabetes_pct']}")
    return problems

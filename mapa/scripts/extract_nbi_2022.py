"""Extrae conteos de hogares NBI 2022 del Cuadro 2 oficial, sin tocar el libro fuente.

Ejecutar desde la raíz del repositorio con Python y openpyxl (requirements.txt):
    python mapa/scripts/extract_nbi_2022.py
"""

import csv
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "serie_nbi_2022.xlsx"
OUTPUT = ROOT / "data" / "processed" / "nbi_2022_hogares.csv"

NAMES = {
    "Total del país": "argentina",
    "Ciudad Autónoma de Buenos Aires": "caba",
    "Buenos Aires": "buenos-aires",
    "Catamarca": "catamarca",
    "Córdoba": "cordoba",
    "Corrientes": "corrientes",
    "Chaco": "chaco",
    "Chubut": "chubut",
    "Entre Ríos": "entre-rios",
    "Formosa": "formosa",
    "Jujuy": "jujuy",
    "La Pampa": "la-pampa",
    "La Rioja": "la-rioja",
    "Mendoza": "mendoza",
    "Misiones": "misiones",
    "Neuquén": "neuquen",
    "Río Negro": "rio-negro",
    "Salta": "salta",
    "San Juan": "san-juan",
    "San Luis": "san-luis",
    "Santa Cruz": "santa-cruz",
    "Santa Fe": "santa-fe",
    "Santiago del Estero": "santiago-del-estero",
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur": "tierra-del-fuego",
    "Tucumán": "tucuman",
}


def extract() -> list[dict[str, int | str]]:
    workbook = load_workbook(SOURCE, read_only=True, data_only=True)
    counts = workbook["NBI_Hogares"]
    published = workbook["NBI_Hogares%"]
    rows = []
    for row in list(counts.values)[5:32]:
        name = str(row[0]).strip()
        if name not in NAMES:  # desgloses del GBA y del interior bonaerense
            continue
        households, with_nbi = row[10], row[11]
        if not isinstance(households, int) or not isinstance(with_nbi, int):
            raise ValueError(f"Conteos inválidos para {name}")
        rows.append({"jurisdiction": NAMES[name], "households": households, "with_nbi": with_nbi})

    if len(rows) != 25 or {r["jurisdiction"] for r in rows} != set(NAMES.values()):
        raise ValueError("Se esperaban 24 jurisdicciones y el total del país")
    country = next(r for r in rows if r["jurisdiction"] == "argentina")
    provinces = [r for r in rows if r["jurisdiction"] != "argentina"]
    for field in ("households", "with_nbi"):
        if sum(r[field] for r in provinces) != country[field]:
            raise ValueError(f"Los conteos provinciales no suman el total: {field}")

    published_by_name = {str(row[0]).strip(): row[9] for row in published.values if row[0]}
    by_slug = {r["jurisdiction"]: r for r in rows}
    for name, slug in NAMES.items():
        row = by_slug[slug]
        expected = published_by_name[name]
        if round(100 * row["with_nbi"] / row["households"], 1) != expected:
            raise ValueError(f"El porcentaje difiere del Cuadro 3: {name}")
    return rows


if __name__ == "__main__":
    if OUTPUT.exists():
        raise SystemExit(f"El archivo derivado ya existe; no se sobrescribe: {OUTPUT}")
    rows = extract()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["jurisdiction", "households", "with_nbi"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{OUTPUT}: 24 provincias y total del país verificados")

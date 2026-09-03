# -*- coding: utf-8 -*-
"""
02 - Construye el dataset global por pais (incluye Argentina).

Une la prevalencia de diabetes por pais (IDF / Our World in Data, 2024 -> archivo
data/raw/diabetes-prevalence.csv) con indicadores socioeconomicos del World Bank
descargados en linea via su API. Salida: data/processed/global_paises.csv
"""
from pathlib import Path
import json
import urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OWID = ROOT / "data" / "raw" / "diabetes-prevalence.csv"
OUT = ROOT / "data" / "processed" / "global_paises.csv"

WB_INDICADORES = {
    "poblacion_rural_pct": "SP.RUR.TOTL.ZS",
    "gasto_bolsillo_salud_pct": "SH.XPD.OOPC.CH.ZS",
    "pib_per_capita_usd": "NY.GDP.PCAP.CD",
    "poblacion_65mas_pct": "SP.POP.65UP.TO.ZS",
}
FEATS = list(WB_INDICADORES)


def wb(code):
    url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=400&mrnev=1"
    with urllib.request.urlopen(url, timeout=90) as r:
        j = json.load(r)
    d = {}
    for row in (j[1] or []):
        iso, val = row.get("countryiso3code"), row.get("value")
        if iso and val is not None:
            d[iso] = val
    return d


def main():
    owid = pd.read_csv(OWID)
    owid = owid[owid.Year == 2024][["Entity", "Code",
              "Diabetes prevalence (% of population ages 20 to 79)"]]
    owid.columns = ["pais", "iso3", "prevalencia_diabetes_pct"]
    owid = owid[owid.iso3.notna() & (owid.iso3.str.len() == 3)]

    df = owid.copy()
    for name, code in WB_INDICADORES.items():
        print(f"Descargando World Bank {code} ...")
        df[name] = df.iso3.map(wb(code))

    df = df.dropna(subset=["prevalencia_diabetes_pct"] + FEATS).reset_index(drop=True)
    df["pib_per_capita_usd"] = df["pib_per_capita_usd"].round(0)
    for c in ["prevalencia_diabetes_pct", "poblacion_rural_pct",
              "gasto_bolsillo_salud_pct", "poblacion_65mas_pct"]:
        df[c] = df[c].round(2)
    df = df.sort_values("pais").reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"OK -> {OUT}  ({len(df)} paises)")
    a = df[df.iso3 == "ARG"]
    if len(a):
        print("Argentina:", a.iloc[0].to_dict())


if __name__ == "__main__":
    main()

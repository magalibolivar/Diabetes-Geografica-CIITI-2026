# -*- coding: utf-8 -*-
"""
02 - Construye los datasets globales (incluye Argentina).

Genera cuatro tablas procesadas:
  - global_paises.csv          : prevalencia 2024 + prevalencia 2011 + cambio +
                                 indicadores World Bank (por país, N=193).
  - idf_carga_paises.csv       : número absoluto de adultos con diabetes por país
                                 (IDF Atlas 2024, en miles).
  - idf_totales_globales.csv   : totales mundiales 2000/2011/2024/2050 (IDF).
  - ncdrisc_mundo_tendencia.csv: prevalencia mundial (18+) y % tratados (30+) por
                                 sexo, 1990–2022 (NCD-RisC, The Lancet 2024).

Fuentes crudas en data/raw/. Los indicadores del World Bank se bajan por API.
"""
from pathlib import Path
import json
import urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

WB_INDICADORES = {
    "poblacion_rural_pct": "SP.RUR.TOTL.ZS",
    "gasto_bolsillo_salud_pct": "SH.XPD.OOPC.CH.ZS",
    "pib_per_capita_usd": "NY.GDP.PCAP.CD",
    "poblacion_65mas_pct": "SP.POP.65UP.TO.ZS",
}
FEATS = list(WB_INDICADORES)

# Agregados regionales del IDF que NO son países (a excluir del ranking por país)
IDF_REGIONES = {"World", "Africa", "Europe", "North America and Caribbean",
    "South and Central America", "South-East Asia", "Western Pacific",
    "Middle East and North Africa"}


def wb(code):
    url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=400&mrnev=1"
    with urllib.request.urlopen(url, timeout=90) as r:
        j = json.load(r)
    return {row["countryiso3code"]: row["value"] for row in (j[1] or [])
            if row.get("countryiso3code") and row.get("value") is not None}


def build_paises():
    owid = pd.read_csv(RAW / "diabetes-prevalence.csv")
    col = "Diabetes prevalence (% of population ages 20 to 79)"
    p24 = owid[owid.Year == 2024][["Entity", "Code", col]].rename(
        columns={"Entity": "pais", "Code": "iso3", col: "prevalencia_diabetes_pct"})
    p11 = owid[owid.Year == 2011][["Code", col]].rename(
        columns={"Code": "iso3", col: "prevalencia_2011_pct"})
    df = p24[p24.iso3.notna() & (p24.iso3.str.len() == 3)].merge(p11, on="iso3", how="left")
    for name, code in WB_INDICADORES.items():
        print(f"Descargando World Bank {code} ...")
        df[name] = df.iso3.map(wb(code))
    df = df.dropna(subset=["prevalencia_diabetes_pct"] + FEATS).reset_index(drop=True)
    df["cambio_2011_2024_pp"] = (df.prevalencia_diabetes_pct - df.prevalencia_2011_pct).round(2)
    df["pib_per_capita_usd"] = df["pib_per_capita_usd"].round(0)
    for c in ["prevalencia_diabetes_pct", "prevalencia_2011_pct", "poblacion_rural_pct",
              "gasto_bolsillo_salud_pct", "poblacion_65mas_pct"]:
        df[c] = df[c].round(2)
    df = df.sort_values("pais").reset_index(drop=True)
    df.to_csv(PROC / "global_paises.csv", index=False)
    print(f"OK global_paises.csv ({len(df)} países)")
    a = df[df.iso3 == "ARG"]
    if len(a):
        r = a.iloc[0]
        print(f"  Argentina: 2011={r.prevalencia_2011_pct}%  2024={r.prevalencia_diabetes_pct}%  "
              f"cambio={r.cambio_2011_2024_pp} pp")


def build_carga():
    e = pd.read_csv(RAW / "idf_total_adultos_diabetes_2024.csv")
    e = e.rename(columns={"Location": "pais", "Value": "adultos_con_diabetes_miles"})
    paises = e[~e.pais.isin(IDF_REGIONES)].copy()
    paises = paises.sort_values("adultos_con_diabetes_miles", ascending=False).reset_index(drop=True)
    paises["millones"] = (paises.adultos_con_diabetes_miles / 1000).round(2)
    paises.to_csv(PROC / "idf_carga_paises.csv", index=False)
    print(f"OK idf_carga_paises.csv ({len(paises)} países)")
    a = paises[paises.pais == "Argentina"]
    if len(a):
        rank = paises.index[paises.pais == "Argentina"][0] + 1
        print(f"  Argentina: {a.millones.values[0]} millones de adultos (puesto #{rank})")


def build_totales():
    g = pd.read_excel(RAW / "idf_global_table.xlsx")
    years = [int(float(g.iloc[0, j])) for j in range(1, 5)]
    fila = g[g.iloc[:, 0].astype(str).str.contains("People with diabetes", na=False)].iloc[0]
    vals = [float(fila.iloc[j]) for j in range(1, 5)]
    out = pd.DataFrame({"anio": years, "personas_con_diabetes_miles": vals})
    out["millones"] = (out.personas_con_diabetes_miles / 1000).round(1)
    out.to_csv(PROC / "idf_totales_globales.csv", index=False)
    print(f"OK idf_totales_globales.csv ({out.anio.tolist()})")


def build_ncdrisc():
    d = pd.read_csv(RAW / "ncdrisc_mundo_age_standardised.csv")
    prev = "Prevalence of diabetes (18+ years)"
    trat = "Proportion of people with diabetes who were treated (30+ years)"
    out = d[["Sex", "Year", prev, trat]].rename(columns={
        "Sex": "sexo", "Year": "anio",
        prev: "prevalencia_18mas", trat: "proporcion_tratados_30mas"})
    out["prevalencia_18mas_pct"] = (out.prevalencia_18mas * 100).round(2)
    out["tratados_pct"] = (out.proporcion_tratados_30mas * 100).round(2)
    out = out[["sexo", "anio", "prevalencia_18mas_pct", "tratados_pct"]]
    out.to_csv(PROC / "ncdrisc_mundo_tendencia.csv", index=False)
    print(f"OK ncdrisc_mundo_tendencia.csv ({out.anio.min()}–{out.anio.max()})")


def main():
    build_paises()
    build_carga()
    build_totales()
    build_ncdrisc()


if __name__ == "__main__":
    main()

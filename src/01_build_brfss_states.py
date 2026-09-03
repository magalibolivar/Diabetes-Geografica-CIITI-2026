# -*- coding: utf-8 -*-
"""
01 - Construye el dataset estado-nivel de EE.UU. a partir de los microdatos crudos
del CDC BRFSS 2015 (archivo de ancho fijo LLCP2015.ASC, ~441.456 encuestados).

Extrae las variables usando las posiciones del codebook oficial y agrega cada
indicador a nivel estatal mediante PROMEDIOS PONDERADOS por el peso muestral
final (_LLCPWT). Salida: data/processed/brfss2015_estados.csv (51 jurisdicciones).

El archivo LLCP2015.ASC (909 MB) NO se incluye en el repositorio. Descargarlo de:
  https://www.cdc.gov/brfss/annual_data/annual_2015.html  (LLCP 2015 ASCII)
y ubicarlo en la ruta indicada por la variable de entorno BRFSS_ASC, o en
  <repo>/../Dataset/LLCP2015.ASC   (ubicacion por defecto).
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ASC = Path(os.environ.get("BRFSS_ASC", ROOT.parent / "Dataset" / "LLCP2015.ASC"))
OUT = ROOT / "data" / "processed" / "brfss2015_estados.csv"

# Posiciones 1-based (inicio, fin) segun el codebook LLCP 2015
POS = dict(state=(1, 2), hlthpln1=(97, 97), medcost=(99, 99), diabete3=(117, 117),
           educa=(158, 158), income2=(175, 176), mscode=(1406, 1406),
           llcpwt=(1746, 1755), bmi5=(1988, 1991), totinda=(2058, 2058))

FIPS = {1:"Alabama",2:"Alaska",4:"Arizona",5:"Arkansas",6:"California",8:"Colorado",
9:"Connecticut",10:"Delaware",11:"District of Columbia",12:"Florida",13:"Georgia",
15:"Hawaii",16:"Idaho",17:"Illinois",18:"Indiana",19:"Iowa",20:"Kansas",21:"Kentucky",
22:"Louisiana",23:"Maine",24:"Maryland",25:"Massachusetts",26:"Michigan",27:"Minnesota",
28:"Mississippi",29:"Missouri",30:"Montana",31:"Nebraska",32:"Nevada",33:"New Hampshire",
34:"New Jersey",35:"New Mexico",36:"New York",37:"North Carolina",38:"North Dakota",
39:"Ohio",40:"Oklahoma",41:"Oregon",42:"Pennsylvania",44:"Rhode Island",
45:"South Carolina",46:"South Dakota",47:"Tennessee",48:"Texas",49:"Utah",50:"Vermont",
51:"Virginia",53:"Washington",54:"West Virginia",55:"Wisconsin",56:"Wyoming"}


def cut(line, a, b):
    return line[a - 1:b].strip()


def main():
    if not ASC.exists():
        raise SystemExit(f"No se encontro el ASC crudo en: {ASC}\n"
                         f"Descargalo del CDC y defini BRFSS_ASC o ubicalo en esa ruta.")
    print(f"Leyendo {ASC} ...")
    rows = []
    with open(ASC, encoding="latin-1") as f:
        for l in f:
            rows.append({k: cut(l, *v) for k, v in POS.items()})
    df = pd.DataFrame(rows)
    for c in ["hlthpln1", "medcost", "diabete3", "educa", "income2", "mscode", "totinda", "bmi5"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["llcpwt"] = pd.to_numeric(df["llcpwt"], errors="coerce")
    df["bmi"] = df["bmi5"] / 100.0
    df["fips"] = pd.to_numeric(df["state"], errors="coerce").astype("Int64")
    df = df[df.fips.isin(FIPS.keys())].copy()
    print(f"Registros validos (50 estados + DC): {len(df):,}")

    w = "llcpwt"
    recs = []
    for fips, g in df.groupby("fips"):
        def wm(valid, cond):
            gg = g[valid]
            if gg[w].sum() == 0:
                return np.nan
            return float(np.average(cond[valid].astype(float), weights=gg[w]))
        recs.append(dict(
            fips=int(fips), estado=FIPS[int(fips)], n=int(len(g)),
            tasa_diabetes_pct=round(100 * wm(g.diabete3.isin([1, 3, 4]), g.diabete3 == 1), 2),
            indice_ruralidad=round(wm(g.mscode.isin([1, 2, 3, 5]), g.mscode == 5), 3),
            sin_cobertura_salud_pct=round(100 * wm(g.hlthpln1.isin([1, 2]), g.hlthpln1 == 2), 2),
            secundario_incompleto_pct=round(100 * wm(g.educa.isin(range(1, 7)), g.educa <= 3), 2),
            barrera_costo_medico_pct=round(100 * wm(g.medcost.isin([1, 2]), g.medcost == 1), 2),
            obesidad_pct=round(100 * wm(g.bmi.notna(), g.bmi >= 30), 2),
            inactividad_fisica_pct=round(100 * wm(g.totinda.isin([1, 2]), g.totinda == 2), 2),
            pobreza_ingresos_pct=round(100 * wm(g.income2.isin(range(1, 9)), g.income2 <= 3), 2),
        ))
    out = pd.DataFrame(recs).sort_values("estado").reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"OK -> {OUT}  ({len(out)} estados)")
    print(f"Prevalencia nacional (prom. estados): {out.tasa_diabetes_pct.mean():.2f}% "
          f"| rango {out.tasa_diabetes_pct.min()}–{out.tasa_diabetes_pct.max()}")


if __name__ == "__main__":
    main()

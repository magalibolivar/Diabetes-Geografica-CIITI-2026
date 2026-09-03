# Determinantes geoespaciales y sociodemográficos de la diabetes

Pipeline reproducible de ciencia de datos que cuantifica, **con datos reales**, cómo los
determinantes sociales, económicos y del entorno explican la variación geográfica de la
prevalencia de diabetes, en dos escalas:

- **Subnacional (EE.UU.):** microdatos del CDC **BRFSS 2015** (441.456 encuestados) agregados,
  ponderados por peso muestral, a las 51 jurisdicciones. → *OLS R²=0,91 · Random Forest R²(CV)=0,81.*
- **Global (por país, incluye Argentina):** prevalencia **IDF / Our World in Data (2024)** +
  indicadores del **World Bank** para 193 países. → *la "paradoja de la diabetes" (R²=0,10).*
- **Carga, evolución y tratamiento:** número absoluto de adultos con diabetes por país (**IDF Atlas**,
  Argentina = 4,3 M), cambio de prevalencia **2011→2024** (Argentina +8,5 pp) y brecha de tratamiento
  mundial 1990–2022 (**NCD-RisC**, The Lancet 2024): la prevalencia se duplicó pero solo ~40% recibe tratamiento.

Trabajo del grupo CAETI — Universidad Abierta Interamericana (UAI).

## Estructura del repositorio

```
diabetes-geoespacial/
├── paper/        # Paper final (.docx, formato UAI/CAETI)
├── src/          # Scripts reproducibles (numerados por orden de ejecución)
├── data/
│   ├── raw/          # Datos crudos chicos versionables (OWID). El BRFSS crudo NO se versiona.
│   └── processed/    # Datasets finales estado-nivel y país-nivel (los que usa el análisis)
├── geo/          # Geometrías (GeoJSON) de estados de EE.UU. y países del mundo
├── figures/      # Figuras generadas (PNG)
└── tables/       # Tablas generadas (CSV)
```

## Cómo reproducir

```bash
pip install -r requirements.txt

# 1) (opcional) Reconstruir el dataset estatal desde el BRFSS crudo.
#    Requiere descargar LLCP2015.ASC del CDC (ver data/README.md) — 909 MB, NO versionado.
python src/01_build_brfss_states.py

# 2) (opcional) Reconstruir el dataset global (descarga indicadores del World Bank online).
python src/02_build_global.py

# 3) Ejecutar el análisis: genera todas las figuras y tablas.
python src/03_pipeline.py

# 4) Generar el paper .docx con los resultados.
python src/04_build_paper.py
```

Los pasos 1 y 2 son opcionales: `data/processed/` ya incluye los datasets finales, de modo que
los pasos 3 y 4 corren directamente.

## Fuentes de datos

- CDC BRFSS 2015 — https://www.cdc.gov/brfss/annual_data/annual_2015.html
- IDF Diabetes Atlas / Our World in Data — https://ourworldindata.org/grapher/diabetes-prevalence
- World Bank, World Development Indicators — https://data.worldbank.org

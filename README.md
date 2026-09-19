# Determinantes geoespaciales y sociodemográficos de la diabetes

Pipeline reproducible de ciencia de datos que cuantifica, **con datos reales**, cómo los
determinantes sociales, económicos y del entorno explican la variación geográfica de la
prevalencia de diabetes, en dos escalas:

- **Subnacional (Argentina - Rama flor):** microdatos oficiales de la 4ª **ENFR 2018** (24 jurisdicciones) cruzados con el **Censo 2010/2022** y la **EPH 2018** del INDEC. → *Atlas geoespacial, disparidad territorial en la brecha de tratamiento (32,7% a 70,0%) y diagnóstico metodológico sobre escala y potencia estadística en N=24.*
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
├── paper/        # Papers finales (.docx en formato CoNaIISI 2 col y estándar)
│   ├── Determinantes_Geoespaciales_Diabetes_Argentina_CONAIISI.docx
│   ├── Determinantes_Geoespaciales_Diabetes_Argentina.docx
│   ├── Determinantes_Geoespaciales_Diabetes_UAI_CONAIISI.docx
│   └── Determinantes_Geoespaciales_Diabetes_UAI.docx
├── src/          # Scripts reproducibles (numerados por orden de ejecución)
│   ├── 01_build_brfss_states.py
│   ├── 02_build_global.py
│   ├── 03_pipeline.py
│   ├── 04_build_paper.py
│   ├── 05_build_argentina.py
│   ├── 06_pipeline_argentina.py
│   └── 07_build_paper_argentina.py
├── data/
│   ├── raw/          # Datos crudos (ENFR 2018, Censo 2022, NBI, EPH, OWID)
│   └── processed/    # Datasets finales consolidados (enfr2018_provincias.csv, etc.)
├── geo/          # Geometrías (GeoJSON) de Argentina (24 provs), EE.UU. y mundo
├── figures/      # Figuras generadas en alta resolución (PNG)
└── tables/       # Tablas generadas (CSV)
```

## Cómo reproducir

```bash
pip install -r requirements.txt

# --- Análisis Nacional: Argentina (Opción A) ---
# 1) Construir el dataset consolidado de 24 provincias (ENFR + INDEC)
python src/05_build_argentina.py

# 2) Generar los mapas coropléticos, atlas de factores de riesgo y análisis de brecha
python src/06_pipeline_argentina.py

# 3) Compilar el paper completo en formato CoNaIISI y estándar (.docx)
python src/07_build_paper_argentina.py

# --- Análisis Previo: EE.UU. y Global ---
# python src/03_pipeline.py
# python src/04_build_paper.py
```

## Fuentes de datos

- INDEC / Ministerio de Salud — 4ª Encuesta Nacional de Factores de Riesgo (ENFR 2018)
- INDEC — Censo Nacional de Población, Hogares y Viviendas (2010 y 2022)
- INDEC — Encuesta Permanente de Hogares (EPH 2018)
- CDC BRFSS 2015 — https://www.cdc.gov/brfss/annual_data/annual_2015.html
- IDF Diabetes Atlas / Our World in Data — https://ourworldindata.org/grapher/diabetes-prevalence
- World Bank, World Development Indicators — https://data.worldbank.org


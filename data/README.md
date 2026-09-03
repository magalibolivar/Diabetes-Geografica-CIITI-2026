# Datos

## `processed/` — datasets finales (versionados)
- **`brfss2015_estados.csv`** — 51 jurisdicciones de EE.UU. con prevalencia de diabetes y
  determinantes, agregados y ponderados desde el BRFSS 2015. Lo genera `src/01_build_brfss_states.py`.
- **`global_paises.csv`** — 193 países con prevalencia de diabetes (IDF/OWID 2024) e indicadores
  del World Bank. Lo genera `src/02_build_global.py`.

## `raw/` — datos crudos
- **`diabetes-prevalence.csv`** — prevalencia por país (Our World in Data / IDF vía World Bank).
  Chico, versionado.
- **`LLCP2015.ASC`** — microdatos crudos del CDC BRFSS 2015 (**909 MB, NO versionado**).
  Descargar de https://www.cdc.gov/brfss/annual_data/annual_2015.html
  (sección *2015 BRFSS Data (ASCII)*), descomprimir y colocar aquí como `LLCP2015.ASC`,
  o apuntar la variable de entorno `BRFSS_ASC` a su ruta.

Los CSV curados de Kaggle/UCI ("CDC Diabetes Health Indicators") derivan del mismo BRFSS pero
**no conservan el estado**, por eso el análisis subnacional parte del ASC crudo.

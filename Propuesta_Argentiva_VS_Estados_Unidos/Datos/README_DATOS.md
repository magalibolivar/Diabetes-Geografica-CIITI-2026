# Diccionario de Datos, Provenance y Fuentes — Comparativa Argentina vs. Estados Unidos

Esta carpeta contiene los datasets procesados, las geometrías vectoriales y la trazabilidad completa (*data provenance*) de las fuentes crudas para el paper comparativo entre la República Argentina y los Estados Unidos.

---

## 1. Inventario y Trazabilidad de los Archivos Crudos en `data/`

En la carpeta raíz `data/` del repositorio se encuentran los archivos originales provistos por fuentes oficiales. A continuación se detalla **cuáles se utilizaron para construir el dataset de Argentina, qué datos se extrajeron de cada uno, y cuáles se descartaron justificadamente**:

| Archivo Crudo en `data/` | ¿Se usa en el Paper? | Rol y Variables Extraídas | Justificación / Nota Metodológica |
| :--- | :---: | :--- | :--- |
| **`cuadros_definitivos_enfr_2018.xls`** | **SÍ (Principal)** | • Diabetes autorreportada y medida (Cuadro 7.3)<br>• Coeficiente de variación (CV)<br>• Tratamiento farmacológico activo (Cuadro 7.5)<br>• Screening de glucemia alguna vez (Cuadro 7.1)<br>• Obesidad IMC $\ge 30$ (Cuadro 6.3)<br>• Inactividad física / sedentarismo (Cuadro 3.1)<br>• Presión arterial elevada (Cuadro 8.3)<br>• Colesterol elevado (Cuadro 9.3)<br>• Consumo de frutas/verduras (Cuadro 5.7) | Fuente epidemiológica primaria de la 4ª Encuesta Nacional de Factores de Riesgo (Secretaría de Gobierno de Salud / INDEC). Representatividad urbana para las 24 provincias. |
| **`c2022_tp_salud_c1.xlsx`** | **SÍ** | • Población sin cobertura formal de salud (`sin_cobertura_salud_pct`) | Datos del Censo Nacional 2022 (INDEC). Se tomó la hoja *"Cobertura de salud N°1"* excluyendo subtotales para obtener la población que depende exclusivamente del hospital público en cada provincia. |
| **`serie_nbi_2022.xlsx`** | **SÍ** | • Necesidades Básicas Insatisfechas en hogares (`nbi_2010_pct`) | Serie histórica de NBI del INDEC (hoja `NBI_Hogares_%_80_22`). Se tomó el relevamiento censal 2010 (último año con este estándar multidimensional). |
| **`cuadros_informe_pobreza_03_26.xls`** | **SÍ** | • Personas bajo la línea de pobreza monetaria (`pobreza_personas_pct`) | Informe técnico de la EPH (INDEC). Del Cuadro 4.3 se extrajo la pobreza del **2º semestre de 2018**, promediando los aglomerados a nivel provincial para sincronizar temporalmente con la ENFR 2018. |
| **`usu_hogar_T126.txt`** | **NO** | *Ninguno (Descartado)* | Microdatos crudos de hogares de la EPH correspondientes al **1º trimestre de 2026** (`ANO4=2026, TRIMESTRE=1`). Se descartaron porque usar pobreza de 2026 para predecir diabetes de 2018 violaría la validez temporal del estudio. |
| **`usu_individual_T126.txt`** | **NO** | *Ninguno (Descartado)* | Microdatos crudos individuales de la EPH de **2026**. Descartados por el mismo motivo de anacronismo temporal. |
| **`data/raw/`** | **SÍ (Contexto)** | • Prevalencia global IDF / Our World in Data (`diabetes-prevalence.csv`)<br>• Carga absoluta de pacientes (`idf_total_adultos_diabetes_2024.csv`)<br>• Tendencias mundiales de prevalencia y tratamiento 1990–2022 (`ncdrisc_mundo_age_standardised.csv`) | Series mundiales para situar a la Argentina y a EE.UU. en el contexto internacional de 193 países (*The Lancet* 2024). |
| **`data/processed/`** | **SÍ (Entrada)** | • Tablas consolidadas generadas por los scripts de construcción | Es el directorio consolidado del cual se nutren los pipelines. |

---

### Diagrama de Flujo del Procesamiento de Datos (Lineage)

```
FUENTES CRUDAS (data/)                                SCRIPT CONSTRUCTOR                           DATASET PROCESADO (Datos/)
┌──────────────────────────────────────┐
│ cuadros_definitivos_enfr_2018.xls    │ ───┐
└──────────────────────────────────────┘    │
┌──────────────────────────────────────┐    │
│ c2022_tp_salud_c1.xlsx               │ ───┤
└──────────────────────────────────────┘    │
┌──────────────────────────────────────┐    ├──►  src/05_build_argentina.py  ──►  Datos/enfr2018_provincias.csv
│ serie_nbi_2022.xlsx                  │ ───┤                                     (24 provincias x 17 variables)
└──────────────────────────────────────┘    │
┌──────────────────────────────────────┐    │
│ cuadros_informe_pobreza_03_26.xls    │ ───┘
└──────────────────────────────────────┘

CDC BRFSS 2015 (Microdatos 441k enc.)  ─────────►  src/01_build_brfss_states.py ──►  Datos/brfss2015_estados.csv
                                                                                   (51 estados x 11 variables)
```

---

## 2. Archivos Disponibles en esta Carpeta (`Propuesta_Argentiva_VS_Estados_Unidos/Datos/`)

| Archivo | Tipo | Cobertura | Filas / Entidades | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| [`enfr2018_provincias.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Datos/enfr2018_provincias.csv) | Tabla CSV | Argentina | 24 jurisdicciones (23 provs + CABA) | Microdatos consolidados de ENFR 2018 + Censo 2010/2022 + EPH 2018 |
| [`brfss2015_estados.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Datos/brfss2015_estados.csv) | Tabla CSV | Estados Unidos | 51 estados (50 estados + D.C.) | Microdatos del CDC BRFSS 2015 (441.456 encuestados con peso muestral) |
| [`argentina_provincias.geojson`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Datos/argentina_provincias.geojson) | Vector GeoJSON | Argentina | 24 geometrías provinciales | Límites vectoriales WGS84 para cartografía coroplética |
| [`us_states.geojson`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Datos/us_states.geojson) | Vector GeoJSON | Estados Unidos | 51 geometrías estatales | Límites vectoriales WGS84 para cartografía coroplética |
| [`c2022_tp_salud_c1.xlsx`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Datos/c2022_tp_salud_c1.xlsx) | Excel XLSX | Argentina | 24 provincias | Censo Nacional 2022: Cobertura de salud pública exclusiva |
| [`cuadros_definitivos_enfr_2018.xls`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Datos/cuadros_definitivos_enfr_2018.xls) | Excel XLS | Argentina | 24 provincias | 4° Encuesta Nacional de Factores de Riesgo (MSAL/INDEC) |
| [`cuadros_informe_pobreza_03_26.xls`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Datos/cuadros_informe_pobreza_03_26.xls) | Excel XLS | Argentina | 31 aglomerados | EPH INDEC: Incidencia de pobreza e indigencia urbana |
| [`serie_nbi_2022.xlsx`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Datos/serie_nbi_2022.xlsx) | Excel XLSX | Argentina | 24 provincias | Necesidades Básicas Insatisfechas (Censo INDEC) |

---

## 3. Diccionario de Variables — Argentina (`enfr2018_provincias.csv`)

Fuente base: INDEC y Secretaría de Gobierno de Salud (ENFR 2018), Censo Nacional 2010 y 2022 (INDEC), EPH 2018 (INDEC).

| Columna | Tipo | Rango / Unidad | Fuente Oficial | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `provincia` | Texto | 24 nombres | INDEC | Nombre oficial de la jurisdicción político-administrativa |
| `tasa_diabetes_pct` | Float | 8,8% – 17,3% | ENFR 2018 (Cuadro 7.3) | Prevalencia de diabetes autorreportada o glucemia elevada medida |
| `cv_diabetes_pct` | Float | 5,3% – 12,5% | ENFR 2018 (Cuadro 7.3) | Coeficiente de variación muestral de la tasa de diabetes (<15% es confiable) |
| `tratamiento_diabetes_pct` | Float | 32,7% – 70,0% | ENFR 2018 (Cuadro 7.5) | Porcentaje de personas con diabetes bajo tratamiento farmacológico activo |
| `medicion_glucemia_pct` | Float | 60,3% – 92,9% | ENFR 2018 (Cuadro 7.1) | Adultos que se midieron la glucemia alguna vez en la vida (screening) |
| `obesidad_pct` | Float | 17,0% – 34,4% | ENFR 2018 (Cuadro 6.3) | Adultos con IMC $\ge 30$ según peso y talla autorreportados |
| `inactividad_fisica_pct` | Float | 23,2% – 69,1% | ENFR 2018 (Cuadro 3.1) | Población con nivel bajo de actividad física (sedentarismo) |
| `presion_elevada_pct` | Float | 26,6% – 52,2% | ENFR 2018 (Cuadro 8.3) | Prevalencia de presión arterial elevada autorreportada |
| `colesterol_elevado_pct` | Float | 21,2% – 35,6% | ENFR 2018 (Cuadro 9.3) | Prevalencia de colesterol elevado autorreportado |
| `tabaquismo_pct` | Float | 14,9% – 26,7% | ENFR 2018 (Cuadro 2.1) | Consumo habitual de tabaco |
| `consumo_frutas_verduras_pct`| Float | 3,4% – 12,9% | ENFR 2018 (Cuadro 5.7) | Consumo de al menos 5 porciones diarias recomendadas |
| `nbi_2010_pct` | Float | 5,98% – 19,73% | Censo 2010 (INDEC) | Porcentaje de hogares con Necesidades Básicas Insatisfechas |
| `pobreza_personas_pct` | Float | 12,6% – 49,3% | EPH 2018 2º Sem (INDEC) | Personas por debajo de la línea de pobreza monetaria |
| `sin_cobertura_salud_pct` | Float | 16,3% – 55,9% | Censo 2022 (INDEC C1) | Personas que dependen exclusivamente del sistema público de salud |
| `densidad_hab_km2` | Float | 1,0 – 15.169,0 | Censo 2022 (INDEC) | Densidad poblacional corregida por superficie emergida efectiva |
| `log_densidad` | Float | 0,00 – 4,18 | Cálculo propio | $\log_{10}(\text{densidad})$ para linealizar la distribución espacial |
| `region` | Texto | 5 regiones | INDEC | Región geográfica: Pampeana y GBA, Cuyo, Noroeste, Noreste, Patagonia |

---

## 4. Diccionario de Variables — Estados Unidos (`brfss2015_estados.csv`)

Fuente base: Centers for Disease Control and Prevention (CDC) — Behavioral Risk Factor Surveillance System (BRFSS 2015). Microdatos de 441.456 encuestados agregados a nivel estatal aplicando el ponderador muestral `_LLCPWT`.

| Columna | Tipo | Rango / Unidad | Variable CDC | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `fips` | Entero | 1 – 56 | `_STATE` | Código geográfico federal FIPS del estado |
| `estado` | Texto | 51 nombres | — | Nombre oficial del estado de EE.UU. |
| `n` | Entero | 3.657 – 13.537 | Encuestados | Tamaño de muestra efectiva por estado |
| `tasa_diabetes_pct` | Float | 6,8% – 14,8% | `DIABETE3` | Prevalencia de diabetes diagnosticada ponderada |
| `obesidad_pct` | Float | 20,2% – 35,6% | `_BMI5CAT` | Porcentaje de adultos con índice de masa corporal IMC $\ge 30$ |
| `inactividad_fisica_pct` | Float | 17,9% – 34,2% | `_TOTINDA` | Adultos sin actividad física ni ejercicio regular en el mes previo |
| `pobreza_ingresos_pct` | Float | 12,8% – 26,6% | `INCOME2` | Adultos en hogares con ingresos menores a USD 25.000 anuales |
| `secundario_incompleto_pct`| Float | 8,2% – 18,4% | `_EDUCAG` | Adultos que no completaron la educación secundaria (High School) |
| `barrera_costo_medico_pct` | Float | 8,8% – 18,5% | `MEDCOST` | Adultos que no pudieron ver a un médico por barrera de costo |
| `sin_cobertura_salud_pct` | Float | 6,0% – 17,1% | `_HCVU651` | Adultos entre 18 y 64 años sin seguro de salud formal |
| `indice_ruralidad` | Float | 0,00 – 0,48 | USDA / ERS | Proporción de población residente en condados clasificados como rurales |

---

## 5. Equivalencias Metodológicas para la Comparación

Para garantizar que el contraste científico entre ambos países sea estadísticamente válido, se alinearon los indicadores conceptualmente idénticos:

| Dimensión Conceptual | Indicador en Argentina (ENFR / INDEC) | Indicador en EE.UU. (CDC BRFSS) |
| :--- | :--- | :--- |
| **Outcome principal** | `tasa_diabetes_pct` | `tasa_diabetes_pct` |
| **Nutrición / Masa Corporal** | `obesidad_pct` (IMC $\ge 30$) | `obesidad_pct` (IMC $\ge 30$) |
| **Sedentarismo** | `inactividad_fisica_pct` | `inactividad_fisica_pct` |
| **Privación Económica** | `pobreza_personas_pct` / `nbi_2010_pct` | `pobreza_ingresos_pct` |
| **Falta de Seguro Médico** | `sin_cobertura_salud_pct` (Censo 2022) | `sin_cobertura_salud_pct` (BRFSS) |
| **Distribución Territorial** | Geometrías de 24 provincias | Geometrías de 51 estados |

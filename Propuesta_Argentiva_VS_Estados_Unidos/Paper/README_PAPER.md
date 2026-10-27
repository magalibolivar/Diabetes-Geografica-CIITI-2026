# 📄 Manuscrito Científico Extenso: Argentina vs. Estados Unidos (CIITI 2026)
### *Determinantes geoespaciales de la diabetes tipo 2 en la Argentina y los Estados Unidos: Salud basada en datos, cobertura de tratamiento y límites del modelado predictivo*

**Autores:** María Florencia Rossi, Magali Bolivar, Matías Montiel, Roxana Martínez, Nestor Balich, Franco Balich  
**Afiliación:** CAETI — Centro de Altos Estudios en Tecnología Informática, Facultad de Tecnología Informática — Universidad Abierta Interamericana (UAI)  
**Destino:** XIV Congreso Internacional de Innovación y Tecnología Informática (CIITI 2026) / CoNaIISI  
**Repositorio Reproducible:** `https://github.com/florr/Diabetes-Geografica-CIITI-2026`

---

## 📌 1. Resumen Ejecutivo del Paper

Este artículo científico extenso formaliza un estudio comparativo transnacional entre los **51 estados de EE.UU.** (CDC BRFSS 2015, $N=441.456$ encuestados ponderados) y las **24 jurisdicciones de la República Argentina** (4ª ENFR 2018 integrada con los Censos Nacionales 2010/2022 y la EPH del INDEC, $N=29.224$ hogares urbanos).

### Hallazgos Principales (Calculados 100% desde el Motor Reproducible):
1. **Autocorrelación Espacial y Gradiente Socioeconómico:**
   * En **EE.UU.**, la prevalencia estatal (media $10,2\%$, $\text{DE } 1,8\%$) presenta un fuerte agrupamiento geográfico ($\text{Índice } I \text{ de Moran} = +0,59, p < 0,001$) en el *Cinturón de la Diabetes* y se asocia linealmente con los bajos ingresos ($r = +0,81, \text{IC95\% } [+0,69; +0,89], \rho = +0,80$) y la inactividad física ($r = +0,79$).
   * En **Argentina**, la prevalencia provincial declarada (media provincial $13,0\%$, $\text{DE muestral } 2,1\%$, $\text{DE poblacional } 2,06\%$, $\text{Var}(y) = 4,24$; media nacional ponderada $12,7\%$) exhibe una autocorrelación espacial moderada ($I \text{ de Moran} = +0,33, p = 0,039$) y no correlaciona linealmente con la pobreza monetaria EPH ($r = -0,05, \text{IC95\% } [-0,44; +0,36], \rho = -0,19$) ni con la falta de cobertura médica formal ($r = -0,16$).
2. **Detección (Screening), Outlier Urbano (CABA) y Factores Concurrentes:**
   * Junto con la estructura etaria provincial y el error muestral ($\text{CV} \le 12,5\%$), se constata una fuerte correlación negativa entre la pobreza estructural (NBI) y el acceso al screening glucémico ($r = -0,81, p < 0,001, \text{IC95\% } [-0,91; -0,60]$).
   * Al evaluar la relación entre screening y prevalencia declarada, la inclusión de **CABA** ($8,8\%$ de prevalencia con la menor obesidad del país, $17,0\%$, y el máximo screening, $92,9\%$) atenúa la correlación global ($r = +0,13$ en $N=24$); al excluir este outlier ($N=23$ provincias), el screening se asocia positivamente con la diabetes declarada ($r = +0,40, p = 0,057, \rho = +0,35$).
3. **Cobertura vs. Brecha de Tratamiento Farmacológico:**
   * En Argentina, la cobertura media provincial de tratamiento farmacológico activo entre personas diagnosticadas es del **$54,4\%$** (lo que implica una **brecha media de tratamiento del $45,6\%$**, con rango de cobertura de $32,7\%$ en La Pampa a $70,0\%$ en Santa Cruz y Tierra del Fuego).
   * No existe un gradiente regresivo entre carecer de obra social/prepaga y recibir tratamiento ($r = -0,11, p = 0,62$): las tres provincias con más del $50\%$ de población sin cobertura formal (**Santiago del Estero $56,0\%$**, **Formosa $55,9\%$** y **Chaco $52,2\%$**) alcanzan coberturas terapéuticas del **$59,7\%$**, **$62,6\%$** y **$54,2\%$** respectivamente (respaldadas por el Programa Remediar y la Ley 26.914 / PRODIABA).
4. **Evaluación Simétrica de Machine Learning (LOOCV y 5-Fold CV):**
   * En EE.UU. ($N=51$), OLS ($R^2 = 0,891$; $\text{LOOCV } R^2 = 0,859$), Ridge ($\text{LOOCV } R^2 = 0,858$) y Random Forest ($\text{5-Fold } R^2 = 0,802$) generalizan sólidamente fuera de muestra.
   * En Argentina ($N=24$), tanto OLS multivariado ($\text{LOOCV } R^2 = -0,701$), Ridge regularizado ($\text{LOOCV } R^2 = -0,311$), OLS parsimonioso con 1 predictor ($\text{LOOCV } R^2 = -0,100$) como Random Forest ($\text{LOOCV } R^2 = -0,657$; $\text{5-Fold } R^2 = -0,802$) rinden por debajo del estimador baseline de media constante ($R^2 = 0$).

---

## 📂 2. Archivos del Manuscrito en esta Carpeta

| Archivo | Formato | Descripción |
| :--- | :--- | :--- |
| 📄 [**`Paper_Comparativo_Argentina_USA_2026.docx`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Paper/Paper_Comparativo_Argentina_USA_2026.docx) | Word (`.docx`) | **Manuscrito final compilado** con plantilla oficial CoNaIISI / CIITI a doble columna, 5 figuras de 220 DPI incrustadas, 4 tablas formales y 25 referencias IEEE actualizadas (2022–2026), verificadas y 100% citadas en el texto. |
| 📝 [**`Paper_Comparativo_Argentina_USA.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Paper/Paper_Comparativo_Argentina_USA.md) | Markdown (`.md`) | Manuscrito completo estructurado en Markdown, generado automáticamente por el mismo motor para garantizar coincidencia del 100% con el `.docx`. |
| 📖 [**`README_PAPER.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Paper/README_PAPER.md) | Markdown | Este documento de especificación del paper. |

---

## 🔗 3. Vínculos a Figuras y Tablas (en `Resultados/`)

Las figuras y tablas generadas por el motor se encuentran centralizadas en [**`Resultados/`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados):

* **Figuras científicas (220 DPI):**
  * 🖼️ [**`Resultados/figura1_mapas_comparativos.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura1_mapas_comparativos.png) (Mapas coropléticos unificados e Índice $I$ de Moran)
  * 🖼️ [**`Resultados/figura2_factores_riesgo.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura2_factores_riesgo.png) (Obesidad e inactividad física / baja actividad IPAQ)
  * 🖼️ [**`Resultados/figura3_brecha_tratamiento.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura3_brecha_tratamiento.png) (Cobertura y brecha asistencial provincial vs. barrera de costo en EE.UU.)
  * 🖼️ [**`Resultados/figura4_matriz_correlaciones.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura4_matriz_correlaciones.png) (Matrices de calor de correlaciones de Pearson)
  * 🖼️ [**`Resultados/figura5_modelos_dispersion.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura5_modelos_dispersion.png) (Regresiones Pobreza vs. Diabetes con IC95% y NBI vs. Screening)
* **Tablas de datos:**
  * 📊 [**`Resultados/tabla1_resumen_comparativo.csv`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla1_resumen_comparativo.csv)
  * 📊 [**`Resultados/tabla2_ols_coeficientes.csv`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla2_ols_coeficientes.csv)
  * 📊 [**`Resultados/tabla3_diagnostico_modelos.csv`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla3_diagnostico_modelos.csv)
  * 📊 [**`Resultados/tabla4_ranking_extremos.csv`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla4_ranking_extremos.csv)

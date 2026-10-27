# 📈 Guía de Resultados, Tablas y Figuras — Comparativa Argentina vs. Estados Unidos
### *Determinantes geoespaciales de la diabetes tipo 2 en la Argentina y los Estados Unidos (CIITI 2026 / CoNaIISI)*

---

## 📌 1. Visión General de los Resultados

Esta carpeta reúne toda la **evidencia cuantitativa, tablas estadísticas formales y figuras cartográficas y analíticas de alta resolución (220 DPI)** generadas directamente por el motor reproducible ([`Pipeline/pipeline_comparativa_argentina_usa.py`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Pipeline/pipeline_comparativa_argentina_usa.py)).

Todas las cifras coinciden de forma exacta con el manuscrito en Markdown ([`Paper/Paper_Comparativo_Argentina_USA.md`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Paper/Paper_Comparativo_Argentina_USA.md)) y en Word ([`Paper/Paper_Comparativo_Argentina_USA_2026.docx`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Paper/Paper_Comparativo_Argentina_USA_2026.docx)).

---

## 📁 2. Inventario de Archivos en `Resultados/`

```
Propuesta_Argentiva_VS_Estados_Unidos/Resultados/
│
├── 📊 Tablas Estadísticas (.csv):
├── tabla1_resumen_comparativo.csv       <-- Comparación de medias, DE, Moran's I y cobertura (51 estados vs. 24 provs)
├── tabla2_ols_coeficientes.csv          <-- Regresiones OLS con errores robustos HC3, VIF y constructos explícitos
├── tabla3_diagnostico_modelos.csv       <-- Evaluación simétrica LOOCV y 5-Fold: OLS, Ridge, Univariado y Random Forest
├── tabla4_ranking_extremos.csv          <-- Jurisdicciones con mayor y menor prevalencia
├── tabla_comparativa_resumen.csv        <-- Síntesis consolidada con IC95% y correlaciones con/sin CABA
│
├── 🖼️ Figuras Científicas (220 DPI):
├── figura1_mapas_comparativos.png       <-- Mapas coropléticos unificados e Índice I de Moran
├── figura2_factores_riesgo.png          <-- Cartografía comparada de obesidad e inactividad física (tiempo libre vs IPAQ)
├── figura3_brecha_tratamiento.png       <-- Cobertura de tratamiento farmacológico en Arg vs. barrera de costo en EE.UU.
├── figura4_matriz_correlaciones.png     <-- Matrices de calor de Pearson cruzadas
├── figura5_modelos_dispersion.png       <-- Dispersión Pobreza vs. Diabetes (IC95%) y NBI vs. Screening (r = -0,81)
├── figura_comparativa_argentina_usa.png <-- Infografía comparativa global unificada
│
└── 📖 README_RESULTADOS.md              <-- Este documento explicativo
```

---

## 3. 📑 Detalle y Explicación de las Tablas Estadísticas

### A. Tabla 1: Resumen Comparativo General de Indicadores
📄 **Archivo:** [`tabla1_resumen_comparativo.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla1_resumen_comparativo.csv)

* **Prevalencia media de diabetes:**
  * **Argentina:** **$13,0\%$** media simple interprovincial ($\text{DE muestral } 2,1\%$; $\text{DE poblacional } 2,06\%$; $\text{Var}(y) = 4,24$) y **$12,7\%$** total nacional ponderado (rango: $8,8\%$ CABA a $17,3\%$ San Luis). Incluye diagnóstico autorreportado de *"diabetes o glucemia elevada"* (ENFR Cuadro 7.3).
  * **Estados Unidos:** **$10,2\%$** media estatal ($\text{DE } 1,8\%$; mediana $10,0\%$; rango: $6,8\%$ Colorado a $14,8\%$ Misisipi). Mide diabetes diagnosticada excluyendo prediabetes (`DIABETE3`).
* **Autocorrelación espacial ($\text{Índice } I \text{ de Moran}$):**
  * **EE.UU.:** **$I = +0,59$** ($p < 0,001$), confirmando un fuerte agrupamiento espacial en el *Cinturón de la Diabetes*.
  * **Argentina:** **$I = +0,33$** ($p = 0,039$), agrupamiento moderado concentrado en Cuyo y región pampeana occidental.
* **Inactividad física / Baja actividad física:**
  * **Argentina:** **$46,2\%$** media provincial ($45,9\%$ nacional) de baja actividad física medida con el cuestionario multidominio **IPAQ** (Cuadro 3.1).
  * **EE.UU.:** **$25,8\%$** media estatal ($23,8\%$ nacional) de ausencia de actividad física recreativa en el tiempo libre (`_TOTINDA`).
* **Cobertura de salud y Tratamiento farmacológico:**
  * **Población sin seguro médico formal:** En Argentina promedia el **$37,3\%$** provincial ($35,6\%$ nacional en Censo 2022); en EE.UU. promedia el **$11,0\%$** ($10,9\%$ nacional).
  * **Screening glucémico:** $>85\%$ en EE.UU. frente a una media de **$74,8\%$** en Argentina ($60,3\%$ en Chaco a $92,9\%$ en CABA).
  * **Cobertura de tratamiento farmacológico activo (y brecha):** En Argentina la cobertura activa promedia el **$54,4\%$** de los diagnosticados (lo que equivale a una **brecha media sin tratamiento del $45,6\%$**, oscilando entre $32,7\%$ de cobertura en La Pampa y $70,0\%$ en Santa Cruz y Tierra del Fuego).

---

### B. Tabla 2: Coeficientes de Regresión OLS Multivariada (Errores Robustos HC3 y VIF)
📄 **Archivo:** [`tabla2_ols_coeficientes.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla2_ols_coeficientes.csv)

1. **En Estados Unidos ($N=51$, $R^2 = 0,891$, $R^2_{\text{adj}} = 0,878$, $F = 73,7, p < 0,001$):**
   * **Obesidad ($\text{IMC} \ge 30$):** $\beta = +0,180$ ($p < 0,001$, $\text{VIF} = 2,2$).
   * **Inactividad en tiempo libre:** $\beta = +0,095$ ($p = 0,026$, $\text{VIF} = 2,5$).
   * **Bajos ingresos ($<\text{USD } 25\text{k}$):** $\beta = +0,137$ ($p = 0,004$, $\text{VIF} = 4,0$).
   * **Secundario incompleto:** $\beta = +0,202$ ($p = 0,001$, $\text{VIF} = 4,4$).
   * **Sin seguro (18–64 años):** $\beta = -0,096$ ($p = 0,006$, $\text{VIF} = 1,5$).
2. **En Argentina ($N=24$, $R^2 = 0,264$, $R^2_{\text{adj}} = 0,059$, $F = 1,29, p = 0,31$):**
   * Ningún predictor alcanza significancia estadística individual al $5\%$ (Obesidad $\beta = +0,053, p = 0,831$; Baja actividad IPAQ $\beta = -0,002, p = 0,983$; Pobreza EPH $\beta = +0,017, p = 0,888$; Sin obra social $\beta = -0,056, p = 0,555$; $\log_{10}(\text{Densidad})$ $\beta = -1,162, p = 0,397$).

---

### C. Tabla 3: Evaluación Simétrica de Modelos (LOOCV y 5-Fold CV en Ambos Países)
📄 **Archivo:** [`tabla3_diagnostico_modelos.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla3_diagnostico_modelos.csv)

* **Estimador Naive Baseline (Media constante $\bar{y}$):** $R^2 = 0,000$ ($\text{MAE} = 1,53\%$ en EE.UU.; $\text{MAE} = 1,59\%$ y $\text{Var}(y) = 4,24$ en Argentina).
* **OLS Multivariado (5 predictores, LOOCV / 5-Fold CV):**
  * **EE.UU.:** $R^2 = +0,859 \text{ / } +0,842$ ($\text{MAE} = 0,56\% \text{ / } 0,59\%$).
  * **Argentina:** $R^2 = -0,701 \text{ / } -1,294$ ($\text{MAE} = 2,12\% \text{ / } 2,43\%$). En LOOCV el $\text{MSE} = 7,21$ supera en un $70,1\%$ a la varianza base ($7,21 / 4,24 = 1,701$).
* **Regresión Regularizada Ridge ($\alpha = 10$, LOOCV / 5-Fold CV):**
  * **EE.UU.:** $R^2 = +0,858 \text{ / } +0,856$ ($\text{MAE} = 0,58\% \text{ / } 0,58\%$).
  * **Argentina:** $R^2 = -0,311 \text{ / } -0,429$ ($\text{MAE} = 1,87\% \text{ / } 1,97\%$).
* **OLS Parsimonioso Univariado (1 solo predictor: Obesidad, LOOCV / 5-Fold CV):**
  * **EE.UU.:** $R^2 = +0,532 \text{ / } +0,521$ ($\text{MAE} = 1,02\% \text{ / } 1,03\%$).
  * **Argentina:** $R^2 = -0,100 \text{ / } -0,023$ ($\text{MAE} = 1,58\% \text{ / } 1,56\%$).
* **Random Forest Regressor (LOOCV / 5-Fold CV):**
  * **EE.UU.:** $R^2 = +0,815 \text{ / } +0,802$ ($\text{MAE} = 0,67\% \text{ / } 0,66\%$).
  * **Argentina:** $R^2 = -0,657 \text{ / } -0,802$ ($\text{MAE} = 2,07\% \text{ / } 2,20\%$).

---

### D. Tabla 4: Ranking de Jurisdicciones Extremas
📄 **Archivo:** [`tabla4_ranking_extremos.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla4_ranking_extremos.csv)

* **Máximas en EE.UU.:** Misisipi ($14,8\%$, bajos ingresos $29,4\%$) y Virginia Occidental ($14,5\%$, bajos ingresos $23,5\%$).
* **Mínimas en EE.UU.:** Colorado ($6,8\%$, bajos ingresos $13,2\%$) y Utah ($7,1\%$, bajos ingresos $11,6\%$).
* **Máximas en Argentina:** San Luis ($17,3\%$, pobreza EPH $31,3\%$) y San Juan ($15,9\%$, pobreza EPH $33,1\%$, obesidad $34,4\%$).
* **Mínimas en Argentina:** CABA ($8,8\%$, menor obesidad $17,0\%$ y máximo screening $92,9\%$) y Jujuy ($8,9\%$, obesidad $31,1\%$ pero bajo screening $71,3\%$).

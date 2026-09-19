# 📈 Guía de Resultados, Tablas y Figuras — Comparativa Argentina vs. Estados Unidos
### *Determinantes geoespaciales de la diabetes tipo 2 en la Argentina y los Estados Unidos (CIITI 2026)*

---

## 📌 1. Visión General de los Resultados

Esta carpeta reúne toda la **evidencia cuantitativa, tablas estadísticas formales y figuras cartográficas y analíticas de alta resolución (220 DPI)** generadas por el pipeline científico para el **CIITI 2026 / CoNaIISI**.

Mientras que el texto del paper expone la argumentación teórica, aquí se centralizan los valores empíricos: correlaciones ($r$), coeficientes de regresión ($\beta$), diagnósticos de multicolinealidad (VIF) y validación cruzada de Machine Learning ($R^2$, LOOCV, MAE).

---

## 📁 2. Inventario de Archivos en `Resultados/`

```
Propuesta_Argentiva_VS_Estados_Unidos/Resultados/
│
├── 📊 Tablas Estadísticas (.csv):
├── tabla1_resumen_comparativo.csv       <-- Comparación de medias, medianas y rangos (51 estados vs. 24 provs)
├── tabla2_ols_coeficientes.csv          <-- Regresiones OLS con errores robustos HC3 y factores VIF
├── tabla3_diagnostico_modelos.csv       <-- Evaluación Machine Learning: OLS vs Random Forest y CV
├── tabla4_ranking_extremos.csv          <-- Jurisdicciones con mayor y menor prevalencia
├── tabla_comparativa_resumen.csv        <-- Síntesis consolidada de indicadores
│
├── 🖼️ Figuras Científicas (220 DPI):
├── figura1_mapas_comparativos.png       <-- Mapas coropléticos unificados de EE.UU. y Argentina
├── figura2_factores_riesgo.png          <-- Cartografía comparada de obesidad y sedentarismo
├── figura3_brecha_tratamiento.png       <-- Ranking horizontal de tratamiento farmacológico y barrera de costo
├── figura4_matriz_correlaciones.png     <-- Matrices de calor de Pearson cruzadas
├── figura5_modelos_dispersion.png       <-- Dispersión Pobreza vs. Diabetes y Screening vs. NBI
├── figura_comparativa_argentina_usa.png <-- Infografía comparativa global unificada
│
└── 📖 README_RESULTADOS.md              <-- Este documento explicativo
```

---

## 3. 📑 Detalle y Explicación de las Tablas Estadísticas

### A. Tabla 1: Resumen Comparativo General de Indicadores
📄 **Archivo:** [`tabla1_resumen_comparativo.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla1_resumen_comparativo.csv)

* **Prevalencia media de diabetes:**
  * **Argentina:** **12,7%** (con rango de 8,8% a 17,3%).
  * **Estados Unidos:** **10,2%** (con rango de 6,8% a 14,8%).
  * *Hallazgo:* Argentina presenta, en promedio poblacional, **mayor prevalencia que Estados Unidos**.
* **Sedentarismo (Inactividad física):**
  * **Argentina:** **45,9%** de los adultos es sedentario (en Formosa alcanza el 69,1%).
  * **EE.UU.:** **23,8%** promedio.
  * *Hallazgo:* El sedentarismo en Argentina casi duplica al de EE.UU.
* **Cobertura de salud:**
  * **Argentina:** El **35,6%** de la población depende exclusivamente del subsistema público gratuito (en el norte supera el 50-55%).
  * **EE.UU.:** Solo el **10,9%** carece de seguro médico formal.
* **Screening preventivo (Medición de glucemia en sangre):**
  * **EE.UU.:** Más del **85%** de la población se testea rutinariamente.
  * **Argentina:** Media del 74,8%, pero con una brecha crítica: CABA testea al **92,9%**, mientras que en Chaco o Santiago del Estero el **40% de los adultos nunca se midió la glucosa**.

---

### B. Tabla 2: Coeficientes de Regresión OLS Multivariada
📄 **Archivo:** [`tabla2_ols_coeficientes.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla2_ols_coeficientes.csv)

Aplica mínimos cuadrados ordinarios con **errores estándar robustos HC3**:
1. **En Estados Unidos (Relaciones lineales robustas):**
   * **Obesidad:** $\beta = +0,177$ ($p < 0,001$, VIF = 3,7).
   * **Pobreza de ingresos:** $\beta = +0,111$ ($p = 0,042$, VIF = 3,3). A mayor pobreza, mayor diabetes detectada.
   * **Barrera de costo médico:** $\beta = +0,257$ ($p = 0,008$, VIF = 2,4).
2. **En Argentina (Desacople por subdiagnóstico):**
   * **Pobreza:** $\beta = -0,047$ ($p = 0,55$, no significativo). La pobreza no predice más diabetes en la encuesta porque las provincias más pobres tienen menor acceso a screening y confirmación bioquímica.
   * **Prueba F conjunta:** $F = 1,84$ ($p = 0,16$, no significativo), comprobando matemáticamente los límites de transferir modelos de países centrales a periferias con subdiagnóstico.

---

### C. Tabla 3: Diagnóstico de Modelos y Machine Learning
📄 **Archivo:** [`tabla3_diagnostico_modelos.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla3_diagnostico_modelos.csv)

* **En Estados Unidos ($N=51$):**
  * OLS in-sample: $R^2 = \mathbf{0,912}$.
  * Random Forest en 5-Fold CV: $R^2 = \mathbf{0,806}$, $\text{MAE} = 0,59\%$. Los algoritmos generalizan sólidamente.
* **En Argentina ($N=24$):**
  * OLS in-sample: $R^2 = 0,385$.
  * Leave-One-Out CV: El $R^2$ colapsa a **$-0,291$ (negativo)**.
  * Random Forest en CV: Da **$-0,324$ (negativo)**.
  * *Aporte para el CIITI:* Un $R^2$ negativo demuestra que el algoritmo supervisado sobreajusta y falla más que predecir la media constante, justificando el enfoque analítico geoespacial descriptivo.

---

### D. Tabla 4: Ranking de Jurisdicciones Extremas
📄 **Archivo:** [`tabla4_ranking_extremos.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla4_ranking_extremos.csv)

* **Máximas en EE.UU.:** Misisipi (`14,8%`) y Virginia Occidental (`13,9%`) (Cinturón de la Diabetes del sur profundo).
* **Mínimas en EE.UU.:** Colorado (`6,8%`) y Utah (`7,5%`) (cultura de actividad al aire libre y bajo tabaquismo).
* **Máximas en Argentina:** San Luis (`17,3%`) y San Juan (`15,9%`) (Cuyo, alto sedentarismo).
* **Mínimas en Argentina:** CABA (`8,8%`, alta cobertura y screening) frente a Jujuy (`8,9%`) y Chaco (`10,3%`) (bajas por subdiagnóstico por falta de acceso a análisis clínicos).

---

## 4. 🖼️ Catálogo de Figuras Científicas (220 DPI)

* 🗺️ [**`figura1_mapas_comparativos.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura1_mapas_comparativos.png):  
  Cartografía coroplética bajo escala cromática continua común unificada, revelando la concentración del Diabetes Belt en EE.UU. frente al gradiente Cuyo-Patagonia en Argentina.
* ⚖️ [**`figura2_factores_riesgo.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura2_factores_riesgo.png):  
  Matriz de 4 mapas comparando la geografía de la obesidad adulta ($\text{IMC} \ge 30$) y el sedentarismo en ambas naciones.
* 💊 [**`figura3_brecha_tratamiento.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura3_brecha_tratamiento.png):  
  Ranking horizontal de tratamiento farmacológico en las 24 provincias argentinas y gráfico de barras de no adherencia por barrera de costo en EE.UU.
* 🔗 [**`figura4_matriz_correlaciones.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura4_matriz_correlaciones.png):  
  Matrices de calor de correlación de Pearson cruzadas ($5 \times 5$) entre variables epidemiológicas y socioeconómicas.
* 📈 [**`figura5_modelos_dispersion.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura5_modelos_dispersion.png):  
  *(a) Dispersión Pobreza vs. Diabetes (comparando pendientes entre EE.UU. y Argentina) y (b) Pobreza Estructural NBI vs. Acceso a Screening Glucémico en Argentina ($r = -0.62, p < 0.001$).*
* 🌟 [**`figura_comparativa_argentina_usa.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura_comparativa_argentina_usa.png):  
  Póster infográfico consolidado para la exposición oral en el CIITI 2026.

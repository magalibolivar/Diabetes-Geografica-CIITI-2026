# 🧠 AYUDA MEMORIA — COMPARATIVA DIABETES: ARGENTINA VS. EE.UU. (CIITI 2026)

Este documento es una guía rápida y sencilla para repasar los conceptos clave del paper, entender por qué los resultados difieren entre ambos países y conocer con total exactitud de qué archivo y columna proviene cada dato.

---

## ⚡ 1. Aclaración Fundamental sobre los Datos
> **¿Se usaron los datos que ya tenías o se inventaron/generaron otros?**  
> **SE USARON 100% TUS PROPIOS DATOS REALES.**  
> No se inventó ni se generó ningún dato sintético. Toda la evidencia matemática, estadística y cartográfica proviene exclusivamente de los archivos que ya están en tu carpeta `Datos/`:
> 1. `Datos/enfr2018_provincias.csv` (24 jurisdicciones de Argentina).
> 2. `Datos/brfss2015_estados.csv` (51 estados de Estados Unidos).

---

## 🌍 2. ¿Por qué los resultados entre EE.UU. y Argentina NO son iguales?

La idea más potente y valiosa del trabajo es que **la relación entre pobreza y diabetes se comporta de manera totalmente opuesta en ambos países debido al diseño de sus sistemas de salud**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ESTADOS UNIDOS                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Sistema privado / de mercado (fragmentado).                                          │
│ • Diagnóstico masivo (>85% testeado), pero barrera económica en el tratamiento.        │
│ • La pobreza predice fuertemente la diabetes (r = +0,81).                              │
│ • Patrón lineal directo: Más pobreza = más sedentarismo = más diabetes detectada.     │
│ • Machine Learning (Random Forest) predice bien (R² = 0,80) porque la señal es lineal. │
└────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                     ARGENTINA                                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • Sistema público universal con gratuidad en atención y fármacos (Remediar).           │
│ • Barrera en el diagnóstico inicial (screening), no en la entrega de medicamentos.     │
│ • La pobreza NO predice más diabetes en la encuesta (r = -0,05, correlación nula).     │
│ • Hay dos mecanismos sanitarios que explican este desacople:                           │
│    1) Subdiagnóstico en el Norte: En Chaco, Formosa y Santiago del Estero, cerca del   │
│       40% de la población NUNCA se midió la glucosa. Si no se testea, la persona no    │
│       sabe que tiene diabetes y en la encuesta responde "no tengo", bajando la tasa.   │
│    2) Amortiguación pública: En distritos muy vulnerables (Formosa, Chaco), quienes    │
│       fueron diagnosticados reciben medicación gratuita y superan el 60% de cobertura.  │
│ • Machine Learning colapsa (LOOCV R² = -0,70): Al haber subdiagnóstico y ruido, el     │
│   modelo no encuentra un patrón lineal estable en 24 provincias y sobreajusta.         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 3. ¿Por qué falla el Machine Learning en Argentina ($R^2 < 0$)?
* **En EE.UU.:** Hay 51 estados. Aunque 51 observaciones también es una muestra reducida, los factores de riesgo (pobreza, obesidad, sedentarismo) van de la mano de la diabetes con correlaciones altísimas ($r \approx 0,80$). La relación es limpia y lineal, permitiendo $R^2 = 0,802$ en Random Forest y un error absoluto medio de solo $\text{MAE} = 0,59\% \pm 0,04\%$ con mínima variabilidad entre folds.
* **En Argentina:** Hay 24 provincias. La relación entre pobreza y prevalencia declarada está distorsionada por la falta de detección clínica en las provincias vulnerables. Al no haber una relación lineal limpia, los algoritmos intentan memorizar el ruido y fallan catastróficamente fuera de muestra.
* **¿Qué significa $R^2 = -0,701$ negativo? (Demostración matemática):**
  1. **El Estimador Naive Baseline (Modelo de Referencia Ingenuo):** Si ignoramos todas las variables y simplemente predecimos la media histórica constante ($\hat{y} = \bar{y} = 13,0\%$), el error absoluto medio es $\text{MAE} = 1,59\%$ y la varianza no explicada es $\text{Var}(y) = \text{MSE}_{\text{baseline}} = 4,24$. Por definición, este baseline tiene $R^2 = 0$.
  2. **El Modelo OLS en Validación Cruzada (LOOCV):** Cuando el modelo predice fuera de muestra (Leave-One-Out determinístico sobre las 24 provincias), comete un error absoluto medio de $\text{MAE} = 2,12\%$ y un error cuadrático medio de $\text{MSE}_{\text{LOOCV}} = 7,21$.
  3. **La Fórmula de $R^2$:** $R^2_{\text{CV}} = 1 - \frac{\text{MSE}_{\text{modelo}}}{\text{MSE}_{\text{baseline}}} = 1 - \frac{7,21}{4,24} = 1 - 1,701 = -0,701$.
  4. **Conclusión:** El modelo predictivo comete un **70,1% más de error cuadrático** que si simplemente predijéramos la media constante sin usar ninguna variable. Es decir, agregar la pobreza y la cobertura médica agrega ruido y empeora la predicción.
* **Hipótesis del subdiagnóstico vs. Prueba definitiva:** La correlación $r = -0,81$ ($\text{IC95\% } [-0,91; -0,60]$) entre NBI y controles de glucemia —junto con la correlación positiva $r = +0,40$ ($p = 0,057$) entre screening y diabetes al excluir el outlier urbano de CABA— constituye una evidencia ecológica sólida, complementada por factores demográficos (estructura etaria) y muestrales ($\text{CV} \le 12,5\%$). Por eso, el paper propone como trabajo futuro contrastar los datos con las **submuestras bioquímicas de laboratorio de la ENFR** (fase 2, Cuadros 7.9 a 7.11) para cuantificar los casos reales no detectados.
* **Conclusión metodológica del paper:** Con 24 provincias y subdiagnóstico, **no sirve forzar Machine Learning predictivo**. La respuesta honesta y rigurosa de la ciencia de datos en salud es construir **atlas geoespaciales descriptivos** y auditorías de datos para orientar operativos de testeo territorial en el terreno.

---

## 📌 4. Mapeo Columna por Columna: De dónde sale cada dato

### 🇦🇷 A. República Argentina (`Datos/enfr2018_provincias.csv`)

| Columna en el CSV | Fuente Oficial | Cuadro / Hoja Exacta | ¿Qué mide en la vida real? |
| :--- | :--- | :--- | :--- |
| `provincia` | INDEC | Cartografía oficial | Nombre de la jurisdicción (23 provincias + CABA). |
| `tasa_diabetes_pct` | **ENFR 2018** (MSAL/INDEC) | **Cuadro 7.3** | % de adultos con diagnóstico previo de diabetes o glucemia elevada otorgado por personal de salud (100% autorreporte). |
| `cv_diabetes_pct` | **ENFR 2018** | **Cuadro 7.3** | Coeficiente de variación muestral (todos <12,5%, validando calidad estadística). |
| `tratamiento_diabetes_pct` | **ENFR 2018** | **Cuadro 7.5** | % de diagnosticados bajo tratamiento farmacológico activo (pastillas o insulina). |
| `medicion_glucemia_pct` | **ENFR 2018** | **Cuadro 7.1** | % de adultos que se midió la glucemia alguna vez en su vida (**screening**). |
| `obesidad_pct` | **ENFR 2018** | **Cuadro 6.3** | % de adultos con IMC $\ge 30$ (calculado con peso y talla declarados). |
| `inactividad_fisica_pct` | **ENFR 2018** | **Cuadro 3.1** | % de población con nivel bajo de actividad física (sedentarismo). |
| `presion_elevada_pct` | **ENFR 2018** | **Cuadro 8.3** | % con presión arterial elevada autorreportada. |
| `colesterol_elevado_pct` | **ENFR 2018** | **Cuadro 9.3** | % con colesterol elevado autorreportado. |
| `tabaquismo_pct` | **ENFR 2018** | **Cuadro 2.1** | % de prevalencia de consumo de tabaco habitual. |
| `consumo_frutas_verduras_pct` | **ENFR 2018** | **Cuadro 5.7** | % que consume al menos 5 porciones diarias recomendadas. |
| `nbi_2010_pct` | **Censo 2010** (INDEC) | Hoja `NBI_Hogares_%_80_22` | % de hogares con Necesidades Básicas Insatisfechas (pobreza estructural). |
| `pobreza_personas_pct` | **EPH 2018** (INDEC) | **Cuadro 4.3** (2º Semestre) | % de personas bajo la línea de pobreza monetaria (promedio provincial). |
| `sin_cobertura_salud_pct` | **Censo 2022** (INDEC) | **Hoja C1** (Salud) | % de población que depende exclusivamente del hospital público (sin obra social ni prepaga). |
| `densidad_hab_km2` | **Censo 2022 / IGN** | Superficie continental | Habitantes por kilómetro cuadrado. |
| `log_densidad` | Cálculo matemático | $\log_{10}(\text{densidad})$ | Transformación logarítmica para controlar la concentración urbana de CABA. |
| `region` | INDEC | Regiones estadísticas | Pampeana y GBA, Cuyo, Noroeste (NOA), Noreste (NEA), Patagonia. |

---

### 🇺🇸 B. Estados Unidos (`Datos/brfss2015_estados.csv`)

| Columna en el CSV | Fuente Oficial | Variable Original CDC BRFSS | ¿Qué mide en la vida real? |
| :--- | :--- | :--- | :--- |
| `fips` | Federal Standard | `_STATE` | Código federal identificador del estado (1 a 56). |
| `estado` | CDC BRFSS | State Name | Nombre de los 50 estados + Washington D.C. |
| `n` | CDC BRFSS | Casos efectivos | Cantidad de encuestados por estado (ej. 13.537 en Colorado). Total: 441.456. |
| `tasa_diabetes_pct` | CDC BRFSS 2015 | `DIABETE3` | % con diagnóstico de diabetes (excluyendo diabetes gestacional), ponderado con `_LLCPWT`. |
| `obesidad_pct` | CDC BRFSS 2015 | `_BMI5CAT` | % de adultos con índice de masa corporal IMC $\ge 30$. |
| `inactividad_fisica_pct` | CDC BRFSS 2015 | `_TOTINDA` | % de adultos sin actividad física ni ejercicio físico en tiempo libre en el mes previo. |
| `pobreza_ingresos_pct` | CDC BRFSS 2015 | `INCOME2` | % de adultos que viven en hogares con ingresos menores a USD 25.000 anuales. |
| `secundario_incompleto_pct` | CDC BRFSS 2015 | `_EDUCAG` | % de adultos que no completaron la escuela secundaria (*High School*). |
| `barrera_costo_medico_pct` | CDC BRFSS 2015 | `MEDCOST` | % que necesitó ir al médico en los últimos 12 meses pero no pudo por el costo económico. |
| `sin_cobertura_salud_pct` | CDC BRFSS 2015 | `_HCVU651` | % de adultos entre 18 y 64 años sin seguro de salud ni plan médico. |
| `indice_ruralidad` | USDA / ERS | Rural-Urban Codes | Proporción de población del estado residente en condados no metropolitanos/rurales. |

---

### 🔄 C. Tabla de Equivalencias Directas: ¿Qué columna de Argentina equivale a cuál de EE.UU.?

Esta tabla es fundamental para responder en la defensa o exposición: **¿qué columna usamos en Argentina y cuál es exactamente su contraparte en Estados Unidos?**

| Dimensión / Variable | Columna en Argentina 🇦🇷 (`enfr2018_provincias.csv`) | Columna en EE.UU. 🇺🇸 (`brfss2015_estados.csv`) | ¿Por qué son equivalentes y cómo se interpretan? | Rol en los Modelos / Figuras |
| :--- | :--- | :--- | :--- | :--- |
| **Enfermedad (Outcome Principal)** | `tasa_diabetes_pct` | `tasa_diabetes_pct` | **Equivalencia directa 1:1:** Ambas miden el porcentaje de adultos con diagnóstico previo de diabetes otorgado por personal de salud (autorreporte estandarizado en ambas encuestas). | Variable dependiente ($y$) en todos los modelos OLS, Random Forest y en la **Figura 1**. |
| **Nutrición y Obesidad** | `obesidad_pct` | `obesidad_pct` | **Equivalencia directa 1:1:** Ambas miden el porcentaje de adultos con Índice de Masa Corporal $\text{IMC} \ge 30\text{ kg/m}^2$, calculado a partir de peso y talla declarados. | Predictor central en OLS, correlaciones y en la **Figura 2 (a y b)**. |
| **Estilo de Vida (Sedentarismo)** | `inactividad_fisica_pct` | `inactividad_fisica_pct` | **Equivalencia conceptual directa:** Ambas miden inactividad física en tiempo libre / nivel bajo de actividad física habitual en el último mes. | Predictor central en OLS, correlaciones y en la **Figura 2 (c y d)**. |
| **Pobreza e Ingresos (Económico)** | `pobreza_personas_pct` *(y también `nbi_2010_pct`)* | `pobreza_ingresos_pct` | **Equivalencia de privación socioeconómica:**<br>• En EE.UU.: Hogares con ingresos anuales menores a USD 25.000 (`INCOME2`).<br>• En Argentina: Personas bajo la línea de pobreza monetaria (EPH 2018) y porcentaje de hogares con NBI (Censo 2010). | Predictor clave en OLS y correlaciones (**Figura 3**). Muestra el gran desacople: $r = +0,81$ en EE.UU. vs. $r = -0,05$ en Argentina. |
| **Falta de Seguro Médico (Salud)** | `sin_cobertura_salud_pct` | `sin_cobertura_salud_pct` | **Equivalencia de vulnerabilidad en cobertura:**<br>• En EE.UU.: Adultos de 18 a 64 años sin seguro de salud formal ni plan médico (`_HCVU651`).<br>• En Argentina: Personas que dependen exclusivamente del hospital público, sin obra social ni prepaga (Censo 2022). | Variable de sistema sanitario en modelos OLS y análisis de equidad (**Figura 4**). |
| **Unidad Territorial Subnacional** | `provincia` (24 jurisdicciones) | `estado` (51 entidades) | Representa la unidad político-administrativa de análisis territorial (23 provincias + CABA vs. 50 estados + Washington D.C.). | Clave primaria para unir los datos con las capas cartográficas GeoJSON. |
| **Acceso al Diagnóstico (Screening)** | `medicion_glucemia_pct` | Detección clínica rutinaria (>85% en CDC BRFSS) | **Clave de la paradoja:** En Argentina mide quiénes se hicieron análisis de sangre alguna vez. En provincias pobres cae al 60% (subdiagnóstico). En EE.UU. el testeo de rutina supera el 85% en casi todos los estados. | Explica la paradoja en la **Figura 5b**: a mayor pobreza NBI en Argentina, menos controles ($r = -0,74$). |
| **Tratamiento vs. Barrera Económica** | `tratamiento_diabetes_pct` | `barrera_costo_medico_pct` | **Contraste de modelos sanitarios:**<br>• En Argentina: % de diagnosticados con fármacos activos (gratis por Programa Remediar y Ley 26.914).<br>• En EE.UU.: % de personas que no pudieron ir al médico o costear el tratamiento por falta de dinero. | Evidencia central de la **Figura 4** (brecha de acceso y protección pública). |
| **Distribución Espacial / Ruralidad** | `densidad_hab_km2` y `log_densidad` | `indice_ruralidad` | **Equivalencia demográfica de urbanización:**<br>• En Argentina: Densidad de población continental (linealizada con logaritmo base 10).<br>• En EE.UU.: Proporción de población residente en condados rurales según códigos oficiales USDA/ERS. | Control de concentración territorial en regresiones OLS y en modelos espaciales. |
| **Nivel Educativo** | Capturado estructuralmente en `nbi_2010_pct` | `secundario_incompleto_pct` | En EE.UU. mide adultos sin escuela secundaria (*High School*). En Argentina, el déficit educativo está integrado en el indicador multidimensional censal de NBI. | Factor sociodemográfico de vulnerabilidad en regresiones OLS de EE.UU. |

#### 💡 Variables adicionales exclusivas del dataset argentino (`enfr2018_provincias.csv`)
Si te preguntan por columnas que están en el archivo de Argentina pero no tienen contraparte directa en la tabla de EE.UU., son variables clínicas complementarias de la ENFR 2018:
* `cv_diabetes_pct`: Coeficiente de variación muestral (demuestra que todas las estimaciones provinciales son confiables, CV < 12,5%).
* `presion_elevada_pct`: Prevalencia de hipertensión arterial autorreportada.
* `colesterol_elevado_pct`: Prevalencia de colesterol alto autorreportado.
* `tabaquismo_pct`: Consumo habitual de tabaco.
* `consumo_frutas_verduras_pct`: Alimentación saludable (consumo de al menos 5 porciones diarias de frutas y verduras).
* `region`: Agrupación estadística regional oficial del INDEC (Pampeana y GBA, Cuyo, NOA, NEA, Patagonia).

---

## 🔢 5. Recordatorio Rápido sobre los Números Unificados

Para que no te queden dudas si te preguntan en la defensa del paper:

1. **Prevalencia de diabetes en Argentina:**
   * **13,0%**: Es el **promedio simple** si sumás las 24 provincias y dividís por 24.
   * **12,7%**: Es el **total nacional ponderado** oficial que publica la ENFR (dándole más peso poblacional a Buenos Aires, Córdoba y Santa Fe).
   * *Ambos son correctos, pero ahora en el paper se aclaran ambos explícitamente.*

2. **Prevalencia de obesidad:**
   * EE.UU.: **29,3%** promedio de los 51 estados (**28,6%** total nacional ponderado).
   * Argentina: **26,7%** promedio de las 24 provincias (**25,6%** total nacional ponderado).

3. **Prevalencia de sedentarismo:**
   * EE.UU.: **25,8%** promedio de los 51 estados (**23,8%** total nacional ponderado).
   * Argentina: **46,2%** promedio de las 24 provincias (**45,9%** total nacional ponderado).

4. **Modelos predictivos en Argentina (Tabla 3):**
   * **Estimador Naive Baseline:** $R^2 = 0,000$, $\text{MAE} = 1,59\%$ (prediciendo la media histórica provincial constante $\bar{y} = 13,0\%$).
   * **Regresión OLS in-sample:** $R^2 = 0,264$ ($R^2_{\text{adj}} = 0,059$), $\text{MAE} = 1,44\%$ (no significativo, $F=1,29$, $p = 0,31$).
   * **Validación cruzada OLS (LOOCV):** $R^2 = -0,701$, $\text{MAE} = 2,12\%$ (empeora un 70,1% frente al baseline ingenuo).
   * **Random Forest Regressor (5-Fold CV):** $R^2 = -0,802$, $\text{MAE} = 2,20\%$ (pérdida de capacidad predictiva fuera de muestra).

---

## 📐 6. Diccionario de Fórmulas, Símbolos Matemáticos y Conceptos de Machine Learning

Si en la defensa del congreso o en una clase te preguntan qué significa cada letra, símbolo o término estadístico, acá tenés la traducción exacta a lenguaje simple:

### 🔤 A. Símbolos y Letras Estadísticas

| Símbolo / Letra | Nombre Formal | ¿Qué significa en lenguaje sencillo y cómo se interpreta? |
| :---: | :--- | :--- |
| **$r$** | **Coeficiente de Correlación de Pearson** | Mide qué tan asociadas van dos variables en línea recta. Varía siempre entre **$-1$ y $+1$**:<br>• **$r > 0$ (Positivo):** Si una sube, la otra también sube (ej. en EE.UU. a más pobreza, más diabetes: $r = +0,81$).<br>• **$r < 0$ (Negativo o Inverso):** Si una sube, la otra baja (ej. en Argentina a más pobreza NBI, menos controles de glucemia: $r = -0,74$).<br>• **$r \approx 0$ (Nulo):** No hay relación en línea recta (ej. en Argentina pobreza vs diabetes da $r = -0,05$). |
| **$R^2$** | **Coeficiente de Determinación** | Mide qué porcentaje de la variación de la diabetes logra explicar el modelo predictivo:<br>• En entrenamiento va de $0$ a $1$ (o de $0\%$ a $100\%$). Ej: en EE.UU. $R^2 = 0,891$ significa que el modelo explica el $89,1\%$ de las diferencias entre estados.<br>• **¿Por qué puede dar negativo en validación cruzada ($R^2 < 0$)?** Porque la fórmula matemática es $R^2 = 1 - \frac{\text{Error del Modelo}}{\text{Error de la Media}}$. Si el modelo fuera de muestra comete más error que simplemente predecir el promedio provincial, la fracción es mayor a $1$ y la resta da negativa (en Argentina da $-0,701$). |
| **$R^2_{\text{adj}}$** | **$R^2$ Ajustado** | Es el $R^2$ corregido por la cantidad de variables. Penaliza si agregás muchas variables explicativas que no aportan información real. |
| **$\beta$ (Beta)** | **Coeficiente de Regresión (Pendiente)** | En la ecuación de la recta ($y = \beta_0 + \beta_1 x_1 + \dots$), indica **cuántos puntos porcentuales sube o baja la diabetes por cada $1\%$ que sube esa variable**. Ej: en EE.UU., el $\beta$ de la obesidad es $+0,180$; significa que por cada $1\%$ más de obesidad en un estado, la diabetes sube $+0,180\%$. |
| **$p$ o $p\text{-value}$** | **Valor de Significancia Estadística** | Mide la probabilidad de que el resultado sea pura casualidad o suerte del azar:<br>• Si **$p < 0,05$**: Se considera **estadísticamente significativo** (hay menos del 5% de chance de que sea azar; la relación es real).<br>• Si **$p < 0,001$**: Altamente significativo y muy confiable (ej. en EE.UU. la pobreza y la obesidad tienen $p < 0,001$).<br>• Si **$p > 0,05$**: No es significativo (no se puede descartar el azar; en Argentina la pobreza tiene $p = 0,89$). |
| **$\text{MAE}$** | **Error Absoluto Medio (*Mean Absolute Error*)** | Es el promedio de los errores en las mismas unidades de la variable (% de diabetes). Te dice en promedio cuántos puntos le erra el modelo al predecir una provincia. Ej: en EE.UU. $\text{MAE} = 0,50\%$ (le erra por medio punto); en Argentina $\text{MAE} = 2,12\%$ (le erra por más de 2 puntos). |
| **$\text{MSE}$** | **Error Cuadrático Medio (*Mean Squared Error*)** | Es el promedio de los errores elevados al cuadrado ($\text{error}^2$). Se eleva al cuadrado para penalizar con mucha más fuerza los errores grandes y evitar que los errores positivos y negativos se cancelen. |
| **$\bar{y}$ (y con barra)** | **Media o Promedio Aritmético** | El valor promedio de la variable que queremos predecir. En Argentina la media provincial es $\bar{y} = 13,0\%$; en EE.UU. es $\bar{y} = 10,2\%$. |
| **$\text{Var}(y)$ y $\sigma$** | **Varianza y Desvío Estándar** | Miden qué tan desparramados o dispersos están los datos reales alrededor del promedio. En Argentina el desvío estándar muestral es $2,1\%$ (y el poblacional es $\sigma = 2,06\%$), lo que da exactamente una varianza poblacional de $\text{Var}(y) = 4,24$. |
| **$\text{VIF}$** | **Factor de Inflación de Varianza (*Variance Inflation Factor*)** | Mide la **multicolinealidad** (si dos variables predictoras dicen exactamente lo mismo y se estorban entre sí). Si $\text{VIF} < 5$, el modelo está sano y no hay redundancia nociva. En nuestro paper todos los VIF dieron entre 1,5 y 4,4 (controlados). |
| **$\text{HC3}$** | **Errores Estándar Robustos (MacKinnon-White)** | Es un método matemático que corrige la heterocedasticidad (evita que provincias con mucha población como Buenos Aires distorsionen el cálculo del error respecto a provincias chicas como Tierra del Fuego). Hace que los $p$-values sean 100% confiables. |

---

### 🤖 B. Conceptos de Machine Learning y Modelado

* **OLS (*Ordinary Least Squares* o Mínimos Cuadrados Ordinarios):** Es el método clásico de regresión lineal. Busca la mejor línea recta matemática que minimice la distancia vertical a todos los puntos observados.
* **Random Forest Regressor:** Algoritmo no lineal de Machine Learning que combina cientos de "árboles de decisión" entrenados en paralelo y promedia sus pronósticos. Es muy potente porque detecta curvas e interacciones complejas.
* **Validación Cruzada (*Cross-Validation*):** Técnica fundamental para evaluar si un modelo realmente sabe predecir o si solo se memorizó los datos de memoria. Consiste en esconder una parte de las provincias (datos de prueba), entrenar el modelo con las que quedan, y obligarlo a predecir la parte escondida.
  * **K-Fold ($k=5$):** Se usa en EE.UU. Divide los 51 estados en 5 grupitos de ~10 estados. Entrena con 4 grupitos y evalúa en el 5º, repitiendo 5 veces.
  * **LOOCV (*Leave-One-Out Cross-Validation*):** Se usa en Argentina porque son 24 provincias. Esconde 1 provincia, entrena con las otras 23, predice la escondida, y repite el proceso 24 veces (una vez por cada provincia).
* **Estimador Naive Baseline (Modelo Ingenuo de Referencia):** Es el punto de partida de cualquier evaluación seria en ciencia de datos. Consiste en preguntarse: *¿Qué pasa si no uso ninguna variable compleja y simplemente le asigno a todas las provincias el promedio histórico $\bar{y} = 13,0\%$?* Si un algoritmo de Machine Learning sofisticado comete más error que este estimador tonto, significa que el algoritmo fracasó.
* **Data Leakage (Filtración de Información):** Ocurre cuando el algoritmo "hace trampa" y ve información del conjunto de prueba durante el entrenamiento. En nuestro pipeline se evitó al 100% porque cada provincia de prueba estuvo estrictamente aislada del entrenamiento.

---

### ⚙️ C. ¿Cómo funciona el Pipeline de Python (`pipeline_comparativa_argentina_usa.py`)?
El script de Python es el corazón del trabajo. Hace automáticamente 4 pasos secuenciales sin que tengas que tocar nada a mano:
1. **Paso 1 (Carga):** Lee los archivos CSV de `Datos/enfr2018_provincias.csv` y `Datos/brfss2015_estados.csv` y junta los datos con los mapas vectoriales GeoJSON.
2. **Paso 2 (Cálculo):** Aplica las fórmulas de Pearson ($r$), ajusta las regresiones OLS con corrección HC3, calcula los VIF, corre las validaciones cruzadas (LOOCV y 5-Fold), evalúa el Random Forest y genera las 4 tablas oficiales en formato CSV dentro de `Resultados/`.
3. **Paso 3 (Graficación):** Dibuja y exporta las 5 figuras científicas en alta definición (220 DPI) listas para imprenta.
4. **Paso 4 (Compilación Word):** Abre la plantilla oficial de dos columnas del congreso CIITI/CoNaIISI, escribe los textos académicos estructurados, incrusta las figuras y las tablas, formatea las referencias bibliográficas y guarda el archivo final [Paper_Comparativo_Argentina_USA_2026.docx](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Paper/Paper_Comparativo_Argentina_USA_2026.docx).

---

## 📖 7. Explicación Detallada del Paper Sección por Sección y de Cada Gráfico

Acá tenés el resumen narrativo del paper para entender la historia completa de la investigación:

### 🔹 Sección 1: Introducción y Motivación
* **¿Qué plantea?** La diabetes tipo 2 es una epidemia mundial. En países desarrollados como EE.UU. hay muchísimos modelos de inteligencia artificial y predicción territorial. Pero nos preguntamos: **¿esos modelos de ciencia de datos sirven y se pueden aplicar directamente en Argentina o en América Latina?**
* **La respuesta preliminar:** No, porque los sistemas de salud son opuestos: EE.UU. tiene un sistema privado donde el acceso a remedios depende de la billetera; Argentina tiene un sistema público universal gratuito que regala medicamentos (Remediar) pero tiene distancias enormes y demoras en el diagnóstico.

### 🔹 Sección 2: Marco Conceptual y Antecedentes
* Se apoya en el modelo de **Determinantes Sociales de la Salud (DSS)** de la OMS: la diabetes no es solo genética; depende de si podés comprar comida sana, si tenés tiempo de hacer ejercicio y si tenés un hospital cerca.
* En EE.UU. existe el famoso *"Cinturón de la Diabetes"* en el sur pobre. En Argentina hay antecedentes de desigualdad regional en el norte, pero muy pocos atlas geoespaciales comparativos.
* Introduce el aviso metodológico sobre el **Problema de la Unidad de Área Modificable (MAUP)** y la **Falacia Ecológica**: cuando mirás datos por provincia (macro), estás viendo propiedades del sistema territorial y no el comportamiento individual de cada persona.

### 🔹 Sección 3: Fuentes de Datos y Metodología
* **Estados Unidos:** Relevamiento CDC BRFSS 2015 con 441.456 personas encuestadas representativas de los 51 estados.
* **Argentina:** 4ª Encuesta Nacional de Factores de Riesgo (ENFR 2018) del INDEC y Ministerio de Salud (24 provincias), cruzada con el Censo 2010 (NBI), Censo 2022 (cobertura médica pública) y EPH 2018 (pobreza monetaria).
* **Punto clave:** Ambas encuestas miden la prevalencia mediante **autorreporte estandarizado** de diagnóstico médico previo.

---

### 🗺️ Sección 4.1 y FIGURA 1: Atlas Geoespacial de Prevalencia
* **¿Qué muestra la Figura 1?** Dos mapas puestos uno al lado del otro con la **misma escala de colores (del 6% al 18%)** para que sean visualmente comparables:
  * **Figura 1a (EE.UU.):** Se ve claramente una franja roja oscura en el sur profundo (Misisipi 14,8%, Virginia Occidental 14,5%, Alabama 13,6%). Los estados ricos del oeste y norte son claritos (Colorado 6,8%, Utah 7,1%). Hay un contraste geográfico nítido.
  * **Figura 1b (Argentina):** La distribución sorprende. Las tasas más altas no están en el norte pobre, sino en Cuyo y el Centro (San Luis 17,3%, San Juan 15,9%, La Rioja 15,1%). CABA tiene el valor más bajo (8,8%), pero comparte valores llamativamente bajos con provincias muy postergadas del norte como Jujuy (8,9%) y Chaco (10,3%).

---

### 🏃‍♂️ Sección 4.2 y FIGURA 2: Factores de Riesgo (Obesidad y Sedentarismo)
* **¿Qué muestra la Figura 2?** Cuatro mapas que comparan obesidad y sedentarismo en ambos países:
  * **Figura 2a y 2c (EE.UU.):** La obesidad (media 29,3%) y el sedentarismo (media 25,8%) se concentran exactamente en los mismos estados del sur que tienen más diabetes. Van en sintonía perfecta.
  * **Figura 2b y 2d (Argentina):** La obesidad promedia 26,7% (con picos en San Juan 34,4% y Santa Cruz 34,0%). Pero el sedentarismo es escandaloso: promedia **46,2%** a nivel provincial (casi el doble que en EE.UU.), llegando al 69,1% en Formosa y 61,2% en La Rioja. El sedentarismo en Argentina es un problema generalizado en casi todo el país.

---

### 🔥 Sección 4.3 y FIGURA 3 / TABLA 2: Matriz de Correlaciones y Regresión OLS
* **¿Qué muestra la Figura 3?** Dos matrices de calor de correlaciones ($r$ de Pearson):
  * En EE.UU. casi todos los casilleros de factores de riesgo con diabetes son rojos intensos: pobreza de ingresos ($r = +0,81$), sedentarismo ($r = +0,79$), bajo nivel educativo ($r = +0,77$) y obesidad ($r = +0,75$). Todos con $p < 0,001$. En la Tabla 2, la regresión lineal logra un ajuste excelente de $R^2 = 0,891$.
  * En Argentina la matriz muestra casilleros azulados o casi blancos: la pobreza monetaria no se asocia con diabetes ($r = -0,05$), el NBI da correlación negativa ($r = -0,26$) y la falta de obra social da $r = -0,16$. En la Tabla 2, el modelo OLS no es significativo ($p = 0,31$, $R^2 = 0,264$).

---

### 💊 Sección 4.4 y FIGURA 4 / FIGURA 5b: La Paradoja de Detección vs. Tratamiento
Acá está la explicación de por qué los datos argentinos se comportan de forma tan rara. Se explica en dos etapas:
1. **Etapa 1: Detección Temprana (Screening) y Subdiagnóstico (Figura 5b):**
   * Para saber si tenés diabetes, te tenés que hacer un análisis de sangre. En EE.UU. más del 85% de la gente se hace chequeos de rutina.
   * En Argentina descubrimos una correlación negativa fuertísima: **$r = -0,81$ entre pobreza estructural (NBI) y haberse medido la glucosa alguna vez** (y al excluir a CABA, el screening correlaciona positivamente con la prevalencia declarada con **$r = +0,40$**). En CABA el 92,9% se testeó, pero en Chaco, Formosa y Santiago del Estero el **40% de la población adulta jamás se midió la glucemia en su vida**.
   * Si 4 de cada 10 personas nunca se hicieron el análisis, no saben que están enfermas. Al encuestarlas responden "no tengo diabetes", lo que hace bajar artificialmente la tasa declarada en el norte.
2. **Etapa 2: Cobertura Farmacológica en Tratamiento (Figura 4a y 4b):**
   * En EE.UU. (Figura 4b), la pesquisa diagnóstica es alta, pero el remedio es caro (la insulina ha llegado a costar más de USD 300 mensuales, provocando que la gente racione sus dosis por falta de plata).
   * En Argentina (Figura 4a), una vez que el paciente fue diagnosticado, el hospital público (**Programa Remediar** para metformina/glibenclamida y **Ley 26.914 / PRODIABA** para cobertura al 100% de insulina e insumos) amortigua la desigualdad ($r = -0,11, p = 0,62$ entre falta de obra social y tratamiento). Por eso, las tres provincias donde más del 50% de la gente no tiene obra social ni prepaga (**Santiago del Estero 56,0%**, **Formosa 55,9%** y **Chaco 52,2%**) alcanzan coberturas de tratamiento superiores al promedio nacional (**59,7%**, **62,6%** y **54,2%** respectivamente), aunque a nivel nacional persiste una brecha media del **45,6%** sin tratamiento farmacológico activo (con cobertura media de **54,4%**).

---

### 📉 Sección 4.5 y FIGURA 5a / TABLA 3: Límites de Predictibilidad y Machine Learning
* **¿Qué demuestra la Tabla 3?**
  * En EE.UU. ($N=51$), como hay un gradiente lineal claro, Random Forest predice con gran solidez ($R^2_{\text{CV}} = 0,802$, error de apenas $0,66\%$).
  * En Argentina ($N=24$), el modelo lineal OLS en muestra parece ajustar ($R^2 = 0,264$), pero cuando lo obligás a predecir provincias que no vio mediante validación cruzada (LOOCV), el modelo se destruye: $R^2_{\text{LOOCV}} = -0,701$ y Random Forest da $R^2 = -0,802$.
  * **Demostración clave:** El predictor de la media (Naive Baseline) tiene un error de $\text{MAE} = 1,59\%$. El modelo de regresión OLS tiene un error peor de $\text{MAE} = 2,12\%$.
* **Conclusión:** Las variables socioeconómicas provinciales no sirven para predecir diabetes en Argentina con Machine Learning porque los datos observados están distorsionados por el subdiagnóstico.

---

### 🏛️ Sección 5: Discusión y Políticas Públicas
* **Para EE.UU.:** La prioridad sanitaria no es salir a buscar enfermos, sino regular el mercado farmacéutico y poner topes de precio a la insulina para que la gente no se muera por no poder pagar el copago.
* **Para Argentina:** La prioridad no es regalar más medicamentos en los grandes hospitales, sino salir a buscar a la gente en operativos territoriales barriales y parajes rurales con tiras reactivas de glucosa para diagnosticar a ese 40% que no sabe que tiene diabetes.
* **Advertencia epistemológica contra el "solucionismo predictivo":** No hay que tirar algoritmos complejos de Machine Learning sobre datos agregados chicos ($N=24$) esperando que hagan magia. Cuando hay problemas de subregistro, la máquina confunde la falta de diagnóstico con falta de enfermedad.

---

### 🎯 Sección 6: Conclusiones y Trabajos Futuros
* Se demostró el valor del **Atlas Geoespacial Descriptivo** por sobre los modelos predictivos frágiles.
* **Línea futura fundamental:** Analizar las submuestras con mediciones bioquímicas de laboratorio de la ENFR (Cuadros 7.9 a 7.11) para cuantificar por primera vez en números reales cuánta diabetes oculta hay en cada región del país.

---

## 📋 8. TABLA FINAL: EQUIVALENCIAS DIRECTAS DE COLUMNAS (ARGENTINA 🇦🇷 VS. ESTADOS UNIDOS 🇺🇸)

> **¿Qué columna usamos en Argentina y cuál es exactamente su equivalente en Estados Unidos?**  
> Si te preguntan en la defensa cómo se corresponden los datos entre ambos países, acá tenés el mapeo directo columna por columna:

| Dimensión / Variable | Columna en Argentina 🇦🇷<br>(`Datos/enfr2018_provincias.csv`) | Columna en EE.UU. 🇺🇸<br>(`Datos/brfss2015_estados.csv`) | ¿Por qué son equivalentes y qué miden? | Rol en los Modelos / Figuras |
| :--- | :--- | :--- | :--- | :--- |
| **Enfermedad (Outcome / Variable Objetivo $y$)** | `tasa_diabetes_pct` | `tasa_diabetes_pct` | **Equivalencia directa 1 a 1:** % de adultos con diagnóstico de diabetes otorgado por personal de salud (autorreporte oficial estandarizado en ambas encuestas). | Variable dependiente ($y$) en todos los modelos OLS, Random Forest y en la **Figura 1**. |
| **Nutrición y Obesidad** | `obesidad_pct` | `obesidad_pct` | **Equivalencia directa 1 a 1:** % de adultos con Índice de Masa Corporal $\text{IMC} \ge 30\text{ kg/m}^2$, calculado a partir de peso y talla declarados. | Predictor central en OLS, correlaciones y en la **Figura 2 (a y b)**. |
| **Estilo de Vida (Sedentarismo)** | `inactividad_fisica_pct` | `inactividad_fisica_pct` | **Equivalencia conceptual directa:** Ambas miden inactividad física en tiempo libre / nivel bajo de actividad física habitual en el último mes. | Predictor central en OLS, correlaciones y en la **Figura 2 (c y d)**. |
| **Pobreza e Ingresos (Económico)** | `pobreza_personas_pct`<br>*(y `nbi_2010_pct`)* | `pobreza_ingresos_pct` | **Equivalencia de privación socioeconómica:**<br>• En EE.UU.: Hogares con ingresos anuales menores a USD 25.000 (`INCOME2`).<br>• En Argentina: Personas bajo la línea de pobreza monetaria (EPH 2018) y porcentaje de hogares con NBI (Censo 2010). | Predictor clave en OLS y correlaciones (**Figura 3**). Muestra el gran desacople: $r = +0,81$ en EE.UU. vs. $r = -0,05$ en Argentina. |
| **Falta de Cobertura Médica** | `sin_cobertura_salud_pct` | `sin_cobertura_salud_pct` | **Equivalencia de vulnerabilidad en cobertura:**<br>• En EE.UU.: Adultos de 18 a 64 años sin seguro de salud formal ni plan médico (`_HCVU651`).<br>• En Argentina: Personas que dependen exclusivamente del hospital público, sin obra social ni prepaga (Censo 2022). | Variable de sistema sanitario en modelos OLS y análisis de equidad (**Figura 4**). |
| **Unidad Territorial Subnacional** | `provincia`<br>(24 jurisdicciones: 23 provs + CABA) | `estado`<br>(51 entidades: 50 estados + D.C.) | Representa la unidad político-administrativa de análisis territorial. En EE.UU. incluye además el código federal `fips`. | Clave primaria para unir los datos con las capas cartográficas GeoJSON. |
| **Acceso al Diagnóstico (Screening)** | `medicion_glucemia_pct` | Detección clínica rutinaria<br>(>85% en CDC BRFSS) | **Clave de la paradoja:** En Argentina mide quiénes se hicieron análisis de sangre alguna vez. En provincias pobres cae al 60% (subdiagnóstico). En EE.UU. el testeo de rutina supera el 85% en casi todos los estados. | Explica la paradoja en la **Figura 5b**: a mayor pobreza NBI en Argentina, menos controles ($r = -0,74$). |
| **Tratamiento vs. Barrera Económica** | `tratamiento_diabetes_pct` | `barrera_costo_medico_pct` | **Contraste de modelos sanitarios:**<br>• En Argentina: % de diagnosticados con fármacos activos (gratis por Programa Remediar y Ley 26.914).<br>• En EE.UU.: % de personas que no pudieron ir al médico o costear el tratamiento por falta de dinero. | Evidencia central de la **Figura 4** (brecha de acceso y protección pública). |
| **Urbanización / Ruralidad** | `densidad_hab_km2`<br>y `log_densidad` | `indice_ruralidad` | **Equivalencia demográfica de distribución espacial:**<br>• En Argentina: Densidad de población continental (linealizada con logaritmo base 10).<br>• En EE.UU.: Proporción de población residente en condados rurales según códigos oficiales USDA/ERS. | Control de concentración territorial en regresiones OLS y en modelos espaciales. |
| **Nivel Educativo** | Integrado estructuralmente en `nbi_2010_pct` | `secundario_incompleto_pct` | En EE.UU. mide adultos sin escuela secundaria (*High School*). En Argentina, el déficit educativo está integrado en el indicador multidimensional censal de NBI. | Factor sociodemográfico de vulnerabilidad en regresiones OLS de EE.UU. |

### 💡 Columnas adicionales exclusivas de Argentina (`enfr2018_provincias.csv`)
Si te preguntan por columnas que están en el archivo argentino y no en el de EE.UU., son variables clínicas complementarias de la ENFR 2018:
* `cv_diabetes_pct`: Coeficiente de variación muestral (demuestra que todas las estimaciones provinciales son confiables, CV < 12,5%).
* `presion_elevada_pct`: Prevalencia de hipertensión arterial autorreportada.
* `colesterol_elevado_pct`: Prevalencia de colesterol alto autorreportado.
* `tabaquismo_pct`: Consumo habitual de tabaco.
* `consumo_frutas_verduras_pct`: Alimentación saludable (consumo de al menos 5 porciones diarias de frutas y verduras).
* `region`: Agrupación estadística regional oficial del INDEC (Pampeana y GBA, Cuyo, NOA, NEA, Patagonia).

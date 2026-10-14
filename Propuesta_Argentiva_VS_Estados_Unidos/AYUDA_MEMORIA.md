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

## 📊 3. ¿Por qué colapsa el Machine Learning en Argentina ($R^2 < 0$)?
* **En EE.UU.:** Hay 51 estados. Aunque 51 observaciones también es una muestra reducida, los factores de riesgo (pobreza, obesidad, sedentarismo) van de la mano de la diabetes con correlaciones altísimas ($r \approx 0,80$). La relación es limpia y lineal, permitiendo $R^2 = 0,80$.
* **En Argentina:** Hay 24 provincias. La relación entre pobreza y prevalencia declarada está distorsionada por la falta de detección clínica en las provincias vulnerables. Al no haber una relación lineal limpia, los algoritmos complejos intentan memorizar el ruido y fallan catastróficamente fuera de muestra.
* **¿Qué significa $R^2 = -0,70$ negativo?** Matemáticamente significa que el modelo es **peor que un predictor ingenuo** que simplemente le asigne a todas las provincias el promedio general ($\bar{y}$).
* **Conclusión metodológica del paper:** Con 24 provincias y subdiagnóstico, **no sirve forzar Machine Learning predictivo**. La respuesta honesta y rigurosa de la ciencia de datos en salud es construir **atlas geoespaciales descriptivos** para orientar operativos de testeo territorial en el terreno.

---

## 📌 4. Mapeo Columna por Columna: De dónde sale cada dato

### 🇦🇷 A. República Argentina (`Datos/enfr2018_provincias.csv`)

| Columna en el CSV | Fuente Oficial | Cuadro / Hoja Exacta | ¿Qué mide en la vida real? |
| :--- | :--- | :--- | :--- |
| `provincia` | INDEC | Cartografía oficial | Nombre de la jurisdicción (23 provincias + CABA). |
| `tasa_diabetes_pct` | **ENFR 2018** (MSAL/INDEC) | **Cuadro 7.3** | % de adultos que declararon tener diabetes o glucemia elevada (o se midió en la muestra). |
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
   * Regresión OLS in-sample: $R^2 = 0,264$ (no significativo, $p = 0,31$).
   * Validación cruzada OLS (LOOCV): $R^2 = -0,701$ (colapso predictivo).
   * Random Forest Regressor (5-Fold CV): $R^2 = -0,802$ (colapso predictivo).

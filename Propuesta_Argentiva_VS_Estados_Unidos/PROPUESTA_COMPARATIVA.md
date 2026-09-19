# Propuesta de Paper: Determinantes Geoespaciales de la Diabetes — Análisis Comparativo Argentina vs. Estados Unidos

**Destino propuesto:** CIITI 2026 (Congreso Internacional de Innovación y Tecnología Informática) / CoNaIISI  
**Grupo de Investigación:** CAETI — Facultad de Tecnología Informática, Universidad Abierta Interamericana (UAI)  
**Fecha:** Septiembre 2026  

---

## 1. Resumen Ejecutivo y Pregunta Central

### ¿Cuál es la pregunta de investigación?
> **¿Los mismos factores sociales, económicos y de estilo de vida que determinan la diabetes en un país desarrollado con salud privada (EE.UU.) operan de la misma manera en un país en desarrollo con sistema público universal (Argentina)?**

Este trabajo propone un enfoque de **salud basada en datos (Health Data Science)** y **epidemiología geoespacial** que compara directamente dos realidades territoriales a nivel subnacional:
1. **51 estados de Estados Unidos** (datos del CDC / BRFSS, 441.456 encuestados agregados con ponderación muestral).
2. **24 jurisdicciones de la República Argentina** (23 provincias + CABA, cruzando microdatos de la 4ª Encuesta Nacional de Factores de Riesgo ENFR 2018 con el Censo Nacional y la EPH del INDEC).

---

## 2. De dónde sacamos los datos (Fuentes Oficiales y Provenance)

Todos los datos utilizados provienen exclusivamente de **organismos oficiales y repositorios públicos abiertos verificados**:

### A. Datos de Argentina (24 Jurisdicciones)
*Archivo consolidado en el repo:* `data/processed/enfr2018_provincias.csv`  
*Script constructor:* `src/05_build_argentina.py`  
*Capa geográfica:* `geo/argentina_provincias.geojson` (24 geometrías vectoriales)

1. **4ª Encuesta Nacional de Factores de Riesgo (ENFR 2018):**  
   * **Organismo:** INDEC y Secretaría de Gobierno de Salud de la Nación.
   * **Variables extraídas:**
     * `tasa_diabetes_pct`: Prevalencia de diabetes o glucemia elevada autorreportada y medida (Cuadro 7.3). Rango: 8,8% (CABA) a 17,3% (San Luis). Coeficientes de variación (CV) menores al 12,5% en todas las provincias (estimaciones confiables).
     * `tratamiento_diabetes_pct`: Porcentaje de personas con diabetes bajo tratamiento farmacológico activo (Cuadro 7.5). Rango: 32,7% (La Pampa) a 70,0% (Santa Cruz y Tierra del Fuego).
     * `medicion_glucemia_pct`: Acceso a screening preventivo (medición de glucosa en sangre alguna vez en la vida, Cuadro 7.1). Rango: 60,3% (Chaco) a 92,9% (CABA).
     * `obesidad_pct`: Porcentaje de población adulta con IMC $\ge 30$ autorreportado (Cuadro 6.3).
     * `inactividad_fisica_pct`: Prevalencia de sedentarismo o actividad física baja (Cuadro 3.1).
     * `presion_elevada_pct`: Hipertensión arterial autorreportada (Cuadro 8.3).
     * `colesterol_elevado_pct`: Colesterol elevado autorreportado (Cuadro 9.3).
     * `consumo_frutas_verduras_pct`: Consumo de al menos 5 porciones diarias (Cuadro 5.7).

2. **Censo Nacional de Población, Hogares y Viviendas (Censo 2010 y 2022 - INDEC):**
   * `nbi_2010_pct`: Porcentaje de hogares con Necesidades Básicas Insatisfechas (Censo 2010, serie histórica oficial `serie_nbi_2022.xlsx`).
   * `sin_cobertura_salud_pct`: Población que no posee obra social ni prepaga y depende exclusivamente del sistema público de salud (Censo 2022, archivo `c2022_tp_salud_c1.xlsx`, Hoja C1). Rango: 16,3% (CABA) a 55,9% (Formosa).
   * `densidad_hab_km2` / `log_densidad`: Habitantes por kilómetro cuadrado de superficie continental efectiva (Censo 2022).

3. **Encuesta Permanente de Hogares (EPH 2018 - INDEC):**
   * `pobreza_personas_pct`: Incidencia de la pobreza monetaria por debajo de la línea de pobreza correspondiente al 2º semestre de 2018 (`cuadros_informe_pobreza_03_26.xls`, Cuadro 4.3), promediada por aglomerados urbanos para coincidir temporalmente con la ENFR 2018.

---

### B. Datos de Estados Unidos (51 Estados / Jurisdicciones)
*Archivo consolidado en el repo:* `data/processed/brfss2015_estados.csv`  
*Script constructor:* `src/01_build_brfss_states.py`  
*Capa geográfica:* `geo/us_states.geojson` (51 geometrías vectoriales)

1. **CDC BRFSS 2015 (Behavioral Risk Factor Surveillance System):**
   * **Organismo:** Centers for Disease Control and Prevention (CDC), Departamento de Salud de EE.UU.
   * **Volumen:** 441.456 entrevistas individuales agregadas a los 51 estados aplicando el factor de ponderación muestral oficial (`_LLCPWT`) para asegurar representatividad poblacional.
   * **Variables extraídas:**
     * `tasa_diabetes_pct`: Prevalencia de diabetes diagnosticada (excluyendo diabetes gestacional). Rango: 6,8% (Colorado) a 14,8% (Misisipi).
     * `obesidad_pct`: IMC $\ge 30$ calculado sobre peso y estatura declarados (`_BMI5CAT`).
     * `inactividad_fisica_pct`: Adultos sin actividad física regular fuera del trabajo (`_TOTINDA`).
     * `pobreza_ingresos_pct`: Población con ingresos menores a USD 25.000 anuales.
     * `secundario_incompleto_pct`: Población adulta sin título de nivel secundario/high school (`_EDUCAG`).
     * `barrera_costo_medico_pct`: Adultos que no pudieron consultar al médico en los últimos 12 meses debido al costo económico (`MEDCOST`).
     * `sin_cobertura_salud_pct`: Adultos sin ningún seguro médico o plan de salud (`_HCVU651`).
     * `indice_ruralidad`: Proporción de población en condados rurales según códigos USDA/ERS.

---

### C. Contexto Global (193 Países)
*Archivos:* `data/processed/global_paises.csv` y `data/processed/ncdrisc_mundo_tendencia.csv`
1. **IDF Diabetes Atlas (11ª edición, 2024) / Our World in Data:** Prevalencia mundial estandarizada por edad en 193 países y carga absoluta de pacientes (Argentina: 4,3 millones de adultos con diabetes, puesto #24 del mundo).
2. **Banco Mundial (World Development Indicators):** PBI per cápita (PPA), gasto de bolsillo en salud, envejecimiento poblacional y ruralidad.
3. **Consorcio NCD-RisC (publicado en The Lancet, 2024):** Series temporales 1990–2022 que demuestran que la prevalencia mundial se duplicó pero el tratamiento se estancó en solo ~40%.

---

## 3. ¿Qué se observa en cada país? (El Gran Contraste)

### A. Lo que se observa en Estados Unidos 🇺🇸: "El modelo de mercado"
1. **La pobreza predice la enfermedad con precisión matemática:**
   * La correlación entre diabetes y bajos ingresos es altísima ($r = +0,81$).
   * Quienes no completaron el secundario tienen correlación $r = +0,77$, y el sedentarismo $r = +0,79$.
2. **El "Cinturón de la Diabetes" (Diabetes Belt):**
   * En el mapa se observa una concentración extrema en el sur rural y los Apalaches (Misisipi 14,8%, Alabama 13,6%, Virginia Occidental 13,9%), mientras que estados del norte y oeste con mayores ingresos y vida activa (Colorado 6,8%, Utah 7,5%) tienen menos de la mitad de casos.
3. **Ajuste casi perfecto de los modelos:**
   * Una regresión multivariada OLS explica el **91% de la varianza ($R^2 = 0,91$)**.
   * Un algoritmo de Random Forest con validación cruzada alcanza $R^2_{\text{CV}} = 0,81$.

---

### B. Lo que se observa en Argentina 🇦🇷: "La paradoja del subdiagnóstico y la gestión pública"
1. **La pobreza no correlaciona positivamente con la diabetes:**
   * La pobreza monetaria de la EPH da $r = -0,19$ ($p=0,37$, no significativa) y el NBI da $r = -0,26$.
   * Provincias con alta pobreza estructural del norte (Chaco 10,3%, Formosa 12,1%, Jujuy 8,9%) declaran **menos diabetes** que distritos de mayor ingreso relativo como Cuyo y Centro (San Luis 17,3%, San Juan 15,9%, La Pampa 14,6%).
2. **La causa oculta: El sesgo de subdiagnóstico:**
   * En provincias del NOA y NEA, **hasta un 40% de los adultos jamás se midió la glucemia en su vida** (screening de apenas 60-61%).
   * Al ser encuestas por autorreporte, quien no tiene acceso al control de laboratorio no sabe que tiene diabetes. En CABA, donde el 93% se testea, la prevalencia es del 8,8%.
3. **La brecha de tratamiento farmacológico está desacoplada del dinero:**
   * El porcentaje de personas con diabetes que recibe medicación varía entre un crítico **32,7% (La Pampa)** y un **70,0% (Santa Cruz y Tierra del Fuego)**.
   * Crucialmente, la tasa de tratamiento **no correlaciona** con no tener obra social ($r = +0,12$) ni con la pobreza ($r = -0,19$).
   * Provincias pobres con más del 50% de la gente atendida en el hospital público (como Formosa con 62,6% o Chaco con 54,2%) tienen coberturas de medicación muy superiores a provincias con menor pobreza estructural (La Pampa 32,7% o Chubut 38,3%). El acceso depende de la logística de atención primaria provincial y programas como Remediar, no de la billetera familiar.
4. **Impacto en Machine Learning:**
   * Con $N=24$ provincias y sesgos de screening, los modelos predictivos supervisados fallan al generalizar ($R^2_{\text{LOOCV}} \le 0$). Forzar modelos de Machine Learning produce sobreajuste; la respuesta científica honesta es un atlas analítico y geoespacial.

---

## 4. La Aparente Paradoja: ¿Por qué en Argentina la salud es gratis pero falta diagnóstico, y en EE.UU. se diagnostica pero cuesta el remedio?

A primera vista parece una contradicción: si en Argentina la salud es pública y gratuita, ¿por qué no se diagnostica a todos? Y si en EE.UU. son una potencia con diagnósticos rápidos, ¿por qué hay problemas con el tratamiento?

Para comprenderlo científicamente, hay que separar el proceso en **dos etapas independientes**:

```
[Etapa 1: Diagnóstico / Screening]  --->  [Etapa 2: Tratamiento / Fármacos]
 ¿Sé que tengo diabetes?                   ¿Tomo la medicación continua?
 (Análisis de glucemia)                    (Insulina / Metformina)
```

### A. Etapa 1: El Diagnóstico (Detectar la enfermedad)
* **La naturaleza silenciosa de la diabetes:** La diabetes tipo 2 no produce dolor en sus etapas iniciales. Nadie concurre a la consulta médica manifestando "dolor de glucosa". La única forma de detectarla precozmente es mediante una extracción de sangre venosa en ayunas.
* **En Argentina (Barrera geográfica y de prevención):**
  * En el interior profundo de provincias con alta vulnerabilidad (parajes o pueblos rurales de Chaco, Formosa o Santiago del Estero), realizarse un laboratorio implica trasladarse decenas de kilómetros hasta un hospital cabecera, conseguir turnos de madrugada y retornar días después por el resultado.
  * Como el paciente no experimenta dolor y existen barreras de distancia, **no asiste al hospital a testearse**. 
  * Por este motivo, el **40% de la población adulta en esas provincias jamás se midió la glucemia en su vida**, generando un **severo subdiagnóstico**: la persona padece diabetes pero la estadística oficial no la registra porque ella misma lo desconoce.
* **En Estados Unidos (Facilidad de acceso al screening):**
  * El sistema asistencial incorpora paneles de laboratorio completos en controles de empleo, chequeos rutinarios o coberturas básicas (Medicare/Medicaid). El testeo es masivo y automatizado, por lo que casi todo individuo con diabetes es formalmente notificado de su condición.

### B. Etapa 2: El Tratamiento Farmacológico (Acceder a la medicación)
* **En Argentina (El rol amortiguador del sistema público):**
  * El indicador de tratamiento de la ENFR evalúa la proporción de personas bajo medicación **entre aquellas que ya fueron diagnosticadas**.
  * Una vez que el paciente argentino atraviesa la barrera del diagnóstico e ingresa formalmente al sistema de salud pública, se activan programas estatales (como el programa nacional **Remediar**, **Redes** y programas provinciales de diabetes como PRODIABA o PROPAT).
  * Estos programas distribuyen **insulina y metformina de forma 100% gratuita** en los centros de atención primaria (salitas). Por consiguiente, distritos con más del 50% de su población sin cobertura privada (como Formosa o Chaco) logran tasas de medicación activa superiores al 60%.
* **En Estados Unidos (La barrera económica de mercado):**
  * El sistema de salud estadounidense opera bajo lógica de mercado y aseguramiento privado.
  * La insulina y los hipoglucemiantes orales presentan costos elevados (frecuentemente entre USD 300 y USD 1.000 mensuales sin cobertura completa o bajo pólizas con altos deducibles).
  * Esto provoca un fenómeno ampliamente documentado en la literatura (y reflejado en la variable `barrera_costo_medico_pct` del CDC BRFSS): los pacientes **saben que tienen diabetes, pero racionan o suspenden las dosis de insulina** por imposibilidad económica de pago.

### C. Síntesis Comparativa de Barreras:
* **La barrera en Estados Unidos es la BILLETERA (Económica):** El diagnóstico es sencillo, pero acceder y sostener el tratamiento depende de la capacidad de pago y del seguro médico individual.
* **La barrera en Argentina es la DISTANCIA Y LA PREVENCIÓN (Logística):** La medicación es gratuita en el hospital público, pero una fracción sustancial de los sectores vulnerables permanece sin diagnosticar por falta de campañas activas de testeo en el primer nivel de atención.

---

## 5. Tabla Resumen: ¿Qué cambia entre Argentina y EE.UU.?

| Dimensión de Análisis | Estados Unidos 🇺🇸 | República Argentina 🇦🇷 |
| :--- | :--- | :--- |
| **Unidades Territoriales** | 51 estados | 24 jurisdicciones provinciales |
| **Prevalencia Mínima / Máxima** | 6,8% (Colorado) a 14,8% (Misisipi) | 8,8% (CABA) a 17,3% (San Luis) |
| **Correlación Diabetes vs. Pobreza** | **$r = +0,81$ (Fuerte y positiva)** | **$r = -0,19$ (Débil / invertida)** |
| **Causa de la Asociación** | La privación material deteriora la dieta y el estilo de vida. | Subdiagnóstico: la pobreza se asocia a falta de testeo médico ($r = -0,74$ con screening). |
| **Acceso a Medicamentos** | Condicionado por tener seguro médico o capacidad de pago. | Desacoplado del ingreso: condicionado por la red provincial de centros de salud y programas públicos. |
| **Comportamiento de Modelos (ML)** | $R^2 = 0,91$ en OLS y $0,81$ en Random Forest. | Sobreajuste con $N=24$ ($R^2_{\text{LOOCV}} \le 0$). Exige enfoque descriptivo riguroso. |
| **Lección para Políticas Públicas** | Focalizar intervenciones en reducir costos de atención y zonas vulnerables. | Fortalecer campañas de testeo activo (screening) en el norte y auditar la logística de medicación en provincias rezagadas. |

---

## 6. Propuesta de Gráficos / Mapas de Calor para el Paper

La propuesta incluye una **figura compuesta de alta resolución** (guardada en [`Resultados/figura_comparativa_argentina_usa.png`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura_comparativa_argentina_usa.png)) con los siguientes paneles:

1. **Panel Superior: Mapas de Calor Geoespaciales (Coropléticos con escala común 6% a 18%)**
   * **Mapa de EE.UU. (Izquierda):** Coloreado con escala térmica continua (`YlOrRd`), mostrando el "Cinturón de la Diabetes" en el sur (Misisipi 14,8%, Alabama 13,6%) frente a estados de bajo riesgo como Colorado (6,8%).
   * **Mapa de Argentina (Derecha):** Misma escala cromática, destacando el foco en Cuyo/Centro (San Luis 17,3%), el recuadro ampliado para CABA (8,8%) y la llamada de subdiagnóstico en el norte.
2. **Panel Inferior Izquierdo: Mapa de Calor de Correlaciones (Correlation Heatmap)**
   * Matriz cruzada que enfrenta las 5 variables clave (Diabetes, Obesidad, Sedentarismo, Pobreza, Falta de Cobertura).
   * **El contraste visual:** En EE.UU. la columna arde en rojo ($r = +0,81$ pobreza, $r = +0,79$ sedentarismo, $r = +0,75$ obesidad); en Argentina los factores socioeconómicos dan correlaciones casi nulas ($r = -0,05$ pobreza) o negativas.
3. **Panel Inferior Derecho: Dispersión Pobreza vs. Diabetes (Scatter Plot con Regresión)**
   * **Línea roja sólida (EE.UU.):** Pendiente ascendente pronunciada ($r = +0,81$; $R^2 = 0,66$). A más pobreza, matemáticamente más diabetes.
   * **Línea azul discontinua (Argentina):** Pendiente plana ($r = -0,05$; $p = 0,82$), ilustrando el desacople provocado por el sesgo de screening/subdiagnóstico.

---

## 7. 🗂️ Estructura Modular y Carpetas del Proyecto

El proyecto está rigurosamente segmentado en 4 carpetas sin duplicación de archivos:

```
Propuesta_Argentiva_VS_Estados_Unidos/
│
├── 📁 Datos/            <-- Datasets consolidados (Argentina + EE.UU.) y fuentes oficiales crudas de INDEC
│   ├── enfr2018_provincias.csv
│   ├── brfss2015_estados.csv
│   ├── argentina_provincias.geojson
│   ├── us_states.geojson
│   ├── c2022_tp_salud_c1.xlsx (Censo INDEC)
│   ├── cuadros_definitivos_enfr_2018.xls (ENFR)
│   ├── cuadros_informe_pobreza_03_26.xls (EPH INDEC)
│   ├── serie_nbi_2022.xlsx (NBI INDEC)
│   └── 📖 README_DATOS.md
│
├── 📁 Resultados/       <-- Todas las tablas (.csv) y figuras de alta resolución (220 DPI)
│   ├── tabla1_resumen_comparativo.csv
│   ├── tabla2_ols_coeficientes.csv
│   ├── tabla3_diagnostico_modelos.csv
│   ├── tabla4_ranking_extremos.csv
│   ├── tabla_comparativa_resumen.csv
│   ├── figura1_mapas_comparativos.png
│   ├── figura2_factores_riesgo.png
│   ├── figura3_brecha_tratamiento.png
│   ├── figura4_matriz_correlaciones.png
│   ├── figura5_modelos_dispersion.png
│   ├── figura_comparativa_argentina_usa.png
│   └── 📖 README_RESULTADOS.md
│
├── 📁 Paper/            <-- Manuscrito formal de ~10 páginas para el CIITI 2026
│   ├── Paper_Comparativo_Argentina_USA_2026.docx (📄 Formato Word IEEE oficial)
│   ├── Paper_Comparativo_Argentina_USA.md        (📝 Manuscrito en Markdown)
│   └── 📖 README_PAPER.md
│
├── 📁 Pipeline/         <-- Script reproducible de análisis econométrico y compilación
│   ├── pipeline_comparativa_argentina_usa.py
│   └── 📖 README_PIPELINE.md
│
└── 📖 PROPUESTA_COMPARATIVA.md
```

---

## 8. Enlaces Directos a los Documentos `.md` de Cada Carpeta

1. 📖 [**`Datos/README_DATOS.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Datos/README_DATOS.md): Detalle de fuentes INDEC, ENFR y CDC BRFSS, variables y justificaciones de inclusión/exclusión.
2. 📖 [**`Resultados/README_RESULTADOS.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/README_RESULTADOS.md): Análisis exhaustivo de las 5 tablas y las 6 figuras comparativas.
3. 📖 [**`Paper/README_PAPER.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Paper/README_PAPER.md): Resumen del paper de ~10 páginas, hipótesis y referencias bibliográficas IEEE.
4. 📖 [**`Pipeline/README_PIPELINE.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Pipeline/README_PIPELINE.md): Arquitectura del motor de procesamiento en 5 pasos reproducibles.


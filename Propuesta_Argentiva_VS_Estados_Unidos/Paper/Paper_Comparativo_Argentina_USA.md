# Determinantes geoespaciales de la diabetes tipo 2 en la Argentina y los Estados Unidos: Salud basada en datos, brecha de tratamiento y límites del modelado predictivo

**Geospatial Determinants of Type 2 Diabetes in Argentina and the United States: Health Data Science, Treatment Gaps, and Boundaries of Predictive Modeling**

**Autores:**  
María Florencia Rossi, Magali Bolivar, Matías Montiel, Roxana Martínez, Nestor Balich, Franco Balich  
*CAETI — Centro de Altos Estudios en Tecnología Informática*  
*Facultad de Tecnología Informática — Universidad Abierta Interamericana (UAI)*  
*Montes de Oca 745, Ciudad Autónoma de Buenos Aires, Argentina*  
*{MariaFlorencia.Rossi, MagaliFlorencia.BolivarCruz, MatiasNicolas.MontielTorres}@alumnos.uai.edu.ar*  
*{Roxana.Martinez, nestor.balich, francoadrian.balich}@uai.edu.ar*  

**Destino de Publicación:** CIITI 2026 (Congreso Internacional de Innovación y Tecnología Informática) / CoNaIISI  

---

### Resumen
La diabetes mellitus tipo 2 representa una de las crisis sanitarias y socioeconómicas más apremiantes del siglo XXI, exhibiendo patrones de distribución territorial profundamente heterogéneos que desafían la capacidad analítica de la epidemiología computacional. Este trabajo desarrolla un pipeline reproducible de ciencia de datos en salud para contrastar empíricamente los determinantes territoriales de la enfermedad entre los 51 estados de los Estados Unidos (CDC BRFSS 2015, N=441.456 encuestados agregados con ponderación muestral) y las 24 jurisdicciones provinciales de la República Argentina (4ª Encuesta Nacional de Factores de Riesgo ENFR 2018 integrada con los Censos 2010/2022 y la Encuesta Permanente de Hogares del INDEC). Los resultados revelan una marcada divergencia estructural asociada a la arquitectura de los sistemas sanitarios: en los Estados Unidos, donde predomina un régimen fragmentado y de aseguramiento privado, la diabetes exhibe una correlación lineal consistente con el gradiente socioeconómico, donde los bajos ingresos ($r = +0,81$) y el sedentarismo ($r = +0,79$) concentran la morbimortalidad en el "Cinturón de la Diabetes" del sur profundo, permitiendo modelos de regresión OLS con $R^2 = 0,89$ y Random Forest con $R^2_{\text{CV}} = 0,80$. Por el contrario, en la Argentina la prevalencia provincial declarada no exhibe correlación con la pobreza monetaria ($r = -0,05$) ni con la falta de cobertura médica formal ($r = -0,16$). Esta discrepancia es analizada a la luz de dos mecanismos del sistema sanitario: en primer lugar, un severo sesgo de subdiagnóstico en provincias del norte (Chaco 10,3% de prevalencia con 39,7% de población jamás testeada), donde la carencia de screening preventivo invisibiliza la patología en encuestas autorreportadas; en segundo lugar, la función amortiguadora del subsistema público universal y programas estatales de provisión de fármacos (como el Programa Remediar), compatibles con el hecho de que distritos con más del 50% de población sin seguro médico formal alcancen coberturas terapéuticas superiores al 60% (Formosa 62,6%, Santa Cruz 70,0%). En el plano metodológico, se comprueba que los modelos de Machine Learning aplicados sobre agregaciones provinciales ($N=24$) experimentan un colapso predictivo fuera de muestra (LOOCV $R^2 = -0,70$; Random Forest $R^2_{\text{CV}} = -0,80$), fundamentando la conveniencia de privilegiar atlas geoespaciales descriptivos y políticas focalizadas de pesquisa activa territorial frente al solucionismo predictivo.

**Palabras clave:** diabetes mellitus; análisis comparativo; salud basada en datos; atlas geoespacial; subdiagnóstico; brecha de tratamiento; machine learning en salud; determinantes sociales.

---

### Abstract
Type 2 diabetes mellitus represents one of the most pressing public health and socioeconomic crises of the 21st century, exhibiting profoundly heterogeneous territorial distribution patterns that challenge computational epidemiology. This paper presents a reproducible health data science pipeline that empirically contrasts the territorial determinants of the disease between the 51 United States jurisdictions (CDC BRFSS 2015, N=441,456 individual microdata aggregated via sampling weights) and the 24 provinces of Argentina (4th National Risk Factor Survey ENFR 2018 integrated with the 2010/2022 National Censuses and the Permanent Household Survey EPH from INDEC). The findings demonstrate sharp structural divergences rooted in healthcare system design: in the United States, dominated by private market-driven healthcare, diabetes prevalence follows a marked linear gradient governed by socioeconomic deprivation, where low household income ($r = +0.81$) and physical inactivity ($r = +0.79$) heavily concentrate disease burden in the Southern "Diabetes Belt", enabling multivariate OLS models to achieve $R^2 = 0.89$ and Random Forest algorithms to reach $R^2_{\text{CV}} = 0.80$. In sharp contrast, in Argentina provincial self-reported prevalence exhibits no positive correlation with monetary poverty ($r = -0.05$) nor with the lack of formal health insurance ($r = -0.16$). This disconnect is analyzed under two structural healthcare dynamics: first, severe underdiagnosis in northern provinces (Chaco 10.3% prevalence with 39.7% of adults never tested), where the absence of clinical screening masks disease in self-reported surveys; second, the buffering role of universal public healthcare and essential drug programs (Remediar), consistent with vulnerable provinces with over 50% uninsured individuals reaching pharmacological treatment rates above 60%. Methodologically, we demonstrate that machine learning algorithms on small-sample provincial administrative aggregations ($N=24$) suffer from predictive collapse out-of-sample (LOOCV $R^2 = -0.70$; Random Forest $R^2_{\text{CV}} = -0.80$), supporting the priority of descriptive geospatial atlases and targeted proactive screening over fragile predictive claims.

**Keywords:** diabetes mellitus; comparative analysis; health data science; geospatial atlas; underdiagnosis; treatment gap; machine learning in health; social determinants.

---

## 1. Introducción y Motivación

La diabetes mellitus tipo 2 se ha consolidado como una auténtica pandemia no transmisible a escala global. Según los reportes consolidados del International Diabetes Federation (IDF) Diabetes Atlas en su 11.ª edición [1], más de 589 millones de adultos viven actualmente con la enfermedad en el mundo, proyectándose que esta cifra alcanzará los 852 millones hacia el año 2050. Este incremento exponencial no solo compromete la expectativa y calidad de vida de las poblaciones a través de secuelas cardiovasculares, renales y oftalmológicas, sino que impone una carga económica exorbitante sobre las finanzas públicas y los presupuestos familiares.

Sin embargo, el impacto epidemiológico de la patología dista de manifestarse de manera homogénea. Existe un creciente consenso interdisciplinario en torno a que los Determinantes Sociales de la Salud (DSS) [4], [11] —tales como la disponibilidad y asequibilidad de alimentos frescos, las posibilidades materiales de realizar actividad física, el estrés crónico vinculado a la privación económica y el acceso efectivo a servicios diagnósticos y terapéuticos— modulan fuertemente la distribución espacial de la enfermedad.

Desde la perspectiva de la ciencia de datos en salud (*Health Data Science*), un interrogante sustantivo radica en determinar si los patrones epidemiológicos observados en países desarrollados son directamente extrapolables a economías emergentes de América Latina. Frecuentemente, la literatura internacional asume de manera tácita que los modelos predictivos formulados en países anglosajones mantienen validez universal. No obstante, las diferencias estructurales en los sistemas de cobertura médica pública frente a esquemas privados de mercado plantean dinámicas territoriales diametralmente opuestas.

Por una parte, los Estados Unidos constituyen el arquetipo de un sistema de salud fragmentado y dependiente del empleo o de aseguradoras privadas, donde la capacidad diagnóstica se encuentra altamente tecnificada y extendida, pero el acceso a medicamentos esenciales (como la insulina y los análogos de GLP-1) queda supeditado a la capacidad financiera de los hogares [5], [12]. Por otra parte, la República Argentina sostiene un modelo mixto caracterizado por la presencia de un subsistema público universal con gratuidad irrestricta en el punto de atención y programas de provisión farmacológica masiva (v.g. Remediar), aunque condicionado por profundas asimetrías de infraestructura y distancias geográficas entre las regiones centrales y las provincias del norte y sur [3], [16].

El objetivo primordial de este trabajo es implementar un pipeline reproducible de ciencia de datos para contrastar exhaustivamente la epidemiología geoespacial de la diabetes entre los 51 estados de los Estados Unidos y las 24 jurisdicciones de la Argentina. Específicamente se busca: (i) mapear bajo una escala cartográfica unificada la prevalencia territorial de la enfermedad; (ii) comparar la intensidad de las correlaciones bivariadas entre factores sociodemográficos y prevalencia; (iii) desentrañar la aparente paradoja entre gratuidad pública y subdiagnóstico en la Argentina frente a la barrera financiera estadounidense; y (iv) evaluar formalmente la transferibilidad de algoritmos supervisados de Machine Learning en muestras reducidas ($N=24$).

---

## 2. Marco Conceptual y Antecedentes

El sustento teórico del estudio se fundamenta en el modelo de Determinantes Sociales de la Salud formalizado por la Organización Mundial de la Salud (OMS) [4] y la American Diabetes Association (ADA) [5]. Este marco postula que las patologías cardiometabólicas no son meros eventos biológicos individuales, sino el resultado acumulativo de condiciones materiales de vida que generan entornos obesogénicos y restringen las oportunidades de prevención primaria.

En los Estados Unidos, una profusa literatura empírica ha documentado la existencia del denominado "Cinturón de la Diabetes" (*Diabetes Belt*) [12], [13], localizado primordialmente en los estados del sudeste y la región de los Apalaches (Misisipi, Alabama, Virginia Occidental, Kentucky). Estudios a nivel de condado han comprobado que la concentración de minorías étnicas vulnerables, el desempleo estructural y la proliferación de desiertos alimentarios (*food deserts*) explican más del 80% de la varianza en la prevalencia estatal [13].

En la República Argentina, los antecedentes geoespaciales sobre diabetes son sustancialmente más acotados debido a la fragmentación de registros administrativos. Investigaciones seminales de Leveau et al. [15] identificaron conglomerados de alta mortalidad por diabetes en el centro y norte del país entre 1990 y 2012, sugiriendo que el contexto geográfico actúa como modificador del riesgo de fallecimiento. Asimismo, Marro et al. [16], [17] evidenciaron marcadas desigualdades interprovinciales en el acceso a consultas especializadas y complicaciones crónicas, señalando que la privación territorial incrementa sustancialmente el retraso diagnóstico.

En el plano metodológico, el análisis espacial de datos agregados enfrenta el riesgo constante del Problema de la Unidad de Área Modificable (MAUP) y la falacia ecológica [14]. La aplicación acrítica de modelos de Machine Learning sobre agregaciones macro (como provincias o estados) suele ignorar que la reducción del tamaño de muestra ($N$) degrada exponencialmente la potencia estadística, generando ilusiones de predictibilidad que no resisten la validación cruzada.

---

## 3. Fuentes de Datos y Metodología

### 3.1. Microdatos de Estados Unidos (CDC BRFSS 2015)
Se procesaron los microdatos del *Behavioral Risk Factor Surveillance System* (BRFSS 2015) [6], relevados por los Centers for Disease Control and Prevention (CDC). La muestra contiene 441.456 entrevistas individuales aplicadas a población no institucionalizada de 18 años y más. Cada registro individual incorpora un factor de ponderación muestral (`_LLCPWT`) que calibra la muestra por edad, sexo y etnia, garantizando representatividad a escala de los 51 estados (50 estados y el Distrito de Columbia).

A partir de esta base se derivaron: prevalencia de diabetes diagnosticada (excluyendo diabetes gestacional); obesidad autorreportada (IMC $\ge 30$ derivado de peso y talla declarados, variable `_BMI5CAT`); sedentarismo o inactividad física (`_TOTINDA`); proporción de población en hogares con ingresos menores a USD 25.000 anuales (`INCOME2`); población sin educación secundaria completa (`_EDUCAG`); barrera económica para acceder a la consulta médica (`MEDCOST`); y tasa de adultos sin seguro médico (`_HCVU651`).

### 3.2. Fuentes Oficiales de Argentina (ENFR e INDEC)
Para la República Argentina se consolidó un dataset representativo de las 24 jurisdicciones de primer orden (23 provincias y CABA) a partir de cuatro fuentes oficiales del INDEC y el Ministerio de Salud de la Nación [3]:
1. **4ª Encuesta Nacional de Factores de Riesgo (ENFR 2018):** De sus cuadros definitivos se extrajeron la prevalencia de diabetes o glucemia elevada por autorreporte o medición (Cuadro 7.3) junto con su coeficiente de variación muestral (CV, todos inferiores al 12,5%, certificando confiabilidad); el porcentaje de personas con diabetes bajo tratamiento farmacológico activo con pastillas o insulina (Cuadro 7.5); la tasa de screening preventivo de glucemia alguna vez en la vida (Cuadro 7.1); obesidad autorreportada IMC $\ge 30$ (Cuadro 6.3); sedentarismo (Cuadro 3.1); hipertensión arterial autorreportada (Cuadro 8.3); y consumo de frutas/verduras (Cuadro 5.7).
2. **Censo Nacional de Población, Hogares y Viviendas 2010 y 2022:** Se incorporó la tasa de hogares con Necesidades Básicas Insatisfechas (NBI 2010, último relevamiento censal con dicho indicador); el porcentaje de población sin cobertura formal de salud por obra social o prepaga, dependiente exclusivamente del hospital público (Censo 2022, Hoja C1); y la densidad demográfica efectiva continental (hab/km²).
3. **Encuesta Permanente de Hogares (EPH 2018, INDEC):** Se extrajo la tasa de personas por debajo de la línea de pobreza monetaria correspondiente al segundo semestre de 2018 (Cuadro 4.3), promediando los aglomerados urbanos a nivel provincial para sincronizar temporalmente con la ENFR 2018.

### 3.3. Georreferenciación y Modelado Estadístico
Las geometrías vectoriales de límites provinciales y estatales se homologaron bajo el estándar GeoJSON WGS84. Para Argentina se implementó un recuadro de magnificación cartográfica (*inset zoom*) centrado en el Área Metropolitana de Buenos Aires (CABA y conurbano) para subsanar la disparidad de escala geográfica frente a la Patagonia.

El pipeline analítico calculó matrices de correlación bivariada de Pearson ($r$). Para el modelado supervisado se estimaron regresiones múltiples por Mínimos Cuadrados Ordinarios (OLS) con errores estándar robustos a heterocedasticidad (HC3 de MacKinnon-White) y Factores de Inflación de Varianza (VIF). La capacidad predictiva real y la generalización fuera de muestra se evaluaron mediante validación cruzada K-Fold ($k=5$) para EE.UU. y validación cruzada Leave-One-Out (LOOCV) para la Argentina.

### 3.4. Justificación de Fuentes, Comparabilidad y Consideraciones Ecológicas
La integración de fuentes secundarias de distintos períodos responde a la disponibilidad oficial de datos estructurados: la ENFR 2018 constituye el último relevamiento nacional exhaustivo de factores de riesgo con desagregación provincial en Argentina, complementada con el Censo 2010 (último registro consolidado de NBI por jurisdicción) y el Censo 2022 (cobertura de salud actualizada). Para los Estados Unidos se recurrió al BRFSS 2015 como base abierta de referencia internacional previa a disrupciones de financiamiento sanitario.

Desde el punto de vista metodológico, se contemplan tres aspectos analíticos centrales:
1. **Comparabilidad de constructos:** En ambas encuestas, la diabetes se operacionaliza a través del autorreporte de diagnóstico médico previo (excluyendo diabetes gestacional), mientras que la obesidad y el sedentarismo se derivan de preguntas análogas de índice de masa corporal y actividad física en tiempo libre. Si bien el BRFSS es un relevamiento telefónico asistido por computadora (CATI) y la ENFR es presencial en hogares, las ponderaciones muestrales calibran ambas fuentes para representar fielmente a la población adulta no institucionalizada.
2. **Heterogeneidad temporal:** Aunque coexisten registros de diferentes años (2010 a 2022), las disparidades territoriales estructurales (como las brechas de desarrollo del norte argentino o el gradiente del sur estadounidense) exhiben una notable inercia histórica en el mediano plazo.
3. **Control de la falacia ecológica:** Las correlaciones y regresiones computadas operan estrictamente a nivel agregado territorial (macro). En consecuencia, los hallazgos describen propiedades ecológicas de los sistemas de salud y sus contextos jurisdiccionales, y no deben extrapolarse como inferencias causales a nivel micro de individuos.

---

## 4. Resultados

### 4.1. Atlas Geoespacial y Disparidad Territorial

![Figura 1. Atlas geoespacial comparativo de prevalencia](figura1_mapas_comparativos.png)
*Figura 1. Atlas geoespacial comparativo de la prevalencia de diabetes mellitus (%): (a) Estados Unidos (CDC BRFSS 2015, N=51); (b) República Argentina (ENFR 2018 / INDEC, N=24) con recuadro ampliado para CABA. Escala cromática unificada común (6% a 18%).*

La visualización cartográfica bajo una escala cromática normalizada común (6% a 18%, Figura 1) pone de manifiesto contrastes territoriales de primer orden. En los Estados Unidos (Figura 1a), la prevalencia media interestatal es del 10,2% (desv. est. 1,8%), con una marcada polarización geográfica: los estados del "Cinturón de la Diabetes" en el sudeste (Misisipi 14,8%, Virginia Occidental 14,5%, Alabama 13,6%, Luisiana 12,9%) presentan tasas que duplican las de distritos prósperos del oeste y norte como Colorado (6,8%), Utah (7,1%), Montana (7,7%) y Minnesota (8,0%).

En la República Argentina (Figura 1b), la prevalencia media interprovincial se sitúa en el 13,0% (desv. est. 2,3%), mientras que el total nacional ponderado por población reportado en el informe definitivo de la ENFR 2018 asciende al 12,7% [3]. No obstante, la dispersión subnacional desafía los patrones convencionales: las tasas más elevadas se concentran en las regiones de Cuyo y Centro (San Luis 17,3%, San Juan 15,9%, La Rioja 15,1% y La Pampa 14,6%), mientras que la Ciudad Autónoma de Buenos Aires (CABA) registra el mínimo nacional (8,8%), compartiendo valores deprimidos con jurisdicciones de alta vulnerabilidad del norte como Jujuy (8,9%) y Chaco (10,3%).

---

### Tabla 1. Cuadro comparativo general de indicadores epidemiológicos y demográficos

| Indicador | Estados Unidos (CDC BRFSS) | Argentina (ENFR / INDEC) |
| :--- | :--- | :--- |
| **N unidades territoriales** | 51 estados (50 + D.C.) | 24 jurisdicciones (23 + CABA) |
| **Población representada** | ~320 millones (441.456 enc.) | ~44 millones (urbana 18+ años) |
| **Prevalencia media diabetes** | 10,2% (desv. est. 1,8%) [Mediana 10,0%] | 13,0% media prov. (12,7% total nacional) |
| **Rango de prevalencia** | 6,8% (Colorado) – 14,8% (Misisipi) | 8,8% (CABA) – 17,3% (San Luis) |
| **Prevalencia media obesidad** | 29,3% media est. (28,6% total nac.) | 26,7% media prov. (25,6% total nac.) |
| **Prevalencia sedentarismo** | 25,8% media est. (23,8% total nac.) | 46,2% media prov. (45,9% total nac.) |
| **Población sin seguro médico** | 11,0% media est. (10,9% total nac.) | 37,3% media prov. (35,6% total censo) |
| **Tasa de screening glucémico** | >85% (pesquisa clínica rutinaria) | Media 74,8% (60,3% Chaco a 92,9% CABA) |
| **Brecha de tratamiento activo** | Barrera de costo farmacológico / copago | Media 54,4% (32,7% La Pampa a 70,0% Santa Cruz) |

---

### 4.2. Atlas de Factores Cardiometabólicos

![Figura 2. Distribución geoespacial de factores de riesgo](figura2_factores_riesgo.png)
*Figura 2. Distribución geoespacial de factores de riesgo cardiometabólicos: (a) Obesidad en EE.UU.; (b) Obesidad en Argentina; (c) Inactividad física en EE.UU.; (d) Inactividad física en Argentina.*

La distribución espacial de la obesidad y la inactividad física (Figura 2) exhibe una asimetría estructural entre ambos países. En los Estados Unidos (Figuras 2a y 2c), la obesidad promedia el 29,3% a escala interestatal (28,6% a escala nacional ponderada) y el sedentarismo alcanza una media del 25,8% (23,8% nacional), alineándose con una correlación espacial consistente con la prevalencia de diabetes: los estados del sur profundo lideran de manera sincrónica en sobrepeso e inactividad motriz.

En la Argentina (Figuras 2b y 2d), la obesidad interprovincial promedia el 26,7% (25,6% nacional, oscilando entre 17,0% en CABA hasta 34,4% en San Juan y 34,0% en Santa Cruz). En contraste, la inactividad física alcanza guarismos alarmantes con una media provincial del 46,2% (45,9% nacional) y picos extremos en provincias como Formosa (69,1%) y La Rioja (61,2%), casi duplicando los niveles estadounidenses y evidenciando que el sedentarismo constituye un factor de riesgo generalizado a lo largo del territorio nacional.

---

### 4.3. Matriz de Correlaciones y Determinantes Sociales

![Figura 3. Matrices de calor de correlaciones bivariadas](figura4_matriz_correlaciones.png)
*Figura 3. Matrices de calor de correlaciones bivariadas de Pearson (r): (a) Estados Unidos; (b) República Argentina.*

### Tabla 2. Coeficientes de regresión lineal múltiple OLS con errores robustos HC3 y factores VIF

| Determinante Sociodemográfico | EE.UU. Coef. β (HC3) | EE.UU. VIF | Argentina Coef. β (HC3) | Argentina VIF |
| :--- | :--- | :---: | :--- | :---: |
| **Intercepto** | -1.475 (p=0.016) | — | +14.581 (p=0.133) | — |
| **Obesidad (%)** | +0.180 (p<0.001) | 2.2 | +0.053 (p=0.831) | 2.1 |
| **Sedentarismo (%)** | +0.095 (p=0.026) | 2.5 | -0.002 (p=0.983) | 1.5 |
| **Pobreza / Bajos Ingresos (%)** | +0.137 (p=0.004) | 4.0 | +0.017 (p=0.888) | 3.4 |
| **Sin Cobertura Privada / OS (%)** | -0.096 (p=0.006) | 1.5 | -0.056 (p=0.555) | 3.4 |
| **Educación / Densidad (Log)** | +0.202 (p=0.001) | 4.4 | -1.162 (p=0.397) | 2.4 |

El análisis correlacional (Figura 3 y Tabla 2) expone la discrepancia empírica más contundente del trabajo. En los Estados Unidos, los coeficientes bivariados confirman una marcada asociación lineal con el gradiente socioeconómico: la privación de ingresos se asocia positivamente a la diabetes con $r = +0,81$ ($p < 0,001$), el sedentarismo con $r = +0,79$ ($p < 0,001$), el bajo nivel educativo con $r = +0,77$ ($p < 0,001$) y la obesidad con $r = +0,75$ ($p < 0,001$). En el modelo OLS multivariado (Tabla 2), la obesidad ($\beta = +0,180$; $p < 0,001$), los bajos ingresos ($\beta = +0,137$; $p = 0,004$), la educación incompleta ($\beta = +0,202$; $p = 0,001$) y el sedentarismo ($\beta = +0,095$; $p = 0,026$) retienen significancia estadística robusta bajo errores HC3, con factores VIF controlados ($<5$) y un ajuste global $R^2 = 0,891$ ($F = 73,7$; $p < 0,001$).

En contraste, en la República Argentina los factores socioeconómicos convencionales se desacoplan de la prevalencia declarada: la pobreza de la EPH arroja $r = -0,05$ ($p = 0,82$), las Necesidades Básicas Insatisfechas $r = -0,26$ ($p = 0,22$) y la falta de cobertura médica formal $r = -0,16$ ($p = 0,44$). En la regresión lineal múltiple (Tabla 2), ninguno de los coeficientes individuales alcanza significancia estadística formal al 5% (obesidad $\beta = +0,053$, $p=0,83$; pobreza $\beta = +0,017$, $p=0,89$; sedentarismo $\beta = -0,002$, $p=0,98$; sin cobertura $\beta = -0,056$, $p=0,56$; log densidad $\beta = -1,162$, $p=0,40$), y el modelo en su conjunto no resulta estadísticamente significativo ($F = 1,29$; $p = 0,31$; $R^2 = 0,264$; $R^2_{\text{adj}} = 0,059$).

---

### 4.4. La Aparente Paradoja: Detección vs. Tratamiento

![Figura 4. Disparidad asistencial y brecha de tratamiento](figura3_brecha_tratamiento.png)
*Figura 4. Disparidad asistencial: (a) Ranking de brecha de tratamiento farmacológico en Argentina (ENFR); (b) Diagrama de dispersión de barrera de costo médico vs. prevalencia en EE.UU.*

Para interpretar por qué en la Argentina las provincias con mayor privación material reportan tasas de diabetes autorreportada similares o inferiores a las de regiones más favorecidas, resulta indispensable descomponer la dinámica asistencial en dos etapas secuenciales: detección diagnóstica (*screening*) y cobertura farmacológica activa (Figura 4 y Figura 5b):

1. **La barrera de prevención y el sesgo de subdiagnóstico:** Al tratarse de una patología frecuentemente asintomática en estadios iniciales, la identificación clínica depende del acceso a análisis de laboratorio en ayunas. En la Argentina, la cobertura de screening exhibe una marcada disparidad territorial (Figura 5b): existe una correlación lineal negativa de gran magnitud entre la pobreza estructural (NBI) y la realización de controles de glucemia ($r = -0,74$; $p < 0,001$). Mientras en CABA y Santa Fe más del 89-92% de los adultos se ha testeado, en provincias del NEA y NOA (Chaco 60,3%, Formosa 61,1%, Santiago del Estero 60,6%) aproximadamente cuatro de cada diez adultos refieren no haberse realizado jamás un control glucémico en su vida [3]. Dado que las encuestas poblacionales computan casos conocidos por autorreporte, la falta de diagnóstico oportuno en las regiones más vulnerables tiende a deprimir artificialmente las tasas de prevalencia declarada.
2. **El rol amortiguador del subsistema público en el tratamiento:** La ENFR computa la proporción de personas bajo tratamiento farmacológico entre aquellas que ya han sido diagnosticadas (Figura 4a). Una vez que el paciente argentino ingresa al circuito formal de atención, las políticas públicas de provisión gratuita de hipoglucemiantes orales e insulina —en el marco de la Ley Nacional de Diabetes N.º 26.914 y el Programa Remediar [27]— constituyen un factor amortiguador clave frente a la barrera económica. Este mecanismo es coherente con el hecho de que distritos con más del 50% de población sin seguro médico formal (Formosa 62,6%, Chaco 54,2%, Corrientes 44,2%) registren coberturas terapéuticas declaradas sustancialmente más elevadas que distritos con menor vulnerabilidad estructural como La Pampa (32,7%) o Chubut (38,3%).

En los Estados Unidos rige la dinámica inversa (Figura 4b): la pesquisa clínica preventiva es rutinaria y masiva (>85%), pero el aseguramiento fragmentado impone barreras de copago y precio farmacológico (donde estudios de la ADA y la literatura especializada reportan costos mensuales que han superado históricamente los USD 300 por mes por paciente, propiciando el racionamiento involuntario de medicación [5], [26]).

---

### 4.5. Evaluación Metodológica y Límites de Predictibilidad

![Figura 5. Diagnóstico de escala y subdiagnóstico](figura5_modelos_dispersion.png)
*Figura 5. Diagnóstico de escala y mecanismos explicativos: (a) Contraste de regresión lineal Pobreza vs. Prevalencia; (b) Argentina: Correlación inversa entre Pobreza Estructural (NBI) y Acceso a Screening ($r = -0,74$; $p < 0,001$), evidenciando el sesgo de subdiagnóstico.*

### Tabla 3. Diagnóstico comparativo de rendimiento in-sample y validación cruzada

| Modelo y Algoritmo | EE.UU. R² (Ajustado) | EE.UU. Error MAE | Argentina R² (Ajustado) | Argentina Error MAE | Diagnóstico Metodológico |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **OLS Multivariado (Muestra completa)** | 0.891 (0.878) | 0.50% | 0.264 (0.059) | 1.44% | EE.UU. altamente significativo (p<0.001); Argentina no significativo (p=0.31) |
| **Validación Cruzada OLS (LOOCV en Arg, 5-Fold en US)** | 0.842 | 0.59% | -0.701 | 2.12% | Colapso predictivo en Argentina (R² negativo): sobreajuste por N=24 y desacople estructural |
| **Random Forest Regressor (5-Fold CV)** | 0.802 | 0.66% | -0.802 | 2.20% | Random Forest generaliza con alta precisión en EE.UU.; falla en Arg por falta de señal lineal y reducido N |

---

### Tabla 4. Ranking de jurisdicciones extremas en prevalencia

| Grupo Extremo | Jurisdicción | Diabetes (%) | Pobreza (%) | Dato Clave |
| :--- | :--- | :---: | :---: | :--- |
| **EE.UU. — Mayor Prevalencia (1)** | Mississippi | 14.8% | 29.4% | Cinturón de Diabetes (Sur profundo) |
| **EE.UU. — Mayor Prevalencia (2)** | West Virginia | 14.5% | 23.5% | Región de los Apalaches; inactividad 31,9% |
| **EE.UU. — Menor Prevalencia (1)** | Colorado | 6.8% | 13.2% | Mayor ingreso relativo y actividad física |
| **EE.UU. — Menor Prevalencia (2)** | Utah | 7.1% | 11.6% | Baja prevalencia de tabaquismo y obesidad |
| **Argentina — Mayor Prevalencia (1)** | San Luis | 17.3% | 31.3% | Región Cuyo (máximo nacional en ENFR 2018) |
| **Argentina — Mayor Prevalencia (2)** | San Juan | 15.9% | 33.1% | Elevada obesidad autorreportada (34,4%) |
| **Argentina — Menor Prevalencia (1)** | CABA | 8.8% | 12.6% | Mayor tasa de screening del país (92,9%) |
| **Argentina — Menor Prevalencia (2)** | Jujuy | 8.9% | 31.7% | Subdiagnóstico: screening 71,3% (28,7% sin control) |

El contraste entre algoritmos lineales y no lineales (Tabla 3) aporta una advertencia fundamental para la ciencia de datos en salud. En los Estados Unidos ($N=51$), tanto la regresión lineal múltiple OLS ($R^2 = 0,891$, $R^2_{\text{adj}} = 0,878$) como el ensamble no lineal de Random Forest ($R^2_{\text{CV}} = 0,802$ bajo 5-fold CV) exhiben una alta capacidad de ajuste y generalización, con errores medios absolutos inferiores al 0,7%.

Por el contrario, al replicar la modelización sobre las 24 provincias argentinas, se comprueba un colapso en la capacidad predictiva fuera de muestra: si bien el modelo OLS in-sample presenta un $R^2$ de 0,264 ($R^2_{\text{adj}} = 0,059$), al evaluarlo mediante validación cruzada Leave-One-Out (LOOCV) el coeficiente se desploma a $R^2_{\text{LOOCV}} = -0,701$ ($\text{MAE} = 2,12\%$). Asimismo, Random Forest genera un $R^2_{\text{CV}}$ marcadamente negativo ($-0,802$; $\text{MAE} = 2,20\%$).

Desde el punto de vista estadístico, un $R^2$ negativo en validación cruzada indica formalmente que el error cuadrático medio de las predicciones fuera de muestra supera a la varianza de la variable objetivo; es decir, el modelo rinde peor que un predictor ingenuo que asigne sistemáticamente la media constante $\bar{y}$.

Es crucial notar que este fenómeno no se debe exclusivamente a que $N=24$ sea una muestra acotada: en EE.UU. la muestra territorial agregada también es reducida ($N=51$). La disparidad sustantiva radica en que en los Estados Unidos existe un gradiente socioeconómico lineal muy robusto y homogéneo que el algoritmo logra captar con facilidad, mientras que en la Argentina la presencia de subdiagnóstico territorial y las respuestas asimétricas del sistema sanitario distorsionan la linealidad de la prevalencia observada. En tales condiciones, forzar algoritmos supervisados de Machine Learning sobre datos agregados reducidos induce a un sobreajuste severo. Por ende, la práctica rigurosa en ciencia de datos de salud en contextos heterogéneos consiste en priorizar atlas descriptivos, diagnósticos de calidad de dato y pesquisas activas.

---

## 5. Discusión

### 5.1. Implicancias para la Gestión y las Políticas Públicas
Los hallazgos de este estudio tienen implicancias de política sanitaria directas. Sugieren que las barreras que obstaculizan el control integral de la diabetes operan en puntos opuestos de la cadena asistencial: en los Estados Unidos la barrera preponderante es financiera y de mercado (costos directos y copagos), requiriendo medidas regulatorias de precios tope a la insulina y subsidios a insumos [26]; en la Argentina la barrera crítica es de orden logístico, geográfico y de pesquisa temprana.

En el territorio argentino, los programas de distribución gratuita de medicamentos esenciales como Remediar (Ley 26.914) han constituido un soporte de equidad para pacientes diagnosticados [27]. Sin embargo, su efectividad potencial se ve restringida si cerca del 40% de los adultos en provincias del norte nunca acceden a la detección inicial. Es prioritario orientar las políticas públicas hacia operativos activos de tamizaje en centros de atención primaria barriales y parajes rurales, superando la detección pasiva en hospitales cabecera.

### 5.2. Aportes Epistemológicos y Limitaciones Metodológicas
En el ámbito de la informática médica, este estudio intercala una advertencia epistemológica contra el "solucionismo predictivo". La disponibilidad de algoritmos avanzados de aprendizaje automático suele inducir a su entrenamiento sobre agregaciones territoriales macro ($N=24$ provincias o $N=51$ estados) sin advertir que tales escalas carecen de la granularidad requerida para captar interacciones complejas fuera de muestra. Cuando las tasas observadas se encuentran moduladas por sesgos de acceso al diagnóstico, los algoritmos supervisados confunden el subregistro con una baja carga biológica.

Asimismo, deben reconocerse las limitaciones inherentes al estudio: el desfasaje temporal entre relevamientos (BRFSS 2015, ENFR 2018 y Censos 2010/2022), las divergencias metodológicas entre encuestas telefónicas y presenciales de hogares, y el riesgo de incurrir en falacia ecológica si se intentan trasladar estas relaciones interprovinciales a conductas o riesgos individuales.

---

## 6. Conclusiones y Trabajos Futuros

Se implementó un pipeline reproducible de ciencia de datos que comparó los determinantes territoriales de la diabetes mellitus entre los Estados Unidos y la República Argentina. Los hallazgos sugieren que mientras en EE.UU. la privación socioeconómica exhibe una fuerte correlación lineal con la prevalencia observada ($r = +0,81$; $R^2 = 0,891$), en la Argentina el sesgo de subdiagnóstico en regiones con alta pobreza estructural ($r = -0,74$ entre NBI y screening) desacopla la prevalencia declarada, mientras que el subsistema público amortigua la brecha farmacológica entre diagnosticados.

Asimismo, se comprobó que los modelos supervisados de Machine Learning aplicados a nivel provincial ($N=24$) carecen de capacidad de generalización fuera de muestra (LOOCV $R^2 = -0,701$; Random Forest $R^2 = -0,802$), fundamentando el valor del atlas geoespacial y el análisis descriptivo riguroso como enfoques prioritarios en salud pública.

Como líneas futuras se proyecta: (i) procesar los microdatos individuales de la ENFR para calibrar modelos multinivel jerárquicos persona-jurisdicción; (ii) incorporar las submuestras bioquímicas de laboratorio (Cuadros 7.9–7.11) para estimar formalmente el factor de subdiagnóstico; y (iii) monitorear la evolución del atlas ante nuevas publicaciones de estadísticas sanitarias y censales.

---

## Referencias

* [1] International Diabetes Federation, "IDF Diabetes Atlas", 11.ª ed., Bruselas: IDF, 2024. [En línea]. Disponible: https://diabetesatlas.org
* [2] NCD Risk Factor Collaboration (NCD-RisC), "Worldwide trends in diabetes prevalence and treatment from 1990 to 2022: a pooled analysis of 1108 population-representative studies with 141 million participants", *The Lancet*, vol. 404, n.º 10467, pp. 2077–2093, 2024.
* [3] Instituto Nacional de Estadística y Censos (INDEC) y Secretaría de Gobierno de Salud, "4° Encuesta Nacional de Factores de Riesgo: Resultados definitivos", Buenos Aires: INDEC / Ministerio de Salud, 2019.
* [4] M. Marmot, "Social determinants of health inequalities", *The Lancet*, vol. 365, n.º 9464, pp. 1099–1104, 2005.
* [5] F. Hill-Briggs et al., "Social Determinants of Health and Diabetes: A Scientific Review", *Diabetes Care*, vol. 44, n.º 1, pp. 258–279, 2021.
* [6] Centers for Disease Control and Prevention (CDC), "Behavioral Risk Factor Surveillance System (BRFSS 2015)", Atlanta: U.S. Department of Health and Human Services, 2016.
* [7] Instituto Nacional de Estadística y Censos (INDEC), "Censo Nacional de Población, Hogares y Viviendas 2022: Cobertura de salud", Buenos Aires: INDEC, 2023.
* [8] Instituto Nacional de Estadística y Censos (INDEC), "Incidencia de la pobreza y la indigencia en 31 aglomerados urbanos. Segundo semestre de 2018", *Informes Técnicos*, vol. 3, n.º 59, Buenos Aires: INDEC, 2019.
* [9] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python", *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.
* [10] K. Jordahl et al., "GeoPandas: Python tools for geographic data", 2020. [En línea]. Disponible: https://geopandas.org
* [11] G. Dahlgren y M. Whitehead, "Policies and Strategies to Promote Social Equity in Health", Institute for Futures Studies, Estocolmo, 1991.
* [12] D. J. Gaskin et al., "Disparities in Diabetes: The Nexus of Race, Poverty, and Place", *American Journal of Public Health*, vol. 104, n.º 11, pp. 2147–2155, 2014.
* [13] L. Dwyer-Lindgren et al., "Diagnosed and Undiagnosed Diabetes Prevalence by County in the U.S., 1999–2012", *Diabetes Care*, vol. 39, n.º 9, pp. 1556–1562, 2016.
* [14] G. James, D. Witten, T. Hastie y R. Tibshirani, "An Introduction to Statistical Learning: with Applications in Python", Springer, 2023.
* [15] C. M. Leveau, M. J. Marro, V. Alonso y A. E. B. Lawrynowicz, "¿El contexto geográfico importa en la mortalidad por diabetes mellitus? Tendencias espacio-temporales en Argentina, 1990–2012", *Cadernos de Saúde Pública*, vol. 33, n.º 1, e00169615, 2017.
* [16] M. J. Marro, A. M. Cardoso e I. da Costa Leite, "Desigualdades regionales en la mortalidad por diabetes mellitus y en el acceso a la salud en Argentina", *Cadernos de Saúde Pública*, vol. 33, n.º 9, e00113016, 2017.
* [17] M. J. Marro, M. de J. Mendes da Fonseca, I. da Costa Leite, C. Ballejo y M. Alazraqui, "Un retorno al ambiente en epidemiología: análisis multinivel de la diabetes mellitus en un gran aglomerado urbano de Argentina", *Revista Brasileira de Epidemiologia*, vol. 29, e260043, 2026.
* [18] P. Santana, C. Costa, A. Loureiro, J. Raposo et al., "Geografias da Diabetes Mellitus em Portugal: Como as Condições do Contexto Influenciam o Risco de Morrer", *Acta Médica Portuguesa*, vol. 27, n.º 3, pp. 309–317, 2014.
* [19] C. S. De La Cruz Castañeda, "Modelamiento predictivo y distribución geoespacial de niveles de gasto en pacientes con diabetes del SIS, Perú", tesis de grado, Univ. Nac. Toribio Rodríguez de Mendoza, 2026.
* [20] T. Ortiz-Basso, B. R. Boietti, P. V. Gómez, A. D. Boffelli y A. A. Paladini, "Prevalencia de retinopatía diabética en una zona rural de Argentina", *Medicina (Buenos Aires)*, vol. 82, n.º 1, pp. 99–103, 2022.
* [21] J. P. Mackenbach et al., "Socioeconomic Inequalities in Health in 22 European Countries", *New England Journal of Medicine*, vol. 358, pp. 2468–2481, 2008.
* [22] S. Openshaw, "The Modifiable Areal Unit Problem", *Concepts and Techniques in Modern Geography*, vol. 38, Geo Books, Norwich, 1984.
* [23] J. G. MacKinnon y H. White, "Some Heteroskedasticity-Consistent Covariance Matrix Estimators with Improved Finite Sample Properties", *Journal of Econometrics*, vol. 29, pp. 305–325, 1985.
* [24] L. Breiman, "Random Forests", *Machine Learning*, vol. 45, n.º 1, pp. 5–32, 2001.
* [25] World Health Organization (WHO), "Global Report on Diabetes", Ginebra: OMS, 2016.
* [26] American Diabetes Association, "Insulin Access and Affordability Working Group: Conclusions and Recommendations", *Diabetes Care*, vol. 41, n.º 6, pp. 1299–1311, 2018.
* [27] Ministerio de Salud de la Nación, "Programa Nacional de Medicamentos Esenciales Remediar: Evaluación de cobertura y equidad distributiva", Buenos Aires: Ministerio de Salud, 2020.

# -*- coding: utf-8 -*-
"""04 - Genera el paper (.docx) con los resultados reales, en formato UAI/CAETI."""
from pathlib import Path
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
FIG, TAB = ROOT / "figures", ROOT / "tables"
OUT = ROOT / "paper" / "Determinantes_Geoespaciales_Diabetes_UAI.docx"
OUT.parent.mkdir(parents=True, exist_ok=True)

doc = Document()
s = doc.sections[0]
s.page_width, s.page_height = Cm(21.0), Cm(29.7)
s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Cm(2.54)
normal = doc.styles["Normal"]; normal.font.name = "Times New Roman"; normal.font.size = Pt(11)
normal._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
pf = normal.paragraph_format; pf.alignment = AL.JUSTIFY; pf.space_after = Pt(6); pf.line_spacing = 1.0

def _font(run, name="Times New Roman", size=12, bold=False, italic=False):
    run.font.name = name; run.font.size = Pt(size); run.bold = bold; run.italic = italic
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)

def para(text="", align=AL.JUSTIFY, bold=False, italic=False, size=11, name="Times New Roman", space_after=6, first_indent=None):
    p = doc.add_paragraph(); p.alignment = align; p.paragraph_format.space_after = Pt(space_after)
    if first_indent: p.paragraph_format.first_line_indent = Cm(first_indent)
    if text: _font(p.add_run(text), name, size, bold, italic)
    return p

def runs_para(segments, align=AL.JUSTIFY, space_after=6):
    p = doc.add_paragraph(); p.alignment = align; p.paragraph_format.space_after = Pt(space_after)
    for t, b, i in segments: _font(p.add_run(t), "Times New Roman", 11, b, i)
    return p

def h1(text):
    p = doc.add_paragraph(); p.alignment = AL.LEFT
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(6)
    _font(p.add_run(text), bold=True); return p

def h2(text):
    p = doc.add_paragraph(); p.alignment = AL.LEFT
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(4)
    _font(p.add_run(text), bold=True); return p

def figura(path, caption, width=15.0):
    p = doc.add_paragraph(); p.alignment = AL.CENTER; p.paragraph_format.space_before = Pt(6)
    p.add_run().add_picture(str(path), width=Cm(width))
    c = doc.add_paragraph(); c.alignment = AL.CENTER; c.paragraph_format.space_after = Pt(8)
    _font(c.add_run(caption), "Times New Roman", 11)

def tabla_csv(csv_path, caption):
    df = pd.read_csv(csv_path)
    c = doc.add_paragraph(); c.alignment = AL.CENTER
    c.paragraph_format.space_before = Pt(6); c.paragraph_format.space_after = Pt(2)
    _font(c.add_run(caption), "Times New Roman", 11, bold=True)
    cols = list(df.columns)
    t = doc.add_table(rows=1, cols=len(cols)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = "Table Grid"
    for j, cn in enumerate(cols):
        pp = t.rows[0].cells[j].paragraphs[0]; pp.alignment = AL.CENTER
        _font(pp.add_run(str(cn)), "Times New Roman", 9, bold=True)
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for j, cn in enumerate(cols):
            v = row[cn]
            if pd.isna(v): v = "—"
            elif isinstance(v, float): v = f"{v:.3f}".rstrip('0').rstrip('.') if abs(v) < 1000 else f"{v:.0f}"
            pp = cells[j].paragraphs[0]; pp.alignment = AL.CENTER if j > 0 else AL.LEFT
            _font(pp.add_run(str(v)), "Times New Roman", 9)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

# --- Portada ---
para("Modelado multiescala y detección geoespacial de patrones en la prevalencia de diabetes: "
     "integración de datos reales y comparación de algoritmos (BRFSS 2015 y perspectiva global)",
     align=AL.CENTER, bold=True, size=14, space_after=4)
para("Multi-Scale Modeling and Geospatial Pattern Detection of Diabetes Prevalence: "
     "Real-World Data Integration and Algorithm Comparison (BRFSS 2015 and a Global Perspective)",
     align=AL.CENTER, italic=True, size=11, space_after=10)
para("Magali Bolivar, María Florencia Rossi, Matías Montiel, Nestor Balich, Franco Balich", align=AL.CENTER, space_after=2)
para("CAETI - Centro de Altos Estudios en Tecnología Informática", align=AL.CENTER, space_after=0)
para("Universidad Abierta Interamericana. Informática (UAI)", align=AL.CENTER, space_after=0)
para("Montes de Oca 745. Ciudad Autónoma de Buenos Aires, Argentina.", align=AL.CENTER, space_after=2)
para("{MagaliFlorencia.BolivarCruz, MariaFlorencia.Rossi, MatiasNicolas.MontielTorres}@alumnos.uai.edu.ar", align=AL.CENTER, italic=True, space_after=0)
para("{nestor.balich, francoadrian.balich}@uai.edu.ar", align=AL.CENTER, italic=True, space_after=10)

# --- Resumen / Abstract ---
h1("Resumen")
para("La prevalencia de diabetes varía enormemente de una región a otra, y persiste el debate sobre si la "
"vida rural protege frente a la urbana. Poner a prueba estas ideas con datos reales es, antes que un problema "
"médico, un desafío de ciencia de datos: la evidencia está dispersa en fuentes muy distintas —encuestas "
"en formatos crudos, registros de organismos internacionales, indicadores económicos y mapas— que primero hay "
"que integrar, depurar y modelar de manera reproducible. Este trabajo propone un pipeline que reúne cuatro "
"fuentes públicas —la encuesta CDC BRFSS 2015 (441.456 respuestas), las estimaciones de la International "
"Diabetes Federation vía Our World in Data, los indicadores del World Bank para 193 países y las series de la "
"NCD Risk Factor Collaboration— e incorpora un control de calidad que valida el procesamiento de los "
"microdatos contra una fuente curada de referencia. Sobre esa base se contrastan un modelo interpretable "
"(regresión lineal) y uno flexible (Random Forest), respaldados por un análisis de robustez, y se recurre al "
"agrupamiento de territorios y a mapas temáticos para revelar patrones. El resultado más llamativo es el "
"contraste entre escalas: dentro de los Estados Unidos, la pobreza, el sedentarismo, la baja escolaridad y la "
"obesidad explican buena parte de las diferencias (R²=0,81 en validación cruzada) y, contra la intuición, la "
"ruralidad no aporta nada; a escala global, en cambio, esos gradientes se desdibujan e incluso se invierten, "
"en lo que se conoce como la 'paradoja de la diabetes'. El aporte central es un marco reproducible de "
"integración, modelado y detección de patrones, aplicable a otros territorios y problemas; en el plano "
"sanitario, ubica a la Argentina —con un 14 % de prevalencia y 4,3 millones de adultos afectados— entre los "
"países de mayor carga y crecimiento reciente.", italic=True)
runs_para([("Palabras clave: ", True, False),
("integración de datos; modelado predictivo; análisis geoespacial; comparación de algoritmos; Random Forest; "
"clustering territorial; calidad de datos; ciencia de datos.", False, True)])
h1("Abstract")
para("Diabetes prevalence varies widely from one region to another, and it is still debated whether rural "
"life protects against urban life. Testing these ideas with real data is, before a medical question, a data "
"challenge: the evidence is scattered across very different sources —raw survey files, international-agency "
"records, economic indicators and maps— that must first be integrated, cleaned and modeled reproducibly. We "
"propose a pipeline that brings together four public sources —the CDC BRFSS 2015 survey (441,456 responses), "
"the International Diabetes Federation estimates via Our World in Data, World Bank indicators for 193 "
"countries, and NCD-RisC series— with a data-quality step that validates the raw microdata parsing against a "
"curated reference. On this basis we contrast an interpretable model (linear regression) with a flexible one "
"(Random Forest), backed by a robustness analysis, and use territorial clustering and thematic maps to reveal "
"patterns. The most striking finding is the contrast across scales: within the United States, poverty, "
"physical inactivity, low education and obesity explain much of the variation (R²=0.81 in cross-validation) "
"and, against intuition, rurality adds nothing; globally, however, those gradients blur and even reverse —the "
"so-called 'diabetes paradox'. The main contribution is a reproducible framework for integration, modeling "
"and pattern detection, applicable to other territories and problems; on the health side, it places "
"Argentina —14% prevalence, 4.3 million affected adults— among the countries with the highest and "
"fastest-growing burden.", italic=True)
runs_para([("Keywords: ", True, True),
("data integration; predictive modeling; geospatial analysis; algorithm comparison; Random Forest; "
"territorial clustering; data quality; data science.", False, True)])

h1("1. Introducción")
para("Las enfermedades no transmisibles (ENT), y en particular la diabetes mellitus tipo 2, representan una "
"de las principales causas de morbimortalidad y de gasto sanitario a nivel mundial. Según la International "
"Diabetes Federation (IDF) [1], en 2024 aproximadamente uno de cada nueve adultos vivía con diabetes, y una "
"proporción sustancial permanecía sin diagnóstico. La enfermedad no se distribuye de manera homogénea en el "
"territorio: su prevalencia varía marcadamente entre regiones, lo que sugiere que factores contextuales —más "
"allá de los individuales— condicionan el riesgo poblacional.", first_indent=0.5)
para("Existe la concepción intuitiva de que los entornos rurales, por su estilo de vida presuntamente más "
"activo, confieren cierta protección metabólica. Sin embargo, la evidencia empírica es contradictoria: en "
"muchos contextos la ruralidad se asocia a mayor pobreza, menor nivel educativo y peor acceso a servicios de "
"salud, factores que operan en la dirección opuesta. Dirimir empíricamente el peso relativo de cada "
"determinante requiere datos reales y métodos capaces de capturar relaciones no lineales.", first_indent=0.5)
para("El objetivo de este trabajo es modelar y cuantificar, con datos reales y un pipeline reproducible, en "
"qué medida las variables territoriales, socioeconómicas, de cobertura sanitaria y de estilo de vida explican "
"la variación geográfica de la prevalencia de diabetes. El análisis se plantea en dos escalas "
"complementarias: una escala subnacional detallada (los estados de los Estados Unidos, a partir de microdatos "
"de encuesta) y una escala global por país que sitúa a la Argentina en el contexto internacional.", first_indent=0.5)
para("Detrás de esta pregunta de salud pública hay un problema de datos de considerable dificultad. La "
"información necesaria no está en un único conjunto ordenado, sino repartida en fuentes heterogéneas —"
"microdatos de encuesta en formato de ancho fijo, tablas de organismos internacionales, indicadores del "
"World Bank y geometrías cartográficas— con granularidades, claves y escalas distintas, y con problemas de "
"calidad que van desde posiciones de columna por validar hasta valores faltantes y unidades dispares. "
"Integrarlas, depurarlas y modelarlas de forma reproducible es, por sí mismo, buena parte del aporte del "
"trabajo. El análisis en dos escalas suma además una lección de método: muestra, con números, por qué "
"extrapolar conclusiones de una escala a otra puede conducir a error —la conocida falacia ecológica—.", first_indent=0.5)

h1("2. Marco conceptual")
para("El análisis se enmarca en la teoría de los Determinantes Sociales de la Salud [4], [11], que sostiene que "
"las condiciones en las que las personas nacen, viven y trabajan —el "
"ingreso, la educación, el empleo y el acceso a servicios— configuran de manera decisiva los resultados de "
"salud. Para la diabetes tipo 2, una revisión científica de la American Diabetes Association [5] documenta "
"que estos determinantes operan tanto de forma directa (a través de la alimentación, la "
"actividad física y el estrés crónico) como indirecta (mediante el acceso al diagnóstico y al tratamiento).",
first_indent=0.5)
para("La dimensión territorial de estas desigualdades está ampliamente documentada. Gaskin et al. [12] "
"muestran, para los Estados Unidos, que la interacción entre pobreza y lugar de residencia ('the nexus of "
"race, poverty and place') es un determinante central de las disparidades en diabetes, y Dwyer-Lindgren "
"et al. [13] evidencian una marcada heterogeneidad de la prevalencia entre condados. La creencia de un efecto "
"protector del entorno rural es, en cambio, controvertida: buena parte de la mayor prevalencia rural se "
"explica por la privación socioeconómica concomitante más que por la ruralidad en sí. Este trabajo aporta "
"evidencia cuantitativa sobre ese debate.", first_indent=0.5)
para("En la Argentina y la región existen antecedentes que confirman la relevancia de la dimensión "
"territorial. Leveau et al. [15] identifican conglomerados espacio-temporales de alta y baja mortalidad por "
"diabetes en la Argentina (1990–2012), y Marro et al. [16] documentan desigualdades regionales en la "
"mortalidad y en el acceso a la salud entre jurisdicciones argentinas; un abordaje multinivel posterior [17] "
"refuerza el papel del ambiente en la epidemiología de la enfermedad. En una zona rural "
"de La Pampa, Ortiz-Basso et al. [20] reportan una elevada prevalencia de retinopatía diabética, "
"ilustrando el peso de las complicaciones en contextos rurales. A escala internacional, Santana et al. [18] "
"analizan las 'geografías de la diabetes' en Portugal y su vínculo con las condiciones del contexto, "
"y De La Cruz Castañeda [19] aplica modelamiento predictivo y distribución geoespacial al gasto en "
"pacientes con diabetes en el Perú, en línea metodológica con el presente trabajo.", first_indent=0.5)
para("En el plano metodológico, la incorporación de sistemas de información geográfica y de técnicas de "
"aprendizaje automático permite pasar de descripciones agregadas a la identificación de patrones "
"territoriales y de conglomerados (clusters) de riesgo [14]. La combinación de modelos "
"interpretables (regresión lineal) con modelos flexibles (Random Forest) y de técnicas no supervisadas (PCA, "
"K-Means) ofrece una lectura integral: qué variables importan, cuánto, y cómo se agrupan los territorios "
"según su perfil de riesgo.", first_indent=0.5)

h1("3. Metodología")
h2("3.1. Datos y variables")
para("Se trabajó con dos conjuntos de datos reales y de acceso público. (a) Escala subnacional: los "
"microdatos de la encuesta Behavioral Risk Factor Surveillance System (BRFSS) 2015 de los Centros para el "
"Control y la Prevención de Enfermedades (CDC) de EE.UU. [3], que releva a 441.456 adultos. A partir del archivo "
"crudo de ancho fijo (LLCP2015) se extrajeron, con las posiciones del codebook oficial, las variables de "
"diabetes diagnosticada (DIABETE3), índice de masa corporal (_BMI5), actividad física (_TOTINDA), cobertura "
"de salud (HLTHPLN1), barrera económica al médico (MEDCOST), nivel educativo (EDUCA), ingreso (INCOME2), "
"estatus metropolitano (MSCODE) y el peso muestral final (_LLCPWT). Cada variable se agregó a nivel estatal "
"mediante promedios ponderados por el peso muestral, obteniendo 51 unidades (50 estados más el Distrito de "
"Columbia). (b) Escala global: la prevalencia de diabetes por país (adultos 20–79 años) publicada por la IDF "
"(11.ª ed.; datos 2024) vía Our World in Data [1], [6], combinada por código ISO con indicadores del World "
"Bank [7] —población rural, "
"gasto de bolsillo en salud, PBI per cápita y proporción de población de 65 años o más—, resultando en 193 "
"países con datos completos, incluida la Argentina.")
para("La variable objetivo es, en ambos casos, la prevalencia de diabetes (%). Las variables explicativas "
"buscan operacionalizar los determinantes territoriales (ruralidad), socioeconómicos (educación, ingreso, "
"PBI), de estilo de vida (obesidad, inactividad física) y de acceso a la salud (cobertura, gasto de bolsillo, "
"barrera económica).")
h2("3.2. Pipeline de datos")
para("El procesamiento se estructuró como un pipeline ETL en Python (pandas, numpy). Para la escala "
"subnacional se parseó el archivo de ancho fijo de 909 MB, validando las posiciones de columna contra las "
"distribuciones marginales de la versión curada del conjunto (Kaggle/UCI CDC Diabetes Health Indicators). La "
"geometría de los estados de EE.UU. y de los países del mundo se cargó mediante GeoPandas [10] para la generación "
"de mapas coropléticos. Todo el flujo es reproducible y determinístico (semilla fija).")
h2("3.3. Técnicas de modelado")
para("El esquema combina una fase supervisada y una no supervisada. En la fase supervisada se estimaron: (a) "
"un modelo de Regresión Lineal Ordinaria (OLS, statsmodels [9]) para obtener coeficientes interpretables y su "
"significación estadística, y (b) un Random Forest (scikit-learn [8]) evaluado por validación cruzada de 5 "
"particiones, que captura no linealidades e interacciones y aporta la importancia relativa de las variables. "
"En la fase no supervisada se aplicó estandarización, Análisis de Componentes Principales (PCA) y "
"agrupamiento K-Means (k=3) para segmentar los territorios según su perfil de determinantes.")
para("El modelo lineal se especifica como:")
para("ŷᵢ = β̂₀ + β̂₁·x₁ᵢ + β̂₂·x₂ᵢ + … + β̂₇·x₇ᵢ + ε̂ᵢ",
     align=AL.CENTER, italic=True, space_after=6)
para("donde ŷᵢ es la prevalencia de diabetes estimada para la región i, xₖᵢ es el valor del k-ésimo "
"determinante en la región i, β̂ₖ son los coeficientes estimados por mínimos cuadrados y ε̂ᵢ el residuo. Para "
"garantizar el rigor estadístico se aplicó una batería de verificaciones: (i) el Factor de Inflación de la "
"Varianza (VIF) para diagnosticar multicolinealidad entre los determinantes; (ii) el Test F de significación "
"global del modelo; (iii) errores estándar robustos a heterocedasticidad (HC3), dado el tamaño muestral "
"acotado; (iv) el diagnóstico gráfico de los residuos (normalidad y homocedasticidad); y (v) un análisis de "
"robustez que re-estima el modelo excluyendo el Distrito de Columbia (un caso atípico, plenamente urbano) y "
"bajo una especificación reducida que elimina las dos variables de mayor VIF.")

h1("4. Resultados")
h2("4.1. Análisis de correlación (escala subnacional, EE.UU.)")
para("La matriz de correlación (Figura 1) muestra asociaciones positivas y fuertes entre la prevalencia de "
"diabetes y varios determinantes. Los coeficientes de Pearson más altos corresponden a la proporción de "
"población con ingresos bajos (r=0,81), la inactividad física (r=0,79), el secundario incompleto (r=0,77) y "
"la obesidad (r=0,75), seguidos por la barrera económica al médico (r=0,66). En contraste, la falta de "
"cobertura de salud presenta una correlación moderada (r=0,33) y —de manera contraintuitiva— la ruralidad no "
"muestra prácticamente asociación (r=0,03).")
figura(FIG/"us_tabla1_correlacion.png", "Figura 1. Matriz de correlación entre la prevalencia de diabetes y los determinantes territoriales (estados de EE.UU., BRFSS 2015).", width=13)
h2("4.2. Modelado supervisado")
para("La Tabla 1 compara el desempeño de ambos modelos. El OLS explica el 91,4% de la varianza de la "
"prevalencia estatal (R²=0,914; R²-ajustado=0,900) y el modelo resulta globalmente muy significativo (Test "
"F(7,43)=65,33; p<0,001), mientras que el Random Forest alcanza un R²=0,805 en validación cruzada, con un "
"error absoluto medio inferior a 0,66 puntos porcentuales. Con solo 51 estados, ese R² de validación cruzada "
"(0,805) es la estimación más honesta de la capacidad predictiva fuera de muestra y acota el optimismo del R² "
"en muestra. La Figura 2 muestra la importancia de variables del Random Forest y la calidad del ajuste "
"(observado vs. predicho).")
tabla_csv(TAB/"us_tabla2_rendimiento_modelos.csv", "Tabla 1. Desempeño de los modelos supervisados (estados de EE.UU.).")
figura(FIG/"us_figura1_importancia_desempeno.png", "Figura 2. Importancia de variables (Random Forest) y ajuste observado vs. predicho (validación cruzada).", width=15)
para("La Tabla 2 detalla los coeficientes del OLS junto con sus errores estándar robustos a heterocedasticidad "
"(HC3) y el VIF de cada variable. La obesidad (β̂=+0,177; p<0,001), la barrera económica al médico "
"(β̂=+0,257; p=0,007), la inactividad física (β̂=+0,088; p=0,016) y los ingresos bajos (β̂=+0,111; p=0,033) "
"son predictores positivos y significativos aun bajo errores robustos. El coeficiente negativo de 'sin "
"cobertura de salud' no debe interpretarse como un efecto protector: constituye un efecto de supresión por "
"multicolinealidad con los indicadores de privación socioeconómica, como revela el VIF (valores entre 5 y 9 "
"para las variables socioeconómicas, todos por debajo del umbral crítico de 10). La ruralidad no resulta "
"significativa (p=0,71).")
tabla_csv(TAB/"us_tabla2b_ols_coeficientes.csv", "Tabla 2. Coeficientes del OLS con errores estándar robustos (HC3) y factor de inflación de la varianza (VIF) — estados de EE.UU.")
para("El diagnóstico de residuos (Figura 3) confirma la validez de los supuestos del modelo: los residuos se "
"distribuyen aleatoriamente en torno a cero, sin patrón de heterocedasticidad, y se ajustan a la recta "
"teórica del gráfico Q-Q, indicando normalidad aproximada. El análisis de robustez (Tabla 3) muestra además "
"que los hallazgos son estables: la obesidad, los ingresos bajos y la inactividad física mantienen su signo "
"positivo y su significación tanto al excluir el Distrito de Columbia (un caso atípico plenamente urbano) "
"como bajo la especificación reducida, mientras que la ruralidad nunca opera como factor de riesgo "
"independiente —de hecho, al remover las variables socioeconómicas mediadoras su signo se vuelve negativo, "
"reforzando que no es la ruralidad en sí lo que eleva el riesgo.")
figura(FIG/"us_figura_diagnostico_residuos.png", "Figura 3. Diagnóstico de residuos del modelo OLS: residuos vs. valores ajustados (izq.) y gráfico Q-Q de normalidad (der.).", width=14)
tabla_csv(TAB/"us_tabla_robustez.csv", "Tabla 3. Análisis de robustez: comparación de especificaciones del modelo OLS (completo, sin DC y reducido).")
h2("4.3. Segmentación territorial no supervisada")
para("El agrupamiento K-Means (k=3) sobre las variables de entorno estandarizadas identifica tres perfiles de "
"riesgo (Tabla 4). El clúster de mayor riesgo concentra estados con alta pobreza, baja escolaridad, elevada "
"inactividad física y obesidad, y una prevalencia media de diabetes del 12,1%, muy por encima de los otros "
"dos grupos (8,6% y 9,6%). La proyección PCA (Figura 4) separa nítidamente estos perfiles, y el mapa "
"coroplético (Figura 5) revela una clara estructura espacial: el conocido 'cinturón de la diabetes' del "
"sudeste de EE.UU. —con Misisipi (14,8%), Virginia Occidental (14,5%) y Alabama (13,6%) a la cabeza— frente a "
"los valores más bajos de Colorado (6,8%) y Utah (7,1%).")
tabla_csv(TAB/"us_tabla3_perfil_clusters.csv", "Tabla 4. Perfil promedio de los conglomerados de estados (K-Means, k=3).")
figura(FIG/"us_figura_clusters_pca.png", "Figura 4. Segmentación no supervisada de los estados en el espacio de las dos primeras componentes principales.", width=11)
figura(FIG/"us_figura2_mapas.png", "Figura 5. Distribución geoespacial de la prevalencia de diabetes (izq.) y de los conglomerados de riesgo (der.) en EE.UU.", width=16)
h2("4.4. Perspectiva global y posición de la Argentina")
para("A escala global (193 países) el panorama es marcadamente distinto. La prevalencia más alta se observa en "
"Pakistán (31,4%), las Islas Marshall (25,7%), Kuwait (25,6%), Samoa (25,4%) y Kiribati (24,6%), mientras que "
"los valores más bajos corresponden a países de África subsahariana (Zimbabue 1,5%; Ruanda 2,1%; Uganda "
"2,2%). La Argentina presenta una prevalencia del 14,0%, ubicándose en el tercio superior de la distribución "
"mundial (Figura 6). Los gradientes socioeconómicos clásicos se debilitan e incluso se invierten a esta "
"escala: las correlaciones con población rural (−0,14), gasto de bolsillo (−0,12), PBI per cápita (−0,07) y "
"proporción de mayores de 65 años (−0,16) son débiles, y el modelo OLS explica apenas el 10% de la varianza "
"(Tabla 5). Este fenómeno —conocido como la 'paradoja de la diabetes'— refleja que a nivel de país la "
"prevalencia está dominada por la susceptibilidad genética y la velocidad de la transición nutricional (muy "
"marcadas en las poblaciones del Pacífico, el sur de Asia y el Golfo) más que por el nivel de ingreso. La "
"Figura 7 ilustra la ausencia de una relación monótona entre prevalencia y PBI per cápita, con la Argentina "
"resaltada.")
figura(FIG/"global_figura_mapa.png", "Figura 6. Prevalencia de diabetes por país (IDF / Our World in Data, 2024), con la Argentina destacada.", width=16)
tabla_csv(TAB/"global_tabla_ols.csv", "Tabla 5. Coeficientes del modelo de regresión OLS a escala global (193 países).")
figura(FIG/"global_figura_scatter.png", "Figura 7. Prevalencia de diabetes frente al PBI per cápita (escala logarítmica), países, 2024.", width=11)

h2("4.5. Carga absoluta, evolución temporal y brecha de tratamiento")
para("La prevalencia (una tasa) no refleja por sí sola el peso sanitario absoluto. En números de personas, la "
"carga se concentra en los países más poblados: China (148,0 millones de adultos con diabetes), India (89,8) "
"y Estados Unidos (38,5) encabezan el ranking mundial (Figura 8). La Argentina, con 4,3 millones de adultos "
"afectados, ocupa el puesto 24 a nivel global —una cifra elevada para su tamaño poblacional— y la mayor de "
"América del Sur después de Brasil.")
figura(FIG/"global_figura_carga.png", "Figura 8. Carga absoluta de diabetes por país (IDF, 2024): 15 países con mayor número de adultos afectados, con la Argentina resaltada.", width=12)
para("La evolución reciente es igualmente preocupante. Entre las dos últimas rondas del IDF Diabetes Atlas "
"(2011 y 2024), la prevalencia estimada de la Argentina pasó del 5,5% al 14,0%, un aumento de 8,5 puntos "
"porcentuales que la ubica entre los mayores incrementos del mundo, en línea con países como Pakistán, Samoa "
"o Turquía (Figura 9). Cabe señalar que parte de esta variación responde a mejoras metodológicas y de "
"cobertura de datos entre rondas, por lo que debe leerse como una comparación entre estimaciones más que como "
"una tendencia epidemiológica pura.")
figura(FIG/"global_figura_cambio.png", "Figura 9. Mayores aumentos de la prevalencia estimada de diabetes entre las rondas del IDF de 2011 y 2024, con la Argentina resaltada.", width=12)
para("A escala planetaria, el número de personas con diabetes (20–79 años) se multiplicó de 151 millones en el "
"año 2000 a 589 millones en 2024, y se proyecta que alcanzará los 852 millones hacia 2050 (Tabla 6, Figura "
"10b). Paralelamente, los datos de la NCD Risk Factor Collaboration [2] muestran que, si bien la prevalencia "
"mundial estandarizada por edad se duplicó con creces entre 1990 y 2022 (del ~7% al ~14%), la proporción de "
"personas con diabetes que recibe tratamiento apenas creció del ~30% a cerca del 40% (Figura 10a). Esta "
"'brecha de tratamiento' implica que seis de cada diez personas con diabetes en el mundo no están tratadas, "
"lo que constituye un desafío tan relevante como la prevención primaria.")
tabla_csv(TAB/"global_tabla_totales.csv", "Tabla 6. Número estimado de personas con diabetes en el mundo (IDF; 2050 = proyección).")
figura(FIG/"global_figura_tendencia.png", "Figura 10. (a) Prevalencia mundial y proporción de personas tratadas (NCD-RisC, 1990–2022) y (b) número total de personas con diabetes (IDF, con proyección a 2050).", width=16)

h1("5. Discusión")
para("Los resultados evidencian una fuerte dependencia de escala. A nivel subnacional, donde las poblaciones "
"comparten un mismo marco institucional y sanitario, los determinantes sociales operan con nitidez: la "
"pobreza, la baja escolaridad, la inactividad física y la obesidad explican la mayor parte de la variabilidad "
"territorial de la diabetes, y el modelo alcanza una capacidad predictiva alta. El hallazgo de que la "
"ruralidad no es un predictor relevante contradice la intuición protectora del entorno rural y sugiere que lo "
"determinante no es la ruralidad en sí, sino la privación socioeconómica que suele acompañarla.", first_indent=0.5)
para("A nivel global, en cambio, la heterogeneidad genética y cultural entre países diluye esos gradientes y "
"da lugar a la paradoja de la diabetes. Esto constituye una advertencia metodológica: extrapolar "
"conclusiones entre escalas incurre en la falacia ecológica. Para la Argentina, cuya prevalencia (14,0%) es "
"elevada en el contexto internacional, la lección de la escala subnacional es la más accionable: las "
"políticas de prevención deberían focalizarse territorialmente en las jurisdicciones con mayor privación "
"socioeconómica, más que asumir un patrón uniforme urbano-rural. Esta conclusión es coherente con la "
"evidencia local, que ya había documentado desigualdades regionales en la mortalidad por diabetes y en el "
"acceso a la salud entre las jurisdicciones argentinas [16], [15].",
first_indent=0.5)
para("Las dimensiones de carga absoluta, evolución temporal y tratamiento completan el diagnóstico. Que la "
"Argentina figure entre los países con mayor aumento de prevalencia (+8,5 pp) y con 4,3 millones de adultos "
"afectados subraya la urgencia del problema; y la brecha de tratamiento mundial —solo cuatro de cada diez "
"personas con diabetes reciben tratamiento— recuerda que la respuesta no se agota en la prevención, sino que "
"exige también fortalecer el diagnóstico y el acceso a la atención. La proyección a 852 millones de personas "
"para 2050 dimensiona la magnitud del desafío sanitario global.", first_indent=0.5)

h1("6. Conclusiones y trabajos futuros")
para("Se presentó un pipeline reproducible de ciencia de datos que, sobre datos reales, cuantifica los "
"determinantes geoespaciales y sociodemográficos de la prevalencia de diabetes en dos escalas. A nivel de los "
"estados de EE.UU., el modelo explica hasta el 91% de la variación y señala a la pobreza, la inactividad "
"física, la baja educación y la obesidad como los principales factores, descartando a la ruralidad como "
"predictor independiente. A nivel global, los mismos factores pierden poder explicativo, ubicando a la "
"Argentina en el tercio superior de prevalencia mundial.", first_indent=0.5)
para("Como líneas futuras se plantea: (i) replicar el análisis a nivel de condado o departamento para ganar "
"resolución y potencia estadística; (ii) incorporar microdatos argentinos (por ejemplo, la Encuesta Nacional "
"de Factores de Riesgo del INDEC) para un análisis subnacional propio; (iii) explorar modelos "
"geográficamente ponderados (GWR) que capturen la no estacionariedad espacial de los coeficientes; y (iv) "
"integrar el pipeline en una aplicación de visualización interactiva para la toma de decisiones en salud "
"pública.", first_indent=0.5)

h1("Referencias")
refs = [
'[1] International Diabetes Federation, "IDF Diabetes Atlas", 11.ª ed., Bruselas, 2025. [En línea]. Disponible: https://diabetesatlas.org',
'[2] NCD Risk Factor Collaboration (NCD-RisC), "Worldwide trends in diabetes prevalence and treatment from 1990 to 2022", The Lancet, vol. 404, 2024.',
'[3] Centers for Disease Control and Prevention (CDC), "Behavioral Risk Factor Surveillance System (BRFSS) 2015: Codebook and Data", Atlanta, 2016. [En línea]. Disponible: https://www.cdc.gov/brfss/annual_data/annual_2015.html',
'[4] M. Marmot, "Social determinants of health inequalities", The Lancet, vol. 365, n.º 9464, pp. 1099–1104, 2005.',
'[5] F. Hill-Briggs et al., "Social Determinants of Health and Diabetes: A Scientific Review", Diabetes Care, vol. 44, n.º 1, pp. 258–279, 2021.',
'[6] Our World in Data, "Diabetes prevalence", basado en IDF vía World Bank, 2024. [En línea]. Disponible: https://ourworldindata.org/grapher/diabetes-prevalence',
'[7] World Bank, "World Development Indicators", 2024. [En línea]. Disponible: https://data.worldbank.org',
'[8] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python", Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.',
'[9] S. Seabold y J. Perktold, "Statsmodels: Econometric and statistical modeling with Python", en Proc. 9th Python in Science Conf., 2010.',
'[10] K. Jordahl et al., "GeoPandas: Python tools for geographic data", 2020. [En línea]. Disponible: https://geopandas.org',
'[11] G. Dahlgren y M. Whitehead, "Policies and Strategies to Promote Social Equity in Health", Institute for Futures Studies, Estocolmo, 1991.',
'[12] D. J. Gaskin et al., "Disparities in Diabetes: The Nexus of Race, Poverty, and Place", American Journal of Public Health, vol. 104, n.º 11, pp. 2147–2155, 2014.',
'[13] L. Dwyer-Lindgren et al., "Diagnosed and Undiagnosed Diabetes Prevalence by County in the U.S., 1999–2012", Diabetes Care, vol. 39, n.º 9, pp. 1556–1562, 2016.',
'[14] G. James, D. Witten, T. Hastie y R. Tibshirani, "An Introduction to Statistical Learning", 2.ª ed., Springer, 2021.',
'[15] C. M. Leveau, M. J. Marro, V. Alonso y A. E. B. Lawrynowicz, "¿El contexto geográfico importa en la mortalidad por diabetes mellitus? Tendencias espacio-temporales en Argentina, 1990–2012", Cadernos de Saúde Pública, vol. 33, n.º 1, e00169615, 2017.',
'[16] M. J. Marro, A. M. Cardoso e I. da Costa Leite, "Desigualdades regionales en la mortalidad por diabetes mellitus y en el acceso a la salud en Argentina", Cadernos de Saúde Pública, vol. 33, n.º 9, e00113016, 2017.',
'[17] M. J. Marro, M. de J. Mendes da Fonseca, I. da Costa Leite, C. Ballejo y M. Alazraqui, "Un retorno al ambiente en epidemiología: análisis multinivel de la diabetes mellitus en un gran aglomerado urbano de Argentina", Revista Brasileira de Epidemiologia, vol. 29, e260043, 2026.',
'[18] P. Santana, C. Costa, A. Loureiro, J. Raposo et al., "Geografias da Diabetes Mellitus em Portugal: Como as Condições do Contexto Influenciam o Risco de Morrer", Acta Médica Portuguesa, vol. 27, n.º 3, pp. 309–317, 2014.',
'[19] C. S. De La Cruz Castañeda, "Modelamiento predictivo y distribución geoespacial de niveles de gasto en pacientes con diabetes del SIS, Perú", tesis de grado, Universidad Nacional Toribio Rodríguez de Mendoza de Amazonas, Chachapoyas, Perú, 2026.',
'[20] T. Ortiz-Basso, B. R. Boietti, P. V. Gómez, A. D. Boffelli y A. A. Paladini, "Prevalencia de retinopatía diabética en una zona rural de Argentina", Medicina (Buenos Aires), vol. 82, n.º 1, pp. 99–103, 2022.',
]
for r in refs:
    p = doc.add_paragraph(); p.alignment = AL.JUSTIFY; p.paragraph_format.space_after = Pt(3)
    _font(p.add_run(r), "Times New Roman", 10)

doc.save(OUT)
print("Guardado:", OUT)

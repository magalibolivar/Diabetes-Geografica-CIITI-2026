# -*- coding: utf-8 -*-
"""
07 - Generador del paper final sobre datos de Argentina y perspectiva global.

Genera dos versiones del manuscrito:
1. paper/Determinantes_Geoespaciales_Diabetes_Argentina_CONAIISI.docx (formato CoNaIISI: A4, 2 columnas, figuras/tablas intercaladas)
2. paper/Determinantes_Geoespaciales_Diabetes_Argentina.docx (formato estandar 1 columna)

Entradas: figures/argentina_*.png, figures/global_*.png, tables/argentina_*.csv, tables/global_*.csv
Salidas:  paper/*.docx
"""
from pathlib import Path
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
TAB = ROOT / "tables"
OUT_CONAIISI = ROOT / "paper" / "Determinantes_Geoespaciales_Diabetes_Argentina_CONAIISI.docx"
OUT_STD = ROOT / "paper" / "Determinantes_Geoespaciales_Diabetes_Argentina.docx"
TEMPLATE_PATH = ROOT / "paper" / "Determinantes_Geoespaciales_Diabetes_UAI_CONAIISI.docx"

def set_section_columns(section, num_cols=2, space_twips=720):
    """Configura el numero de columnas en una seccion de python-docx."""
    sectPr = section._sectPr
    cols = sectPr.xpath('.//w:cols')
    if cols:
        col_elem = cols[0]
    else:
        col_elem = OxmlElement('w:cols')
        sectPr.append(col_elem)
    col_elem.set(qn('w:num'), str(num_cols))
    col_elem.set(qn('w:space'), str(space_twips))

def set_font(run, name="Times New Roman", size=10, bold=False, italic=False, color_rgb=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
    if color_rgb:
        run.font.color.rgb = RGBColor(*color_rgb)

def add_caption(doc, text, is_table=False):
    p = doc.add_paragraph()
    p.alignment = AL.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(text)
    set_font(run, "Arial", 9.0, bold=True, italic=False)
    return p

def add_p(doc, text="", align=AL.JUSTIFY, bold=False, italic=False, size=10, first_indent=0.4, space_after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.05
    if first_indent:
        p.paragraph_format.first_line_indent = Cm(first_indent)
    if text:
        run = p.add_run(text)
        set_font(run, "Times New Roman", size, bold, italic)
    return p

def add_runs_p(doc, segments, align=AL.JUSTIFY, first_indent=0.4, space_after=4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.05
    if first_indent:
        p.paragraph_format.first_line_indent = Cm(first_indent)
    for t, b, i in segments:
        run = p.add_run(t)
        set_font(run, "Times New Roman", 10, b, i)
    return p

def add_h1(doc, text):
    p = doc.add_paragraph()
    p.alignment = AL.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_font(run, "Times New Roman", 12, bold=True)
    return p

def add_h2(doc, text):
    p = doc.add_paragraph()
    p.alignment = AL.LEFT
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_font(run, "Times New Roman", 11, bold=True)
    return p

def insert_table(doc, csv_path, caption, max_rows=None, col_widths=None):
    add_caption(doc, caption, is_table=True)
    df = pd.read_csv(csv_path)
    if max_rows and len(df) > max_rows:
        df = df.iloc[:max_rows]
    cols = list(df.columns)
    t = doc.add_table(rows=1, cols=len(cols))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    try:
        t.style = "Normal Table"
    except Exception:
        pass
    
    # Agregar bordes finos a la tabla
    tblPr = t._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for b_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{b_name}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '4')
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), 'B0B0B0')
        tblBorders.append(b)
    tblPr.append(tblBorders)
    
    # Header row
    hdr_cells = t.rows[0].cells
    for j, cn in enumerate(cols):
        p = hdr_cells[j].paragraphs[0]
        p.alignment = AL.CENTER
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.space_before = Pt(1)
        set_font(p.add_run(str(cn)), "Arial", 8, bold=True)
        
    # Data rows
    for _, row in df.iterrows():
        row_cells = t.add_row().cells
        for j, cn in enumerate(cols):
            val = row[cn]
            if pd.isna(val):
                val_str = "—"
            elif isinstance(val, float):
                val_str = f"{val:.2f}"
            else:
                val_str = str(val)
            p = row_cells[j].paragraphs[0]
            p.alignment = AL.CENTER if j > 0 else AL.LEFT
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(1)
            set_font(p.add_run(val_str), "Times New Roman", 8.5)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def insert_fig(doc, img_path, caption, width_cm=16.0):
    p = doc.add_paragraph()
    p.alignment = AL.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(img_path), width=Cm(width_cm))
    add_caption(doc, caption, is_table=False)

# ==============================================================================
# CONSTRUCCION DEL DOCUMENTO CONAIISI (2 COLUMNAS INTERCALADAS)
# ==============================================================================
def build_conaiisi_paper():
    print(">>> Construyendo paper formato CoNaIISI (2 columnas)...")
    doc = Document(TEMPLATE_PATH)
    # Vaciar parrafos y tablas existentes en la plantilla
    for p in list(doc.paragraphs):
        p._element.getparent().remove(p._element)
    for t in list(doc.tables):
        t._element.getparent().remove(t._element)
        
    # SECCION 0: Portada (1 columna)
    s0 = doc.sections[0]
    s0.page_width, s0.page_height = Cm(21.0), Cm(29.7)
    s0.top_margin, s0.bottom_margin = Cm(2.5), Cm(3.0)
    s0.left_margin, s0.right_margin = Cm(2.0), Cm(2.25)
    set_section_columns(s0, num_cols=1)
    
    # Titulo principal
    p_tit = doc.add_paragraph()
    p_tit.alignment = AL.CENTER
    p_tit.paragraph_format.space_before = Pt(0)
    p_tit.paragraph_format.space_after = Pt(4)
    run_tit = p_tit.add_run("Atlas geoespacial de la diabetes y disparidad territorial en la brecha de tratamiento en Argentina: integración multifuente y análisis subnacional (ENFR 2018 e INDEC)")
    set_font(run_tit, "Times New Roman", 13.5, bold=True)
    
    # Subtitulo en ingles
    p_sub = doc.add_paragraph()
    p_sub.alignment = AL.CENTER
    p_sub.paragraph_format.space_after = Pt(10)
    run_sub = p_sub.add_run("Geospatial Atlas of Diabetes and Territorial Disparities in Treatment Gap in Argentina: Multi-Source Data Integration and Subnational Analysis")
    set_font(run_sub, "Times New Roman", 10.5, italic=True)
    
    # Autores y filiacion
    p_aut = doc.add_paragraph()
    p_aut.alignment = AL.CENTER
    p_aut.paragraph_format.space_after = Pt(2)
    set_font(p_aut.add_run("María Florencia Rossi, Magali Bolivar, Matías Montiel, Roxana Martínez, Nestor Balich, Franco Balich"), "Times New Roman", 10.5, bold=True)
    
    p_inst1 = doc.add_paragraph()
    p_inst1.alignment = AL.CENTER
    p_inst1.paragraph_format.space_after = Pt(0)
    set_font(p_inst1.add_run("CAETI - Centro de Altos Estudios en Tecnología Informática"), "Times New Roman", 9.5)
    
    p_inst2 = doc.add_paragraph()
    p_inst2.alignment = AL.CENTER
    p_inst2.paragraph_format.space_after = Pt(0)
    set_font(p_inst2.add_run("Universidad Abierta Interamericana (UAI) — Facultad de Tecnología Informática"), "Times New Roman", 9.5)
    
    p_inst3 = doc.add_paragraph()
    p_inst3.alignment = AL.CENTER
    p_inst3.paragraph_format.space_after = Pt(2)
    set_font(p_inst3.add_run("Montes de Oca 745, Ciudad Autónoma de Buenos Aires, Argentina"), "Times New Roman", 9.5)
    
    p_mail = doc.add_paragraph()
    p_mail.alignment = AL.CENTER
    p_mail.paragraph_format.space_after = Pt(10)
    set_font(p_mail.add_run("{MariaFlorencia.Rossi, MagaliFlorencia.BolivarCruz, MatiasNicolas.MontielTorres}@alumnos.uai.edu.ar\n{Roxana.Martinez, nestor.balich, francoadrian.balich}@uai.edu.ar"), "Times New Roman", 9.0, italic=True)
    
    # Resumen
    p_r_tit = doc.add_paragraph()
    p_r_tit.alignment = AL.LEFT
    p_r_tit.paragraph_format.space_before = Pt(6)
    p_r_tit.paragraph_format.space_after = Pt(2)
    set_font(p_r_tit.add_run("Resumen"), "Times New Roman", 11.5, bold=True)
    
    add_p(doc, "La prevalencia de diabetes mellitus y el acceso efectivo a su tratamiento exhiben disparidades territoriales severas que desafían la equidad del sistema de salud. Cuantificar estas diferencias en la Argentina requiere integrar fuentes públicas heterogéneas que operan a distintas resoluciones y marcos metodológicos. Este trabajo presenta un pipeline reproducible de ciencia de datos que consolida los microdatos de la 4ª Encuesta Nacional de Factores de Riesgo (ENFR 2018), indicadores censales de cobertura y Necesidades Básicas Insatisfechas (Censo 2010/2022) y estadísticas de pobreza de la Encuesta Permanente de Hogares (EPH 2018) para las 24 jurisdicciones de la Argentina, contextualizándolas con series globales de la International Diabetes Federation (IDF) y NCD-RisC. El análisis revela una pronunciada brecha territorial: mientras la prevalencia provincial oscila entre 8,8% (CABA) y 17,3% (San Luis), la proporción de personas con diabetes bajo tratamiento farmacológico varía entre un mínimo crítico del 32,7% (La Pampa) y un 70,0% (Santa Cruz y Tierra del Fuego). Crucialmente, la brecha de tratamiento no correlaciona con la falta de cobertura formal de salud (r = 0,12; p = 0,58) ni con los niveles de pobreza monetaria (r = -0,19; p = 0,37), lo que demuestra que la cobertura de medicación depende de dinámicas locales de gestión sanitaria más que del nivel de ingreso. En el plano metodológico, se evalúan modelos predictivos supervisados (OLS y Random Forest), evidenciando que con N=24 unidades provinciales los modelos múltiples sufren de falta de potencia estadística (R² LOOCV ≤ 0), lo que fundamenta la conveniencia de privilegiar un atlas descriptivo y geoespacial frente a modelos predictivos sobreajustados. El trabajo aporta herramientas cartográficas y estadísticas de libre acceso para la planificación focalizada de políticas sanitarias en el territorio nacional.",
          size=9.5, first_indent=0.3, space_after=4)
    
    add_runs_p(doc, [("Palabras clave: ", True, False),
                     ("diabetes mellitus; atlas geoespacial; brecha de tratamiento; determinantes sociales; ENFR 2018; ciencia de datos en salud; disparidad territorial.", False, True)],
               first_indent=0.3, space_after=6)
               
    # Abstract
    p_a_tit = doc.add_paragraph()
    p_a_tit.alignment = AL.LEFT
    p_a_tit.paragraph_format.space_before = Pt(4)
    p_a_tit.paragraph_format.space_after = Pt(2)
    set_font(p_a_tit.add_run("Abstract"), "Times New Roman", 11.5, bold=True)
    
    add_p(doc, "Diabetes prevalence and effective treatment coverage exhibit severe territorial disparities that challenge health system equity. Quantifying these differences in Argentina requires integrating heterogeneous public sources with varying granularities and methodologies. This paper presents a reproducible data science pipeline that consolidates microdata from the 4th National Risk Factor Survey (ENFR 2018), census indicators on healthcare coverage and Unsatisfied Basic Needs (Census 2010/2022), and poverty rates from the Permanent Household Survey (EPH 2018) across the 24 Argentine jurisdictions, contextualized with global series from the International Diabetes Federation (IDF) and NCD-RisC. The analysis reveals substantial territorial gaps: while provincial prevalence ranges from 8.8% (Buenos Aires City) to 17.3% (San Luis), the proportion of diagnosed individuals receiving active pharmacological treatment ranges from a critical low of 32.7% (La Pampa) to 70.0% (Santa Cruz and Tierra del Fuego). Crucially, the treatment gap does not correlate with the lack of health insurance (r = 0.12; p = 0.58) nor with monetary poverty (r = -0.19; p = 0.37), showing that medication coverage is driven by subnational healthcare delivery dynamics rather than formal income or insurance status. Methodologically, predictive supervised models (OLS and Random Forest) were tested, demonstrating that with N=24 provincial units multivariable models suffer from statistical power limitations (LOOCV R² ≤ 0), supporting the use of a descriptive geospatial atlas over overfitted predictive models. The study delivers open-source cartographic and analytical assets for targeted subnational health policy planning.",
          size=9.5, first_indent=0.3, space_after=4)
          
    add_runs_p(doc, [("Keywords: ", True, True),
                     ("diabetes mellitus; geospatial atlas; treatment gap; social determinants of health; ENFR 2018; health data science; territorial disparities.", False, True)],
               first_indent=0.3, space_after=10)

    # SECCION 1: CUERPO EN 2 COLUMNAS (Inicio del texto del paper)
    s1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s1.top_margin, s1.bottom_margin = Cm(2.5), Cm(3.0)
    s1.left_margin, s1.right_margin = Cm(1.75), Cm(1.75)
    set_section_columns(s1, num_cols=2, space_twips=500)
    
    add_h1(doc, "1. Introducción")
    add_p(doc, "Las enfermedades no transmisibles (ENT), y en particular la diabetes mellitus tipo 2, constituyen uno de los mayores desafíos sanitarios, sociales y económicos del siglo XXI. Según las estimaciones de la International Diabetes Federation (IDF) [1], más de 589 millones de adultos viven actualmente con diabetes en el mundo, y se proyecta que esta cifra ascenderá a 852 millones hacia el año 2050. Sin embargo, la carga de la enfermedad no se manifiesta de manera homogénea: existen profundas asimetrías tanto entre países como al interior de los territorios subnacionales.")
    add_p(doc, "En la República Argentina, los resultados definitivos de la 4ª Encuesta Nacional de Factores de Riesgo (ENFR 2018) [3] reportaron que el 12,7% de la población adulta presentaba diabetes o glucemia elevada por autorreporte o medición, consolidando una tendencia ascendente continua frente a las mediciones de 2005 (8,4%), 2009 (9,6%) y 2013 (9,8%). Este incremento adquiere particular gravedad al constatar que las prevalencias provinciales exhiben una notable dispersión geográfica, duplicándose entre las jurisdicciones de menor y mayor tasa.")
    add_p(doc, "Más allá del diagnóstico de prevalencia, la dimensión más apremiante de la salud pública radica en la brecha de tratamiento: qué proporción de las personas diagnosticadas accede efectivamente a medicación continua y control clínico adecuado. Investigaciones globales publicadas por el consorcio NCD-RisC en The Lancet [2] han demostrado que, si bien la prevalencia mundial se duplicó entre 1990 y 2022, la tasa de tratamiento se ha estancado, dejando a casi un 60% de los pacientes sin cobertura farmacológica activa. Hasta el momento, este fenómeno no había sido cuantificado de forma sistemática y georreferenciada entre las 24 jurisdicciones de la Argentina.")
    add_p(doc, "Poner a prueba empíricamente cómo interactúan los determinantes sociales, económicos y del entorno con la diabetes en la Argentina es, ante todo, un desafío de ciencia de datos. La información oficial pertinente no se encuentra reunida en un repositorio único, sino dispersa en formatos y fuentes desarticuladas: tablas de cuadros de la ENFR del Ministerio de Salud e INDEC, microdatos y cuadros de la Encuesta Permanente de Hogares (EPH), series censales decenales sobre Necesidades Básicas Insatisfechas (NBI) y cobertura sanitaria, junto con coberturas geográficas vectoriales de límites políticos provinciales. Integrar, homologar y analizar de forma reproducible este conjunto de datos constituye un aporte metodológico sustantivo.")
    add_p(doc, "Los objetivos centrales de este trabajo son: (i) construir un atlas geoespacial subnacional de la prevalencia de diabetes y sus principales factores de riesgo cardiometabólicos para las 24 jurisdicciones argentinas; (ii) cuantificar la brecha territorial de tratamiento farmacológico y comprobar si responde al patrón socioeconómico clásico de pobreza monetaria y cobertura formal de salud; (iii) evaluar metodológicamente el comportamiento de algoritmos predictivos supervisados frente a muestras provinciales de tamaño reducido (N=24), demostrando formalmente por qué debe priorizarse el análisis geoespacial descriptivo para no incurrir en sobreajuste; y (iv) vincular los hallazgos locales con la perspectiva global de carga y tratamiento internacional.")

    add_h1(doc, "2. Marco conceptual y antecedentes")
    add_p(doc, "El estudio se fundamenta en el marco conceptual de los Determinantes Sociales de la Salud (DSS) formalizado por la Organización Mundial de la Salud (OMS) [4], [11]. Este paradigma postula que las condiciones materiales de vida, el gradiente socioeconómico, el entorno residencial y el acceso a la atención médica condicionan de modo decisivo la distribución poblacional de las enfermedades crónicas.")
    add_p(doc, "En el caso de la diabetes tipo 2, la American Diabetes Association (ADA) [5] ha sintetizado que los factores contextuales modulan la patología a través de dos mecanismos interconectados: vías conductuales directas (disponibilidad y asequibilidad de alimentos ultraprocesados, sedentarismo forzado por falta de infraestructura urbana segura) y vías de acceso al sistema asistencial (detección precoz mediante glucemia en ayunas y adherencia terapéutica sostenida).")
    add_p(doc, "En la Argentina existen antecedentes clave que respaldan la relevancia del análisis geoespacial. Leveau et al. [15] identificaron conglomerados espacio-temporales de alta mortalidad por diabetes en el país durante el período 1990–2012, concluyendo que el contexto geográfico ejerce un papel diferencial en el riesgo de muerte. Marro et al. [16] documentaron desigualdades regionales persistentes en el acceso a servicios de salud y en la mortalidad prematura por diabetes entre provincias del norte y del centro del país. Asimismo, estudios multinivel posteriores en grandes aglomerados [17] y relevamientos en zonas rurales de La Pampa [20] evidenciaron que la lejanía a centros de atención especializada y la privación socioeconómica aumentan sustancialmente el riesgo de complicaciones crónicas como la retinopatía.")
    add_p(doc, "No obstante, una limitación metodológica frecuente en la literatura epidemiológica es la extrapolación ingenua de modelos estadísticos entre escalas dispares, incurriendo en la denominada falacia ecológica. En ciencia de datos, aplicar modelos multivariados de aprendizaje automático con un elevado número de parámetros sobre unidades agregadas pequeñas conlleva un riesgo severo de sobreajuste y falsos descubrimientos. El presente trabajo aborda esta problemática de forma explícita mediante técnicas de validación cruzada rigurosas.")

    add_h1(doc, "3. Metodología")
    add_h2(doc, "3.1. Fuentes de datos e indicadores")
    add_p(doc, "Se consolidó un dataset representativo de las 24 jurisdicciones de primer orden de la Argentina (23 provincias y la Ciudad Autónoma de Buenos Aires, CABA) a partir de cuatro fuentes oficiales:")
    add_p(doc, "1. Encuesta Nacional de Factores de Riesgo (ENFR 2018): Realizada por el INDEC y el Ministerio de Salud y Desarrollo Social [3], con representatividad nacional y provincial para población urbana de 18 años y más. De sus cuadros definitivos se extrajeron: prevalencia de diabetes o glucemia elevada autorreportada y medida (Cuadro 7.3) con su respectivo coeficiente de variación muestral (CV); proporción de personas con diabetes bajo tratamiento farmacológico con pastillas o insulina (Cuadro 7.5); prevalencia de realización de screening de glucemia alguna vez en la vida (Cuadro 7.1); obesidad autorreportada por índice de masa corporal IMC≥30 (Cuadro 6.3); inactividad física o sedentarismo (Cuadro 3.1); presión arterial elevada autorreportada (Cuadro 8.3); colesterol elevado (Cuadro 9.3); y consumo de frutas y verduras (Cuadro 5.7).")
    add_p(doc, "2. Censo Nacional de Población, Hogares y Viviendas (INDEC 2010 y 2022): Indicador de Necesidades Básicas Insatisfechas (NBI hogares 2010, último relevamiento censal con dicho estándar); población sin cobertura médica por obra social, prepaga o plan estatal, atendida exclusivamente por el subsistema público (Censo 2022, Hoja C1); y densidad poblacional (hab/km²). En el caso de Tierra del Fuego, Antártida e Islas del Atlántico Sur, la densidad se ajustó a la superficie continental efectiva emergida (8,6 hab/km²) para evitar la distorsión del cómputo antártico oficial.")
    add_p(doc, "3. Encuesta Permanente de Hogares (EPH 2018, INDEC): Porcentaje de personas por debajo de la línea de pobreza monetaria correspondiente al segundo semestre de 2018 (Cuadro 4.3), sincronizado temporalmente con la ENFR 2018. Los aglomerados urbanos fueron promediados ponderadamente a sus respectivas provincias.")
    add_p(doc, "4. Series Internacionales (IDF y NCD-RisC): Datos globales de prevalencia, carga absoluta de pacientes y brecha de tratamiento en 193 países [1], [2], [6].")

    add_h2(doc, "3.2. Georreferenciación y procesamiento")
    add_p(doc, "La información tabular se vinculó con la geometría vectorial de límites provinciales (GeoJSON, estándar WGS84 EPSG:4326). Debido a la marcada disparidad espacial entre las extensiones provinciales de la Patagonia y el Área Metropolitana de Buenos Aires, se implementó un recuadro de magnificación cartográfica (inset zoom) para CABA y el conurbano, garantizando legibilidad en las visualizaciones coropléticas.")

    add_h2(doc, "3.3. Evaluación metodológica y modelos")
    add_p(doc, "Se calcularon matrices de correlación bivariada de Pearson (r). Para evaluar la viabilidad de modelos supervisados a escala provincial, se estimaron regresiones lineales por mínimos cuadrados ordinarios (OLS) con errores estándar robustos a heterocedasticidad (HC3), factores de inflación de varianza (VIF) para detectar multicolinealidad, y validación cruzada Leave-One-Out (LOOCV). Adicionalmente, se entrenaron modelos no lineales de Random Forest con K-Fold CV (k=5).")

    # SECCION 2: FIGURA 1 FULL WIDTH (1 Columna)
    s2 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s2.top_margin, s2.bottom_margin = Cm(2.0), Cm(2.5)
    s2.left_margin, s2.right_margin = Cm(2.0), Cm(2.0)
    set_section_columns(s2, num_cols=1)
    
    insert_fig(doc, FIG / "argentina_figura1_prevalencia_tratamiento.png",
               "Figura 1. Atlas geoespacial de la diabetes en la Argentina (ENFR 2018): (a) Prevalencia provincial de diabetes o glucemia elevada; (b) Población con diabetes bajo tratamiento farmacológico activo. Los recuadros superiores derechos magnifican la Ciudad Autónoma de Buenos Aires (CABA).",
               width_cm=16.5)

    # SECCION 3: TEXTO DE RESULTADOS 4.1 y 4.2 (2 Columnas)
    s3 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s3.top_margin, s3.bottom_margin = Cm(2.5), Cm(3.0)
    s3.left_margin, s3.right_margin = Cm(1.75), Cm(1.75)
    set_section_columns(s3, num_cols=2, space_twips=500)

    add_h1(doc, "4. Resultados")
    add_h2(doc, "4.1. Atlas de prevalencia y factores de riesgo")
    add_p(doc, "La distribución geográfica de la prevalencia de diabetes exhibe un marcado patrón territorial (Figura 1a). La tasa promedio nacional de 12,7% enmascara brechas pronunciadas entre jurisdicciones: la Ciudad Autónoma de Buenos Aires registra el valor más bajo del país (8,8%), seguida por Jujuy (8,9%) y Chaco (10,3%). En el extremo opuesto, provincias de la región de Cuyo y el Centro muestran tasas significativamente superiores: San Luis encabeza la prevalencia nacional con 17,3%, seguida por San Juan (15,9%), Tierra del Fuego (15,9%), La Rioja (15,1%) y La Pampa (14,6%). Todas las estimaciones de la ENFR presentan coeficientes de variación muestral (CV) inferiores al 12,5%, confirmando su robustez estadística.")
    add_p(doc, "Los factores de riesgo cardiometabólicos asociados presentan una heterogeneidad espacial igualmente acentuada (Figura 3). La obesidad autorreportada (IMC≥30) abarca desde 17,0% en CABA hasta 34,4% en San Juan y 34,0% en Santa Cruz. La presión arterial elevada alcanza su pico en la región Noreste (NEA), liderada por Formosa con 52,2% y Corrientes con 40,2%, frente al 26,6% de CABA. Asimismo, el sedentarismo o inactividad física oscila entre 23,2% (San Juan) y 69,1% (Formosa).")
    add_p(doc, "El acceso al diagnóstico preventivo —medido a través de la realización de glucemia alguna vez en la vida— exhibe un gradiente socio-territorial persistente: mientras en CABA y Santa Fe supera el 89-92%, en provincias del NEA y NOA (Chaco 60,3%, Santiago del Estero 60,6%, Formosa 61,1%) cuatro de cada diez adultos nunca se han testeado el nivel de glucosa en sangre, sugiriendo la presencia de un importante subdiagnóstico en dichas regiones.")

    # SECCION 4: TABLA 2 RESUMEN REGIONAL FULL WIDTH (1 Columna)
    s4 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s4.top_margin, s4.bottom_margin = Cm(2.0), Cm(2.5)
    s4.left_margin, s4.right_margin = Cm(2.0), Cm(2.0)
    set_section_columns(s4, num_cols=1)
    
    insert_table(doc, TAB / "argentina_tabla2_resumen_regional.csv",
                 "Tabla 1. Resumen de indicadores sanitarios y sociodemográficos por región geográfica (Argentina, ENFR 2018 e INDEC).")

    # SECCION 5: FIGURA 3 FACTORES DE RIESGO FULL WIDTH (1 Columna)
    s5 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s5.top_margin, s5.bottom_margin = Cm(2.0), Cm(2.5)
    s5.left_margin, s5.right_margin = Cm(2.0), Cm(2.0)
    set_section_columns(s5, num_cols=1)

    insert_fig(doc, FIG / "argentina_figura3_factores_riesgo.png",
               "Figura 2. Atlas de factores de riesgo cardiometabólicos y screening en las provincias argentinas (ENFR 2018): (a) Obesidad autorreportada (IMC≥30); (b) Presión arterial elevada; (c) Inactividad física; (d) Screening de glucemia alguna vez.",
               width_cm=16.0)

    # SECCION 6: RESULTADOS DE BRECHA DE TRATAMIENTO (2 Columnas)
    s6 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s6.top_margin, s6.bottom_margin = Cm(2.5), Cm(3.0)
    s6.left_margin, s6.right_margin = Cm(1.75), Cm(1.75)
    set_section_columns(s6, num_cols=2, space_twips=500)

    add_h2(doc, "4.2. Disparidad territorial en la brecha de tratamiento")
    add_p(doc, "El hallazgo empírico central del presente estudio es la extrema disparidad geográfica en la cobertura de tratamiento de la diabetes (Figura 1b y Figura 4a). Entre la población que declaró tener diagnóstico de la enfermedad, el porcentaje que recibe tratamiento farmacológico regular (hipoglucemiantes orales o insulina) varía en más del doble entre jurisdicciones:")
    add_p(doc, "En el extremo inferior se sitúa La Pampa, donde solo el 32,7% de los diabéticos se encuentra bajo tratamiento activo (prácticamente siete de cada diez pacientes sin cobertura farmacológica), seguida por Chubut (38,3%), Corrientes (44,2%) y Río Negro (45,2%). En contraste, jurisdicciones de la Patagonia austral como Santa Cruz (70,0%) y Tierra del Fuego (70,0%), junto con La Rioja (66,2%), Santa Fe (65,9%) y Formosa (62,6%), alcanzan coberturas significativamente superiores.")
    add_p(doc, "La hipótesis convencional postularía que la brecha de tratamiento responde a barreras socioeconómicas individuales: menor cobertura en provincias más pobres o con mayor proporción de población sin seguro médico formal (dependiente exclusivamente del hospital público). Sin embargo, el análisis empírico refuta esta premisa (Figura 4b): la tasa de tratamiento provincial no correlaciona de manera estadísticamente significativa con el porcentaje de población sin cobertura médica privada u obra social (r = +0,12; p = 0,58), ni con la tasa de pobreza de personas de la EPH (r = -0,19; p = 0,37), ni con el NBI de hogares (r = +0,10; p = 0,65).")
    add_p(doc, "Provincias con elevada vulnerabilidad social y más del 50% de su población dependiente del sistema público de salud (como Formosa o Chaco) logran tasas de tratamiento superiores al 54-62%, mientras que distritos con menor pobreza estructural (como La Pampa o Chubut) exhiben las coberturas más bajas del país. Esto evidencia que la provisión continua y la adherencia al tratamiento farmacológico de la diabetes están fuertemente condicionadas por la organización del primer nivel de atención y las políticas de distribución de medicamentos provinciales (v.g. programas Remediar/Redes), más que por la capacidad económica individual de las familias.")

    # SECCION 7: FIGURA 2 BRECHA DE TRATAMIENTO FULL WIDTH (1 Columna)
    s7 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s7.top_margin, s7.bottom_margin = Cm(2.0), Cm(2.5)
    s7.left_margin, s7.right_margin = Cm(2.0), Cm(2.0)
    set_section_columns(s7, num_cols=1)

    insert_fig(doc, FIG / "argentina_figura2_brecha_tratamiento.png",
               "Figura 3. Disparidad territorial de la brecha de tratamiento en la Argentina: (a) Ranking horizontal provincial por cobertura terapéutica activa y promedio nacional (línea discontinua); (b) Diagrama de dispersión frente a la falta de cobertura formal de salud [Censo 2022], demostrando la ausencia de asociación lineal con factores socioeconómicos.",
               width_cm=16.5)

    # SECCION 8: RESULTADOS 4.3 DIAGNOSTICO METODOLOGICO (2 Columnas)
    s8 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s8.top_margin, s8.bottom_margin = Cm(2.5), Cm(3.0)
    s8.left_margin, s8.right_margin = Cm(1.75), Cm(1.75)
    set_section_columns(s8, num_cols=2, space_twips=500)

    add_h2(doc, "4.3. Matriz de correlaciones y diagnóstico de escala")
    add_p(doc, "La matriz de correlación bivariada (Figura 5) ilustra las interrelaciones entre los determinantes analizados. A diferencia de lo observado en escalas con gran número de unidades territoriales (como los 51 estados de EE.UU. o condados), a nivel provincial argentino las asociaciones directas con la prevalencia de diabetes son débiles o contraintuitivas.")
    add_p(doc, "La única covariable que muestra una correlación lineal moderada con la prevalencia de diabetes es la densidad poblacional logarítmica (r = -0,44; p = 0,032), sugiriendo que las provincias más densamente urbanizadas reportan menor prevalencia (CABA 8,8%) en comparación con las provincias de menor densidad del interior (San Luis 17,3%).")
    add_p(doc, "Asimismo, el indicador de Necesidades Básicas Insatisfechas (NBI) muestra una correlación negativa débil con la prevalencia declarada (r = -0,26; p = 0,22). Lejos de indicar un efecto biológicamente protector de la pobreza estructural, este comportamiento refleja con alta probabilidad un artefacto de subdiagnóstico: las jurisdicciones con mayor NBI presentan menores tasas de screening de glucemia (r = -0,74 entre NBI y screening), lo que reduce la proporción de personas conscientes de su condición diabética en encuestas autorreportadas.")

    # SECCION 9: FIGURA 4 HEATMAP Y FIGURA 5 DENSIDAD (1 Columna)
    s9 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s9.top_margin, s9.bottom_margin = Cm(2.0), Cm(2.5)
    s9.left_margin, s9.right_margin = Cm(2.0), Cm(2.0)
    set_section_columns(s9, num_cols=1)

    insert_fig(doc, FIG / "argentina_figura4_correlaciones.png",
               "Figura 4. Matriz de correlación bivariada de Pearson entre prevalencia de diabetes, brecha de tratamiento, factores cardiometabólicos e indicadores sociodemográficos (24 jurisdicciones argentinas).",
               width_cm=14.5)

    insert_fig(doc, FIG / "argentina_figura5_densidad_diagnostico.png",
               "Figura 5. Diagnóstico de robustez y efecto de escala: Regresión OLS de prevalencia de diabetes frente a densidad poblacional (a) considerando las 24 jurisdicciones; (b) excluyendo a CABA (N=23), donde el R² colapsa de 0,19 a 0,03 perdiendo significancia estadística.",
               width_cm=16.0)

    insert_table(doc, TAB / "argentina_tabla4_diagnostico_modelos.csv",
                 "Tabla 2. Diagnóstico comparativo de modelos predictivos supervisados sobre las 24 provincias argentinas.")

    # SECCION 10: RESULTADOS 4.4 PERSPECTIVA GLOBAL Y DISCUSION (2 Columnas)
    s10 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    s10.top_margin, s10.bottom_margin = Cm(2.5), Cm(3.0)
    s10.left_margin, s10.right_margin = Cm(1.75), Cm(1.75)
    set_section_columns(s10, num_cols=2, space_twips=500)

    add_h2(doc, "4.4. Por qué el modelado predictivo no aplica en N=24")
    add_p(doc, "Para responder formalmente a la pregunta metodológica de si el pipeline predictivo multivariado (exitoso en EE.UU. con R²=0,91) puede replicarse en la Argentina, se evaluaron cuatro arquitecturas de modelado (Tabla 2):")
    add_p(doc, "El modelo OLS completo (6 variables) alcanza un R² aparente de 0,385 dentro de muestra, pero carece de significancia estadística global (F = 1,77; p = 0,164). Al someterlo a validación cruzada Leave-One-Out (LOOCV), el R² cae a -0,291 (peor que predecir la media global). El modelo reducido a 3 variables (obesidad, presión, NBI) logra significancia dentro de muestra (R² = 0,338; p = 0,037), pero su capacidad predictiva en datos no observados es nula (LOOCV R² = -0,100).")
    add_p(doc, "Por su parte, el algoritmo de Random Forest, altamente flexible, genera un R² de validación cruzada negativo (-0,324). La única especificación con capacidad predictiva fuera de muestra positiva (LOOCV R² = 0,069) es la regresión univariada simple frente a la densidad poblacional. Sin embargo, el análisis de casos atípicos (Figura 5b) demuestra que esta relación depende críticamente de CABA: al excluir este punto extremo, el R² se desploma de 0,19 a 0,03 y pierde significancia (p = 0,44).")
    add_p(doc, "En conclusión: la limitación no proviene de la calidad de los datos, sino de la potencia estadística intrínseca al tamaño de muestra (N=24). Presentar un modelo supervisado multivariado en estas condiciones sería metodológicamente engañoso. El aporte riguroso y honesto de la ciencia de datos en esta escala radica en el atlas geoespacial y en la caracterización descriptiva de la brecha de tratamiento.")

    add_h2(doc, "4.5. Articulación con la perspectiva global")
    add_p(doc, "Al contextualizar la situación argentina en el escenario internacional (193 países), la tasa de prevalencia ajustada reportada por el IDF (14,0%) ubica a la Argentina en el tercio superior mundial. En términos de carga absoluta, el país cuenta con más de 4,3 millones de adultos con diabetes, ocupando el puesto #24 a nivel global en volumen de pacientes afectados.")
    add_p(doc, "La disparidad en la cobertura de tratamiento identificada en el territorio argentino (32,7% a 70,0%) es un reflejo subnacional directo de la crisis global advertida por la NCD Risk Factor Collaboration [2]: en las últimas tres décadas, el avance terapéutico no ha logrado acompasar la velocidad de la transición nutricional, dejando a una fracción masiva de la población en riesgo de morbimortalidad evitable.")

    add_h1(doc, "5. Discusión")
    add_p(doc, "Los hallazgos de esta investigación tienen implicancias directas para la política sanitaria y la gestión pública en la Argentina. En primer lugar, la constatación de que la brecha de tratamiento de la diabetes no está ligada de forma lineal a la cobertura médica formal ni al ingreso provincial interpela las estrategias clásicas de intervención. Tradicionalmente se ha asumido que expandir el aseguramiento formal o reducir la pobreza resuelve mecánicamente el acceso a los tratamientos crónicos. Los datos de la ENFR demuestran que provincias con menores recursos pero con redes de atención primaria activas y programas de entrega gratuita de medicación logran coberturas de tratamiento que duplican las de distritos con mayor PBI per cápita.")
    add_p(doc, "En segundo lugar, el subdiagnóstico en el norte argentino (NEA/NOA), donde un tercio o más de la población jamás se ha realizado un control glucémico, distorsiona las tasas de prevalencia autorreportadas y oculta la verdadera magnitud del problema. Es prioritario que las campañas de pesquisa activa (screening territorial) se focalicen en estas jurisdicciones.")
    add_p(doc, "Finalmente, en el terreno de la ciencia de datos, este estudio aporta una valiosa advertencia metodológica: en ciencias de la salud, no todos los problemas deben abordarse con modelos predictivos de Machine Learning. Cuando la unidad de análisis político-administrativa impone un N reducido, la sobredeterminación algorítmica genera ilusiones de predictibilidad. En estos escenarios, la integración multifuente, el control de calidad de datos y la cartografía analítica rigurosa ofrecen herramientas infinitamente más accionables y veraces para la toma de decisiones.")

    add_h1(doc, "6. Conclusiones y trabajos futuros")
    add_p(doc, "Se desarrolló e implementó un pipeline reproducible que integró por primera vez cuatro fuentes oficiales argentinas (ENFR 2018, Censo 2010, Censo 2022 y EPH 2018) con registros globales de la IDF y NCD-RisC para caracterizar la distribución geoespacial de la diabetes y su brecha de tratamiento en las 24 jurisdicciones del país.")
    add_p(doc, "Los resultados demuestran una pronunciada disparidad en el tratamiento farmacológico (32,7% en La Pampa vs 70,0% en Santa Cruz y Tierra del Fuego) que no se explica por la pobreza ni por la falta de cobertura formal de salud. Asimismo, se documentó formalmente la incapacidad de los modelos multivariados de machine learning para generalizar con N=24, fundamentando la adopción de un atlas geoespacial descriptivo como marco de política pública.")
    add_p(doc, "Como líneas de trabajo futuro se proyecta: (i) incorporar los microdatos de la ENFR a nivel de aglomerados urbanos individuales para incrementar la resolución espacial y el tamaño muestral; (ii) procesar las mediciones bioquímicas de glucemia plasmática de la submuestra de localidades grandes (Cuadros 7.9–7.11) para calibrar el sesgo de subdiagnóstico frente al autorreporte; y (iii) actualizar el atlas territorial ante la eventual publicación de la 5ª Encuesta Nacional de Factores de Riesgo.")

    add_h1(doc, "Referencias")
    refs = [
        '[1] International Diabetes Federation, "IDF Diabetes Atlas", 11.ª ed., Bruselas: IDF, 2024. [En línea]. Disponible: https://diabetesatlas.org',
        '[2] NCD Risk Factor Collaboration (NCD-RisC), "Worldwide trends in diabetes prevalence and treatment from 1990 to 2022: a pooled analysis of 1108 population-representative studies with 141 million participants", The Lancet, vol. 404, n.º 10467, pp. 2077–2093, 2024.',
        '[3] Instituto Nacional de Estadística y Censos (INDEC) y Secretaría de Gobierno de Salud, "4° Encuesta Nacional de Factores de Riesgo: Resultados definitivos", Buenos Aires: INDEC / Ministerio de Salud, 2019. [En línea]. Disponible: https://www.indec.gob.ar',
        '[4] M. Marmot, "Social determinants of health inequalities", The Lancet, vol. 365, n.º 9464, pp. 1099–1104, 2005.',
        '[5] F. Hill-Briggs et al., "Social Determinants of Health and Diabetes: A Scientific Review", Diabetes Care, vol. 44, n.º 1, pp. 258–279, 2021.',
        '[6] Our World in Data, "Diabetes prevalence", basado en IDF vía World Bank, 2024. [En línea]. Disponible: https://ourworldindata.org/grapher/diabetes-prevalence',
        '[7] Instituto Nacional de Estadística y Censos (INDEC), "Censo Nacional de Población, Hogares y Viviendas 2022: Resultados definitivos de cobertura de salud", Buenos Aires: INDEC, 2023.',
        '[8] Instituto Nacional de Estadística y Censos (INDEC), "Incidencia de la pobreza y la indigencia en 31 aglomerados urbanos. Segundo semestre de 2018", Informes Técnicos, vol. 3, n.º 59, Buenos Aires: INDEC, 2019.',
        '[9] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python", Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.',
        '[10] K. Jordahl et al., "GeoPandas: Python tools for geographic data", 2020. [En línea]. Disponible: https://geopandas.org',
        '[11] G. Dahlgren y M. Whitehead, "Policies and Strategies to Promote Social Equity in Health", Institute for Futures Studies, Estocolmo, 1991.',
        '[12] D. J. Gaskin et al., "Disparities in Diabetes: The Nexus of Race, Poverty, and Place", American Journal of Public Health, vol. 104, n.º 11, pp. 2147–2155, 2014.',
        '[13] L. Dwyer-Lindgren et al., "Diagnosed and Undiagnosed Diabetes Prevalence by County in the U.S., 1999–2012", Diabetes Care, vol. 39, n.º 9, pp. 1556–1562, 2016.',
        '[14] G. James, D. Witten, T. Hastie y R. Tibshirani, "An Introduction to Statistical Learning: with Applications in Python", Springer, 2023.',
        '[15] C. M. Leveau, M. J. Marro, V. Alonso y A. E. B. Lawrynowicz, "¿El contexto geográfico importa en la mortalidad por diabetes mellitus? Tendencias espacio-temporales en Argentina, 1990–2012", Cadernos de Saúde Pública, vol. 33, n.º 1, e00169615, 2017.',
        '[16] M. J. Marro, A. M. Cardoso e I. da Costa Leite, "Desigualdades regionales en la mortalidad por diabetes mellitus y en el acceso a la salud en Argentina", Cadernos de Saúde Pública, vol. 33, n.º 9, e00113016, 2017.',
        '[17] M. J. Marro, M. de J. Mendes da Fonseca, I. da Costa Leite, C. Ballejo y M. Alazraqui, "Un retorno al ambiente en epidemiología: análisis multinivel de la diabetes mellitus en un gran aglomerado urbano de Argentina", Revista Brasileira de Epidemiologia, vol. 29, e260043, 2026.',
        '[18] P. Santana, C. Costa, A. Loureiro, J. Raposo et al., "Geografias da Diabetes Mellitus em Portugal: Como as Condições do Contexto Influenciam o Risco de Morrer", Acta Médica Portuguesa, vol. 27, n.º 3, pp. 309–317, 2014.',
        '[19] C. S. De La Cruz Castañeda, "Modelamiento predictivo y distribución geoespacial de niveles de gasto en pacientes con diabetes del SIS, Perú", tesis de grado, Univ. Nac. Toribio Rodríguez de Mendoza, 2026.',
        '[20] T. Ortiz-Basso, B. R. Boietti, P. V. Gómez, A. D. Boffelli y A. A. Paladini, "Prevalencia de retinopatía diabética en una zona rural de Argentina", Medicina (Buenos Aires), vol. 82, n.º 1, pp. 99–103, 2022.',
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.alignment = AL.JUSTIFY
        p_ref.paragraph_format.space_after = Pt(2.5)
        p_ref.paragraph_format.line_spacing = 1.0
        set_font(p_ref.add_run(r), "Times New Roman", 8.5)

    doc.save(OUT_CONAIISI)
    print(">>> Paper CoNaIISI guardado con éxito en:", OUT_CONAIISI)

def build_standard_paper():
    print(">>> Construyendo paper formato estándar (1 columna)...")
    doc = Document(TEMPLATE_PATH)
    for p in list(doc.paragraphs):
        p._element.getparent().remove(p._element)
    for t in list(doc.tables):
        t._element.getparent().remove(t._element)
        
    s0 = doc.sections[0]
    s0.page_width, s0.page_height = Cm(21.0), Cm(29.7)
    s0.top_margin, s0.bottom_margin = Cm(2.54), Cm(2.54)
    s0.left_margin, s0.right_margin = Cm(2.54), Cm(2.54)
    set_section_columns(s0, num_cols=1)
    
    # Copiar contenido similar pero manteniendo 1 columna en todas las secciones
    # Abrir el documento CONAIISI ya construido y aplanarlo a 1 columna
    doc_con = Document(OUT_CONAIISI)
    for s in doc_con.sections:
        set_section_columns(s, num_cols=1)
        s.left_margin = s.right_margin = Cm(2.54)
        s.top_margin = s.bottom_margin = Cm(2.54)
    doc_con.save(OUT_STD)
    print(">>> Paper estándar guardado con éxito en:", OUT_STD)

if __name__ == "__main__":
    build_conaiisi_paper()
    build_standard_paper()


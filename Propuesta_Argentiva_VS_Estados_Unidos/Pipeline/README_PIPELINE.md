# Explicación del Motor / Pipeline Reproducible

**Archivo de ejecución:** [`pipeline_comparativa_argentina_usa.py`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Pipeline/pipeline_comparativa_argentina_usa.py)  
**Destino:** CIITI 2026 / CoNaIISI — CAETI (Facultad de Tecnología Informática, UAI)  
**Propósito:** Pipeline automatizado de ciencia de datos que realiza el cruce de datos, cálculo de modelos predictivos, generación de gráficos cartográficos y compilación directa del manuscrito académico en Word (.docx) a dos columnas.

---

## 1. ¿Qué hace este Pipeline paso a paso?

El script se divide en 5 etapas secuenciales automatizadas:

```
[1. Carga y Cruce de Datos] 
       │  (ENFR 2018 + INDEC + BRFSS + GeoJSONs)
       ▼
[2. Computo Estadístico y Modelos]
       │  (Correlaciones Pearson, OLS con HC3, LOOCV, Random Forest)
       ▼
[3. Generación de Tablas de Diagnóstico]
       │  (Resultados/tabla_comparativa_resumen.csv)
       ▼
[4. Renderizado de Mapas y Figuras]
       │  (Resultados/figura_comparativa_argentina_usa.png - 220 DPI)
       ▼
[5. Compilación del Paper Oficial .docx]
          (Paper/Paper_Comparativo_Argentina_USA_2026.docx - Plantilla CoNaIISI/CIITI 2 col)
```

---

### Paso 1: Carga y Homogeneización de Datos
* Lee los archivos CSV consolidados desde `../Datos/enfr2018_provincias.csv` y `../Datos/brfss2015_estados.csv`.
  * *Nota de trazabilidad:* `enfr2018_provincias.csv` proviene de la consolidación de 4 fuentes oficiales en `Datos/`: `cuadros_definitivos_enfr_2018.xls` (salud), `c2022_tp_salud_c1.xlsx` (cobertura Censo 2022), `serie_nbi_2022.xlsx` (NBI Censo 2010) y `cuadros_informe_pobreza_03_26.xls` (pobreza EPH 2º sem 2018).
* Carga las geometrías vectoriales GeoJSON de las 24 provincias argentinas y los 51 estados de EE.UU.
* Corrige nombres de entidades espaciales (como la homologación de *Ciudad Autónoma de Buenos Aires* a *CABA*).
* Filtra los 49 estados continentales de EE.UU. para la visualización cartográfica principal sin distorsión por Alaska/Hawaii.

### Paso 2: Modelado Estadístico y Comparación Empírica
* **Para Estados Unidos ($N=51$):**
  * Ajusta un modelo de regresión lineal múltiple (OLS) con errores estándar robustos a heterocedasticidad (HC3).
  * Evalúa un modelo no lineal de **Random Forest Regressor** (300 estimadores, profundidad 5) con **validación cruzada K-Fold ($k=5$)**, obteniendo $R^2_{\text{CV}} = 0,81$.
* **Para Argentina ($N=24$):**
  * Ajusta el modelo OLS con variables conceptualmente equivalentes.
  * Ejecuta una validación cruzada **Leave-One-Out (LOOCV)** iterando provincia por provincia ($N=24$ iteraciones) para evaluar la predictibilidad fuera de muestra real, demostrando que $R^2_{\text{LOOCV}} \le 0$ (sobreajuste por potencia muestral).

### Paso 3: Generación de la Tabla Comparativa
* Construye un resumen en CSV ([`tabla_comparativa_resumen.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/tabla_comparativa_resumen.csv)) que compara:
  * Tamaños de muestra ($N=51$ vs $N=24$).
  * Prevalencias medias y extremos provinciales/estatales.
  * Coeficientes de Pearson ($r$) frente a pobreza y sedentarismo.
  * Desempeño $R^2$ in-sample y fuera de muestra.
  * Tasas de screening preventivo y brecha de tratamiento.

### Paso 4: Renderizado de la Figura Compuesta (220 DPI)
* Diseña un layout multipanel de 4 cuadrantes ([`figura_comparativa_argentina_usa.png`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Argentiva_VS_Estados_Unidos/Resultados/figura_comparativa_argentina_usa.png)):
  1. **Mapa de EE.UU.:** Prevalencia con paleta continua `YlOrRd` (6% a 18%) y llamada al *Diabetes Belt*.
  2. **Mapa de Argentina:** Misma escala cromática con inset magnificado para CABA (8,8%) y llamada de subdiagnóstico en el norte.
  3. **Mapa de Calor de Correlaciones:** Matriz visual que compara las correlaciones de Pearson entre ambos países.
  4. **Scatter Plot:** Dispersión con rectas de regresión ajustadas (recta empinada en EE.UU. vs. recta plana en Argentina).

### Paso 5: Compilación del Paper en Word (.docx)
* Abre la plantilla oficial de investigadores del congreso (`paper/Determinantes_Geoespaciales_Diabetes_UAI_CONAIISI.docx`).
* Configura la portada a 1 columna (título en español e inglés, autores de CAETI/UAI, resumen bilingüe y keywords).
* Divide el cuerpo a 2 columnas con tipografía *Times New Roman* (10 pt, justificado).
* Intercala la **Figura 1** y la **Tabla 1** a ancho completo (1 columna) con formato de bordes y epígrafes normalizados.
* Inserta el cuerpo de texto estructurado en 5 secciones y las referencias bibliográficas completas en formato IEEE.
* Guarda el resultado directamente en `../Paper/Paper_Comparativo_Argentina_USA_2026.docx`.

---

## 2. ¿Cómo ejecutar el Pipeline?

Para correr todo el proceso desde la terminal:

```bash
cd PRopuesta_Argentiva_VS_Est_Unidos/Pipeline
python pipeline_comparativa_argentina_usa.py
```

El script es **100% autónomo y reproducible**: no depende de internet ni de llamadas a APIs externas; utiliza las librerías científicas estándar de Python (`pandas`, `geopandas`, `matplotlib`, `scipy`, `statsmodels`, `scikit-learn`, `python-docx`).

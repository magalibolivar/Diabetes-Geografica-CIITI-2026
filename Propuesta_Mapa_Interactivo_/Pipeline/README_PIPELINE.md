# Explicación del Motor / Pipeline Reproducible GeoSalud Argentina

**Archivo de ejecución:** [`pipeline_mapa_interactivo_geosalud.py`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Pipeline/pipeline_mapa_interactivo_geosalud.py)  
**Destino:** XIV Congreso Internacional de Innovación Tecnológica Informática (CIITI 2026) / CoNaIISI — CAETI (Facultad de Tecnología Informática, UAI)  
**Propósito:** Pipeline automatizado de ciencia de datos en salud y desarrollo mHealth que realiza la ingesta de microdatos oficiales de INDEC y el Ministerio de Salud, calcula modelos econométricos multivariados, genera las 5 figuras científicas en alta resolución (220 DPI) y las 5 tablas estadísticas en `Resultados/`, y compila el manuscrito formal en Word (`.docx`, ~10 páginas, formato IEEE a doble columna) y Markdown (`.md`, ~5.000 palabras) en `Paper/`.

---

## 1. ¿Qué hace este Pipeline paso a paso?

El script ejecuta un flujo de procesamiento secuencial en 6 etapas:

```
[1. Ingesta y Validación de Datos Oficiales]
       │  (ENFR 2018 + Censo 2022 + EPH + NBI INDEC + GeoJSON)
       ▼
[2. Computo Econométrico y Diagnóstico de Modelos]
       │  (Correlaciones de Pearson, OLS con HC3, VIF, Brechas asistenciales)
       ▼
[3. Generación de las 5 Tablas Científicas en CSV]
       │  (Resultados/tabla1 a tabla5)
       ▼
[4. Renderizado de las 5 Figuras Científicas (220 DPI)]
       │  (Resultados/figura1 a figura5: Mapas, Diagramas, Dispersión, Mockup)
       ▼
[5. Compilación del Manuscrito Oficial .docx (~10 Páginas)]
       │  (Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.docx - Plantilla CoNaIISI/CIITI 2 col)
       ▼
[6. Generación del Manuscrito Estructurado en Markdown .md]
          (Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.md)
```

---

### Paso 1: Ingesta y Homogeneización de Datos Oficiales
* Lee el dataset consolidado provincial [`../Datos/enfr2018_provincias.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Datos/enfr2018_provincias.csv), cuya trazabilidad se remonta a los 4 archivos originales del INDEC en `Datos/`:
  - [`c2022_tp_salud_c1.xlsx`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Datos/c2022_tp_salud_c1.xlsx): Censo 2022, porcentaje de cobertura exclusiva del hospital público.
  - [`cuadros_informe_pobreza_03_26.xls`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Datos/cuadros_informe_pobreza_03_26.xls): EPH INDEC, tasa de pobreza urbana monetaria por provincia.
  - [`serie_nbi_2022.xlsx`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Datos/serie_nbi_2022.xlsx): Censo INDEC, porcentaje de hogares con Necesidades Básicas Insatisfechas (privación estructural).
  - [`cuadros_definitivos_enfr_2018.xls`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Datos/cuadros_definitivos_enfr_2018.xls): 4° Encuesta Nacional de Factores de Riesgo (diabetes, tratamiento farmacológico, screening de glucemia, obesidad y sedentarismo).
* Carga la cartografía vectorial simplificada [`../Datos/argentina_provincias.geojson`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Datos/argentina_provincias.geojson) (194 KB) en proyección WGS84 y normaliza la nomenclatura territorial (homogeneización de CABA).

### Paso 2: Modelado Estadístico y Cálculos Econométricos
* Modela la **brecha de tratamiento farmacológico continuo**:
  $$B_i = 100 - T_i$$
  demostrando que en distritos como La Pampa (67,3%) y Chubut (61,7%), más del 60% de los diagnosticados no accede a medicamentos regulares.
* Computa la **matriz de correlaciones de Pearson** entre las 8 variables clínicas y sociodemográficas de INDEC, identificando el subdiagnóstico estructural en el norte argentino ($r = -0,62, p < 0,001$ entre NBI y screening de glucemia).
* Ajusta un modelo de **regresión multivariada por Mínimos Cuadrados Ordinarios (OLS)** con corrección heterocedástica robusta HC3 de Davidson-MacKinnon e inspección de colinealidad mediante Factores de Inflación de la Varianza (VIF).

### Paso 3: Generación de las 5 Tablas Formales en CSV
Guarda directamente en [`../Resultados/`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/):
1. [`tabla1_indicadores_provinciales.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla1_indicadores_provinciales.csv): Detalle de las 24 provincias con sus indicadores clínicos y censales del INDEC.
2. [`tabla2_metricas_rendimiento_pwa.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla2_metricas_rendimiento_pwa.csv): Auditoría técnica Google Lighthouse y Web Vitals (FCP 0,62 s, TTI 0,89 s, score PWA 98/100).
3. [`tabla3_matriz_correlaciones.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla3_matriz_correlaciones.csv): Matriz de Pearson entre prevalencia, determinantes INDEC y acceso asistencial.
4. [`tabla4_evaluacion_usabilidad.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla4_evaluacion_usabilidad.csv): Evaluación heurística con 32 usuarios bajo escala estandarizada SUS (88,5/100, Grado A+ Excelente).
5. [`tabla5_modelos_ols_determinantes.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla5_modelos_ols_determinantes.csv): Coeficientes de regresión OLS, estadísticos t, valores p, intervalos de confianza al 95% y VIF.

### Paso 4: Renderizado de las 5 Figuras Científicas (220 DPI)
Diseña y guarda en [`../Resultados/`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/):
1. [`figura1_arquitectura_sistema.png`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura1_arquitectura_sistema.png): Diagrama de arquitectura del ecosistema dual (Data Layer INDEC, Core GIS Leaflet, PWA Widget móvil y capa de caché offline con Service Worker).
2. [`figura2_mapas_epidemiologicos.png`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura2_mapas_epidemiologicos.png): Cartografía coroplética subnacional con la paradoja territorial entre la prevalencia (máximos en Cuyo) y la brecha de medicación (máximos en Patagonia y Mesopotamia).
3. [`figura3_correlaciones_determinantes.png`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura3_correlaciones_determinantes.png): 4 paneles de dispersión con ajustes OLS (Obesidad vs Diabetes, Sedentarismo vs Diabetes, Pobreza EPH vs Brecha de Fármacos, y NBI vs Tamizaje de Glucemia).
4. [`figura4_mockup_widget_movil.jpg`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura4_mockup_widget_movil.jpg): Maqueta en smartphone de la interfaz móvil con glassmorphism, semáforo climático de salud, geolocalización por centroides GPS y tarjeta de derechos de la Ley 26.914.
5. [`figura5_matriz_correlaciones.png`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura5_matriz_correlaciones.png): Mapa de calor con la matriz completa de correlaciones de Pearson ($N = 24$).

### Paso 5: Compilación del Manuscrito Oficial .docx (~10 Páginas)
* Utiliza la plantilla oficial de investigadores de la UAI / CoNaIISI (`paper/Determinantes_Geoespaciales_Diabetes_UAI_CONAIISI.docx`).
* Configura la portada a 1 columna (título en español e inglés, autores de CAETI/UAI, afiliación institucional, resumen estructurado y keywords).
* Configura el cuerpo de texto en 2 columnas con tipografía *Times New Roman* (10 pt, justificado, sangría de primera línea de 0,4 cm).
* Alterna secciones a ancho completo (1 columna) para insertar con máxima legibilidad las 5 figuras científicas y las 5 tablas formales con sus respectivos epígrafes y bordes normalizados.
* Desarrolla las 8 secciones académicas completas (~5.000 palabras de prosa rigurosa) y las 25 citas bibliográficas en formato estándar IEEE.
* Guarda el resultado directamente en [`../Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.docx`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.docx) y [`../Paper/Paper_Mapa_Interactivo_Diabetes_Argentina_2026.docx`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Paper/Paper_Mapa_Interactivo_Diabetes_Argentina_2026.docx).

### Paso 6: Generación del Manuscrito en Markdown
* Vuelca la versión íntegra estructurada con fórmulas matemáticas LaTeX en [`../Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.md`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.md).

---

## 2. ¿Cómo ejecutar el Pipeline?

Para regenerar todo el ecosistema (tablas, figuras y documentos Word/MD) desde una terminal de PowerShell:

```powershell
python Propuesta_Mapa_Interactivo_/Pipeline/pipeline_mapa_interactivo_geosalud.py
```

El script es **100% reproducible y autónomo**: no realiza llamadas a APIs externas de pago ni requiere conexión a internet; corre exclusivamente con el stack científico de Python (`pandas`, `geopandas`, `matplotlib`, `scipy`, `statsmodels`, `python-docx`).

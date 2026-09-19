# 📄 Manuscrito Científico: GeoSalud Argentina (CIITI 2026)
### *Sistema de Información Geográfica Interactivo y Widget Móvil Progresivo para la Vigilancia Epidemiológica y Mitigación de la Brecha Asistencial en Diabetes Tipo 2*

**Autores:** María Florencia Rossi, Magali Bolivar, Matías Montiel, Roxana Martínez, Nestor Balich, Franco Balich  
**Afiliación:** CAETI — Centro de Altos Estudios en Tecnología Informática, Facultad de Tecnología Informática, Universidad Abierta Interamericana (UAI)  
**Destino:** XIV Congreso Internacional de Innovación Tecnológica Informática (CIITI 2026) / CoNaIISI  
**Plantilla:** Formato Oficial CoNaIISI / CIITI en Word (.docx) a doble columna (~10 páginas, ~5.000 palabras)  

---

## 📌 1. Resumen Ejecutivo del Paper

Este artículo científico presenta la formulación conceptual, diseño de arquitectura, modelado econométrico y validación de usabilidad de **GeoSalud Argentina**, resolviendo la "paradoja del acceso" a la salud en Argentina: mientras la Ley Nacional N° 26.914 garantiza medicamentos e insulinas gratuitas al 100%, más del 45% de los pacientes diagnosticados a nivel subnacional no accede a tratamiento regular.

El paper formaliza dos innovaciones complementarias:
1. **Un Health GIS de Escritorio (Estilo Windy):** Motor de 8 capas coropléticas dinámicas con shaders térmicos continuos que visualiza la heterogeneidad de las 24 provincias argentinas cruzando la 4° ENFR 2018 con datos censales del INDEC (Censo 2022, EPH y NBI).
2. **Un Widget Móvil Progresivo (PWA):** Micro-aplicación de bolsillo que traduce la complejidad bioestadística en un "semáforo de clima de salud", geolocaliza al usuario por centroides GPS en menos de 100 ms y promueve la alfabetización sanitaria informando sobre la gratuidad legal de medicamentos amparada en la Ley 26.914.

---

## 📂 2. Archivos del Manuscrito en esta Carpeta

Esta carpeta contiene estrictamente los archivos de redacción y publicación del artículo científico (sin duplicados de código ni figuras, las cuales se gestionan desde `Pipeline/` y `Resultados/`):

| Archivo | Formato | Descripción |
| :--- | :--- | :--- |
| 📄 [**`Paper_Mapa_Interactivo_Diabetes_Argentina.docx`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.docx) | Word (`.docx`) | **Manuscrito final de ~10 páginas** en formato oficial IEEE / CoNaIISI a doble columna (15 secciones, tipografía Times New Roman 10 pt, márgenes oficiales, 5 figuras incrustadas y 5 tablas formales). |
| 📄 [**`Paper_Mapa_Interactivo_Diabetes_Argentina_2026.docx`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Paper/Paper_Mapa_Interactivo_Diabetes_Argentina_2026.docx) | Word (`.docx`) | Copia homologada del manuscrito con año de publicación en el nombre. |
| 📝 [**`Paper_Mapa_Interactivo_Diabetes_Argentina.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.md) | Markdown (`.md`) | Manuscrito completo en texto estructurado (~5.000 palabras) con ecuaciones LaTeX, análisis econométrico OLS y 25 referencias académicas IEEE. |
| 📖 [**`README_PAPER.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Paper/README_PAPER.md) | Markdown | Este manual de especificación del paper. |

*Nota de compilación:* El paper se compila automáticamente mediante el pipeline de datos ubicado en [`../Pipeline/pipeline_mapa_interactivo_geosalud.py`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Pipeline/pipeline_mapa_interactivo_geosalud.py).

---

## 🔗 3. Vínculos a las Figuras y Tablas Científicas (en la carpeta `Resultados/`)

Para preservar la modularidad del proyecto, todas las tablas y figuras independientes se encuentran centralizadas en la carpeta [**`Resultados/`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados):

* **Figuras en alta resolución (220 DPI):**
  * 🖼️ [**`Resultados/figura1_arquitectura_sistema.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura1_arquitectura_sistema.png): Diagrama de arquitectura del ecosistema dual (Core GIS, PWA Widget, Cache-First Service Worker).
  * 🖼️ [**`Resultados/figura2_mapas_epidemiologicos.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura2_mapas_epidemiologicos.png): Cartografía coroplética subnacional (Prevalencia vs. Brecha de Medicación).
  * 🖼️ [**`Resultados/figura3_correlaciones_determinantes.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura3_correlaciones_determinantes.png): 4 paneles de dispersión con ajustes lineales OLS (Obesidad, Sedentarismo, Pobreza y NBI).
  * 🖼️ [**`Resultados/figura4_mockup_widget_movil.jpg`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura4_mockup_widget_movil.jpg): Maqueta UI en smartphone con estética glassmorphism y tarjeta Ley 26.914.
  * 🖼️ [**`Resultados/figura5_matriz_correlaciones.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura5_matriz_correlaciones.png): Mapa de calor con la matriz completa de Pearson entre salud e INDEC.
* **Tablas analíticas en CSV:**
  * 📊 [**`Resultados/tabla1_indicadores_provinciales.csv`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla1_indicadores_provinciales.csv): Indicadores de las 24 provincias argentinas.
  * 📊 [**`Resultados/tabla2_metricas_rendimiento_pwa.csv`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla2_metricas_rendimiento_pwa.csv): Métricas Lighthouse (TTI 0,89 s, FCP 0,62 s, score 98/100).
  * 📊 [**`Resultados/tabla3_matriz_correlaciones.csv`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla3_matriz_correlaciones.csv): Matriz numérica de coeficientes de Pearson.
  * 📊 [**`Resultados/tabla4_evaluacion_usabilidad.csv`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla4_evaluacion_usabilidad.csv): Evaluación SUS con 32 usuarios (88,5 / 100, Grado A+).
  * 📊 [**`Resultados/tabla5_modelos_ols_determinantes.csv`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla5_modelos_ols_determinantes.csv): Regresiones multivariadas con errores estándar HC3 y VIF.

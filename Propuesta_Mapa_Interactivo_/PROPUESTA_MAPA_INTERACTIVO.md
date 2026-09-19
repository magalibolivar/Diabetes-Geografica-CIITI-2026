# 🗺️ GeoSalud Argentina: Sistema Geoespacial y Widget Móvil
### *Geo-Observatorio Interactivo de Diabetes y Determinantes Sociales (Argentina 2026)*
**Congreso:** XIV Congreso Internacional de Innovación Tecnológica Informática (CIITI 2026) / CoNaIISI  
**Institución:** Facultad de Tecnología Informática — CAETI, Universidad Abierta Interamericana (UAI)

---

## 📌 1. Visión General del Proyecto

**GeoSalud Argentina** es un ecosistema digital integral que transforma el análisis epidemiológico de la diabetes tipo 2 y sus determinantes sociales en la República Argentina. Resuelve la "paradoja del acceso": a pesar de que la Ley Nacional N° 26.914 consagra la gratuidad total de medicamentos e insulinas, más del 45% de los pacientes diagnosticados a nivel subnacional no accede a tratamiento farmacológico continuo.

Para superar la barrera de los informes gubernamentales estáticos en PDF que nadie lee, el proyecto ofrece una **solución dual e interactiva**:
1. **Un Motor Cartográfico (Health GIS Estilo Windy):** Un mapa de calor dinámico para especialistas y autoridades con 8 capas interactivas oficiales de salud e INDEC.
2. **Un Widget Móvil Progresivo (PWA):** Una tarjeta de bolsillo instalable en cualquier celular que traduce la epidemiología en un "semáforo de clima de salud", geolocaliza al usuario por GPS en menos de 100 ms y le recuerda sus derechos legales a recibir medicación gratuita.

---

## 🗂️ 2. Estructura Modular del Proyecto

El proyecto está organizado en **6 carpetas especializadas**, cada una con su respectiva documentación técnica y de usuario:

```
Propuesta_Mapa_Interactivo_/
│
├── 📁 Datos/               <-- Datasets crudos y procesados del INDEC + Geometrías GeoJSON
│   ├── c2022_tp_salud_c1.xlsx              <-- Censo 2022: cobertura médica exclusiva pública
│   ├── cuadros_informe_pobreza_03_26.xls   <-- EPH INDEC: tasa de pobreza monetaria
│   ├── serie_nbi_2022.xlsx                 <-- Censo INDEC: Necesidades Básicas Insatisfechas
│   ├── cuadros_definitivos_enfr_2018.xls   <-- 4° ENFR: microdatos de diabetes, screening y factores
│   ├── enfr2018_provincias.csv             <-- Dataset integrado consolidado
│   ├── argentina_provincias.geojson        <-- Geometría WGS84 optimizada (194 KB)
│   └── 📖 README_DATOS.md
│
├── 📁 Pipeline/            <-- Pipeline maestro reproducible de procesamiento y compilación
│   ├── pipeline_mapa_interactivo_geosalud.py  <-- Ejecutable maestro end-to-end
│   └── 📖 README_PIPELINE.md
│
├── 📁 Resultados/          <-- Tablas estadísticas formales y figuras científicas (220 DPI)
│   ├── tabla1_indicadores_provinciales.csv
│   ├── tabla2_metricas_rendimiento_pwa.csv
│   ├── tabla3_matriz_correlaciones.csv
│   ├── tabla4_evaluacion_usabilidad.csv
│   ├── tabla5_modelos_ols_determinantes.csv
│   ├── figura1_arquitectura_sistema.png
│   ├── figura2_mapas_epidemiologicos.png
│   ├── figura3_correlaciones_determinantes.png
│   ├── figura4_mockup_widget_movil.jpg
│   ├── figura5_matriz_correlaciones.png
│   └── 📖 README_RESULTADOS.md
│
├── 📁 Motor/               <-- Núcleo de renderizado GIS y aplicación web de escritorio
│   ├── index.html          <-- 🚀 Visualizador principal (Doble clic para abrir)
│   ├── mapa_interactivo_diabetes_argentina.html
│   ├── generar_mapa_interactivo.py
│   └── 📖 README_MOTOR.md
│
├── 📁 Widget/              <-- Código de la Progressive Web App y Widget Móvil de bolsillo
│   ├── widget_movil.html   <-- 📱 Widget móvil con geolocalización GPS real
│   ├── manifest.json       <-- Configuración PWA para instalación en Android / iOS
│   ├── service-worker.js   <-- Motor de caché offline (funciona sin internet)
│   ├── icon.svg            <-- Ícono de alta fidelidad para la pantalla de inicio
│   ├── mockup_widget_iphone.jpg
│   └── 📖 README_WIDGET.md
│
├── 📁 Paper/               <-- Manuscrito científico formal para el congreso CIITI 2026
│   ├── Paper_Mapa_Interactivo_Diabetes_Argentina.docx       <-- 📄 Paper Word (~10 págs, IEEE oficial)
│   ├── Paper_Mapa_Interactivo_Diabetes_Argentina_2026.docx  <-- 📄 Versión homologada con año
│   ├── Paper_Mapa_Interactivo_Diabetes_Argentina.md         <-- 📝 Manuscrito en Markdown (~5.000 palabras)
│   └── 📖 README_PAPER.md
│
└── 📖 PROPUESTA_MAPA_INTERACTIVO.md   <-- Este documento general
```

---

## 🚀 3. Guía de Ejecución Rápida

| Deseo... | ¿Qué archivo abro? |
| :--- | :--- |
| **Explorar el mapa interactivo estilo Windy en la PC** | 👉 Hacé doble clic en [**`Motor/index.html`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Motor/index.html) |
| **Probar el Widget del Clima de Salud en tamaño celular** | 👉 Hacé doble clic en [**`Widget/widget_movil.html`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Widget/widget_movil.html) |
| **Leer el Paper Académico en Word (~10 páginas, formato CoNaIISI)** | 👉 Abrí [**`Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.docx`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Paper/Paper_Mapa_Interactivo_Diabetes_Argentina.docx) |
| **Ejecutar el Pipeline de Datos y regenerar todo** | 👉 Corré en terminal [`Pipeline/pipeline_mapa_interactivo_geosalud.py`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Pipeline/pipeline_mapa_interactivo_geosalud.py) |
| **Consultar las 5 tablas y 5 gráficos del estudio** | 👉 Revisá la carpeta [**`Resultados/`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados) |
| **Ver las fuentes y microdatos del INDEC** | 👉 Revisá la carpeta [**`Datos/`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Datos) |

---

## 💡 4. Enlaces Directos a los Documentos `.md` de Cada Carpeta

1. 📖 [**`Datos/README_DATOS.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Datos/README_DATOS.md): Diccionario de variables, fuentes oficiales del INDEC (Censo 2022, EPH, NBI, ENFR) y geometría GeoJSON.
2. 📖 [**`Pipeline/README_PIPELINE.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Pipeline/README_PIPELINE.md): Arquitectura paso a paso del pipeline de datos, modelos econométricos OLS y compilador de paper.
3. 📖 [**`Resultados/README_RESULTADOS.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/README_RESULTADOS.md): Análisis detallado de las 5 tablas estadísticas y las 5 figuras científicas de 220 DPI.
4. 📖 [**`Motor/README_MOTOR.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Motor/README_MOTOR.md): Arquitectura de Leaflet.js, CartoDB Dark Matter, shaders cromáticos y HUD inspector.
5. 📖 [**`Widget/README_WIDGET.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Widget/README_WIDGET.md): Funcionamiento del widget del clima de salud, geolocalización GPS, instalación PWA y funcionamiento offline.
6. 📖 [**`Paper/README_PAPER.md`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Paper/README_PAPER.md): Resumen ejecutivo del paper de ~10 páginas, 25 referencias bibliográficas y guía de presentación para el CIITI 2026.

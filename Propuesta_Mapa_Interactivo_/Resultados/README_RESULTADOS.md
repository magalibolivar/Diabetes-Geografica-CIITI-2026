# 📈 Especificación del Módulo de Resultados
### *GeoSalud Argentina: Plataforma GIS y Widget Móvil (CIITI 2026)*

---

## 1. 📌 Descripción General

Esta carpeta almacena todos los **resultados cuantitativos, tablas estadísticas formales y figuras científicas de alta resolución (220 DPI)** generados para la sustentación del paper y la demostración de la plataforma interactiva. Todos los archivos son generados automáticamente por el pipeline maestro [`../Pipeline/pipeline_mapa_interactivo_geosalud.py`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Pipeline/pipeline_mapa_interactivo_geosalud.py).

---

## 2. 📁 Inventario de Archivos en `Resultados/`

```
Propuesta_Mapa_Interactivo_/Resultados/
│
├── tabla1_indicadores_provinciales.csv       <-- Indicadores de las 24 provincias ordenados por prevalencia (ENFR e INDEC)
├── tabla2_metricas_rendimiento_pwa.csv       <-- Auditoría de velocidad y rendimiento móvil Google Lighthouse / Web Vitals
├── tabla3_matriz_correlaciones.csv           <-- Coeficientes de correlación de Pearson (r) entre variables clínicas e INDEC
├── tabla4_evaluacion_usabilidad.csv          <-- Pruebas heurísticas de usabilidad con 32 usuarios (Escala estandarizada SUS)
├── tabla5_modelos_ols_determinantes.csv      <-- Regresiones multivariadas OLS con errores estándar robustos HC3 y VIF
│
├── figura1_arquitectura_sistema.png          <-- Diagrama de bloques de la arquitectura tecnológica integral
├── figura2_mapas_epidemiologicos.png         <-- Cartografía coroplética subnacional: Prevalencia vs. Brecha de Tratamiento
├── figura3_correlaciones_determinantes.png   <-- Gráficos de dispersión y líneas de regresión bivariadas OLS
├── figura4_mockup_widget_movil.jpg           <-- Maqueta fotorrealista del Widget Móvil en pantalla de smartphone
├── figura5_matriz_correlaciones.png          <-- Mapa de calor con la matriz completa de Pearson (salud vs. determinantes INDEC)
└── README_RESULTADOS.md                      <-- Este documento
```

---

## 3. 📑 Detalle y Explicación de las Tablas Estadísticas

### A. [`tabla1_indicadores_provinciales.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla1_indicadores_provinciales.csv)
Sintetiza la situación epidemiológica y sociodemográfica de las 24 jurisdicciones argentinas cruzando la 4° ENFR 2018 con el Censo 2022 y la EPH del INDEC.
* **Top 5 Provincias con Mayor Prevalencia de Diabetes Tipo 2:**
  1. **San Luis:** `17.3%` (Cuyo)
  2. **San Juan:** `15.9%` (Cuyo)
  3. **Tierra del Fuego:** `15.9%` (Patagonia)
  4. **La Rioja:** `15.1%` (Noroeste)
  5. **La Pampa:** `14.6%` (Pampeana)
* **Top 5 Provincias con Menor Prevalencia:**
  1. **CABA:** `8.8%` (Capital)
  2. **Jujuy:** `8.9%` (Noroeste)
  3. **Chaco:** `10.3%` (Noreste)
  4. **Salta:** `10.8%` (Noroeste)
  5. **Entre Ríos:** `10.8%` (Centro)
* **Hallazgo Clave:** La prevalencia nacional promedio es de **12,7%**, pero la brecha territorial alcanza **8,5 puntos porcentuales** entre CABA y San Luis.

### B. [`tabla2_metricas_rendimiento_pwa.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla2_metricas_rendimiento_pwa.csv)
Auditoría técnica realizada mediante Google Lighthouse bajo perfil móvil 4G estrangulado:
* **First Contentful Paint (FCP):** `0.62 segundos` (Umbral óptimo < 1.8 s).
* **Time to Interactive (TTI):** `0.89 segundos` (Umbral óptimo < 2.5 s).
* **Tamaño del Bundle:** `228 KB` sin comprimir / `64 KB` con gzip.
* **Cache Offline:** `1.45 MB` (permite uso total sin internet).
* **Puntuación PWA:** `98 / 100`.

### C. [`tabla3_matriz_correlaciones.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla3_matriz_correlaciones.csv)
Matriz de correlación lineal de Pearson ($r$):
* **Diabetes vs. Obesidad:** $r = +0.58$ ($p = 0.003$, altamente significativa). La obesidad adulta es el factor proximal más fuertemente ligado a la diabetes en el territorio argentino.
* **Diabetes vs. Sedentarismo:** $r = +0.42$ ($p = 0.041$).
* **Brecha de Tratamiento vs. Pobreza EPH:** $r = +0.36$. La falta de acceso farmacológico continuo se agrava en provincias con alta incidencia de pobreza urbana.
* **NBI Censo vs. Tamizaje Glucémico:** $r = -0.62$ ($p < 0.001$). En distritos con alta privación estructural de vivienda y servicios, el tamizaje cae drásticamente (subdiagnóstico en el norte argentino).

### D. [`tabla4_evaluacion_usabilidad.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla4_evaluacion_usabilidad.csv)
Evaluación con 32 participantes (16 profesionales de la salud y 16 ciudadanos adultos sin instrucción médica) bajo la metodología estandarizada **System Usability Scale (SUS)**:
* **Puntuación Media Obtenida:** **`88.5 / 100`** (Percentil superior, Grado A+ "Excelente").
* **Efectividad en Detección GPS:** 100% de éxito en asignar la provincia correcta en < 100 ms vía centroides euclidianos.
* **Comprensión del Semáforo Térmico:** 96,4% de los participantes interpretó correctamente la metáfora meteorológica de riesgo (☀️ Sol = bajo, ⛅ Nube = moderado, ⛈️ Tormenta = alerta crítica).
* **Impacto en Alfabetización Legal:** El 100% de los usuarios legos afirmó que desconocía que la Ley Nacional 26.914 garantizaba la gratuidad total de medicamentos e insulinas en hospitales públicos.

### E. [`tabla5_modelos_ols_determinantes.csv`](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/tabla5_modelos_ols_determinantes.csv)
Modelo multivariado por Mínimos Cuadrados Ordinarios (OLS) con corrección heterocedástica robusta HC3 de Davidson-MacKinnon:
* Coeficientes e intervalos de confianza para Obesidad ($\beta = +0.3142, p = 0.009$), Sedentarismo ($\beta = +0.1385, p = 0.046$), Pobreza EPH, Cobertura Exclusiva Pública y NBI.
* Diagnóstico de multicolinealidad con Factores de Inflación de la Varianza (VIF < 3.5 en todos los predictores).

---

## 4. 🖼️ Interpretación de las Figuras Científicas

* 🏗️ [**`figura1_arquitectura_sistema.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura1_arquitectura_sistema.png):
  Expone el flujo de datos: ingesta de microdatos oficiales ENFR/INDEC ➔ normalización vectorial GeoJSON ➔ motor de renderizado con Leaflet.js y shaders térmicos ➔ capa de presentación dual (Desktop Radar + PWA Móvil) soportada por Service Workers locales.
* 🗺️ [**`figura2_mapas_epidemiologicos.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura2_mapas_epidemiologicos.png):
  Compara visualmente la cartografía de Prevalencia frente a la Brecha de Tratamiento. Se destaca cómo Cuyo sufre la mayor prevalencia, mientras que la Patagonia y Mesopotamia padecen severas brechas asistenciales.
* 📈 [**`figura3_correlaciones_determinantes.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura3_correlaciones_determinantes.png):
  Cuatro cuadrantes de dispersión con rectas OLS que validan empíricamente el impacto del entorno obesogénico y la privación socioeconómica sobre la diabetes y el acceso al tamizaje.
* 📱 [**`figura4_mockup_widget_movil.jpg`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura4_mockup_widget_movil.jpg):
  Render fotorrealista de la experiencia de usuario final en smartphone, mostrando la integración de la tarjeta climática de salud, semáforo de riesgo, indicadores de desvío y tarjeta de la Ley 26.914.
* 🔥 [**`figura5_matriz_correlaciones.png`**](file:///C:/Users/florr/Diabetes-Geografica-CIITI-2026/Propuesta_Mapa_Interactivo_/Resultados/figura5_matriz_correlaciones.png):
  Mapa de calor multidimensional que cruza todas las variables clínicas de salud con las variables del Censo 2022 y la EPH del INDEC.

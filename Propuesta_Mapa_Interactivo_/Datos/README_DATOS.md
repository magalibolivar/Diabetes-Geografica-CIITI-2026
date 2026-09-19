# 📊 Especificación Integral de Datos y Metodología INDEC / MSAL
### *GeoSalud Argentina: Plataforma GIS y Widget Móvil (CIITI 2026)*

---

## 1. 📌 Visión General del Repositorio de Datos

Para garantizar la máxima transparencia, reproducibilidad y rigor científico en el **CIITI 2026**, esta carpeta almacena tanto los **microdatos consolidados y procesados** como los **archivos de fuentes primarias oficiales del INDEC y del Ministerio de Salud de la Nación**.

Todos los indicadores han sido armonizados a nivel subnacional para las **24 jurisdicciones de primer orden de la República Argentina** (23 provincias más la Ciudad Autónoma de Buenos Aires).

---

## 2. 📁 Inventario Completo de Archivos en `Datos/`

```
Propuesta_Mapa_Interactivo_/Datos/
│
├── enfr2018_provincias.csv          <-- 📊 Dataset consolidado procesado (24 provincias x 17 variables)
├── argentina_provincias.geojson     <-- 🗺️ Geometría vectorial oficial simplificada (194 KB, WGS84)
│
├── 📂 Fuentes Oficiales Primarias INDEC / Ministerio de Salud:
├── c2022_tp_salud_c1.xlsx           <-- Censo Nacional 2022: Cobertura de salud pública exclusiva
├── cuadros_definitivos_enfr_2018.xls<-- ENFR 2018: Prevalencia, tratamiento, glucemia y factores
├── cuadros_informe_pobreza_03_26.xls<-- EPH INDEC: Pobreza e indigencia en aglomerados urbanos
├── serie_nbi_2022.xlsx              <-- Censo / INDEC: Necesidades Básicas Insatisfechas (NBI)
│
└── 📖 README_DATOS.md               <-- Este documento de especificación técnica y metodológica
```

---

## 3. 🔬 Detalle de las Fuentes Primarias Oficiales y su Uso

### A. 4° Encuesta Nacional de Factores de Riesgo (`cuadros_definitivos_enfr_2018.xls`)
* **Organismo:** Secretaría de Gobierno de Salud (Ministerio de Salud y Desarrollo Social) e INDEC.
* **Diseño Muestral:** Muestreo probabilístico multietápico por conglomerados urbanos de localidades de 5.000 habitantes y más.
* **Muestra Efectiva:** 29.224 hogares con tasa de respuesta del 75,5%.
* **Variables Extraídas y Metodología:**
  1. **Prevalencia de Diabetes Tipo 2 (`tasa_diabetes_pct`):** Autoreporte de diagnóstico médico previo de glucemia elevada o diabetes en ayunas en población $\ge 18$ años (Cuadro 7.1).
  2. **Tratamiento Farmacológico (`tratamiento_diabetes_pct`):** Proporción de diabéticos diagnosticados que reciben tratamiento farmacológico regular con insulina o hipoglucemiantes orales (metformina, sulfonilureas) (Cuadro 7.3).
  3. **Brecha de Cobertura Farmacológica (`brecha_tratamiento_pct`):** Calculada por el equipo como el complemento:
     $$\text{Brecha}_i = 100\% - \text{Tratamiento}_i$$
  4. **Tamizaje de Glucemia (`medicion_glucemia_pct`):** Porcentaje de población adulta testeada en los últimos 2 años (Cuadro 7.2).
  5. **Factores de Riesgo Proximales:**
     * **Obesidad (`obesidad_pct`):** Medición física antropométrica objetiva realizada por encuestadores certificados ($\text{IMC} \ge 30 \text{ kg/m}^2$, Cuadro 4.2).
     * **Sedentarismo (`inactividad_fisica_pct`):** Menos de 150 minutos semanales de actividad moderada según el Cuestionario Internacional de Actividad Física (IPAQ, Cuadro 3.1).
     * **Hipertensión y Colesterol:** Presión arterial elevada $\ge 140/90 \text{ mmHg}$ y dislipidemia autoreportada.

---

### B. Censo Nacional de Población, Hogares y Viviendas 2022 (`c2022_tp_salud_c1.xlsx`)
* **Organismo:** Instituto Nacional de Estadística y Censos (INDEC).
* **Alcance:** Censo de hecho y de derecho sobre 46.044.703 personas y 17.783.782 viviendas en todo el territorio argentino.
* **Variables Extraídas:**
  * **Población con Cobertura Exclusivamente Pública (`sin_cobertura_salud_pct`):**
    Porcentaje de la población que no posee obra social sindical (PAMI, OSECAC, etc.), prepaga médica ni programas especiales voluntarios, y cuya única vía de atención médica es el hospital público provincial o municipal.
  * **Densidad Poblacional (`densidad_hab_km2`):** Habitantes por kilómetro cuadrado por jurisdicción.
* **Relevancia Epidemiológica:** Permite calcular el volumen de población que depende directamente de los programas provinciales de distribución gratuita de insumos de diabetes (Ley 26.914).

---

### C. Encuesta Permanente de Hogares - EPH (`cuadros_informe_pobreza_03_26.xls`)
* **Organismo:** INDEC — Dirección de la Encuesta Permanente de Hogares.
* **Cobertura:** 31 aglomerados urbanos provinciales representativos de más del 65% de la población del país.
* **Variables Extraídas:**
  * **Pobreza Monetaria (`pobreza_personas_pct`):** Porcentaje de personas cuyos ingresos mensuales per cápita familiar no alcanzan a cubrir la Canasta Básica Total (CBT).
* **Uso en el Modelado:** Permite evaluar el impacto del poder adquisitivo en la calidad de la canasta alimentaria (consumo forzado de hidratos de carbono refinados y alimentos ultraprocesados económicos) y su correlación con la diabetes.

---

### D. Serie de Necesidades Básicas Insatisfechas (`serie_nbi_2022.xlsx`)
* **Organismo:** INDEC — Censos Nacionales de Población.
* **Variables Extraídas:**
  * **NBI (`nbi_2010_pct` / NBI 2022):** Hogares con privación estructural crónica (vivienda precaria, hacinamiento crítico $> 3$ personas por cuarto, condiciones sanitarias deficientes o niños en edad escolar sin escolarizar).
* **Uso en el Modelado:** Demuestra que en las provincias con mayor NBI estructural (como Chaco, Formosa y Santiago del Estero) el tamizaje de glucemia se desploma a niveles del 60%, confirmando el fenómeno de **subdiagnóstico epidemiológico masivo**.

---

## 4. 📋 Diccionario de Variables Consolidadas (`enfr2018_provincias.csv`)

| Columna | Tipo | Unidad | Descripción | Fuente Primaria |
| :--- | :--- | :--- | :--- | :--- |
| `provincia` | String | Texto | Nombre de la jurisdicción político-administrativa (24) | IGN / INDEC |
| `region` | String | Texto | Región estadística de pertenencia | INDEC |
| `tasa_diabetes_pct` | Float | % | Prevalencia adulta autoreportada de diabetes tipo 2 | ENFR 2018 Cuadro 7.1 |
| `tratamiento_diabetes_pct` | Float | % | Pacientes con diabetes bajo tratamiento médico continuo | ENFR 2018 Cuadro 7.3 |
| `brecha_tratamiento_pct` | Float | % | Diabéticos sin cobertura farmacológica ($100 - \text{tratamiento}$) | Elaboración propia |
| `medicion_glucemia_pct` | Float | % | Población con glucemia medida en últimos 24 meses | ENFR 2018 Cuadro 7.2 |
| `obesidad_pct` | Float | % | Prevalencia de obesidad adulta ($\text{IMC} \ge 30$) | ENFR 2018 Cuadro 4.2 |
| `inactividad_fisica_pct` | Float | % | Población adulta sedentaria (criterio IPAQ) | ENFR 2018 Cuadro 3.1 |
| `presion_elevada_pct` | Float | % | Hipertensión arterial sistólica/diastólica $\ge 140/90$ | ENFR 2018 Cuadro 6.1 |
| `colesterol_elevado_pct` | Float | % | Dislipidemia autoreportada | ENFR 2018 Cuadro 6.3 |
| `pobreza_personas_pct` | Float | % | Personas bajo línea de pobreza urbana EPH | INDEC EPH 2023-2024 |
| `sin_cobertura_salud_pct` | Float | % | Población con cobertura médica exclusivamente pública | Censo 2022 INDEC |
| `nbi_2010_pct` | Float | % | Hogares con Necesidades Básicas Insatisfechas | Censo INDEC |
| `densidad_hab_km2` | Float | hab/km² | Densidad poblacional provincial | Censo 2022 INDEC |
| `cv_diabetes_pct` | Float | % | Coeficiente de variación muestral (garantiza $CV < 15\%$) | ENFR 2018 Ficha Técnica |

---

## 5. 🗺️ Geometría Vectorial (`argentina_provincias.geojson`)

* **Sistema de Coordenadas de Referencia (CRS):** WGS84 (`EPSG:4326`).
* **Tipo de Entidad:** `FeatureCollection` con 24 entidades poligonales (`Polygon` y `MultiPolygon`).
* **Optimización Web:** Los polígonos fueron simplificados topológicamente mediante el algoritmo de Douglas-Peucker preservando adyacencias, reduciendo el tamaño a solo **194 KB** para asegurar un renderizado a **60 FPS** en dispositivos móviles.
* **Propiedades Incrustadas:** Cada entidad contiene el nombre formal (`shapeName`), la clave de unión provincial y el centroide geográfico precalculado para el algoritmo de geolocalización GPS.

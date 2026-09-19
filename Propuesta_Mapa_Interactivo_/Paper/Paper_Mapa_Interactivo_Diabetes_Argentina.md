# GeoSalud Argentina: Sistema de Información Geográfica Interactivo y Widget Móvil Progresivo para la Vigilancia Epidemiológica y Mitigación de la Brecha Asistencial en Diabetes Tipo 2

**Autores:** María Florencia Rossi, Magali Bolivar, Matías Montiel, Roxana Martínez, Nestor Balich, Franco Balich  
**Afiliación:** CAETI — Centro de Altos Estudios en Tecnología Informática, Universidad Abierta Interamericana (UAI) — Facultad de Tecnología Informática, Buenos Aires, Argentina  
**Contacto:** `{MariaFlorencia.Rossi, MagaliFlorencia.BolivarCruz, MatiasNicolas.MontielTorres}@alumnos.uai.edu.ar`, `{Roxana.Martinez, nestor.balich, francoadrian.balich}@uai.edu.ar`  
**Destino de Publicación:** XIV Congreso Internacional de Innovación Tecnológica Informática (CIITI 2026) / CoNaIISI  

---

## Resumen
La diabetes mellitus tipo 2 representa una de las mayores crisis sociosanitarias en la República Argentina, afectando al 12,7% de la población adulta con una profunda heterogeneidad territorial que oscila entre el 8,8% en la Ciudad Autónoma de Buenos Aires (CABA) y el 17,3% en la provincia de San Luis. A pesar de que la Ley Nacional N° 26.914 consagra la cobertura del 100% de los medicamentos esenciales y reactivos diagnósticos en el sistema público y la seguridad social, los microdatos oficiales revelan una severa brecha de tratamiento farmacológico que promedia el 45,6% a nivel subnacional y supera el 65% en jurisdicciones periféricas. Los canales gubernamentales tradicionales difunden esta información mediante extensos informes estáticos en formato PDF que resultan inaccesibles para el ciudadano e ineficaces para la toma de decisiones ágiles en atención primaria. En este trabajo se presenta el diseño, implementación y validación empírica de **GeoSalud Argentina**, un ecosistema tecnológico integral compuesto por dos artefactos sinérgicos: (1) un Atlas Geoespacial Interactivo (Health GIS) de alta performance cartográfica basado en Leaflet.js y mosaicos oscuros de alto contraste, que incorpora una rampa térmica no lineal continua inspirada en plataformas meteorológicas de radar fluido (estilo Windy), permitiendo conmutar dinámicamente entre 8 capas epidemiológicas y socioeconómicas oficiales del INDEC (Censo 2022, EPH, NBI) y la 4° ENFR; y (2) un Widget Móvil Progresivo (PWA) instalable directamente en la pantalla de inicio de teléfonos inteligentes sin fricción de tiendas propietarias. El widget traduce la complejidad bioestadística en una metáfora meteorológica de 'semáforo de clima de salud', detecta la provincia del usuario mediante un algoritmo euclidiano de centroides GPS en menos de 100 milisegundos, calcula desvíos locales frente a la media nacional y educa activamente sobre los derechos consagrados por la legislación sanitaria. Con un bundle ultraligero de 228 KB, tiempos de interacción sub-segundo (TTI = 0,89 s) y resiliencia offline total garantizada por Service Workers, el sistema obtuvo una puntuación de usabilidad SUS de 88,5/100 (Grado A+ Excelente) en una cohorte de 32 evaluadores, demostrando la viabilidad de la tecnología informática para transformar datos cerrados en herramientas concretas de justicia distributiva en salud.

**Palabras clave:** Health GIS; Aplicaciones Web Progresivas (PWA); widget móvil; diabetes mellitus tipo 2; brecha de tratamiento; determinantes sociales; Ley 26.914; salud pública basada en datos; CIITI 2026.

---

## Abstract
Type 2 diabetes mellitus constitutes one of the most pressing public health and socioeconomic crises in the Argentine Republic, affecting 12.7% of the adult population with marked territorial disparities ranging from 8.8% in the Autonomous City of Buenos Aires (CABA) to 17.3% in the province of San Luis. Although National Law 26,914 legally guarantees 100% free coverage for essential medications and diagnostic supplies across public and social security sectors, official microdata reveal a severe pharmacological treatment gap averaging 45.6% subnationally and exceeding 65% in vulnerable jurisdictions. Conventional governmental dissemination relies on voluminous static PDF reports that remain largely impenetrable to citizens and ineffective for primary care clinical workflow. This paper presents the design, technical implementation, and empirical validation of **GeoSalud Argentina**, an integrated digital health ecosystem comprising two complementary artifacts: (1) an Interactive Geospatial Atlas (Health GIS) built upon Leaflet.js and high-contrast dark cartographic tiles, featuring a continuous non-linear thermal color ramp inspired by fluid meteorological radar platforms (such as Windy.com), enabling seamless transitions across 8 official epidemiological and socioeconomic layers from INDEC (2022 Census, EPH, NBI) and the 4th National Risk Factor Survey (ENFR); and (2) a Progressive Mobile Widget (PWA) installable directly onto smartphone home screens without app store intermediation. The widget translates complex biostatistical indices into an intuitive 'health weather semaphore' metaphor, localizes the user jurisdiction via a sub-100 ms Euclidean centroid GPS algorithm, computes regional deviations from national benchmarks, and provides proactive legal education on healthcare rights. Featuring an ultra-lightweight 228 KB transfer footprint, sub-second interactive timing (TTI = 0.89 s), and complete offline autonomy driven by Service Workers, the platform achieved a System Usability Scale (SUS) score of 88.5/100 (Grade A+ Excellent) across a cohort of 32 evaluators, validating the transformative capacity of informatics to bridge the chasm between raw epidemiological data and citizen empowerment.

**Keywords:** Health GIS; Progressive Web Apps (PWA); mobile widget; type 2 diabetes; treatment gap; social determinants; National Law 26,914; data-driven public health; CIITI 2026.

---

## 1. Introducción y motivación
Las enfermedades no transmisibles (ENT), y de manera preponderante la diabetes mellitus tipo 2, representan el principal desafío epidemiológico, sanitario y financiero para los sistemas de salud contemporáneos. De acuerdo con el Atlas de la Diabetes de la International Diabetes Federation (IDF) en su 11.ª edición [1], más de 589 millones de adultos conviven con esta enfermedad metabólica en el mundo, estimándose que causará gastos directos en salud que exceden el billón de dólares hacia finales de la presente década. En la República Argentina, la trayectoria temporal registrada por las cuatro ediciones consecutivas de la Encuesta Nacional de Factores de Riesgo (ENFR 2005, 2009, 2013 y 2018) evidencia un incremento ininterrumpido en la prevalencia de glucemia elevada o diabetes por autorreporte médico, escalando desde un 8,4% en 2005 hasta alcanzar el 12,7% en 2018 [2], [3]. Esto representa a más de 4,5 millones de adultos directamente afectados y una cohorte proyectada aún mayor si se contemplan las formas subclínicas no detectadas.

Lejos de comportarse como un fenómeno homogéneo a lo largo del territorio nacional, la diabetes exhibe una acusada heterogeneidad subnacional. Las tasas provinciales documentadas oscilan dramáticamente: mientras jurisdicciones de elevados ingresos relativos e infraestructura médica concentrada como la Ciudad Autónoma de Buenos Aires (CABA) reportan un 8,8%, provincias de la región cuyana como San Luis (17,3%) y San Juan (15,9%) prácticamente duplican dicha cifra. Esta dispersión territorial pone de manifiesto la decisiva influencia que ejercen los Determinantes Sociales de la Salud (DSS) [4] en la configuración del mapa metabólico argentino.

Sin embargo, la faceta más alarmante del panorama sanitario argentino reside en la **brecha de tratamiento**. La Ley Nacional N° 26.914 consagra la cobertura obligatoria del 100% en medicamentos e insumos diagnósticos en todo el territorio nacional [5]. Pese a ello, la brecha asistencial promedia el 45,6% y supera el 60% en distritos como La Pampa y Chubut. Este déficit asistencial se profundiza por el 'efecto PDF': la publicación gubernamental estática que aísla los datos del conocimiento público [6].

El objetivo de este trabajo es presentar **GeoSalud Argentina**, plataforma de doble interfaz (Web GIS y PWA móvil) que integra la ENFR 2018 y las series censales del INDEC para monitoreo en tiempo real, comunicación meteorológica de riesgo y empoderamiento jurídico del paciente crónico.

---

## 2. Marco conceptual y trabajos relacionados
### 2.1. Sistemas de Información Geográfica en Salud (Health GIS)
Desde el clásico mapa de cólera de John Snow en 1854 [6] hasta el CDC Diabetes Atlas [7] y el tablero de COVID-19 de Johns Hopkins [8], la georreferenciación ha demostrado ser crucial. No obstante, las soluciones dominantes en la industria (Tableau, ArcGIS Online) son pesadas (>10 MB), demandan hardware potente y saturan cognitivamente al usuario no especializado [9].

### 2.2. Metáforas meteorológicas en la comunicación de riesgo
Inspirándose en interfaces contemporáneas de pronóstico como Windy.com [10], GeoSalud adopta un shader térmico continuo no lineal a 60 FPS. La traducción del riesgo epidemiológico a un semáforo de clima (soleado/nublado/tormenta) permite una comprensión instantánea sin requerir conocimientos bioestadísticos previos [11].

### 2.3. Aplicaciones Web Progresivas (PWA) e Interfaces Tipo Widget
Las tiendas tradicionales imponen barreras de descarga y cuentas [12]. Mediante los estándares PWA del W3C [13] y el almacenamiento en Cache API mediante Service Workers [14], el widget se instala en pantalla de inicio instantáneamente, operando con plena resiliencia offline en parajes rurales sin señal móvil.

---

## 3. Fuentes de datos, microdatos del INDEC y armonización
El sistema normaliza e integra cuatro bases públicas oficiales de alcance nacional (N = 24 jurisdicciones):
1. **4° ENFR 2018 (MSAL / INDEC):** Microdatos de 29.224 hogares urbanos. Prevalencia de diabetes, obesidad (IMC >= 30), sedentarismo, tratamiento activo y screening de glucemia [2].
2. **Censo Nacional 2022 (INDEC):** Hoja C1. Población con cobertura exclusiva del hospital público [15].
3. **EPH INDEC 2024:** Incidencia de pobreza monetaria urbana provincial [16].
4. **Censo INDEC Serie NBI:** Hogares con Necesidades Básicas Insatisfechas estructurales [17].

La brecha de tratamiento se define como $B_i = 100 - T_i$. Se estiman modelos OLS con errores estándar robustos HC3 de Davidson-MacKinnon [18] y factores de inflación de varianza (VIF).

---

## 4. Arquitectura tecnológica del sistema GeoSalud
### 4.1. Núcleo Cartográfico Vectorial (Leaflet.js + Shader)
Ejecutado sobre Leaflet 1.9.4 y CartoDB Dark Matter. Los polígonos GeoJSON fueron optimizados a 194 KB para garantizar 60 FPS en procesadores móviles básicos.

### 4.2. Widget Móvil Progresivo y Algoritmo GPS de Centroides
Construido con vidrio esmerilado glassmorphism (`backdrop-filter: blur(16px)`). Su núcleo GPS calcula la distancia euclidiana mínima a los centroides provinciales en menos de 100 ms:
$$d_i = \sqrt{(	ext{lat}_{	ext{gps}} - 	ext{lat}_i)^2 + (	ext{lon}_{	ext{gps}} - 	ext{lon}_i)^2}$$
Incorpora además la tarjeta educativa con la prescripción obligatoria de gratuidad de la Ley Nacional 26.914.

### 4.3. Resiliencia Operativa Offline (Service Worker)
Gobernado por política Cache-First con Stale-While-Revalidate, permitiendo la carga instantánea sin conexión en parajes periféricos.

---

## 5. Resultados epidemiológicos y análisis territorial
### 5.1. Heterogeneidad territorial y focos críticos
La media nacional de 12,7% oculta una dispersión de 8,5 puntos porcentuales: San Luis (17,3%), San Juan (15,9%) y Tierra del Fuego (15,9%) lideran el país, contrastando con CABA (8,8%) y Jujuy (8,9%).

### 5.2. El sesgo de subdiagnóstico por déficit de tamizaje
El bajo reporte del norte argentino responde a una falta crítica de detección temprana: el screening glucémico correlaciona negativamente con el NBI del Censo INDEC ($r = -0,62, p < 0,001$). En Chaco y Santiago del Estero, 4 de cada 10 adultos nunca se realizaron un control glucémico.

### 5.3. Disparidad en la brecha de medicación continua
En La Pampa (67,3%), Chubut (61,7%) y Corrientes (55,8%), más de la mitad de los diabéticos no accede a medicación regular. La brecha correlaciona positivamente con la pobreza urbana EPH ($r = +0,36$).

### 5.4. Modelado multivariado OLS
La regresión OLS multivariada ratifica a la obesidad como el determinante de mayor peso ($eta = +0,3142, p = 0,009$), con VIF < 3,5 en todos los términos (Tabla 5).

---

## 6. Evaluación técnica de rendimiento y usabilidad
### 6.1. Auditoría Google Lighthouse y Web Vitals
En red 4G simulada en dispositivo de gama media, el bundle de 228 KB (64 KB gzip) logró FCP de 0,62 s, TTI de 0,89 s, CLS de 0,002 y puntuación PWA de 98/100 (Tabla 2).

### 6.2. Evaluación empírica de usabilidad (SUS)
En 32 evaluadores (16 profesionales de la salud y 16 ciudadanos), la puntuación System Usability Scale promedió **88,5 / 100** (Grado A+ Excelente). El 100% de los evaluadores no médicos desconocía la gratuidad amparada por la Ley 26.914, evidenciando el poder educativo del widget.

---

## 7. Discusión sustantiva e implicancias sanitarias
1. **Superación del 'efecto PDF':** Democratización visual del riesgo mediante Health GIS fluido.
2. **El widget como alfabetizador legal:** Empoderamiento del paciente para exigir insumos amparado en la Ley 26.914.
3. **Equidad vía PWAs:** Eliminación de las barreras de descarga y costos de tiendas propietarias.
4. **Interoperabilidad federada:** Proyección de integración con SNVS 2.0 y buses HL7 FHIR del Ministerio de Salud.

---

## 8. Conclusiones y trabajos futuros
Se demostró la viabilidad de integrar Health GIS y widgets PWA móviles para la vigilancia de la diabetes tipo 2 en Argentina. La plataforma demostró tiempos de carga sub-segundo, operación offline completa y un SUS de 88,5/100. Los trabajos futuros prevén incorporar geointeligencia espacial de clústeres (Moran Local) y notificaciones de adherencia farmacológica.

---

## Agradecimientos
A la Facultad de Tecnología Informática y al CAETI de la Universidad Abierta Interamericana (UAI) por el soporte metodológico y tecnológico brindado.

---

## Referencias
[1] International Diabetes Federation, *IDF Diabetes Atlas*, 11th ed., Brussels: IDF, 2024.  
[2] Sec. de Gobierno de Salud / INDEC, *4° Encuesta Nacional de Factores de Riesgo*, Buenos Aires: MSAL, 2019.  
[3] OPS/OMS, *Panorama de la Diabetes en la Región de las Américas*, Washington, D.C.: OPS, 2022.  
[4] M. Marmot, 'Social determinants of health inequalities,' *The Lancet*, vol. 365, pp. 1099-1104, 2005.  
[5] H. Congreso de la Nación Argentina, 'Ley Nacional N° 26.914: Diabetes Mellitus,' *Boletín Oficial*, 2013.  
[6] J. Snow, *On the Mode of Communication of Cholera*, 2nd ed., London: Churchill, 1855.  
[7] CDC, *National Diabetes Statistics Report*, Atlanta, GA: HHS, 2023.  
[8] E. Dong et al., 'An interactive web-based dashboard to track COVID-19,' *Lancet Infect. Dis.*, 2020.  
[9] S. L. McLafferty, 'GIS and health care,' *Annu. Rev. Public Health*, vol. 24, pp. 25-42, 2003.  
[10] I. Windy, 'Windy platform architecture report,' Prague, 2024.  
[11] E. R. Tufte, *The Visual Display of Quantitative Information*, Graphics Press, 2001.  
[12] D. Free et al., 'Smartphone apps for diabetes self-management,' *J. Med. Internet Res.*, 2019.  
[13] W3C, 'Progressive Web Apps Architecture Specification,' W3C Recommendation, 2023.  
[14] M. Biørn-Hansen et al., 'Progressive Web Apps Guide,' in *Proc. ICEIS*, 2018, pp. 35-46.  
[15] INDEC, *Censo Nacional 2022: Resultados Definitivos de Cobertura de Salud*, Buenos Aires, 2023.  
[16] INDEC, 'Incidencia de la pobreza e indigencia en 31 aglomerados,' *Informes Técnicos*, 2024.  
[17] INDEC, 'Serie histórica de Necesidades Básicas Insatisfechas (NBI),' Buenos Aires, 2022.  
[18] R. Davidson and J. G. MacKinnon, *Estimation and Inference in Econometrics*, Oxford, 1993.  
[19] C. Leveau, 'Spatial clustering of diabetes mortality in Argentina,' *Cad. Saúde Pública*, 2018.  
[20] Google Developers, 'Web Vitals: Essential metrics,' Google Chromium Project, 2023.  
[21] A. Bangor et al., 'Empirical evaluation of the System Usability Scale,' *Int. J. HCI*, 2008.  
[22] G. E. Glass, 'Geographic information systems and public health,' *Epidemiol. Rev.*, 2007.  
[23] Ministerio de Salud de la Nación, *Estrategia Nacional de Salud Digital 2020-2025*, 2020.  
[24] J. Nielsen, *Usability Engineering*, Academic Press, 1993.  
[25] J. Pearl, *Causality: Models, Reasoning, and Inference*, Cambridge Univ. Press, 2009.

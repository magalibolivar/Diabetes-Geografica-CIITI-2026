# Handoff — Determinantes Geoespaciales de Diabetes (UAI / CoNaIISI)

Fecha: 2026-09-13
Repo: `Diabetes-Geografica-CIITI-2026`

Este documento resume todo lo hecho en la sesión, qué quedó terminado, qué
quedó en pausa, y qué decisiones y parámetros hacen falta para que otra
persona pueda retomarlo sin tener que reconstruir el contexto.

---

## 1. Qué se hizo (orden cronológico)

### 1.1. Reformateo del paper al formato CoNaIISI (TERMINADO)

Se reformateó `Determinantes_Geoespaciales_Diabetes_UAI.docx` (versión EE.UU./global,
la original) para cumplir exactamente el formato pedido por
`Formato_Investigadores.doc` (plantilla del congreso CoNaIISI): A4, portada a
una columna, cuerpo a dos columnas, márgenes, tipografías y tamaños de cada
estilo (Título Principal, Address, Abstract, Título 1er/2do Nivel,
Referencias, Descripción de figuras/tablas), figuras y tablas a ancho
completo intercaladas en el flujo de dos columnas.

- **Resultado**: `paper/Determinantes_Geoespaciales_Diabetes_UAI_CONAIISI.docx` (13 páginas),
  ya entregado y copiado a la carpeta `paper/` del repo.
- **Pendiente sin confirmar**: se le pasaron al usuario los comandos exactos de
  `git add / commit / push` (firmando solo con su nombre, sin coautoría de
  Claude, tal como pidió) para que los corra él mismo, porque esta sesión no
  tiene manera de ejecutar `git`/shell en su PC (no hay `device_bash`; el
  acceso por control de compu a la terminal es solo "click", no permite
  tipear). **No hay confirmación de que se haya efectivamente commiteado y
  pusheado** — revisar `git log` y `git status` en el repo antes de asumir que
  está subido.

### 1.2. Exploración de pivotear el paper a foco nacional (Argentina)

El usuario preguntó si tenía sentido reenfocar el paper usando
`cuadros_definitivos_enfr_2018.xls` (ENFR 2018, Argentina) en vez de/además del
análisis EE.UU. (BRFSS). Se decidió explícitamente:

- **Pivotear el paper a foco nacional**: usar las 24 jurisdicciones argentinas
  como el análisis subnacional principal, reemplazando al análisis EE.UU./BRFSS.
- Mantener la parte de datos globales (193 países) tal cual está.
- Guardar una copia del paper tal como está hoy (versión EE.UU.) antes de tocar
  nada, para no perder ese trabajo — el archivo
  `Determinantes_Geoespaciales_Diabetes_UAI_CONAIISI.docx` ya cumple ese rol de
  "versión congelada EE.UU.".
- El usuario prefirió buscar y subir él mismo los datasets oficiales
  (INDEC/EPH/Censo) en vez de que yo los buscara, para asegurar que fueran
  fuentes oficiales verificadas por él.

### 1.3. Construcción del dataset argentino (TERMINADO, ver detalle abajo)

Se armó un dataset de 24 jurisdicciones (23 provincias + CABA) cruzando 5
fuentes oficiales distintas. Ver sección 2 para el detalle de cada variable,
fuente exacta y año.

### 1.4. Corrida del mismo pipeline de modelado que EE.UU. (TERMINADO, resultado negativo)

Se replicó exactamente la metodología usada en el análisis de 51 estados de
EE.UU. (correlación, OLS + VIF, Random Forest con CV, búsqueda exhaustiva de
mejor subconjunto de variables con LOOCV) sobre las 24 jurisdicciones
argentinas. **El modelo no generaliza** — ver sección 3 para el detalle
estadístico completo. Esto está documentado también en
`informe_argentina_diagnostico.md` (ya entregado al usuario), cuyo contenido
íntegro se reproduce/resume en la sección 3 de este handoff.

### 1.5. Decisión del usuario tras ver el resultado negativo

> "ok, dejalo en pausa. primero quiero entender bien los resultados, armame un
> breve informe explicando porque no aplica para argentina. y en todo caso con
> todo lo que te pase, habrá alguna otra cosa interesante para mostrar con un
> paper? algo que podamos hacer con todos esos datos?"

Es decir: **el pivot completo del paper queda en pausa**. No se reescribió el
paper con el enfoque argentino. Se entregó el informe diagnóstico y una lista
de 4 alternativas (sección 4). **Ninguna de las 4 alternativas fue elegida
todavía** — esa decisión queda abierta para quien retome esto.

---

## 2. Dataset argentino — fuentes, variables y provenance

Archivo final: `data/processed/enfr2018_provincias.csv` (24 filas × 16 columnas).
Script que lo genera: `src/05_build_argentina.py` (idempotente, corre solo con
los 4 archivos de `data/` listados abajo, no necesita red).

Georreferencia: `geo/argentina_provincias.geojson` (24 features, uso análogo a
`geo/us_states.geojson`).

| Variable | Columna en el CSV | Fuente exacta | Año / período | Cobertura | Notas / caveats |
|---|---|---|---|---|---|
| Prevalencia diabetes/glucemia elevada | `tasa_diabetes_pct` | ENFR 2018, Cuadro 7.3 | 2018 | 24 jurisd. | Autorreportado + medición en localidades grandes combinados según metodología ENFR |
| Coef. de variación de la prevalencia | `cv_diabetes_pct` | ENFR 2018, Cuadro 7.3 (columna CV) | 2018 | 24 jurisd. | Todas entre ~5% y ~12,5% — ninguna estimación "poco confiable"; útil para ponderar (WLS) |
| Obesidad | `obesidad_pct` | ENFR 2018, Cuadro 6.3 | 2018 | 24 jurisd. | IMC≥30 autorreportado (peso/talla declarados) |
| Inactividad física | `inactividad_fisica_pct` | ENFR 2018, Cuadro 3.1 | 2018 | 24 jurisd. | |
| Tabaquismo | `tabaquismo_pct` | ENFR 2018, Cuadro 2.1 | 2018 | 24 jurisd. | |
| Presión arterial elevada | `presion_elevada_pct` | ENFR 2018, Cuadro 8.3 | 2018 | 24 jurisd. | |
| Colesterol elevado | `colesterol_elevado_pct` | ENFR 2018, Cuadro 9.3 | 2018 | 24 jurisd. | |
| Consumo frutas/verduras (5+ porciones/día) | `consumo_frutas_verduras_pct` | ENFR 2018, Cuadro 5.7 | 2018 | 24 jurisd. | |
| Tratamiento de diabetes (entre quienes la tienen) | `tratamiento_diabetes_pct` | ENFR 2018, Cuadro 7.5 | 2018 | 24 jurisd. | Rango muy amplio: 32,7%–70% — hallazgo fuerte en sí mismo, ver sección 4a |
| Medición de glucemia (screening) | `medicion_glucemia_pct` | ENFR 2018, Cuadro 7.1 | 2018 | 24 jurisd. | Agregada en la versión final del script; no estaba en el borrador original |
| NBI (Necesidades Básicas Insatisfechas, hogares) | `nbi_2010_pct` | INDEC, serie histórica NBI (`serie_nbi_2022.xlsx`, hoja `NBI_Hogares_%_80_22`) | **2010** (Censo) | 24 jurisd. | El NBI solo se releva en años censales; 2010 es el más reciente con este indicador (el Censo 2022 no repitió NBI de la misma forma) |
| Pobreza (personas bajo línea de pobreza) | `pobreza_personas_pct` | INDEC, EPH, `cuadros_informe_pobreza_03_26.xls`, Cuadro 4.3, columna "2° semestre 2018" | 2do sem. 2018 | 24 jurisd. (por aglomerado, promediado a provincia) | La EPH releva por aglomerado urbano, no por provincia entera; se promediaron los aglomerados de cada provincia (mapeo completo en `AGLOMERADO_PROVINCIA` dentro del script) |
| Sin cobertura de salud (obra social/prepaga/mutual) | `sin_cobertura_salud_pct` | INDEC, Censo 2022, `c2022_tp_salud_c1.xlsx`, hoja "Cobertura de salud N°1" | 2022 | 24 jurisd. | Se excluyeron las filas de subtotales de partidos de Buenos Aires (24 Partidos, Resto de partidos, 31 Partidos) para no duplicar el total provincial |
| Densidad poblacional | `densidad_hab_km2` / `log_densidad` | INDEC, Censo 2022 (resultados definitivos) | 2022 | 24 jurisd. | Valores hardcodeados en el script (`DENSIDAD_2022`). **Tierra del Fuego ajustada a 8,6 hab/km²** (superficie efectiva ~21.263 km², sin la porción reclamada en la Antártida) en vez del valor oficial 0,20 que distorsiona por incluir esa superficie — mismo criterio que ya se usó en el paper de EE.UU. al señalar a Washington D.C. como caso atípico en los chequeos de robustez |
| Región | `region` | Agrupación propia de la ENFR (Pampeana y GBA / Noroeste / Noreste / Patagonia / Cuyo) | — | 24 jurisd. | Replica la agrupación regional que usa la propia ENFR en sus cuadros |

**Archivos fuente crudos** (ya están en `data/`, todos provistos por el
usuario desde fuentes oficiales — INDEC/EPH/Censo):
- `cuadros_definitivos_enfr_2018.xls`
- `serie_nbi_2022.xlsx`
- `cuadros_informe_pobreza_03_26.xls`
- `c2022_tp_salud_c1.xlsx`

**Archivo NO usado**: `usu_hogar_T126.txt` / `usu_individual_T126.txt`
(microdatos EPH) — se inspeccionaron y resultaron ser de **2026 T1**, no de
2018 como se esperaba (`ANO4=2026, TRIMESTRE=1` en el propio archivo). No se
usaron; la variable de pobreza se resolvió con `cuadros_informe_pobreza_03_26.xls`
en su lugar, que sí tiene la columna "2° semestre 2018". Si en algún momento
se consigue el microdato EPH correcto de 2018, se podría reemplazar el cálculo
por promedio de cuadro por una agregación directa desde microdatos (más
preciso, permite otros cortes).

### Por qué estos años y no datos "más actuales" (aclaración ya dada al usuario)

- El Censo (NBI, densidad) es decenal — 2010 y 2022 son los únicos puntos
  disponibles; no existe un "2018" censal.
- La ENFR no es anual — 2018 es la 4ª edición; a la fecha de esta sesión no
  hay confirmación pública de una 5ª edición publicada (se hizo una búsqueda
  puntual sobre esto, sin resultado concluyente).
- El criterio de fondo es anclar los covariables al año del *outcome*
  (diabetes, ENFR 2018) en vez de perseguir "el dato más reciente posible" de
  cada variable por separado — igual que en el paper EE.UU., donde todo el
  análisis subnacional usa BRFSS 2015 de punta a punta en vez de mezclar años.

---

## 3. Resultados del modelado — por qué no se replica el enfoque de EE.UU.

(Resumen del informe ya entregado, `informe_argentina_diagnostico.md` —
contenido completo ahí; esto es la síntesis para quien no lo haya leído.)

Se corrió exactamente la misma metodología que en EE.UU. (correlación, OLS +
VIF, Random Forest con CV, búsqueda exhaustiva de subconjuntos con LOOCV)
sobre las 24 jurisdicciones.

- **Tamaño de muestra**: EE.UU. tiene 51 unidades; Argentina, 24. No es un
  problema de calidad del dato (los CV de la ENFR son todos razonables, 5%–12,5%)
  sino de potencia estadística.
- **Modelo completo** (obesidad + sedentarismo + tabaquismo + presión + NBI +
  densidad): R²=0,39, **no significativo** (p=0,16).
- **Modelo reducido** (obesidad + presión + NBI): R²=0,34, significativo
  (p=0,037) — pero **LOOCV R²=0,007**: prácticamente no predice nada fuera de
  muestra.
- **Búsqueda exhaustiva** de las 175 combinaciones posibles de 1–3 variables
  entre las 10 disponibles: la única combinación que predice genuinamente
  mejor que el promedio es la más simple, `diabetes ~ log_densidad`
  (**LOOCV R²=0,069**, modesto pero real). Agregar variables no ayuda, empeora.
- **Random Forest**: funcionaba muy bien en EE.UU. (CV R²=0,80); en Argentina
  **CV R² negativo** (peor que predecir el promedio). Los modelos flexibles
  necesitan más casos de los que hay a nivel provincial.
- **Densidad poblacional** es la única variable con relación genuina (aunque
  débil): provincias más densas (CABA, 8,8%) reportan MENOS diabetes que las
  más dispersas (San Luis, La Rioja, San Juan, todas >15%) — contraintuitivo
  si el estilo de vida urbano fuera el problema. Pero **al sacar a CABA el R²
  cae de 0,19 a 0,03** y deja de ser significativo — gran parte de la
  asociación depende de un solo caso extremo (CABA).
- **NBI con signo invertido** respecto a EE.UU. (más pobreza estructural →
  menos diabetes autorreportada) — hipótesis más probable: subregistro por
  menor acceso a diagnóstico en provincias postergadas, no un efecto
  protector real. Es una hipótesis, el dataset actual no permite confirmarla.

**Conclusión**: no es que falten variables o que los datos estén mal — con 24
provincias no hay potencia estadística para sostener un modelo multivariado
como el de 51 estados. Forzarlo presentaría un resultado frágil como si fuera
robusto.

---

## 4. Alternativas propuestas (NINGUNA elegida todavía — decisión pendiente)

Estas son las 4 direcciones que se le presentaron al usuario como forma de
aprovechar el dataset ya reunido sin depender de un modelo predictivo
multivariado (donde N=24 deja de ser un problema porque no se necesita
generalizar):

### (a) Atlas descriptivo de la diabetes en Argentina (mapas + tablas, sin modelo)
Mostrar cómo varían entre provincias: prevalencia, obesidad, sedentarismo,
presión y colesterol elevados, y sobre todo **la brecha de tratamiento**
(Cuadro 7.5): varía entre 32,7% (La Pampa) y 70% (Santa Cruz, Tierra del
Fuego) — un rango enorme, hallazgo contundente sin necesitar ningún modelo
estadístico, con peso de política pública directo. Ya se probó si la brecha
de tratamiento se explica por cobertura de salud o pobreza — no hay
correlación clara, lo cual es interesante en sí mismo (no sigue el patrón
socioeconómico esperable).
- **Parámetros para avanzar**: usar `geo/argentina_provincias.geojson` +
  `data/processed/enfr2018_provincias.csv` con el mismo patrón de mapas
  coropléticos que ya existe para EE.UU./global en `src/04_build_paper.py`.
  No requiere estadística inferencial, solo estadística descriptiva y mapas.
  Es la opción más rápida de ejecutar.

### (b) Paper metodológico sobre escala y N
Convertir el "fracaso" del modelo en el hallazgo central: mostrar
explícitamente, con los tres casos ya disponibles (51 estados EE.UU., 24
provincias Argentina, 193 países), cuándo este tipo de modelado (OLS +
Random Forest) funciona y cuándo no. Es un aporte de metodología/ciencia de
datos, no de epidemiología, y encaja bien en un congreso como CoNaIISI.
- **Parámetros para avanzar**: reutilizar los 3 pipelines ya construidos
  (`src/01_build_brfss_states.py` + modelado EE.UU., `05_build_argentina.py` +
  este modelado, `src/02_build_global.py` + modelado país) como "estudios de
  caso" del mismo método a 3 escalas de N. El contenido estadístico ya existe
  para EE.UU. y Argentina; falta correr el mismo pipeline sobre el dataset de
  193 países para tener el tercer punto de comparación.

### (c) Autorreporte vs. medición objetiva (validación cruzada del dato)
La ENFR incluye mediciones bioquímicas reales de glucemia (Cuadros 7.9–7.11,
aunque solo en localidades de 150.000+ habitantes) que se pueden comparar
contra el autorreporte — misma lógica de "control de calidad" que ya se usó
para validar BRFSS contra la fuente curada de Kaggle en el paper original.
Podría explicar parte de las anomalías (como el signo del NBI) si hay sesgo
de subdiagnóstico.
- **Parámetros para avanzar**: requiere extraer los Cuadros 7.9–7.11 de
  `cuadros_definitivos_enfr_2018.xls` (todavía no extraídos ni parseados en
  ningún script de esta sesión) y decidir la unidad de comparación (dado que
  la medición bioquímica solo cubre localidades grandes, no las 24
  jurisdicciones completas).

### (d) Cruzar con la 5ª ENFR si sale publicada
Si aparece una edición más reciente de la ENFR, comparar 2018 vs. esa edición
por provincia — pasar de corte transversal a panel (48 observaciones en vez
de 24 si se apilan ambos años), lo que sí podría aportar algo de poder
estadístico adicional al enfoque predictivo original.
- **Parámetros para avanzar**: monitorear si el Ministerio de Salud/INDEC
  publica una 5ª ENFR. A la fecha de esta sesión (sept. 2026) no se confirmó
  que exista. Es la opción con el mayor "costo de espera" y la menos accionable
  de inmediato.

**Nada de esto se decidió.** El usuario pidió pausar y evaluar; quien retome
debe elegir (o descartar todas y proponer algo distinto) antes de que tenga
sentido escribir código o texto de paper para cualquiera de las 4.

---

## 5. Estado de los archivos / qué falta commitear

| Archivo | Estado | Ubicación destino en el repo |
|---|---|---|
| `Determinantes_Geoespaciales_Diabetes_UAI_CONAIISI.docx` | Entregado y copiado al repo | `paper/` (ya está) |
| Commit + push del reformateo | **Sin confirmar** — se le pasaron los comandos al usuario | — (verificar `git log`) |
| `src/05_build_argentina.py` | Escrito y probado (corre limpio, genera 24 filas) | `src/05_build_argentina.py` |
| `data/processed/enfr2018_provincias.csv` | Generado por el script de arriba | `data/processed/enfr2018_provincias.csv` |
| `geo/argentina_provincias.geojson` | Construido (24 features, geoBoundaries + Entre Ríos de otra fuente, con fix de typo "La Roja"→"La Rioja") | `geo/argentina_provincias.geojson` |
| `informe_argentina_diagnostico.md` | Entregado al usuario en el chat | Sugerido: copiar también al repo, p.ej. `docs/informe_argentina_diagnostico.md`, para que quede versionado junto con el resto |
| Este `handoff.md` | Este archivo | raíz del repo (`handoff.md`) |

---

## 6. Notas técnicas para quien retome

- **No hay `device_bash` en esta sesión** (ni lo hubo en toda la sesión): todo
  lo que se necesita ejecutar en la PC del usuario (git, scripts) requiere que
  el usuario lo corra él mismo. Los archivos se pueden escribir directamente
  en su carpeta vía el puente de dispositivo (lectura/escritura de archivos),
  pero no hay ejecución de shell remota.
- El script `05_build_argentina.py` sigue la misma convención que
  `01_build_brfss_states.py` (rutas relativas a `ROOT = Path(__file__).resolve().parent.parent`,
  para que funcione corriéndolo como `python src/05_build_argentina.py` desde
  cualquier lugar dentro del repo clonado).
- El dataset y el script **no asumen ni habilitan** un modelo predictivo — el
  docstring del script referencia explícitamente este handoff y advierte que
  LOOCV R²≈0 para el enfoque multivariado, para que no se reuse por error
  como si fuera una base sólida para ese tipo de modelo.

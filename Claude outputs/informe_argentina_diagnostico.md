# Por qué el modelo de EE.UU. no se replica en Argentina — y qué sí se puede hacer con estos datos

## 1. Qué se probó

Se construyó un dataset de las 24 jurisdicciones argentinas (ENFR 2018 + NBI 2010 + pobreza EPH 2018 + cobertura de salud 2022 + densidad 2022), replicando exactamente la metodología usada para los 51 estados de EE.UU.: matriz de correlación, regresión OLS con VIF, Random Forest con validación cruzada, y búsqueda del mejor subconjunto de variables por validación cruzada *leave-one-out* (LOOCV, la más exigente posible dado que solo hay 24 casos).

## 2. Por qué no funciona igual que en EE.UU.

**a) El tamaño de muestra es la limitación de fondo.** EE.UU. aporta 51 unidades; Argentina, 24. No es un problema de calidad de los datos (los coeficientes de variación de la ENFR son todos razonables, entre 5% y 12,5%, sin provincias con estimaciones no confiables) sino de *potencia estadística*: con 24 casos y varias variables, cualquier modelo múltiple encuentra combinaciones que ajustan bien "en la muestra" pero que no generalizan.

**b) Esto se confirma con la validación cruzada.** El modelo completo (obesidad, sedentarismo, tabaquismo, presión, NBI, densidad) da R²=0,39 pero no es significativo (p=0,16). Reducido a 3 variables (obesidad + presión + NBI) sí es significativo (R²=0,34, p=0,037) — pero apenas explica el 1% de la varianza real fuera de muestra (LOOCV R²=0,007), es decir, prácticamente no predice nada en un caso no visto. Se probaron **las 175 combinaciones posibles** de 1, 2 y 3 variables entre las 10 disponibles: la única que predice genuinamente mejor que adivinar el promedio es la más simple de todas, diabetes ~ densidad poblacional (LOOCV R²=0,07, modesto pero real). Agregar más variables no ayuda — empeora.

**c) El Random Forest, que en EE.UU. funcionaba muy bien (R² de validación cruzada = 0,80), acá falla directamente**: R² de validación cruzada negativo (peor que predecir el promedio). Los modelos flexibles necesitan más casos de los que hay a nivel provincial.

**d) Un hallazgo real, aunque modesto: la densidad poblacional.** Es la única variable con relación genuina (aunque débil) con la prevalencia: las provincias más densas/urbanas (CABA a la cabeza, 8,8%) reportan MENOS diabetes que las más dispersas (San Luis, La Rioja, San Juan, todas >15%) — lo contrario de lo esperable si el estilo de vida urbano fuera el problema. Pero al sacar a CABA del análisis, la relación se debilita mucho (R² cae de 0,19 a 0,03, deja de ser significativa) — con lo cual gran parte de esa asociación depende de un solo caso extremo, y no se puede afirmar con solidez.

**e) El NBI sale con signo invertido respecto a EE.UU.** (más pobreza estructural → *menos* diabetes autorreportada). Es más probable que refleje menor acceso a diagnóstico en las provincias más postergadas (subregistro) que un verdadero efecto protector — pero esto es una hipótesis, no algo que el dataset actual permita confirmar.

**En síntesis:** no es que los datos estén mal o falten variables — es que, estadísticamente, 24 provincias no alcanzan para sostener un modelo multivariado como el de 51 estados. Forzarlo sería presentar un resultado frágil como si fuera robusto.

## 3. Ideas para aprovechar estos datos de otra forma

Ya reuniste un dataset genuinamente valioso — con fuentes oficiales, cruzado a nivel de las 24 jurisdicciones. Estas son direcciones donde el enfoque predictivo no es el punto, y por eso el N=24 deja de ser un problema:

**a) Un atlas descriptivo de la diabetes en Argentina (mapas + tablas, sin modelo).** Mostrar cómo varían entre provincias la prevalencia, la obesidad, el sedentarismo, la presión y el colesterol elevados, y sobre todo **la brecha de tratamiento** (Cuadro 7.5): hoy varía entre 32,7% (La Pampa) y 70% (Santa Cruz, Tierra del Fuego) — un rango enorme, sin necesidad de ningún modelo estadístico para que sea un hallazgo contundente y con peso de política pública. (Ya probé si esto se explica por cobertura de salud o pobreza — no hay correlación clara, lo cual en sí mismo es interesante: la brecha de tratamiento no sigue el patrón socioeconómico esperable, y merece explorarse con otras variables o cualitativamente.)

**b) Un paper metodológico sobre escala y N.** Convertir el "fracaso" en el hallazgo central: mostrar explícitamente, con los tres casos (51 estados, 24 provincias, 193 países), cuándo este tipo de modelado (OLS + Random Forest) funciona y cuándo no — una advertencia útil para cualquiera que quiera aplicar la misma receta a otro país o región con pocas unidades. Es un aporte de ciencia de datos, no de epidemiología, y encaja bien en un congreso como CoNaIISI.

**c) Autorreporte vs. medición objetiva.** La ENFR incluye mediciones bioquímicas reales de glucemia (Cuadro 7.9-7.11, aunque solo en localidades de 150.000+ habitantes) que se pueden comparar contra el autorreporte — replicando la misma lógica de "control de calidad" que ya usaste para validar el BRFSS contra la fuente curada de Kaggle. Podría explicar parte de las anomalías (como el signo del NBI) si hay sesgo de subdiagnóstico.

**d) Cruzar con la 5ta ENFR si sale publicada.** Si aparecen resultados nuevos, se podría comparar 2018 vs. la edición más reciente por provincia — evolución temporal en vez de corte transversal, con el intento de agregar poder estadístico juntando ambos años como panel (48 observaciones en vez de 24).

¿Alguna de estas te interesa para retomar? Si querés, puedo armar un mockup rápido de la opción (a) — el atlas descriptivo con mapas — para que veas si el enfoque tiene punch antes de comprometernos a escribir nada.

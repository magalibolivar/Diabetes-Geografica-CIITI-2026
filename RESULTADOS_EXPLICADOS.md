# Resultados explicados — Determinantes geoespaciales de la diabetes

Documento de apoyo para leer los resultados sin ser especialista. Todos los números
salen del código real (`src/03_pipeline.py`) sobre datos reales.

---

## Glosario rápido

- **Prevalencia de diabetes:** porcentaje de adultos que tienen diabetes en una región.
- **R² (R cuadrado):** qué porcentaje de la variación de la prevalencia explica el modelo. 0 = no explica nada; 1 = explica todo. En ciencias sociales, R²>0,4 ya es sólido; **el nuestro es 0,91** (muy alto).
- **R² ajustado:** el R² penalizado por la cantidad de variables. Sirve para comparar modelos (el nuestro: 0,90).
- **Correlación de Pearson (r):** número entre −1 y +1 que mide cuán relacionadas están dos variables. r>0,7 = relación fuerte.
- **β̂ (beta):** coeficiente de la regresión. Cuánto cambia la prevalencia si la variable sube 1 unidad, manteniendo el resto constante.
- **p-valor:** probabilidad de que el resultado sea azar. p<0,05 = "estadísticamente significativo".
- **VIF (factor de inflación de la varianza):** mide multicolinealidad (variables que se pisan entre sí). VIF>10 = problema serio. **Los nuestros están entre 2 y 9** (aceptable).
- **Test F:** prueba si el modelo *en su conjunto* sirve. **F(7,43)=65,3; p<0,001** → el modelo es altamente significativo.
- **HC3:** errores estándar robustos, que siguen siendo válidos aunque haya heterocedasticidad (varianza no constante).
- **Ponderación (peso muestral):** cada encuestado del BRFSS representa a un número distinto de personas; se pondera para que el promedio estatal sea representativo.

---

## Parte A — Estados de EE.UU. (BRFSS 2015, 441.456 encuestados → 51 estados)

**Pregunta:** ¿qué determinantes explican por qué unos estados tienen más diabetes que otros?

- **Prevalencia:** de 6,8% (Colorado) a 14,8% (Misisipi). Promedio ~10,2%.
- **Correlaciones más fuertes con la diabetes:** ingresos bajos (0,81), inactividad física (0,79), secundario incompleto (0,77), obesidad (0,75).
- **La ruralidad casi no correlaciona (0,03).** → No es la ruralidad lo que enferma, sino la pobreza que suele acompañarla.
- **Modelo:** OLS R²=0,91 · Random Forest R²=0,81 (validación cruzada). Muy buen ajuste.
- **Coeficientes significativos (errores robustos HC3):** obesidad (β̂=+0,177), barrera económica al médico (+0,257), inactividad (+0,088), ingresos bajos (+0,111).
- **Multicolinealidad:** VIF entre 2 y 9 (todos < 10). Esto explica por qué "sin cobertura de salud" da un signo negativo raro: es un efecto de supresión estadística, no un efecto real protector.
- **Robustez:** los hallazgos se mantienen al sacar el Distrito de Columbia y al usar un modelo reducido.
- **Clusters (K-Means, k=3):** aparece el "cinturón de la diabetes" del sudeste (alto riesgo, 12,1% promedio) frente a estados de bajo riesgo (8,6%).

**Conclusión A:** a nivel subnacional, la diabetes es un problema de **desigualdad socioeconómica**, no de ruralidad.

---

## Parte B — Países del mundo (193 países, IDF/OWID + World Bank)

**Pregunta:** ¿los mismos determinantes explican las diferencias entre países?

- **Prevalencia más alta:** Pakistán (31,4%), Islas Marshall (25,7%), Kuwait (25,6%). **Más baja:** Zimbabue (1,5%), Ruanda (2,1%).
- **Argentina: 14,0%** (tercio superior mundial).
- **Correlaciones débiles o invertidas** (R²=0,10): rural −0,14, PBI per cápita −0,07, 65+ −0,16.

**Conclusión B — "paradoja de la diabetes":** entre países, la prevalencia la dominan la genética y la velocidad de la transición nutricional (Pacífico, sur de Asia, Golfo), no el nivel de ingreso. **Ojo con la falacia ecológica:** lo que vale entre estados de un país no vale entre países.

---

## Parte C — Carga, evolución y tratamiento

- **Carga absoluta (IDF 2024):** China 148 M, India 90 M, EE.UU. 38,5 M. **Argentina 4,3 M de adultos (puesto #24).**
- **Evolución:** el mundo pasó de 151 M (2000) a 589 M (2024) y se proyectan **852 M para 2050**.
- **Argentina 2011→2024:** de 5,5% a 14,0% (**+8,5 pp**), entre las mayores subas del mundo. *Nota: parte del salto es por cambios metodológicos del IDF entre rondas; se lee como comparación entre estimaciones, no como tendencia pura.*
- **Brecha de tratamiento (NCD-RisC):** la prevalencia mundial se duplicó (7%→14%, 1990-2022) pero solo **~40% recibe tratamiento**. Seis de cada diez personas con diabetes no están tratadas.

**Conclusión C:** el problema no es solo prevenir, también **diagnosticar y tratar**.

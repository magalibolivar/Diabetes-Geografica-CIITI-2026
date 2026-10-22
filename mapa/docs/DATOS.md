# Notas sobre los datos

Hallazgos de revisar la procedencia de los datos antes de construir el sitio. Varios cambian
**qué se puede afirmar** en pantalla.

## 1. La brecha de tratamiento es un dato más frágil de lo que parece

El indicador `diabetes_treatment` sale del **Cuadro 7.5 de la ENFR 2018**: *«Realización de
algún tipo de tratamiento en las últimas dos semanas de la población de 18 años y más con
glucemia elevada/diabetes por autorreporte»*.

- **No es** «recibe tratamiento farmacológico continuo» ni «accede a insulina». Mide *algún
  tipo de tratamiento en las últimas dos semanas* y no distingue cuál. La frase «el 45% no
  accede a tratamiento» (en la propuesta anterior) **no se sostiene con este indicador**.
  Formulación defendible: *«X% de quienes declaran diabetes no hizo ningún tratamiento en las
  últimas dos semanas»*, y llamarlo **brecha de tratamiento**, no «de acceso».
- **8 de las 24 provincias tienen marca de INDEC** en este cuadro, y justo los extremos del
  rango: La Pampa (32,7%) y Santa Cruz y Tierra del Fuego (70,0%) figuran como **«no
  confiable»** (nota 2). El «rango 32,7%–70%» que el `handoff.md` presenta como hallazgo
  fuerte descansa en tres estimaciones que el propio INDEC desaconseja.
- La marca de INDEC **no es solo el CV**: Jujuy tiene CV 13,2% y aun así figura como no
  confiable (casos insuficientes). Por eso el ETL guarda la marca oficial en lugar de aplicar
  un umbral propio.
- Otros cuadros afectados: frutas y verduras (5 «precaución», 14 «no confiable») — evitar
  rankings de ese indicador. Prevalencia, glucemia, obesidad, sedentarismo, tabaco, presión
  y colesterol no traen marcas.

El sitio debe mostrar la marca (rayado/asterisco) y excluir las «no confiables» de rankings
y de titulares.

## 2. Las definiciones secundarias del repo contradicen al cuadro oficial

`Propuesta_Mapa_Interactivo_/Datos/README_DATOS.md` difiere de las planillas oficiales y del
script que genera el CSV (`src/05_build_argentina.py`):

| Dato | README_DATOS (incorrecto) | Cuadro oficial (usado acá) |
|---|---|---|
| Prevalencia | «diabetes tipo 2», Cuadro 7.1 | «glucemia elevada/diabetes» por autorreporte, **Cuadro 7.3** |
| Tratamiento | «farmacológico regular», Cuadro 7.3 | «algún tratamiento, últimas 2 semanas», **Cuadro 7.5** |
| Glucemia | «testeada en los últimos 2 años», 7.2 | «medida **alguna vez** en la vida», **Cuadro 7.1** |
| Obesidad | «medición antropométrica objetiva» | **autorreporte** (Cuadro 6.3) |
| Pobreza | «EPH 2023-2024» | **2º semestre 2018** (promedio simple de aglomerados) |
| CV | «garantiza CV < 15%» | hay CV de hasta 45% (frutas y verduras) |

Las definiciones del catálogo (`api/src/mapa/catalog.py`) salen de los títulos de los cuadros.

## 3. Cobertura: solo población urbana

La ENFR cubre **localidades de 5.000 y más habitantes**. No describe la población rural ni la
de localidades chicas; el sitio debe decirlo.

## 4. Geometría: el GeoJSON heredado estaba mal — reemplazado

`geo/argentina_provincias.geojson` (idéntico al de `Propuesta_Mapa_Interactivo_/Datos`) venía de
geoBoundaries (23 unidades, base 2006) con CABA agregada a mano:

- **CABA** eran 24 vértices en un blob sobre el conurbano oeste, ~4× el tamaño real, que **no
  contenía al Obelisco**.
- **Buenos Aires** llegaba hasta el paralelo −30,15 y **se superponía con Santa Fe y Entre
  Ríos**: Rosario resolvía como «Buenos Aires».
- Posadas y Ushuaia caían fuera de su provincia; Neuquén capital resolvía como Río Negro.
- Entre Ríos no tenía `shapeISO`/`shapeID`: la capa había sido editada a mano.

**Solución:** `mapa/data/geo/argentina_provincias.geojson`, generada desde la capa oficial del
IGN con `mapa geo build` (ver `mapa/data/geo/README.md`). Pasa los controles de calidad
(capitales dentro de su provincia, sin solapes, CABA del tamaño correcto) y `/v1/locate` ya
resuelve bien esos casos.

**Decidido por el equipo:** se muestra todo el territorio oficial de Tierra del Fuego, Antártida e Islas
del Atlántico Sur, aunque no tenga datos: las Malvinas en su lugar y la Antártida con las islas australes
en un recuadro, todo en gris «sin datos» (ver `mapa/data/geo/README.md`).

**No se tocó** el archivo viejo: lo usan el paper y el Motor anterior, cuyos mapas siguen
teniendo el defecto.

## 5. Pendientes de verificar

- **NBI**: el CSV histórico mantiene `nbi_2010_pct` intacto. El mapa carga por separado
  `nbi_2022_hogares.csv`, extraído de los conteos del Cuadro 2 de `serie_nbi_2022.xlsx`
  y cotejado con los porcentajes del Cuadro 3. Son hogares censados en 2022, no la
  población adulta urbana de la ENFR 2018. No se calculan variaciones 2010-2022:
  en el propio libro oficial, el Cuadro 1 presenta 9,1% para 2010, mientras que
  los conteos del Cuadro 2 y el porcentaje del Cuadro 3 dan 9,2% al redondear.
- **«Sin cobertura de salud»**: confirmar qué categorías del Censo 2022 se sumaron (¿entra
  «programas o planes estatales»?) para que la etiqueta no engañe.
- **Densidad de Tierra del Fuego**: ajustada a 8,6 hab/km² (oficial 0,20). Está en las notas
  del indicador; confirmar que el equipo quiere ese criterio también en la web.
- **ENFR 2022**: el handoff dice que no había confirmación de una 5ª edición. Si existe,
  el modelo ya soporta cargarla como un dataset nuevo y armar series de tiempo.

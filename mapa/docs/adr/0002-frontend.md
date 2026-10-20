# ADR 0002 — Frontend: SvelteKit + D3 (SVG), sin librería de mapas

Fecha: 2026-10-20 · Estado: aceptada · Complementa a [0001](0001-arquitectura.md)

## Decisiones

1. **SvelteKit 3 con `adapter-node`** (SSR). El HTML llega renderizado (primera carga rápida, funciona
   sin JS, se puede compartir una URL), y las partes interactivas se hidratan.
2. **Mapa con D3 (`d3-geo`) y SVG, no MapLibre.** Con 24 polígonos y sin teselas de fondo, SVG es más
   liviano, funciona sin red externa y permite animar la transición del mapa al mosaico (cada provincia
   viaja de su centroide a su celda). MapLibre se justificaría con una capa de ~500 departamentos y zoom.
   *Esto corrige lo propuesto en la conversación inicial (MapLibre).*
3. **Territorios sin datos incluidos.** Tierra del Fuego, Antártida e Islas del Atlántico Sur se reparte al
   dibujar: el sector insular austral lleva los datos de la provincia; las Malvinas (en su lugar) y la
   Antártida con las islas australes (recuadro polar) se ven en gris «sin datos» y llevan a la ficha de la
   provincia. La clasificación vive en `src/lib/geometry.ts` y replica la del ETL.
4. **El servidor del sitio proyecta la geometría** (cónica de áreas iguales) y entrega paths SVG listos.
   Hubo que reorientar los anillos: el GeoJSON de PostGIS sigue RFC 7946 (exterior antihorario) y D3
   espera lo contrario; sin eso dibuja «el globo menos la provincia».
5. **Caché en memoria con «stale-while-error», no pre-render.** Se evaluó pre-renderizar para que el sitio
   no dependa de la API, pero en Dokploy el build tendría que alcanzar la API (y su clave). La caché logra
   lo mismo en la práctica: si la API se cae, se sigue sirviendo el último dato bueno (probado en
   `api.test.ts`). Sin dato previo, el sitio responde 503 con un mensaje claro.
6. **La API key vive sólo en el servidor** (`src/env.ts`, `$app/env/private`) y se exige al arrancar,
   no al compilar. El navegador nunca habla con la API: «¿en qué provincia estoy?» pasa por
   `/api/locate`, que consulta la API desde el servidor y no registra las coordenadas.
7. **El estado de la vista vive en la URL** (`?i=indicador&p=provincia&v=mosaico&m=dif&x=…&y=…`): toda
   vista se puede compartir y funciona el botón «atrás».
8. **Todo número que aparece en un texto sale de los datos** (`src/lib/story.ts`, con tests); nada de
   cifras escritas a mano que puedan quedar desactualizadas.
9. **Color:** una rampa azul para magnitud (validada), naranja sólo para selección, rayado para lo que el
   INDEC marca como poco confiable. La paleta categórica (azul/naranja en «Comparar») se validó con el
   script del skill de visualización en claro y oscuro. Modo oscuro con pasos propios.

## Consecuencias

- Los iconos y fuentes se sirven desde el propio dominio (fuentes autoalojadas con Fontsource): ninguna
  petición a terceros, nada que registrar en una política de privacidad.
- `adapter-node` no comprime respuestas: conviene activar compresión en el proxy (Traefik).
- El mosaico de provincias es una disposición a mano (`src/lib/tiles.ts`), aproximada.

# MAPA — sitio web

SvelteKit 3 (Svelte 5, TypeScript) + D3 (`d3-geo`, `d3-delaunay`) + GSAP/Lenis. Decisiones en
[`../docs/adr/0002-frontend.md`](../docs/adr/0002-frontend.md).

## Desarrollo

Necesita la API corriendo (ver `../README.md`) y una clave de sólo lectura:

```bash
cd ../ && docker compose run --rm etl keys create --name web-dev --scope read
cd web && cp .env.example .env      # pegar la clave en MAPA_API_KEY
npm install
npm run dev
```

```bash
npm test            # vitest: estadística, formato, armado del atlas, historia, caché de la API
npm run check       # svelte-check (tipos)
npm run build       # build de producción (adapter-node)
```

## Páginas

| Ruta | Qué es |
|---|---|
| `/` | Historia con scroll: el mapa fijo cambia de dato (y pasa a mosaico) según lo que se lee |
| `/explorar` | Mapa/mosaico + ranking con intervalos + dispersión + tabla. Estado en la URL |
| `/provincia/[slug]` | Ficha: dónde cae la provincia entre las 24 en cada indicador |
| `/comparar?a=&b=` | Dos provincias lado a lado |
| `/metodologia` | Fuentes, confiabilidad, cálculos propios y límites |
| `/api/locate?lat=&lng=` | «¿En qué provincia estoy?» (consulta la API interna desde el servidor) |
| `/healthz` | Healthcheck del contenedor |

## Estructura

```
src/lib/
  compose.ts        # API (crudo) → Atlas; calcula la brecha de tratamiento
  stats.ts          # IC 95% desde el CV, Spearman/Pearson, cortes de la leyenda
  viz.ts            # escalas de color, ítems del mapa
  story.ts          # textos de la portada, con los números calculados de los datos
  tiles.ts          # disposición del mosaico
  server/           # sólo servidor: cliente de la API con caché, proyección del mapa
  components/       # Map, Legend, Ranking, Scatter, Strip, ...
```

## Reglas del proyecto

- **La marca de confiabilidad del INDEC se respeta siempre**: rayado en mapa/mosaico/ranking/puntos
  huecos; las «no confiables» no se usan para titulares ni rankings.
- **Nada de números escritos a mano en los textos**: salen de `story.ts` o de los datos.
- El color no es el único canal: rayado, etiquetas, leyenda siempre presente, tabla alternativa.

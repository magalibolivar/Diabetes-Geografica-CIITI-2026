import { error } from '@sveltejs/kit';
import { geoAzimuthalEqualArea, geoConicEqualArea, geoPath } from 'd3-geo';
import type { FeatureCollection, MultiPolygon } from 'geojson';
import { apiGet, ApiError } from './api';
import { splitTierraDelFuego } from '#lib/geometry';
import { buildAtlas, type RawIndicator, type RawJurisdiction, type RawObservation } from '#lib/compose';
import type { Atlas, MapExtra, MapGeometry } from '#lib/types';

export async function loadAtlas(): Promise<Atlas> {
	try {
		const [indicators, jurisdictions, observations] = await Promise.all([
			apiGet<RawIndicator[]>('/v1/indicators'),
			apiGet<RawJurisdiction[]>('/v1/jurisdictions'),
			apiGet<RawObservation[]>('/v1/observations?limit=20000')
		]);
		return buildAtlas(indicators, jurisdictions, observations);
	} catch (err) {
		console.error('[atlas] no se pudo cargar', err);
		const detail = err instanceof ApiError ? `la API respondió ${err.status}` : 'la API no responde';
		error(503, `Los datos no están disponibles en este momento (${detail}). Probá de nuevo en un rato.`);
	}
}

/**
 * D3 espera el exterior de cada polígono en sentido horario (y los huecos antihorarios); el estándar
 * GeoJSON (RFC 7946) que emite PostGIS es al revés. Sin esto D3 dibuja "todo el globo menos la provincia".
 */
type Ring = number[][];
function isClockwise(ring: Ring): boolean {
	let sum = 0;
	for (let i = 0; i < ring.length - 1; i++) sum += (ring[i + 1][0] - ring[i][0]) * (ring[i + 1][1] + ring[i][1]);
	return sum > 0;
}
export function rewindForD3(polygons: Ring[][]): Ring[][] {
	return polygons.map((rings) =>
		rings.map((ring, i) => (isClockwise(ring) === (i === 0) ? ring : [...ring].reverse()))
	);
}

const W = 600;
const H = 940;
const PAD = 12;
/** Recuadro de Antártida e islas australes: el hueco libre a la derecha de la Patagonia. */
const INSET = { x: 352, y: 690, width: 238, height: 240 };

const TDF = 'tierra-del-fuego';

/**
 * Provincias proyectadas a paths SVG (cónica de áreas iguales, adecuada para Argentina).
 * Tierra del Fuego, Antártida e Islas del Atlántico Sur se reparte: el sector insular austral se dibuja con
 * la provincia (y lleva sus datos), las Malvinas en su lugar sin datos, y la Antártida con las islas
 * australes en un recuadro polar, también sin datos (la encuesta no releva esos territorios).
 */
export async function loadMapGeometry(): Promise<MapGeometry> {
	const raw = await apiGet<FeatureCollection<MultiPolygon, { slug: string }>>('/v1/geo/provinces');

	const features = raw.features.map((f) => ({
		...f,
		geometry: { ...f.geometry, coordinates: rewindForD3(f.geometry.coordinates) }
	}));
	const tdf = features.find((f) => f.properties.slug === TDF);
	if (!tdf) throw new Error('La API no devolvió Tierra del Fuego');
	const parts = splitTierraDelFuego(tdf.geometry.coordinates);

	const mainFc: FeatureCollection<MultiPolygon, { slug: string }> = {
		type: 'FeatureCollection',
		features: features.map((f) =>
			f === tdf ? { ...f, geometry: { type: 'MultiPolygon', coordinates: parts.main } } : f
		)
	};
	const projection = geoConicEqualArea()
		.parallels([-30, -50])
		.rotate([66, 0])
		.fitExtent(
			[
				[PAD, PAD],
				[W - PAD, H - PAD]
			],
			mainFc
		);
	const path = geoPath(projection).digits(1);

	const paths: MapGeometry['paths'] = {};
	const centroids: MapGeometry['centroids'] = {};
	for (const f of mainFc.features) {
		paths[f.properties.slug] = path(f) ?? '';
		centroids[f.properties.slug] = path.centroid(f) as [number, number];
	}

	const extras: MapExtra[] = [];
	if (parts.malvinas.length) {
		const geometry = { type: 'MultiPolygon' as const, coordinates: parts.malvinas };
		const c = path.centroid(geometry) as [number, number];
		extras.push({
			id: 'malvinas',
			label: 'Islas Malvinas',
			aria: 'Islas Malvinas: territorio sin datos en esta encuesta. Forman parte de la provincia de Tierra del Fuego, Antártida e Islas del Atlántico Sur. Ver su ficha.',
			path: path(geometry) ?? '',
			labelAt: [c[0] + 22, c[1] + 4],
			belongsTo: TDF
		});
	}
	if (parts.remote.length) {
		const geometry = { type: 'MultiPolygon' as const, coordinates: parts.remote };
		const polar = geoAzimuthalEqualArea()
			// λ = 50°: el polo queda abajo y el sector argentino (meridiano 50°O) apunta hacia arriba.
			.rotate([50, 90])
			.fitExtent(
				[
					[INSET.x + 10, INSET.y + 10],
					[INSET.x + INSET.width - 10, INSET.y + INSET.height - 34]
				],
				geometry
			);
		const polarPath = geoPath(polar).digits(1);
		extras.push({
			id: 'antartida',
			label: 'Antártida e islas australes',
			aria: 'Antártida Argentina e islas del Atlántico Sur (Georgias, Sandwich y Orcadas del Sur): territorio sin datos en esta encuesta. Forman parte de la provincia de Tierra del Fuego, Antártida e Islas del Atlántico Sur. Ver su ficha.',
			path: polarPath(geometry) ?? '',
			labelAt: [INSET.x + INSET.width / 2, INSET.y + INSET.height - 12],
			frame: INSET,
			belongsTo: TDF
		});
	}

	return { width: W, height: H, paths, centroids, extras };
}

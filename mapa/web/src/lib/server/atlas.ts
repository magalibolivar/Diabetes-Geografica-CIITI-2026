import { error } from '@sveltejs/kit';
import { geoConicEqualArea, geoPath } from 'd3-geo';
import type { FeatureCollection, MultiPolygon } from 'geojson';
import { apiGet, ApiError } from './api';
import { buildAtlas, type RawIndicator, type RawJurisdiction, type RawObservation } from '#lib/compose';
import type { Atlas, MapGeometry } from '#lib/types';

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

/** Provincias proyectadas a paths SVG (proyección cónica de áreas iguales, adecuada para Argentina). */
export async function loadMapGeometry(): Promise<MapGeometry> {
	const raw = await apiGet<FeatureCollection<MultiPolygon, { slug: string }>>('/v1/geo/provinces');
	const fc: typeof raw = {
		...raw,
		features: raw.features.map((f) => ({
			...f,
			geometry: { ...f.geometry, coordinates: rewindForD3(f.geometry.coordinates) }
		}))
	};
	const projection = geoConicEqualArea()
		.parallels([-30, -50])
		.rotate([66, 0])
		.fitExtent(
			[
				[PAD, PAD],
				[W - PAD, H - PAD]
			],
			fc
		);
	const path = geoPath(projection).digits(1);

	const paths: MapGeometry['paths'] = {};
	const centroids: MapGeometry['centroids'] = {};
	for (const f of fc.features) {
		const slug = f.properties.slug;
		paths[slug] = path(f) ?? '';
		centroids[slug] = path.centroid(f) as [number, number];
	}
	return { width: W, height: H, paths, centroids };
}

/**
 * La feature oficial «Tierra del Fuego, Antártida e Islas del Atlántico Sur» reúne territorios muy distintos.
 * Para dibujarla se reparte en tres partes. Los límites replican los del ETL (`geo_build.py`).
 */
export type TdfPart = 'main' | 'malvinas' | 'remote';

type Ring = number[][];

const MAIN_MAX_LON = -62;
const MAIN_MIN_LAT = -56.5;
const MALVINAS = { lon: [-62, -57], lat: [-53.5, -50.5] } as const;

/** Punto representativo: promedio de los vértices del anillo exterior (alcanza para ubicar islas). */
export function ringCenter(ring: Ring): [number, number] {
	let x = 0;
	let y = 0;
	for (const [lon, lat] of ring) {
		x += lon;
		y += lat;
	}
	return [x / ring.length, y / ring.length];
}

export function classifyTdfPart([lon, lat]: [number, number]): TdfPart {
	if (lon < MAIN_MAX_LON && lat > MAIN_MIN_LAT) return 'main';
	if (lon >= MALVINAS.lon[0] && lon <= MALVINAS.lon[1] && lat >= MALVINAS.lat[0] && lat <= MALVINAS.lat[1]) {
		return 'malvinas';
	}
	return 'remote';
}

export function splitTierraDelFuego(polygons: Ring[][]): Record<TdfPart, Ring[][]> {
	const out: Record<TdfPart, Ring[][]> = { main: [], malvinas: [], remote: [] };
	for (const polygon of polygons) out[classifyTdfPart(ringCenter(polygon[0]))].push(polygon);
	return out;
}

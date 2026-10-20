import { MAPA_API_KEY, MAPA_API_URL } from '$app/env/private';

/**
 * Cliente de la API interna de MAPA. Sólo corre en el servidor: la API key nunca llega al navegador.
 *
 * Caché en memoria con "stale-while-error": si la API se cae, se sigue sirviendo el último dato bueno
 * en lugar de romper el sitio público. (Los datos cambian sólo cuando el equipo publica una versión.)
 */

const TTL_MS = 5 * 60 * 1000;
const TIMEOUT_MS = 8000;

export class ApiError extends Error {
	constructor(
		readonly status: number,
		readonly path: string
	) {
		super(`API ${status} en ${path}`);
	}
}

const cache = new Map<string, { at: number; data: unknown }>();
const inflight = new Map<string, Promise<unknown>>();

async function fetchJson(path: string): Promise<unknown> {
	const res = await fetch(MAPA_API_URL + path, {
		headers: { 'X-API-Key': MAPA_API_KEY ?? '', accept: 'application/json' },
		signal: AbortSignal.timeout(TIMEOUT_MS)
	});
	if (!res.ok) throw new ApiError(res.status, path);
	return res.json();
}

export async function apiGet<T>(path: string): Promise<T> {
	const hit = cache.get(path);
	if (hit && Date.now() - hit.at < TTL_MS) return hit.data as T;

	let pending = inflight.get(path);
	if (!pending) {
		pending = fetchJson(path).finally(() => inflight.delete(path));
		inflight.set(path, pending);
	}
	try {
		const data = await pending;
		cache.set(path, { at: Date.now(), data });
		return data as T;
	} catch (err) {
		if (hit) {
			console.warn(`[api] ${path} falló; se sirve el dato en caché (${String(err)})`);
			return hit.data as T;
		}
		throw err;
	}
}

/** Consulta sin caché (para búsquedas puntuales como /v1/locate). */
export async function apiGetFresh<T>(path: string): Promise<T> {
	return (await fetchJson(path)) as T;
}

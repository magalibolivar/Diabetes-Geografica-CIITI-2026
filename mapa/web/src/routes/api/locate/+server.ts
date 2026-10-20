import { error, json } from '@sveltejs/kit';
import { ApiError, apiGetFresh } from '#lib/server/api';
import type { RequestHandler } from './$types';

interface Located {
	jurisdiction: { slug: string; name: string };
}

/**
 * «¿En qué provincia estoy?» — el navegador le pregunta a ESTE servidor, que consulta la API interna.
 * Así la API (y su clave) nunca se exponen. Las coordenadas no se guardan ni se registran.
 */
export const GET: RequestHandler = async ({ url }) => {
	const lat = Number(url.searchParams.get('lat'));
	const lng = Number(url.searchParams.get('lng'));
	if (!Number.isFinite(lat) || !Number.isFinite(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) {
		error(400, 'Coordenadas inválidas.');
	}
	try {
		const found = await apiGetFresh<Located>(`/v1/locate?lat=${lat}&lng=${lng}`);
		return json(
			{ slug: found.jurisdiction.slug, name: found.jurisdiction.name },
			{ headers: { 'Cache-Control': 'no-store' } }
		);
	} catch (err) {
		if (err instanceof ApiError && err.status === 404) {
			return json({ slug: null, name: null }, { status: 404, headers: { 'Cache-Control': 'no-store' } });
		}
		error(502, 'No pudimos ubicarte en este momento.');
	}
};

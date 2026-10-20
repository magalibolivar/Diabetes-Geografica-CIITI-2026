import { building } from '$app/env';
import { MAPA_API_KEY } from '$app/env/private';
import type { Handle, ServerInit } from '@sveltejs/kit/hooks';

/** Al arrancar el servidor (no al compilar): sin clave de la API el sitio no puede mostrar nada. */
export const init: ServerInit = () => {
	if (!building && !MAPA_API_KEY) {
		throw new Error(
			'Falta MAPA_API_KEY. Crearla con `mapa keys create --name web --scope read` (ver web/.env.example).'
		);
	}
};

/** Cabeceras de seguridad básicas. La geolocalización sólo se habilita para este mismo origen. */
export const handle: Handle = async ({ event, resolve }) => {
	const response = await resolve(event, {
		// Los archivos de fuente se precargan para evitar el salto de tipografía.
		preload: ({ type }) => type === 'font' || type === 'js' || type === 'css'
	});
	response.headers.set('X-Content-Type-Options', 'nosniff');
	response.headers.set('X-Frame-Options', 'SAMEORIGIN');
	response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
	response.headers.set('Permissions-Policy', 'geolocation=(self), camera=(), microphone=()');
	return response;
};

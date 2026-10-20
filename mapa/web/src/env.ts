import { defineEnvVars } from '@sveltejs/kit/env';

/** Variables de entorno del servidor. Se validan al arrancar: si falta la clave, no se levanta. */
export const variables = defineEnvVars({
	MAPA_API_URL: {
		description: 'URL base de la API interna de MAPA (sólo la usa este servidor).',
		schema: (value) => (value ?? 'http://127.0.0.1:8000').replace(/\/$/, '')
	},
	MAPA_API_KEY: {
		description: 'API key con alcance `read`. Crearla con `mapa keys create --name web --scope read`.',
		// Es un secreto de ejecución: no hace falta al compilar. Se exige al arrancar (ver hooks.server.ts).
		schema: (value) => value || undefined
	}
});

import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

/** Para el healthcheck del contenedor: responde sin tocar la API. */
export const GET: RequestHandler = () => json({ status: 'ok' });

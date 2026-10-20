import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { apiGet, ApiError } from './api';

const ok = (body: unknown) => new Response(JSON.stringify(body), { status: 200 });

describe('apiGet', () => {
	beforeEach(() => vi.useFakeTimers());
	afterEach(() => {
		vi.useRealTimers();
		vi.unstubAllGlobals();
	});

	it('usa la caché mientras está fresca y no vuelve a pedir', async () => {
		const fetchMock = vi.fn().mockResolvedValue(ok({ v: 1 }));
		vi.stubGlobal('fetch', fetchMock);
		await apiGet('/fresh');
		await apiGet('/fresh');
		expect(fetchMock).toHaveBeenCalledTimes(1);
	});

	it('si la API se cae, sigue sirviendo el último dato bueno', async () => {
		const fetchMock = vi.fn().mockResolvedValueOnce(ok({ v: 'bueno' }));
		vi.stubGlobal('fetch', fetchMock);
		expect(await apiGet('/stale')).toEqual({ v: 'bueno' });

		vi.advanceTimersByTime(10 * 60 * 1000); // vence la caché
		fetchMock.mockRejectedValue(new Error('ECONNREFUSED'));
		vi.spyOn(console, 'warn').mockImplementation(() => {});
		expect(await apiGet('/stale')).toEqual({ v: 'bueno' });
	});

	it('sin dato previo, un error de la API se propaga', async () => {
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('no', { status: 500 })));
		await expect(apiGet('/never')).rejects.toBeInstanceOf(ApiError);
	});

	it('pedidos simultáneos comparten una sola consulta', async () => {
		const fetchMock = vi.fn().mockResolvedValue(ok([1, 2]));
		vi.stubGlobal('fetch', fetchMock);
		await Promise.all([apiGet('/dedupe'), apiGet('/dedupe'), apiGet('/dedupe')]);
		expect(fetchMock).toHaveBeenCalledTimes(1);
	});

	it('manda la API key en el header', async () => {
		const fetchMock = vi.fn().mockResolvedValue(ok({}));
		vi.stubGlobal('fetch', fetchMock);
		await apiGet('/headers');
		expect(fetchMock.mock.calls[0][1].headers).toHaveProperty('X-API-Key');
	});
});

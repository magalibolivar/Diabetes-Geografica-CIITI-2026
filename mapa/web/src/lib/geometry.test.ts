import { describe, expect, it } from 'vitest';
import { classifyTdfPart, ringCenter, splitTierraDelFuego } from './geometry';

describe('classifyTdfPart', () => {
	it('Isla Grande y de los Estados son el sector principal', () => {
		expect(classifyTdfPart([-68.3, -54.0])).toBe('main'); // Isla Grande
		expect(classifyTdfPart([-64.5, -54.8])).toBe('main'); // Isla de los Estados
	});
	it('las Malvinas están al este de Santa Cruz', () => {
		expect(classifyTdfPart([-59.0, -51.7])).toBe('malvinas'); // Soledad
		expect(classifyTdfPart([-60.2, -51.6])).toBe('malvinas'); // Gran Malvina
	});
	it('Antártida e islas australes van al recuadro', () => {
		expect(classifyTdfPart([-60, -75])).toBe('remote'); // Antártida
		expect(classifyTdfPart([-36.5, -54.3])).toBe('remote'); // Georgias del Sur
		expect(classifyTdfPart([-26.5, -58])).toBe('remote'); // Sandwich del Sur
		expect(classifyTdfPart([-45.5, -60.6])).toBe('remote'); // Orcadas del Sur
	});
});

describe('splitTierraDelFuego', () => {
	const square = (lon: number, lat: number) => [
		[
			[lon, lat],
			[lon + 1, lat],
			[lon + 1, lat + 1],
			[lon, lat + 1],
			[lon, lat]
		]
	];
	it('reparte los polígonos sin perder ninguno', () => {
		const parts = splitTierraDelFuego([square(-68, -54), square(-59, -52), square(-60, -80), square(-37, -55)]);
		expect(parts.main).toHaveLength(1);
		expect(parts.malvinas).toHaveLength(1);
		expect(parts.remote).toHaveLength(2);
	});
	it('el centro del anillo es el promedio de sus vértices', () => {
		expect(ringCenter([[0, 0], [2, 0], [2, 2], [0, 2]])).toEqual([1, 1]);
	});
});

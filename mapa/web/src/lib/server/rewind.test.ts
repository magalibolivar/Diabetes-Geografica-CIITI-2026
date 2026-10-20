import { describe, expect, it } from 'vitest';
import { rewindForD3 } from './atlas';

// Cuadrado antihorario (RFC 7946) con un hueco horario.
const ccwSquare = [
	[0, 0],
	[10, 0],
	[10, 10],
	[0, 10],
	[0, 0]
];
const cwHole = [
	[3, 3],
	[3, 6],
	[6, 6],
	[6, 3],
	[3, 3]
];

function clockwise(ring: number[][]): boolean {
	let sum = 0;
	for (let i = 0; i < ring.length - 1; i++) sum += (ring[i + 1][0] - ring[i][0]) * (ring[i + 1][1] + ring[i][1]);
	return sum > 0;
}

describe('rewindForD3', () => {
	it('deja el exterior en sentido horario y los huecos en antihorario', () => {
		const [[outer, hole]] = rewindForD3([[ccwSquare, cwHole]]);
		expect(clockwise(outer)).toBe(true);
		expect(clockwise(hole)).toBe(false);
	});
	it('no toca lo que ya está bien orientado', () => {
		const good = [...ccwSquare].reverse();
		const [[outer]] = rewindForD3([[good]]);
		expect(outer).toEqual(good);
	});
});

import { describe, expect, it } from 'vitest';
import { binIndex, ci95, describeCorrelation, niceBins, pearson, ranks, spearman } from './stats';

describe('ci95', () => {
	it('deriva el intervalo del CV publicado', () => {
		// La Pampa, tratamiento: 32,7% con CV 17,7% -> SE = 5,79 -> ±11,3
		const ci = ci95(32.7, 17.7)!;
		expect(ci.low).toBeCloseTo(21.35, 1);
		expect(ci.high).toBeCloseTo(44.05, 1);
	});
	it('sin CV no hay intervalo', () => expect(ci95(10, null)).toBeNull());
	it('se acota a [0, max]', () => {
		expect(ci95(2, 60)!.low).toBe(0);
		expect(ci95(95, 20, 100)!.high).toBe(100);
	});
});

describe('correlación', () => {
	it('pearson de una recta perfecta es 1 y de una inversa −1', () => {
		expect(pearson([1, 2, 3, 4], [2, 4, 6, 8])).toBeCloseTo(1);
		expect(pearson([1, 2, 3, 4], [8, 6, 4, 2])).toBeCloseTo(-1);
	});
	it('con varianza cero o pocos datos devuelve null', () => {
		expect(pearson([1, 1, 1], [1, 2, 3])).toBeNull();
		expect(pearson([1, 2], [1, 2])).toBeNull();
	});
	it('ranks promedia empates', () => expect(ranks([10, 30, 30, 20])).toEqual([4, 1.5, 1.5, 3]));
	it('spearman ignora el efecto de un valor extremo', () => {
		const xs = [1, 2, 3, 4, 1000];
		const ys = [1, 2, 3, 4, 5];
		expect(spearman(xs, ys)).toBeCloseTo(1);
		expect(pearson(xs, ys)!).toBeLessThan(1);
	});
});

describe('niceBins', () => {
	it('cubre el rango con bordes redondos', () => {
		const b = niceBins(8.8, 17.3, 6);
		expect(b.edges[0]).toBeLessThanOrEqual(8.8);
		expect(b.edges.at(-1)!).toBeGreaterThanOrEqual(17.3);
		expect(b.edges.every((e) => Math.abs(e * 2 - Math.round(e * 2)) < 1e-9)).toBe(true);
	});
	it('binIndex ubica extremos dentro del rango', () => {
		const b = niceBins(0, 100, 5);
		expect(binIndex(b, 0)).toBe(0);
		expect(binIndex(b, 100)).toBe(b.count - 1);
		expect(binIndex(b, 49.9)).toBe(2);
	});
	it('rango degenerado', () => expect(niceBins(5, 5, 6).count).toBe(1));
});

describe('describeCorrelation', () => {
	it('devuelve una frase que funciona después de "hay"', () => {
		expect(`hay ${describeCorrelation(0.1)}`).toBe('hay casi ninguna relación');
		expect(`hay ${describeCorrelation(-0.5)}`).toBe('hay una relación moderada');
		expect(`hay ${describeCorrelation(-0.8)}`).toBe('hay una relación fuerte');
	});
});

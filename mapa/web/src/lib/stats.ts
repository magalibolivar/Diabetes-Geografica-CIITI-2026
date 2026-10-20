/** Estadística descriptiva del sitio. Todo lo que aparece en pantalla como "dato derivado" sale de acá. */

export interface Interval {
	low: number;
	high: number;
}

/**
 * Intervalo de confianza aproximado del 95% a partir del CV publicado.
 * CV = error estándar / estimación, así que SE = valor × CV/100 y el IC es valor ± 1,96·SE.
 * Es una aproximación normal: se acota al rango válido [0, max].
 */
export function ci95(value: number, cv: number | null, max = Infinity): Interval | null {
	if (cv == null) return null;
	const se = (value * cv) / 100;
	return { low: Math.max(0, value - 1.96 * se), high: Math.min(max, value + 1.96 * se) };
}

export function extent(values: number[]): [number, number] {
	return [Math.min(...values), Math.max(...values)];
}

export function mean(values: number[]): number {
	return values.reduce((a, b) => a + b, 0) / values.length;
}

/** Posiciones 1..n (1 = valor más alto); los empates comparten el promedio de sus posiciones. */
export function ranks(values: number[]): number[] {
	const order = values.map((v, i) => [v, i] as const).sort((a, b) => b[0] - a[0]);
	const out = new Array<number>(values.length);
	let i = 0;
	while (i < order.length) {
		let j = i;
		while (j + 1 < order.length && order[j + 1][0] === order[i][0]) j++;
		const avg = (i + j) / 2 + 1;
		for (let k = i; k <= j; k++) out[order[k][1]] = avg;
		i = j + 1;
	}
	return out;
}

export function pearson(xs: number[], ys: number[]): number | null {
	const n = xs.length;
	if (n < 3 || n !== ys.length) return null;
	const mx = mean(xs);
	const my = mean(ys);
	let sxy = 0;
	let sxx = 0;
	let syy = 0;
	for (let i = 0; i < n; i++) {
		const dx = xs[i] - mx;
		const dy = ys[i] - my;
		sxy += dx * dy;
		sxx += dx * dx;
		syy += dy * dy;
	}
	if (sxx === 0 || syy === 0) return null;
	return sxy / Math.sqrt(sxx * syy);
}

/** Correlación de Spearman: robusta a valores extremos (con 24 provincias, CABA pesa mucho en Pearson). */
export function spearman(xs: number[], ys: number[]): number | null {
	return pearson(ranks(xs), ranks(ys));
}

/** Cómo contar la fuerza de una correlación sin exagerar. */
export function describeCorrelation(r: number): string {
	const a = Math.abs(r);
	if (a < 0.2) return 'casi ninguna relación';
	if (a < 0.4) return 'una relación débil';
	if (a < 0.6) return 'una relación moderada';
	return 'una relación fuerte';
}

export interface Bins {
	/** Bordes: bins.length + 1 valores. */
	edges: number[];
	count: number;
}

/** Pasos "lindos" (1, 2, 2.5, 5 × 10^k) para que los cortes de la leyenda sean legibles. */
export function niceStep(raw: number): number {
	const exp = Math.floor(Math.log10(raw));
	const f = raw / 10 ** exp;
	const nice = f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10;
	return nice * 10 ** exp;
}

/** Cortes de igual intervalo con bordes redondeados. Igual intervalo (no cuantiles) = honesto con los valores. */
export function niceBins(min: number, max: number, count: number): Bins {
	if (max === min) return { edges: [min, max], count: 1 };
	const step = niceStep((max - min) / count);
	const start = Math.floor(min / step) * step;
	const edges: number[] = [];
	for (let e = start; e < max + step * 0.999; e += step) edges.push(round(e));
	return { edges, count: edges.length - 1 };
}

export function binIndex(bins: Bins, value: number): number {
	for (let i = 0; i < bins.count; i++) if (value < bins.edges[i + 1]) return i;
	return bins.count - 1;
}

function round(x: number): number {
	return Math.round(x * 1e6) / 1e6;
}

/** Marcas de eje en pasos "lindos" que cubren [min, max]. */
export function ticks(min: number, max: number, count = 5): number[] {
	if (max === min) return [min];
	const step = niceStep((max - min) / count);
	const out: number[] = [];
	for (let t = Math.ceil(min / step) * step; t <= max + step * 1e-9; t += step) out.push(round(t));
	return out;
}

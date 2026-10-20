import { num, signed } from './format';
import { binIndex, mean, niceBins, niceStep } from './stats';
import type { Atlas, Indicator, MapItem, Reliability, Value } from './types';

export type Measure = 'value' | 'delta';

export interface Swatch {
	/** Valor CSS (variable de tema): así el modo oscuro cambia sin recalcular nada. */
	fill: string;
	/** Tinta legible sobre ese relleno. */
	ink: string;
	label: string;
}

export interface Scale {
	measure: Measure;
	swatches: Swatch[];
	/** Valor de referencia de la medida "diferencia" (total del país o promedio de provincias). */
	reference: { value: number; label: string; isCountry: boolean } | null;
	swatchOf(value: number): Swatch;
}

const SEQ = [1, 2, 3, 4, 5, 6];

/** Indicadores con distribución muy sesgada: cortes a mano (cada corte ~ el doble o más que el anterior). */
const CUSTOM_EDGES: Record<string, number[]> = {
	population_density: [0, 5, 10, 20, 50, 100, Infinity]
};

/** Elige índices parejos de la rampa cuando hay menos cortes que pasos disponibles. */
function spread(count: number, steps: number[]): number[] {
	if (count === 1) return [steps[Math.floor(steps.length / 2)]];
	return Array.from({ length: count }, (_, i) => steps[Math.round((i * (steps.length - 1)) / (count - 1))]);
}

export function provinceValues(atlas: Atlas, slug: string): { slug: string; v: Value }[] {
	const all = atlas.values[slug] ?? {};
	return atlas.provinces.flatMap((p) => (all[p.slug] ? [{ slug: p.slug, v: all[p.slug] }] : []));
}

export function referenceFor(atlas: Atlas, indicator: Indicator): NonNullable<Scale['reference']> {
	const country = atlas.values[indicator.slug]?.[atlas.country.slug];
	if (country) return { value: country.value, label: 'Total del país', isCountry: true };
	const vs = provinceValues(atlas, indicator.slug).map((x) => x.v.value);
	return { value: mean(vs), label: 'Promedio simple de las provincias', isCountry: false };
}

function decimalsFor(edges: number[]): number {
	return edges.every((e) => Math.abs(e - Math.round(e)) < 1e-9) ? 0 : 1;
}

export function buildScale(atlas: Atlas, indicator: Indicator, measure: Measure): Scale {
	const rows = provinceValues(atlas, indicator.slug);
	const values = rows.map((r) => r.v.value);
	const unit = indicator.unit === '%' ? '%' : '';

	if (measure === 'delta') {
		const ref = referenceFor(atlas, indicator);
		const maxAbs = Math.max(...values.map((v) => Math.abs(v - ref.value)), 0.1);
		const s = niceStep(maxAbs / 3.5);
		const dec = s >= 1 && Number.isInteger(s) ? 0 : 1;
		const cuts = [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5].map((k) => k * s);
		const labels = [
			`menos de ${signed(cuts[0], dec)}`,
			`${signed(cuts[0], dec)} a ${signed(cuts[1], dec)}`,
			`${signed(cuts[1], dec)} a ${signed(cuts[2], dec)}`,
			'parecido al país',
			`${signed(cuts[3], dec)} a ${signed(cuts[4], dec)}`,
			`${signed(cuts[4], dec)} a ${signed(cuts[5], dec)}`,
			`más de ${signed(cuts[5], dec)}`
		].map((l, i) => (i === 3 && !ref.isCountry ? 'parecido al promedio' : l));
		const swatches: Swatch[] = labels.map((label, i) => ({
			fill: `var(--div-${i + 1})`,
			ink: `var(--on-div-${i + 1})`,
			label: label + (unit && i !== 3 ? ' pp' : '')
		}));
		return {
			measure,
			swatches,
			reference: ref,
			swatchOf(v) {
				const d = v - ref.value;
				const i = cuts.findIndex((c) => d < c);
				return swatches[i === -1 ? 6 : i];
			}
		};
	}

	const custom = CUSTOM_EDGES[indicator.slug];
	if (custom) {
		const n = custom.length - 1;
		const swatches: Swatch[] = spread(n, SEQ).map((step, i) => ({
			fill: `var(--seq-${step})`,
			ink: `var(--on-seq-${step})`,
			label:
				i === 0
					? `menos de ${num(custom[1], 0)}`
					: i === n - 1
						? `más de ${num(custom[n - 1], 0)}`
						: `${num(custom[i], 0)} – ${num(custom[i + 1], 0)}`
		}));
		return {
			measure,
			swatches,
			reference: null,
			swatchOf: (x) => swatches[Math.max(0, custom.findIndex((c, i) => i > 0 && x < c) - 1) % n]
		};
	}

	const lo = Math.min(...values);
	const hi = Math.max(...values);
	let bins = niceBins(lo, hi, 6);
	for (let k = 5; bins.count > 6 && k >= 3; k--) bins = niceBins(lo, hi, k);
	const dec = decimalsFor(bins.edges);
	const steps = spread(bins.count, SEQ);
	const swatches: Swatch[] = steps.map((step, i) => ({
		fill: `var(--seq-${step})`,
		ink: `var(--on-seq-${step})`,
		label: `${num(bins.edges[i], dec)} – ${num(bins.edges[i + 1], dec)}`
	}));
	return {
		measure,
		swatches,
		reference: null,
		swatchOf: (v) => swatches[binIndex(bins, v)]
	};
}

export const NODATA: Swatch = { fill: 'var(--nodata)', ink: 'var(--ink-2)', label: 'Sin dato' };

export const RELIABILITY_TEXT: Record<Exclude<Reliability, null>, { short: string; long: string }> = {
	ok: { short: '', long: '' },
	caution: {
		short: 'Con precaución',
		long: 'El INDEC pide tomar esta estimación con precaución: su margen de error es considerable (CV entre 16,6% y 33,3%).'
	},
	unreliable: {
		short: 'Poco confiable',
		long: 'El INDEC marca esta estimación como no confiable: margen de error muy alto o muy pocos casos. Se muestra, pero no conviene sacar conclusiones de ella.'
	}
};

export const CATEGORY_LABEL: Record<Indicator['category'], string> = {
	outcome: 'Resultado',
	care: 'Atención',
	risk_factor: 'Factores de riesgo',
	context: 'Contexto socioeconómico'
};

export function describe(atlas: Atlas, indicator: Indicator, slug: string): string {
	const v = atlas.values[indicator.slug]?.[slug];
	const name = atlas.provinces.find((p) => p.slug === slug)?.name ?? slug;
	if (!v) return `${name}: sin dato`;
	const base = `${name}: ${num(v.value, indicator.decimals)}${indicator.unit === '%' ? '%' : ' ' + indicator.unit}`;
	const note = v.reliability && v.reliability !== 'ok' ? `. ${RELIABILITY_TEXT[v.reliability].short}` : '';
	return base + note;
}

/** Una entrada de mapa por provincia, con su color ya decidido por la escala. */
export function mapItems(atlas: Atlas, indicator: Indicator, scale: Scale): MapItem[] {
	return atlas.provinces.map((p) => {
		const v = atlas.values[indicator.slug]?.[p.slug];
		const swatch = v ? scale.swatchOf(v.value) : NODATA;
		const shown = v
			? scale.measure === 'delta' && scale.reference
				? signed(v.value - scale.reference.value, indicator.decimals)
				: num(v.value, indicator.unit === '%' ? (v.value >= 100 ? 0 : indicator.decimals) : 0)
			: '–';
		return {
			slug: p.slug,
			name: p.name,
			fill: swatch.fill,
			ink: swatch.ink,
			label: shown,
			reliability: v?.reliability ?? null,
			aria: describe(atlas, indicator, p.slug)
		};
	});
}

/** Posición (1 = más alto) de una provincia en un indicador, y cuántas hay. */
export function rankOf(atlas: Atlas, indicator: string, slug: string): { rank: number; of: number } | null {
	const rows = provinceValues(atlas, indicator);
	const mine = rows.find((r) => r.slug === slug);
	if (!mine) return null;
	const higher = rows.filter((r) => r.v.value > mine.v.value).length;
	return { rank: higher + 1, of: rows.length };
}

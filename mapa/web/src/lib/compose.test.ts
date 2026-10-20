import { describe, expect, it } from 'vitest';
import { buildAtlas, type RawIndicator, type RawJurisdiction, type RawObservation } from './compose';
import { ci95 } from './stats';

const lineage = [
	{
		dataset: 'enfr-2018',
		dataset_name: 'ENFR 2018',
		source_name: 'ENFR',
		publisher: 'INDEC',
		source_url: null,
		reference_period: '2018',
		universe: null,
		source_ref: 'Cuadro 7.5',
		note: null,
		dataset_notes: null
	}
];
const indicator = (slug: string): RawIndicator => ({
	slug,
	label: slug,
	description: '',
	unit: '%',
	decimals: 1,
	higher_is: 'better',
	category: 'care',
	lineage
});
const jur = (slug: string, kind: 'country' | 'province'): RawJurisdiction => ({
	slug,
	iso_code: slug,
	name: slug,
	short_name: slug,
	kind,
	region: null
});
const obs = (jurisdiction: string, value: number, cv: number, reliability = 'ok'): RawObservation => ({
	jurisdiction,
	indicator: 'diabetes_treatment',
	period: '2018',
	value,
	cv,
	reliability: reliability as RawObservation['reliability'],
	dataset: 'enfr-2018'
});

const atlas = buildAtlas(
	[indicator('diabetes_treatment'), indicator('obesity')],
	[jur('argentina', 'country'), jur('la-pampa', 'province'), jur('chubut', 'province')],
	[obs('argentina', 52.6, 2.6), obs('la-pampa', 32.7, 17.7, 'unreliable'), obs('chubut', 38.3, 17.2, 'caution')]
);

describe('buildAtlas', () => {
	it('separa el total del país de las provincias', () => {
		expect(atlas.country.slug).toBe('argentina');
		expect(atlas.provinces.map((p) => p.slug)).toEqual(['chubut', 'la-pampa']);
	});

	it('agrega la brecha de tratamiento como indicador derivado, con su fórmula', () => {
		const gap = atlas.indicators.find((i) => i.slug === 'treatment_gap')!;
		expect(gap.derived).toEqual({ formula: '100 − tratamiento', from: 'diabetes_treatment' });
		expect(gap.higherIs).toBe('worse');
	});

	it('la brecha es 100 − tratamiento y hereda la marca de confiabilidad', () => {
		const g = atlas.values.treatment_gap['la-pampa'];
		expect(g.value).toBeCloseTo(67.3);
		expect(g.reliability).toBe('unreliable');
	});

	it('la brecha conserva el mismo error estándar absoluto que el tratamiento', () => {
		const t = atlas.values.diabetes_treatment['la-pampa'];
		const g = atlas.values.treatment_gap['la-pampa'];
		const seT = (t.value * t.cv!) / 100;
		const seG = (g.value * g.cv!) / 100;
		expect(seG).toBeCloseTo(seT, 1);
		// El ancho del intervalo es idéntico: es el mismo dato visto desde el otro lado.
		const ciT = ci95(t.value, t.cv)!;
		const ciG = ci95(g.value, g.cv)!;
		expect(ciG.high - ciG.low).toBeCloseTo(ciT.high - ciT.low, 0);
	});

	it('ordena los indicadores de resultado a contexto y pone la brecha junto al tratamiento', () => {
		const slugs = atlas.indicators.map((i) => i.slug);
		expect(slugs.indexOf('treatment_gap')).toBeLessThan(slugs.indexOf('diabetes_treatment'));
		expect(slugs.indexOf('diabetes_treatment')).toBeLessThan(slugs.indexOf('obesity'));
	});
});

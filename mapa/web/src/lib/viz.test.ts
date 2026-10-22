import { describe, expect, it } from 'vitest';
import type { Atlas, Indicator, Value } from './types';
import { buildScale, rankOf, referenceFor } from './viz';

const indicator: Indicator = {
	slug: 'nbi_households', label: 'Hogares con al menos una NBI', description: '',
	unit: '%', decimals: 1, higherIs: 'worse', category: 'context', lineage: []
};
const v = (value: number, reliability: Value['reliability'] = null): Value => ({
	value, reliability, cv: null, period: '2022', dataset: 'indec-nbi-2022'
});
const provinces = Array.from({ length: 6 }, (_, i) => ({
	slug: `p${i + 1}`, iso: `AR-${i + 1}`, name: `Provincia ${i + 1}`,
	shortName: `P${i + 1}`, region: null
}));
const atlas: Atlas = {
	indicators: [indicator], provinces,
	country: { slug: 'argentina', iso: 'AR', name: 'Argentina', shortName: 'Total', region: null },
	values: { nbi_households: {
		argentina: v(6.7),
		...Object.fromEntries(provinces.map((p, i) => [p.slug, v(i + 1, i === 5 ? 'unreliable' : null)]))
	} }
};

describe('lectura del mapa y del puesto', () => {
	it('asigna el primer color a porcentajes bajos y el último a los altos', () => {
		const scale = buildScale(atlas, indicator, 'value');
		expect(scale.swatchOf(1).fill).toBe('var(--seq-1)');
		expect(scale.swatchOf(6).fill).toBe('var(--seq-6)');
	});

	it('usa el total nacional publicado; el puesto cuenta las provincias con dato, incluso marcadas', () => {
		expect(referenceFor(atlas, indicator)).toEqual({ value: 6.7, label: 'Total del país', isCountry: true });
		expect(rankOf(atlas, indicator.slug, 'p1')).toEqual({ rank: 6, of: 6 });
		expect(rankOf(atlas, indicator.slug, 'p6')).toEqual({ rank: 1, of: 6 });
	});

	it('si no existe total nacional, usa el promedio simple provincial', () => {
		const withoutCountry: Atlas = { ...atlas, values: { nbi_households: { ...atlas.values.nbi_households } } };
		delete withoutCountry.values.nbi_households.argentina;
		expect(referenceFor(withoutCountry, indicator)).toEqual({ value: 3.5, label: 'Promedio simple de las provincias', isCountry: false });
	});
});

import { describe, expect, it } from 'vitest';
import { buildAtlas, type RawIndicator, type RawJurisdiction, type RawObservation } from './compose';
import { buildStory, shakyAtExtremes } from './story';

const ind = (slug: string): RawIndicator => ({
	slug,
	label: slug,
	description: '',
	unit: '%',
	decimals: 1,
	higher_is: 'worse',
	category: 'outcome',
	lineage: []
});
const jur = (slug: string, kind: 'country' | 'province', short = slug): RawJurisdiction => ({
	slug,
	iso_code: slug,
	name: short,
	short_name: short,
	kind,
	region: null
});
const o = (j: string, i: string, value: number, reliability: RawObservation['reliability'] = 'ok'): RawObservation => ({
	jurisdiction: j,
	indicator: i,
	period: '2018',
	value,
	cv: null,
	reliability,
	dataset: 'x'
});

const provs = ['a', 'b', 'c', 'd', 'e', 'f', 'g'];
const atlas = buildAtlas(
	[ind('diabetes_prevalence'), ind('diabetes_treatment'), ind('glucose_screening'), ind('nbi_households')],
	[jur('argentina', 'country'), ...provs.map((p) => jur(p, 'province', p.toUpperCase()))],
	[
		o('argentina', 'diabetes_prevalence', 12.7),
		o('argentina', 'diabetes_treatment', 52.6),
		o('argentina', 'glucose_screening', 79.1),
		...provs.flatMap((p, i) => [
			o(p, 'diabetes_prevalence', 9 + i),
			// "a" y "g" quedan en los extremos de la brecha y son poco confiables
			o(p, 'diabetes_treatment', 30 + i * 6, p === 'a' || p === 'g' ? 'unreliable' : 'ok'),
			o(p, 'glucose_screening', 70 + i),
			o(p, 'nbi_households', 20 - i * 2)
		])
	]
);

describe('buildStory', () => {
	const steps = buildStory(atlas);

	it('arma los pasos en orden y termina en el mosaico', () => {
		expect(steps.map((s) => s.id)).toEqual(['prevalencia', 'tratamiento', 'control', 'contexto', 'mosaico']);
		expect(steps.at(-1)!.mode).toBe('tiles');
	});

	it('los números del texto salen de los datos', () => {
		const p = steps[0];
		expect(p.title).toContain('12,7%');
		expect(p.paragraphs[0 + 1]).toContain('9,0% en A');
		expect(p.paragraphs[0 + 1]).toContain('15,0% en G');
	});

	it('la brecha usa 100 − tratamiento y avisa cuántos extremos son poco confiables', () => {
		const t = steps[1];
		expect(t.title).toContain('47,4%'); // 100 − 52,6
		expect(t.paragraphs[1]).toContain('2'); // a y g
		expect(t.indicator).toBe('treatment_gap');
	});

	it('describe el signo de la correlación sin inventarlo', () => {
		const c = steps[3];
		expect(c.paragraphs[0]).toContain('ρ = −1,00'); // NBI baja exactamente cuando sube la prevalencia
		expect(c.paragraphs[0]).toContain('una relación fuerte');
		expect(c.paragraphs[0]).toContain('no pueden confirmar'); // la hipótesis se presenta como tal
	});

	it('si falta un indicador, omite el paso en vez de romper', () => {
		const sparse = buildAtlas([ind('diabetes_prevalence')], [jur('argentina', 'country'), jur('a', 'province')], [
			o('argentina', 'diabetes_prevalence', 12.7),
			o('a', 'diabetes_prevalence', 10)
		]);
		expect(buildStory(sparse).map((s) => s.id)).toEqual(['prevalencia', 'mosaico']);
	});
});

describe('shakyAtExtremes', () => {
	it('cuenta sólo los extremos', () => {
		const list = [1, 2, 3, 4, 5, 6, 7, 8].map((v) => ({ slug: `${v}`, name: `${v}`, value: 9 - v, unreliable: v === 1 || v === 4 }));
		expect(shakyAtExtremes(list)).toEqual({ shaky: 1, total: 6 }); // el 4 queda en el medio
	});
});

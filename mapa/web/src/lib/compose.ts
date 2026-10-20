import type { Atlas, Category, Indicator, Province, Reliability, Value } from '#lib/types';

export interface RawLineage {
	dataset: string;
	dataset_name: string;
	source_name: string;
	publisher: string;
	source_url: string | null;
	reference_period: string;
	universe: string | null;
	source_ref: string;
	note: string | null;
	dataset_notes: string | null;
}
export interface RawIndicator {
	slug: string;
	label: string;
	description: string;
	unit: string;
	decimals: number;
	higher_is: Indicator['higherIs'];
	category: Category;
	lineage: RawLineage[];
}
export interface RawJurisdiction {
	slug: string;
	iso_code: string;
	name: string;
	short_name: string;
	kind: 'country' | 'province';
	region: string | null;
}
export interface RawObservation {
	jurisdiction: string;
	indicator: string;
	period: string;
	value: number;
	cv: number | null;
	reliability: Reliability;
	dataset: string;
}

/** Orden de presentación: de lo que pasa (resultado) a lo que lo rodea. */
const ORDER = [
	'diabetes_prevalence',
	'treatment_gap',
	'diabetes_treatment',
	'glucose_screening',
	'obesity',
	'low_physical_activity',
	'smoking',
	'high_blood_pressure',
	'high_cholesterol',
	'fruit_veg_5plus',
	'nbi_households',
	'poverty_persons',
	'no_health_coverage',
	'population_density'
];

function toIndicator(r: RawIndicator): Indicator {
	return {
		slug: r.slug,
		label: r.label,
		description: r.description,
		unit: r.unit,
		decimals: r.decimals,
		higherIs: r.higher_is,
		category: r.category,
		lineage: r.lineage.map((l) => ({
			dataset: l.dataset,
			datasetName: l.dataset_name,
			sourceName: l.source_name,
			publisher: l.publisher,
			sourceUrl: l.source_url,
			referencePeriod: l.reference_period,
			universe: l.universe,
			sourceRef: l.source_ref,
			note: l.note,
			datasetNotes: l.dataset_notes
		}))
	};
}

function toProvince(r: RawJurisdiction): Province {
	return { slug: r.slug, iso: r.iso_code, name: r.name, shortName: r.short_name, region: r.region };
}

/**
 * Brecha de tratamiento = 100 − tratamiento. Es el mismo dato visto desde el otro lado: por eso conserva
 * el error estándar absoluto (SE = v·CV/100) y la marca de confiabilidad de la fuente.
 */
function deriveTreatmentGap(treatment: Indicator, values: Record<string, Value>) {
	const indicator: Indicator = {
		...treatment,
		slug: 'treatment_gap',
		label: 'Brecha de tratamiento',
		description:
			'Entre quienes declaran glucemia elevada o diabetes, porcentaje que no realizó ningún ' +
			'tratamiento en las últimas dos semanas. Es el complemento del indicador de tratamiento.',
		higherIs: 'worse',
		derived: { formula: '100 − tratamiento', from: treatment.slug }
	};
	const out: Record<string, Value> = {};
	for (const [slug, v] of Object.entries(values)) {
		const gap = 100 - v.value;
		out[slug] = {
			...v,
			value: round(gap),
			cv: v.cv == null || gap <= 0 ? null : round((v.value * v.cv) / gap)
		};
	}
	return { indicator, values: out };
}

const round = (x: number) => Math.round(x * 100) / 100;

export function buildAtlas(
	rawIndicators: RawIndicator[],
	jurisdictions: RawJurisdiction[],
	observations: RawObservation[]
): Atlas {
	const indicators = rawIndicators.map(toIndicator);
	const provinces = jurisdictions
		.filter((j) => j.kind === 'province')
		.map(toProvince)
		.sort((a, b) => a.name.localeCompare(b.name, 'es'));
	const countryRaw = jurisdictions.find((j) => j.kind === 'country');
	if (!countryRaw) throw new Error('La API no devolvió el total del país');

	const values: Atlas['values'] = {};
	for (const o of observations) {
		(values[o.indicator] ??= {})[o.jurisdiction] = {
			value: o.value,
			cv: o.cv,
			reliability: o.reliability,
			period: o.period,
			dataset: o.dataset
		};
	}

	const treatment = indicators.find((i) => i.slug === 'diabetes_treatment');
	if (treatment && values.diabetes_treatment) {
		const gap = deriveTreatmentGap(treatment, values.diabetes_treatment);
		indicators.push(gap.indicator);
		values.treatment_gap = gap.values;
	}

	const rank = (i: Indicator) => {
		const at = ORDER.indexOf(i.slug);
		return at === -1 ? ORDER.length : at;
	};
	indicators.sort((a, b) => rank(a) - rank(b));

	return { indicators, provinces, country: toProvince(countryRaw), values };
}

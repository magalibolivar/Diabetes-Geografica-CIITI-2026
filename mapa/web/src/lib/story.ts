import { num } from './format';
import { describeCorrelation, spearman } from './stats';
import type { Atlas } from './types';
import { provinceValues } from './viz';

export interface Step {
	id: string;
	eyebrow: string;
	title: string;
	paragraphs: string[];
	/** Indicador que muestra el mapa mientras se lee este paso. */
	indicator: string;
	mode: 'geo' | 'tiles';
}

interface Row {
	slug: string;
	name: string;
	value: number;
	unreliable: boolean;
}

function rows(atlas: Atlas, indicator: string): Row[] {
	return provinceValues(atlas, indicator)
		.map(({ slug, v }) => ({
			slug,
			name: atlas.provinces.find((p) => p.slug === slug)?.shortName ?? slug,
			value: v.value,
			unreliable: v.reliability === 'unreliable'
		}))
		.sort((a, b) => b.value - a.value);
}

const pct = (v: number) => `${num(v, 1)}%`;

/** Cuántas de las provincias en los extremos (3 más altas + 3 más bajas) tienen marca de poco confiable. */
export function shakyAtExtremes(list: Row[], k = 3): { shaky: number; total: number } {
	const ends = [...list.slice(0, k), ...list.slice(-k)];
	return { shaky: ends.filter((r) => r.unreliable).length, total: ends.length };
}

export function buildStory(atlas: Atlas): Step[] {
	const steps: Step[] = [];
	const country = (slug: string) => atlas.values[slug]?.[atlas.country.slug]?.value;

	const prev = rows(atlas, 'diabetes_prevalence');
	const natPrev = country('diabetes_prevalence');
	if (prev.length && natPrev != null) {
		const hi = prev[0];
		const lo = prev[prev.length - 1];
		const flagged = prev.filter((r) => r.unreliable).length;
		steps.push({
			id: 'prevalencia',
			eyebrow: 'El dato de partida',
			title: `${pct(natPrev)} de los adultos dice tener glucemia elevada o diabetes.`,
			paragraphs: [
				`Es el promedio de las localidades urbanas del país en 2018, según lo que la gente declara en la Encuesta Nacional de Factores de Riesgo.`,
				`Entre provincias va de ${pct(lo.value)} en ${lo.name} a ${pct(hi.value)} en ${hi.name}: ${num(hi.value - lo.value, 1)} puntos de distancia.` +
					(flagged === 0 ? ' Ninguna de estas estimaciones está marcada como poco confiable.' : '')
			],
			indicator: 'diabetes_prevalence',
			mode: 'geo'
		});
	}

	const gap = rows(atlas, 'treatment_gap');
	const natGap = country('treatment_gap');
	if (gap.length && natGap != null) {
		const { shaky, total } = shakyAtExtremes(gap);
		steps.push({
			id: 'tratamiento',
			eyebrow: 'La brecha de tratamiento',
			title: `${pct(natGap)} de quienes declaran diabetes no hizo ningún tratamiento en las últimas dos semanas.`,
			paragraphs: [
				'La encuesta no distingue qué tratamiento ni si es continuo: mide si hizo «alguno» en las últimas dos semanas. Por eso hablamos de brecha de tratamiento y no de falta de acceso.',
				shaky > 0
					? `Las provincias rayadas tienen estimaciones que el INDEC marca como poco confiables. De las ${total} que ocupan los extremos, ${shaky} lo son: conviene mirar el panorama general antes que el podio.`
					: 'Las provincias rayadas tienen estimaciones que el INDEC marca como poco confiables.'
			],
			indicator: 'treatment_gap',
			mode: 'geo'
		});
	}

	const scr = rows(atlas, 'glucose_screening');
	const natScr = country('glucose_screening');
	if (scr.length && natScr != null) {
		const hi = scr[0];
		const lo = scr[scr.length - 1];
		steps.push({
			id: 'control',
			eyebrow: 'El control',
			title: `${pct(natScr)} se midió alguna vez el azúcar en sangre.`,
			paragraphs: [
				`Entre provincias va de ${pct(lo.value)} en ${lo.name} a ${pct(hi.value)} en ${hi.name}.`,
				'Ojo: es «alguna vez en la vida», no un control reciente. Sirve para ver quién llega a un análisis, no si se controla a tiempo.'
			],
			indicator: 'glucose_screening',
			mode: 'geo'
		});
	}

	const nbi = atlas.values.nbi_households;
	const pv = atlas.values.diabetes_prevalence;
	if (nbi && pv) {
		const pairs = atlas.provinces.flatMap((p) => (nbi[p.slug] && pv[p.slug] ? [[nbi[p.slug].value, pv[p.slug].value]] : []));
		const rho = spearman(
			pairs.map((p) => p[0]),
			pairs.map((p) => p[1])
		);
		if (rho != null) {
			const inverse =
				rho < -0.2
					? ' Y va al revés de lo que muchos esperarían: donde hay más NBI se declara menos diabetes. Una explicación posible, que estos datos no pueden confirmar, es que se diagnostica menos.'
					: '';
			steps.push({
				id: 'contexto',
				eyebrow: 'El contexto',
				title: 'La pobreza estructural no alcanza para explicar el mapa.',
				paragraphs: [
					`Cruzando los hogares con necesidades básicas insatisfechas (NBI) con la diabetes declarada, entre las ${pairs.length} provincias hay ${describeCorrelation(rho)} (ρ = ${num(rho, 2)}).${inverse}`,
					'Con 24 puntos, un patrón así sirve para hacer preguntas, no para dar respuestas.'
				],
				indicator: 'nbi_households',
				mode: 'geo'
			});
		}
	}

	steps.push({
		id: 'mosaico',
		eyebrow: 'Otra forma de mirar',
		title: 'Cada provincia, el mismo lugar.',
		paragraphs: [
			'En el mapa, Santa Cruz parece enorme y la Ciudad de Buenos Aires casi desaparece, aunque viven mucho más personas en la segunda. En el mosaico las 24 pesan lo mismo.',
			'Es el mismo dato de antes: la glucemia elevada o diabetes declarada.'
		],
		indicator: 'diabetes_prevalence',
		mode: 'tiles'
	});

	return steps;
}

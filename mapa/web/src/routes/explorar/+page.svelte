<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import DataTable from '#lib/components/DataTable.svelte';
	import IndicatorPicker from '#lib/components/IndicatorPicker.svelte';
	import InfoCard from '#lib/components/InfoCard.svelte';
	import Legend from '#lib/components/Legend.svelte';
	import Map from '#lib/components/Map.svelte';
	import ProvTip from '#lib/components/ProvTip.svelte';
	import Ranking from '#lib/components/Ranking.svelte';
	import Scatter from '#lib/components/Scatter.svelte';
	import { buildScale, mapItems } from '#lib/viz';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const atlas = $derived(data.atlas);

	const q = $derived(page.url.searchParams);
	const slugs = $derived(new Set(atlas.indicators.map((i) => i.slug)));
	const pick = (v: string | null, fallback: string) => (v && slugs.has(v) ? v : fallback);

	const indicator = $derived(
		atlas.indicators.find((i) => i.slug === pick(q.get('i'), 'diabetes_prevalence'))!
	);
	const featured = [
		{ slug: 'diabetes_prevalence', question: 'Glucemia elevada o diabetes declarada', detail: 'Porcentaje de personas adultas que lo declaró en la encuesta de 2018.' },
		{ slug: 'glucose_screening', question: 'Medición de azúcar en sangre', detail: 'Porcentaje que se la midió alguna vez, según la encuesta de 2018.' }
	];
	const featuredAvailable = $derived(featured.filter((item) => slugs.has(item.slug)));
	const advanced = $derived(
		q.get('a') === '1' || !featuredAvailable.some((item) => item.slug === indicator.slug) ||
		q.get('m') === 'dif' || q.has('x') || q.has('y')
	);
	const lineage = $derived(indicator.lineage[0]);
	const mode = $derived(q.get('v') === 'mosaico' ? 'tiles' : 'geo');
	const measure = $derived(q.get('m') === 'dif' ? 'delta' : 'value');
	const selected = $derived(
		atlas.provinces.some((p) => p.slug === q.get('p')) ? (q.get('p') as string) : null
	);
	const sx = $derived(pick(q.get('x'), 'nbi_households'));
	const sy = $derived(pick(q.get('y'), 'diabetes_prevalence'));

	function set(patch: Record<string, string | null>) {
		const u = new URL(page.url.href);
		for (const [k, v] of Object.entries(patch)) {
			if (v == null || v === '') u.searchParams.delete(k);
			else u.searchParams.set(k, v);
		}
		goto(u, { replace: true, reset: false });
	}

	const scale = $derived(buildScale(atlas, indicator, measure));
	const items = $derived(mapItems(atlas, indicator, scale));
	const hasShaky = $derived(items.some((i) => i.reliability === 'unreliable' || i.reliability === 'caution'));
	const selectedProvince = $derived(atlas.provinces.find((p) => p.slug === selected));

	function toggleSelect(slug: string) {
		set({ p: selected === slug ? null : slug });
	}

	function setAdvanced(show: boolean) {
		set(show
			? { a: '1' }
			: { a: null, i: featuredAvailable.some((item) => item.slug === indicator.slug) ? indicator.slug : 'diabetes_prevalence', m: null, x: null, y: null });
	}
</script>

<svelte:head>
	<title>Explorar provincias · Diabetes en Argentina</title>
	<meta
		name="description"
		content="Explorá en el mapa indicadores de salud por provincia argentina y consultá la fuente, la población y el año de cada dato."
	/>
</svelte:head>

<div class="wrap">
	<header class="intro">
		<div class="eyebrow">Explorar</div>
		<h1>Explorá los datos por provincia.</h1>
		<p class="lede">
			{#if advanced}
				Elegí un indicador para mirar el mapa, comparar provincias o consultar la tabla. Cada dato muestra su fuente, población y período.
			{:else}
				Empezá con los dos datos de la encuesta de salud de 2018. Elegí una provincia en el mapa para ver su ficha.
			{/if}
		</p>
	</header>

	<div class="entry">
		<div>
			<h2>{advanced ? 'Todos los indicadores' : 'Elegí un dato'}</h2>
			<p>{advanced ? 'También podés consultar el ranking, las relaciones y la tabla.' : 'Podés cambiarlo cuando quieras.'}</p>
		</div>
		<button class="chip advanced-toggle" aria-expanded={advanced} onclick={() => setAdvanced(!advanced)}>
			{advanced ? 'Volver a explorar' : 'Profundizar: más indicadores y comparaciones'}
		</button>
	</div>
	{#if !advanced}
		<div class="featured" aria-label="Preguntas principales">
			{#each featuredAvailable as item (item.slug)}
				<button class="question card" aria-pressed={indicator.slug === item.slug} onclick={() => set({ i: item.slug })}>
					<strong>{item.question}</strong><span>{item.detail}</span>
				</button>
			{/each}
		</div>
	{/if}

	<div class:advanced class="layout">
		{#if advanced}
			<aside class="col picker">
				<p class="eyebrow">Todos los indicadores</p>
				<IndicatorPicker {atlas} current={indicator.slug} onpick={(i) => set({ i, a: '1' })} />
			</aside>
		{/if}

		<section class="col main" aria-labelledby="mapa-h">
			<div class="card mapcard">
				{#if lineage}
					<p class="map-context"><strong>{lineage.referencePeriod}</strong> · {lineage.universe ?? 'Población indicada por la fuente'}</p>
				{/if}
				<div class="controls">
					<h2 id="mapa-h" class="sr-only">Mapa de {indicator.label}</h2>
					<div class="seg" role="group" aria-label="Tipo de vista">
						<button class="chip" aria-pressed={mode === 'geo'} onclick={() => set({ v: null })}>Mapa</button>
						<button class="chip" aria-pressed={mode === 'tiles'} onclick={() => set({ v: 'mosaico' })}>
							Mosaico
						</button>
					</div>
					{#if advanced}<div class="seg" role="group" aria-label="Qué mostrar">
						<button class="chip" aria-pressed={measure === 'value'} onclick={() => set({ m: null })}>Valor</button>
						<button class="chip" aria-pressed={measure === 'delta'} onclick={() => set({ m: 'dif' })}>
							Diferencia con el país
						</button>
					</div>{/if}
				</div>
				{#if measure === 'delta'}
					<p class="hint delta-note">La diferencia se expresa en puntos porcentuales: 15% frente a 12% son 3 puntos de diferencia.</p>
				{/if}

				<div class="mapframe">
					<Map
						geometry={data.geometry}
						{items}
						{mode}
						{selected}
						onselect={toggleSelect}
						caption="Mapa de {indicator.label} por provincia"
					>
						{#snippet tip(slug)}
							<ProvTip {atlas} {indicator} {slug} {advanced} />
						{/snippet}
					</Map>
				</div>
				{#if mode === 'tiles'}
					<p class="hint">
						Cada provincia ocupa el mismo lugar, sin importar su superficie. Malvinas, Antártida e islas
						australes (sin datos) forman parte de Tierra del Fuego y solo se ven en el mapa.
					</p>
				{/if}

				<Legend {scale} {indicator} showHatch={hasShaky} showNoData={mode === 'geo'} />
			</div>

			{#if selectedProvince}
				<div class="card sel">
					<div>
						<div class="eyebrow">Provincia seleccionada</div>
						<strong>{selectedProvince.name}</strong>
					</div>
					<a class="chip" href="/provincia/{selectedProvince.slug}">Ver todos sus datos →</a>
				</div>
			{/if}
		</section>

		<aside class="col side">
			{#if advanced}
				<div class="card"><InfoCard {atlas} {indicator} /></div>
				<div class="card pad"><Ranking {atlas} {indicator} {selected} onselect={toggleSelect} /></div>
			{:else}
				<div class="card simple-info">
					<div class="eyebrow">Cómo leer este dato</div>
					<h2>{indicator.label}</h2>
					<p>{indicator.description}</p>
			{#if indicator.slug === 'treatment_gap'}<p>La pregunta se refiere a cualquier tratamiento en las últimas dos semanas.</p>{/if}
					{#if lineage}
						<p><strong>Año:</strong> {lineage.referencePeriod}<br /><strong>Población:</strong> {lineage.universe ?? 'Ver metodología de la fuente'}.</p>
					{/if}
					<p class="simple-limit">Los datos de la encuesta son autorreportados. Consultá la fuente si querés conocer cómo se obtuvo la cifra.</p>
					<button class="chip" onclick={() => setAdvanced(true)}>Ver más indicadores y detalles</button>
				</div>
			{/if}
		</aside>
	</div>

	{#if advanced}
	<section class="rel" aria-labelledby="rel-h">
		<div class="relhead">
			<div class="eyebrow">Profundizar · relaciones</div>
			<h2 id="rel-h">Compará dos indicadores</h2>
			<p class="lede">
				Cada punto representa una provincia. Una relación en este gráfico no demuestra que un dato cause el otro.
			</p>
		</div>
		<div class="card pad">
			<Scatter
				{atlas}
				x={sx}
				y={sy}
				{selected}
				onaxes={(x, y) => set({ x, y })}
				onselect={toggleSelect}
			/>
		</div>
	</section>

	<section class="card pad tablecard">
		<DataTable {atlas} {indicator} />
	</section>
	{/if}
</div>

<style>
	.intro {
		padding: 2rem 0 1.3rem;
		max-width: 46rem;
	}
	.intro h1 {
		font-size: clamp(2rem, 4vw, 3rem);
		margin-top: 0.6rem;
	}
	.intro .lede { font-family: var(--font-ui); font-size: 1rem; line-height: 1.5; max-width: 42rem; margin: 0.6rem 0 0; }
	.entry {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		flex-wrap: wrap;
		margin-bottom: 1rem;
	}
	.entry h2 { font-size: 1.5rem; margin: 0; }
	.entry p { color: var(--ink-2); margin: 0.25rem 0 0; }
	.advanced-toggle { white-space: nowrap; }
	.featured { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
	.question { text-align: left; padding: 1rem 1.1rem; border: 1px solid var(--ring); cursor: pointer; }
	.question[aria-pressed='true'] { border-color: var(--orange); box-shadow: 0 0 0 2px var(--orange); }
	.question strong, .question span { display: block; }
	.question strong { line-height: 1.3; }
	.question span { color: var(--ink-2); font-size: 0.85rem; margin-top: 0.45rem; }
	.layout {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(280px, 380px);
		gap: 1.5rem;
		align-items: start;
	}
	.layout.advanced { grid-template-columns: minmax(220px, 280px) minmax(0, 1fr) minmax(300px, 380px); }
	.simple-info { padding: 1.3rem 1.4rem; }
	.simple-info h2 { font-size: 1.5rem; margin: 0.45rem 0; }
	.simple-info p { color: var(--ink-2); line-height: 1.5; }
	.simple-limit { border-top: 1px solid var(--ring); padding-top: 0.8rem; }
	.delta-note { text-align: left; margin: 0 0 0.8rem; }
	.picker {
		position: sticky;
		top: 84px;
	}
	.side {
		display: grid;
		gap: 1.5rem;
	}
	.pad {
		padding: 1.3rem 1.4rem;
	}
	.mapcard {
		padding: 1.2rem 1.4rem 1.5rem;
	}
	.map-context { color: var(--ink-2); font-size: 0.82rem; line-height: 1.4; margin: 0 0 0.85rem; }
	.controls {
		display: flex;
		gap: 0.8rem 1.4rem;
		flex-wrap: wrap;
		justify-content: space-between;
		margin-bottom: 0.8rem;
	}
	.seg {
		display: flex;
		gap: 0.3rem;
	}
	.mapframe {
		max-width: 430px;
		margin: 0 auto 1.2rem;
	}
	.hint {
		text-align: center;
		font-size: 0.8rem;
		color: var(--ink-2);
		margin: -0.4rem 0 1rem;
	}
	.sel {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		padding: 0.9rem 1.2rem;
		margin-top: 1rem;
		flex-wrap: wrap;
	}
	.rel {
		margin-top: 5rem;
	}
	.relhead {
		max-width: 44rem;
		margin-bottom: 1.5rem;
	}
	.relhead h2 {
		margin: 0.5rem 0 0.8rem;
	}
	.tablecard {
		margin-top: 1.5rem;
	}
	@media (max-width: 1180px) {
		.layout.advanced {
			grid-template-columns: minmax(0, 1fr) minmax(300px, 380px);
		}
		.picker {
			position: static;
			grid-column: 1 / -1;
		}
	}
	@media (max-width: 800px) {
		.layout, .layout.advanced {
			grid-template-columns: minmax(0, 1fr);
		}
		.featured { grid-template-columns: 1fr; }
	}
</style>

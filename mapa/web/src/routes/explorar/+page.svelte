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
</script>

<svelte:head>
	<title>Explorar · MAPA</title>
	<meta
		name="description"
		content="Explorá en el mapa la diabetes y sus factores en las 24 provincias argentinas, con el margen de error de cada dato."
	/>
</svelte:head>

<div class="wrap">
	<header class="intro">
		<div class="eyebrow">Explorar</div>
		<h1>Elegí un dato y mirá cómo cambia el mapa.</h1>
	</header>

	<div class="layout">
		<aside class="col picker">
			<IndicatorPicker {atlas} current={indicator.slug} onpick={(i) => set({ i })} />
		</aside>

		<section class="col main" aria-labelledby="mapa-h">
			<div class="card mapcard">
				<div class="controls">
					<h2 id="mapa-h" class="sr-only">Mapa de {indicator.label}</h2>
					<div class="seg" role="group" aria-label="Tipo de vista">
						<button class="chip" aria-pressed={mode === 'geo'} onclick={() => set({ v: null })}>Mapa</button>
						<button class="chip" aria-pressed={mode === 'tiles'} onclick={() => set({ v: 'mosaico' })}>
							Mosaico
						</button>
					</div>
					<div class="seg" role="group" aria-label="Qué mostrar">
						<button class="chip" aria-pressed={measure === 'value'} onclick={() => set({ m: null })}>Valor</button>
						<button class="chip" aria-pressed={measure === 'delta'} onclick={() => set({ m: 'dif' })}>
							Diferencia con el país
						</button>
					</div>
				</div>

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
							<ProvTip {atlas} {indicator} {slug} />
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
			<div class="card"><InfoCard {atlas} {indicator} /></div>
			<div class="card pad"><Ranking {atlas} {indicator} {selected} onselect={toggleSelect} /></div>
		</aside>
	</div>

	<section class="rel" aria-labelledby="rel-h">
		<div class="relhead">
			<div class="eyebrow">Relaciones</div>
			<h2 id="rel-h">¿Se parecen entre sí?</h2>
			<p class="lede">
				Elegí dos datos y mirá cada provincia como un punto. Sirve para hacer preguntas, no para
				responderlas.
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
</div>

<style>
	.intro {
		padding: 3rem 0 2rem;
		max-width: 46rem;
	}
	.intro h1 {
		font-size: clamp(2rem, 4.6vw, 3.4rem);
		margin-top: 0.6rem;
	}
	.layout {
		display: grid;
		grid-template-columns: minmax(220px, 280px) minmax(0, 1fr) minmax(300px, 380px);
		gap: 1.5rem;
		align-items: start;
	}
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
		.layout {
			grid-template-columns: minmax(0, 1fr) minmax(300px, 380px);
		}
		.picker {
			position: static;
			grid-column: 1 / -1;
		}
	}
	@media (max-width: 800px) {
		.layout {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>

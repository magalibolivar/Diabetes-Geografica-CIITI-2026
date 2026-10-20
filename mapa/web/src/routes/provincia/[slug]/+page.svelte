<script lang="ts">
	import { goto } from '$app/navigation';
	import Map from '#lib/components/Map.svelte';
	import Strip from '#lib/components/Strip.svelte';
	import { num, signed } from '#lib/format';
	import { ci95 } from '#lib/stats';
	import type { Category, Indicator, MapItem } from '#lib/types';
	import { CATEGORY_LABEL, RELIABILITY_TEXT, provinceValues, rankOf, referenceFor } from '#lib/viz';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const atlas = $derived(data.atlas);
	const province = $derived(atlas.provinces.find((p) => p.slug === data.slug)!);

	const hero = $derived(atlas.indicators.find((i) => i.slug === 'diabetes_prevalence')!);
	const heroValue = $derived(atlas.values[hero.slug]?.[data.slug]);
	const heroRef = $derived(referenceFor(atlas, hero));

	// Mapa localizador: todas en gris, ésta resaltada.
	const items = $derived<MapItem[]>(
		atlas.provinces.map((p) => ({
			slug: p.slug,
			name: p.name,
			fill: p.slug === data.slug ? 'var(--orange)' : 'var(--nodata)',
			ink: 'var(--ink)',
			label: '',
			reliability: null,
			aria: p.name
		}))
	);

	const order: Category[] = ['outcome', 'care', 'risk_factor', 'context'];
	// La brecha es el espejo del tratamiento: se muestra sólo el indicador original en la ficha.
	const shown = $derived(atlas.indicators.filter((i) => !i.derived));
	const groups = $derived(
		order.map((c) => ({ key: c, label: CATEGORY_LABEL[c], items: shown.filter((i) => i.category === c) }))
	);

	function row(i: Indicator) {
		const v = atlas.values[i.slug]?.[data.slug];
		if (!v) return null;
		const rank = rankOf(atlas, i.slug, data.slug);
		const ref = referenceFor(atlas, i);
		return {
			i,
			v,
			rank,
			ref,
			ci: ci95(v.value, v.cv, i.unit === '%' ? 100 : Infinity)
		};
	}

	/** Lo que más se aparta: los tres primeros y los tres últimos puestos, aclarando si el dato es dudoso. */
	const standouts = $derived(
		shown
			.map(row)
			.filter((r): r is NonNullable<ReturnType<typeof row>> => !!r && !!r.rank && i_nonNeutral(r.i))
			.filter((r) => r.rank!.rank <= 3 || r.rank!.rank >= r.rank!.of - 2)
			.slice(0, 6)
	);
	function i_nonNeutral(i: Indicator) {
		return i.higherIs !== 'neutral';
	}

	const others = $derived(atlas.provinces.filter((p) => p.slug !== data.slug));
</script>

<svelte:head>
	<title>{province.name} · MAPA</title>
	<meta
		name="description"
		content="Diabetes y factores asociados en {province.name}: cada dato comparado con las demás provincias y con su margen de error."
	/>
</svelte:head>

<div class="wrap">
	<header class="top">
		<div class="titles">
			<div class="eyebrow">{province.region ?? 'Provincia'}</div>
			<h1>{province.name}</h1>
			{#if heroValue}
				<div class="herorow">
					<div class="hero num">{num(heroValue.value, 1)}<span>%</span></div>
					<p class="herotext">
						de los adultos de localidades urbanas declara glucemia elevada o diabetes.
						<span class="delta num">{signed(heroValue.value - heroRef.value)} pp</span> respecto del total del país
						({num(heroRef.value, 1)}%).
					</p>
				</div>
			{/if}
		</div>
		<div class="loc card">
			<div class="mapbox">
				<Map
					geometry={data.geometry}
					{items}
					onselect={(s) => goto(`/provincia/${s}`)}
					showExtras={false}
					caption="Mapa para ubicar {province.name}. Tocá otra provincia para ir a su ficha."
				>
					{#snippet tip(slug)}
						<strong>{atlas.provinces.find((p) => p.slug === slug)?.name}</strong>
					{/snippet}
				</Map>
			</div>
		</div>
	</header>

	{#if data.slug === 'tierra-del-fuego'}
		<aside class="tdf card">
			<strong>Sobre esta provincia.</strong> Tierra del Fuego, Antártida e Islas del Atlántico Sur también incluye
			las Islas Malvinas, la Antártida Argentina y las islas australes. La encuesta no releva esos territorios:
			los datos de esta ficha describen solo sus localidades urbanas de la Isla Grande.
		</aside>
	{/if}

	{#if standouts.length}
		<section class="stand" aria-labelledby="stand-h">
			<h2 id="stand-h">Lo que más se destaca</h2>
			<ul>
				{#each standouts as s (s.i.slug)}
					<li class="card">
						<span class="eyebrow">{s.rank!.rank <= 3 ? 'Entre las más altas' : 'Entre las más bajas'}</span>
						<strong>{s.i.label}</strong>
						<span class="num big">{num(s.v.value, s.i.decimals)}{s.i.unit === '%' ? '%' : ' ' + s.i.unit}</span>
						<span class="sub num">N.º {s.rank!.rank} de {s.rank!.of}</span>
						{#if s.v.reliability === 'unreliable' || s.v.reliability === 'caution'}
							<span class="flag" class:caution={s.v.reliability === 'caution'}>
								{RELIABILITY_TEXT[s.v.reliability].short}
							</span>
						{/if}
					</li>
				{/each}
			</ul>
		</section>
	{/if}

	<section aria-labelledby="todo-h" class="all">
		<div class="allhead">
			<h2 id="todo-h">Todos los datos</h2>
			<p class="key">
				<span class="kdot a"></span> {province.name}
				<span class="kdot"></span> las otras provincias
				<span class="kdot hollow"></span> poco confiable
				<span class="kref"></span> total del país
			</p>
		</div>

		{#each groups as g (g.key)}
			<div class="group">
				<h3>{g.label}</h3>
				{#each g.items as ind (ind.slug)}
					{@const r = row(ind)}
					{#if r}
						<div class="irow">
							<div class="label">
								<strong>{ind.label}</strong>
								{#if r.v.reliability === 'unreliable' || r.v.reliability === 'caution'}
									<span class="flag" class:caution={r.v.reliability === 'caution'}>
										{RELIABILITY_TEXT[r.v.reliability].short}
									</span>
								{/if}
							</div>
							<div class="value num">
								{num(r.v.value, ind.decimals)}<small>{ind.unit === '%' ? '%' : ' ' + ind.unit}</small>
							</div>
							<div class="strip"><Strip {atlas} indicator={ind} slug={data.slug} /></div>
							<div class="meta num">
								{#if r.rank}N.º {r.rank.rank} de {r.rank.of}{/if}
								{#if r.ci}· IC 95%: {num(r.ci.low, 1)}–{num(r.ci.high, 1)}{/if}
								· {signed(r.v.value - r.ref.value, ind.decimals)}
								{ind.unit === '%' ? 'pp' : ind.unit} vs. {r.ref.isCountry ? 'el país' : 'el promedio'}
							</div>
						</div>
					{/if}
				{/each}
			</div>
		{/each}
	</section>

	<section class="next card">
		<div>
			<h2>Compará con otra provincia</h2>
			<p class="lede">Mirá lado a lado dos jurisdicciones, dato por dato.</p>
		</div>
		<label>
			<span class="sr-only">Elegir provincia para comparar</span>
			<select onchange={(e) => e.currentTarget.value && goto(`/comparar?a=${data.slug}&b=${e.currentTarget.value}`)}>
				<option value="">Elegí una provincia…</option>
				{#each others as p (p.slug)}
					<option value={p.slug}>{p.name}</option>
				{/each}
			</select>
		</label>
	</section>
</div>

<style>
	.top {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(200px, 300px);
		gap: 2rem;
		align-items: center;
		padding: 3.5rem 0 3rem;
	}
	h1 {
		margin: 0.6rem 0 1.4rem;
	}
	.herorow {
		display: flex;
		align-items: center;
		gap: 1.4rem;
		flex-wrap: wrap;
	}
	.hero {
		font-size: clamp(3.4rem, 9vw, 6.2rem);
		font-weight: 600;
		line-height: 0.95;
		letter-spacing: -0.03em;
		color: var(--ink);
	}
	.hero span {
		font-size: 0.5em;
		font-weight: 500;
		margin-left: 0.05em;
		color: var(--ink-2);
	}
	.herotext {
		max-width: 22rem;
		margin: 0;
		color: var(--ink-2);
		font-size: 1.02rem;
	}
	.delta {
		color: var(--ink);
		font-weight: 600;
	}
	.loc {
		padding: 1rem 1.2rem;
	}
	.mapbox {
		max-width: 220px;
		margin: 0 auto;
	}
	.tdf {
		padding: 1rem 1.2rem;
		margin-bottom: 2.5rem;
		font-size: 0.92rem;
		color: var(--ink-2);
		max-width: 46rem;
	}
	.tdf strong {
		color: var(--ink);
	}
	.stand {
		margin-bottom: 4rem;
	}
	.stand h2,
	.allhead h2 {
		font-size: 1.9rem;
		margin-bottom: 1.2rem;
	}
	.stand ul {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
		gap: 0.9rem;
	}
	.stand li {
		padding: 1rem 1.1rem;
		display: grid;
		gap: 0.2rem;
		align-content: start;
	}
	.big {
		font-size: 1.8rem;
		font-weight: 600;
		line-height: 1.15;
		margin-top: 0.3rem;
	}
	.sub {
		font-size: 0.82rem;
		color: var(--ink-2);
	}
	.allhead {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 1rem;
		flex-wrap: wrap;
	}
	.key {
		font-size: 0.78rem;
		color: var(--ink-2);
		margin: 0;
	}
	.kdot {
		display: inline-block;
		width: 9px;
		height: 9px;
		border-radius: 50%;
		margin: 0 0.3rem 0 0.9rem;
		background: color-mix(in srgb, var(--blue) 55%, var(--surface));
	}
	.kdot.a {
		background: var(--orange);
		margin-left: 0;
	}
	.kdot.hollow {
		background: var(--surface);
		border: 1.5px solid color-mix(in srgb, var(--blue) 70%, var(--surface));
	}
	.kref {
		display: inline-block;
		height: 12px;
		border-left: 1.5px solid var(--muted);
		margin: 0 0.3rem 0 0.9rem;
		vertical-align: middle;
	}
	.group {
		margin-top: 2.4rem;
	}
	.group h3 {
		padding-bottom: 0.6rem;
		border-bottom: 1px solid var(--ink);
		margin-bottom: 0.2rem;
	}
	.irow {
		display: grid;
		grid-template-columns: minmax(180px, 1.1fr) 5.5rem minmax(180px, 2fr);
		grid-template-areas: 'label value strip' '. . meta';
		gap: 0.2rem 1.4rem;
		align-items: center;
		padding: 0.9rem 0;
		border-bottom: 1px solid var(--hair);
	}
	.label {
		grid-area: label;
		display: grid;
		gap: 0.2rem;
		justify-items: start;
	}
	.value {
		grid-area: value;
		font-size: 1.45rem;
		font-weight: 600;
		text-align: right;
	}
	.value small {
		font-size: 0.8rem;
		font-weight: 500;
		color: var(--ink-2);
	}
	.strip {
		grid-area: strip;
	}
	.meta {
		grid-area: meta;
		font-size: 0.78rem;
		color: var(--ink-2);
	}
	.next {
		margin-top: 5rem;
		padding: 2rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1.5rem;
		flex-wrap: wrap;
	}
	.next h2 {
		font-size: 1.8rem;
		margin-bottom: 0.4rem;
	}
	.next .lede {
		margin: 0;
	}
	.next select {
		background: var(--page);
		border: 1px solid var(--hair);
		border-radius: 999px;
		padding: 0.7rem 1.2rem;
		font-size: 1rem;
		min-width: 15rem;
	}
	@media (max-width: 800px) {
		.top {
			grid-template-columns: 1fr;
		}
		.loc {
			order: -1;
			justify-self: start;
			width: 190px;
		}
		.irow {
			grid-template-columns: 1fr auto;
			grid-template-areas: 'label value' 'strip strip' 'meta meta';
		}
	}
</style>

<script lang="ts">
	import { goto } from '$app/navigation';
	import Legend from '#lib/components/Legend.svelte';
	import Map from '#lib/components/Map.svelte';
	import ProvTip from '#lib/components/ProvTip.svelte';
	import { num } from '#lib/format';
	import { buildScale, mapItems } from '#lib/viz';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const atlas = $derived(data.atlas);
	const prevalence = $derived(atlas.indicators.find((i) => i.slug === 'diabetes_prevalence'));
	const screening = $derived(atlas.indicators.find((i) => i.slug === 'glucose_screening'));
	const prevalenceValue = $derived(atlas.values.diabetes_prevalence?.[atlas.country.slug]?.value);
	const screeningValue = $derived(atlas.values.glucose_screening?.[atlas.country.slug]?.value);
	const scale = $derived(prevalence ? buildScale(atlas, prevalence, 'value') : null);
	const items = $derived(prevalence && scale ? mapItems(atlas, prevalence, scale) : []);
	const hasShaky = $derived(items.some((i) => i.reliability === 'unreliable' || i.reliability === 'caution'));
</script>

<svelte:head>
	<title>Diabetes en Argentina · Datos por provincia</title>
	<meta name="description" content="Dos datos de la encuesta de salud de 2018 y un mapa para explorar la diabetes declarada por provincia en Argentina." />
	<meta property="og:title" content="Diabetes en Argentina" />
	<meta property="og:locale" content="es_AR" />
</svelte:head>

<div class="wrap home">
	<section class="hero" aria-labelledby="hero-title">
		<div class="eyebrow">Datos públicos · Argentina</div>
		<h1 id="hero-title">Diabetes en Argentina</h1>
		<p class="lede">Qué muestran los datos públicos por provincia.</p>
		<p class="intro">La Encuesta Nacional de Factores de Riesgo de 2018 preguntó a personas adultas sobre su salud. Estas son dos formas de empezar a leer sus resultados.</p>
	</section>

	<section class="findings" aria-label="Dos datos para empezar">
		{#if prevalence && prevalenceValue != null}
			<article class="finding card">
				<div class="eyebrow">Glucemia elevada o diabetes declarada</div>
				<div class="value">{num(prevalenceValue, 1)}%</div>
				<h2>Lo declaró alrededor de una de cada ocho personas adultas.</h2>
				<p>Es una respuesta a la encuesta, no un diagnóstico confirmado ni una cuenta de todas las personas con diabetes.</p>
				<p class="source">ENFR 2018 · Personas de 18 años o más en localidades urbanas de 5.000 habitantes o más.</p>
				<a href="/explorar?i=diabetes_prevalence">Ver en el mapa →</a>
			</article>
		{/if}
		{#if screening && screeningValue != null}
			<article class="finding card">
				<div class="eyebrow">Medición de glucosa</div>
				<div class="value">{num(screeningValue, 1)}%</div>
				<h2>Se había medido el azúcar en sangre alguna vez.</h2>
				<p>“Alguna vez” no indica si el control fue reciente ni si se hizo con la frecuencia adecuada.</p>
				<p class="source">ENFR 2018 · Personas de 18 años o más en localidades urbanas de 5.000 habitantes o más.</p>
				<a href="/explorar?i=glucose_screening">Ver en el mapa →</a>
			</article>
		{/if}
	</section>

	<section class="explore" aria-labelledby="explore-title">
		<div class="explore-copy">
			<div class="eyebrow">Explorá tu provincia</div>
			<h2 id="explore-title">Un dato nacional, distintas realidades provinciales.</h2>
			<p>El mapa muestra el porcentaje que declaró glucemia elevada o diabetes en cada provincia. Seleccioná una para abrir su ficha, o entrá al explorador para cambiar de indicador.</p>
			<div class="links">
				<a class="chip primary" href="/explorar">Abrir el mapa →</a>
				<a class="chip" href="/explorar?a=1">Profundizar en los datos →</a>
			</div>
		</div>
		{#if prevalence && scale}
			<div class="map-preview card">
				<div class="mapframe">
					<Map geometry={data.geometry} {items} mode="geo" onselect={(slug) => goto(`/provincia/${slug}`)} caption="Porcentaje de personas adultas que declaró glucemia elevada o diabetes en 2018, por provincia. Seleccioná una provincia para abrir su ficha.">
						{#snippet tip(slug)}<ProvTip {atlas} indicator={prevalence} {slug} />{/snippet}
					</Map>
				</div>
				<Legend {scale} indicator={prevalence} showHatch={hasShaky} showNoData={true} />
			</div>
		{/if}
	</section>

	<section class="deeper" aria-labelledby="deeper-title">
		<div class="eyebrow">Profundizar</div>
		<h2 id="deeper-title">Más formas de mirar los datos</h2>
		<p>Compará provincias, consultá otros indicadores y revisá cómo se obtuvo cada cifra.</p>
		<div class="links">
			<a href="/explorar?a=1">Todos los indicadores y gráficos →</a>
			<a href="/comparar">Comparar provincias →</a>
			<a href="/metodologia">Fuentes y metodología →</a>
		</div>
	</section>
</div>

<style>
	.home { padding-top: clamp(3rem, 7vw, 6rem); }
	.hero { max-width: 48rem; margin-bottom: 3rem; }
	.hero h1 { margin: .75rem 0 .4rem; }
	.hero .lede { margin: 0 0 1.3rem; color: var(--orange-ink); }
	.intro { color: var(--ink-2); font-size: 1.1rem; line-height: 1.6; max-width: 43rem; }
	.findings { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
	.finding { padding: clamp(1.5rem, 3vw, 2.5rem); display: flex; flex-direction: column; align-items: flex-start; }
	.value { font: 650 clamp(3.5rem, 7vw, 6rem)/1 var(--font-ui); letter-spacing: -.055em; margin: 1.1rem 0; color: var(--seq-5); }
	.finding h2 { font-size: clamp(1.35rem, 2.2vw, 1.8rem); margin: 0 0 .6rem; }
	.finding p { color: var(--ink-2); line-height: 1.5; margin: 0 0 1rem; }
	.finding .source { font-size: .84rem; margin-top: auto; padding-top: .5rem; }
	.finding a { font-weight: 650; }
	.explore { display: grid; grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr); gap: clamp(2rem, 5vw, 5rem); align-items: center; margin-top: clamp(5rem, 9vw, 9rem); }
	.explore h2, .deeper h2 { margin: .7rem 0 1rem; }
	.explore p, .deeper p { color: var(--ink-2); line-height: 1.6; }
	.links { display: flex; gap: .8rem 1.3rem; flex-wrap: wrap; margin-top: 1.7rem; }
	.primary { background: var(--ink); color: var(--surface); }
	.map-preview { padding: 1.2rem; }
	.mapframe { max-width: 390px; margin: 0 auto 1rem; }
	.deeper { margin: clamp(5rem, 9vw, 9rem) 0 1rem; padding: 2.5rem 0; border-top: 1px solid var(--hair); }
	.deeper .links a { font-weight: 600; }
	@media (max-width: 800px) { .findings, .explore { grid-template-columns: 1fr; } .hero { margin-bottom: 2rem; } }
</style>

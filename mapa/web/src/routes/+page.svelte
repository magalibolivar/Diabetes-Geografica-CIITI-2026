<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Legend from '#lib/components/Legend.svelte';
	import Locate from '#lib/components/Locate.svelte';
	import Map from '#lib/components/Map.svelte';
	import ProvTip from '#lib/components/ProvTip.svelte';
	import { buildStory } from '#lib/story';
	import { buildScale, mapItems } from '#lib/viz';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const atlas = $derived(data.atlas);
	const steps = $derived(buildStory(atlas));

	/** -1 = portada; 0.. = pasos de la historia. */
	let active = $state(-1);
	let introEl: HTMLElement | undefined = $state();
	let outroEl: HTMLElement | undefined = $state();
	let stepEls: HTMLElement[] = $state([]);

	const current = $derived(steps[Math.max(active, 0)]);
	const indicator = $derived(atlas.indicators.find((i) => i.slug === current?.indicator));
	const scale = $derived(indicator ? buildScale(atlas, indicator, 'value') : null);
	const items = $derived(indicator && scale ? mapItems(atlas, indicator, scale) : []);
	const hasShaky = $derived(items.some((i) => i.reliability === 'unreliable' || i.reliability === 'caution'));

	onMount(() => {
		let cleanup = () => {};
		let dead = false;

		(async () => {
			const [{ gsap }, { ScrollTrigger }, { default: Lenis }] = await Promise.all([
				import('gsap'),
				import('gsap/ScrollTrigger'),
				import('lenis')
			]);
			if (dead) return;
			gsap.registerPlugin(ScrollTrigger);

			const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
			let lenis: InstanceType<typeof Lenis> | undefined;
			let tick: ((t: number) => void) | undefined;
			if (!reduce) {
				lenis = new Lenis({ lerp: 0.11 });
				lenis.on('scroll', ScrollTrigger.update);
				tick = (t: number) => lenis!.raf(t * 1000);
				gsap.ticker.add(tick);
				gsap.ticker.lagSmoothing(0);
			}

			const ctx = gsap.context(() => {
				if (!reduce) {
					gsap.from('[data-reveal]', { y: 28, opacity: 0, duration: 1, ease: 'power3.out', stagger: 0.09, delay: 0.1 });
					gsap.from('.stage .mapwrap', { opacity: 0, scale: 0.97, duration: 1.2, ease: 'power2.out' });
					gsap.from('.stage .poly:not(.over):not(.marker):not(.ring):not(.hring)', {
						opacity: 0,
						duration: 0.7,
						ease: 'power1.out',
						stagger: { each: 0.03, from: 'random' },
						clearProps: 'opacity'
					});
				}
				if (introEl) {
					ScrollTrigger.create({
						trigger: introEl,
						start: 'top 90%',
						end: 'bottom 55%',
						onToggle: (self) => self.isActive && (active = -1)
					});
				}
				stepEls.forEach((el, i) => {
					if (!el) return;
					ScrollTrigger.create({
						trigger: el,
						start: 'top 55%',
						end: 'bottom 55%',
						onToggle: (self) => self.isActive && (active = i)
					});
				});
			});

			cleanup = () => {
				ctx.revert();
				if (tick) gsap.ticker.remove(tick);
				lenis?.destroy();
			};
		})();

		return () => {
			dead = true;
			cleanup();
		};
	});
</script>

<svelte:head>
	<title>MAPA · Atlas de la diabetes en Argentina</title>
	<meta
		name="description"
		content="Qué dicen —y qué no— los datos oficiales sobre diabetes, atención y contexto en las 24 provincias argentinas, con el margen de error de cada cifra."
	/>
	<meta property="og:title" content="MAPA · Atlas de la diabetes en Argentina" />
	<meta property="og:locale" content="es_AR" />
</svelte:head>

<div class="wrap story">
	<div class="steps">
		<section class="step intro" bind:this={introEl}>
			<div class="eyebrow" data-reveal>Atlas de la diabetes en Argentina</div>
			<h1 data-reveal>Diabetes en Argentina, <em>provincia</em> por provincia.</h1>
			<p class="lede" data-reveal>
				Qué dicen —y qué no— los datos oficiales sobre diabetes, atención y contexto en las 24
				jurisdicciones, con el margen de error de cada cifra a la vista.
			</p>
			<div class="ctas" data-reveal>
				<Locate />
				<a class="more" href="/explorar">Explorar todos los datos →</a>
			</div>
			<p class="hint" data-reveal aria-hidden="true">Seguí bajando <span>↓</span></p>
		</section>

		{#each steps as s, i (s.id)}
			<section class="step" class:on={active === i} id={s.id} bind:this={stepEls[i]}>
				<div class="eyebrow">{s.eyebrow}</div>
				<h2>{s.title}</h2>
				{#each s.paragraphs as p (p)}
					<p>{p}</p>
				{/each}
			</section>
		{/each}

		<section class="step outro on" bind:this={outroEl}>
			<div class="eyebrow">Antes de sacar conclusiones</div>
			<h2>Lo que estos datos no dicen.</h2>
			<ul class="nots">
				<li><strong>No cuentan cuántas personas tienen diabetes.</strong> Miden lo que la gente declara; quien nunca se hizo un análisis no lo sabe.</li>
				<li><strong>No explican causas.</strong> Son comparaciones entre 24 provincias, y las provincias no son personas.</li>
				<li><strong>No cubren a todos.</strong> Solo localidades de 5.000 o más habitantes, y con datos de 2018 o anteriores.</li>
			</ul>
			<div class="outro-links">
				<a class="chip big" href="/explorar">Explorar el mapa</a>
				<a class="chip big" href="/comparar">Comparar provincias</a>
				<a class="chip big" href="/metodologia">Cómo se hizo</a>
			</div>
		</section>
	</div>

	<div class="stage" aria-label="Mapa de la historia">
		{#if current && indicator && scale}
			<div class="now" aria-live="polite">
				<span class="eyebrow">Mostrando</span>
				<strong>{indicator.label}</strong>
				<span class="per">{indicator.lineage[0]?.referencePeriod ?? ''}</span>
			</div>
			<div class="mapwrap">
				<Map
					geometry={data.geometry}
					{items}
					mode={current.mode}
					onselect={(slug) => goto(`/provincia/${slug}`)}
					caption="Mapa de {indicator.label} por provincia. Tocá una provincia para ver su ficha."
				>
					{#snippet tip(slug)}
						<ProvTip {atlas} {indicator} {slug} />
					{/snippet}
				</Map>
			</div>
			<div class="lg">
				<Legend {scale} {indicator} showHatch={hasShaky} />
			</div>
		{/if}
	</div>
</div>

<style>
	.story {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(340px, 560px);
		gap: clamp(2rem, 6vw, 6rem);
		align-items: start;
	}
	.step {
		min-height: 88vh;
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: 3rem 0;
		max-width: 36rem;
		opacity: 0.3;
		transition: opacity 0.5s var(--ease);
	}
	.step.on,
	.step.intro,
	.step.outro {
		opacity: 1;
	}
	.step.intro {
		min-height: calc(100vh - 64px);
		max-width: 38rem;
	}
	.step h2 {
		margin: 0.8rem 0 1.3rem;
		font-size: clamp(1.9rem, 3.4vw, 2.9rem);
	}
	.step p {
		font-size: 1.12rem;
		line-height: 1.6;
		color: var(--ink-2);
	}
	h1 {
		margin: 1rem 0 1.4rem;
	}
	h1 em {
		font-style: italic;
		font-weight: 350;
		font-variation-settings: 'opsz' 144;
		color: var(--orange-ink);
	}
	.lede {
		margin-bottom: 2.2rem;
		max-width: 33rem;
	}
	.ctas {
		display: flex;
		align-items: flex-start;
		gap: 1.8rem;
		flex-wrap: wrap;
	}
	.more {
		align-self: center;
		font-weight: 600;
	}
	.hint {
		margin-top: 3.5rem;
		font-size: 0.85rem !important;
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
	.hint span {
		display: inline-block;
		animation: bob 1.8s ease-in-out infinite;
	}
	@keyframes bob {
		50% {
			transform: translateY(5px);
		}
	}
	.nots {
		padding: 0;
		list-style: none;
		display: grid;
		gap: 1rem;
		margin: 0 0 2rem;
	}
	.nots li {
		font-size: 1.05rem;
		line-height: 1.55;
		color: var(--ink-2);
		padding-left: 1.4rem;
		position: relative;
	}
	.nots li::before {
		content: '';
		position: absolute;
		left: 0;
		top: 0.62em;
		width: 8px;
		height: 8px;
		border-radius: 2px;
		background: var(--orange);
	}
	.nots strong {
		color: var(--ink);
	}
	.outro-links {
		display: flex;
		gap: 0.6rem;
		flex-wrap: wrap;
	}
	.chip.big {
		padding: 0.7rem 1.2rem;
		font-size: 1rem;
		font-weight: 500;
	}

	.stage {
		position: sticky;
		top: 78px;
		height: calc(100vh - 96px);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 1rem;
	}
	.now {
		align-self: flex-start;
		display: flex;
		align-items: baseline;
		gap: 0.7rem;
		flex-wrap: wrap;
		font-size: 0.95rem;
	}
	.per {
		color: var(--ink-2);
		font-size: 0.85rem;
	}
	.mapwrap {
		width: min(100%, calc((100vh - 290px) * 0.638));
		min-width: 200px;
	}
	.lg {
		width: min(100%, 480px);
	}

	@media (max-width: 900px) {
		.story {
			display: flex;
			flex-direction: column;
		}
		.stage {
			order: -1;
			position: sticky;
			top: 56px;
			z-index: 4;
			height: 44vh;
			padding: 0.6rem 0 0.4rem;
			gap: 0.4rem;
			background: var(--page);
			border-bottom: 1px solid var(--hair);
		}
		.mapwrap {
			width: min(100%, calc((44vh - 90px) * 0.638));
		}
		.lg {
			display: none;
		}
		.step {
			min-height: 74vh;
		}
		.step.intro {
			min-height: auto;
			padding-top: 2rem;
		}
	}
</style>

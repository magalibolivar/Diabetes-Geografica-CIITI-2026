<script lang="ts">
	import '../app.css';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Logo from '#lib/components/Logo.svelte';
	import ThemeToggle from '#lib/components/ThemeToggle.svelte';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const nav = [
		{ href: '/explorar', label: 'Explorar' },
		{ href: '/comparar', label: 'Comparar' },
		{ href: '/metodologia', label: 'Metodología' }
	];
	const here = $derived(page.url.pathname);
	const currentProvince = $derived(
		here.startsWith('/provincia/') ? decodeURIComponent(here.split('/')[2] ?? '') : ''
	);

	function jump(e: Event) {
		const slug = (e.currentTarget as HTMLSelectElement).value;
		if (slug) goto(`/provincia/${slug}`);
	}
</script>

<svelte:head>
	<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
</svelte:head>

<a class="skip" href="#contenido">Saltar al contenido</a>

<header>
	<div class="wrap bar">
		<a class="brand" href="/" aria-label="MAPA, inicio">
			<Logo />
			<span class="word">MAPA</span>
			<span class="tag">Atlas de la diabetes en Argentina</span>
		</a>
		<nav aria-label="Principal">
			{#each nav as n (n.href)}
				<a href={n.href} aria-current={here.startsWith(n.href) ? 'page' : undefined}>{n.label}</a>
			{/each}
		</nav>
		<div class="tools">
			<label class="jump">
				<span class="sr-only">Ir a una provincia</span>
				<select onchange={jump} value={currentProvince}>
					<option value="">Ir a una provincia…</option>
					{#each data.atlas.provinces as p (p.slug)}
						<option value={p.slug}>{p.name}</option>
					{/each}
				</select>
			</label>
			<ThemeToggle />
		</div>
	</div>
</header>

<main id="contenido">
	{@render children()}
</main>

<footer>
	<div class="wrap foot">
		<div>
			<div class="fbrand"><Logo size={22} /> MAPA</div>
			<p class="small">
				Proyecto académico · CIITI 2026. Los datos describen localidades urbanas de 5.000 o más
				habitantes y no permiten sacar conclusiones sobre causas.
			</p>
		</div>
		<div class="small">
			<strong>Fuentes</strong><br />
			INDEC · Encuesta Nacional de Factores de Riesgo 2018, Censos 2010 y 2022, EPH.<br />
			Límites provinciales: Instituto Geográfico Nacional (IGN).<br />
			<a href="/metodologia">Cómo se calcula cada cifra</a>
		</div>
	</div>
</footer>

<style>
	.skip {
		position: absolute;
		left: -999px;
		top: 0;
		background: var(--ink);
		color: var(--surface);
		padding: 0.6rem 1rem;
		z-index: 200;
	}
	.skip:focus {
		left: 8px;
		top: 8px;
	}
	header {
		position: sticky;
		top: 0;
		z-index: 50;
		background: color-mix(in srgb, var(--page) 88%, transparent);
		backdrop-filter: blur(12px);
		border-bottom: 1px solid var(--hair);
	}
	.bar {
		display: flex;
		align-items: center;
		gap: 1.2rem;
		min-height: 64px;
		flex-wrap: wrap;
		padding-block: 0.4rem;
	}
	.brand {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		text-decoration: none;
	}
	.word {
		font-family: var(--font-display);
		font-variation-settings: 'opsz' 48;
		font-size: 1.45rem;
		font-weight: 600;
		letter-spacing: 0.04em;
	}
	.tag {
		font-size: 0.78rem;
		color: var(--ink-2);
		border-left: 1px solid var(--axis);
		padding-left: 0.7rem;
		line-height: 1.2;
		max-width: 11rem;
	}
	nav {
		display: flex;
		gap: 0.3rem;
		margin-left: auto;
	}
	nav a {
		text-decoration: none;
		padding: 0.4rem 0.8rem;
		border-radius: 999px;
		font-size: 0.95rem;
		font-weight: 500;
	}
	nav a:hover {
		background: var(--hair);
	}
	nav a[aria-current='page'] {
		background: var(--ink);
		color: var(--surface);
	}
	.tools {
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}
	.jump select {
		appearance: none;
		background: var(--surface)
			url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' fill='none' stroke='%23898781' stroke-width='1.5'/%3E%3C/svg%3E")
			no-repeat right 0.8rem center;
		border: 1px solid var(--hair);
		border-radius: 999px;
		padding: 0.45rem 2.1rem 0.45rem 0.9rem;
		font-size: 0.9rem;
		max-width: 13rem;
	}
	footer {
		margin-top: 6rem;
		border-top: 1px solid var(--hair);
		padding-block: 2.5rem 3.5rem;
	}
	.foot {
		display: grid;
		grid-template-columns: 1.2fr 1fr;
		gap: 2rem;
	}
	.fbrand {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-family: var(--font-display);
		font-size: 1.2rem;
		font-weight: 600;
		letter-spacing: 0.04em;
		margin-bottom: 0.5rem;
	}
	.small {
		font-size: 0.85rem;
		color: var(--ink-2);
		line-height: 1.55;
		max-width: 38rem;
	}
	@media (max-width: 860px) {
		.tag {
			display: none;
		}
		.bar {
			flex-wrap: nowrap;
			gap: 0.6rem;
			min-height: 56px;
		}
		nav {
			margin-left: auto;
			gap: 0;
		}
		nav a {
			padding: 0.4rem 0.6rem;
			font-size: 0.88rem;
		}
		.foot {
			grid-template-columns: 1fr;
		}
	}
	@media (max-width: 700px) {
		.jump {
			display: none;
		}
	}
	@media (max-width: 460px) {
		.word {
			display: none;
		}
		nav a {
			padding: 0.4rem 0.5rem;
			font-size: 0.84rem;
		}
	}
</style>

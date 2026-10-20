<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Strip from '#lib/components/Strip.svelte';
	import { num, signed } from '#lib/format';
	import { ci95 } from '#lib/stats';
	import type { Category, Indicator } from '#lib/types';
	import { CATEGORY_LABEL, RELIABILITY_TEXT } from '#lib/viz';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const atlas = $derived(data.atlas);

	const valid = (s: string | null, fb: string) => (atlas.provinces.some((p) => p.slug === s) ? (s as string) : fb);
	const a = $derived(valid(page.url.searchParams.get('a'), 'caba'));
	const b = $derived(valid(page.url.searchParams.get('b'), 'chaco'));
	const nameA = $derived(atlas.provinces.find((p) => p.slug === a)!.shortName);
	const nameB = $derived(atlas.provinces.find((p) => p.slug === b)!.shortName);

	function set(patch: { a?: string; b?: string }) {
		const u = new URL(page.url.href);
		for (const [k, v] of Object.entries(patch)) u.searchParams.set(k, v);
		goto(u, { replace: true, reset: false });
	}

	const order: Category[] = ['outcome', 'care', 'risk_factor', 'context'];
	const shown = $derived(atlas.indicators.filter((i) => !i.derived));
	const groups = $derived(
		order.map((c) => ({ key: c, label: CATEGORY_LABEL[c], items: shown.filter((i) => i.category === c) }))
	);

	function cell(ind: Indicator, slug: string) {
		const v = atlas.values[ind.slug]?.[slug];
		if (!v) return null;
		return { v, ci: ci95(v.value, v.cv, ind.unit === '%' ? 100 : Infinity) };
	}
	const unit = (i: Indicator) => (i.unit === '%' ? '%' : ' ' + i.unit);
</script>

<svelte:head>
	<title>{nameA} y {nameB} · MAPA</title>
</svelte:head>

<div class="wrap">
	<header class="top">
		<div class="eyebrow">Comparar</div>
		<h1>{nameA} <span class="vs">y</span> {nameB}</h1>

		<div class="pickers">
			<label>
				<span class="who"><i class="k a"></i> Primera provincia</span>
				<select value={a} onchange={(e) => set({ a: e.currentTarget.value })}>
					{#each atlas.provinces as p (p.slug)}<option value={p.slug}>{p.name}</option>{/each}
				</select>
			</label>
			<button class="swap chip" onclick={() => set({ a: b, b: a })} aria-label="Intercambiar provincias">⇄</button>
			<label>
				<span class="who"><i class="k b"></i> Segunda provincia</span>
				<select value={b} onchange={(e) => set({ b: e.currentTarget.value })}>
					{#each atlas.provinces as p (p.slug)}<option value={p.slug}>{p.name}</option>{/each}
				</select>
			</label>
		</div>
		<p class="how">
			Cada fila muestra a las dos provincias entre las 24. Los puntos huecos son estimaciones que el INDEC
			marca como poco confiables: <strong>una diferencia entre ellas puede no ser real</strong>.
		</p>
	</header>

	{#each groups as g (g.key)}
		<section class="group">
			<h2>{g.label}</h2>
			{#each g.items as ind (ind.slug)}
				{@const ca = cell(ind, a)}
				{@const cb = cell(ind, b)}
				{#if ca && cb}
					{@const diff = ca.v.value - cb.v.value}
					<div class="row">
						<div class="name"><strong>{ind.label}</strong></div>
						<div class="side">
							<div class="val num"><i class="k a"></i>{num(ca.v.value, ind.decimals)}<small>{unit(ind)}</small></div>
							<div class="sub num">
								{#if ca.ci}IC 95%: {num(ca.ci.low, 1)}–{num(ca.ci.high, 1)}{/if}
								{#if ca.v.reliability === 'unreliable' || ca.v.reliability === 'caution'}
									<span class="flag" class:caution={ca.v.reliability === 'caution'}>{RELIABILITY_TEXT[ca.v.reliability].short}</span>
								{/if}
							</div>
						</div>
						<div class="mid">
							<Strip {atlas} indicator={ind} slug={b} compare={a} />
							<div class="diff num">
								{signed(diff, ind.decimals)}{ind.unit === '%' ? ' pp' : ' ' + ind.unit} de diferencia
							</div>
						</div>
						<div class="side r">
							<div class="val num">{num(cb.v.value, ind.decimals)}<small>{unit(ind)}</small><i class="k b"></i></div>
							<div class="sub num">
								{#if cb.v.reliability === 'unreliable' || cb.v.reliability === 'caution'}
									<span class="flag" class:caution={cb.v.reliability === 'caution'}>{RELIABILITY_TEXT[cb.v.reliability].short}</span>
								{/if}
								{#if cb.ci}IC 95%: {num(cb.ci.low, 1)}–{num(cb.ci.high, 1)}{/if}
							</div>
						</div>
					</div>
				{/if}
			{/each}
		</section>
	{/each}
</div>

<style>
	.top {
		padding: 3rem 0 1rem;
	}
	h1 {
		font-size: clamp(2.2rem, 6vw, 4.6rem);
		margin: 0.6rem 0 1.6rem;
	}
	.vs {
		font-style: italic;
		font-weight: 300;
		color: var(--ink-2);
	}
	.pickers {
		display: flex;
		align-items: flex-end;
		gap: 1rem;
		flex-wrap: wrap;
	}
	label {
		display: grid;
		gap: 0.4rem;
	}
	.who {
		font-size: 0.78rem;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--ink-2);
	}
	select {
		background: var(--surface);
		border: 1px solid var(--hair);
		border-radius: 999px;
		padding: 0.65rem 1.1rem;
		font-size: 1rem;
		min-width: 14rem;
	}
	.swap {
		height: 44px;
		width: 44px;
		justify-content: center;
		padding: 0;
	}
	.k {
		display: inline-block;
		width: 11px;
		height: 11px;
		border-radius: 50%;
		margin: 0 0.5rem 0 0;
		vertical-align: baseline;
	}
	.k.a {
		background: var(--blue);
	}
	.k.b {
		background: var(--orange);
		margin: 0 0 0 0.5rem;
	}
	.who .k.b {
		margin: 0 0.5rem 0 0;
	}
	.how {
		margin-top: 1.4rem;
		color: var(--ink-2);
		font-size: 0.95rem;
		max-width: 44rem;
	}
	.group {
		margin-top: 3rem;
	}
	h2 {
		font-size: 1.7rem;
		padding-bottom: 0.6rem;
		border-bottom: 1px solid var(--ink);
	}
	.row {
		display: grid;
		grid-template-columns: 1fr minmax(0, 1.5fr) 1fr;
		grid-template-areas: 'name name name' 'a mid b';
		gap: 0.4rem 1.6rem;
		align-items: center;
		padding: 1.1rem 0;
		border-bottom: 1px solid var(--hair);
	}
	.name {
		grid-area: name;
	}
	.side {
		grid-area: a;
	}
	.side.r {
		grid-area: b;
		text-align: right;
	}
	.mid {
		grid-area: mid;
	}
	.val {
		font-size: 1.7rem;
		font-weight: 600;
		line-height: 1.1;
	}
	.val small {
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--ink-2);
	}
	.sub {
		font-size: 0.78rem;
		color: var(--ink-2);
		margin-top: 0.3rem;
		display: flex;
		gap: 0.6rem;
		flex-wrap: wrap;
	}
	.side.r .sub {
		justify-content: flex-end;
	}
	.diff {
		text-align: center;
		font-size: 0.78rem;
		color: var(--ink-2);
		margin-top: 0.2rem;
	}
	@media (max-width: 720px) {
		.row {
			grid-template-columns: 1fr 1fr;
			grid-template-areas: 'name name' 'mid mid' 'a b';
		}
	}
</style>

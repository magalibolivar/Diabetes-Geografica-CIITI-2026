<script lang="ts">
	import type { Atlas, Indicator } from '#lib/types';
	import { provinceValues, referenceFor } from '#lib/viz';

	let {
		atlas,
		indicator,
		slug,
		compare = null
	}: { atlas: Atlas; indicator: Indicator; slug: string; compare?: string | null } = $props();

	const rows = $derived(provinceValues(atlas, indicator.slug));
	const log = $derived(indicator.unit !== '%');
	const lo = $derived(Math.min(...rows.map((r) => r.v.value)));
	const hi = $derived(Math.max(...rows.map((r) => r.v.value)));
	const ref = $derived(referenceFor(atlas, indicator));

	function pos(x: number): number {
		const f = (v: number) => (log ? Math.log10(Math.max(v, 0.5)) : v);
		const span = f(hi) - f(lo) || 1;
		return 4 + ((f(x) - f(lo)) / span) * 92;
	}
</script>

<!-- Decorativo: los valores exactos están en el texto de la fila. -->
<div class="strip" aria-hidden="true">
	<div class="line"></div>
	<div class="ref" style="left:{pos(ref.value)}%"></div>
	{#each rows as r (r.slug)}
		{#if r.slug !== slug && r.slug !== compare}
			<span
				class="dot"
				class:shaky={r.v.reliability === 'unreliable'}
				style="left:{pos(r.v.value)}%"
				title="{atlas.provinces.find((p) => p.slug === r.slug)?.name}: {r.v.value}"
			></span>
		{/if}
	{/each}
	{#if compare}
		{@const c = atlas.values[indicator.slug]?.[compare]}
		{#if c}<span class="dot b" style="left:{pos(c.value)}%"></span>{/if}
	{/if}
	{#each rows.filter((r) => r.slug === slug) as r (r.slug)}
		<span class="dot a" class:shaky={r.v.reliability === 'unreliable'} style="left:{pos(r.v.value)}%"></span>
	{/each}
</div>

<style>
	.strip {
		position: relative;
		height: 22px;
	}
	.line {
		position: absolute;
		left: 0;
		right: 0;
		top: 10px;
		height: 1px;
		background: var(--axis);
	}
	.ref {
		position: absolute;
		top: 2px;
		bottom: 2px;
		border-left: 1.5px solid var(--muted);
	}
	.dot {
		position: absolute;
		top: 11px;
		width: 9px;
		height: 9px;
		margin: -4.5px 0 0 -4.5px;
		border-radius: 50%;
		background: color-mix(in srgb, var(--blue) 55%, var(--surface));
		box-shadow: 0 0 0 2px var(--surface);
	}
	.dot.shaky {
		background: var(--surface);
		border: 1.5px solid color-mix(in srgb, var(--blue) 70%, var(--surface));
	}
	.dot.a,
	.dot.b {
		width: 14px;
		height: 14px;
		margin: -7px 0 0 -7px;
		z-index: 2;
	}
	.dot.a {
		background: var(--orange);
		border-color: var(--orange);
	}
	.dot.a.shaky {
		background: var(--surface);
		border: 2.5px solid var(--orange);
	}
	.dot.b {
		background: var(--blue);
	}
</style>

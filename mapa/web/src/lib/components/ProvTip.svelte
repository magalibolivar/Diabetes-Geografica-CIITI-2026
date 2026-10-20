<script lang="ts">
	import { num, signed } from '#lib/format';
	import { ci95 } from '#lib/stats';
	import type { Atlas, Indicator } from '#lib/types';
	import { RELIABILITY_TEXT, rankOf, referenceFor } from '#lib/viz';

	let { atlas, indicator, slug }: { atlas: Atlas; indicator: Indicator; slug: string } = $props();

	const province = $derived(atlas.provinces.find((p) => p.slug === slug));
	const v = $derived(atlas.values[indicator.slug]?.[slug]);
	const rank = $derived(rankOf(atlas, indicator.slug, slug));
	const ci = $derived(v ? ci95(v.value, v.cv, indicator.unit === '%' ? 100 : Infinity) : null);
	const ref = $derived(referenceFor(atlas, indicator));
	const unit = $derived(indicator.unit === '%' ? '%' : ` ${indicator.unit}`);
</script>

<div class="t">
	<div class="name">{province?.name}</div>
	{#if v}
		<div class="big num">{num(v.value, indicator.decimals)}<span class="u">{unit}</span></div>
		<div class="meta num">
			{#if ci}
				Intervalo de confianza 95%: {num(ci.low, 1)}–{num(ci.high, 1)}<br />
			{/if}
			{signed(v.value - ref.value, indicator.decimals)}
			{indicator.unit === '%' ? 'pp' : indicator.unit} vs. {ref.isCountry ? 'el país' : 'el promedio'}
			{#if rank}· N.º {rank.rank} de {rank.of}{/if}
		</div>
		{#if v.reliability === 'unreliable' || v.reliability === 'caution'}
			<div class="warn">{RELIABILITY_TEXT[v.reliability].short} (INDEC)</div>
		{/if}
	{:else}
		<div class="meta">Sin dato</div>
	{/if}
</div>

<style>
	.name {
		font-size: 0.78rem;
		opacity: 0.75;
		letter-spacing: 0.02em;
	}
	.big {
		font-size: 1.7rem;
		font-weight: 600;
		line-height: 1.15;
		margin: 0.1rem 0 0.3rem;
	}
	.u {
		font-size: 1rem;
		font-weight: 500;
		margin-left: 0.05em;
		opacity: 0.8;
	}
	.meta {
		font-size: 0.78rem;
		opacity: 0.8;
	}
	.warn {
		margin-top: 0.45rem;
		padding-top: 0.45rem;
		border-top: 1px solid color-mix(in srgb, currentColor 25%, transparent);
		font-size: 0.78rem;
		font-weight: 600;
	}
</style>

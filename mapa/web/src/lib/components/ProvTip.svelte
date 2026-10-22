<script lang="ts">
	import { num, signed } from '#lib/format';
	import { ci95 } from '#lib/stats';
	import type { Atlas, Indicator } from '#lib/types';
	import { RELIABILITY_TEXT, rankOf, referenceFor } from '#lib/viz';

	let { atlas, indicator, slug, advanced = false }: { atlas: Atlas; indicator: Indicator; slug: string; advanced?: boolean } = $props();

	const province = $derived(atlas.provinces.find((p) => p.slug === slug));
	const v = $derived(atlas.values[indicator.slug]?.[slug]);
	const rank = $derived(rankOf(atlas, indicator.slug, slug));
	const ci = $derived(v ? ci95(v.value, v.cv, indicator.unit === '%' ? 100 : Infinity) : null);
	const ref = $derived(referenceFor(atlas, indicator));
	const unit = $derived(indicator.unit === '%' ? '%' : ` ${indicator.unit}`);
	const hasUnreliable = $derived(
		atlas.provinces.some((p) => atlas.values[indicator.slug]?.[p.slug]?.reliability === 'unreliable')
	);
</script>

<div class="t">
	<div class="name">{province?.name}</div>
	{#if v}
		<div class="big num">{num(v.value, indicator.decimals)}<span class="u">{unit}</span></div>
		<div class="meaning">{indicator.description}</div>
		<div class="period">Año: {v.period}</div>
		{#if advanced}
			<div class="meta num">
				{#if ci}Intervalo de confianza 95%: {num(ci.low, 1)}–{num(ci.high, 1)}<br />{/if}
				{#if rank}Puesto {rank.rank} de {rank.of} provincias con dato, de mayor a menor.
					{#if hasUnreliable}Incluye estimaciones marcadas por el INDEC.{/if}<br />{/if}
				{signed(v.value - ref.value, indicator.decimals)} {indicator.unit === '%' ? 'puntos porcentuales' : indicator.unit}
				frente {ref.isCountry ? 'al total nacional' : 'al promedio simple provincial'}.
			</div>
		{/if}
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
	.meaning, .period { font-size: .78rem; line-height: 1.35; }
	.meaning { max-width: 16rem; }
	.period { margin-top: .3rem; opacity: .78; }
	.meta { border-top: 1px solid color-mix(in srgb, currentColor 25%, transparent); margin-top: .55rem; padding-top: .45rem; }
	.warn {
		margin-top: 0.45rem;
		padding-top: 0.45rem;
		border-top: 1px solid color-mix(in srgb, currentColor 25%, transparent);
		font-size: 0.78rem;
		font-weight: 600;
	}
</style>

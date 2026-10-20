<script lang="ts">
	import type { Atlas, Indicator } from '#lib/types';
	import { CATEGORY_LABEL, provinceValues } from '#lib/viz';

	let { atlas, indicator }: { atlas: Atlas; indicator: Indicator } = $props();

	const lineage = $derived(indicator.lineage[0]);
	const rows = $derived(provinceValues(atlas, indicator.slug));
	const shaky = $derived(rows.filter((r) => r.v.reliability === 'unreliable').length);
	const caution = $derived(rows.filter((r) => r.v.reliability === 'caution').length);
</script>

<article class="info">
	<div class="eyebrow">{CATEGORY_LABEL[indicator.category]}</div>
	<h3>{indicator.label}</h3>
	<p class="desc">{indicator.description}</p>

	{#if indicator.derived}
		<p class="derived">
			<strong>Cálculo del sitio:</strong>
			{indicator.derived.formula}. Es el mismo dato visto desde el otro lado y hereda su margen de error.
		</p>
	{/if}

	{#if shaky + caution > 0}
		<p class="alert">
			<span class="flag">En {shaky + caution} de {rows.length} provincias</span>
			el INDEC marca esta estimación como poco confiable o para tomar con precaución. Se ven rayadas en el
			mapa.
		</p>
	{/if}

	{#if lineage}
		<dl>
			<dt>Fuente</dt>
			<dd>{lineage.sourceName}</dd>
			<dt>Dónde</dt>
			<dd>{lineage.sourceRef}</dd>
			<dt>Período</dt>
			<dd>{lineage.referencePeriod}</dd>
			{#if lineage.universe}
				<dt>Población</dt>
				<dd>{lineage.universe}</dd>
			{/if}
		</dl>
		{#if lineage.note}<p class="note">{lineage.note}</p>{/if}
	{/if}
</article>

<style>
	.info {
		padding: 1.3rem 1.4rem;
	}
	h3 {
		margin: 0.35rem 0 0.7rem;
		font-size: 1.5rem;
	}
	.desc {
		font-size: 0.95rem;
		color: var(--ink-2);
		margin-bottom: 0.9rem;
	}
	.derived,
	.alert {
		font-size: 0.85rem;
		background: color-mix(in srgb, var(--ink) 5%, transparent);
		border-radius: var(--radius-sm);
		padding: 0.65rem 0.8rem;
		line-height: 1.45;
	}
	dl {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 0.3rem 1rem;
		margin: 1rem 0 0;
		font-size: 0.82rem;
	}
	dt {
		color: var(--muted);
	}
	dd {
		margin: 0;
	}
	.note {
		font-size: 0.8rem;
		color: var(--ink-2);
		margin: 0.8rem 0 0;
	}
</style>

<script lang="ts">
	import { num } from '#lib/format';
	import type { Indicator } from '#lib/types';
	import type { Scale } from '#lib/viz';

	let {
		scale,
		indicator,
		showHatch = false,
		showNoData = false
	}: { scale: Scale; indicator: Indicator; showHatch?: boolean; showNoData?: boolean } = $props();
</script>

<div class="legend">
	<div class="title">
		{#if scale.measure === 'delta'}
			Diferencia con {scale.reference?.isCountry ? 'el total del país' : 'el promedio de las provincias'}
			({scale.reference ? num(scale.reference.value, indicator.decimals) : ''}{indicator.unit === '%'
				? '%'
				: ' ' + indicator.unit}), en {indicator.unit === '%' ? 'puntos porcentuales' : indicator.unit}
		{:else}
			{indicator.label}{indicator.unit === '%' ? ' (%)' : ` (${indicator.unit})`}
		{/if}
	</div>
	<ul class="bins" style="--n:{scale.swatches.length}">
		{#each scale.swatches as s (s.label)}
			<li>
				<span class="sw" style:background={s.fill}></span>
				<span class="lab num">{s.label}</span>
			</li>
		{/each}
	</ul>
	{#if showHatch || showNoData}
		<div class="keys">
			{#if showHatch}
				<span class="flag">Poco confiable según el INDEC</span>
				<span class="flag caution">Con precaución</span>
			{/if}
			{#if showNoData}
				<span class="nodata">Sin datos (la encuesta no releva Malvinas, Antártida ni las islas australes)</span>
			{/if}
		</div>
	{/if}
</div>

<style>
	.legend {
		font-size: 0.82rem;
	}
	.title {
		font-weight: 600;
		margin-bottom: 0.55rem;
		line-height: 1.3;
	}
	.bins {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		grid-template-columns: repeat(var(--n), minmax(0, 1fr));
		gap: 2px;
	}
	.sw {
		display: block;
		height: 12px;
		border-radius: 3px;
		box-shadow: 0 0 0 1px var(--ring);
	}
	.lab {
		display: block;
		margin-top: 0.3rem;
		font-size: 0.7rem;
		line-height: 1.2;
		color: var(--ink-2);
	}
	.nodata {
		display: inline-flex;
		align-items: center;
		gap: 0.35em;
		font-size: 0.8rem;
		font-weight: 500;
		color: var(--ink-2);
		line-height: 1.3;
	}
	.nodata::before {
		content: '';
		width: 14px;
		height: 14px;
		border-radius: 3px;
		flex: none;
		background: var(--nodata);
		box-shadow: 0 0 0 1px var(--axis);
	}
	.keys {
		display: flex;
		gap: 1.1rem;
		flex-wrap: wrap;
		margin-top: 0.8rem;
	}
	@media (max-width: 560px) {
		.bins {
			grid-template-columns: repeat(2, minmax(0, 1fr));
			gap: 6px 10px;
		}
		.bins li {
			display: flex;
			align-items: center;
			gap: 0.5rem;
		}
		.sw {
			width: 22px;
			flex: none;
		}
		.lab {
			margin: 0;
		}
	}
</style>

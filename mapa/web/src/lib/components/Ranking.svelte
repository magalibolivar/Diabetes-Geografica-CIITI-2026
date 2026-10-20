<script lang="ts">
	import { num } from '#lib/format';
	import { ci95 } from '#lib/stats';
	import type { Atlas, Indicator } from '#lib/types';
	import { provinceValues, referenceFor } from '#lib/viz';

	let {
		atlas,
		indicator,
		selected = null,
		onselect
	}: {
		atlas: Atlas;
		indicator: Indicator;
		selected?: string | null;
		onselect?: (slug: string) => void;
	} = $props();

	let hideShaky = $state(false);

	const log = $derived(indicator.unit !== '%');
	const pctUnit = $derived(indicator.unit === '%');
	const all = $derived(
		provinceValues(atlas, indicator.slug).map((r) => ({
			slug: r.slug,
			name: atlas.provinces.find((p) => p.slug === r.slug)!.name,
			v: r.v,
			ci: ci95(r.v.value, r.v.cv, pctUnit ? 100 : Infinity)
		}))
	);
	const shakyCount = $derived(all.filter((r) => r.v.reliability === 'unreliable').length);
	const rows = $derived(
		all
			.filter((r) => !(hideShaky && r.v.reliability === 'unreliable'))
			.sort((a, b) => b.v.value - a.v.value)
	);
	const max = $derived.by(() => {
		const top = Math.max(...all.map((r) => r.ci?.high ?? r.v.value));
		if (log) return top;
		const step = top > 60 ? 20 : 10;
		return Math.ceil(top / step) * step;
	});
	const ref = $derived(referenceFor(atlas, indicator));

	function w(x: number): number {
		if (log) return (Math.log10(x + 1) / Math.log10(max + 1)) * 100;
		return (x / max) * 100;
	}
</script>

<div class="rank">
	<div class="head">
		<h3>Ranking</h3>
		{#if shakyCount > 0}
			<label class="toggle">
				<input type="checkbox" bind:checked={hideShaky} />
				Ocultar las {shakyCount} poco confiables
			</label>
		{/if}
	</div>

	<ol>
		{#each rows as r (r.slug)}
			{@const shaky = r.v.reliability === 'unreliable'}
			<li>
				<button class="row" class:sel={selected === r.slug} onclick={() => onselect?.(r.slug)}>
					<span class="name">{r.name}{#if shaky}<span class="sr-only"> (estimación poco confiable)</span>{/if}</span>
					<span class="track">
						<span class="bar" class:shaky style="width:{w(r.v.value)}%"></span>
						{#if r.ci}
							<span class="ci" style="left:{w(r.ci.low)}%; width:{w(r.ci.high) - w(r.ci.low)}%"></span>
						{/if}
						<span class="ref" style="left:{w(ref.value)}%" aria-hidden="true"></span>
					</span>
					<span class="val num">{num(r.v.value, indicator.decimals)}</span>
				</button>
			</li>
		{/each}
	</ol>

	<p class="legend">
		<span class="k bar-k"></span> valor
		<span class="k ci-k"></span> intervalo de confianza 95%
		<span class="k ref-k"></span> {ref.isCountry ? 'total del país' : 'promedio'}
		{#if shakyCount > 0}<span class="flag">poco confiable</span>{/if}
		{#if log}<br />Escala logarítmica: cada tramo equivale a multiplicar por 10.{/if}
	</p>
</div>

<style>
	.head {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 1rem;
		margin-bottom: 0.6rem;
		flex-wrap: wrap;
	}
	.toggle {
		font-size: 0.8rem;
		color: var(--ink-2);
		display: flex;
		align-items: center;
		gap: 0.4rem;
		cursor: pointer;
	}
	ol {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.row {
		display: grid;
		grid-template-columns: minmax(6.6rem, 9.5rem) 1fr 3rem;
		align-items: center;
		gap: 0.7rem;
		width: 100%;
		text-align: left;
		background: none;
		border: 0;
		padding: 0.18rem 0.4rem;
		border-radius: 8px;
	}
	.row:hover {
		background: color-mix(in srgb, var(--ink) 6%, transparent);
	}
	.row.sel {
		background: color-mix(in srgb, var(--orange) 14%, transparent);
	}
	.name {
		font-size: 0.86rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.sel .name {
		font-weight: 600;
	}
	.track {
		position: relative;
		height: 20px;
	}
	.bar {
		position: absolute;
		left: 0;
		top: 3px;
		height: 14px;
		border-radius: 0 4px 4px 0; /* extremo de datos redondeado, base recta */
		background: var(--blue);
	}
	.sel .bar {
		background: var(--orange);
	}
	.bar.shaky {
		background-image: repeating-linear-gradient(135deg, var(--hatch-ink) 0 1.5px, transparent 1.5px 4.5px);
		background-color: color-mix(in srgb, var(--blue) 55%, var(--surface));
	}
	.sel .bar.shaky {
		background-color: color-mix(in srgb, var(--orange) 55%, var(--surface));
	}
	.ci {
		position: absolute;
		top: 9.25px;
		height: 1.5px;
		background: var(--ink);
		opacity: 0.8;
	}
	.ci::before,
	.ci::after {
		content: '';
		position: absolute;
		top: -3px;
		width: 1.5px;
		height: 7.5px;
		background: var(--ink);
	}
	.ci::after {
		right: 0;
	}
	.ref {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 0;
		border-left: 1.5px solid var(--muted);
	}
	.val {
		font-size: 0.86rem;
		font-weight: 600;
		text-align: right;
	}
	.legend {
		margin: 0.8rem 0 0;
		font-size: 0.76rem;
		color: var(--ink-2);
		line-height: 1.9;
	}
	.k {
		display: inline-block;
		vertical-align: middle;
		margin: 0 0.3rem 0 0.8rem;
	}
	.k:first-child {
		margin-left: 0;
	}
	.bar-k {
		width: 14px;
		height: 8px;
		border-radius: 0 3px 3px 0;
		background: var(--blue);
	}
	.ci-k {
		width: 16px;
		height: 8px;
		border-left: 1.5px solid var(--ink);
		border-right: 1.5px solid var(--ink);
		background: linear-gradient(var(--ink), var(--ink)) center / 100% 1.5px no-repeat;
	}
	.ref-k {
		width: 0;
		height: 12px;
		border-left: 1.5px solid var(--muted);
	}
</style>

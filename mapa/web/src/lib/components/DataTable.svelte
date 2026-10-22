<script lang="ts">
	import { num } from '#lib/format';
	import { ci95 } from '#lib/stats';
	import type { Atlas, Indicator } from '#lib/types';
	import { RELIABILITY_TEXT, provinceValues } from '#lib/viz';

	let { atlas, indicator }: { atlas: Atlas; indicator: Indicator } = $props();

	const rows = $derived(
		provinceValues(atlas, indicator.slug).map((r) => ({
			province: atlas.provinces.find((p) => p.slug === r.slug)!,
			v: r.v,
			ci: ci95(r.v.value, r.v.cv, indicator.unit === '%' ? 100 : Infinity)
		}))
	);
	const country = $derived(atlas.values[indicator.slug]?.[atlas.country.slug]);
</script>

<details class="tbl">
	<summary>Ver los datos como tabla ({indicator.lineage[0]?.referencePeriod ?? 'año no indicado'})</summary>
	<div class="scroll">
		<table>
			<caption>{indicator.label} por provincia · {indicator.lineage[0]?.referencePeriod ?? 'período no indicado'} · {indicator.lineage[0]?.universe ?? 'población indicada por la fuente'}</caption>
			<thead>
				<tr>
					<th scope="col">Provincia</th>
					<th scope="col">Región</th>
					<th scope="col" class="r">{indicator.label} ({indicator.unit})</th>
					<th scope="col" class="r">Intervalo de confianza 95%</th>
					<th scope="col">Confiabilidad</th>
				</tr>
			</thead>
			<tbody>
				{#if country}
					<tr class="total">
						<th scope="row">Total del país</th>
						<td></td>
						<td class="r num">{num(country.value, indicator.decimals)}</td>
						<td class="r num">
							{#if country.cv != null}
								{@const c = ci95(country.value, country.cv, 100)}
								{c ? `${num(c.low, 1)} – ${num(c.high, 1)}` : ''}
							{/if}
						</td>
						<td></td>
					</tr>
				{/if}
				{#each rows as r (r.province.slug)}
					<tr>
						<th scope="row">{r.province.name}</th>
						<td>{r.province.region}</td>
						<td class="r num">{num(r.v.value, indicator.decimals)}</td>
						<td class="r num">{r.ci ? `${num(r.ci.low, 1)} – ${num(r.ci.high, 1)}` : '—'}</td>
						<td>
							{#if r.v.reliability === 'unreliable' || r.v.reliability === 'caution'}
								<span class="flag" class:caution={r.v.reliability === 'caution'}>
									{RELIABILITY_TEXT[r.v.reliability].short}
								</span>
							{:else if r.v.reliability === 'ok'}
								Aceptable
							{:else}
								Sin evaluar
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</details>

<style>
	.tbl {
		border-top: 1px solid var(--hair);
		padding-top: 1rem;
	}
	summary {
		cursor: pointer;
		font-weight: 600;
		font-size: 0.95rem;
	}
	caption { text-align: left; color: var(--ink-2); font-size: .82rem; padding: 0 0 .5rem; white-space: normal; }
	.scroll {
		overflow-x: auto;
		margin-top: 1rem;
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.88rem;
	}
	th,
	td {
		padding: 0.5rem 0.8rem 0.5rem 0;
		text-align: left;
		border-bottom: 1px solid var(--hair);
		white-space: nowrap;
	}
	thead th {
		font-size: 0.72rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--ink-2);
	}
	th[scope='row'] {
		font-weight: 500;
	}
	.r {
		text-align: right;
	}
	.total th,
	.total td {
		font-weight: 700;
	}
</style>

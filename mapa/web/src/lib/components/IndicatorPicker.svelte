<script lang="ts">
	import type { Atlas, Category } from '#lib/types';
	import { CATEGORY_LABEL } from '#lib/viz';

	let {
		atlas,
		current,
		onpick
	}: { atlas: Atlas; current: string; onpick: (slug: string) => void } = $props();

	const order: Category[] = ['outcome', 'care', 'risk_factor', 'context'];
	const groups = $derived(
		order.map((c) => ({ key: c, label: CATEGORY_LABEL[c], items: atlas.indicators.filter((i) => i.category === c) }))
	);
</script>

<nav class="picker" aria-label="Indicador">
	{#each groups as g (g.key)}
		{#if g.items.length}
			<div class="group">
				<div class="eyebrow">{g.label}</div>
				<ul>
					{#each g.items as i (i.slug)}
						<li>
							<button
								class="chip"
								aria-pressed={current === i.slug}
								onclick={() => onpick(i.slug)}
								title={i.description}
							>
								{i.label}{#if i.derived}<span class="calc" title="Calculado por el sitio">ƒ</span>{/if}
							</button>
						</li>
					{/each}
				</ul>
			</div>
		{/if}
	{/each}
</nav>

<style>
	.picker {
		display: grid;
		gap: 1.4rem;
	}
	ul {
		list-style: none;
		margin: 0.5rem 0 0;
		padding: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	.chip {
		text-align: left;
	}
	.calc {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.85em;
		opacity: 0.7;
	}
	@media (max-width: 1000px) {
		.picker {
			grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
		}
	}
</style>

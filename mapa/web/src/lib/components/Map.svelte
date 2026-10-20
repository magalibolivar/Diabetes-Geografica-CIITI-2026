<script lang="ts">
	import type { Snippet } from 'svelte';
	import { TILES, TILE_COLS, TILE_ROWS } from '#lib/tiles';
	import type { MapGeometry, MapItem } from '#lib/types';

	let {
		geometry,
		items,
		mode = 'geo',
		selected = null,
		onselect,
		tip,
		caption
	}: {
		geometry: MapGeometry;
		items: MapItem[];
		mode?: 'geo' | 'tiles';
		selected?: string | null;
		onselect?: (slug: string) => void;
		tip?: Snippet<[string]>;
		caption: string;
	} = $props();

	const PITCH = 84;
	const TILE = 78;
	const gridX = $derived((geometry.width - TILE_COLS * PITCH + (PITCH - TILE)) / 2);
	const gridY = $derived((geometry.height - TILE_ROWS * PITCH + (PITCH - TILE)) / 2);

	let box: HTMLDivElement | undefined = $state();
	let hover = $state<{ slug: string; x: number; y: number } | null>(null);

	function place(slug: string, clientX: number, clientY: number) {
		if (!box) return;
		const r = box.getBoundingClientRect();
		hover = { slug, x: clientX - r.left, y: clientY - r.top };
	}
	function pointer(e: PointerEvent, slug: string) {
		place(slug, e.clientX, e.clientY);
	}
	function focus(e: FocusEvent, slug: string) {
		const r = (e.currentTarget as SVGGElement).getBoundingClientRect();
		place(slug, r.left + r.width / 2, r.top + r.height / 2);
	}
	function key(e: KeyboardEvent, slug: string) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			onselect?.(slug);
		}
	}

	const tilePos = (slug: string) => {
		const t = TILES[slug];
		return { x: gridX + t.col * PITCH, y: gridY + t.row * PITCH };
	};
	const hoverWidth = $derived(box?.clientWidth ?? 600);
	const tipLeft = $derived(hover ? Math.min(Math.max(hover.x, 150), hoverWidth - 150) : 0);
</script>

<div class="mapbox" bind:this={box}>
	<svg
		viewBox="0 0 {geometry.width} {geometry.height}"
		class:tiles={mode === 'tiles'}
		role="group"
		aria-label={caption}
	>
		<defs>
			<pattern
				id="hatch"
				width="7"
				height="7"
				patternUnits="userSpaceOnUse"
				patternTransform="rotate(45)"
			>
				<line x1="0" y1="0" x2="0" y2="7" stroke-width="1.7" style="stroke: var(--hatch-ink)" />
				<line
					x1="3.5"
					y1="0"
					x2="3.5"
					y2="7"
					stroke-width="1.7"
					opacity="0.75"
					style="stroke: var(--surface)"
				/>
			</pattern>
			<pattern
				id="hatch-soft"
				width="9"
				height="9"
				patternUnits="userSpaceOnUse"
				patternTransform="rotate(45)"
			>
				<line x1="0" y1="0" x2="0" y2="9" stroke-width="1" style="stroke: var(--hatch-ink)" opacity="0.55" />
			</pattern>
		</defs>

		{#each items as item, i (item.slug)}
			{@const tile = tilePos(item.slug)}
			{@const c = geometry.centroids[item.slug]}
			<!-- svelte-ignore a11y_no_noninteractive_tabindex -->
			<g
				class="prov"
				role="button"
				tabindex="0"
				aria-label={item.aria}
				aria-pressed={selected === item.slug}
				onclick={() => onselect?.(item.slug)}
				onkeydown={(e) => key(e, item.slug)}
				onpointermove={(e) => pointer(e, item.slug)}
				onpointerleave={() => (hover = null)}
				onfocus={(e) => focus(e, item.slug)}
				onblur={() => (hover = null)}
			>
				<path class="poly" d={geometry.paths[item.slug]} style:fill={item.fill} />
				{#if item.reliability === 'unreliable'}
					<path class="poly over" d={geometry.paths[item.slug]} fill="url(#hatch)" />
				{:else if item.reliability === 'caution'}
					<path class="poly over" d={geometry.paths[item.slug]} fill="url(#hatch-soft)" />
				{/if}
				{#if item.slug === 'caba'}
					<g class="poly marker">
						<circle cx={c[0]} cy={c[1]} r="15" fill="transparent" />
						<circle cx={c[0]} cy={c[1]} r="6.5" style:fill={item.fill} />
					</g>
				{/if}

				<g
					class="tile"
					style="--tx:{tile.x}px; --ty:{tile.y}px; --cx:{c[0] - TILE / 2}px; --cy:{c[1] - TILE / 2}px; --d:{i * 18}ms"
				>
					<rect class="tile-bg" width={TILE} height={TILE} rx="10" style:fill={item.fill} />
					{#if item.reliability === 'unreliable'}
						<rect class="over" width={TILE} height={TILE} rx="10" fill="url(#hatch)" />
					{:else if item.reliability === 'caution'}
						<rect class="over" width={TILE} height={TILE} rx="10" fill="url(#hatch-soft)" />
					{/if}
					<text class="abbr" x="9" y="19" style:fill={item.ink}>{TILES[item.slug].abbr}</text>
					<text class="val" x={TILE - 9} y={TILE - 12} text-anchor="end" style:fill={item.ink}>
						{item.label}
					</text>
				</g>
			</g>
		{/each}

		{#if selected && geometry.paths[selected]}
			{@const t = tilePos(selected)}
			<path class="ring poly" d={geometry.paths[selected]} />
			<rect class="ring tile-ring" x={t.x} y={t.y} width={TILE} height={TILE} rx="10" />
		{/if}
		{#if hover && hover.slug !== selected}
			{@const t = tilePos(hover.slug)}
			<path class="hring poly" d={geometry.paths[hover.slug]} />
			<rect class="hring tile-ring" x={t.x} y={t.y} width={TILE} height={TILE} rx="10" />
		{/if}
	</svg>

	{#if hover && tip}
		<div class="tip" style="left:{tipLeft}px; top:{hover.y}px" role="tooltip">
			{@render tip(hover.slug)}
		</div>
	{/if}
</div>

<style>
	.mapbox {
		position: relative;
		width: 100%;
	}
	svg {
		display: block;
		width: 100%;
		height: auto;
		overflow: visible;
	}
	.prov {
		cursor: pointer;
		outline: none;
	}
	.poly {
		transition: opacity 0.55s var(--ease);
	}
	.poly:not(.over):not(.marker):not(.ring):not(.hring) {
		stroke: var(--surface);
		stroke-width: 1.4;
		stroke-linejoin: round;
		transition:
			opacity 0.55s var(--ease),
			fill 0.5s var(--ease);
	}
	.over {
		pointer-events: none;
	}
	.marker circle:last-child {
		stroke: var(--surface);
		stroke-width: 2;
		pointer-events: none;
	}
	.ring {
		fill: none;
		stroke: var(--orange);
		stroke-width: 3;
		stroke-linejoin: round;
		pointer-events: none;
	}
	.hring {
		fill: none;
		stroke: var(--ink);
		stroke-width: 1.8;
		stroke-linejoin: round;
		pointer-events: none;
	}
	.prov:focus-visible .poly:not(.over),
	.prov:focus-visible .tile-bg {
		stroke: var(--orange);
		stroke-width: 3;
	}

	/* --- mosaico: cada tile nace en el centroide de su provincia y viaja a su celda --- */
	.tile {
		transform: translate(var(--cx), var(--cy)) scale(0.22);
		transform-origin: 39px 39px;
		opacity: 0;
		pointer-events: none;
		transition:
			transform 0.95s var(--ease) var(--d),
			opacity 0.5s var(--ease) var(--d);
	}
	.tile-bg {
		stroke: var(--surface);
		stroke-width: 0;
	}
	.tile-ring {
		display: none;
	}
	.abbr {
		font: 600 11px var(--font-ui);
		letter-spacing: 0.08em;
	}
	.val {
		font: 600 21px var(--font-ui);
		font-variant-numeric: tabular-nums;
	}

	svg.tiles .tile {
		transform: translate(var(--tx), var(--ty)) scale(1);
		opacity: 1;
		pointer-events: auto;
	}
	svg.tiles .poly {
		opacity: 0;
		pointer-events: none;
	}
	svg.tiles .tile-ring {
		display: block;
	}
	svg.tiles :global(path.ring),
	svg.tiles :global(path.hring) {
		display: none;
	}
	svg:not(.tiles) :global(.tile-ring) {
		display: none;
	}

	.tip {
		position: absolute;
		z-index: 5;
		transform: translate(-50%, calc(-100% - 16px));
		width: max-content;
		max-width: 290px;
		pointer-events: none;
		background: var(--ink);
		color: var(--surface);
		border-radius: 10px;
		padding: 0.7rem 0.85rem;
		font-size: 0.85rem;
		line-height: 1.35;
		box-shadow: 0 10px 30px -8px rgba(0, 0, 0, 0.45);
	}
</style>

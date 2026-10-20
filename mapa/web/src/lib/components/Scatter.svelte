<script lang="ts">
	import { Delaunay } from 'd3-delaunay';
	import { num } from '#lib/format';
	import { describeCorrelation, pearson, spearman, ticks } from '#lib/stats';
	import type { Atlas, Category } from '#lib/types';
	import { CATEGORY_LABEL } from '#lib/viz';

	let {
		atlas,
		x,
		y,
		selected = null,
		onaxes,
		onselect
	}: {
		atlas: Atlas;
		x: string;
		y: string;
		selected?: string | null;
		onaxes: (x: string, y: string) => void;
		onselect?: (slug: string) => void;
	} = $props();

	const W = 680;
	const H = 470;
	const M = { l: 62, r: 22, t: 18, b: 58 };

	const ix = $derived(atlas.indicators.find((i) => i.slug === x)!);
	const iy = $derived(atlas.indicators.find((i) => i.slug === y)!);

	const pts = $derived(
		atlas.provinces.flatMap((p) => {
			const a = atlas.values[x]?.[p.slug];
			const b = atlas.values[y]?.[p.slug];
			if (!a || !b) return [];
			return [
				{
					slug: p.slug,
					name: p.shortName,
					x: a.value,
					y: b.value,
					shaky: a.reliability === 'unreliable' || b.reliability === 'unreliable'
				}
			];
		})
	);

	function domain(vals: number[], log: boolean): [number, number] {
		const lo = Math.min(...vals);
		const hi = Math.max(...vals);
		if (log) return [Math.log10(Math.max(lo, 0.5)) - 0.1, Math.log10(hi) + 0.1];
		const pad = (hi - lo) * 0.08 || 1;
		return [Math.max(0, lo - pad), hi + pad];
	}
	const logX = $derived(ix.unit !== '%');
	const logY = $derived(iy.unit !== '%');
	const dx = $derived(domain(pts.map((p) => p.x), logX));
	const dy = $derived(domain(pts.map((p) => p.y), logY));

	const sx = $derived((v: number) => {
		const t = logX ? Math.log10(Math.max(v, 0.5)) : v;
		return M.l + ((t - dx[0]) / (dx[1] - dx[0])) * (W - M.l - M.r);
	});
	const sy = $derived((v: number) => {
		const t = logY ? Math.log10(Math.max(v, 0.5)) : v;
		return H - M.b - ((t - dy[0]) / (dy[1] - dy[0])) * (H - M.t - M.b);
	});

	function tickList(d: [number, number], log: boolean): number[] {
		if (log) {
			const out: number[] = [];
			for (let k = Math.ceil(d[0]); k <= Math.floor(d[1]); k++) out.push(10 ** k);
			return out;
		}
		return ticks(d[0], d[1], 5);
	}
	const xt = $derived(tickList(dx, logX));
	const yt = $derived(tickList(dy, logY));

	const screen = $derived(pts.map((p) => [sx(p.x), sy(p.y)] as [number, number]));
	const delaunay = $derived(Delaunay.from(screen));

	let hover = $state<number | null>(null);
	let svg: SVGSVGElement | undefined = $state();

	function move(e: PointerEvent) {
		if (!svg) return;
		const r = svg.getBoundingClientRect();
		const px = ((e.clientX - r.left) / r.width) * W;
		const py = ((e.clientY - r.top) / r.height) * H;
		hover = delaunay.find(px, py);
	}

	const xs = $derived(pts.map((p) => p.x));
	const ys = $derived(pts.map((p) => p.y));
	const rho = $derived(spearman(xs, ys));
	const r = $derived(pearson(xs, ys));
	const woCaba = $derived.by(() => {
		const k = pts.filter((p) => p.slug !== 'caba');
		return spearman(k.map((p) => p.x), k.map((p) => p.y));
	});

	const order: Category[] = ['outcome', 'care', 'risk_factor', 'context'];
	const fmt = (v: number, d: number) => num(v, d);
	const selPt = $derived(pts.find((p) => p.slug === selected));
	const hovPt = $derived(hover != null ? pts[hover] : null);
	const labelPts = $derived([selPt, hovPt].filter((p, i, a): p is NonNullable<typeof p> => !!p && a.indexOf(p) === i));
</script>

<div class="sc">
	<div class="pick">
		{#each [{ id: 'sx', label: 'Eje horizontal', v: x, set: (s: string) => onaxes(s, y) }, { id: 'sy', label: 'Eje vertical', v: y, set: (s: string) => onaxes(x, s) }] as ax (ax.id)}
			<label>
				<span class="eyebrow">{ax.label}</span>
				<select value={ax.v} onchange={(e) => ax.set(e.currentTarget.value)}>
					{#each order as c (c)}
						<optgroup label={CATEGORY_LABEL[c]}>
							{#each atlas.indicators.filter((i) => i.category === c) as i (i.slug)}
								<option value={i.slug}>{i.label}</option>
							{/each}
						</optgroup>
					{/each}
				</select>
			</label>
		{/each}
	</div>

	<div class="plot">
		<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
		<svg
			bind:this={svg}
			viewBox="0 0 {W} {H}"
			role="img"
			aria-label="Gráfico de dispersión de {ix.label} contra {iy.label} en las provincias. Los mismos valores están en la tabla de abajo."
			onpointermove={move}
			onpointerleave={() => (hover = null)}
		>
			{#each yt as t (t)}
				<line class="grid" x1={M.l} x2={W - M.r} y1={sy(t)} y2={sy(t)} />
				<text class="tick" x={M.l - 10} y={sy(t) + 4} text-anchor="end">{fmt(t, t >= 100 ? 0 : t % 1 ? 1 : 0)}</text>
			{/each}
			{#each xt as t (t)}
				<line class="grid" y1={M.t} y2={H - M.b} x1={sx(t)} x2={sx(t)} />
				<text class="tick" x={sx(t)} y={H - M.b + 20} text-anchor="middle">{fmt(t, t >= 100 ? 0 : t % 1 ? 1 : 0)}</text>
			{/each}
			<line class="axis" x1={M.l} x2={W - M.r} y1={H - M.b} y2={H - M.b} />
			<line class="axis" x1={M.l} x2={M.l} y1={M.t} y2={H - M.b} />

			<text class="alabel" x={(M.l + W - M.r) / 2} y={H - 12} text-anchor="middle">
				{ix.label} ({ix.unit}){logX ? ' · escala logarítmica' : ''}
			</text>
			<text class="alabel" transform="translate(16 {(M.t + H - M.b) / 2}) rotate(-90)" text-anchor="middle">
				{iy.label} ({iy.unit}){logY ? ' · escala log.' : ''}
			</text>

			{#each pts as p, i (p.slug)}
				<g
					class="pt"
					class:sel={p.slug === selected}
					class:dim={hover != null && hover !== i && p.slug !== selected}
					onclick={() => onselect?.(p.slug)}
					role="presentation"
				>
					<circle class="ring" cx={screen[i][0]} cy={screen[i][1]} r={p.slug === selected ? 10 : 8} />
					<circle
						class="dot"
						class:shaky={p.shaky}
						cx={screen[i][0]}
						cy={screen[i][1]}
						r={p.slug === selected ? 7.5 : 5.5}
					/>
				</g>
			{/each}
			{#each labelPts as p (p.slug)}
				{@const i = pts.indexOf(p)}
				<text
					class="plabel"
					x={screen[i][0] + (screen[i][0] > W - 130 ? -12 : 12)}
					y={screen[i][1] - 10}
					text-anchor={screen[i][0] > W - 130 ? 'end' : 'start'}>{p.name}</text
				>
			{/each}
		</svg>

		{#if hovPt}
			<div class="tipc" role="tooltip">
				<strong>{hovPt.name}</strong><br />
				<span class="num">{ix.label}: {fmt(hovPt.x, ix.decimals)}{ix.unit === '%' ? '%' : ' ' + ix.unit}<br />
				{iy.label}: {fmt(hovPt.y, iy.decimals)}{iy.unit === '%' ? '%' : ' ' + iy.unit}</span>
				{#if hovPt.shaky}<br /><em>Estimación poco confiable (INDEC)</em>{/if}
			</div>
		{/if}
	</div>

	<div class="stats">
		<p class="legendline"><span class="dot-k"></span> provincia <span class="dot-k hollow"></span> estimación poco confiable</p>
		{#if rho != null}
			<p class="read">
				Entre las {pts.length} provincias hay <strong>{describeCorrelation(rho)}</strong>
				(<span class="num">ρ de Spearman = {fmt(rho, 2)}</span>{#if r != null}, <span class="num">r de Pearson = {fmt(r, 2)}</span>{/if}).
				{#if woCaba != null && Math.abs(woCaba - rho) >= 0.1}
					Sin CABA, que suele pesar mucho, baja a <span class="num">{fmt(woCaba, 2)}</span>.
				{/if}
			</p>
		{/if}
		<p class="caveat">
			Esto describe lo que pasa entre provincias; <strong>no explica causas</strong>. Con 24 puntos, una
			relación puede cambiar mucho si se quita uno solo, y las provincias no son personas: una tendencia
			entre provincias puede no valer para individuos.
		</p>
	</div>
</div>

<style>
	.pick {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		margin-bottom: 1rem;
	}
	label {
		display: grid;
		gap: 0.3rem;
	}
	select {
		background: var(--surface);
		border: 1px solid var(--hair);
		border-radius: var(--radius-sm);
		padding: 0.55rem 0.7rem;
		font-size: 0.92rem;
		width: 100%;
	}
	.plot {
		position: relative;
	}
	svg {
		display: block;
		width: 100%;
		height: auto;
		touch-action: pan-y;
	}
	.grid {
		stroke: var(--hair);
		stroke-width: 1;
	}
	.axis {
		stroke: var(--axis);
		stroke-width: 1;
	}
	.tick {
		font: 500 11px var(--font-ui);
		fill: var(--muted);
		font-variant-numeric: tabular-nums;
	}
	.alabel {
		font: 500 12px var(--font-ui);
		fill: var(--ink-2);
	}
	.pt {
		cursor: pointer;
		transition: opacity 0.15s;
	}
	.pt.dim {
		opacity: 0.4;
	}
	.ring {
		fill: var(--surface);
	}
	.dot {
		fill: var(--blue);
	}
	.dot.shaky {
		fill: var(--surface);
		stroke: var(--blue);
		stroke-width: 2;
	}
	.sel .dot {
		fill: var(--orange);
	}
	.sel .dot.shaky {
		fill: var(--surface);
		stroke: var(--orange);
		stroke-width: 2.5;
	}
	.plabel {
		font: 600 13px var(--font-ui);
		fill: var(--ink);
		paint-order: stroke;
		stroke: var(--surface);
		stroke-width: 4px;
		stroke-linejoin: round;
		pointer-events: none;
	}
	.tipc {
		position: absolute;
		top: 10px;
		right: 10px;
		background: var(--ink);
		color: var(--surface);
		border-radius: 10px;
		padding: 0.6rem 0.8rem;
		font-size: 0.8rem;
		line-height: 1.4;
		pointer-events: none;
	}
	.stats {
		margin-top: 0.6rem;
		max-width: 46rem;
	}
	.legendline {
		font-size: 0.78rem;
		color: var(--ink-2);
		margin-bottom: 0.7rem;
	}
	.dot-k {
		display: inline-block;
		width: 10px;
		height: 10px;
		border-radius: 50%;
		background: var(--blue);
		vertical-align: -1px;
		margin-right: 0.3rem;
	}
	.dot-k.hollow {
		background: var(--surface);
		border: 2px solid var(--blue);
		margin-left: 0.9rem;
	}
	.read {
		font-size: 1rem;
		margin-bottom: 0.5rem;
	}
	.caveat {
		font-size: 0.85rem;
		color: var(--ink-2);
	}
	@media (max-width: 560px) {
		.pick {
			grid-template-columns: 1fr;
		}
	}
</style>

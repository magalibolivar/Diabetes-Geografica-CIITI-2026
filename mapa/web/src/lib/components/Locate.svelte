<script lang="ts">
	import { goto } from '$app/navigation';

	let status = $state<'idle' | 'busy' | 'error'>('idle');
	let message = $state('');

	function fail(text: string) {
		status = 'error';
		message = text;
	}

	function locate() {
		if (!('geolocation' in navigator)) return fail('Tu navegador no permite ubicarte. Elegí tu provincia en el menú de arriba.');
		status = 'busy';
		message = '';
		navigator.geolocation.getCurrentPosition(
			async (pos) => {
				try {
					const res = await fetch(`/api/locate?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}`);
					if (res.status === 404) return fail('Parece que estás fuera de Argentina. Elegí una provincia en el menú.');
					if (!res.ok) return fail('No pudimos ubicarte ahora. Probá con el menú de arriba.');
					const found = (await res.json()) as { slug: string };
					await goto(`/provincia/${found.slug}`);
				} catch {
					fail('No pudimos ubicarte ahora. Probá con el menú de arriba.');
				}
			},
			(err) =>
				fail(
					err.code === err.PERMISSION_DENIED
						? 'No diste permiso para ubicarte. Podés elegir tu provincia en el menú de arriba.'
						: 'No pudimos obtener tu ubicación.'
				),
			{ timeout: 10000, maximumAge: 600000 }
		);
	}
</script>

<div class="loc">
	<button class="btn" onclick={locate} disabled={status === 'busy'}>
		<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
			<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z" stroke-linejoin="round" />
			<circle cx="12" cy="9.5" r="2.4" />
		</svg>
		{status === 'busy' ? 'Buscando…' : 'Encontrá tu provincia'}
	</button>
	<p class="priv" role="status">
		{#if status === 'error'}{message}{:else}Usamos tu ubicación solo para esta consulta; no se guarda.{/if}
	</p>
</div>

<style>
	.loc {
		display: grid;
		gap: 0.5rem;
		justify-items: start;
	}
	.btn {
		display: inline-flex;
		align-items: center;
		gap: 0.6rem;
		background: var(--orange);
		color: #0b0b0b;
		border: 0;
		border-radius: 999px;
		padding: 0.85rem 1.4rem;
		font-weight: 600;
		font-size: 1rem;
		transition: transform 0.15s;
	}
	.btn:hover:not(:disabled) {
		transform: translateY(-1px);
	}
	.btn:disabled {
		opacity: 0.7;
		cursor: progress;
	}
	.priv {
		margin: 0;
		font-size: 0.8rem;
		color: var(--ink-2);
		max-width: 24rem;
		min-height: 1.3em;
	}
</style>
